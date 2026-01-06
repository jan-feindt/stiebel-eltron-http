"""Comprehensive test to ensure all sensors are extracted with values.

This test validates the complete extraction chain:
1. I18n translations exist for canonical keys
2. Test data contains the sensor
3. Extraction actually works and returns non-None values
"""

import pytest
from pathlib import Path

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.i18n import HEADER_ALIASES, CanonicalKey


TESTDATA_DIR = Path(__file__).parent.parent / "scripts" / "testdata"


def get_canonical_keys_defined():
    """Get all canonical keys defined in CanonicalKey enum."""
    return {item for item in CanonicalKey}


def get_canonical_keys_with_translations():
    """Get all canonical keys that have i18n translations."""
    return set(HEADER_ALIASES.keys())


# Canonical keys that are intentionally optional (not on all systems or sections)
# These are keys that may not be present in test data or on all system models
OPTIONAL_CANONICAL_KEYS = {
    # Buffer sensors (not all systems have buffers)
    CanonicalKey.ACTUAL_BUFFER_TEMPERATURE,
    CanonicalKey.SET_BUFFER_TEMPERATURE,
    # Room temperature/humidity (not all systems)
    CanonicalKey.RELATIVE_HUMIDITY_1,
    # External heater fields
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE,
    CanonicalKey.EXTERNAL_SET_TEMPERATURE,
    # Dual mode and lower limit (configuration page fields)
    CanonicalKey.DUAL_MODE_TEMP_HZG,
    CanonicalKey.DUAL_MODE_TEMP_WW,
    CanonicalKey.LOWER_LIMIT_HZG,
    CanonicalKey.LOWER_LIMIT_WW,
}


def test_all_canonical_keys_have_translations():
    """Verify all canonical keys that need translations have them.
    
    Section keys don't need their own translations (they're just grouping),
    but field keys do need translations to be extracted from HTML.
    """
    all_keys = get_canonical_keys_defined()
    keys_with_translations = get_canonical_keys_with_translations()
    
    # Filter out section keys (they don't need translations)
    section_keys = {k for k in all_keys if "SECTION" in k.value}
    
    # Required keys are all non-section, non-optional keys
    required_keys = all_keys - section_keys - OPTIONAL_CANONICAL_KEYS
    
    # Check which required keys lack translations
    missing_translations = required_keys - keys_with_translations
    
    if missing_translations:
        pytest.fail(
            f"Required canonical keys lack i18n translations:\n  "
            f"{', '.join(sorted(k.value for k in missing_translations))}\n\n"
            f"Add translations to custom_components/stiebel_eltron_http/i18n/*.py files"
        )


@pytest.mark.parametrize("lang", ["en", "de", "da", "fi", "sv", "nl", "fr", "it", "pl", "cs", "es", "hu"])
def test_critical_sensors_extracted_all_languages(lang):
    """Verify critical sensors are extracted in all languages.
    
    Critical sensors are those that should always be present on all systems.
    This test would have caught the missing compressor_starts translations.
    """
    # These sensor keys should ALWAYS be extractable from s=1,1 (info heatpump page)
    critical_sensor_keys = {
        "outside_temperature",
        "return_temperature",
        "supply_temperature",
        "compressor_starts",
        "defrost_starts",
        "runtime_vd_heating",
        "runtime_vd_dhw",
    }
    
    html_file = TESTDATA_DIR / f"s_1_1_{lang}.html"
    if not html_file.exists():
        pytest.skip(f"Test data for {lang} not available")
    
    client = StiebelEltronScrapingClient("dummy", None)
    html = html_file.read_text(encoding="utf-8")
    result = client._extract_info_heatpump(html)
    
    extracted = set(result.keys())
    missing = critical_sensor_keys - extracted
    
    if missing:
        pytest.fail(
            f"Critical sensors missing in {lang} extraction:\n  "
            f"{', '.join(sorted(missing))}\n"
            f"Extracted: {', '.join(sorted(extracted))}\n\n"
            f"If sensor is not extracted, check:\n"
            f"1. i18n translations in custom_components/stiebel_eltron_http/i18n/{lang}.py\n"
            f"2. HEADER_ALIASES contains the canonical key\n"
            f"3. Test HTML file has the expected data structure"
        )


def test_no_none_values_in_extracted_data():
    """Verify that extracted data never contains None values.
    
    If a sensor can't be extracted, it should be omitted from the result,
    not included with a None value.
    """
    client = StiebelEltronScrapingClient("dummy", None)
    
    for html_file in TESTDATA_DIR.glob("s_*.html"):
        html = html_file.read_text(encoding="utf-8")
        
        for extractor in [
            client._extract_info_heatpump,
            client._extract_info_system,
            client._extract_diagnosis_system,
            client._extract_start_page,
        ]:
            result = extractor(html)
            
            none_values = [key.value for key, val in result.items() if val is None]
            if none_values:
                pytest.fail(
                    f"File {html_file.name} extractor {extractor.__name__} "
                    f"returned None values for keys: {', '.join(none_values)}"
                )


def test_all_translations_have_canonical_keys():
    """Verify that all translations in HEADER_ALIASES map to valid canonical keys.
    
    This prevents typos or orphaned translations that don't map to any canonical key.
    """
    defined_keys = get_canonical_keys_defined()
    translated_keys = get_canonical_keys_with_translations()
    
    orphaned = translated_keys - defined_keys
    
    if orphaned:
        pytest.fail(
            f"HEADER_ALIASES contains translations for undefined canonical keys:\n  "
            f"{', '.join(sorted(k.value for k in orphaned))}\n\n"
            f"Either add these keys to CanonicalKey enum or remove the translations"
        )

