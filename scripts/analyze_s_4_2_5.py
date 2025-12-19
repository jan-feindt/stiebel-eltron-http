#!/usr/bin/env python3
"""Analyze page s=4,2,5 (External Heat Generator) to extract all fields."""

import re
from pathlib import Path
from bs4 import BeautifulSoup

def extract_fields_from_html(html_path: Path) -> dict:
    """Extract all fields with their values from the HTML."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    fields = {}
    
    # Find all calibration divs
    for cal_div in soup.find_all('div', class_='calibration'):
        # Get the field title
        title_elem = cal_div.find('h3', class_='title')
        if not title_elem:
            continue
        
        title = title_elem.text.strip()
        
        # Check for dropdown field (aval* with value attribute)
        dropdown = cal_div.find('input', id=re.compile(r'^aval\d+'))
        if dropdown and dropdown.get('value'):
            field_value = dropdown['value']
            field_type = 'dropdown'
            # Get all radio options
            options = []
            for radio in cal_div.find_all('input', type='radio'):
                opt_text = radio.get('alt', '')
                opt_value = radio.get('value', '')
                is_checked = radio.get('checked') is not None
                options.append({
                    'text': opt_text,
                    'value': opt_value,
                    'checked': is_checked
                })
            fields[title] = {
                'type': field_type,
                'value': field_value,
                'options': options
            }
            continue
        
        # Check for numeric field (val* with jsvalues)
        script_tags = cal_div.find_all('script')
        for script in script_tags:
            if not script.string:
                continue
            
            # Extract jsvalues assignment
            match = re.search(r"jsvalues\['(\d+)'\]\['val'\]='([^']+)'", script.string)
            if match:
                field_id = match.group(1)
                field_value = match.group(2)
                
                # Extract min/max from valSettings
                min_match = re.search(r"valSettings\['val\d+'\]\['min'\]\s*=\s*'([^']+)'", script.string)
                max_match = re.search(r"valSettings\['val\d+'\]\['max'\]\s*=\s*'([^']+)'", script.string)
                type_match = re.search(r"valSettings\['val\d+'\]\['type'\]\s*=\s*'([^']+)'", script.string)
                
                # Get unit from the values div
                unit_div = cal_div.find('div', class_='values span-1 append-1')
                unit = unit_div.text.strip() if unit_div else ''
                
                fields[title] = {
                    'type': type_match.group(1) if type_match else 'unknown',
                    'value': field_value,
                    'min': min_match.group(1) if min_match else None,
                    'max': max_match.group(1) if max_match else None,
                    'unit': unit,
                    'id': field_id
                }
                break
    
    return fields

def main():
    """Main analysis function."""
    testdata_dir = Path(__file__).parent / 'testdata'
    
    languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'pl', 'cs', 'hu', 'es', 'fi', 'da']
    
    all_data = {}
    
    for lang in languages:
        html_file = testdata_dir / f'_s_4_2_5_{lang}.html'
        if not html_file.exists():
            print(f"⚠️  Missing: {html_file.name}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Language: {lang.upper()}")
        print('='*60)
        
        fields = extract_fields_from_html(html_file)
        all_data[lang] = fields
        
        for title, data in fields.items():
            print(f"\n{title}")
            print(f"  Type: {data['type']}")
            print(f"  Value: {data['value']}")
            if data['type'] == 'dropdown':
                print(f"  Options ({len(data['options'])}):")
                for opt in data['options']:
                    checked = " [CURRENT]" if opt['checked'] else ""
                    print(f"    [{opt['value']}] {opt['text']}{checked}")
            else:
                if data.get('min') and data.get('max'):
                    print(f"  Range: {data['min']} - {data['max']} {data['unit']}")
                if data.get('id'):
                    print(f"  Field ID: {data['id']}")
    
    # Create translation mapping
    print(f"\n{'='*60}")
    print("TRANSLATION MAPPING")
    print('='*60)
    
    # Get German field names as base
    if 'de' in all_data:
        de_fields = list(all_data['de'].keys())
        print(f"\nFound {len(de_fields)} fields to translate:")
        
        for field_name in de_fields:
            print(f"\n{field_name}:")
            for lang in languages:
                if lang in all_data and field_name in all_data[lang]:
                    # Find corresponding field in other language by position
                    pass
                elif lang in all_data:
                    # Find by position
                    lang_fields = list(all_data[lang].keys())
                    idx = de_fields.index(field_name)
                    if idx < len(lang_fields):
                        print(f"  {lang}: {lang_fields[idx]}")

if __name__ == '__main__':
    main()
