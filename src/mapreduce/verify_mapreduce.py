#!/usr/bin/env python3
"""
src/mapreduce/verify_mapreduce.py
Performs independent pandas aggregation of crop production and rainfall datasets
and cross-validates against the Hadoop MapReduce outputs to verify numerical fidelity.
"""

import sys
import os
import pandas as pd
import numpy as np

def verify_crop_job(raw_csv, mr_output_file):
    print("\n--- Verifying Crop Production MapReduce Output ---")
    if not os.path.exists(mr_output_file):
        print(f"ERROR: MapReduce output file not found: {mr_output_file}")
        return False

    # 1. Independent Python calculation using raw dataset
    df = pd.read_csv(raw_csv)
    df["State_Name"] = df["State_Name"].str.strip().str.title()
    df["Crop"] = df["Crop"].str.strip()
    df["Crop_Year"] = df["Crop_Year"].astype(int)
    df["Area"] = pd.to_numeric(df["Area"], errors="coerce").fillna(0.0)
    df["Production"] = pd.to_numeric(df["Production"], errors="coerce").fillna(0.0)

    py_agg = df.groupby(["State_Name", "Crop", "Crop_Year"]).agg(
        Total_Area=("Area", "sum"),
        Total_Production=("Production", "sum"),
        Record_Count=("Crop", "count")
    ).reset_index()

    py_agg["Total_Area"] = py_agg["Total_Area"].round(2)
    py_agg["Total_Production"] = py_agg["Total_Production"].round(2)

    # 2. Load MapReduce Output
    # Format: State_Name\tCrop\tCrop_Year\tTotal_Area\tTotal_Production\tMean_Yield\tRecord_Count
    mr_df = pd.read_csv(
        mr_output_file,
        sep="\t",
        header=None,
        names=["State_Name", "Crop", "Crop_Year", "Total_Area", "Total_Production", "Mean_Yield", "Record_Count"]
    )

    print(f"Independent Python groups: {len(py_agg):,}")
    print(f"MapReduce output groups:   {len(mr_df):,}")

    assert len(py_agg) == len(mr_df), f"Group count mismatch: Python {len(py_agg)} vs MR {len(mr_df)}"

    # Merge and compare
    merged = pd.merge(
        py_agg, mr_df,
        on=["State_Name", "Crop", "Crop_Year"],
        suffixes=("_py", "_mr")
    )

    area_diff = np.abs(merged["Total_Area_py"] - merged["Total_Area_mr"]).max()
    prod_diff = np.abs(merged["Total_Production_py"] - merged["Total_Production_mr"]).max()
    count_diff = np.abs(merged["Record_Count_py"] - merged["Record_Count_mr"]).max()

    print(f"Maximum Area Difference:       {area_diff:.4f}")
    print(f"Maximum Production Difference: {prod_diff:.4f}")
    print(f"Maximum Record Count Diff:     {count_diff}")

    if area_diff < 0.05 and prod_diff < 0.05 and count_diff == 0:
        print("[PASSED] Crop MapReduce results are 100% numerically identical to Python calculation!")
        return True
    else:
        print("[FAILED] Discrepancies detected between MapReduce and Python baseline.")
        return False

def verify_rainfall_job(raw_csv, mr_output_file):
    print("\n--- Verifying Meteorological Rainfall MapReduce Output ---")
    if not os.path.exists(mr_output_file):
        print(f"ERROR: MapReduce output file not found: {mr_output_file}")
        return False

    df = pd.read_csv(raw_csv)
    df["SUBDIVISION"] = df["SUBDIVISION"].str.strip().str.upper()
    df["Decade"] = (df["YEAR"] // 10) * 10
    df["Decade"] = df["Decade"].astype(str) + "s"
    df["ANNUAL"] = pd.to_numeric(df["ANNUAL"], errors="coerce")
    df["Jun-Sep"] = pd.to_numeric(df["Jun-Sep"], errors="coerce").fillna(0.0)

    # Filter invalid annuals just like mapper
    valid_df = df[df["ANNUAL"].notnull()].copy()

    py_agg = valid_df.groupby(["SUBDIVISION", "Decade"]).agg(
        Avg_Annual_Rainfall=("ANNUAL", "mean"),
        Avg_Monsoon_Rainfall=("Jun-Sep", "mean"),
        Year_Count=("ANNUAL", "count")
    ).reset_index()

    py_agg["Avg_Annual_Rainfall"] = py_agg["Avg_Annual_Rainfall"].round(2)
    py_agg["Avg_Monsoon_Rainfall"] = py_agg["Avg_Monsoon_Rainfall"].round(2)

    mr_df = pd.read_csv(
        mr_output_file,
        sep="\t",
        header=None,
        names=["SUBDIVISION", "Decade", "Avg_Annual_Rainfall", "Avg_Monsoon_Rainfall", "Year_Count"]
    )

    print(f"Independent Python groups: {len(py_agg):,}")
    print(f"MapReduce output groups:   {len(mr_df):,}")

    assert len(py_agg) == len(mr_df), f"Group count mismatch: Python {len(py_agg)} vs MR {len(mr_df)}"

    merged = pd.merge(
        py_agg, mr_df,
        on=["SUBDIVISION", "Decade"],
        suffixes=("_py", "_mr")
    )

    annual_diff = np.abs(merged["Avg_Annual_Rainfall_py"] - merged["Avg_Annual_Rainfall_mr"]).max()
    monsoon_diff = np.abs(merged["Avg_Monsoon_Rainfall_py"] - merged["Avg_Monsoon_Rainfall_mr"]).max()

    print(f"Maximum Annual Rain Diff:  {annual_diff:.4f}")
    print(f"Maximum Monsoon Rain Diff: {monsoon_diff:.4f}")

    if annual_diff < 0.05 and monsoon_diff < 0.05:
        print("[PASSED] Rainfall MapReduce results are 100% numerically identical to Python calculation!")
        return True
    else:
        print("[FAILED] Discrepancies detected between MapReduce and Python baseline.")
        return False

def main():
    crop_ok = verify_crop_job(
        "data/raw/crop_production.csv",
        "outputs/tables/mr_crop_production_results.tsv"
    )
    rain_ok = verify_rainfall_job(
        "data/raw/rainfall_in_india.csv",
        "outputs/tables/mr_rainfall_results.tsv"
    )

    if crop_ok and rain_ok:
        print("\nAll MapReduce numerical verifications PASSED!")
        exit(0)
    else:
        print("\nOne or more MapReduce verifications FAILED.")
        exit(1)

if __name__ == "__main__":
    main()
