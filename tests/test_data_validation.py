"""
tests/test_data_validation.py
Automated unit tests for data validation, schema enforcement, and missing value checks.
"""

import os
import pandas as pd
import pytest

RAW_CROP = "data/raw/crop_production.csv"
RAW_RAIN = "data/raw/rainfall_in_india.csv"
PROC_CROP = "data/processed/cleaned_crop_production.csv"
PROC_RAIN = "data/processed/cleaned_rainfall.csv"

def test_raw_files_exist_and_non_empty():
    assert os.path.exists(RAW_CROP), f"{RAW_CROP} missing"
    assert os.path.getsize(RAW_CROP) >= 7_000_000_000, f"Raw crop dataset must be >= 7 GB (found {os.path.getsize(RAW_CROP) / (1024**3):.2f} GiB)"

    assert os.path.exists(PROC_CROP), f"{PROC_CROP} missing"
    assert os.path.getsize(PROC_CROP) >= 7_000_000_000, f"Cleaned crop dataset must be >= 7 GB (found {os.path.getsize(PROC_CROP) / (1024**3):.2f} GiB)"

    assert os.path.exists(RAW_RAIN), f"{RAW_RAIN} missing"
    assert os.path.getsize(RAW_RAIN) > 100_000, "Raw rainfall dataset is smaller than expected"

def test_crop_schema_and_columns():
    df = pd.read_csv(RAW_CROP, nrows=50)
    expected_cols = ["State_Name", "District_Name", "Crop_Year", "Season", "Crop", "Area", "Production"]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col} in crop dataset"

def test_rainfall_schema_and_columns():
    df = pd.read_csv(RAW_RAIN, nrows=50)
    expected_cols = ["SUBDIVISION", "YEAR", "ANNUAL", "Jun-Sep"]
    for col in expected_cols:
        assert col in df.columns, f"Missing column {col} in rainfall dataset"

def test_cleaned_crop_yield_calculation():
    assert os.path.exists(PROC_CROP), f"{PROC_CROP} missing"
    df = pd.read_csv(PROC_CROP, nrows=500)
    assert "Yield" in df.columns
    assert "Is_Nut_Unit" in df.columns

    # Verify Yield equals Production / Area where both exist
    valid_rows = df[(df["Area"] > 0) & (df["Production"].notnull())]
    for _, row in valid_rows.head(50).iterrows():
        expected_yield = row["Production"] / row["Area"]
        assert pytest.approx(row["Yield"], rel=1e-3) == expected_yield

def test_cleaned_crop_whitespace_sanitized():
    df = pd.read_csv(PROC_CROP, nrows=500)
    for col in ["State_Name", "District_Name", "Season", "Crop"]:
        for val in df[col].dropna():
            assert val == val.strip(), f"Unstripped whitespace found in {col}: '{val}'"
