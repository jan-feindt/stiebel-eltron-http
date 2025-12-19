#!/usr/bin/env python3
"""Extract WCCI translations from HTML test data files."""

import re
from pathlib import Path
from bs4 import BeautifulSoup

# Language codes to process
LANGUAGES = ["cs", "da", "de", "en", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

# Fields to extract with their HTML identifiers
FIELDS = {
    "wcci_input_mode": "EINGABEMODUS",
    "wcci_input_source": "EINGABEQUELLE", 
    "wcci_buffer": "PUFFER",
    "wcci_operating_mode": "AKTUELLER ZUSTAND",
    "wcci_user_power_limit": "LEISTUNGSBEGRENZUNG",
    "wcci_load_temp_room_1": "LADETEMPERATUR HEIZKREIS 1",
    "wcci_load_temp_room_2": "LADETEMPERATUR HEIZKREIS 2",
    "wcci_load_temp_room_3": "LADETEMPERATUR HEIZKREIS 3",
    "wcci_load_temp_room_4": "LADETEMPERATUR HEIZKREIS 4",
    "wcci_load_temp_room_5": "LADETEMPERATUR HEIZKREIS 5",
    "wcci_load_temp_buffer": "LADETEMPERATUR PUFFER",
    "wcci_load_temp_dhw": "LADETEMPERATUR WARMWASSER",
    "wcci_limit_functionality_blocked": "LIMITIERUNGSFUNKTION BLOCKIERT",
}

def extract_translations(lang_code: str) -> dict:
    """Extract WCCI translations from HTML file."""
    testdata_dir = Path(__file__).parent / "testdata"
    html_file = testdata_dir / f"s_4_25_{lang_code}.html"
    
    if not html_file.exists():
        print(f"Warning: {html_file} not found")
        return {}
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    translations = {}
    
    # Extract Input Mode
    h3 = soup.find('h3', string=lambda x: x and 'EINGABEMODUS' in x)
    if h3:
        translations['wcci_input_mode'] = h3.get_text(strip=True)
    
    # Extract Input Source  
    h3 = soup.find('h3', string=lambda x: x and 'EINGABEQUELLE' in x)
    if h3:
        translations['wcci_input_source'] = h3.get_text(strip=True)
    
    # Extract Buffer
    h3 = soup.find('h3', string=lambda x: x and 'PUFFER' in x and 'LADETEMPERATUR' not in x)
    if h3:
        translations['wcci_buffer'] = h3.get_text(strip=True)
    
    # Extract Operating Mode (Aktueller Zustand)
    h3 = soup.find('h3', string=lambda x: x and 'AKTUELLER ZUSTAND' in x)
    if h3:
        translations['wcci_operating_mode'] = h3.get_text(strip=True)
    
    # Extract Power Limitation
    h3 = soup.find('h3', string=lambda x: x and 'LEISTUNGSBEGRENZUNG' in x)
    if h3:
        translations['wcci_user_power_limit'] = h3.get_text(strip=True)
    
    # Extract Load Temperatures
    for h3 in soup.find_all('h3', class_='title'):
        text = h3.get_text(strip=True)
        if 'LADETEMPERATUR HEIZKREIS 1' in text or 'HEIZKREIS 1 / PUFFER' in text:
            translations['wcci_load_temp_room_1'] = text
        elif 'LADETEMPERATUR HEIZKREIS 2' in text:
            translations['wcci_load_temp_room_2'] = text
        elif 'LADETEMPERATUR HEIZKREIS 3' in text:
            translations['wcci_load_temp_room_3'] = text
        elif 'LADETEMPERATUR HEIZKREIS 4' in text:
            translations['wcci_load_temp_room_4'] = text
        elif 'LADETEMPERATUR HEIZKREIS 5' in text:
            translations['wcci_load_temp_room_5'] = text
        elif 'LADETEMPERATUR PUFFER' in text and 'HEIZKREIS' not in text:
            translations['wcci_load_temp_buffer'] = text
        elif 'LADETEMPERATUR WARMWASSER' in text:
            translations['wcci_load_temp_dhw'] = text
    
    # Limit functionality blocked - use German default since not visible in HTML
    translations['wcci_limit_functionality_blocked'] = "LIMITIERUNGSFUNKTION BLOCKIERT"
    
    return translations


def main():
    """Extract translations for all languages."""
    print("Extracting WCCI translations from HTML test data...\n")
    
    for lang in LANGUAGES:
        print(f"\n{lang.upper()}:")
        translations = extract_translations(lang)
        
        if translations:
            for key, value in sorted(translations.items()):
                print(f'  "{key}": {{"name": "{value}"}}')
        else:
            print("  No translations found")


if __name__ == "__main__":
    main()
