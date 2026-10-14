# Agricultural Big Data Analytics System

## End-to-End Implementation and Submission Guide

**Project type:** Big Data Analytics\
**Domain:** Agriculture\
**Platform:** macOS (single-node Hadoop / pseudo-distributed setup)\
**Core technologies:** Hadoop, HDFS, MapReduce (Hadoop Streaming with
Python), Hive, PySpark, R\
**Suggested timeline:** 2 days\
**Project goal:** Store agricultural data in HDFS, process and analyze
it with Hadoop tools, and present results as tables and visualizations.

> Important: Tool versions and installation layouts vary. Verify each
> installation before proceeding. Do not claim a component works until
> you have run it and captured its output. With a two-day deadline,
> prioritize a working HDFS → processing → results pipeline; treat Hive
> and R as additional milestones if setup becomes difficult.

------------------------------------------------------------------------

# 1. Define the project

## 1.1 Problem statement

Agricultural datasets are often large and spread across years, crops,
seasons, and regions. This project demonstrates how a Big Data ecosystem
can store and analyze crop-production records and, when compatible
weather data is available, examine historical rainfall and temperature
alongside production.

## 1.2 Objectives

1.  Configure Hadoop and HDFS on one machine.
2.  Store a crop-production dataset in HDFS.
3.  Run a MapReduce job to aggregate production by crop.
4.  Use PySpark to clean and analyze agricultural records.
5.  Use Hive SQL to query the stored data.
6.  Export results and create charts using R.
7.  Document the architecture, commands, outputs, limitations, and
    findings.

## 1.3 Scope and honest interpretation

The minimum project can use crop-production data alone. Rainfall and
temperature analysis requires datasets with compatible geography and
time periods. A correlation is an association, not proof that weather
caused a change in production. This is a historical analytics project,
not a real-time crop prediction or advisory system.

## 1.4 Questions the project should answer

-   Which crops have the largest recorded production?
-   Which states or districts contribute the most production?
-   How does production change across years and seasons?
-   What is the calculated yield per hectare?
-   If weather data is available, how do rainfall and temperature vary
    alongside production?

------------------------------------------------------------------------

# 2. Plan the folder structure

Create a project folder:

``` bash
mkdir -p ~/AgriculturalBigData/{data/raw,data/processed,src/mapreduce,src/pyspark,src/hive,src/r,output,screenshots,report}
cd ~/AgriculturalBigData
```

Recommended structure:

``` text
AgriculturalBigData/
├── data/
│   ├── raw/                 # Original downloaded CSV files
│   └── processed/           # Cleaned/local intermediate files
├── src/
│   ├── mapreduce/
│   │   ├── mapper.py
│   │   └── reducer.py
│   ├── pyspark/
│   │   └── agricultural_analysis.py
│   ├── hive/
│   │   └── analysis.sql
│   └── r/
│       └── visualize.R
├── output/                  # Exported analysis results
├── screenshots/             # Evidence for the report
└── report/                  # Final report and presentation material
```

Keep an untouched copy of the original dataset in `data/raw`.

------------------------------------------------------------------------

# 3. Select and inspect the dataset

## 3.1 Recommended source

Use an openly available Indian crop-production dataset from the
Government of India's Open Government Data platform:

-   https://www.data.gov.in/
-   Search for: **district-wise season-wise crop production statistics**

A suitable dataset should contain fields equivalent to: - State -
District - Crop year - Season - Crop - Area - Production

Field names and units may differ. Use the exact names in your downloaded
file when writing code.

Optional weather sources: - India Meteorological Department:
https://mausam.imd.gov.in/ - National Water Data Portal:
https://nwdp.nwic.gov.in/

Only combine weather data if region names, date/year definitions, and
units can be matched reliably. If that takes too long, finish the
crop-only pipeline.

## 3.2 Save and inspect the CSV

Save the downloaded file as `data/raw/crop_production.csv`.

Inspect it:

``` bash
head -5 data/raw/crop_production.csv
wc -l data/raw/crop_production.csv
```

Check: - Is there a header row? - What are the exact column names? - Are
area and production numeric? - Are missing values represented by blank
cells, `NA`, or another marker? - What are the production and area
units? - Does the file contain multiple years and regions?

Do not assume the example field names in this guide match the dataset.

## 3.3 Create a data dictionary

