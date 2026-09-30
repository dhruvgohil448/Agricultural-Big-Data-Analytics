#!/usr/bin/env bash
# ==============================================================================
# scripts/run_pipeline.sh
# End-to-end reproducible pipeline execution script.
# Executes: Ingestion -> Quality Check -> HDFS Ingest -> MapReduce -> EDA -> Reports -> Tests.
# ==============================================================================

set -euo pipefail

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
PIPELINE_LOG="$LOG_DIR/pipeline_$(date +%Y%m%d_%H%M%S).log"

exec > >(tee -a "$PIPELINE_LOG") 2>&1

echo "================================================================="
echo "   Agricultural Big Data Analytics: Complete End-to-End Pipeline "
echo "================================================================="
echo "Start Time: $(date)"
echo "Logging to: $PIPELINE_LOG"

PYTHON=".venv/bin/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON="python3"
fi

echo ""
echo "[Step 1/8] Verifying Environment & Cluster Health..."
./scripts/check_environment.sh

echo ""
echo "[Step 2/8] Ingesting Public Datasets..."
$PYTHON scripts/download_data.py

echo ""
echo "[Step 3/8] Performing Data Validation & Quality Audit..."
$PYTHON scripts/validate_data.py

echo ""
echo "[Step 4/8] Cleaning & Normalizing Datasets..."
$PYTHON src/python/clean_data.py

echo ""
echo "[Step 5/8] Ingesting to HDFS Distributed File System..."
./scripts/upload_to_hdfs.sh

echo ""
echo "[Step 6/8] Executing Distributed Hadoop MapReduce Jobs on HDFS..."
./scripts/run_mapreduce.sh

echo ""
echo "[Step 7/8] Running Exploratory Analytics & Generating Publication Visualizations..."
$PYTHON src/python/exploratory_analysis.py

echo ""
echo "[Step 8/8] Generating Academic & HTML Reports..."
$PYTHON src/python/generate_report.py

echo ""
echo "[Step 9/8] Executing Automated Test Suite..."
.venv/bin/pytest tests/ -v

echo ""
echo "================================================================="
echo "              Pipeline Execution Successfully Completed          "
echo "================================================================="
echo "End Time: $(date)"
echo "Log File: $PIPELINE_LOG"
