# Operational Runbook & Execution Guide

This document provides start-to-finish instructions for deploying, operating, verifying, and testing the Agricultural Big Data Analytics System.

---

## 1. System Prerequisites

- **Operating System:** macOS (Apple Silicon `arm64` or Intel `x86_64`)
- **Java Runtime:** OpenJDK 17 (`JAVA_HOME` configured)
- **Hadoop Ecosystem:** Apache Hadoop 3.5.0 installed via Homebrew (`/opt/homebrew/opt/hadoop/libexec`)
- **Python Environment:** Python 3.9+ with virtual environment at `.venv`
- **Disk Storage:** Minimum 20 GB free disk space (to host >= 7 GB raw, ~9 GB cleaned, and distributed HDFS blocks)

---

## 2. HDFS Cluster Startup & Verification

> [!CAUTION]
> **Never execute `hdfs namenode -format`**. The NameNode is already formatted. Running format will permanently destroy existing HDFS block metadata!

### Start HDFS Daemons:
```bash
start-dfs.sh
```

### Verify Running Daemons:
```bash
jps
```
Expected output should list `NameNode`, `DataNode`, `SecondaryNameNode`, and `Jps`.

### Check Cluster Health & Storage:
```bash
hdfs dfsadmin -report
hdfs dfs -ls /
```

---

## 3. Python Virtual Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install project dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. End-to-End Pipeline Execution

You can run the entire pipeline sequentially or via the automated master script.

### Option A: One-Command Master Execution
```bash
./scripts/run_pipeline.sh
```
All outputs and console logs will be preserved in `logs/pipeline_YYYYMMDD_HHMMSS.log`.

---

### Option B: Step-by-Step Manual Execution

#### Step 1: Environment Health Check
```bash
./scripts/check_environment.sh
```

#### Step 2: Automated Dataset Ingestion & Verification
Downloads official datasets to `data/raw/` and computes SHA-256 hashes:
```bash
./.venv/bin/python scripts/download_data.py
```

#### Step 3: Data Quality & Schema Audit
Runs schema, null, range, and duplicate validations:
```bash
./.venv/bin/python scripts/validate_data.py
```
Outputs saved to `outputs/reports/data_validation_report.json` and `.md`.

#### Step 4: Data Cleaning & Normalization
Sanitizes strings, derives `Yield = Production / Area`, and creates state-level aggregates:
```bash
./.venv/bin/python src/python/clean_data.py
```
Cleaned files generated in `data/processed/`.

#### Step 5: Ingestion into HDFS
Creates HDFS directories and uploads raw and cleaned datasets:
```bash
./scripts/upload_to_hdfs.sh
```
Verify HDFS storage:
```bash
hdfs dfs -ls -R /user/dhruvgohil/agriculture
```

#### Step 6: Execute Distributed Hadoop MapReduce Jobs
Runs both streaming MapReduce jobs on HDFS and triggers independent Python cross-validation:
```bash
./scripts/run_mapreduce.sh
```
Results saved to `outputs/tables/mr_crop_production_results.tsv` and `mr_rainfall_results.tsv`.

#### Step 7: Exploratory Analytics & Chart Generation
Computes 5 analytical CSV tables and generates 5 publication-ready PNG figures (300 DPI):
```bash
./.venv/bin/python src/python/exploratory_analysis.py
```

#### Step 8: Generate Academic Reports
Builds the final technical Markdown and interactive HTML reports:
```bash
./.venv/bin/python src/python/generate_report.py
```
Open `outputs/reports/final_academic_report.html` in your web browser.

#### Step 9: Run Automated Test Suite
Executes all 10 automated unit and integration tests:
```bash
./.venv/bin/pytest tests/ -v
```

---

## 5. Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `SocketException: Operation not permitted` | Sandboxed environment or HDFS daemons not started. | Run `start-dfs.sh` and ensure terminal has local network access. |
| `WARN util.NativeCodeLoader` | Missing Hadoop native C libraries for macOS arm64. | Non-fatal warning; Hadoop automatically falls back to pure Java classes. |
| `ModuleNotFoundError: No module named 'pyspark'` | PySpark is an optional component; binary wheels are omitted on macOS arm64. | Run `./.venv/bin/python src/pyspark/crop_rainfall_pyspark.py` to view setup notes; the core pipeline uses Hadoop MapReduce. |
| `Retrying connect to server: 0.0.0.0:8032` | YARN ResourceManager not started while running MapReduce in YARN mode. | The project's `run_mapreduce.sh` explicitly passes `-D mapreduce.framework.name=local` to execute MapReduce streaming seamlessly against HDFS without requiring YARN. |
