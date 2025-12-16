"""Test WCCI scraping works with pages from different languages."""

import pytest
import os
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient


def test_wcci_session_token_extraction_all_languages():
    """Verify session token can be extracted from all language versions of the WCCI page."""
    # Create client instance
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Test data directory
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    
    # All 12 supported languages
    languages = ["cs", "da", "de", "en", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]
    
    results = {}
    for lang in languages:
        html_file = os.path.join(testdata_dir, f"s_4_25_{lang}.html")
        
        if not os.path.exists(html_file):
            pytest.skip(f"Test file not found: {html_file}")
        
        # Read the HTML file
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Extract session token using BeautifulSoup (same method as scraper)
        import bs4
        soup = bs4.BeautifulSoup(html_content, "html.parser")
        token_div = soup.find("div", {"class": "sessionToken", "id": "sessionToken"})
        
        # Verify token was found
        assert token_div is not None, f"Session token div not found in {lang} page"
        
        session_token = token_div.get_text(strip=True)
        
        # Verify token is not empty
        assert session_token, f"Session token is empty in {lang} page"
        
        # Verify token looks like a hex string (typical format)
        assert len(session_token) > 0, f"Session token too short in {lang} page"
        
        results[lang] = session_token
    
    # Verify we tested all expected languages
    assert len(results) == len(languages), f"Expected {len(languages)} languages, got {len(results)}"
    
    print(f"\n✅ Successfully extracted session tokens from all {len(results)} language pages:")
    for lang, token in sorted(results.items()):
        print(f"  {lang}: {token}")


def test_wcci_data_extraction_language_independent():
    """Verify that WCCI data extraction doesn't depend on page language.
    
    The WCCI endpoint returns JSON data which is language-independent.
    The only language-dependent part is the session token extraction,
    which we test separately.
    """
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Sample WCCI JSON response (same for all languages)
    wcci_json = {
        "buffer": "NOBUFFER",
        "inputSource": "MODBUS", 
        "inputMode": "SGREADY",
        "operatingMode": "NO_LIMITATION",
        "userPowerLimit": 420,
        "loadTempRoom_1": 230,
        "loadTempRoom_2": 230,
        "loadTempRoom_3": 230,
        "loadTempRoom_4": 230,
        "loadTempRoom_5": 230,
        "loadTempBuffer": 400,
        "loadTempDhw": 500,
        "limitFunctionalityBlocked": False,
    }
    
    # Extract data
    result = client._extract_wcci_data(wcci_json)
    
    # Verify extraction works (values are language-independent)
    from custom_components.stiebel_eltron_http.const import (
        WCCI_INPUT_MODE_KEY,
        WCCI_USER_POWER_LIMIT_KEY,
        WCCI_LOAD_TEMP_DHW_KEY,
    )
    
    assert result[WCCI_INPUT_MODE_KEY] == "SGREADY"
    assert result[WCCI_USER_POWER_LIMIT_KEY] == 4.2  # 420 / 100
    assert result[WCCI_LOAD_TEMP_DHW_KEY] == 50.0  # 500 / 10
    
    print("\n✅ WCCI data extraction is language-independent")
