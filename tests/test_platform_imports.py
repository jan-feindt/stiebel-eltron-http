"""Test module imports and initialization.

This test ensures that platform modules with entity descriptions can be
imported without errors, preventing missing import issues from reaching production.
"""

import pytest
from importlib import util
from pathlib import Path


# Platform files with module-level entity descriptions that need validation
ENTITY_DESCRIPTION_FILES = [
    "sensor.py",
    "binary_sensor.py",
]


@pytest.mark.parametrize("module_file", ENTITY_DESCRIPTION_FILES)
def test_platform_module_can_be_parsed(module_file):
    """Verify platform module can be parsed and all imports are satisfied at module level.
    
    This catches issues like missing UnitOfPower imports that cause NameErrors
    when the module's top-level code executes during entity description creation.
    
    Only tests platform files with ENTITY_DESCRIPTIONS to avoid complications
    with files that have complex relative imports or external dependencies.
    """
    module_path = f"custom_components/stiebel_eltron_http/{module_file}"
    module_name = module_file.replace(".py", "")
    
    # Load module directly without executing Home Assistant imports
    spec = util.spec_from_file_location(module_name, module_path)
    module = util.module_from_spec(spec)
    
    # This will fail if there are missing imports (like UnitOfPower)
    # at module level - specifically in ENTITY_DESCRIPTIONS definitions
    try:
        spec.loader.exec_module(module)
        # If we get here without errors, all module-level code executed successfully
        assert True
    except NameError as e:
        pytest.fail(f"NameError in {module_file} module-level code: {e}")
    except ImportError as e:
        # This is expected - homeassistant module is mocked in test environment
        if "homeassistant" not in str(e):
            pytest.fail(f"Unexpected ImportError in {module_file}: {e}")
        # If it's just homeassistant imports, that's expected and OK
        assert True


def test_all_required_units_imported_in_sensor():
    """Verify all unit constants used in sensor.py are imported.
    
    This is a static check that parses the file and ensures imports match usage.
    Specifically checks for UnitOf* constants from homeassistant.const.
    """
    import re
    
    with open("custom_components/stiebel_eltron_http/sensor.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract what's imported from homeassistant.const
    import_match = re.search(
        r"from homeassistant\.const import (.+)",
        content,
        re.MULTILINE
    )
    assert import_match, "Could not find homeassistant.const imports"
    
    imported = {item.strip() for item in import_match.group(1).split(",")}
    
    # Find all UnitOf* references in the file
    used_units = set(re.findall(r"\b(UnitOf\w+)\b", content))
    
    # Check that all used units are imported
    missing_imports = used_units - imported
    assert not missing_imports, f"Units used but not imported: {missing_imports}"


def test_entity_description_files_exist():
    """Verify all platform files we're testing actually exist."""
    for module_file in ENTITY_DESCRIPTION_FILES:
        module_path = Path(f"custom_components/stiebel_eltron_http/{module_file}")
        assert module_path.exists(), f"Platform file {module_file} does not exist"

