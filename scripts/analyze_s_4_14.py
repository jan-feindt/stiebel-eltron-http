"""
Analyze s=4,14 (ENERGIEMANAGEMENT) configuration page
Extract all configurable fields with their specifications
"""
from bs4 import BeautifulSoup
import json

def parse_s_4_14_page(html_file):
    """Parse the s=4,14 HTML page and extract all configurable fields"""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find page title
    page_title_elem = soup.find('div', class_='left main sifr span-9')
    page_title = page_title_elem.get_text(strip=True) if page_title_elem else "Unknown"
    
    print(f"\n{'='*80}")
    print(f"PAGE: {page_title}")
    print(f"{'='*80}\n")
    
    fields = []
    
    # Find all calibration divs (these contain the configurable fields)
    cal_divs = soup.find_all('div', class_='calibration')
    
    for cal_div in cal_divs:
        # Get the div ID (contains the val ID)
        div_id = cal_div.get('id', '')
        if not div_id.startswith('calval'):
            continue
        
        val_id = div_id.replace('calval', '')
        
        # Get field name from h3.title
        title_elem = cal_div.find('h3', class_='title')
        field_name = title_elem.get_text(strip=True) if title_elem else "Unknown"
        
        # Determine input type and extract relevant data
        field_data = {
            'field_name': field_name,
            'val_id': val_id,
            'div_id': div_id
        }
        
        # Check for radio buttons
        radio_buttons = cal_div.find_all('input', type='radio')
        if radio_buttons:
            field_data['input_type'] = 'radio'
            field_data['options'] = []
            
            for radio in radio_buttons:
                option = {
                    'value': radio.get('value', ''),
                    'label': radio.get('alt', ''),
                    'checked': radio.has_attr('checked')
                }
                field_data['options'].append(option)
        
        # Check for numeric input (with up/down buttons)
        # Look for inputs with class containing 'upndown' or 'edit upndown'
        numeric_input = cal_div.find('input', {'class': lambda x: x and 'upndown' in ' '.join(x) if isinstance(x, list) else 'upndown' in x if x else False})
        if not numeric_input:
            # Also check for inputs with editors (up/down buttons)
            editors_div = cal_div.find('div', class_='editors')
            if editors_div:
                numeric_input = cal_div.find('input', {'id': lambda x: x and x.startswith('val')})
        
        if numeric_input:
            field_data['input_type'] = 'numeric'
            
            # Extract min/max from JavaScript
            script = cal_div.find('script')
            if script:
                script_text = script.get_text()
                
                # Extract min value - look for pattern like ['min'] = '20';
                import re
                min_match = re.search(r"\['min'\]\s*=\s*'([^']+)'", script_text)
                if min_match:
                    field_data['min'] = min_match.group(1)
                
                # Extract max value
                max_match = re.search(r"\['max'\]\s*=\s*'([^']+)'", script_text)
                if max_match:
                    field_data['max'] = max_match.group(1)
                
                # Extract data type
                type_match = re.search(r"\['type'\]\s*=\s*'([^']+)'", script_text)
                if type_match:
                    field_data['data_type'] = type_match.group(1)
                
                # Extract current value
                val_match = re.search(r"\['val'\]\s*=\s*'([^']+)'", script_text)
                if val_match:
                    field_data['current_value'] = val_match.group(1)
            
            # Extract unit from adjacent div
            unit_div = cal_div.find('div', class_='values span-1 append-1')
            if unit_div:
                unit = unit_div.get_text(strip=True)
                if unit and unit != '':
                    field_data['unit'] = unit
        
        # Extract description from green info box
        green_div = cal_div.find('div', class_='green round-right')
        if green_div:
            description = green_div.get_text(strip=True)
            field_data['description'] = description
        
        fields.append(field_data)
    
    return page_title, fields


def print_field_summary(fields):
    """Print a summary of all extracted fields"""
    
    print(f"\nTotal fields found: {len(fields)}\n")
    
    for i, field in enumerate(fields, 1):
        print(f"\n{i}. {field['field_name']}")
        print(f"   {'─'*70}")
        print(f"   Val ID:      {field['val_id']}")
        print(f"   Div ID:      {field['div_id']}")
        print(f"   Input Type:  {field.get('input_type', 'unknown')}")
        
        if field.get('input_type') == 'radio':
            print(f"   Options:")
            for opt in field.get('options', []):
                checked = " (CHECKED)" if opt['checked'] else ""
                print(f"      - {opt['label']}: {opt['value']}{checked}")
        
        elif field.get('input_type') == 'numeric':
            print(f"   Data Type:   {field.get('data_type', 'N/A')}")
            print(f"   Min Value:   {field.get('min', 'N/A')}")
            print(f"   Max Value:   {field.get('max', 'N/A')}")
            print(f"   Current:     {field.get('current_value', 'N/A')}")
            if 'unit' in field:
                print(f"   Unit:        {field.get('unit')}")
        
        if 'description' in field:
            print(f"   Description: {field['description']}")


def export_to_json(fields, output_file):
    """Export fields to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)
    print(f"\n\nExported to: {output_file}")


if __name__ == '__main__':
    html_file = r'C:\GitHub\stiebel-eltron-http\scripts\testdata\_s_4_14_en.html'
    
    page_title, fields = parse_s_4_14_page(html_file)
    print_field_summary(fields)
    
    # Export to JSON
    output_file = r'C:\GitHub\stiebel-eltron-http\scripts\s_4_14_fields.json'
    export_to_json(fields, output_file)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
