# Analysis of s=4,14 (ENERGIEMANAGEMENT) Configuration Page

## Page Overview
- **Page Title**: ENERGIEMANAGEMENT (Energy Management)
- **Total Configurable Fields**: 6
- **HTML File**: `scripts/testdata/_s_4_14_en.html`

## Extracted Fields

### 1. SG READY ENABLED
- **Val ID**: 60305
- **Div ID**: calval60305
- **Input Type**: Radio buttons
- **Options**:
  - `0` = OFF
  - `1` = ON ✓ (currently selected)

---

### 2. SG-READY INPUT
- **Val ID**: 60028
- **Div ID**: calval60028
- **Input Type**: Radio buttons
- **Options**:
  - `0` = OFF
  - `1` = MODBUS ✓ (currently selected)
  - `3` = CAN BUS
  - `4` = ISG PLUS

---

### 3. Heating buffer
- **Val ID**: 60317
- **Div ID**: calval60317
- **Input Type**: Radio buttons
- **Options**:
  - `0` = No buffer
  - `1` = Buffer with mixer ✓ (currently selected)
  - `2` = Buffer without mixer

---

### 4. UPPER ROOM/BUFFER TEMP. HC1
- **Val ID**: 60310
- **Div ID**: calval60310
- **Input Type**: Numeric (float)
- **Min Value**: 20°C
- **Max Value**: 50°C
- **Current Value**: 24,0°C
- **Unit**: °C
- **Step**: 0.1°C (from up/down buttons)
- **Description**: Applicable values: Input between 20 °C and 50 °C

---

### 5. UPPER ROOM TEMP. HC2
- **Val ID**: 60311
- **Div ID**: calval60311
- **Input Type**: Numeric (float)
- **Min Value**: 20°C
- **Max Value**: 30°C
- **Current Value**: 23,0°C
- **Unit**: °C
- **Step**: 0.1°C (from up/down buttons)
- **Description**: Applicable values: Input between 20 °C and 30 °C

---

### 6. UPPER SET DHW TEMP.
- **Val ID**: 60312
- **Div ID**: calval60312
- **Input Type**: Numeric (float)
- **Min Value**: 40°C
- **Max Value**: 80°C
- **Current Value**: 52,0°C
- **Unit**: °C
- **Step**: 0.5°C (from up/down buttons)
- **Description**: Applicable values: Input between 40 °C and 80 °C

---

## HTML Structure Patterns

### Radio Button Fields
Structure pattern:
```html
<div class="calibration round span-24 last" id="calval{ID}">
  <div class="span-7 ialigned">
    <h3 class="title">{FIELD_NAME}</h3>
  </div>
  <div class="values span-7">
    <div class="dropdown">
      <input class="dropdown" id="aval{ID}" readonly value="{CURRENT_LABEL}"/>
      <div class="black">
        <input id="radioval{ID}{OPTION}" name="val{ID}" type="radio" value="{VALUE}" alt="{LABEL}"/>
        <label for="radioval{ID}{OPTION}">{LABEL}</label>
        <!-- More options... -->
      </div>
    </div>
  </div>
  <div class="green round-right span-8 last">
    <p>{DESCRIPTION}</p>
  </div>
</div>
```

### Numeric Input Fields
Structure pattern:
```html
<div class="calibration round span-24 last" id="calval{ID}">
  <div class="span-7 ialigned">
    <h3 class="title">{FIELD_NAME}</h3>
  </div>
  <div class="values span-7">
    <div class="editors">
      <a href="javascript://" onmousedown="change('val{ID}','+',{MIN},{MAX},'{STEP}',true)">
        <img src="./pics/button_higher.png"/>
      </a>
      <a href="javascript://" onmousedown="change('val{ID}','-',{MIN},{MAX},'{STEP}',true)">
        <img src="./pics/button_lower.png"/>
      </a>
    </div>
    <input class="edit upndown" id="val{ID}" name="val{ID}" type="text" value=""/>
    <script>
      valSettings['val{ID}'] = new Array();
      valSettings['val{ID}']['type'] = '{DATA_TYPE}';
      valSettings['val{ID}']['min'] = '{MIN}';
      valSettings['val{ID}']['max'] = '{MAX}';
      jsvalues['{ID}'] = new Array();
      jsvalues['{ID}']['id']='val{ID}';
      jsvalues['{ID}']['val']='{CURRENT_VALUE}';
    </script>
  </div>
  <div class="values span-1 append-1">{UNIT}</div>
  <div class="green round-right span-8 last">
    <p>{DESCRIPTION}</p>
  </div>
</div>
```

## Key Identifiers

1. **Calibration Divs**: All configurable fields are wrapped in `<div class="calibration" id="calval{ID}">`
2. **Field Names**: Located in `<h3 class="title">` within each calibration div
3. **Val IDs**: Extracted from div IDs by removing the "calval" prefix
4. **Radio Options**: Radio button `alt` attribute contains the display label
5. **Numeric Ranges**: Min/max values stored in JavaScript `valSettings` array
6. **Current Values**: Stored in JavaScript `jsvalues` array
7. **Units**: Found in `<div class="values span-1 append-1">` for numeric fields
8. **Descriptions**: Located in `<div class="green round-right">`

## Data Export

The extracted data has been saved to:
- **JSON Format**: `scripts/s_4_14_fields.json`
- **Analysis Script**: `scripts/analyze_s_4_14.py`

The JSON file contains a structured array with all field specifications suitable for:
- Automated form generation
- API integration
- Configuration validation
- Documentation generation