Record each column, its meaning, type, and unit. For example:

  Field        Meaning                    Type / unit
  ------------ -------------------------- ----------------------------------
  State        State or union territory   Text
  District     District name              Text
  Crop_Year    Observation year           Integer
  Season       Agricultural season        Text
  Crop         Crop name                  Text
  Area         Cultivated area            Dataset-specific area unit
  Production   Crop production            Dataset-specific production unit

Use the dataset's actual units in the final report.

------------------------------------------------------------------------

# 4. Install and verify prerequisites

## 4.1 Check existing tools first

On macOS, open Terminal:

``` bash
java -version
python3 --version
brew --version
hadoop version
```

If Hadoop is already installed, do not reinstall it just to follow this
guide.

## 4.2 Install missing tools

Using Homebrew where available:

``` bash
brew install hadoop
brew install apache-spark
brew install hive
```

Install Python packages:

``` bash
python3 -m pip install pyspark pandas
```

Install R from https://cran.r-project.org/ if it is not already
installed. RStudio is optional.

Check:

``` bash
hadoop version
spark-submit --version
python3 -c "import pyspark; print(pyspark.__version__)"
R --version
```

Hive packaging and compatibility can vary. If the Homebrew installation
is unavailable or incompatible, document the issue and continue with the
working HDFS and Spark pipeline rather than losing the whole project to
installation troubleshooting.

------------------------------------------------------------------------

# 5. Configure Hadoop for single-node HDFS

A single-node pseudo-distributed configuration runs Hadoop services on
one machine. It is suitable for a student demonstration, but it does not
demonstrate actual multi-machine fault tolerance or cluster scaling.

## 5.1 Find Hadoop's configuration directory

``` bash
brew --prefix hadoop
```

A common Homebrew layout is:

``` text
$(brew --prefix hadoop)/libexec/etc/hadoop/
```

Confirm the directory exists before editing files.

## 5.2 Set `core-site.xml`

Set the default filesystem. The port must be consistent across your
configuration and commands.

``` xml
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:9000</value>
  </property>
</configuration>
```

## 5.3 Set `hdfs-site.xml`

For a one-DataNode demonstration, replication is set to 1. Use dedicated
directories for NameNode and DataNode data.

``` xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///tmp/hadoop-dhruv/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///tmp/hadoop-dhruv/datanode</value>
  </property>
</configuration>
```

Create the local directories if needed:

``` bash
mkdir -p /tmp/hadoop-dhruv/namenode
mkdir -p /tmp/hadoop-dhruv/datanode
```

## 5.4 Set Java in `hadoop-env.sh`

Find Java's home:

``` bash
/usr/libexec/java_home
```

Set `JAVA_HOME` in `hadoop-env.sh` to the path returned by the command.
Do not copy a Java path from another machine.

## 5.5 Configure localhost SSH if required

Some Hadoop start scripts use SSH even for a local setup. Test:

``` bash
ssh localhost
```

If it fails and your Hadoop script requires it, configure a local SSH
key and authorize it for localhost according to your macOS SSH setup. Do
not disable SSH security globally.

## 5.6 Format and start HDFS

Only format a new NameNode. Formatting an existing NameNode can make
existing HDFS metadata inaccessible.

``` bash
hdfs namenode -format
start-dfs.sh
jps
```

Expected Java processes commonly include: - NameNode - DataNode -
SecondaryNameNode

Exact process names can vary by setup.

## 5.7 Verify HDFS

``` bash
hdfs dfs -mkdir -p /agriculture/raw
hdfs dfs -ls /
hdfs dfsadmin -report
```

If these commands succeed, HDFS is responding.

Useful optional web interfaces are often: - NameNode:
http://localhost:9870 - DataNode: http://localhost:9864

Ports can vary by Hadoop version and configuration.

**Evidence to capture:** `jps`, `hdfs dfs -ls /`, and
`hdfs dfsadmin -report`.

------------------------------------------------------------------------

# 6. Upload the dataset to HDFS

Copy the downloaded file into the project folder, then upload it:

``` bash
hdfs dfs -mkdir -p /agriculture/raw
hdfs dfs -put data/raw/crop_production.csv /agriculture/raw/
hdfs dfs -ls /agriculture/raw
```

View a small portion:

``` bash
hdfs dfs -cat /agriculture/raw/crop_production.csv | head
```

If a file already exists, use `-put -f` only when you intentionally want
to overwrite it.

