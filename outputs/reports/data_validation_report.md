# Data Quality and Ingestion Validation Report

**Date of Validation:** 2026-09-30  
**Pipeline Stage:** Data Ingestion & Schema Verification  

---

## 1. Executive Summary

| Dataset | File Path | Total Rows | Columns | Duplicate Rows | Null Fields Count | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Crop Production** | `data/raw/crop_production.csv` | 246,091 | 7 | 0 | 3,730 | **PASSED** |
| **Rainfall in India** | `data/raw/rainfall_in_india.csv` | 4,116 | 19 | 0 | 134 | **PASSED** |

---

## 2. Crop Production Dataset Details

- **Temporal Coverage:** 1997 to 2015
- **Geographic Granularity:** 33 States / Union Territories, District-level data
- **Crop Types:** 124 crops recorded
- **Data Quality Observations:**
  - Zero rows with negative Area or negative Production.
  - Exactly 3,730 records have missing `Production` (1.52%).
  - Categorical text fields (`Season`, `Crop`, `State_Name`) contain trailing whitespace (e.g. `'Kharif     '`).
  - Coconut production values are enumerated in count of nuts rather than metric tonnes.

### Column Null Breakdown:
```json
{
  "State_Name": 0,
  "District_Name": 0,
  "Crop_Year": 0,
  "Season": 0,
  "Crop": 0,
  "Area": 0,
  "Production": 3730
}
```

---

## 3. Rainfall Dataset Details

- **Temporal Coverage:** 1901 to 2015 (115 years of meteorological records)
- **Subdivisions:** 36 Meteorological Subdivisions (India Meteorological Department)
- **Data Quality Observations:**
  - Zero rows with negative rainfall values.
  - Minor missing values across monthly figures (at most 11 missing entries in November).
  - Annual rainfall values match seasonal breakdowns.

### Column Null Breakdown:
```json
{
  "JAN": 4,
  "FEB": 3,
  "MAR": 6,
  "APR": 4,
  "MAY": 3,
  "JUN": 5,
  "JUL": 7,
  "AUG": 4,
  "SEP": 6,
  "OCT": 7,
  "NOV": 11,
  "DEC": 10,
  "ANNUAL": 26,
  "Jan-Feb": 6,
  "Mar-May": 9,
  "Jun-Sep": 10,
  "Oct-Dec": 13
}
```

---

## 4. Remediation and Data Cleaning Decisions

1. **Whitespace Trimming:** Strip leading and trailing whitespace across all string columns (`State_Name`, `District_Name`, `Season`, `Crop`, `SUBDIVISION`).
2. **Missing Production Values:** Retain raw records intact. In downstream aggregations, exclude NaN production records from yield computations without deleting records from the raw corpus.
3. **Unit Segregation:** Create distinct metrics for food grains/field crops (tonnes) vs. plantation nuts (coconut).
4. **Geographic Mapping:** Construct explicit dictionary mappings connecting IMD subdivisions to State-level administrative boundaries.
