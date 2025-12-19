#!/usr/bin/env python3
"""Extract heating configuration translations from testdata HTML files."""

import json
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Base directory
SCRIPT_DIR = Path(__file__).parent
TESTDATA_DIR = SCRIPT_DIR / "testdata"
TRANSLATIONS_DIR = SCRIPT_DIR.parent / "custom_components" / "stiebel_eltron_http" / "translations"

# Languages to process
LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "pl", "cs", "hu", "da", "es", "fi"]

# Page configurations
PAGES = {
    "_s_4_2_0": "HEIZKREIS 1",  # HC1
    "_s_4_2_1": "HEIZKREIS 2",  # HC2
    "_s_4_2_2": "STANDARDEINSTELLUNG",  # Basic
    "_s_4_2_3": "SOMMERBETRIEB",  # Summer Mode
    "_s_4_2_4": "PUMPENZYKLEN",  # Pump Cycles
    "_s_4_2_5": "EXTERNE WÄRMEQUELLE",  # External Heat Source
    "_s_4_3_0": "WARMWASSER-TEMPERATUR",  # DHW Temperatures
    "_s_4_3_1": "WARMWASSER",  # DHW Standard Setting
    "_s_4_3_2": "WW-LERNFUNKTION",  # DHW Learning Function
    "_s_4_3_3": "KOMBISPEICHER",  # DHW Combi Cylinder
    "_s_4_3_4": "WW-LEISTUNG WP",  # DHW Output
    "_s_4_3_5": "MAX VORLAUFTEMPERATUR",  # DHW Max Flow Temp
    "_s_4_3_6": "PASTEURISIERUNG",  # DHW Pasteurisation
    "_s_4_3_7": "WÄRMEERZEUGER EXTERN",  # DHW External Heat Source
}

# Sensor key mappings
SENSOR_MAPPINGS = {
    "_s_4_2_0": {
        "val10976": "hc1_comfort_temperature",
        "val10977": "hc1_eco_temperature",
        "val486": "hc1_minimum_temperature",
        "val25": "hc1_heating_curve_rise",
    },
    "_s_4_2_1": {
        "val10980": "hc2_comfort_temperature",
        "val10981": "hc2_eco_temperature",
        "val487": "hc2_minimum_temperature",
        "val10982": "hc2_maximum_temperature",
        "val10983": "hc2_mixer_dynamics",
        "val26": "hc2_heating_curve_rise",
    },
    "_s_4_2_2": {
        "val450": "heating_buffer_operation",
        "val11010": "heating_max_return_temp",
        "val38": "heating_max_flow_temp",
        "val35": "heating_fixed_value_operation",
        "val45": "heating_frost_protection",
    },
    "_s_4_2_3": {
        "val103": "heating_summer_mode",
        "val105": "heating_summer_outside_temp",
        "val104": "heating_summer_heat_buffer",
    },
    "_s_4_2_4": {
        "val106": "heating_pump_cycles",
    },
    "_s_4_2_5": {
        "val342": "heating_external_source",
        "val119": "heating_external_curve_gap",
        "val374": "heating_external_blocking_time",
        "val41": "heating_external_dual_mode_temp",
        "val43": "heating_external_lower_limit",
    },
    "_s_4_3_0": {
        "val11018": "dhw_comfort_temperature",
        "val11019": "dhw_eco_temperature",
    },
    "_s_4_3_1": {
        "val375": "dhw_mode",
        "val120": "dhw_hysteresis",
        "val399": "dhw_stages",
    },
    "_s_4_3_2": {
        "val123": "dhw_learning_function",
    },
    "_s_4_3_3": {
        "val454": "dhw_combi_cylinder",
    },
    "_s_4_3_4": {
        "val1126": "dhw_output_summer",
        "val1127": "dhw_output_winter",
    },
    "_s_4_3_5": {
        "val372": "dhw_max_flow_temp",
    },
    "_s_4_3_6": {
        "val122": "dhw_pasteurisation",
        "val11033": "dhw_pasteurisation_temp",
    },
    "_s_4_3_7": {
        "val369": "dhw_external_source",
        "val42": "dhw_external_dual_mode_temp",
        "val44": "dhw_external_lower_limit",
        "val455": "dhw_external_pwm",
    },
}