Create output folders only when needed. Hadoop jobs normally require the
output directory not to exist before a run.

**Milestone:** The original CSV is visible in HDFS.

------------------------------------------------------------------------

# 7. Build a Python MapReduce job with Hadoop Streaming

## 7.1 What this job does

The mapper emits `(crop, production)` pairs. Hadoop groups the same crop
keys, and the reducer sums their production values.

This demonstrates a real MapReduce aggregation. It is separate from
Spark; both are included to show different processing approaches.

## 7.2 Important data preparation

The simple example below assumes the CSV has columns named `Crop` and
`Production`, and that the file is a standard comma-separated CSV with a
header. If the downloaded file uses different field names or unusual CSV
quoting, adjust the script or create a normalized CSV first.

Create `src/mapreduce/mapper.py`:

``` python
#!/usr/bin/env python3
import sys
import csv

reader = csv.DictReader(sys.stdin)

for row in reader:
    crop = (row.get("Crop") or "").strip()
    production = (row.get("Production") or "").strip()

    if not crop or not production:
        continue

    try:
        value = float(production)
    except ValueError:
        continue

    print(f"{crop}\t{value}")
```

Create `src/mapreduce/reducer.py`:

``` python
#!/usr/bin/env python3
import sys

current_crop = None
total = 0.0

for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue

    crop, value = line.split("\t", 1)

    try:
        value = float(value)
    except ValueError:
        continue

    if crop == current_crop:
        total += value
    else:
        if current_crop is not None:
            print(f"{current_crop}\t{total}")

        current_crop = crop
        total = value

if current_crop is not None:
    print(f"{current_crop}\t{total}")
```

Make the scripts executable:

``` bash
chmod +x src/mapreduce/mapper.py src/mapreduce/reducer.py
```

The Hadoop Streaming reducer expects keys to be grouped and sorted.
Hadoop Streaming performs the shuffle and sort stage.

## 7.3 Find the Streaming JAR

``` bash
find "$(brew --prefix hadoop)" -name 'hadoop-streaming*.jar'
```

Use the actual path returned. If no JAR is found, check the installed
Hadoop package and its available components.

## 7.4 Run the job

From the project directory, replace `/ACTUAL/PATH/hadoop-streaming.jar`
with the path you found:

``` bash
hadoop jar /ACTUAL/PATH/hadoop-streaming.jar \
  -files src/mapreduce/mapper.py,src/mapreduce/reducer.py \
  -mapper mapper.py \
  -reducer reducer.py \
  -input /agriculture/raw/crop_production.csv \
  -output /agriculture/output/mapreduce_crop_totals
```

If the output directory already exists from a previous run, remove that
output directory first:

``` bash
hdfs dfs -rm -r /agriculture/output/mapreduce_crop_totals
```

Only remove the generated output directory, not your raw input data.

## 7.5 View the output

``` bash
hdfs dfs -cat /agriculture/output/mapreduce_crop_totals/part-*
```

Verify a few crop totals against a small manual sample or an independent
aggregation.

**Evidence to capture:** job completion message and the `part-*` output.

------------------------------------------------------------------------

# 8. Analyze the dataset with PySpark

## 8.1 What PySpark does

PySpark is Python's API for Apache Spark. It provides DataFrame
operations for reading, filtering, transforming, grouping, and
aggregating data. In this project, use it to clean records and calculate
agricultural metrics.

## 8.2 Create the script

Create `src/pyspark/agricultural_analysis.py`.

The example below assumes a normalized CSV with these columns: `State`,
`District`, `Crop_Year`, `Season`, `Crop`, `Area`, and `Production`.

If your actual dataset uses different column names, update the script
accordingly.

