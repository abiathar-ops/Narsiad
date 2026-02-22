import re
import os

# Updated to point to the correct dynasty localization file
NAME_LIST_PATH = "common/culture/name_lists/00_nars_name_lists.txt"
LOC_PATH = "localization/english/dynasties/nars_dynasty_l_english.yml"

def restore_dynasties():
    if not os.path.exists(NAME_LIST_PATH) or not os.path.exists(LOC_PATH):
        print(f"Error: Could not find one of the files.\nMake sure these paths exist:\n1. {NAME_LIST_PATH}\n2. {LOC_PATH}")
        return

    # 1. Read localization and extract all dynn_ keys
    with open(LOC_PATH, 'r', encoding='utf-8') as f:
        loc_lines = f.readlines()
        
    dynasties = []
    for line in loc_lines:
        # Match keys that start with dynn_ (this targets dynasties)
        match = re.match(r'^\s*(dynn_[a-zA-Z0-9_\']+):0', line)
        if match:
            key = match.group(1)
            # Skip dynasty prefixes like "dynnp_ek" to only grab the actual names
            if not key.startswith('dynnp_'):
                dynasties.append(f'"{key}"')
                
    if not dynasties:
        print("No dynasty names found in the localization file.")
        return
        
    # 2. Split the recovered dynasties equally into cadet and main blocks
    half_idx = len(dynasties) // 2
    cadet_dynasties = dynasties[:half_idx]
    main_dynasties = dynasties[half_idx:]
    
    def format_names(name_list):
        # Neatly groups names, 8 per line
        lines = []
        for i in range(0, len(name_list), 8):
            lines.append(" ".join(name_list[i:i+8]))
        return "\n\t\t".join(lines)
        
    cadet_block = f"cadet_dynasty_names = {{\n\t\t{format_names(cadet_dynasties)}\n\t}}"
    main_block = f"dynasty_names = {{\n\t\t{format_names(main_dynasties)}\n\t}}"
    
    # 3. Read the text file and clean up any broken blocks
    with open(NAME_LIST_PATH, 'r', encoding='utf-8') as f:
        nl_content = f.read()
        
    # Remove any existing/empty cadet_dynasty_names or dynasty_names blocks to avoid duplicates
    nl_content = re.sub(r'cadet_dynasty_names\s*=\s*\{[^{}]*\}\s*', '', nl_content)
    nl_content = re.sub(r'dynasty_names\s*=\s*\{[^{}]*\}\s*', '', nl_content)
    
    # 4. Inject the reconstructed blocks right after the start of the name_list block
    new_content = re.sub(
        r'(name_list_nars\s*=\s*\{)', 
        f'\\1\n\n\t{cadet_block}\n\n\t{main_block}\n', 
        nl_content,
        count=1
    )
    
    with open(NAME_LIST_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Success! Restored {len(dynasties)} dynasty names from the localization file back into the name list.")

if __name__ == "__main__":
    restore_dynasties()