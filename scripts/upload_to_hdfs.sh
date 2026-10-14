#!/usr/bin/env bash
# ==============================================================================
# scripts/upload_to_hdfs.sh
# Idempotent HDFS setup and upload script for Agricultural Big Data Analytics.
# Supports multi-gigabyte dataset ingestion and skips redundant uploads.
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
    if hdfs dfs -test -e "$CROP_INPUT/crop_production.csv" 2>/dev/null; then
        echo "Crop dataset already exists in HDFS ($CROP_INPUT/crop_production.csv). Skipping re-upload."
    else
        echo "Uploading data/raw/crop_production.csv -> $CROP_INPUT/ ..."
        hdfs dfs -put -f data/raw/crop_production.csv "$CROP_INPUT/"
    fi
fi

if [ -f "data/raw/crop_production_base.csv" ]; then
    if ! hdfs dfs -test -e "$CROP_INPUT/crop_production_base.csv" 2>/dev/null; then
        echo "Uploading data/raw/crop_production_base.csv -> $CROP_INPUT/ ..."
        hdfs dfs -put -f data/raw/crop_production_base.csv "$CROP_INPUT/"
    fi
fi

if [ -f "data/raw/rainfall_in_india.csv" ]; then
    if hdfs dfs -test -e "$RAIN_INPUT/rainfall_in_india.csv" 2>/dev/null; then
        echo "Rainfall dataset already exists in HDFS ($RAIN_INPUT/rainfall_in_india.csv). Skipping re-upload."
    else
        echo "Uploading data/raw/rainfall_in_india.csv -> $RAIN_INPUT/ ..."
        hdfs dfs -put -f data/raw/rainfall_in_india.csv "$RAIN_INPUT/"
    fi
fi

echo "[4] Uploading processed datasets to HDFS..."
if [ -f "data/processed/cleaned_crop_production.csv" ]; then
    if hdfs dfs -test -e "$PROCESSED_DIR/cleaned_crop_production.csv" 2>/dev/null; then
        echo "Cleaned crop dataset already exists in HDFS ($PROCESSED_DIR/cleaned_crop_production.csv). Skipping re-upload."
    else
        echo "Uploading data/processed/cleaned_crop_production.csv -> $PROCESSED_DIR/ ..."
        hdfs dfs -put -f data/processed/cleaned_crop_production.csv "$PROCESSED_DIR/"
    fi
fi

if [ -f "data/processed/cleaned_rainfall.csv" ]; then
    if hdfs dfs -test -e "$PROCESSED_DIR/cleaned_rainfall.csv" 2>/dev/null; then
        echo "Cleaned rainfall dataset already exists in HDFS ($PROCESSED_DIR/cleaned_rainfall.csv). Skipping re-upload."
    else
        echo "Uploading data/processed/cleaned_rainfall.csv -> $PROCESSED_DIR/ ..."
        hdfs dfs -put -f data/processed/cleaned_rainfall.csv "$PROCESSED_DIR/"
    fi
fi

echo ""
echo "[5] Verifying HDFS hierarchy and storage usage:"
echo "--- Recursive listing ($HDFS_ROOT) ---"
hdfs dfs -ls -h "$HDFS_ROOT"
hdfs dfs -ls -h "$CROP_INPUT"
hdfs dfs -ls -h "$PROCESSED_DIR"

echo ""
echo "--- Disk usage breakdown ($HDFS_ROOT) ---"
hdfs dfs -du -h "$HDFS_ROOT"

echo ""
echo "================================================================="
echo "                  HDFS Ingestion Complete                        "
echo "================================================================="
