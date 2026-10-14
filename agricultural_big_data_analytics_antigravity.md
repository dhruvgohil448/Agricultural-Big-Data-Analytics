# Agricultural Big Data Analytics System

## End-to-End Project Specification for Antigravity

**Project:** Agricultural Big Data Analytics System\
**Environment:** macOS Apple Silicon, local Hadoop/HDFS\
**Purpose:** Build a complete, reproducible academic big-data project
using real public agricultural CSV datasets.

## 1. Mission

Act as a senior data engineer and build the complete project in the
current workspace. Do not stop at a plan or pseudocode. Research
datasets, download them where accessible, validate and process them, run
the pipeline where the environment supports it, test results, and write
documentation.

The pipeline should demonstrate:

**Public CSV datasets → validation and cleaning → HDFS → Hadoop
MapReduce → Hive/PySpark where compatible → Python/R analysis → charts
and final report**

This is an academic analytics prototype. Do not claim real-time
monitoring, guaranteed forecasts, causal effects, or operational
recommendations unless genuinely implemented and validated.

## 2. Mandatory safety and execution rules

1.  Inspect the workspace before creating files. If a project already
    exists, preserve it; do not overwrite user work.
2.  Inspect the environment before installing anything. Verify OS,
    architecture, Java, Hadoop, Python, R, Git, and disk space.
3.  **Never run `hdfs namenode -format`.** The NameNode has already been
    formatted and HDFS tested. Reformatting can destroy existing HDFS
    metadata/data.
4.  Never fabricate datasets, sources, licenses, metrics, test results,
    or successful execution claims.
5.  Prefer official government, public research, or reputable open-data
    sources. Verify dataset landing page, direct download URL,
    terms/license, fields, units, geography, and time coverage.
6.  Preserve downloaded originals. Put cleaned/derived files in separate
    directories.
7.  Use scripts/configuration for repeatability. Record commands,
    inputs, outputs, row counts, warnings, and exit status.
8.  If a tool is incompatible or unavailable, document the exact
    limitation and provide a realistic alternative. Do not claim a
    component ran if it did not.
9.  Do not commit credentials, tokens, SSH keys, or unnecessary large
    datasets.
10. Build incrementally, run tests, and fix errors before moving on.

## 3. Known environment snapshot --- verify before use

The user previously installed and tested: - macOS on Apple Silicon
(`arm64`) - Homebrew Hadoop 3.5.0 - OpenJDK 17 -
`HADOOP_HOME=/opt/homebrew/opt/hadoop/libexec` - Config directory:
`$HADOOP_HOME/etc/hadoop` - `fs.defaultFS=hdfs://localhost:9000` - HDFS
web interface: `http://localhost:9870` - HDFS replication set to 1 for
local development - NameNode has already been formatted -
`ssh localhost` was configured successfully - `start-dfs.sh` previously
started NameNode, DataNode, and SecondaryNameNode -
`WARN util.NativeCodeLoader` has appeared and may be non-fatal; confirm
actual command success.

Check current state using:

``` bash
uname -m
sw_vers
java -version
hadoop version
hdfs getconf -confKey fs.defaultFS
python3 --version
R --version
git --version
df -h .
jps
hdfs dfs -ls /
hdfs dfs -ls /user/dhruvgohil/
```

If HDFS daemons are stopped, use `start-dfs.sh`. Inspect logs if startup
fails. Do not reformat.

## 4. Project goal and research questions

Analyze agricultural data, prioritizing India where suitable datasets
are available. Answer only questions supported by selected data, for
example: - Crop production by crop, region, and year - Cultivated area
and yield trends, if definitions and units are known - Rainfall patterns
by location and year - Data quality: missing, duplicate, inconsistent,
and suspicious records - Association between rainfall and production
only when time and geography can be aligned reliably

Do not infer causation from correlation. If datasets cannot be reliably
joined, analyze them separately and explain why.

## 5. Dataset discovery and download

Investigate public CSV datasets from credible sources. These are
starting points to investigate, not confirmation that a specific file is
available or licensed: - Open Government Data Platform India:
https://www.data.gov.in/ - Ministry of Agriculture & Farmers Welfare:
https://agriwelfare.gov.in/ - India Meteorological Department:
https://mausam.imd.gov.in/ - FAOSTAT: https://www.fao.org/faostat/ -
World Bank Data: https://data.worldbank.org/

Aim for at least two datasets: 1. Crop production/area/yield, with year
and state or district where possible. 2. Rainfall with a compatible year
and geographic key.

An optional third dataset may cover soil, irrigation, fertilizer, or
crop prices if provenance and fields are clear.

