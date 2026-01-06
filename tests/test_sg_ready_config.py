"""Test the SG Ready configuration scraping functionality."""

import pytest
import os
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import (
    SG_READY_ENABLED_KEY,
    SG_READY_INPUT_KEY,
    SG_READY_HEATING_BUFFER_KEY,
    SG_READY_UPPER_TEMP_HC1_KEY,
    SG_READY_UPPER_TEMP_HC2_KEY,
    SG_READY_UPPER_TEMP_DHW_KEY,
)


def test_extract_sg_ready_config():
    """Test extraction of SG Ready configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_14_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "SG_READY")
    
    # Verify extracted values exist (values may vary by system)
    # SG Ready enabled (enum: OFF/ON)
    assert SG_READY_ENABLED_KEY in result
    assert result[SG_READY_ENABLED_KEY] in ["OFF", "ON"]
    
    # SG Ready input (enum)
    assert SG_READY_INPUT_KEY in result
    assert result[SG_READY_INPUT_KEY] in ["OFF", "MODBUS", "CAN BUS", "ISG PLUS"]
    
    # Heating buffer configuration (enum)
    assert SG_READY_HEATING_BUFFER_KEY in result
    assert result[SG_READY_HEATING_BUFFER_KEY] in ["no_buffer", "buffer_with_mixer", "buffer_without_mixer"]
    
    # Upper temperature limits (float)
    assert SG_READY_UPPER_TEMP_HC1_KEY in result
    assert isinstance(result[SG_READY_UPPER_TEMP_HC1_KEY], (int, float))
    assert 20.0 <= result[SG_READY_UPPER_TEMP_HC1_KEY] <= 50.0
    
    assert SG_READY_UPPER_TEMP_HC2_KEY in result
    assert isinstance(result[SG_READY_UPPER_TEMP_HC2_KEY], (int, float))
    assert 20.0 <= result[SG_READY_UPPER_TEMP_HC2_KEY] <= 30.0
    
    assert SG_READY_UPPER_TEMP_DHW_KEY in result
    assert isinstance(result[SG_READY_UPPER_TEMP_DHW_KEY], (int, float))
    assert 40.0 <= result[SG_READY_UPPER_TEMP_DHW_KEY] <= 80.0
