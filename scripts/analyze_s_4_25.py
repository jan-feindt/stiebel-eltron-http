#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze page s=4,25 (LEISTUNGSBEEINFLUSSUNG / Power Influence)."""

import sys
import io
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Set stdout to use UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_wcci_fields(html_path: Path) -> dict:
    """Extract WCCI configuration fields from HTML."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    fields = {}
    
    # Find the WCCI site div
    wcci_div = soup.find('div', id='wcci_site')
    if not wcci_div:
        print(f"Warning: No wcci_site div found in {html_path.name}")
        return fields
    
    # Find all calibration divs within WCCI site
    for cal_div in wcci_div.find_all('div', class_='calibration'):
        # Get the field title
        title_elem = cal_div.find('h3', class_='title')
        if not title_elem:
            continue
        
        title = title_elem.text.strip()
        
        # Check for dropdown field with WCCI_ ID
        dropdown = cal_div.find('input', id=re.compile(r'^WCCI_'))
        if dropdown:
            field_id = dropdown.get('id', '')
            field_value = dropdown.get('value', '')
            
            # Get all radio options
            options = []
            for radio in cal_div.find_all('input', type='radio'):
                opt_text = radio.get('alt', '')
                is_checked = radio.get('checked') == 'checked'
                options.append({
                    'text': opt_text,
                    'checked': is_checked
                })
            
            fields[title] = {
                'type': 'dropdown',
                'id': field_id,
                'value': field_value,
                'options': options
            }
            continue
        
        # Check for numeric input field
        num_input = cal_div.find('input', id=re.compile(r'^(load_|user_)'))
        if num_input:
            field_id = num_input.get('id', '')
            field_value = num_input.get('value', '')
            
            # Get unit from the values div
            unit_div = cal_div.find('div', class_='values span-1 append-1')
            unit = unit_div.text.strip() if unit_div else ''
            
            fields[title] = {
                'type': 'numeric',
                'id': field_id,
                'value': field_value,
                'unit': unit
            }
            continue
    
    return fields

def main():
    """Main analysis function."""
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
    
    all_data = {}
    
    print("="*70)
    print("WCCI POWER INFLUENCE CONFIGURATION (Page: /?s=4,25)")
    print("="*70)
    
    for lang_code, lang_name in sorted(languages.items()):
        html_file = testdata_dir / f's_4_25_{lang_code}.html'
        if not html_file.exists():
            print(f"\n⚠️  Missing: {lang_name} ({lang_code})")
            continue
        
        fields = extract_wcci_fields(html_file)
        all_data[lang_code] = fields
        
        print(f"\n{lang_name} ({lang_code}): {len(fields)} fields")
        print("-" * 70)
        
        for title, data in fields.items():
            print(f"\n  {title}")
            print(f"    Type: {data['type']}")
            print(f"    ID: {data['id']}")
            print(f"    Current: {data['value']}")
            
            if data['type'] == 'dropdown':
                print(f"    Options ({len(data['options'])}):")
                for opt in data['options']:
                    marker = " [CURRENT]" if opt['checked'] else ""
                    print(f"      - {opt['text']}{marker}")
            elif data.get('unit'):
                print(f"    Unit: {data['unit']}")
    
    # Create translation mapping
    print(f"\n{'='*70}")
    print("TRANSLATION MAPPING")
    print('='*70)
    
    if 'de' not in all_data:
        print("Error: German base file not found")
        return
    
    de_fields = list(all_data['de'].keys())
    print(f"\nFound {len(de_fields)} configuration fields")
    
    for field_name in de_fields:
        print(f"\n{field_name} (ID: {all_data['de'][field_name]['id']}):")
        
        # Collect translations by position
        translations = {}
        de_idx = de_fields.index(field_name)
        
        for lang_code in sorted(languages.keys()):
            if lang_code not in all_data:
                continue
            
            lang_fields = list(all_data[lang_code].keys())
            if de_idx < len(lang_fields):
                lang_field = lang_fields[de_idx]
                translations[lang_code] = lang_field
                if lang_code != 'de':
                    print(f"  {lang_code}: {lang_field}")
        
        # Show field type and value
        field_data = all_data['de'][field_name]
        print(f"  Type: {field_data['type']}, Current: {field_data['value']}")
    
    #Print field IDs for mapping
    print(f"\n{'='*70}")
    print("FIELD IDS FOR EXTRACTION")
    print('='*70)
    for field_name in de_fields:
        field_id = all_data['de'][field_name]['id']
        field_type = all_data['de'][field_name]['type']
        print(f"{field_id:30} - {field_type:10} - {field_name}")

if __name__ == '__main__':
    main()
