#!/usr/bin/env bash
# ==============================================================================
# scripts/upload_to_hdfs.sh
# Idempotent HDFS setup and upload script for Agricultural Big Data Analytics.
# ==============================================================================

set -euo pipefail

HDFS_ROOT="/user/dhruvgohil/agriculture"
CROP_INPUT="$HDFS_ROOT/input/crop_production"
RAIN_INPUT="$HDFS_ROOT/input/rainfall"
SOIL_INPUT="$HDFS_ROOT/input/soil"
PROCESSED_DIR="$HDFS_ROOT/processed"
OUTPUT_DIR="$HDFS_ROOT/output"
REPORTS_DIR="$HDFS_ROOT/reports"

echo "================================================================="
echo "                HDFS Ingestion & Directory Setup                 "
echo "================================================================="

echo "[1] Checking HDFS connectivity..."
hdfs dfs -test -d /user || { echo "ERROR: Cannot reach HDFS root directory."; exit 1; }

echo "[2] Creating project directories idempotently..."
hdfs dfs -mkdir -p "$CROP_INPUT"
hdfs dfs -mkdir -p "$RAIN_INPUT"
hdfs dfs -mkdir -p "$SOIL_INPUT"
hdfs dfs -mkdir -p "$PROCESSED_DIR"
hdfs dfs -mkdir -p "$OUTPUT_DIR"
hdfs dfs -mkdir -p "$REPORTS_DIR"

echo "[3] Uploading raw datasets to HDFS..."
if [ -f "data/raw/crop_production.csv" ]; then
    echo "Uploading data/raw/crop_production.csv -> $CROP_INPUT/ ..."
    hdfs dfs -put -f data/raw/crop_production.csv "$CROP_INPUT/"
else
    echo "WARNING: data/raw/crop_production.csv not found locally."
fi

if [ -f "data/raw/rainfall_in_india.csv" ]; then
    echo "Uploading data/raw/rainfall_in_india.csv -> $RAIN_INPUT/ ..."
    hdfs dfs -put -f data/raw/rainfall_in_india.csv "$RAIN_INPUT/"
else
    echo "WARNING: data/raw/rainfall_in_india.csv not found locally."
fi

echo "[4] Uploading processed datasets to HDFS..."
if [ -f "data/processed/cleaned_crop_production.csv" ]; then
    echo "Uploading data/processed/cleaned_crop_production.csv -> $PROCESSED_DIR/ ..."
    hdfs dfs -put -f data/processed/cleaned_crop_production.csv "$PROCESSED_DIR/"
fi

if [ -f "data/processed/cleaned_rainfall.csv" ]; then
    echo "Uploading data/processed/cleaned_rainfall.csv -> $PROCESSED_DIR/ ..."
    hdfs dfs -put -f data/processed/cleaned_rainfall.csv "$PROCESSED_DIR/"
fi

echo ""
echo "[5] Verifying HDFS hierarchy and storage usage:"
echo "--- Recursive listing ($HDFS_ROOT) ---"
hdfs dfs -ls -R "$HDFS_ROOT"

echo ""
echo "--- Disk usage breakdown ($HDFS_ROOT) ---"
hdfs dfs -du -h "$HDFS_ROOT"

echo ""
echo "================================================================="
echo "                  HDFS Ingestion Complete                        "
echo "================================================================="