For each candidate, assess: - Public accessibility and CSV
availability - Credibility and reuse terms - Column definitions and
units - Geography and date coverage - Size and suitability for
processing - Whether joining is defensible

Download originals to `data/raw/`, using `curl -L` or Python requests
where appropriate. Do not bypass access controls. If interactive
download is required, document the manual steps. Create
`docs/data_sources.md` with source and direct URLs, publisher,
license/terms URL, download date, filename, file size, SHA-256,
coverage, schema, units, and limitations. Create
`docs/data_dictionary.md` for every field and transformation.

## 6. Repository structure

Inspect before creating. Use this as a suggested structure and adapt if
needed:

``` text
agricultural-big-data-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── config/project.yaml
├── data/
│   ├── raw/.gitkeep
│   ├── processed/.gitkeep
│   └── sample/.gitkeep
├── docs/
│   ├── architecture.md
│   ├── data_sources.md
│   ├── data_dictionary.md
│   ├── methodology.md
│   ├── limitations.md
│   └── runbook.md
├── scripts/
│   ├── check_environment.sh
│   ├── download_data.py
│   ├── validate_data.py
│   ├── upload_to_hdfs.sh
│   └── run_pipeline.sh
├── src/
│   ├── python/
│   │   ├── clean_data.py
│   │   ├── exploratory_analysis.py
│   │   └── generate_report.py
│   ├── mapreduce/
│   ├── pyspark/
│   └── r/
├── hive/
│   ├── create_tables.hql
│   └── analytics.hql
├── notebooks/
├── tests/
├── outputs/
│   ├── tables/
│   ├── figures/
│   └── reports/
└── logs/
```

Ignore large raw data and generated artifacts in Git unless a small
sample is needed for reproducible tests. Include a `.gitignore` and
dependency specification.

## 7. Data ingestion and quality

Implement repeatable download/ingestion and validation. Checks should
include: - File exists and is non-empty - CSV encoding, delimiter, and
headers - Required columns - Numeric and date/year parsing - Missing
values and duplicate counts - Invalid or suspicious values - Unit
consistency - Geographic-name normalization through explicit mappings
only

Produce a validation report with input row count, cleaned row count,
nulls, duplicates, invalid rows, and decisions. Do not silently delete
outliers or records. Preserve raw files unchanged.

## 8. HDFS setup and upload

Use this project root:

``` text
/user/dhruvgohil/agriculture/
├── input/
│   ├── crop_production/
│   ├── rainfall/
│   └── soil/
├── processed/
├── output/
└── reports/
```

Create directories idempotently:

``` bash
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/input/crop_production
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/input/rainfall
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/input/soil
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/processed
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/output
hdfs dfs -mkdir -p /user/dhruvgohil/agriculture/reports
```

Validate local CSVs before uploading with `hdfs dfs -put` or
`hdfs dfs -copyFromLocal`. Check destination first to avoid accidental
duplicates. Verify with:

``` bash
hdfs dfs -ls -R /user/dhruvgohil/agriculture
hdfs dfs -du -h /user/dhruvgohil/agriculture
```

Also verify uploaded content or record counts. Keep HDFS output paths
separate from inputs. Hadoop jobs generally require a new output
directory; only remove a generated output directory after verifying the
exact path.

## 9. Processing tools

### Hadoop MapReduce --- required

Implement at least one meaningful job, such as production totals by
crop/year or rainfall aggregation by region/year. Explain mapper/reducer
input and output, handle headers and malformed rows, test on a small
fixture, then run against HDFS if supported. Verify results against an
independent Python calculation. If using Hadoop Streaming, locate and
verify the installed streaming JAR rather than assuming its path.
Otherwise use a compatible Java MapReduce job or document an
alternative.

### Hive --- if compatible

Create SQL table definitions and queries for aggregates/trends. Use
explicit schemas and delimiters. Save scripts in `hive/`. Run and
validate if Hive is available and compatible. If not, document the exact
limitation and do not claim execution.

### PySpark --- if compatible

Implement a distinct transformation or analysis using PySpark, with
explicit schema/type/null handling. Read local or HDFS data depending on
compatibility, write to a separate output, and compare key aggregates
with MapReduce/Python. If it cannot run with the installed environment,
document the error and provide setup instructions. Do not claim pandas
is PySpark.

### Python

Use Python for EDA, validation, descriptive statistics, independent
checks, charts, and report generation. Use suitable installed libraries
(for example pandas and matplotlib). Charts need titles, axes, units,
legends, and source notes.

### R

Create a meaningful statistical analysis or independent cross-check
under `src/r/`. Document packages and execution commands. If R is
unavailable, provide the script and mark it as not executed.

