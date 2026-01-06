"""Convert sensor names from ALL CAPS to proper capitalization for better readability."""

import json
from pathlib import Path

# Rules for German: Capitalize first letter of each word (nouns) but not all letters
def to_title_case_german(text):
    """Convert German text to proper case - capitalize nouns."""
    # Special abbreviations that should stay uppercase
    keep_upper = ['HK', 'WW', 'ISG', 'VD', 'NHZ', 'DHW', 'HZG', 'COP', 'SG']
    
    words = text.split()
    result = []
    for word in words:
        # Keep abbreviations uppercase
        if word in keep_upper or word.replace('.', '') in keep_upper:
            result.append(word)
        # Keep numbers and mixed case as-is
        elif any(c.isdigit() for c in word) or (word[0].isupper() and not word.isupper()):
            result.append(word)
        # Convert ALLCAPS to Title Case
        elif word.isupper() and len(word) > 2:
            result.append(word.capitalize())
        else:
            result.append(word)
    
    return ' '.join(result)

def to_title_case_english(text):
    """Convert English text to sentence case."""
    # Keep abbreviations uppercase
    keep_upper = ['DHW', 'ISG', 'SG', 'COP']
    
    words = text.split()
    result = []
    for i, word in enumerate(words):
        if word in keep_upper:
            result.append(word)
        elif i == 0:
            # First word capitalized
            result.append(word.capitalize())
        elif any(c.isdigit() for c in word) or (word[0].isupper() and not word.isupper()):
            result.append(word)
        elif word.isupper() and len(word) > 2:
            result.append(word.lower())
        else:
            result.append(word)
    
    return ' '.join(result)

def to_title_case_generic(text):
    """Convert to sentence case for most languages."""
    keep_upper = ['DHW', 'WW', 'VD', 'HK', 'NHZ', 'ISG', 'SG', 'COP']
    
    words = text.split()
    result = []
    for i, word in enumerate(words):
        if word in keep_upper:
            result.append(word)
        elif i == 0:
            result.append(word.capitalize())
        elif any(c.isdigit() for c in word) or (word[0].isupper() and not word.isupper()):
            result.append(word)
        elif word.isupper() and len(word) > 2:
            result.append(word.lower())
        else:
            result.append(word)
    
    return ' '.join(result)

# Language-specific converters
CONVERTERS = {
    'de': to_title_case_german,
    'en': to_title_case_english,
    'da': to_title_case_generic,
    'fi': to_title_case_generic,
    'sv': to_title_case_generic,
    'nl': to_title_case_generic,
    'fr': to_title_case_generic,
    'it': to_title_case_generic,
    'pl': to_title_case_generic,
    'cs': to_title_case_generic,
    'es': to_title_case_generic,
    'hu': to_title_case_generic,
}

def convert_translation_file(lang_code):
    """Convert one translation file."""
    file_path = Path(f'custom_components/stiebel_eltron_http/translations/{lang_code}.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    converter = CONVERTERS.get(lang_code, to_title_case_generic)
    
    # Convert sensor names
    if 'entity' in data and 'sensor' in data['entity']:
        for sensor_key, sensor_data in data['entity']['sensor'].items():
            if 'name' in sensor_data:
                old_name = sensor_data['name']
                new_name = converter(old_name)
                if old_name != new_name:
                    print(f"{lang_code}/{sensor_key}: {old_name} -> {new_name}")
                    sensor_data['name'] = new_name
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Updated {lang_code}.json")

if __name__ == '__main__':
    for lang in ['de', 'en', 'da', 'fi', 'sv', 'nl', 'fr', 'it', 'pl', 'cs', 'es', 'hu']:
        print(f"\n=== {lang.upper()} ===")
        convert_translation_file(lang)
