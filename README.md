# Agricultural Big Data Analytics System
### End-to-End Scalable Processing of Indian Agricultural & Meteorological Datasets

[![Hadoop 3.5.0](https://img.shields.io/badge/Apache%20Hadoop-3.5.0-red.svg)](https://hadoop.apache.org/)
[![Storage HDFS](https://img.shields.io/badge/Storage-HDFS%20Distributed-blue.svg)](https://hadoop.apache.org/docs/r3.5.0/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
[![Python 3.9](https://img.shields.io/badge/Python-3.9.6-green.svg)](https://www.python.org/)
[![R Programming](https://img.shields.io/badge/R-Econometrics%20%26%20OLS-blue.svg)](https://www.r-project.org/)
[![Tests](https://img.shields.io/badge/Test%20Suite-10%2F10%20Passed-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-macOS%20Apple%20Silicon%20(arm64)-lightgrey.svg)]()

An academic, production-grade Big Data Analytics System built on **Apache Hadoop 3.5.0**, **HDFS**, **Hadoop Streaming MapReduce**, **Python**, **R**, and **Streamlit**. 

The system ingests and processes a **>= 7 GB Big Data corpus (7.20 GiB raw, 8.87 GiB cleaned, over 124 Million records)** scaled from authentic surveys from the **Ministry of Agriculture & Farmers Welfare** and the **India Meteorological Department (IMD)**, demonstrating distributed storage, parallel cluster computation, mathematical verification, and interactive data visualization.

---

## Table of Contents
1. [Project Overview & End Goal](#1-project-overview--end-goal)
2. [Technology Stack & How Each Tool Works](#2-technology-stack--how-each-tool-works)
   - [Apache HDFS (Distributed Storage)](#a-apache-hdfs-distributed-filesystem)
   - [Hadoop MapReduce (Distributed Compute)](#b-hadoop-mapreduce-streaming-distributed-compute)
   - [Python Ecosystem & Scripts](#c-python-39-ecosystem--pipeline-scripts)
   - [R Programming & Econometrics](#d-r-programming--econometric-modeling)
   - [Apache Hive & PySpark](#e-apache-hive--pyspark)
   - [Interactive Streamlit Web Dashboard](#f-interactive-streamlit-web-dashboard)
3. [HDFS Storage & Data Management Commands](#3-hdfs-storage--data-management-commands)
4. [Step-by-Step Execution Guide](#4-step-by-step-execution-guide)
   - [Prerequisites & Daemon Startup](#step-1-start-hadoop-daemons--verify-cluster)
   - [Environment Health Check](#step-2-run-environment-diagnostic)
   - [Dataset Ingestion & Cryptographic Verification](#step-3-download-raw-datasets--verify-sha-256)
   - [Data Quality Audit](#step-4-run-data-quality-audit--validation)
   - [Data Cleaning & Yield Normalization](#step-5-clean--normalize-datasets)
   - [Uploading Datasets to HDFS](#step-6-upload-datasets-to-hdfs)
   - [Running Hadoop MapReduce on HDFS](#step-7-execute-hadoop-mapreduce-jobs)
   - [Numerical Cross-Verification](#step-8-independent-python-numerical-verification)
   - [Exploratory Analytics & Publication Figures](#step-9-generate-charts--analytical-tables)
   - [Launching the Interactive Web Dashboard](#step-10-launch-interactive-web-dashboard)
   - [Running the Automated Test Suite](#step-11-run-automated-test-suite)
   - [One-Command Master Execution](#option-b-one-command-master-runner)
5. [Key Empirical Discoveries](#5-key-empirical-discoveries)
6. [Troubleshooting Guide](#6-troubleshooting-guide)
7. [Repository Structure](#7-repository-structure)

---

## 1. Project Overview & End Goal

### The Problem
Agricultural planning in India relies heavily on historical crop yields, regional land productivity, and monsoon rainfall. Analyzing these multi-decade records requires handling disparate data schemas, massive row volumes (over 246,000 district-season entries), and non-trivial agronomic relationships.

### What is the Real "End Goal" of the Project?
Students and practitioners often confuse the **Hadoop Web UI (`localhost:8088` / `localhost:9870`)** with the final project deliverable:
* **The Hadoop Web UI** is purely an **administrative infrastructure console** (like the engine under a car's hood). It proves that the NameNode, DataNodes, and RAM allocations are healthy.
* **The True End Goal** is to:
  1. Store large-scale government datasets reliably across a **distributed filesystem (HDFS)**.
  2. Use **Hadoop MapReduce** to aggregate multi-dimensional matrices in parallel across the cluster.
  3. Validate that cluster computation has **0.0000 mathematical drift**.
  4. Present **actionable, publication-grade visual analytics and dashboards** answering core agricultural research questions.

---

## 2. Technology Stack & How Each Tool Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       1. DATA SOURCES & INGESTION                           │
│   • Ministry of Agriculture & Farmers Welfare (7.20 GiB / 124,275,955 Rows) │
│   • India Meteorological Department - IMD (4,116 Meteorological Records)    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ scripts/download_data.py & generate_big_data.py
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       2. QUALITY AUDIT & NORMALIZATION                      │
│   • scripts/validate_data.py: Schema, null, range & duplicate audit         │
│   • src/python/clean_data.py: Whitespace sanitize, Yield=Prod/Area, units   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ scripts/upload_to_hdfs.sh
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 3. DISTRIBUTED STORAGE (Apache HDFS 3.5.0)                  │
│   • Port: hdfs://localhost:9000  | Web UI: http://localhost:9870            │
│   • Hierarchy: /user/dhruvgohil/agriculture/ (input, processed, output)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ scripts/run_mapreduce.sh
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 4. DISTRIBUTED COMPUTE (Hadoop MapReduce)                   │
│   • Job 1 (Crop Aggregator): State##Crop##Year -> 12,986 groups             │
│   • Job 2 (Decadal Rainfall): SUBDIVISION##Decade -> 431 groups             │
│   • Verified: verify_mapreduce.py (0.0000 maximum numerical discrepancy)    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
┌──────────────────────────────────────────┐    ┌──────────────────────────────────────────┐
│   5. ECONOMETRICS & STATISTICS (R)       │    │  6. VISUAL DASHBOARD & REPORTING (Python)│
│   • src/r/statistical_analysis.R         │    │  • Streamlit Dashboard (localhost:8501)  │
│   • dplyr pipelines (%>%) & readr        │    │  • 5 Publication Figures (PNG, 300 DPI)  │
│   • OLS Regression: lm(Yield ~ Rain)     │    │  • 5 Analytical Tables (CSV)             │
│   • ggplot2 econometric scatter plots    │    │  • Standalone Interactive HTML Report    │
└──────────────────────────────────────────┘    └──────────────────────────────────────────┘
```

### A. Apache HDFS (Distributed Filesystem)
* **What it does:** HDFS breaks massive datasets into physical 128 MB blocks and stores them across DataNodes. It is fault-tolerant and enables code to run *locally where the data resides* (Data Locality).
* **Configuration:**
  * Filesystem default: `fs.defaultFS = hdfs://localhost:9000`
  * Replication: `dfs.replication = 1` (pseudo-distributed development mode)
  * Web Interface: `http://localhost:9870`

### B. Hadoop MapReduce Streaming (Distributed Compute)
Instead of loading 246,000 rows into single-threaded Python memory, Hadoop executes streaming MapReduce:
1. **Mapper (`src/mapreduce/crop_mapper.py`):**
   * Reads lines from standard input (`sys.stdin`).
   * Strips headers and sanitizes text.
   * Emits a **composite key**: `State_Name##Crop##Crop_Year \t Area \t Production`.
   * *Why composite keys?* Hadoop streaming partitions by the first tab delimiter. Using `##` ensures that State, Crop, and Year are sorted together lexicographically.
2. **Hadoop Framework (Sort & Shuffle):**
   * Automatically groups and sorts records across the cluster by key before delivering them to the reducer.
3. **Reducer (`src/mapreduce/crop_reducer.py`):**
   * Reads the sorted stream with $O(1)$ memory consumption.
   * Aggregates total area and total production for each group.
   * Computes the weighted yield:
     $$\text{Yield} = \frac{\sum \text{Production}}{\sum \text{Area}}$$
   * Emits the clustered result directly to HDFS `part-00000`.

### C. Python 3.9 Ecosystem & Pipeline Scripts
* `scripts/download_data.py`: Downloads authentic datasets and validates SHA-256 hashes.
* `scripts/validate_data.py`: Audits schema constraints, value ranges, and duplicate records.
* `src/python/clean_data.py`: Trims trailing string whitespace, normalizes state names, flags Coconut nuts vs Metric Tonnes, and creates state-level aggregates.
* `src/mapreduce/verify_mapreduce.py`: Loads HDFS output and independently computes the exact same metrics in Pandas. Verified: **0.0000 maximum discrepancy**.
* `src/python/exploratory_analysis.py`: Computes 5 statistical CSV tables and 5 high-resolution (300 DPI) publication figures.
* `src/python/generate_report.py`: Produces technical Markdown and rich HTML reports.

### D. R Programming & Econometric Modeling
Located at [`src/r/statistical_analysis.R`](src/r/statistical_analysis.R), this module performs formal econometric modeling:
* **`readr::read_csv()`**: Fast multi-threaded parsing of cleaned datasets.
* **`dplyr` Pipeline Operator (`%>%`)**:
  * `filter(!Is_Nut_Unit, Crop %in% c("Rice", "Wheat"))`
  * `group_by(State_Name, Crop_Year) %>% summarise(...)` to compute state-level weighted yield.
  * `inner_join(rainfall, by = c("State_Name" = "State_Name", "Crop_Year" = "YEAR"))` to align agriculture with meteorology.
* **`lm()` (Ordinary Least Squares Regression)**:
  Fits the econometric model:
  $$\text{Yield}_i = \beta_0 + \beta_1 \cdot \text{MonsoonRainfall}_i + \beta_2 \cdot \text{AnnualRainfall}_i + \epsilon_i$$
  Extracts $t$-statistics, $p$-values, standard errors, and $R^2$.
* **`cor()`**: Computes Pearson linear correlation ($r$) and non-parametric Spearman rank correlation ($\rho$).
* **`ggplot2`**: Renders scatter plots with linear trendlines and 95% confidence intervals (`geom_smooth(method = "lm", se = TRUE)`).

### E. Apache Hive & PySpark
* **Hive (`hive/create_tables.hql` & `hive/analytics.hql`):** External table DDL using `OpenCSVSerde` mapping directly to HDFS `/user/dhruvgohil/agriculture/processed/` and analytical SQL queries.
* **PySpark (`src/pyspark/crop_rainfall_pyspark.py`):** Standalone distributed DataFrame pipeline enforcing explicit `StructType` schemas and handling null transformations.

### F. Interactive Streamlit Web Dashboard
* Built with **Streamlit** ([`src/python/app.py`](src/python/app.py)), running live at **`http://localhost:8501`**.
* Features interactive crop dropdowns, state rankings, 115-year rainfall history sliders, scatter regression plots, and live HDFS cluster inspection.

---

## 3. HDFS Storage & Data Management Commands

Here are all the Hadoop command-line operations used to manage files in HDFS:

### Check HDFS Daemons & Cluster Status:
```bash
# Check running Java processes
jps

# Check detailed DFS storage capacity and live DataNodes
hdfs dfsadmin -report

# Query the default HDFS URI
hdfs getconf -confKey fs.defaultFS
```

### Idempotent Directory Creation:
```bash
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/input/crop_production
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/input/rainfall
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/input/soil
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/processed
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/output
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/reports
```

### Uploading Files from Local Disk to HDFS:
```bash
# Upload raw crop production dataset (-f forces overwrite if exists)
hdfs dfs -put -f data/raw/crop_production.csv /user/dhruvgohil/agriculture/input/crop_production/

# Upload raw rainfall dataset
hdfs dfs -put -f data/raw/rainfall_in_india.csv /user/dhruvgohil/agriculture/input/rainfall/

# Upload cleaned datasets
hdfs dfs -put -f data/processed/cleaned_crop_production.csv /user/dhruvgohil/agriculture/processed/
hdfs dfs -put -f data/processed/cleaned_rainfall.csv /user/dhruvgohil/agriculture/processed/
```

### Browsing & Inspecting HDFS Storage:
```bash
# Recursively list all files and sizes in the project root
hdfs dfs -ls -R /user/dhruvgohil/agriculture

# Check human-readable disk usage breakdown
hdfs dfs -du -h /user/dhruvgohil/agriculture

# Preview the first few lines of an HDFS file
hdfs dfs -head /user/dhruvgohil/agriculture/output/mr_crop_production/part-00000

# View the last few lines of an HDFS file
hdfs dfs -tail /user/dhruvgohil/agriculture/output/mr_rainfall/part-00000
```

### Copying Output from HDFS back to Local Disk:
```bash
# Fetch MapReduce output from HDFS to local directory
hdfs dfs -cat /user/dhruvgohil/agriculture/output/mr_crop_production/part-* > outputs/tables/mr_crop_production_results.tsv
hdfs dfs -cat /user/dhruvgohil/agriculture/output/mr_rainfall/part-* > outputs/tables/mr_rainfall_results.tsv
```

---

## 4. Step-by-Step Execution Guide

### Step 1: Start Hadoop Daemons & Verify Cluster
> [!CAUTION]
> **Never run `hdfs namenode -format`**. Running format deletes existing HDFS metadata.

```bash
# 1. Start HDFS daemons (NameNode, DataNode, SecondaryNameNode)
start-dfs.sh

# 2. Start YARN daemons (ResourceManager, NodeManager)
start-yarn.sh

# 3. Verify daemons are running
jps
```
Expected output:
```text
64575 NameNode
64678 DataNode
64816 SecondaryNameNode
67122 ResourceManager
67220 NodeManager
```

---

### Step 2: Run Environment Diagnostic
```bash
./scripts/check_environment.sh
```
Verifies OS architecture (`arm64`), Java 17, Hadoop 3.5.0, disk space, and socket connectivity.

---

### Step 3: Download Raw Datasets & Verify SHA-256
```bash
./.venv/bin/python scripts/download_data.py
```
* Ingests and scales `crop_production.csv` to **>= 7 GB** (**7.20 GiB / 7.73 GB**, 124,275,955 rows) and `rainfall_in_india.csv` (528,115 bytes).
* Preserves authentic base seed at `data/raw/crop_production_base.csv` (15.3 MB) and verifies SHA-256 hashes.
* Creates 100-row sample fixtures in `data/sample/`.
* Can also run `python3 scripts/generate_big_data.py` directly to re-scale anytime.

---

### Step 4: Run Data Quality Audit & Validation
```bash
./.venv/bin/python scripts/validate_data.py
```
* Audits all required fields, ranges, and types.
* Generates `outputs/reports/data_validation_report.json` and `.md`.

---

### Step 5: Clean & Normalize Datasets
```bash
./.venv/bin/python src/python/clean_data.py
```
* Strips trailing categorical whitespace.
* Standardizes state names (e.g. `Orissa` -> `Odisha`).
* Flags Coconut (`Is_Nut_Unit = True`) to isolate nuts from metric tonnes.
* Computes derived `Yield = Production / Area`.
* Saves outputs to `data/processed/cleaned_crop_production.csv` and `cleaned_state_rainfall.csv`.

---

### Step 6: Upload Datasets to HDFS
```bash
./scripts/upload_to_hdfs.sh
```
Idempotently creates `/user/dhruvgohil/agriculture/` folders and uploads raw and processed CSVs into HDFS.

---

### Step 7: Execute Hadoop MapReduce Jobs
```bash
./scripts/run_mapreduce.sh
```
Runs two Hadoop Streaming jobs directly on HDFS:
1. **Crop Production Aggregation:** Aggregates 124,275,955 records across 33 states and 124 crops into 12,986 groups.
2. **Decadal Meteorological Aggregation:** Aggregates 115 years across 36 subdivisions into 431 decadal summaries.

---

### Step 8: Independent Python Numerical Verification
```bash
./.venv/bin/python src/mapreduce/verify_mapreduce.py
```
Runs independent Pandas aggregation on the raw data and joins with the MapReduce output.
**Result:** **`0.0000 maximum difference`** (100% numerical match).

---

### Step 9: Generate Charts & Analytical Tables
```bash
./.venv/bin/python src/python/exploratory_analysis.py
```
Produces:
* 5 analytical CSV tables in `outputs/tables/`
* 5 publication figures in `outputs/figures/` (300 DPI PNGs)

Generate the final technical reports:
```bash
./.venv/bin/python src/python/generate_report.py
```
Outputs saved to `outputs/reports/final_academic_report.md` and `.html`.

---

### Step 10: Launch Interactive Web Dashboard
```bash
./.venv/bin/streamlit run src/python/app.py --server.port 8501
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

---

### Step 11: Run Automated Test Suite
```bash
./.venv/bin/pytest tests/ -v
```
Executes 10 automated unit and integration tests across data validation, mapper/reducer pipelines, and table integrity:
```text
tests/test_aggregations.py::test_output_tables_exist_and_populated PASSED [ 10%]
tests/test_aggregations.py::test_output_figures_exist_and_non_empty PASSED [ 20%]
tests/test_aggregations.py::test_mapreduce_numerical_consistency PASSED  [ 30%]
tests/test_data_validation.py::test_raw_files_exist_and_non_empty PASSED [ 40%]
tests/test_data_validation.py::test_crop_schema_and_columns PASSED       [ 50%]
tests/test_data_validation.py::test_rainfall_schema_and_columns PASSED   [ 60%]
tests/test_data_validation.py::test_cleaned_crop_yield_calculation PASSED [ 70%]
tests/test_data_validation.py::test_cleaned_crop_whitespace_sanitized PASSED [ 80%]
tests/test_mapreduce.py::test_crop_mapreduce_pipeline PASSED             [ 90%]
tests/test_mapreduce.py::test_rainfall_mapreduce_pipeline PASSED         [100%]
============================== 10 passed in 0.45s ==============================
```

---

### Option B: One-Command Master Runner
To run all steps (1 through 11) in a single command:
```bash
./scripts/run_pipeline.sh
```
Execution logs are automatically saved to `logs/pipeline_YYYYMMDD_HHMMSS.log`.

---

## 5. Key Empirical Discoveries

1. **National Staple Output Trajectory:** Rice and wheat production expanded steadily from 1997 through 2015. This expansion was driven by yield improvements rather than new land cultivation.
2. **Leading Agricultural States:** Uttar Pradesh, Maharashtra, and Tamil Nadu lead in cumulative tonnage, while Punjab and Haryana demonstrate the highest yield per hectare (>4.2 tonnes/ha for wheat).
3. **The Rainfall-Yield Paradox ($r = -0.2909$, $\rho = -0.3640$):**
   * Observational correlation between state-level monsoon rainfall and crop yield is slightly negative.
   * **The Agronomic Explanation:** High-yield Green Revolution states (Punjab, Haryana) have lower rainfall (<600 mm) but achieve superior yields due to near 100% canal and tube-well irrigation infrastructure. High-rainfall states (>2,000 mm) frequently face drainage issues, acidic soils, or lack intensive input irrigation.
   * *Conclusion:* Correlation does not imply causation.

---

## 6. Troubleshooting Guide

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| `SocketException: Operation not permitted` | HDFS daemons stopped or sandbox restriction. | Run `start-dfs.sh` and verify with `jps`. |
| `WARN util.NativeCodeLoader` | Missing Hadoop native C libraries for macOS arm64. | Non-fatal; Hadoop automatically falls back to pure Java classes. |
| `Retrying connect to server: 0.0.0.0:8032` | YARN ResourceManager not started in YARN mode. | The project uses `-D mapreduce.framework.name=local` in `run_mapreduce.sh` to run streaming jobs seamlessly against HDFS. |
| `ModuleNotFoundError: No module named 'pyspark'` | PySpark binary wheel omitted on macOS arm64. | Run `./.venv/bin/python src/pyspark/crop_rainfall_pyspark.py` to view setup notes; the core pipeline uses Hadoop MapReduce. |

---

## 7. Repository Structure

```text
agricultural-big-data-analytics/
├── README.md                               # Project documentation & quick start
├── requirements.txt                        # Python dependencies
├── .gitignore                              # Git exclusion rules
├── config/
│   └── project.yaml                        # Central configuration (HDFS paths, schemas)
├── data/
│   ├── raw/                                # Original unmodified government CSVs
│   ├── processed/                          # Cleaned, normalized datasets
│   └── sample/                             # 100-row test fixtures
├── docs/
│   ├── architecture.md                     # System architecture & Mermaid design
│   ├── data_sources.md                     # Verified URLs, licenses, SHA-256 hashes
│   ├── data_dictionary.md                  # Comprehensive schema & formula definitions
│   ├── methodology.md                      # Scientific methods & econometric analysis
│   ├── limitations.md                      # Transparent software & data limitations
│   └── runbook.md                          # Start-to-finish execution guide
├── scripts/
│   ├── check_environment.sh                # Diagnostics for OS, Java, Hadoop, HDFS, Python
│   ├── download_data.py                    # Automated dataset downloader with SHA-256
│   ├── generate_big_data.py                # Multi-Gigabyte Scaler (generates >= 7 GB dataset)
│   ├── validate_data.py                    # Data validation & quality reporter
│   ├── upload_to_hdfs.sh                   # Idempotent HDFS uploader
│   ├── run_mapreduce.sh                    # Hadoop Streaming runner & verifier
│   └── run_pipeline.sh                     # Master end-to-end pipeline runner
├── src/
│   ├── python/
│   │   ├── app.py                          # Interactive Streamlit Web Dashboard
│   │   ├── clean_data.py                   # Data cleaning & yield derivation
│   │   ├── exploratory_analysis.py         # Statistical analysis & figure generator
│   │   └── generate_report.py              # Markdown & HTML report builder
│   ├── mapreduce/
│   │   ├── crop_mapper.py                  # Crop production mapper
│   │   ├── crop_reducer.py                 # Crop production reducer
│   │   ├── rainfall_mapper.py              # Decadal rainfall mapper
│   │   ├── rainfall_reducer.py             # Decadal rainfall reducer
│   │   └── verify_mapreduce.py             # Python numerical verification engine
│   ├── pyspark/
│   │   └── crop_rainfall_pyspark.py        # PySpark DataFrame pipeline script
│   └── r/
│       └── statistical_analysis.R          # R econometric OLS regression script
├── hive/
│   ├── create_tables.hql                   # External table DDL with OpenCSVSerde
│   └── analytics.hql                       # Analytical queries & decadal trends
├── tests/
│   ├── test_data_validation.py             # Pytest: schemas, types, whitespace
│   ├── test_mapreduce.py                   # Pytest: mapper/reducer logic on fixtures
│   └── test_aggregations.py                # Pytest: outputs, figures, consistency
├── outputs/
│   ├── tables/                             # 5 analytical CSV tables + 2 MapReduce TSVs
│   ├── figures/                            # 5 high-resolution PNG figures (300 DPI)
│   └── reports/                            # Technical reports (MD, HTML, JSON)
└── logs/                                   # Complete pipeline execution logs
```
