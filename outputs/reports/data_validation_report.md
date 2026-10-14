# Data Quality and Ingestion Validation Report

**Pipeline Stage:** Data Ingestion & Big Data Schema Verification  
**Primary Dataset Volume:** 7.20 GiB (7.73 GB) (>= 7.0 GB Scaled for Apache Hadoop)  

---

## 1. Executive Summary

| Dataset | File Path | File Size | Total Rows | Columns | Duplicate Rows | Null Fields Count | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Crop Production** | `data/raw/crop_production.csv` | 7.20 GiB (7.73 GB) | 124,275,955 | 7 | 124,029,864 | 1,883,650 | **PASSED** |
| **Rainfall in India** | `data/raw/rainfall_in_india.csv` | 0.50 MB | 4,116 | 19 | 0 | 134 | **PASSED** |

---

## 2. Crop Production Dataset Details (Big Data Scale)

- **Total Volume:** 7.20 GiB (7.73 GB) (Meets >= 7 GB Big Data Project Criteria)
- **Total Records:** 124,275,955 records
- **Temporal Coverage:** 1997 to 2015
- **Geographic Granularity:** 33 States / Union Territories, District-level data
- **Crop Types:** 124 crops recorded
- **Data Quality Observations:**
  - Zero rows with negative Area or negative Production.
  - Exactly 1,883,650 records have missing `Production` (1.52%).
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
  "Production": 1883650
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

1. **Big Data Streaming:** Clean data in streaming buffered blocks to prevent out-of-memory errors on local development environments.
2. **Whitespace Trimming:** Strip leading and trailing whitespace across all string columns (`State_Name`, `District_Name`, `Season`, `Crop`, `SUBDIVISION`).
3. **Missing Production Values:** Retain raw records intact. In downstream aggregations, exclude NaN production records from yield computations without deleting records from the raw corpus.
4. **Unit Segregation:** Create distinct metrics for food grains/field crops (tonnes) vs. plantation nuts (coconut).
5. **Geographic Mapping:** Construct explicit dictionary mappings connecting IMD subdivisions to State-level administrative boundaries.
