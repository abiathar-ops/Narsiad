import re
import random
import os

NAME_LIST_PATH = "common/culture/name_lists/00_nars_name_lists.txt"
LOC_PATH = "localization/english/names/nars_name_list_l_english.yml"

def equalize_genders():
    if not os.path.exists(NAME_LIST_PATH) or not os.path.exists(LOC_PATH):
        print("Error: Files not found. Please ensure the script is in the project root.")
        return

    # 1. Read the name list file
    with open(NAME_LIST_PATH, 'r', encoding='utf-8') as f:
        nl_content = f.read()

    # Regex to capture just the male and female blocks
    block_pattern = r'(male_names|female_names)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    blocks = dict(re.findall(block_pattern, nl_content))
    
    if 'male_names' not in blocks or 'female_names' not in blocks:
        print("Error: Could not find both male_names and female_names blocks.")
        return

    # Extract elements
    element_pattern = r'(\{\s*"[^"]+"\s+"[^"]+"\s*\}|"[^"]+"|[a-zA-Z0-9_\']+)'
    
    male_elements = [e for e in re.findall(element_pattern, blocks['male_names']) if e.strip()]
    female_elements = [e for e in re.findall(element_pattern, blocks['female_names']) if e.strip()]

    male_count = len(male_elements)
    female_count = len(female_elements)
    
    print(f"Initial counts -> Male: {male_count} | Female: {female_count}")
    
    if male_count == female_count:
        print("The name counts are already equal. No changes needed.")
        return

    # Determine the target size (the smaller of the two)
    target_count = min(male_count, female_count)
    
    # Randomly select the elements to keep
    random.seed(42) # Optional: ensures reproducible results
    kept_males = set(random.sample(male_elements, target_count))
    kept_females = set(random.sample(female_elements, target_count))

    # Maintain original formatting/order for the kept items
    final_males = [e for e in male_elements if e in kept_males]
    final_females = [e for e in female_elements if e in kept_females]

    # Identify which names are being dropped to clean up localization
    dropped_elements = set(male_elements) - kept_males
    dropped_elements.update(set(female_elements) - kept_females)
    
    dropped_keys = set()
    for el in dropped_elements:
        keys = re.findall(r'[a-zA-Z0-9_\']+', el)
        for key in keys:
            if not key.startswith('dynnp_'):
                dropped_keys.add(key)

    # 2. Rebuild the blocks and update the .txt file
    def replace_block(match):
        block_name = match.group(1)
        if block_name == 'male_names':
            elements = final_males
        elif block_name == 'female_names':
            elements = final_females
        else:
            return match.group(0)
            
        new_content = "\n\t\t".join(" ".join(elements[i:i+8]) for i in range(0, len(elements), 8))
        return f"{block_name} = {{\n\t\t{new_content}\n\t}}"

    new_nl_content = re.sub(block_pattern, replace_block, nl_content)

    with open(NAME_LIST_PATH, 'w', encoding='utf-8') as f:
        f.write(new_nl_content)
        
    print(f"Success: Both lists are now equalized at {target_count} names each.")

    # 3. Clean up the localization file
    if dropped_keys:
        with open(LOC_PATH, 'r', encoding='utf-8') as f:
            loc_lines = f.readlines()
            
        new_loc_lines = []
        for line in loc_lines:
            match = re.match(r'^\s*([a-zA-Z0-9_\']+):0', line)
            if match:
                key = match.group(1)
                base_key = re.sub(r'_[0-9]+$', '', key)
                if key in dropped_keys or base_key in dropped_keys:
                    continue # Drop this line
            new_loc_lines.append(line)
            
        with open(LOC_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_loc_lines)
            
        print(f"Cleaned up {len(dropped_keys)} removed names from the localization file.")

if __name__ == "__main__":
    equalize_genders()