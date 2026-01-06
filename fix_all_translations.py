import json
from pathlib import Path

translations_dir = Path("custom_components/stiebel_eltron_http/translations")

# Translations for "STARTS" in each language
starts_translations = {
    'cs': 'SPUŠTĚNÍ',
    'da': 'STARTER',
    'es': 'ARRANQUES',
    'fi': 'KÄYNNISTYKSET',
    'fr': 'DÉMARRAGES',
    'hu': 'INDÍTÁSOK',
    'it': 'AVVIAMENTI',
    'nl': 'STARTS',
    'pl': 'URUCHOMIEŃ',
    'sv': 'STARTER'
}

for json_file in sorted(translations_dir.glob("*.json")):
    if json_file.name in ['en.json', 'de.json']:
        continue  # Already fixed
    
    lang = json_file.stem
    
    print(f"Processing {json_file.name}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sensors = data.get('entity', {}).get('sensor', {})
    changed = False
    
    # Fix compressor_starts
    if 'compressor_starts' in sensors:
        old_name = sensors['compressor_starts']['name']
        if lang in starts_translations:
            new_name = f"{old_name} {starts_translations[lang]}"
            sensors['compressor_starts']['name'] = new_name
            print(f"  Fixed compressor_starts: {old_name} -> {new_name}")
            changed = True
    
    # Remove duplicates
    duplicates_fixed = []
    for key, value in sensors.items():
        name = value.get('name', '')
        words = name.split()
        if len(words) >= 2:
            # Check if any word appears twice consecutively
            for i in range(len(words) - 1):
                if words[i] == words[i + 1]:
                    # Remove the duplicate
                    new_words = words[:i+1] + words[i+2:]
                    new_name = ' '.join(new_words)
                    sensors[key]['name'] = new_name
                    duplicates_fixed.append(f"{key}: {name} -> {new_name}")
                    changed = True
                    break
    
    if duplicates_fixed:
        print(f"  Fixed {len(duplicates_fixed)} duplicates:")
        for fix in duplicates_fixed:
            print(f"    - {fix}")
    
    if changed:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved {json_file.name}")
    else:
        print(f"  No changes needed")
    print()

print("Done!")
