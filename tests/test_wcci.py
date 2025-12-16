"""Test the WCCI (Power Influence) scraping functionality."""

import pytest
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import (
    WCCI_INPUT_MODE_KEY,
    WCCI_INPUT_SOURCE_KEY,
    WCCI_BUFFER_KEY,
    WCCI_OPERATING_MODE_KEY,
    WCCI_USER_POWER_LIMIT_KEY,
    WCCI_LOAD_TEMP_ROOM_1_KEY,
    WCCI_LOAD_TEMP_ROOM_2_KEY,
    WCCI_LOAD_TEMP_ROOM_3_KEY,
    WCCI_LOAD_TEMP_ROOM_4_KEY,
    WCCI_LOAD_TEMP_ROOM_5_KEY,
    WCCI_LOAD_TEMP_BUFFER_KEY,
    WCCI_LOAD_TEMP_DHW_KEY,
    WCCI_LIMIT_FUNCTIONALITY_BLOCKED_KEY,
)


def test_extract_wcci_data():
    """Test extraction of WCCI configuration data from JSON response."""
    # Create client instance
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Sample WCCI JSON response (scaled values as returned by ISG)
    wcci_json = {
        "buffer": "NOBUFFER",
        "inputSource": "MODBUS",
        "inputMode": "SGREADY",
        "operatingMode": "NO_LIMITATION",
        "userPowerLimit": 420,  # 4.20 kW (scaled by 100)
        "userPowerLimit_min": 0,
        "userPowerLimit_max": 707,
        "loadTempRoom_1": 230,  # 23.0°C (scaled by 10)
        "loadTempRoom_1_min": 20,
        "loadTempRoom_1_max": 50,
        "loadTempRoom_2": 230,
        "loadTempRoom_2_min": 20,
        "loadTempRoom_2_max": 30,
        "loadTempRoom_3": 230,
        "loadTempRoom_3_min": 20,
        "loadTempRoom_3_max": 30,
        "loadTempRoom_4": 230,
        "loadTempRoom_4_min": 20,
        "loadTempRoom_4_max": 30,
        "loadTempRoom_5": 230,
        "loadTempRoom_5_min": 20,
        "loadTempRoom_5_max": 30,
        "loadTempBuffer": 400,  # 40.0°C (scaled by 10)
        "loadTempBuffer_min": 20,
        "loadTempBuffer_max": 50,
        "loadTempDhw": 500,  # 50.0°C (scaled by 10)
        "loadTempDhw_min": 40,
        "loadTempDhw_max": 80,
        "limitFunctionalityBlocked": False,
    }
    
    # Extract data
    result = client._extract_wcci_data(wcci_json)
    
    # Verify all fields are extracted correctly
    assert result[WCCI_INPUT_MODE_KEY] == "SGREADY"
    assert result[WCCI_INPUT_SOURCE_KEY] == "MODBUS"
    assert result[WCCI_BUFFER_KEY] == "NOBUFFER"
    assert result[WCCI_OPERATING_MODE_KEY] == "NO_LIMITATION"
    assert result[WCCI_LIMIT_FUNCTIONALITY_BLOCKED_KEY] is False
    
    # Verify power limit is scaled correctly (420 / 100 = 4.2 kW)
    assert result[WCCI_USER_POWER_LIMIT_KEY] == 4.2
    
    # Verify temperatures are scaled correctly (230 / 10 = 23.0°C)
    assert result[WCCI_LOAD_TEMP_ROOM_1_KEY] == 23.0
    assert result[WCCI_LOAD_TEMP_ROOM_2_KEY] == 23.0
    assert result[WCCI_LOAD_TEMP_ROOM_3_KEY] == 23.0
    assert result[WCCI_LOAD_TEMP_ROOM_4_KEY] == 23.0
    assert result[WCCI_LOAD_TEMP_ROOM_5_KEY] == 23.0
    assert result[WCCI_LOAD_TEMP_BUFFER_KEY] == 40.0
    assert result[WCCI_LOAD_TEMP_DHW_KEY] == 50.0


def test_extract_wcci_data_partial():
    """Test extraction with minimal WCCI data."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Minimal WCCI response
    wcci_json = {
        "inputMode": "OFF",
        "inputSource": "ISG",
        "userPowerLimit": 0,
        "limitFunctionalityBlocked": True,
    }
    
    result = client._extract_wcci_data(wcci_json)
    
    assert result[WCCI_INPUT_MODE_KEY] == "OFF"
    assert result[WCCI_INPUT_SOURCE_KEY] == "ISG"
    assert result[WCCI_USER_POWER_LIMIT_KEY] == 0.0
    assert result[WCCI_LIMIT_FUNCTIONALITY_BLOCKED_KEY] is True
    # Temperature fields should not be present if not in source data
    assert WCCI_LOAD_TEMP_ROOM_1_KEY not in result


def test_extract_wcci_data_empty():
    """Test extraction with empty WCCI data."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    wcci_json = {}
    result = client._extract_wcci_data(wcci_json)
    
    # Should return empty dict
    assert result == {}


def test_extract_wcci_data_numeric_mode():
    """Test extraction when mode values are numeric instead of strings."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Some ISG versions may return numeric codes
    wcci_json = {
        "inputMode": 0,  # Numeric instead of string
        "inputSource": 3,
        "buffer": 0,
        "operatingMode": 0,
        "limitFunctionalityBlocked": False,
    }
    
    result = client._extract_wcci_data(wcci_json)
    
    # Should convert to strings
    assert result[WCCI_INPUT_MODE_KEY] == "0"
    assert result[WCCI_INPUT_SOURCE_KEY] == "3"
    assert result[WCCI_BUFFER_KEY] == "0"
    assert result[WCCI_OPERATING_MODE_KEY] == "0"
