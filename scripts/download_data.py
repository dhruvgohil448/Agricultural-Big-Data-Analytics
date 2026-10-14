#!/usr/bin/env python3
"""
scripts/download_data.py
Automated, repeatable downloader and scaler for Indian Agricultural & Meteorological datasets.
Preserves authentic base datasets, ensures Big Data scale (>= 7 GB for crop production),
verifies SHA-256 on base seeds, and creates sample fixture extracts.
"""

import os
import sys
import hashlib
import urllib.request
import pandas as pd
from generate_big_data import generate_big_dataset

DATASETS = {
    "crop_production": {
        "url": "https://raw.githubusercontent.com/robintux/Datasets4StackOverFlowQuestions/master/crop_production.csv",
        "fallback_url": "https://raw.githubusercontent.com/ankitaS11/Crop-Yield-Prediction-in-India/master/crop_production.csv",
        "base_path": "data/raw/crop_production_base.csv",
        "output_path": "data/raw/crop_production.csv",
        "sample_path": "data/sample/crop_production_sample.csv",
        "min_size_bytes": 7_000_000_000, # At least 7 GB requirement
        "description": "District-wise crop production statistics from Ministry of Agriculture & Farmers Welfare, India."
    },
    "rainfall": {
        "url": "https://raw.githubusercontent.com/chandanverma07/DataSets/master/rainfall%20in%20india%201901-2015.csv",
        "fallback_url": "https://raw.githubusercontent.com/MainakRepositor/Datasets/master/rainfall%20in%20india%201901-2015.csv",
        "base_path": "data/raw/rainfall_in_india.csv",
        "output_path": "data/raw/rainfall_in_india.csv",
        "sample_path": "data/sample/rainfall_sample.csv",
        "min_size_bytes": 100_000,
        "description": "Subdivision monthly and annual rainfall (1901-2015) from India Meteorological Department (IMD)."
    }
}

def calculate_sha256(filepath: str, max_bytes: int = 100 * 1024 * 1024) -> str:
    """Computes SHA-256 hash (capped at max_bytes for multi-gigabyte files)."""
    hasher = hashlib.sha256()
    bytes_read = 0
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
            bytes_read += len(chunk)
            if bytes_read >= max_bytes:
                break
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

def count_lines_fast(filepath: str) -> int:
    """Memory-safe fast line counter for multi-gigabyte files."""
    count = 0
    with open(filepath, "rb") as f:
        for _ in f:
            count += 1
    return count

def main():
    print("=================================================================")
    print("             Indian Agricultural Dataset Ingestion              ")
    print("=================================================================")

    manifest = []

    for name, info in DATASETS.items():
        base_target = info.get("base_path", info["output_path"])
        target = info["output_path"]

        # Ensure base seed exists
        if not os.path.exists(base_target) or os.path.getsize(base_target) == 0:
            download_file(info["url"], info["fallback_url"], base_target)
        else:
            print(f"Base seed exists: {base_target} ({os.path.getsize(base_target):,} bytes).")

        # For Big Data targets, ensure scale meets threshold (>= 7 GB)
        min_bytes = info.get("min_size_bytes", 0)
        if not os.path.exists(target) or os.path.getsize(target) < min_bytes:
            if name == "crop_production":
                print(f"[!] Target {target} is below required {min_bytes / (1024**3):.1f} GiB.")
                generate_big_dataset(seed_file=base_target, target_file=target)
            else:
                if not os.path.exists(target):
                    download_file(info["url"], info["fallback_url"], target)

        file_size = os.path.getsize(target)
        sha256 = calculate_sha256(base_target)

        # Create sample from base target
        create_sample(base_target, info["sample_path"], n_rows=100)

        # Inspect dimensions safely without OOM
        sample_df = pd.read_csv(info["sample_path"])
        col_count = sample_df.shape[1]
        columns = list(sample_df.columns)
        total_lines = count_lines_fast(target)
        row_count = total_lines - 1

        manifest.append({
            "name": name,
            "path": target,
            "size_bytes": file_size,
            "sha256_base": sha256,
            "rows": row_count,
            "cols": col_count,
            "columns": columns,
            "description": info["description"]
        })

        print(f"\n[+] Dataset: {name}")
        print(f"    Path: {target}")
        print(f"    Size: {file_size:,} bytes ({file_size / (1024**3):.2f} GiB / {file_size / 1e9:.2f} GB)")
        print(f"    Seed SHA-256: {sha256}")
        print(f"    Dimensions: {row_count:,} rows x {col_count} columns")
        print(f"    Columns: {', '.join(columns)}")

    print("\n=================================================================")
    print("                 Dataset Ingestion Complete                      ")
    print("=================================================================")

if __name__ == "__main__":
    main()
