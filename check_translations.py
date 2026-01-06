import json
from pathlib import Path

translations_dir = Path("custom_components/stiebel_eltron_http/translations")

print("Checking compressor_starts and duplicates in all languages...\n")

for json_file in sorted(translations_dir.glob("*.json")):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sensors = data.get('entity', {}).get('sensor', {})
    
    # Check compressor_starts
    comp_name = sensors.get('compressor_starts', {}).get('name', '')
    
    # Check for duplicates
    duplicates = []
    for key, value in sensors.items():
        name = value.get('name', '')
        words = name.split()
        if len(words) >= 2:
            # Check if any word appears twice consecutively
            for i in range(len(words) - 1):
                if words[i] == words[i + 1]:
                    duplicates.append(f"{key}: {name}")
                    break
    
    print(f"{json_file.name}:")
    print(f"  compressor_starts: {comp_name}")
    if duplicates:
        print(f"  Duplicates found: {len(duplicates)}")
        for dup in duplicates[:3]:  # Show first 3
            print(f"    - {dup}")
    else:
        print(f"  No duplicates")
    print()