``` python
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum as spark_sum, avg, count,
    when, round
)

spark = (
    SparkSession.builder
    .appName("AgriculturalBigDataAnalytics")
    .getOrCreate()
)

input_path = (
    "hdfs://localhost:9000/agriculture/raw/"
    "crop_production.csv"
)

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(input_path)
)

print("Schema:")
df.printSchema()

print("Sample records:")
df.show(10, truncate=False)

# Convert expected numeric columns and remove unusable rows.
df = (
    df.withColumn("Area", col("Area").cast("double"))
      .withColumn("Production", col("Production").cast("double"))
      .withColumn("Crop_Year", col("Crop_Year").cast("int"))
)

clean = df.filter(
    col("Crop").isNotNull() &
    col("Area").isNotNull() &
    col("Production").isNotNull() &
    (col("Area") >= 0) &
    (col("Production") >= 0)
)

# Crop-wise production
crop_totals = (
    clean.groupBy("Crop")
    .agg(round(spark_sum("Production"), 2).alias("Total_Production"))
    .orderBy(col("Total_Production").desc())
)

crop_totals.show(20, truncate=False)

# State-wise production
state_totals = (
    clean.groupBy("State")
    .agg(round(spark_sum("Production"), 2).alias("Total_Production"))
    .orderBy(col("Total_Production").desc())
)

state_totals.show(20, truncate=False)

# Calculate yield. Check that area and production units are compatible.
yield_data = (
    clean.filter(col("Area") > 0)
    .withColumn("Yield", col("Production") / col("Area"))
)

yield_data.select(
    "State", "District", "Crop_Year", "Crop", "Area",
    "Production", "Yield"
).show(20, truncate=False)

# Production by year
yearly = (
    clean.groupBy("Crop_Year")
    .agg(round(spark_sum("Production"), 2).alias("Total_Production"))
    .orderBy("Crop_Year")
)

yearly.show(50, truncate=False)

# Save results to HDFS as CSV directories.
base = "hdfs://localhost:9000/agriculture/processed"

crop_totals.coalesce(1).write.mode("overwrite").option(
    "header", True
).csv(base + "/crop_totals")

state_totals.coalesce(1).write.mode("overwrite").option(
    "header", True
).csv(base + "/state_totals")

yearly.coalesce(1).write.mode("overwrite").option(
    "header", True
).csv(base + "/yearly_production")

spark.stop()
```

**Note:** `coalesce(1)` is convenient for a small student demonstration
because it creates one data part, but it is not recommended for large
production datasets. Spark writes output as directories containing part
files, not as a single CSV file.

## 8.3 Run the script

``` bash
spark-submit src/pyspark/agricultural_analysis.py
```

If the HDFS connection fails, first verify that HDFS is running and that
Spark has compatible Hadoop client configuration. A local Spark test can
help separate Spark installation issues from HDFS issues.

## 8.4 Verify output

``` bash
hdfs dfs -ls /agriculture/processed
hdfs dfs -cat /agriculture/processed/crop_totals/part-*
```

**Milestone:** PySpark reads data from HDFS, performs multiple analyses,
and writes results back to HDFS.

------------------------------------------------------------------------

# 9. Configure Hive and query the data

## 9.1 What Hive does

Hive is a data warehouse system that allows SQL-style querying of data
stored in Hadoop-compatible storage. Its metastore stores table
definitions and metadata. Hive is not a replacement for HDFS.

Hive setup can be version-sensitive. Make sure your Hive, Java, and
Hadoop versions are compatible.

## 9.2 Start with a small test

Verify the installation:

``` bash
hive --version
```

Depending on the installed Hive version, use its supported metastore and
query-service startup procedure. Some versions require a separately
initialized metastore database and HiveServer2.

If you have a working Beeline connection, proceed with the SQL below.

## 9.3 Create a database and external table

The following is a template for a normalized CSV. Change column names,
types, and HDFS location to match your actual data.

``` sql
CREATE DATABASE IF NOT EXISTS agriculture;
USE agriculture;

CREATE EXTERNAL TABLE IF NOT EXISTS crop_production (
    state STRING,
    district STRING,
    crop_year INT,
    season STRING,
    crop STRING,
    area DOUBLE,
    production DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/agriculture/raw';
```

If your source file has a header, configure Hive to skip it, for example
with the supported header property for your Hive version. For CSV files
with quoted commas, use a CSV SerDe rather than a basic delimiter table.

For a robust project, place the normalized crop data in its own HDFS
directory so that Hive doesn't accidentally read unrelated files.

## 9.4 Run useful queries

Total production by crop:

``` sql
SELECT crop, SUM(production) AS total_production
FROM crop_production
GROUP BY crop
ORDER BY total_production DESC;
```

Production by state:

``` sql
SELECT state, SUM(production) AS total_production
FROM crop_production
GROUP BY state
ORDER BY total_production DESC;
```

Production by year:

``` sql
SELECT crop_year, SUM(production) AS total_production
FROM crop_production
GROUP BY crop_year
ORDER BY crop_year;
```

