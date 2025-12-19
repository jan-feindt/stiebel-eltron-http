"""Manual WCCI translations extracted from actual ISG device pages."""

# Based on actual ISG device HTML in different languages
WCCI_TRANSLATIONS = {
    "en": {
        "page_title": "POWER CONSUMPTION CONTROL",
        "wcci_input_mode": "INPUT MODE",
        "wcci_input_source": "INPUT SOURCE",
        "wcci_buffer": "BUFFER",
        "wcci_operating_mode": "CURRENT STATE",
        "wcci_user_power_limit": "POWER LIMIT",
        "wcci_load_temp_room_1": "LOAD TEMPERATURE HC1 / BUFFER",
        "wcci_load_temp_room_2": "LOAD TEMPERATURE HC2",
        "wcci_load_temp_room_3": "LOAD TEMPERATURE HC3",
        "wcci_load_temp_room_4": "LOAD TEMPERATURE HC4",
        "wcci_load_temp_room_5": "LOAD TEMPERATURE HC5",
        "wcci_load_temp_buffer": "LOAD TEMPERATURE BUFFER",
        "wcci_load_temp_dhw": "LOAD TEMPERATURE DHW",
    },
    "de": {
        "page_title": "LEISTUNGSBEEINFLUSSUNG",
        "wcci_input_mode": "EINGABEMODUS",
        "wcci_input_source": "EINGABEQUELLE",
        "wcci_buffer": "HEIZUNGSPUFFER",
        "wcci_operating_mode": "AKTUELLER ZUSTAND",
        "wcci_user_power_limit": "LEISTUNGSBEGRENZUNG",
        "wcci_load_temp_room_1": "LADETEMPERATUR HEIZKREIS 1 / PUFFER",
        "wcci_load_temp_room_2": "LADETEMPERATUR HEIZKREIS 2",
        "wcci_load_temp_room_3": "LADETEMPERATUR HEIZKREIS 3",
        "wcci_load_temp_room_4": "LADETEMPERATUR HEIZKREIS 4",
        "wcci_load_temp_room_5": "LADETEMPERATUR HEIZKREIS 5",
        "wcci_load_temp_buffer": "LADETEMPERATUR PUFFER",
        "wcci_load_temp_dhw": "LADETEMPERATUR WARMWASSER",
    },
}

if __name__ == "__main__":
    import json
    
    print("Manual WCCI translations:")
    for lang, translations in WCCI_TRANSLATIONS.items():
        print(f"\n{lang.upper()}:")
        for key, value in translations.items():
            print(f'  "{key}": {{"name": "{value}"}}')