def extract_page_title(html_content):
    """Extract the page title from HTML."""
    # Look for the JavaScript line: $("#subnavactivename").html('HEATING CIRCUIT 1');
    match = re.search(r'\$\("#subnavactivename"\)\.html\([\'"]([^\'"]+)[\'"]\)', html_content)
    if match:
        return match.group(1)
    
    # Fallback: try BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Look for the title in the navigation breadcrumb
    nav_items = soup.find_all("li", class_="first")
    if nav_items:
        for item in nav_items:
            a_tag = item.find("a")
            if a_tag and a_tag.get_text(strip=True):
                return a_tag.get_text(strip=True)
    
    # Fallback: look for h1 or h2
    title_tags = soup.find_all(["h1", "h2"])
    if title_tags:
        return title_tags[0].get_text(strip=True)
    
    return ""


def extract_field_names(html_content, page_key):
    """Extract field names from HTML for a specific page."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    field_names = {}
    val_ids = SENSOR_MAPPINGS[page_key].keys()
    
    for val_id in val_ids:
        # Look for h3 with class "title" that contains the field name
        # The val_id is in the parent div's id attribute
        parent_div = soup.find("div", id=f"calval{val_id.replace('val', '')}")
        if parent_div:
            title_h3 = parent_div.find("h3", class_="title")
            if title_h3:
                field_name = title_h3.get_text(strip=True)
                sensor_key = SENSOR_MAPPINGS[page_key][val_id]
                field_names[sensor_key] = field_name
    
    return field_names


def main():
    """Main extraction logic."""
    print("Extracting heating configuration translations...")
    
    all_translations = {lang: {} for lang in LANGUAGES}
    
    for page_key, page_title_de in PAGES.items():
        print(f"\nProcessing page: {page_key}")
        
        for lang in LANGUAGES:
            file_path = TESTDATA_DIR / f"{page_key}_{lang}.html"
            
            if not file_path.exists():
                print(f"  ⚠️  {lang}: File not found: {file_path}")
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                # Extract page title
                page_title = extract_page_title(html_content)
                if not page_title:
                    page_title = page_title_de  # Fallback to German
                
                # Extract field names
                field_names = extract_field_names(html_content, page_key)
                
                # Store translations with page prefix
                for sensor_key, field_name in field_names.items():
                    translation_key = sensor_key
                    translation_value = f"{page_title} {field_name}"
                    all_translations[lang][translation_key] = translation_value
                
                print(f"  ✅ {lang}: Extracted {len(field_names)} fields")
                
            except Exception as e:
                print(f"  ❌ {lang}: Error: {e}")
    
    # Print summary for each language
    print("\n" + "="*80)
    print("TRANSLATION SUMMARY")
    print("="*80)
    
    for lang in LANGUAGES:
        print(f"\n{lang.upper()} ({len(all_translations[lang])} translations):")
        for key in sorted(all_translations[lang].keys()):
            print(f"  {key}: {all_translations[lang][key]}")
    
    # Save to JSON files
    print("\n" + "="*80)
    print("Saving to translation files...")
    print("="*80)
    
    for lang in LANGUAGES:
        translation_file = TRANSLATIONS_DIR / f"{lang}.json"
        
        try:
            # Read existing translations
            with open(translation_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
            
            # Update with new translations
            sensor_section = existing.get("entity", {})
            for key, value in all_translations[lang].items():
                sensor_section[key] = {"name": value}
            
            existing["entity"] = sensor_section
            
            # Write back
            with open(translation_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ {lang}: Updated {translation_file}")
            
        except Exception as e:
            print(f"  ❌ {lang}: Error updating file: {e}")
    
    print("\n✅ Translation extraction complete!")


if __name__ == "__main__":
    main()
