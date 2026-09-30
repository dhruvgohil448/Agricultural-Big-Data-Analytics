# Comprehensive Data Dictionary & Transformation Specification

This document details every feature, data type, unit of measurement, null handling rule, and transformation applied throughout the Agricultural Big Data Analytics System.

---

## 1. Raw Datasets

### A. Raw Crop Production (`data/raw/crop_production.csv`)

| Field Name | Type | Unit | Null Policy | Description & Value Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `State_Name` | String | Categorical | Mandatory (0 nulls) | Name of Indian State / UT (33 unique values). Contains trailing whitespace in raw data. |
| `District_Name` | String | Categorical | Mandatory (0 nulls) | Revenue district within the state (646 unique values). |
| `Crop_Year` | Integer | Year (YYYY) | Mandatory (0 nulls) | Agricultural crop year, range: `[1997, 2015]`. |
| `Season` | String | Categorical | Mandatory (0 nulls) | Cropping season: `Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`, `Whole Year`. Contains whitespace padding. |
| `Crop` | String | Categorical | Mandatory (0 nulls) | Crop commodity name (124 crops). |
| `Area` | Float | Hectares (Ha) | Mandatory (0 nulls) | Cultivated land area. Range: `[0.04, 8580100.0]`. No negative values. |
| `Production` | Float | Metric Tonnes (or Nuts) | Optional (3,730 nulls) | Output volume. Tonnes for field crops; Nuts count for Coconut. Range: `[0.0, 1.25e9]`. |

---

### B. Raw Rainfall (`data/raw/rainfall_in_india.csv`)

| Field Name | Type | Unit | Null Policy | Description & Value Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `SUBDIVISION` | String | Categorical | Mandatory (0 nulls) | IMD Meteorological subdivision (36 unique subdivisions). |
| `YEAR` | Integer | Year (YYYY) | Mandatory (0 nulls) | Observation year, range: `[1901, 2015]`. |
| `JAN` to `DEC` | Float | Millimeters (mm) | Minor nulls (3 to 11) | Monthly precipitation totals. Range: `[0.0, 2362.8]`. |
| `ANNUAL` | Float | Millimeters (mm) | 26 nulls | Total annual rainfall. Range: `[51.1, 6331.1]`. |
| `Jan-Feb` | Float | Millimeters (mm) | 6 nulls | Winter seasonal precipitation. |
| `Mar-May` | Float | Millimeters (mm) | 9 nulls | Pre-monsoon seasonal precipitation. |
| `Jun-Sep` | Float | Millimeters (mm) | 10 nulls | South-West Monsoon precipitation (primary cropping season). |
| `Oct-Dec` | Float | Millimeters (mm) | 13 nulls | Post-monsoon / North-East Monsoon precipitation. |

---

## 2. Processed Datasets

### A. Cleaned Crop Production (`data/processed/cleaned_crop_production.csv`)

Derived from `crop_production.csv` with the following transformations:
1. Strings trimmed of leading/trailing whitespace.
2. State names normalized to title case; `Orissa` standardized to `Odisha`.
3. Created unit segregation flag: `Is_Nut_Unit = True` when `Crop == 'Coconut'`.
4. Computed derived feature: `Yield = Production / Area` when `Area > 0` and `Production` is non-null.

| Field Name | Type | Unit | Transformation Logic |
| :--- | :--- | :--- | :--- |
| `State_Name` | String | Categorical | Stripped & title-cased. |
| `District_Name` | String | Categorical | Stripped of whitespace. |
| `Crop_Year` | Integer | Year | Parsed as 4-digit integer. |
| `Season` | String | Categorical | Stripped of whitespace. |
| `Crop` | String | Categorical | Stripped of whitespace. |
| `Area` | Float | Hectares (Ha) | Strictly positive numeric value. |
| `Production` | Float | Tonnes / Nuts | Numeric value; `NaN` preserved for auditability. |
| `Is_Nut_Unit` | Boolean | True/False | `True` for Coconut, `False` for all field crops. |
| `Yield` | Float | Tonnes/Ha (or Nuts/Ha) | `Production / Area`. `NaN` if Production is missing. |

---

### B. Cleaned State-Level Rainfall (`data/processed/cleaned_state_rainfall.csv`)

Derived from `rainfall_in_india.csv` with the following transformations:
1. Imputed missing `ANNUAL` using `sum(JAN..DEC)`.
2. Mapped 36 IMD Subdivisions to 33 Political States via `SUBDIVISION_TO_STATE` crosswalk.
3. Grouped by `(State_Name, YEAR)` to produce state-level annual and monsoon means.

| Field Name | Type | Unit | Transformation Logic |
| :--- | :--- | :--- | :--- |
| `State_Name` | String | Categorical | Crosswalk-mapped from IMD subdivision. |
| `YEAR` | Integer | Year | Filtered to common temporal coverage. |
| `ANNUAL_RAIN_MM` | Float | Millimeters (mm) | Mean annual rainfall across state subdivisions (rounded to 2 decimals). |
| `MONSOON_RAIN_MM` | Float | Millimeters (mm) | Mean South-West monsoon rainfall (Jun–Sep) across state subdivisions. |
| `SUBDIVISION_COUNT`| Integer | Count | Number of subdivisions contributing to the state average. |

---

## 3. MapReduce Aggregated Tables

### A. Crop Production Aggregated (`outputs/tables/mr_crop_production_results.tsv`)
- **Key:** `State_Name`, `Crop`, `Crop_Year`
- **Output Fields:**
  1. `State_Name` (String): Normalized state name.
  2. `Crop` (String): Crop name.
  3. `Crop_Year` (Integer): Crop year.
  4. `Total_Area` (Float): Sum of cultivated district areas in hectares.
  5. `Total_Production` (Float): Sum of production across districts.
  6. `Mean_Yield` (Float): `Total_Production / Total_Area`.
  7. `Record_Count` (Integer): Number of district-season records aggregated.

### B. Decadal Meteorological Summary (`outputs/tables/mr_rainfall_results.tsv`)
- **Key:** `SUBDIVISION`, `Decade` (e.g. `1990s`)
- **Output Fields:**
  1. `SUBDIVISION` (String): Meteorological subdivision.
  2. `Decade` (String): 10-year grouping (e.g., `1950s`).
  3. `Avg_Annual_Rainfall_mm` (Float): Mean decadal annual precipitation.
  4. `Avg_Monsoon_Rainfall_mm` (Float): Mean decadal monsoon precipitation.
  5. `Year_Count` (Integer): Number of years observed in the decade.
