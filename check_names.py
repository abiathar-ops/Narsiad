import re
import os

# File paths - update these if the script is run from a different directory
NAME_LIST_PATH = "common/culture/name_lists/00_nars_name_lists.txt"
LOC_PATH = "localization/english/names/nars_name_list_l_english.yml"

def check_name_sync():
    if not os.path.exists(NAME_LIST_PATH) or not os.path.exists(LOC_PATH):
        print("Error: Files not found. Please ensure the script is in the project root.")
        return

    # 1. Parse Name List
    with open(NAME_LIST_PATH, 'r', encoding='utf-8') as f:
        nl_content = f.read()
        
    required_names = set()
    
    # Find all name blocks (cadet, dynasty, male, female)
    block_pattern = r'(cadet_dynasty_names|dynasty_names|male_names|female_names)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
    blocks = re.findall(block_pattern, nl_content)
    
    for block_name, block_content in blocks:
        # Extract everything that looks like a name (handles both "dynn_Name" and plain Nikias)
        tokens = re.findall(r'"([^"]+)"|([a-zA-Z0-9_\']+)', block_content)
        for t1, t2 in tokens:
            name = t1 if t1 else t2
            # Exclude common CK3 prefix tags (like dynnp_ep_, dynnp_ek)
            if name and not name.startswith('dynnp_'):
                required_names.add(name)
                
    # 2. Parse Localization File
    with open(LOC_PATH, 'r', encoding='utf-8') as f:
        loc_lines = f.readlines()
        
    loc_keys = set()
    
    for line in loc_lines:
        # Match standard localization lines: Key:0 "Translation"
        match = re.match(r'^\s*([a-zA-Z0-9_\']+):0', line)
        if match:
            loc_keys.add(match.group(1))

    # 3. Compare the two sets
    missing_in_loc = required_names - loc_keys
    extra_in_loc = loc_keys - required_names
    
    print("=" * 50)
    print(f"Total unique names in name list: {len(required_names)}")
    print(f"Total unique keys in localization: {len(loc_keys)}")
    print("=" * 50)
    
    if missing_in_loc:
        print(f"\n❌ MISSING IN LOCALIZATION ({len(missing_in_loc)} names):")
        print("These names are in your .txt file but are missing from the .yml file.")
        for name in sorted(missing_in_loc):
            print(f"  - {name}")
    else:
        print("\n✅ NO MISSING LOCALIZATIONS: Every name in your .txt file is localized.")
        
    if extra_in_loc:
        print(f"\n⚠️ EXTRA LOCALIZATIONS ({len(extra_in_loc)} names):")
        print("These keys are in your .yml file but NOT in the .txt name list.")
        for name in sorted(extra_in_loc):
            print(f"  - {name}")
    else:
        print("\n✅ NO EXTRA LOCALIZATIONS: Your .yml file has no leftover orphaned names.")

if __name__ == "__main__":
    check_name_sync()