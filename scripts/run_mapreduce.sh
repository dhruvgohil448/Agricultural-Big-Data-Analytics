#!/usr/bin/env bash
# ==============================================================================
# scripts/run_mapreduce.sh
# Executes Hadoop Streaming MapReduce jobs against HDFS datasets.
# Fetches results from HDFS and triggers independent Python cross-verification.
# ==============================================================================

set -euo pipefail

STREAMING_JAR="/opt/homebrew/Cellar/hadoop/3.5.0/libexec/share/hadoop/tools/lib/hadoop-streaming-3.5.0.jar"
if [ ! -f "$STREAMING_JAR" ]; then
    STREAMING_JAR=$(find /opt/homebrew -name "hadoop-streaming*.jar" 2>/dev/null | head -n 1)
fi

echo "================================================================="
echo "           Hadoop MapReduce Execution on HDFS Cluster            "
echo "================================================================="
echo "Streaming JAR: $STREAMING_JAR"

HDFS_OUTPUT_CROP="/user/dhruvgohil/agriculture/output/mr_crop_production"
HDFS_OUTPUT_RAIN="/user/dhruvgohil/agriculture/output/mr_rainfall"
LOCAL_TABLES="outputs/tables"
mkdir -p "$LOCAL_TABLES"

# ------------------------------------------------------------------------------
# 1. Job 1: Crop Production & Yield Aggregation
# ------------------------------------------------------------------------------
echo ""
echo "[Job 1] Starting MapReduce for Crop Production on HDFS..."
hdfs dfs -rm -r -f "$HDFS_OUTPUT_CROP" 2>/dev/null || true

hadoop jar "$STREAMING_JAR" \
    -D mapreduce.framework.name=local \
    -D mapreduce.job.name="Agri_Crop_Aggregation" \
    -files src/mapreduce/crop_mapper.py,src/mapreduce/crop_reducer.py \
    -mapper "python3 crop_mapper.py" \
    -reducer "python3 crop_reducer.py" \
    -input "/user/dhruvgohil/agriculture/input/crop_production/crop_production.csv" \
    -output "$HDFS_OUTPUT_CROP"

echo "Fetching Crop MapReduce results from HDFS..."
hdfs dfs -cat "$HDFS_OUTPUT_CROP"/part-* > "$LOCAL_TABLES/mr_crop_production_results.tsv"
echo "Crop Results saved to $LOCAL_TABLES/mr_crop_production_results.tsv ($(wc -l < "$LOCAL_TABLES/mr_crop_production_results.tsv" | tr -d ' ') records)"

# ------------------------------------------------------------------------------
# 2. Job 2: Decadal Meteorological Rainfall Aggregation
# ------------------------------------------------------------------------------
echo ""
echo "[Job 2] Starting MapReduce for Rainfall Analysis on HDFS..."
hdfs dfs -rm -r -f "$HDFS_OUTPUT_RAIN" 2>/dev/null || true

hadoop jar "$STREAMING_JAR" \
    -D mapreduce.framework.name=local \
    -D mapreduce.job.name="Agri_Rainfall_Aggregation" \
    -files src/mapreduce/rainfall_mapper.py,src/mapreduce/rainfall_reducer.py \
    -mapper "python3 rainfall_mapper.py" \
    -reducer "python3 rainfall_reducer.py" \
    -input "/user/dhruvgohil/agriculture/input/rainfall/rainfall_in_india.csv" \
    -output "$HDFS_OUTPUT_RAIN"

echo "Fetching Rainfall MapReduce results from HDFS..."
hdfs dfs -cat "$HDFS_OUTPUT_RAIN"/part-* > "$LOCAL_TABLES/mr_rainfall_results.tsv"
echo "Rainfall Results saved to $LOCAL_TABLES/mr_rainfall_results.tsv ($(wc -l < "$LOCAL_TABLES/mr_rainfall_results.tsv" | tr -d ' ') records)"

# ------------------------------------------------------------------------------
# 3. Independent Numerical Cross-Verification
# ------------------------------------------------------------------------------
echo ""
echo "[Validation] Running independent verification against Python pandas baseline..."
./.venv/bin/python src/mapreduce/verify_mapreduce.py

echo ""
echo "================================================================="
echo "             MapReduce Execution & Verification Done             "
echo "================================================================="
