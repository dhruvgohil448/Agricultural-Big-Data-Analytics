# Data Sources and Provenance Manifest

## 1. Primary Dataset: Crop Production Statistics in India

- **Dataset Identifier:** `crop_production.csv`
- **Originating Authority:** Ministry of Agriculture & Farmers Welfare, Directorate of Economics and Statistics (DES), Government of India.
- **Data Portal:** Open Government Data (OGD) Platform India ([data.gov.in](https://www.data.gov.in/))
- **Direct Mirror / Source URL:** `https://raw.githubusercontent.com/robintux/Datasets4StackOverFlowQuestions/master/crop_production.csv`
- **Fallback URL:** `https://raw.githubusercontent.com/ankitaS11/Crop-Yield-Prediction-in-India/master/crop_production.csv`
- **Terms of Use & License:** Government Open Data License - India (GODL) under the National Data Sharing and Accessibility Policy (NDSAP). Free public reuse with attribution.
- **License Information:** [https://data.gov.in/open-government-data-license-india](https://data.gov.in/open-government-data-license-india)
- **Local File Path:** `data/raw/crop_production.csv`
- **File Size:** 15,316,741 bytes (14.61 MB)
- **SHA-256 Checksum:** `5b2637058ca4aff2ef7c0e0f2f391bca712300d082693b585f489871fd91d520`
- **Temporal Coverage:** 1997 – 2015 (19 cropping years)
- **Geographic Coverage:** 33 Indian States and Union Territories, granular at District level.
- **Dimensions:** 246,091 rows x 7 columns
- **Original Schema:**
  - `State_Name` (String): Name of the administrative State or Union Territory.
  - `District_Name` (String): Name of the revenue district.
  - `Crop_Year` (Integer): Agricultural year of harvest (July to June).
  - `Season` (String): Cropping season (`Kharif`, `Rabi`, `Summer`, `Autumn`, `Winter`, `Whole Year`).
  - `Crop` (String): Standardized agricultural commodity (124 crop types).
  - `Area` (Float): Cultivated area in **Hectares (Ha)**.
  - `Production` (Float): Yield volume in **Metric Tonnes (MT)** for field crops, and **Number of Nuts** for Coconut.
- **Known Limitations & Caveats:**
  - Exactly 3,730 records have missing `Production` values (unrecorded harvests or early crop failures).
  - Categorical strings contain trailing space padding.
  - Coconut production values are enumerated in count of nuts (up to 1.25 billion per record) rather than metric tonnes, requiring isolated handling in yield aggregations.

---

## 2. Secondary Dataset: Meteorological Rainfall in India (1901–2015)

- **Dataset Identifier:** `rainfall_in_india.csv`
- **Originating Authority:** India Meteorological Department (IMD), Ministry of Earth Sciences, Government of India.
- **Data Portal:** National Data Sharing and Accessibility Policy (NDSAP) / IMD Pune National Climate Centre ([mausam.imd.gov.in](https://mausam.imd.gov.in/))
- **Direct Mirror / Source URL:** `https://raw.githubusercontent.com/chandanverma07/DataSets/master/rainfall%20in%20india%201901-2015.csv`
- **Fallback URL:** `https://raw.githubusercontent.com/MainakRepositor/Datasets/master/rainfall%20in%20india%201901-2015.csv`
- **Terms of Use & License:** Government Open Data License - India (GODL) / NDSAP Open Public Data.
- **Local File Path:** `data/raw/rainfall_in_india.csv`
- **File Size:** 528,115 bytes (0.50 MB)
- **SHA-256 Checksum:** `635c98a69f07e6ab028414d2411a1e3b4c9ac4b7a5ee4748701a32297d939de7`
- **Temporal Coverage:** 1901 – 2015 (115 continuous meteorological years)
- **Geographic Coverage:** 36 Meteorological Subdivisions across India.
- **Dimensions:** 4,116 rows x 19 columns
- **Original Schema:**
  - `SUBDIVISION` (String): Name of the IMD meteorological subdivision.
  - `YEAR` (Integer): Observation calendar year.
  - `JAN` through `DEC` (Float): Monthly aggregate rainfall in **Millimeters (mm)**.
  - `ANNUAL` (Float): Total annual rainfall in **Millimeters (mm)**.
  - `Jan-Feb`, `Mar-May`, `Jun-Sep`, `Oct-Dec` (Float): Seasonal totals in **Millimeters (mm)**, with `Jun-Sep` representing the critical Indian South-West Monsoon.
- **Known Limitations & Caveats:**
  - 26 records had missing values in the `ANNUAL` summary column, which was mathematically imputed as the sum of the 12 complete monthly figures during cleaning.
  - Subdivisions do not perfectly correspond 1-to-1 with political state boundaries (e.g. Rajasthan is split into East and West; Assam and Meghalaya are combined). Explicit cross-walk mapping was implemented.
