#!/usr/bin/env python3
"""Add WCCI sensor translations to all language files."""

import json
import os
from pathlib import Path

# WCCI translations to add (English as base, will be copied to all languages)
WCCI_TRANSLATIONS = {
    "wcci_input_mode": {
        "name": "WCCI Input Mode"
    },
    "wcci_input_source": {
        "name": "WCCI Input Source"
    },
    "wcci_buffer": {
        "name": "WCCI Buffer"
    },
    "wcci_operating_mode": {
        "name": "WCCI Operating Mode"
    },
    "wcci_user_power_limit": {
        "name": "WCCI User Power Limit"
    },
    "wcci_load_temp_room_1": {
        "name": "WCCI Load Temperature HK1/Buffer"
    },
    "wcci_load_temp_room_2": {
        "name": "WCCI Load Temperature HK2"
    },
    "wcci_load_temp_room_3": {
        "name": "WCCI Load Temperature HK3"
    },
    "wcci_load_temp_room_4": {
        "name": "WCCI Load Temperature HK4"
    },
    "wcci_load_temp_room_5": {
        "name": "WCCI Load Temperature HK5"
    },
    "wcci_load_temp_buffer": {
        "name": "WCCI Load Temperature Buffer"
    },
    "wcci_load_temp_dhw": {
        "name": "WCCI Load Temperature DHW"
    },
    "wcci_limit_functionality_blocked": {
        "name": "WCCI Limit Functionality Blocked"
    }
}


def add_wcci_to_language_file(filepath: Path) -> bool:
    """Add WCCI translations to a language file if not already present."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if WCCI translations already exist
    sensors = data.get("entity", {}).get("sensor", {})
    if "wcci_input_mode" in sensors:
        print(f"  {filepath.name}: Already has WCCI translations")
        return False
    
    # Find the position to insert (after water_flow)
    # Add WCCI translations
    for key, value in WCCI_TRANSLATIONS.items():
        sensors[key] = value
    
    # Save the file with proper formatting
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write('\n')  # Add trailing newline
    
    print(f"  {filepath.name}: Added WCCI translations ✅")
    return True


def main():
    """Add WCCI translations to all language files."""
    translations_dir = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"
    
    if not translations_dir.exists():
        print(f"Error: Translations directory not found: {translations_dir}")
        return
    
    print("Adding WCCI translations to all language files...")
    print()
    
    updated = 0
    skipped = 0
    
    for json_file in sorted(translations_dir.glob("*.json")):
        if add_wcci_to_language_file(json_file):
            updated += 1
        else:
            skipped += 1
    
    print()
    print(f"Summary: {updated} files updated, {skipped} files skipped")


if __name__ == "__main__":
    main()