Only include tools that serve a clear purpose; report accurately which
tools actually ran.

## 10. Outputs and presentation

Where data supports them, produce: 1. Production by crop and year 2.
Regional crop comparisons 3. Area/yield trends with verified definitions
and units 4. Rainfall summaries by year/region 5. Rainfall-production
association only with defensible geographic/time alignment 6.
Data-quality summary 7. At least three useful charts, where data permits

Save tables as CSV and figures as PNG under `outputs/`; optionally copy
results to HDFS. Generate a final report with executive summary,
sources/coverage, methods, findings, figures, data quality, limitations,
and reproduction instructions.

A static HTML report or Jupyter Notebook is sufficient. A Streamlit
dashboard is optional and should only be added if it can be run
reliably. Do not create fake live-data indicators.

## 11. Architecture

Create `docs/architecture.md` with a Mermaid diagram matching the actual
implementation. A starting concept:

``` mermaid
flowchart TD
    A[Public agricultural CSV datasets] --> B[Download and source metadata]
    B --> C[Local raw data]
    C --> D[Validation and cleaning]
    D --> E[HDFS input]
    E --> F[Hadoop MapReduce]
    E --> G[Hive SQL, if supported]
    E --> H[PySpark, if supported]
    F --> I[Aggregated results]
    G --> I
    H --> I
    I --> J[Python and R analysis]
    J --> K[Charts and final report]
```

Update the diagram to show only components actually implemented;
distinguish optional/unexecuted components.

## 12. Testing

Create automated tests for: - CSV parsing and required columns - Numeric
conversion and missing values - Duplicate handling - Aggregation
correctness - MapReduce output against a small expected fixture -
Cross-tool consistency where feasible

Run tests and record actual results. Do not claim tests passed unless
they were executed. Log commands, exit codes, inputs, outputs, and
warnings for each major stage.

## 13. Documentation and deliverables

The repository must contain: - `README.md`: overview, prerequisites,
setup, commands, expected outputs - `docs/data_sources.md`: verified
links, terms, metadata - `docs/data_dictionary.md` -
`docs/architecture.md` - `docs/methodology.md` - `docs/limitations.md` -
`docs/runbook.md`: start-to-finish commands - Download, validation,
cleaning, HDFS upload, and pipeline scripts - At least one implemented
MapReduce job - Hive/PySpark components if compatible, otherwise honest
limitations and alternatives - Python and R analysis scripts - Tests and
actual test results - Output tables, charts, and final report -
`.gitignore` and dependency file

## 14. Execution sequence

1.  **Inspect:** inspect workspace and tools; verify Hadoop/HDFS without
    formatting.
2.  **Research:** find candidate datasets, compare
    provenance/terms/fields, select compatible sources, and download
    originals.
3.  **Validate:** inspect schemas and samples; implement cleaning and
    data-quality reports.
4.  **HDFS:** create folders, upload files, verify paths and content.
5.  **MapReduce:** implement, test locally, run on HDFS, and
    independently validate output.
6.  **Hive/PySpark:** implement and run if compatible; otherwise
    document exact limitations.
7.  **Python/R:** perform descriptive analysis, cross-checks, and
    visualizations.
8.  **Report:** create report and optional presentation/dashboard.
9.  **Final verification:** run tests and pipeline; verify documentation
    commands; summarize completed, tested, and unverified components.

At meaningful checkpoints, explain what was done and show the user the
important choices. Ask only when a decision genuinely requires user
approval, such as unclear licensing or a major tradeoff.

## 15. Definition of done

-   [ ] Real public datasets have verified sources and reuse terms.
-   [ ] Original CSVs and metadata are preserved.
-   [ ] Validation and cleaning are reproducible.
-   [ ] HDFS folders and uploads are verified.
-   [ ] At least one MapReduce job is implemented and tested.
-   [ ] Hive and PySpark run if compatible, or limitations are
    documented honestly.
-   [ ] Python analysis and charts use actual data.
-   [ ] R analysis exists and execution status is stated.
-   [ ] Tests are run and results recorded.
-   [ ] README and runbook accurately reproduce the pipeline.
-   [ ] No fabricated sources, findings, or successful-run claims.
-   [ ] Existing workspace files and HDFS metadata are preserved.

## 16. First actions

Begin by inspecting the current workspace and environment. Verify the
existing Hadoop installation and HDFS state without formatting the
NameNode. Then create the repository structure without overwriting
existing work. Research and shortlist credible public agricultural CSV
datasets, showing source links, terms, fields, and proposed analyses.
Continue through implementation and testing; do not return only a plan.
