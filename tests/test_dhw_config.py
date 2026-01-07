"""Test the DHW configuration scraping functionality."""

import pytest
import os
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import (
    DHW_COMFORT_TEMPERATURE_KEY,
    DHW_ECO_TEMPERATURE_KEY,
    DHW_MODE_KEY,
    DHW_HYSTERESIS_KEY,
    DHW_STAGES_KEY,
    DHW_LEARNING_FUNCTION_KEY,
    DHW_COMBI_CYLINDER_KEY,
    DHW_OUTPUT_SUMMER_KEY,
    DHW_OUTPUT_WINTER_KEY,
    DHW_MAX_FLOW_TEMP_KEY,
    DHW_PASTEURISATION_KEY,
    DHW_PASTEURISATION_TEMP_KEY,
    DHW_EXTERNAL_SOURCE_KEY,
    DHW_EXTERNAL_DUAL_MODE_TEMP_KEY,
    DHW_EXTERNAL_LOWER_LIMIT_KEY,
    DHW_EXTERNAL_PWM_KEY,
)


def test_extract_dhw_temperatures_config():
    """Test extraction of DHW Temperatures configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_0_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_TEMPS")
    
    # Verify extracted values
    assert DHW_COMFORT_TEMPERATURE_KEY in result
    assert result[DHW_COMFORT_TEMPERATURE_KEY] == 50.0
    
    assert DHW_ECO_TEMPERATURE_KEY in result
    assert result[DHW_ECO_TEMPERATURE_KEY] == 45.0


def test_extract_dhw_standard_config():
    """Test extraction of DHW Standard Setting configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_1_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_STANDARD")
    
    # Verify extracted values
    assert DHW_MODE_KEY in result
    assert result[DHW_MODE_KEY] == "priority_operation"
    
    assert DHW_HYSTERESIS_KEY in result
    assert result[DHW_HYSTERESIS_KEY] == 5.0
    
    assert DHW_STAGES_KEY in result
    assert result[DHW_STAGES_KEY] == 1


def test_extract_dhw_learning_config():
    """Test extraction of DHW Learning Function configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_2_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_LEARNING")
    
    # Verify extracted values
    assert DHW_LEARNING_FUNCTION_KEY in result
    assert result[DHW_LEARNING_FUNCTION_KEY] == "off"


def test_extract_dhw_combi_config():
    """Test extraction of DHW Combi Cylinder configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_3_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_COMBI")
    
    # Verify extracted values
    assert DHW_COMBI_CYLINDER_KEY in result
    assert result[DHW_COMBI_CYLINDER_KEY] == "off"


def test_extract_dhw_output_config():
    """Test extraction of DHW Output configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_4_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_OUTPUT")
    
    # Verify extracted values
    assert DHW_OUTPUT_SUMMER_KEY in result
    assert result[DHW_OUTPUT_SUMMER_KEY] == 5
    
    assert DHW_OUTPUT_WINTER_KEY in result
    assert result[DHW_OUTPUT_WINTER_KEY] == 15


def test_extract_dhw_max_flow_config():
    """Test extraction of DHW Maximum Flow Temperature configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_5_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_MAX_FLOW")
    
    # Verify extracted values
    assert DHW_MAX_FLOW_TEMP_KEY in result
    assert result[DHW_MAX_FLOW_TEMP_KEY] == 65.0


def test_extract_dhw_pasteurisation_config():
    """Test extraction of DHW Pasteurisation configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_6_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_PASTEUR")
    
    # Verify extracted values
    assert DHW_PASTEURISATION_KEY in result
    assert result[DHW_PASTEURISATION_KEY] == "off"
    
    assert DHW_PASTEURISATION_TEMP_KEY in result
    assert result[DHW_PASTEURISATION_TEMP_KEY] == 60.0


def test_extract_dhw_external_config():
    """Test extraction of DHW External Heat Source configuration from HTML page."""
    client = StiebelEltronScrapingClient(
        host="test.local",
        session=None,
        language="en",
    )
    
    # Load test file
    testdata_dir = os.path.join(os.getcwd(), "scripts", "testdata")
    html_file = os.path.join(testdata_dir, "_s_4_3_7_en.html")
    
    if not os.path.exists(html_file):
        pytest.skip(f"Test file not found: {html_file}")
    
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract configuration
    result = client._extract_heating_config(html_content, "DHW_EXTERNAL")
    
    # Verify extracted values
    assert DHW_EXTERNAL_SOURCE_KEY in result
    assert result[DHW_EXTERNAL_SOURCE_KEY] == "supported"
    
    assert DHW_EXTERNAL_DUAL_MODE_TEMP_KEY in result
    assert result[DHW_EXTERNAL_DUAL_MODE_TEMP_KEY] == -7.0
    
    # Lower limit and PWM are OFF (36864), should not be in result
    assert DHW_EXTERNAL_LOWER_LIMIT_KEY not in result
    assert DHW_EXTERNAL_PWM_KEY not in result
