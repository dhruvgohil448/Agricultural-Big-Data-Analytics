#!/usr/bin/env bash
# ==============================================================================
# Agricultural Big Data Analytics System - Environment Diagnostic Script
# Verifies system architecture, Java, Hadoop, HDFS daemons, Python, R, and disk.
# ==============================================================================

set -o pipefail

echo "================================================================="
echo "       Agricultural Big Data Analytics: Environment Check         "
echo "================================================================="

echo ""
echo "[1] System Architecture & OS Version:"
uname -m
sw_vers

echo ""
echo "[2] Java Environment:"
if command -v java >/dev/null 2>&1; then
    java -version
else
    echo "ERROR: Java not found in PATH."
fi

echo ""
echo "[3] Hadoop & HDFS Configuration:"
if command -v hadoop >/dev/null 2>&1; then
    hadoop version | head -n 3
    echo "fs.defaultFS: $(hdfs getconf -confKey fs.defaultFS 2>/dev/null || echo 'Unknown')"
else
    echo "ERROR: Hadoop not found in PATH."
fi

echo ""
echo "[4] Hadoop Daemons (jps):"
jps -l

echo ""
echo "[5] Python Environment:"
if [ -d ".venv" ]; then
    echo "Virtual environment detected at .venv"
    .venv/bin/python --version
    .venv/bin/pip --version
else
    python3 --version
fi

echo ""
echo "[6] R Environment:"
if command -v R >/dev/null 2>&1; then
    R --version | head -n 2
else
    echo "NOTICE: R is not installed in system PATH."
fi

echo ""
echo "[7] Git Version:"
git --version 2>/dev/null || echo "Git not found."

echo ""
echo "[8] Disk Space Available:"
df -h .

echo ""
echo "[9] Testing HDFS Connectivity:"
if command -v hdfs >/dev/null 2>&1; then
    hdfs dfs -ls / 2>&1 || echo "WARNING: HDFS root directory query failed or socket inaccessible."
else
    echo "Skipping HDFS test: hdfs command not found."
fi

echo ""
echo "================================================================="
echo "                   Environment Check Complete                    "
echo "================================================================="
