import re
import random

# File paths - update these if the script is run from a different directory
NAME_LIST_PATH = "common/culture/name_lists/00_nars_name_lists.txt"
LOC_PATH = "localization/english/names/nars_name_list_l_english.yml"

def update_files():
    # 1. Process the name_lists file
    with open(NAME_LIST_PATH, 'r', encoding='utf-8') as f:
        name_list_content = f.read()

    removed_names = set()

    def process_block(match):
        block_name = match.group(1)
        block_content = match.group(2)
        
        # Regex to capture individual names or brace-enclosed prefixes (e.g., { "dynnp_ep_" "dynn_Posoidaian" })
        element_pattern = r'(\{\s*"[^"]+"\s+"[^"]+"\s*\}|"[^"]+"|[a-zA-Z0-9_\']+)'
        elements = re.findall(element_pattern, block_content)
        
        # Filter out any empty matches
        elements = [e for e in elements if e.strip()]
        
        # Randomly select 50% to keep
        random.seed(42)  # Ensures the same 50% are kept if run multiple times
        kept_elements = set(random.sample(elements, k=len(elements) // 2))
        
        # Identify removed elements to sync with the localization file
        for el in elements:
            if el not in kept_elements:
                # Extract all alphanumeric keys from the dropped element
                keys = re.findall(r'[a-zA-Z0-9_\']+', el)
                for key in keys:
                    # Ignore prefixes, only target the actual names for loc deletion
                    if key not in ['dynnp_ep_', 'dynnp_ek', 'dynnp_eg', 'dynnp_ex']:
                        removed_names.add(key)

        # Order the kept elements as they originally appeared for consistency
        final_elements = [e for e in elements if e in kept_elements]
        
        # Format the new block content neatly (8 names per line)
        new_content = "\n\t\t".join(" ".join(final_elements[i:i+8]) for i in range(0, len(final_elements), 8))
        return f"{block_name} = {{\n\t\t{new_content}\n\t}}"

    # Regex to match the specific name categories, supporting 1 level of nested braces
    block_regex = r'(cadet_dynasty_names|dynasty_names|male_names|female_names)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    new_name_list_content = re.sub(block_regex, process_block, name_list_content)

    with open(NAME_LIST_PATH, 'w', encoding='utf-8') as f:
        f.write(new_name_list_content)

    # 2. Process the localization file
    with open(LOC_PATH, 'r', encoding='utf-8') as f:
        loc_lines = f.readlines()

    new_loc_lines = []
    for line in loc_lines:
        # Match standard localization lines: Key:0 "Translation"
        loc_match = re.match(r'^(\s*)([a-zA-Z0-9_\']+):0\s+".*"', line)
        if loc_match:
            key = loc_match.group(2)
            # Remove any trailing numbers (e.g., Papias_1 -> Papias) to catch variants
            base_key = re.sub(r'_[0-9]+$', '', key)
            
            # If the localization key corresponds to a name we removed, skip adding it
            if key in removed_names or base_key in removed_names:
                continue
        new_loc_lines.append(line)

    with open(LOC_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_loc_lines)

    print(f"Success! Removed {len(removed_names)} names from the list and their corresponding localizations.")
    print("All other file elements (like mercenary names and grandparent chances) have been preserved.")

if __name__ == "__main__":
    update_files()