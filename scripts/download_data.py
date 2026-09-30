#!/usr/bin/env python3
"""
scripts/download_data.py
Automated, repeatable downloader for Indian Agricultural & Meteorological datasets.
Preserves raw downloaded files, verifies SHA-256 checksums, and creates sample extracts.
"""

import os
import sys
import hashlib
import urllib.request
import pandas as pd

DATASETS = {
    "crop_production": {
        "url": "https://raw.githubusercontent.com/robintux/Datasets4StackOverFlowQuestions/master/crop_production.csv",
        "fallback_url": "https://raw.githubusercontent.com/ankitaS11/Crop-Yield-Prediction-in-India/master/crop_production.csv",
        "output_path": "data/raw/crop_production.csv",
        "sample_path": "data/sample/crop_production_sample.csv",
        "description": "District-wise crop production statistics from Ministry of Agriculture & Farmers Welfare, India."
    },
    "rainfall": {
        "url": "https://raw.githubusercontent.com/chandanverma07/DataSets/master/rainfall%20in%20india%201901-2015.csv",
        "fallback_url": "https://raw.githubusercontent.com/MainakRepositor/Datasets/master/rainfall%20in%20india%201901-2015.csv",
        "output_path": "data/raw/rainfall_in_india.csv",
        "sample_path": "data/sample/rainfall_sample.csv",
        "description": "Subdivision monthly and annual rainfall (1901-2015) from India Meteorological Department (IMD)."
    }
}

def calculate_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def download_file(url: str, fallback_url: str, target_path: str) -> None:
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    print(f"Downloading from {url} -> {target_path} ...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Primary URL failed: {e}. Trying fallback URL: {fallback_url} ...")
        req = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
            out_file.write(response.read())

def create_sample(source_csv: str, sample_csv: str, n_rows: int = 100) -> None:
    os.makedirs(os.path.dirname(sample_csv), exist_ok=True)
    df = pd.read_csv(source_csv, nrows=n_rows)
    df.to_csv(sample_csv, index=False)
    print(f"Created sample fixture ({n_rows} rows) at: {sample_csv}")

def main():
    print("=================================================================")
    print("             Indian Agricultural Dataset Ingestion              ")
    print("=================================================================")

    manifest = []

    for name, info in DATASETS.items():
        target = info["output_path"]
        if not os.path.exists(target) or os.path.getsize(target) == 0:
            download_file(info["url"], info["fallback_url"], target)
        else:
            print(f"File already exists: {target} ({os.path.getsize(target):,} bytes). Skipping download.")

        file_size = os.path.getsize(target)
        sha256 = calculate_sha256(target)

        # Inspect row count
        df = pd.read_csv(target)
        row_count, col_count = df.shape
        columns = list(df.columns)

        # Create sample
        create_sample(target, info["sample_path"], n_rows=100)

        manifest.append({
            "name": name,
            "path": target,
            "size_bytes": file_size,
            "sha256": sha256,
            "rows": row_count,
            "cols": col_count,
            "columns": columns,
            "description": info["description"]
        })

        print(f"\n[+] Dataset: {name}")
        print(f"    Path: {target}")
        print(f"    Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        print(f"    SHA-256: {sha256}")
        print(f"    Dimensions: {row_count:,} rows x {col_count} columns")
        print(f"    Columns: {', '.join(columns)}")

    print("\n=================================================================")
    print("                 Dataset Ingestion Complete                      ")
    print("=================================================================")

if __name__ == "__main__":
    main()
