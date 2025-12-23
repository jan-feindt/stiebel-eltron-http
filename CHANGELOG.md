# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-12-23

### Fixed
- **UnicodeDecodeError in WCCI scraper**: Added encoding fallback (UTF-8 → ISO-8859-1) to handle German umlauts and special characters in WCCI endpoint responses
- **UnboundLocalError in WCCI scraper**: Moved json import to top of file to fix exception handler reference error
- **ImportError for configuration paths**: Added missing PATH constants (HEATING_SUMMER_PATH, HEATING_PUMP_CYCLES_PATH, HEATING_EXTERNAL_PATH, and 8 DHW paths, plus SG_READY_PATH)
- **ValueError for sg_ready_enabled sensor**: Changed from boolean to string enum ("OFF"/"ON") to match sensor device class definition

### Added
- Translations for start page Energy Management sensors in all 12 languages (start_sg_ready_active, start_sg_ready_state, start_energy_mgmt_ok)

### Technical
- Enhanced error handling for non-UTF-8 encoded responses from older ISG devices
- Improved type consistency between scraper output and sensor definitions
- All configuration page paths now properly defined in const.py

## [0.2.1] - 2025-12-23

### Added
- **SG Ready / Energy Management Configuration** (s=4,14): 6 new configuration sensors
  - SG Ready enabled/disabled toggle
  - SG Ready input source selection (OFF/MODBUS/CAN BUS/ISG PLUS)
  - Heating buffer configuration (3 options)
  - Upper temperature limits for HC1, HC2, and DHW circuits
  - Full translation support across 12 languages
- **Energy Management Status on Start Page** (s=0): 3 new real-time status sensors
  - SG Ready active indicator (ON/OFF)
  - SG Ready operating state (1-4) showing current grid signal mode
  - Energy Management system health status (OK/ERROR)
- Multi-language regex pattern matching for German "Betriebszustand" and French "Statut d'exploitation"
- Comprehensive test coverage with 13 parametrized tests for all language variations

### Changed
- Updated start page testdata (s_0_0_*.html) for all 12 languages with firmware changes
- Enhanced scraper to detect and extract Energy Management status box from start page
- Improved sensor entity descriptions with appropriate device classes and icons

### Technical
- Added 9 configuration sensor constants across heating and energy management pages
- Extended heating configuration infrastructure to support SG Ready parameters
- Created test_sg_ready_config.py and test_start_page_energy_mgmt.py
- Total sensors: 64 (55 from 0.2.0 + 9 new configuration/status sensors)

## [0.2.0] - 2025-11-24

### Added
- **55 sensors** across 10 languages with structure-based translation extraction
- Energy page sensors (s=1,8): heat amount, power consumption, efficiency metrics
- All process values sensors (s=1,1): temperatures, pressures, flow rates, power metrics
- Dual-mode temperature sensors for bivalent systems
- Runtime and defrost statistics sensors
- Heating circuit 2 (HK2) temperature sensors
- External heat source temperature sensors
- Configurable update interval (1-1440 minutes) via integration options UI
- Comprehensive documentation in `ADDING_NEW_SENSORS.md` with complete workflow
- Sample scripts for adding new ISG pages (`scripts/samples/`)
- Utility scripts for translation extraction and verification
- GitHub Actions workflow for automated testing
- This CHANGELOG file

### Changed
- Reorganized repository structure: moved analysis scripts to `scripts/`, test shims to `tests/`
- Updated to structure-based translation mapping for better maintainability
- Improved language detection for 12 languages (cs, da, de, en, es, fi, fr, hu, it, nl, pl, sv)
- Version bumped to 0.2.0 reflecting significant feature additions

### Fixed
- Options flow configuration UI (Configure button) now works correctly
- `async_get_options_flow` moved to ConfigFlow class as static method
- Unicode encoding issues on Windows for translation extraction scripts
- HTML pattern compatibility for different ISG firmware versions

### Removed
- Temporary analysis files from repository root
- Non-functional `test_options_flow.py` that always skipped
- Duplicate and obsolete utility scripts

## [0.1.1] - Previous version

### Initial Release
- Basic sensor integration for Stiebel Eltron ISG
- SSDP auto-discovery
- Core sensors: temperatures, energy consumption, hot water
- Multi-language support
