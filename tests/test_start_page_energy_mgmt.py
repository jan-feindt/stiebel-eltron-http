"""Test extraction of Energy Management status from start page (s=0)."""

import pathlib

import pytest

from custom_components.stiebel_eltron_http.const import (
    START_ENERGY_MGMT_OK,
    START_OPERATION_MODE_KEY,
    START_SG_READY_ACTIVE,
    START_SG_READY_STATE,
)
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient


@pytest.mark.parametrize("language", ["en", "de", "fr", "nl", "it", "sv", "pl", "cs", "hu", "es", "fi", "da"])
def test_extract_start_page_energy_management_all_languages(language):
    """Test extraction of Energy Management/SG Ready status from updated start page in all languages."""
    # Read the updated start page testdata
    test_file = pathlib.Path(__file__).parent.parent / "scripts" / "testdata" / f"s_0_0_{language}.html"
    
    if not test_file.exists():
        pytest.skip(f"Test file not found: {test_file}")
    
    with open(test_file, encoding="utf-8") as f:
        html = f.read()
    
    scraper = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language=language,
    )
    result = scraper._extract_start_page(html)
    
    # Verify operation mode is still extracted
    assert START_OPERATION_MODE_KEY in result
    
    # Verify new Energy Management fields
    assert START_ENERGY_MGMT_OK in result
    assert result[START_ENERGY_MGMT_OK] == "OK"
    
    assert START_SG_READY_ACTIVE in result
    assert result[START_SG_READY_ACTIVE] == "on"
    
    assert START_SG_READY_STATE in result
    assert result[START_SG_READY_STATE] == 2
    assert isinstance(result[START_SG_READY_STATE], int)


def test_extract_start_page_energy_management():
    """Test extraction of Energy Management/SG Ready status from updated start page."""
    # Read the updated start page testdata
    test_file = pathlib.Path(__file__).parent.parent / "scripts" / "testdata" / "s_0_0_en.html"
    
    with open(test_file, encoding="utf-8") as f:
        html = f.read()
    
    scraper = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    result = scraper._extract_start_page(html)
    
    # Verify operation mode is still extracted
    assert START_OPERATION_MODE_KEY in result
    assert result[START_OPERATION_MODE_KEY] == "programmed_operation"
    
    # Verify new Energy Management fields
    assert START_ENERGY_MGMT_OK in result
    assert result[START_ENERGY_MGMT_OK] == "OK"
    
    assert START_SG_READY_ACTIVE in result
    assert result[START_SG_READY_ACTIVE] == "on"
    
    assert START_SG_READY_STATE in result
    assert result[START_SG_READY_STATE] == 2
    assert isinstance(result[START_SG_READY_STATE], int)
