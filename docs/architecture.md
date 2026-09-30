# System Architecture & Technical Design

This document details the multi-tier architectural design of the Agricultural Big Data Analytics System, from edge ingestion through distributed HDFS storage, Hadoop MapReduce computation, and presentation.

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Data_Layer["1. Data Ingestion & Quality Verification"]
        D1["Ministry of Agriculture & Farmers Welfare<br/>(246,091 records)"] --> P1["scripts/download_data.py<br/>(SHA-256 Checksum & Sample Fixtures)"]
        D2["India Meteorological Department<br/>(4,116 records)"] --> P1
        P1 --> P2["scripts/validate_data.py<br/>(Schema, Range, Nulls & Duplicates)"]
        P2 --> P3["src/python/clean_data.py<br/>(Whitespace Sanitization & Yield Derivation)"]
    end

    subgraph HDFS_Layer["2. Distributed HDFS Storage (fs.defaultFS: hdfs://localhost:9000)"]
        P3 --> H1["/user/dhruvgohil/agriculture/input/<br/>Raw CSV Ingestion"]
        P3 --> H2["/user/dhruvgohil/agriculture/processed/<br/>Cleaned Datasets"]
        H3["/user/dhruvgohil/agriculture/output/<br/>MapReduce Results"]
    end

    subgraph Compute_Layer["3. Distributed Big Data Compute Engines"]
        H1 --> MR1["Hadoop MapReduce (Streaming 3.5.0)<br/>Job 1: Crop Yield & Area Aggregator"]
        H1 --> MR2["Hadoop MapReduce (Streaming 3.5.0)<br/>Job 2: Decadal Meteorological Aggregator"]
        MR1 --> H3
        MR2 --> H3

        H2 -.->|Schema Mapped| HV["Apache Hive (HQL Scripts)<br/>(create_tables.hql, analytics.hql)<br/>[Cluster-Ready / Unexecuted Locally]"]
        H2 -.->|Code Implemented| SP["PySpark DataFrame Pipeline<br/>(crop_rainfall_pyspark.py)<br/>[Documented Alternative]"]
    end

    subgraph Presentation_Layer["4. Validation, Analytics & Presentation"]
        H3 --> V1["src/mapreduce/verify_mapreduce.py<br/>(Independent Python Cross-Validation: 0.0000 Diff)"]
        H2 --> EA["src/python/exploratory_analysis.py<br/>(5 CSV Tables & 5 High-Res Figures)"]
        H2 -.->|Script Provided| R1["src/r/statistical_analysis.R<br/>(OLS Regression & Econometric Model)"]
        EA --> REP["src/python/generate_report.py<br/>(Markdown & Standalone Interactive HTML Reports)"]
        V1 --> REP
    end

    style HV stroke-dasharray: 5 5
    style SP stroke-dasharray: 5 5
    style R1 stroke-dasharray: 5 5
```

---

## 2. Layer-by-Layer Architectural Breakdown

### Layer 1: Ingestion & Quality Verification
- **Automated Download:** Idempotent fetching of primary open data sources with secondary fallback mirrors and cryptographic SHA-256 verification.
- **Quality Audit:** Structural inspection verifying 7 required crop fields, 19 meteorological fields, absence of negative cultivated areas, and explicit accounting for missing values (3,730 crop records).
- **Standardization:** Strips trailing categorical spaces, standardizes state nomenclature, and derives the unit-aware metric `Yield = Production / Area`.

### Layer 2: Distributed Storage (Apache HDFS)
- **Filesystem URI:** `hdfs://localhost:9000`
- **Replication Factor:** 1 (optimized for Apple Silicon local development).
- **Cluster Capacity:** 228 GB total volume, ~96 GB DFS available.
- **Hierarchy:**
  - `input/`: Preserved raw government CSVs.
  - `processed/`: Cleaned, schema-normalized CSVs.
  - `output/`: Clustered MapReduce part-files.
  - `reports/`: Audit logs and pipeline summaries.

### Layer 3: Distributed Compute (Hadoop MapReduce)
- **Engine:** Hadoop Streaming 3.5.0 with POSIX standard streams (`stdin` / `stdout`).
- **Job 1 (Crop Aggregator):**
  - Mapper emits composite key: `State_Name##Crop##Crop_Year \t Area \t Production`.
  - Reducer accumulates district areas and harvests, computing weighted state-level crop yields and record counts.
  - Performance: Processed 246,091 records into 12,986 groups in ~8 seconds.
- **Job 2 (Meteorological Decadal Aggregator):**
  - Mapper computes decadal bucket (`(Year // 10) * 10`) and emits `SUBDIVISION##Decade \t Annual \t Monsoon \t 1`.
  - Reducer computes decadal average annual and monsoon precipitation across 115 years.
  - Performance: Processed 4,090 records into 431 groups.

### Layer 4: SQL & Distributed DataFrame Layer
- **Hive:** External tables mapped to HDFS `/user/dhruvgohil/agriculture/processed/` using `OpenCSVSerde`. Comprehensive DDL and analytical SQL queries are saved in `hive/`.
- **PySpark:** Complete script provided in `src/pyspark/` utilizing explicit `StructType` schemas, window aggregations, and inner joins between crop and rainfall tables.

### Layer 5: Statistical Analytics & Presentation
- **Validation:** `verify_mapreduce.py` independently computes expected sums using pandas and verifies numerical equality down to four decimal places.
- **Exploratory Analytics:** Python generates 5 analytical CSV tables and 5 high-resolution figures (300 DPI) adhering to academic styling rules.
- **Reporting:** Produces both an extensive Markdown technical report and a self-contained, interactive HTML document.
