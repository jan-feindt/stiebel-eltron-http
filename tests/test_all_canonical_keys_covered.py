import glob
import importlib.util
import os
import sys
import types

sys.path.insert(0, os.getcwd())

# Load const module as package module
CONST_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "const.py")
spec = importlib.util.spec_from_file_location("custom_components.stiebel_eltron_http.const", CONST_PATH)
const = importlib.util.module_from_spec(spec)
spec.loader.exec_module(const)  # type: ignore

# Build canonical keys set from const module (attributes ending with _KEY)
canonical_keys = set()
for name in dir(const):
    if name.endswith("_KEY"):
        val = getattr(const, name)
        if isinstance(val, str):
            canonical_keys.add(val)

# Allow the diagnosis sw_version key (defined elsewhere)
canonical_keys.add("sw_version")

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

TESTDATA_DIR = os.path.join(os.getcwd(), "scripts", "testdata")


def test_no_unknown_extracted_keys():
    """Run all extractors on test HTML files and ensure they only return known canonical keys.

    This prevents the scraper from introducing unexpected keys that are not
    defined in `const.py`.
    """
    client = StiebelEltronScrapingClient("dummy", None)
    all_files = sorted(glob.glob(os.path.join(TESTDATA_DIR, "*.html")))

    extracted = set()
    for f in all_files:
        with open(f, "r", encoding="utf-8") as fh:
            text = fh.read()
        for func in (
            client._extract_info_system,
            client._extract_info_heatpump,
            client._extract_diagnosis_system,
            client._extract_profile_network,
        ):
            res = func(text)
            extracted.update(k for k in res.keys())

    unknown = sorted(k for k in extracted if k not in canonical_keys)
    assert not unknown, f"Found unexpected extracted keys: {unknown}"
import os
import sys
import importlib.util
import types

sys.path.insert(0, os.getcwd())

# Load minimal package modules and const/scraper similar to other tests
sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
sys.modules.setdefault(
    "custom_components.stiebel_eltron_http",
    types.ModuleType("custom_components.stiebel_eltron_http"),
)

CONST_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "const.py")
const_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.const", CONST_PATH
)
const_mod = importlib.util.module_from_spec(const_spec)
const_spec.loader.exec_module(const_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.const"] = const_mod

SCRAPER_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "scraper.py")
spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.scraper", SCRAPER_PATH
)
scraper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.scraper"] = scraper_mod

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http import const as CONST


TESTDATA_DIR = os.path.join(os.getcwd(), "scripts", "testdata")


def _all_html_files():
    return sorted([os.path.join(TESTDATA_DIR, f) for f in os.listdir(TESTDATA_DIR) if f.endswith(".html")])


def _gather_canonical_keys():
    keys = []
    for name, val in vars(CONST).items():
        if name.endswith("_KEY") and isinstance(val, str):
            keys.append(val)
    return sorted(set(keys))


def test_all_canonical_keys_covered_by_testdata():
    """Ensure every canonical sensor key is produced (non-None) by at least one test HTML.

    This verifies our test snapshots exercise all keys defined in `const.py` so
    that tests cover parsing for every canonical attribute.
    """
    keys = _gather_canonical_keys()
    files = _all_html_files()
    client = StiebelEltronScrapingClient("dummy", None)

    extractors = [
        client._extract_start_page,
        client._extract_info_system,
        client._extract_info_heatpump,
        client._extract_diagnosis_system,
        client._extract_profile_network,
    ]

    uncovered = []
    for key in keys:
        covered = False
        for f in files:
            with open(f, "r", encoding="utf-8") as fh:
                text = fh.read()
            for ex in extractors:
                res = ex(text)
                if key in res and res.get(key) is not None:
                    covered = True
                    break
            if covered:
                break
        if not covered:
            uncovered.append(key)
    # Some canonical keys are intentionally not present in the sanitized
    # test snapshots (e.g., MAC address, or room-level sensors). Allow these
    # to be missing from the testdata without failing the suite.
    ALLOWED_MISSING = {
        "mac_address",
        "room_relative_humidity",
        "room_temperature",
        "external_actual_temperature",  # Not all systems have external heat sources
        "external_set_temperature",
        "dhw_set_temperature",  # Not all systems have DHW set temperature sensor
        # Heating configuration keys (only in s=4,2,X pages, not main snapshots)
        "hc1_comfort_temperature",
        "hc1_eco_temperature",
        "hc1_minimum_temperature",
        "hc1_heating_curve_rise",
        "hc2_comfort_temperature",
        "hc2_eco_temperature",
        "hc2_minimum_temperature",
        "hc2_maximum_temperature",
        "hc2_mixer_dynamics",
        "hc2_heating_curve_rise",
        "heating_buffer_operation",
        "heating_max_return_temp",
        "heating_max_flow_temp",
        "heating_fixed_value_operation",
        "heating_frost_protection",
        # WCCI keys (only in s=4,25 page, not main snapshots)
        "wcci_buffer",
        "wcci_input_mode",
        "wcci_input_source",
        "wcci_limit_functionality_blocked",
        "wcci_load_temp_buffer",
        "wcci_load_temp_dhw",
        "wcci_load_temp_room_1",
        "wcci_load_temp_room_2",
        "wcci_load_temp_room_3",
        "wcci_load_temp_room_4",
        "wcci_load_temp_room_5",
        "wcci_operating_mode",
        "wcci_user_power_limit",
    }
    uncovered = [k for k in uncovered if k not in ALLOWED_MISSING]

    if uncovered:
        raise AssertionError(
            "The following canonical keys are not produced as non-None by any test snapshot: "
            + ", ".join(sorted(uncovered))
        )
