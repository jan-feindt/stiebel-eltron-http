#!/usr/bin/env python3
"""Extract translations from page s=4,2,5 (External Heat Generator)."""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List

def extract_field_labels(html_path: Path) -> List[str]:
    """Extract field labels in order from HTML."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    labels = []
    for cal_div in soup.find_all('div', class_='calibration'):
        title_elem = cal_div.find('h3', class_='title')
        if title_elem:
            labels.append(title_elem.text.strip())
    
    return labels

def main():
    """Extract translations for all languages."""
    testdata_dir = Path(__file__).parent / 'testdata'
    
    languages = {
        'de': 'DEUTSCH',
        'en': 'ENGLISH',
        'fr': 'FRANÇAIS',
        'nl': 'NEDERLANDS',
        'it': 'ITALIANO',
        'sv': 'SVENSKA',
        'pl': 'POLSKI',
        'cs': 'ČEŠTINA',
        'hu': 'MAGYAR',
        'es': 'ESPAÑOL',
        'fi': 'SUOMI',
        'da': 'DANSK'
    }
    
    all_labels = {}
    
    for lang_code, lang_name in languages.items():
        html_file = testdata_dir / f'_s_4_2_5_{lang_code}.html'
        if not html_file.exists():
            print(f"Missing: {html_file.name}")
            continue
        
        labels = extract_field_labels(html_file)
        all_labels[lang_code] = labels
        print(f"{lang_name:15} ({lang_code}): {len(labels)} fields")
    
    # Create translation mapping (using German as base)
    if 'de' not in all_labels:
        print("Error: German base file not found")
        return
    
    print(f"\n{'='*70}")
    print("TRANSLATION MAPPING (Page: ?s=4,2,5 - External Heat Generator)")
    print('='*70)
    
    de_labels = all_labels['de']
    
    translations = {}
    
    for i, de_label in enumerate(de_labels):
        print(f"\nField {i+1}: {de_label}")
        field_translations = {}
        
        for lang_code in languages.keys():
            if lang_code in all_labels and i < len(all_labels[lang_code]):
                field_translations[lang_code] = all_labels[lang_code][i]
                if lang_code != 'de':
                    print(f"  {lang_code}: {all_labels[lang_code][i]}")
        
        # Create sensor key (snake_case from German)
        sensor_key = re.sub(r'[^a-zA-Z0-9]+', '_', de_label.lower()).strip('_')
        translations[sensor_key] = field_translations
    
    # Output Python dict format for easy copying
    print(f"\n{'='*70}")
    print("PYTHON DICT FORMAT (for i18n/*.py files)")
    print('='*70)
    print("\nField translations:")
    for sensor_key, trans in translations.items():
        print(f"\n# {trans['de']}")
        for lang_code, label in trans.items():
            print(f'    "{label}",  # {lang_code}')
    
    # Output JSON format for translations/*.json
    print(f"\n{'='*70}")
    print("JSON FORMAT (for translations/*.json files - with section prefix)")
    print('='*70)
    
    json_translations = {}
    for sensor_key, trans in translations.items():
        # Add section prefix for UI display
        prefixed_trans = {}
        for lang_code, label in trans.items():
            prefix = {
                'de': 'Heizen - Wärmeerzeuger Extern',
                'en': 'Heating - External Heat Source',
                'fr': 'Chauffage - Générateur externe',
                'nl': 'Verwarming - Externe warmteopwekker',
                'it': 'Riscaldamento - Generatore esterno',
                'sv': 'Uppvärmning - Extern värmekälla',
                'pl': 'Ogrzewanie - Zewnętrzne źródło',
                'cs': 'Vytápění - Externí zdroj',
                'hu': 'Fűtés - Külső forrás',
                'es': 'Calefacción - Fuente externa',
                'fi': 'Lämmitys - Ulkoinen lähde',
                'da': 'Opvarmning - Ekstern kilde'
            }.get(lang_code, 'Heating - External')
            
            prefixed_trans[lang_code] = f"{prefix}: {label}"
        
        json_translations[sensor_key] = prefixed_trans
    
    print(json.dumps(json_translations, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