Average area by crop:

``` sql
SELECT crop, AVG(area) AS average_area
FROM crop_production
GROUP BY crop;
```

Save these queries in `src/hive/analysis.sql`.

**Evidence to capture:** successful query execution and result rows. If
Hive does not become operational within your time budget, record the
issue accurately and continue with the working PySpark outputs.

------------------------------------------------------------------------

# 10. Optional: Add rainfall and temperature

This is an enhancement, not a requirement for the minimum working
project.

## 10.1 Get weather data

Choose historical rainfall or temperature data with a clear location and
time field. Record the source, download date, units, and geographic
level.

## 10.2 Normalize the join keys

Before joining, standardize: - State and district names - Year or date
format - Rainfall units (for example, millimeters) - Temperature units
(for example, degrees Celsius)

A district-level crop dataset cannot be reliably joined to a state-level
weather dataset without an explicit aggregation strategy.

## 10.3 Join in PySpark

After loading both datasets and checking their schemas, join on the
matching region and year fields. For example:

``` python
joined = crop_df.join(
    weather_df,
    on=["State", "Year"],
    how="inner"
)
```

Use this only if those columns genuinely represent the same state and
year in both datasets.

You can then calculate correlations or summarize production and rainfall
by region and year. Explain missing records and limitations in the
report.

------------------------------------------------------------------------

# 11. Create charts using R

## 11.1 Export analysis results

Use the PySpark output folders or Hive query results. Copy the relevant
CSV part files to your local `output` folder. For example:

``` bash
hdfs dfs -get /agriculture/processed/crop_totals/part-* output/
```

Rename the downloaded file to `crop_totals.csv` if needed.

## 11.2 Create an R script

Create `src/r/visualize.R`:

``` r
crop_data <- read.csv("output/crop_totals.csv")

# Show the top 10 crops by production
crop_data <- crop_data[
  order(-crop_data$Total_Production),
]

top_crops <- head(crop_data, 10)

barplot(
  top_crops$Total_Production,
  names.arg = top_crops$Crop,
  las = 2,
  main = "Top 10 Crops by Production",
  xlab = "Crop",
  ylab = "Total Production"
)

year_data <- read.csv("output/yearly_production.csv")
year_data <- year_data[order(year_data$Crop_Year), ]

plot(
  year_data$Crop_Year,
  year_data$Total_Production,
  type = "b",
  main = "Agricultural Production by Year",
  xlab = "Year",
  ylab = "Total Production"
)
```

Run:

``` bash
Rscript src/r/visualize.R
```

If your R environment is not configured to display plots, save them
using `png()` and `dev.off()` around each chart.

**Milestone:** You have visual output generated from processed
agricultural data.

------------------------------------------------------------------------

# 12. Validate the pipeline

Do not rely only on successful command execution. Check that the results
make sense.

## 12.1 Data checks

-   Record the original row count.
-   Check missing crop names and numeric values.
-   Check for negative area or production values.
-   Confirm the production units.
-   Confirm the year range and regions covered.

## 12.2 Processing checks

-   Run a small sample through the mapper and reducer locally.
-   Compare one or two crop totals with a manual calculation.
-   Confirm PySpark's totals agree with the MapReduce results for the
    same input and grouping.
-   Check that the Hive query and PySpark totals agree when both use the
    same cleaned dataset and filters.

## 12.3 Output checks

-   Confirm HDFS contains raw and processed directories.
-   Confirm the result files are not empty.
-   Confirm R reads the exported files and generates charts.
-   Keep screenshots of successful commands and outputs.

------------------------------------------------------------------------

# 13. Suggested two-day schedule

## Day 1 --- Get the core pipeline working

  -----------------------------------------------------------------------
  Time block              Task                    Completion target
  ----------------------- ----------------------- -----------------------
  First 1--2 hours        Download and inspect    CSV and data dictionary
                          crop dataset            

  Next 1--2 hours         Verify Java and         NameNode and DataNode
                          configure Hadoop        running

  Next hour               Upload data to HDFS     HDFS listing shows
                                                  input

  Next 2--3 hours         Implement Hadoop        Crop totals visible
                          Streaming job           

  Remaining time          Implement PySpark       At least two analysis
                          analysis                outputs
  -----------------------------------------------------------------------

