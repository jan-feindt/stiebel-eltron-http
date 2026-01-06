# Test Coverage Improvements

## Why Was Compressor Starts Missed?

The compressor_starts sensor was missed because **the test suite had a gap between canonical key definition and i18n translation validation**.

### What Existed Before:
1. **test_all_canonical_keys_covered.py** - Validated that all canonical keys CAN be extracted from HTML test files
2. However, it didn't check if the i18n translations actually existed for those keys
3. The test passed because:
   - `CanonicalKey.COMPRESSOR_STARTS` was defined in [canonical_keys.py](custom_components/stiebel_eltron_http/i18n/canonical_keys.py)
   - The HTML test files contained the data  
   - But the i18n/*.py files were missing the translations!
   
### The Problem:
The extraction chain requires ALL of:
1. ✅ Canonical key defined → `CanonicalKey.COMPRESSOR_STARTS`
2. ❌ **I18n translations** → Missing in all 12 language files!
3. ✅ HTML test data → Present
4. ✅ Extractor logic → Working

**The i18n translations were the missing link**, but no test validated they existed.

## How to Ensure All Sensors Are Extracted

### New Test Suite: test_all_sensors_extracted.py

Created comprehensive tests that validate the COMPLETE extraction chain:

#### 1. **test_all_canonical_keys_have_translations()**
```python
# Validates: Every non-section, non-optional canonical key has i18n translations
# This would have caught the missing compressor_starts translations!
```

#### 2. **test_critical_sensors_extracted_all_languages(lang)** [12 tests]
```python
# Validates: Critical sensors extract correctly in ALL 12 languages
# Tests: en, de, da, fi, sv, nl, fr, it, pl, cs, es, hu
# Critical sensors tested:
- outside_temperature
- return_temperature  
- supply_temperature
- compressor_starts  ← Would have caught this!
- defrost_starts
- runtime_vd_heating
- runtime_vd_dhw
```

#### 3. **test_no_none_values_in_extracted_data()**
```python
# Validates: Extracted values are never None
# If a sensor can't be extracted, it should be omitted, not set to None
```

#### 4. **test_all_translations_have_canonical_keys()**
```python
# Validates: No orphaned translations exist
# Prevents typos in HEADER_ALIASES that don't map to canonical keys
```

### Test Results:
```
15 passed in 11.04s

test_all_canonical_keys_have_translations         PASSED
test_critical_sensors_extracted_all_languages[en] PASSED
test_critical_sensors_extracted_all_languages[de] PASSED
test_critical_sensors_extracted_all_languages[da] PASSED
test_critical_sensors_extracted_all_languages[fi] PASSED
test_critical_sensors_extracted_all_languages[sv] PASSED
test_critical_sensors_extracted_all_languages[nl] PASSED
test_critical_sensors_extracted_all_languages[fr] PASSED
test_critical_sensors_extracted_all_languages[it] PASSED
test_critical_sensors_extracted_all_languages[pl] PASSED
test_critical_sensors_extracted_all_languages[cs] PASSED
test_critical_sensors_extracted_all_languages[es] PASSED
test_critical_sensors_extracted_all_languages[hu] PASSED
test_no_none_values_in_extracted_data             PASSED
test_all_translations_have_canonical_keys         PASSED
```

## What This Catches

### Before (Old Tests):
- ✅ Canonical keys are defined
- ✅ HTML contains the data
- ❌ **I18n translations exist** ← GAP!
- ❌ **Extraction actually works** ← GAP!

### After (New Tests):
- ✅ Canonical keys are defined
- ✅ I18n translations exist for all required keys
- ✅ HTML contains the data
- ✅ Extraction produces correct values in ALL 12 languages
- ✅ No None values in results
- ✅ No orphaned translations

## How to Use

When adding a new sensor:

1. **Define the canonical key** in [canonical_keys.py](custom_components/stiebel_eltron_http/i18n/canonical_keys.py)
2. **Add i18n translations** in all 12 language files (custom_components/stiebel_eltron_http/i18n/*.py)
3. **Run the tests**: `pytest tests/test_all_sensors_extracted.py -v`
4. If tests fail, you'll get clear error messages:
   - Missing translations → `test_all_canonical_keys_have_translations` fails
   - Extraction broken → `test_critical_sensors_extracted_all_languages` fails

## Summary

**Before**: Tests validated structure but not the complete extraction chain  
**After**: Tests validate end-to-end extraction in all 12 languages  
**Result**: Future missing translations will be caught immediately!

The compressor_starts issue has been fixed and the new test suite ensures this type of problem won't happen again.
