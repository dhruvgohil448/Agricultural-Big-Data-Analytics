#!/usr/bin/env python3
"""
src/python/clean_data.py
Cleans and standardizes raw agricultural and meteorological datasets:
- Strips trailing/leading whitespace across categorical features
- Normalizes state and subdivision names
- Handles missing values transparently without silent loss of valid data
- Computes derived yield metrics with unit awareness (Tonnes vs Nuts)
- Generates processed datasets ready for HDFS ingestion and MapReduce processing
"""

import os
import pandas as pd
import numpy as np

RAW_CROP = "data/raw/crop_production.csv"
RAW_RAINFALL = "data/raw/rainfall_in_india.csv"
PROC_DIR = "data/processed"

# Explicit IMD Subdivision to State Name mapping
SUBDIVISION_TO_STATE = {
    "ANDAMAN & NICOBAR ISLANDS": "Andaman and Nicobar Islands",
    "ARUNACHAL PRADESH": "Arunachal Pradesh",
    "ASSAM & MEGHALAYA": "Assam",  # Also covers Meghalaya; explicit in notes
    "NAGA MANI MIZO TRIPURA": "Nagaland", # Grouped NE states
    "SUB HIMALAYAN WEST BENGAL & SIKKIM": "West Bengal",
    "GANGETIC WEST BENGAL": "West Bengal",
    "ORISSA": "Odisha",
    "JHARKHAND": "Jharkhand",
    "BIHAR": "Bihar",
    "EAST UTTAR PRADESH": "Uttar Pradesh",
    "WEST UTTAR PRADESH": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand",
    "HARYANA DELHI & CHANDIGARH": "Haryana",
    "PUNJAB": "Punjab",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "JAMMU & KASHMIR": "Jammu and Kashmir",
    "WEST RAJASTHAN": "Rajasthan",
    "EAST RAJASTHAN": "Rajasthan",
    "WEST MADHYA PRADESH": "Madhya Pradesh",
    "EAST MADHYA PRADESH": "Madhya Pradesh",
    "GUJARAT REGION": "Gujarat",
    "SAURASHTRA & KUTCH": "Gujarat",
    "KONKAN & GOA": "Goa",
    "MADHYA MAHARASHTRA": "Maharashtra",
    "MATATHWADA": "Maharashtra",
    "VIDARBHA": "Maharashtra",
    "CHHATTISGARH": "Chhattisgarh",
    "COASTAL ANDHRA PRADESH": "Andhra Pradesh",
    "TELANGANA": "Telangana",
    "RAYALSEEMA": "Andhra Pradesh",
    "TAMIL NADU": "Tamil Nadu",
    "COASTAL KARNATAKA": "Karnataka",
    "NORTH INTERIOR KARNATAKA": "Karnataka",
    "SOUTH INTERIOR KARNATAKA": "Karnataka",
    "KERALA": "Kerala",
    "LAKSHADWEEP": "Lakshadweep"
}

def clean_crop_data(input_csv, output_csv):
    print(f"\n[+] Cleaning Crop Production: {input_csv} -> {output_csv}")
    df = pd.read_csv(input_csv)
    initial_rows = len(df)

    # 1. Strip whitespace from string columns
    str_cols = ["State_Name", "District_Name", "Season", "Crop"]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # 2. Normalize state names
    df["State_Name"] = df["State_Name"].str.strip().str.title()
    # Normalize Orissa to Odisha
    df["State_Name"] = df["State_Name"].replace({"Orissa": "Odisha"})

    # 3. Numeric conversion and validation
    df["Crop_Year"] = pd.to_numeric(df["Crop_Year"], errors="coerce").fillna(0).astype(int)
    df["Area"] = pd.to_numeric(df["Area"], errors="coerce").fillna(0.0)
    df["Production"] = pd.to_numeric(df["Production"], errors="coerce")

    # 4. Mark unit distinction
    df["Is_Nut_Unit"] = df["Crop"].str.lower().str.contains("coconut")

    # 5. Compute Yield (Tonnes/Ha or Nuts/Ha)
    df["Yield"] = np.where(
        (df["Area"] > 0) & (df["Production"].notnull()),
        df["Production"] / df["Area"],
        np.nan
    )

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"    Processed {initial_rows:,} rows. Saved to {output_csv}")
    print(f"    Missing production records retained with NaN: {df['Production'].isnull().sum():,}")
    return df

def clean_rainfall_data(input_csv, output_csv, state_agg_csv):
    print(f"\n[+] Cleaning Rainfall: {input_csv} -> {output_csv}")
    df = pd.read_csv(input_csv)
    initial_rows = len(df)

    # 1. Strip whitespace
    df["SUBDIVISION"] = df["SUBDIVISION"].astype(str).str.strip().str.upper()

    # 2. Impute missing ANNUAL if 12 months are present
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    for m in months:
        df[m] = pd.to_numeric(df[m], errors="coerce")

    monthly_sum = df[months].sum(axis=1, skipna=False)
    df["ANNUAL"] = df["ANNUAL"].fillna(monthly_sum)

    # 3. Map to state
    df["State_Name"] = df["SUBDIVISION"].map(SUBDIVISION_TO_STATE).fillna(df["SUBDIVISION"].str.title())

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"    Processed {initial_rows:,} rows. Saved subdivision data to {output_csv}")

    # 4. Generate state-level aggregated annual & monsoon rainfall
    state_df = df.groupby(["State_Name", "YEAR"]).agg(
        ANNUAL_RAIN_MM=("ANNUAL", "mean"),
        MONSOON_RAIN_MM=("Jun-Sep", "mean"),
        SUBDIVISION_COUNT=("SUBDIVISION", "count")
    ).reset_index()

    state_df["ANNUAL_RAIN_MM"] = state_df["ANNUAL_RAIN_MM"].round(2)
    state_df["MONSOON_RAIN_MM"] = state_df["MONSOON_RAIN_MM"].round(2)

    state_df.to_csv(state_agg_csv, index=False)
    print(f"    Generated {len(state_df):,} state-year rainfall records at {state_agg_csv}")
    return df, state_df

def main():
    os.makedirs(PROC_DIR, exist_ok=True)
    clean_crop_data(RAW_CROP, os.path.join(PROC_DIR, "cleaned_crop_production.csv"))
    clean_rainfall_data(
        RAW_RAINFALL,
        os.path.join(PROC_DIR, "cleaned_rainfall.csv"),
        os.path.join(PROC_DIR, "cleaned_state_rainfall.csv")
    )
    print("\n[SUCCESS] Data cleaning pipeline completed successfully.")

if __name__ == "__main__":
    main()
