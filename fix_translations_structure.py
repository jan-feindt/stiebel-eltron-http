import json
import os
from pathlib import Path

translations_dir = Path("custom_components/stiebel_eltron_http/translations")

for json_file in translations_dir.glob("*.json"):
    if json_file.name == "en.json":
        continue  # Skip en.json as it's already fixed
    
    print(f"Processing {json_file.name}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if there are misplaced entries
    misplaced_keys = []
    entity_keys = list(data.get('entity', {}).keys())
    
    # Find entries that are not 'sensor' or 'binary_sensor'
    for key in entity_keys:
        if key not in ['sensor', 'binary_sensor']:
            misplaced_keys.append(key)
    
    if misplaced_keys:
        print(f"  Found {len(misplaced_keys)} misplaced entries")
        
        # Move them into sensor section
        for key in misplaced_keys:
            data['entity']['sensor'][key] = data['entity'].pop(key)
        
        # Write back with proper formatting
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  Fixed {json_file.name}")
    else:
        print(f"  {json_file.name} is OK")

print("\nDone!")
