"""Constants for stiebel_eltron_http."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "stiebel_eltron_http"
HTTP_CONNECTION_TIMEOUT = 30  # seconds
EXPECTED_HTML_TITLE = "STIEBEL ELTRON Reglersteuerung"

# Configuration keys
CONF_LANGUAGE = "language"
# Special value meaning: auto-detect language during config
AUTO_LANGUAGE = "auto"
# Supported languages for scraping/lookup (include 'auto' for auto-detect)
# Languages: auto, English, German, French, Dutch, Italian, Swedish, Spanish, Polish, Czech, Hungarian, Finnish, Danish
SUPPORTED_LANGUAGES = (AUTO_LANGUAGE, "en", "de", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da")
# Default language
DEFAULT_LANGUAGE = "en"

# Optional config to control whether the integration should also fetch the
# Energy page (`/?s=1,8`) which some devices expose. Default True.
CONF_FETCH_ENERGY = "fetch_energy"
DEFAULT_FETCH_ENERGY = True

# How often to refresh data (in minutes). Can be configured via options.
CONF_UPDATE_INTERVAL = "update_interval_minutes"
DEFAULT_UPDATE_INTERVAL_MINUTES = 1

INFO_SYSTEM_PATH = "/?s=1,0"
INFO_HEATPUMP_PATH = "/?s=1,1"
INFO_ENERGY_PATH = "/?s=1,8"
DIAGNOSIS_SYSTEM_PATH = "/?s=2,7"
PROFILE_NETWORK_PATH = "/?s=5,0"
WCCI_PATH = "/?s=4,25"
WCCI_ENDPOINT = "/external_connections/wcci/wcci_endpoint.php"
HEATING_HC1_PATH = "/?s=4,2,0"
HEATING_HC2_PATH = "/?s=4,2,1"
HEATING_BASIC_PATH = "/?s=4,2,2"

# Sensor keys
ROOM_TEMPERATURE_KEY = "room_temperature"
ROOM_HUMIDITY_KEY = "room_relative_humidity"
DHW_TEMPERATURE_KEY = "dhw_temperature"
DHW_SET_TEMPERATURE_KEY = "dhw_set_temperature"
OUTSIDE_TEMPERATURE_KEY = "outside_temperature"
TOTAL_HEAT_PRODUCED_KEY = "total_heat_produced"
HEAT_PRODUCED_TODAY_KEY = "heat_produced_today"
TOTAL_DHW_PRODUCED_KEY = "total_dhw_produced"
DHW_PRODUCED_TODAY_KEY = "dhw_produced_today"
TOTAL_HEATING_CONSUMED_KEY = "total_heating_consumed"
HEATING_CONSUMED_TODAY_KEY = "heating_consumed_today"
TOTAL_DHW_CONSUMED_KEY = "total_dhw_consumed"
DHW_CONSUMED_TODAY_KEY = "dhw_consumed_today"

# Efficiency / COP metrics (from the EFFIZIENZ / EFFICIENCY table)
EFFICIENCY_HEATING_TODAY_KEY = "efficiency_heating_today"
EFFICIENCY_HEATING_1_12M_KEY = "efficiency_heating_1_12m"
EFFICIENCY_HEATING_13_24M_KEY = "efficiency_heating_13_24m"
EFFICIENCY_DHW_TODAY_KEY = "efficiency_dhw_today"
EFFICIENCY_DHW_1_12M_KEY = "efficiency_dhw_1_12m"
EFFICIENCY_DHW_13_24M_KEY = "efficiency_dhw_13_24m"

# Additional process metrics from the ISG "PROZESSDATEN" / heat pump pages
RETURN_TEMPERATURE_KEY = "return_temperature"
SUPPLY_TEMPERATURE_KEY = "supply_temperature"
FROST_PROTECTION_TEMPERATURE_KEY = "frost_protection_temperature"
OUTSIDE_TEMPERATURE_KEY = OUTSIDE_TEMPERATURE_KEY  # alias (already defined)
COMPRESSOR_INLET_TEMPERATURE_KEY = "compressor_inlet_temperature"
HOT_GAS_TEMPERATURE_KEY = "hot_gas_temperature"
CONDENSER_TEMPERATURE_KEY = "condenser_temperature"
OIL_SUMP_TEMPERATURE_KEY = "oil_sump_temperature"
LOW_PRESSURE_KEY = "low_pressure"
HIGH_PRESSURE_KEY = "high_pressure"
WATER_FLOW_KEY = "water_flow"
INVERTER_CURRENT_KEY = "inverter_current"
INVERTER_VOLTAGE_KEY = "inverter_voltage"
COMPRESSOR_SPEED_ACTUAL_KEY = "compressor_speed_actual"
COMPRESSOR_SPEED_TARGET_KEY = "compressor_speed_target"
FAN_POWER_RELATIVE_KEY = "fan_power_relative"
EVAPORATOR_INLET_TEMPERATURE_KEY = "evaporator_inlet_temperature"
EVAPORATOR_OUTLET_TEMPERATURE_KEY = "evaporator_outlet_temperature"
INVERTER_POWER_INPUT_KEY = "inverter_power_input"
INVERTER_POWER_KEY = "inverter_power"

# Heating circuit 1 (HK 1)
ACTUAL_TEMPERATURE_HK_1_KEY = "actual_temperature_hk_1"
SET_TEMPERATURE_HK_1_KEY = "set_temperature_hk_1"

# Heating circuit 2 (HK 2)
ACTUAL_TEMPERATURE_HK_2_KEY = "actual_temperature_hk_2"
SET_TEMPERATURE_HK_2_KEY = "set_temperature_hk_2"

# Buffer temperatures
ACTUAL_BUFFER_TEMPERATURE_KEY = "actual_buffer_temperature"
SET_BUFFER_TEMPERATURE_KEY = "set_buffer_temperature"

# External heat source temperatures
EXTERNAL_ACTUAL_TEMPERATURE_KEY = "external_actual_temperature"
EXTERNAL_SET_TEMPERATURE_KEY = "external_set_temperature"

# Dual mode temperatures
DUAL_MODE_TEMP_HZG_KEY = "dual_mode_temp_hzg"
DUAL_MODE_TEMP_WW_KEY = "dual_mode_temp_ww"

# Application limits
LOWER_LIMIT_HZG_KEY = "lower_limit_hzg"
LOWER_LIMIT_WW_KEY = "lower_limit_ww"

# Runtime hours and counters
RUNTIME_VD_HEATING_KEY = "runtime_vd_heating"
RUNTIME_VD_DHW_KEY = "runtime_vd_dhw"
RUNTIME_VD_DEFROST_KEY = "runtime_vd_defrost"
DEFROST_TIME_KEY = "defrost_time"
DEFROST_STARTS_KEY = "defrost_starts"
COMPRESSOR_STARTS_KEY = "compressor_starts"


# Other keys
MAC_ADDRESS_KEY = "mac_address"

# Start page (s=0) sensors
START_OPERATION_MODE_KEY = "start_operation_mode"
START_PORTAL_OK = "start_portal_ok"
START_SYSTEM_OK = "start_system_ok"
START_SG_READY_ACTIVE = "start_sg_ready_active"
START_SG_READY_STATE = "start_sg_ready_state"
START_ENERGY_MGMT_OK = "start_energy_mgmt_ok"

# WCCI (Water Control and Communication Interface) - Power Influence (s=4,25)
WCCI_INPUT_MODE_KEY = "wcci_input_mode"
WCCI_INPUT_SOURCE_KEY = "wcci_input_source"
WCCI_BUFFER_KEY = "wcci_buffer"
WCCI_OPERATING_MODE_KEY = "wcci_operating_mode"
WCCI_USER_POWER_LIMIT_KEY = "wcci_user_power_limit"
WCCI_LOAD_TEMP_ROOM_1_KEY = "wcci_load_temp_room_1"
WCCI_LOAD_TEMP_ROOM_2_KEY = "wcci_load_temp_room_2"
WCCI_LOAD_TEMP_ROOM_3_KEY = "wcci_load_temp_room_3"
WCCI_LOAD_TEMP_ROOM_4_KEY = "wcci_load_temp_room_4"
WCCI_LOAD_TEMP_ROOM_5_KEY = "wcci_load_temp_room_5"
WCCI_LOAD_TEMP_BUFFER_KEY = "wcci_load_temp_buffer"
WCCI_LOAD_TEMP_DHW_KEY = "wcci_load_temp_dhw"
WCCI_LIMIT_FUNCTIONALITY_BLOCKED_KEY = "wcci_limit_functionality_blocked"

# Heating Configuration - Circuit 1 (s=4,2,0)
HC1_COMFORT_TEMPERATURE_KEY = "hc1_comfort_temperature"
HC1_ECO_TEMPERATURE_KEY = "hc1_eco_temperature"
HC1_MINIMUM_TEMPERATURE_KEY = "hc1_minimum_temperature"
HC1_HEATING_CURVE_RISE_KEY = "hc1_heating_curve_rise"

# Heating Configuration - Circuit 2 (s=4,2,1)
HC2_COMFORT_TEMPERATURE_KEY = "hc2_comfort_temperature"
HC2_ECO_TEMPERATURE_KEY = "hc2_eco_temperature"
HC2_MINIMUM_TEMPERATURE_KEY = "hc2_minimum_temperature"
HC2_MAXIMUM_TEMPERATURE_KEY = "hc2_maximum_temperature"
HC2_MIXER_DYNAMICS_KEY = "hc2_mixer_dynamics"
HC2_HEATING_CURVE_RISE_KEY = "hc2_heating_curve_rise"

# Heating Configuration - Basic Settings (s=4,2,2)
HEATING_BUFFER_OPERATION_KEY = "heating_buffer_operation"
HEATING_MAX_RETURN_TEMP_KEY = "heating_max_return_temp"
HEATING_MAX_FLOW_TEMP_KEY = "heating_max_flow_temp"
HEATING_FIXED_VALUE_OP_KEY = "heating_fixed_value_operation"
HEATING_FROST_PROTECTION_KEY = "heating_frost_protection"

# Summer Mode configuration keys
HEATING_SUMMER_MODE_KEY = "heating_summer_mode"
HEATING_SUMMER_OUTSIDE_TEMP_KEY = "heating_summer_outside_temp"
HEATING_SUMMER_HEAT_BUFFER_KEY = "heating_summer_heat_buffer"

# Pump Cycles configuration key
HEATING_PUMP_CYCLES_KEY = "heating_pump_cycles"

# External Heat Source configuration keys
HEATING_EXTERNAL_SOURCE_KEY = "heating_external_source"
HEATING_EXTERNAL_CURVE_GAP_KEY = "heating_external_curve_gap"
HEATING_EXTERNAL_BLOCKING_TIME_KEY = "heating_external_blocking_time"
HEATING_EXTERNAL_DUAL_MODE_TEMP_KEY = "heating_external_dual_mode_temp"
HEATING_EXTERNAL_LOWER_LIMIT_KEY = "heating_external_lower_limit"

# Hot Water (DHW) Configuration Keys (s=4,3,X)
# Temperatures (s=4,3,0)
DHW_COMFORT_TEMPERATURE_KEY = "dhw_comfort_temperature"
DHW_ECO_TEMPERATURE_KEY = "dhw_eco_temperature"

# Standard Setting (s=4,3,1)
DHW_MODE_KEY = "dhw_mode"
DHW_HYSTERESIS_KEY = "dhw_hysteresis"
DHW_STAGES_KEY = "dhw_stages"

# Learning Function (s=4,3,2)
DHW_LEARNING_FUNCTION_KEY = "dhw_learning_function"

# Combi Cylinder (s=4,3,3)
DHW_COMBI_CYLINDER_KEY = "dhw_combi_cylinder"

# Output (s=4,3,4)
DHW_OUTPUT_SUMMER_KEY = "dhw_output_summer"
DHW_OUTPUT_WINTER_KEY = "dhw_output_winter"

# Maximum Flow Temperature (s=4,3,5)
DHW_MAX_FLOW_TEMP_KEY = "dhw_max_flow_temp"

# Pasteurisation (s=4,3,6)
DHW_PASTEURISATION_KEY = "dhw_pasteurisation"
DHW_PASTEURISATION_TEMP_KEY = "dhw_pasteurisation_temp"

# External Heat Source (s=4,3,7)
DHW_EXTERNAL_SOURCE_KEY = "dhw_external_source"
DHW_EXTERNAL_DUAL_MODE_TEMP_KEY = "dhw_external_dual_mode_temp"
DHW_EXTERNAL_LOWER_LIMIT_KEY = "dhw_external_lower_limit"
DHW_EXTERNAL_PWM_KEY = "dhw_external_pwm"

# SG Ready / Energy Management Configuration Keys (s=4,14)
SG_READY_ENABLED_KEY = "sg_ready_enabled"
SG_READY_INPUT_KEY = "sg_ready_input"
SG_READY_HEATING_BUFFER_KEY = "sg_ready_heating_buffer"
SG_READY_UPPER_TEMP_HC1_KEY = "sg_ready_upper_temp_hc1"
SG_READY_UPPER_TEMP_HC2_KEY = "sg_ready_upper_temp_hc2"
SG_READY_UPPER_TEMP_DHW_KEY = "sg_ready_upper_temp_dhw"
