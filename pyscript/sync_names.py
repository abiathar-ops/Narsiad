import re
import os

# File paths - update these if the script is run from a different directory
NAME_LIST_PATH = "common/culture/name_lists/00_nars_name_lists.txt"
LOC_PATH = "localization/english/names/nars_name_list_l_english.yml"

def sync_files():
    if not os.path.exists(NAME_LIST_PATH) or not os.path.exists(LOC_PATH):
        print("Error: Files not found. Please ensure the script is in the project root.")
        return

    # 1. Parse Name List
    with open(NAME_LIST_PATH, 'r', encoding='utf-8') as f:
        nl_content = f.read()
        
    required_names = set()
    
    # Regex to capture the main name blocks
    block_pattern = r'(cadet_dynasty_names|dynasty_names|male_names|female_names)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    blocks = re.findall(block_pattern, nl_content)
    
    for block_name, block_content in blocks:
        tokens = re.findall(r'"([^"]+)"|([a-zA-Z0-9_\']+)', block_content)
        for t1, t2 in tokens:
            name = t1 if t1 else t2
            # Exclude common prefix tags
            if name and not name.startswith('dynnp_'):
                required_names.add(name)
                
    # 2. Parse Localization File
    with open(LOC_PATH, 'r', encoding='utf-8') as f:
        loc_lines = f.readlines()
        
    loc_keys = set()
    for line in loc_lines:
        match = re.match(r'^\s*([a-zA-Z0-9_\']+):0', line)
        if match:
            loc_keys.add(match.group(1))

    # 3. Identify mismatches
    missing_in_loc = required_names - loc_keys
    extra_in_loc = loc_keys - required_names
    
    if not missing_in_loc and not extra_in_loc:
        print("Everything is already perfectly matched. No changes needed.")
        return

    # 4. Remove unlocalized names from the .txt file
    if missing_in_loc:
        def process_block(match):
            block_name = match.group(1)
            block_content = match.group(2)
            
            element_pattern = r'(\{\s*"[^"]+"\s+"[^"]+"\s*\}|"[^"]+"|[a-zA-Z0-9_\']+)'
            elements = re.findall(element_pattern, block_content)
            elements = [e for e in elements if e.strip()]
            
            kept_elements = []
            for el in elements:
                keys = re.findall(r'[a-zA-Z0-9_\']+', el)
                should_keep = True
                for key in keys:
                    if key in missing_in_loc:
                        should_keep = False
                        break
                if should_keep:
                    kept_elements.append(el)
            
            new_content = "\n\t\t".join(" ".join(kept_elements[i:i+8]) for i in range(0, len(kept_elements), 8))
            return f"{block_name} = {{\n\t\t{new_content}\n\t}}"

        nl_content = re.sub(block_pattern, process_block, nl_content)
        
        with open(NAME_LIST_PATH, 'w', encoding='utf-8') as f:
            f.write(nl_content)
        print(f"Removed {len(missing_in_loc)} unlocalized names from the name list (.txt).")

    # 5. Remove extra localizations from the .yml file
    if extra_in_loc:
        new_loc_lines = []
        for line in loc_lines:
            match = re.match(r'^\s*([a-zA-Z0-9_\']+):0', line)
            if match:
                key = match.group(1)
                if key in extra_in_loc:
                    continue # Skip saving this line
            new_loc_lines.append(line)
            
        with open(LOC_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_loc_lines)
        print(f"Removed {len(extra_in_loc)} orphaned localizations from the localization file (.yml).")

    print("\nSuccess! Both files are now 100% perfectly synchronized.")

if __name__ == "__main__":
    sync_files()