## Day 2 --- Query, visualize, and document

  -----------------------------------------------------------------------
  Time block              Task                    Completion target
  ----------------------- ----------------------- -----------------------
  First 2--3 hours        Configure Hive          Database and working
                                                  queries

  Next 1--2 hours         Export results and      At least two charts
                          create R charts         

  Next 2 hours            Validate and capture    Evidence folder
                          screenshots             complete

  Final hours             Write report and        Submission ready
                          prepare explanation     
  -----------------------------------------------------------------------

If installation or compatibility problems consume time, prioritize HDFS,
one MapReduce job, and one PySpark job. Do not spend the entire deadline
trying to install an optional component.

------------------------------------------------------------------------

# 14. Final project report structure

Use this outline for your submission report:

1.  **Title page** --- project title, student details, course, and
    submission date.
2.  **Abstract** --- brief summary of the project and its purpose.
3.  **Introduction** --- background on agricultural data and Big Data.
4.  **Problem statement** --- why processing large agricultural datasets
    is useful.
5.  **Objectives** --- what the system is designed to accomplish.
6.  **Tools and technologies** --- Hadoop, HDFS, MapReduce, Hive,
    PySpark, and R.
7.  **System architecture** --- diagram and explanation of the data
    flow.
8.  **Dataset description** --- source, fields, units, years, and
    limitations.
9.  **Implementation** --- setup, configuration, commands, and code.
10. **Results** --- MapReduce output, Hive query results, Spark tables,
    and charts.
11. **Discussion** --- what the analysis shows and what it cannot
    establish.
12. **Challenges and solutions** --- installation, compatibility, data
    cleaning, and integration.
13. **Conclusion and future scope** --- summary and possible extensions.
14. **References** --- dataset and software documentation links.

------------------------------------------------------------------------

# 15. Viva / presentation preparation

Be ready to explain these questions in your own words:

**What is Hadoop?**\
A framework for distributed storage and processing of large datasets.

**What is HDFS?**\
A distributed file system that stores files as blocks across DataNodes,
while the NameNode manages filesystem metadata.

**What is MapReduce?**\
A processing model with map, shuffle/sort, and reduce stages for
parallel data processing.

**What is YARN?**\
Hadoop's resource-management and job-scheduling layer.

**What is Hive?**\
A data warehouse tool that lets users query data with SQL-like
statements.

**What is PySpark?**\
Python's interface to Apache Spark for distributed data processing and
analytics.

**Why use both MapReduce and Spark?**\
They are different processing approaches. MapReduce demonstrates
Hadoop's batch-processing model, while Spark offers a convenient API for
interactive transformations and analysis. A real deployment would choose
engines based on workload and requirements.

**What is the role of R?**\
R is used here to visualize processed results and create statistical
charts.

**Is your project real-time?**\
No. This implementation is a historical batch analytics pipeline.

**Can this project predict crop yield?**\
Not in its current form. Prediction would require a separate model,
suitable training data, evaluation, and validation.

------------------------------------------------------------------------

# 16. Final completion checklist

-   [ ] Dataset downloaded and source recorded
-   [ ] Dataset fields and units documented
-   [ ] Java and Hadoop versions verified
-   [ ] HDFS configured and running
-   [ ] Dataset uploaded to HDFS
-   [ ] MapReduce job completed successfully
-   [ ] PySpark reads and processes the dataset
-   [ ] Hive database/table created, if Hive setup succeeds
-   [ ] At least two Hive queries executed
-   [ ] Analysis results exported
-   [ ] At least two R charts generated
-   [ ] Results cross-checked
-   [ ] Screenshots captured
-   [ ] Report completed
-   [ ] Project limitations documented
-   [ ] Viva explanation practiced

------------------------------------------------------------------------

# 17. Definition of done

The minimum project is complete when you can demonstrate this sequence:

1.  Show the agricultural CSV and explain its fields.
2.  Show Hadoop processes and the HDFS directory.
3.  Show the dataset stored in HDFS.
4.  Run or show the completed MapReduce aggregation.
5.  Run the PySpark analysis and show its output.
6.  Show working Hive queries if Hive is part of the completed
    implementation.
7.  Show R charts generated from the analysis results.
8.  Explain the findings, data limitations, and role of each technology.

A smaller, reproducible pipeline is preferable to a larger project with
unverified components. Clearly distinguish implemented features from
planned extensions in your final report.
