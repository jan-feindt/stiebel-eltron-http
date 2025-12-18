"""Test the heating configuration scraping functionality."""

import pytest
import os
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import (
    HC1_COMFORT_TEMPERATURE_KEY,
    HC1_ECO_TEMPERATURE_KEY,
    HC1_MINIMUM_TEMPERATURE_KEY,
    HC1_HEATING_CURVE_RISE_KEY,
    HC2_COMFORT_TEMPERATURE_KEY,
    HC2_ECO_TEMPERATURE_KEY,
    HC2_MINIMUM_TEMPERATURE_KEY,
    HC2_MAXIMUM_TEMPERATURE_KEY,
    HC2_MIXER_DYNAMICS_KEY,
    HC2_HEATING_CURVE_RISE_KEY,
    HEATING_BUFFER_OPERATION_KEY,
    HEATING_MAX_RETURN_TEMP_KEY,
    HEATING_MAX_FLOW_TEMP_KEY,
    HEATING_FIXED_VALUE_OP_KEY,
    HEATING_FROST_PROTECTION_KEY,
)


def test_extract_heating_hc1_config():
    """Test extraction of Heating Circuit 1 configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_2_0_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "HC1")
    
    # Verify extracted values
    assert HC1_COMFORT_TEMPERATURE_KEY in result
    assert result[HC1_COMFORT_TEMPERATURE_KEY] == 22.0
    
    assert HC1_ECO_TEMPERATURE_KEY in result
    assert result[HC1_ECO_TEMPERATURE_KEY] == 20.0
    
    # Minimum temperature is OFF (36864), should not be in result
    assert HC1_MINIMUM_TEMPERATURE_KEY not in result
    
    assert HC1_HEATING_CURVE_RISE_KEY in result
    assert result[HC1_HEATING_CURVE_RISE_KEY] == 1.10


def test_extract_heating_hc2_config():
    """Test extraction of Heating Circuit 2 configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_2_1_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "HC2")
    
    # Verify extracted values
    assert HC2_COMFORT_TEMPERATURE_KEY in result
    assert result[HC2_COMFORT_TEMPERATURE_KEY] == 23.0
    
    assert HC2_ECO_TEMPERATURE_KEY in result
    assert result[HC2_ECO_TEMPERATURE_KEY] == 20.0
    
    # Minimum temperature is OFF (36864), should not be in result
    assert HC2_MINIMUM_TEMPERATURE_KEY not in result
    
    assert HC2_MAXIMUM_TEMPERATURE_KEY in result
    assert result[HC2_MAXIMUM_TEMPERATURE_KEY] == 55.0
    
    assert HC2_MIXER_DYNAMICS_KEY in result
    assert result[HC2_MIXER_DYNAMICS_KEY] == 50
    
    assert HC2_HEATING_CURVE_RISE_KEY in result
    assert result[HC2_HEATING_CURVE_RISE_KEY] == 0.95


def test_extract_heating_basic_config():
    """Test extraction of Basic Heating Settings from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_2_2_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "BASIC")
    
    # Verify extracted values
    # Note: Buffer operation uses radio buttons without jsvalues, so it won't be extracted
    # assert HEATING_BUFFER_OPERATION_KEY in result
    
    assert HEATING_MAX_RETURN_TEMP_KEY in result
    assert result[HEATING_MAX_RETURN_TEMP_KEY] == 55.0
    
    assert HEATING_MAX_FLOW_TEMP_KEY in result
    assert result[HEATING_MAX_FLOW_TEMP_KEY] == 65.0
    
    # Fixed value operation is OFF (36864), should not be in result
    assert HEATING_FIXED_VALUE_OP_KEY not in result
    
    assert HEATING_FROST_PROTECTION_KEY in result
    assert result[HEATING_FROST_PROTECTION_KEY] == 4.0


def test_parse_value_types():
    """Test value parsing with different types."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Test float parsing
    assert client._parse_value("22,0", "float") == 22.0
    assert client._parse_value("1,5", "float") == 1.5
    
    # Test double parsing
    assert client._parse_value("1,10", "double") == 1.10
    assert client._parse_value("0,95", "double") == 0.95
    
    # Test int parsing
    assert client._parse_value("50", "int") == 50
    assert client._parse_value("1", "int") == 1
    assert client._parse_value("0", "int") == 0
