"""Check which sensors don't get extracted values from test data."""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from custom_components.stiebel_eltron_http.const import (
    COMPRESSOR_STARTS_KEY,
    DEFROST_STARTS_KEY,
    DEFROST_TIME_KEY,
    RUNTIME_VD_HEATING_KEY,
    RUNTIME_VD_DHW_KEY,
    RUNTIME_VD_DEFROST_KEY,
    DHW_TEMPERATURE_KEY,
    OUTSIDE_TEMPERATURE_KEY,
    # Add all sensor keys
)
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

# Get all keys from const.py
import custom_components.stiebel_eltron_http.const as const
sensor_keys = {name: getattr(const, name) for name in dir(const) if name.endswith('_KEY') and not name.startswith('_')}

# Extract from test files
client = StiebelEltronScrapingClient('dummy', None)

testdata = Path('scripts/testdata')
test_files = {
    's_1_1': client._extract_info_heatpump,
    's_1_8': client._extract_info_system,
    's_2_7': client._extract_diagnosis_system,
}

all_extracted = set()
for pattern, extractor in test_files.items():
    for html_file in testdata.glob(f'{pattern}_*.html'):
        html = html_file.read_text(encoding='utf-8')
        result = extractor(html)
        all_extracted.update(result.keys())

# Check which sensors are missing
all_sensor_values = set(sensor_keys.values())
missing = all_sensor_values - all_extracted

# Filter out known optional sensors
OPTIONAL = {
    'mac_address', 'room_relative_humidity', 'room_temperature',
    'external_actual_temperature', 'external_set_temperature',
    'dhw_set_temperature', 'start_operation_mode', 'start_sg_ready_active',
    'start_sg_ready_state', 'start_energy_mgmt_ok', 'start_portal_ok',
    'start_system_ok', 'actual_temperature_hk_1', 'set_temperature_hk_1',
    'actual_temperature_hk_2', 'set_temperature_hk_2',
    'actual_buffer_temperature', 'set_buffer_temperature',
    # Config page sensors
    'hc1_comfort_temperature', 'hc1_eco_temperature', 'hc1_minimum_temperature',
    'hc1_heating_curve_rise', 'hc2_comfort_temperature', 'hc2_eco_temperature',
    'hc2_minimum_temperature', 'hc2_maximum_temperature', 'hc2_mixer_dynamics',
    'hc2_heating_curve_rise', 'heating_buffer_operation', 'heating_max_return_temp',
    'heating_max_flow_temp', 'heating_fixed_value_operation', 'heating_frost_protection',
    'heating_summer_mode', 'heating_summer_outside_temp', 'heating_summer_heat_buffer',
    'heating_pump_cycles', 'heating_external_source', 'heating_external_curve_gap',
    'heating_external_blocking_time', 'heating_external_dual_mode_temp',
    'heating_external_lower_limit', 'dhw_comfort_temperature', 'dhw_eco_temperature',
    'dhw_mode', 'dhw_hysteresis', 'dhw_stages', 'dhw_learning_function',
    'dhw_combi_cylinder', 'dhw_output_summer', 'dhw_output_winter',
    'dhw_max_flow_temp', 'dhw_pasteurisation', 'dhw_pasteurisation_temp',
    'dhw_external_source', 'dhw_external_dual_mode_temp', 'dhw_external_lower_limit',
    'dhw_external_pwm', 'sg_ready_enabled', 'sg_ready_input', 'sg_ready_heating_buffer',
    'sg_ready_upper_temp_hc1', 'sg_ready_upper_temp_hc2', 'sg_ready_upper_temp_dhw',
}

truly_missing = missing - OPTIONAL

if truly_missing:
    print("Sensors with no extracted values:")
    for key in sorted(truly_missing):
        print(f"  - {key}")
else:
    print("All non-optional sensors have values!")

print(f"\nTotal sensors defined: {len(all_sensor_values)}")
print(f"Sensors extracted: {len(all_extracted)}")
print(f"Optional sensors: {len(OPTIONAL)}")
print(f"Missing sensors: {len(truly_missing)}")
