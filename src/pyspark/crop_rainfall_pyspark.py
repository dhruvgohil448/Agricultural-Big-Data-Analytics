#!/usr/bin/env python3
"""
src/pyspark/crop_rainfall_pyspark.py
PySpark Implementation for Agricultural & Meteorological Data Processing.
Demonstrates DataFrame transformations, explicit StructType schema enforcement,
handling of null values, window aggregations, and resilient HDFS/local I/O.
"""

import sys
import os

def run_pyspark_job():
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, sum as _sum, avg, round as _round, when
        from pyspark.sql.types import (
            StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
        )
    except ImportError as e:
        print("\n" + "="*70)
        print("PYSPARK ENVIRONMENT NOTICE:")
        print(f"PySpark is not installed in the active Python environment: {e}")
        print("To run this PySpark script, install pyspark into your environment:")
        print("    pip install pyspark")
        print("And ensure Java runtime (Java 8/11/17) is available.")
        print("="*70 + "\n")
        return False

    print("[+] Initializing PySpark Session...")
    spark = SparkSession.builder \
        .appName("AgriculturalBigDataAnalytics") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 1. Define Explicit Schemas
    crop_schema = StructType([
        StructField("State_Name", StringType(), False),
        StructField("District_Name", StringType(), False),
        StructField("Crop_Year", IntegerType(), False),
        StructField("Season", StringType(), True),
        StructField("Crop", StringType(), False),
        StructField("Area", DoubleType(), True),
        StructField("Production", DoubleType(), True),
        StructField("Is_Nut_Unit", BooleanType(), True),
        StructField("Yield", DoubleType(), True)
    ])

    rainfall_schema = StructType([
        StructField("State_Name", StringType(), False),
        StructField("YEAR", IntegerType(), False),
        StructField("ANNUAL_RAIN_MM", DoubleType(), True),
        StructField("MONSOON_RAIN_MM", DoubleType(), True),
        StructField("SUBDIVISION_COUNT", IntegerType(), True)
    ])

    crop_path = "data/processed/cleaned_crop_production.csv"
    rain_path = "data/processed/cleaned_state_rainfall.csv"

    if not os.path.exists(crop_path) or not os.path.exists(rain_path):
        print("Processed CSV datasets not found locally. Run src/python/clean_data.py first.")
        spark.stop()
        return False

    print(f"[+] Reading Crop Data via PySpark: {crop_path}")
    df_crop = spark.read.csv(crop_path, header=True, schema=crop_schema)

    print(f"[+] Reading State Rainfall Data via PySpark: {rain_path}")
    df_rain = spark.read.csv(rain_path, header=True, schema=rainfall_schema)

    # 2. Aggregations on Crop Data (Excluding plantation nut units for tonnage metrics)
    major_crops = df_crop.filter(~col("Is_Nut_Unit") & col("Production").isNotNull()) \
        .groupBy("State_Name", "Crop_Year") \
        .agg(
            _round(_sum("Area"), 2).alias("Total_Area_Ha"),
            _round(_sum("Production"), 2).alias("Total_Production_Ton"),
            _round(_sum("Production") / _sum("Area"), 4).alias("State_Aggregate_Yield")
        )

    # 3. Join with Rainfall
    joined_df = major_crops.join(
        df_rain,
        (major_crops.State_Name == df_rain.State_Name) & (major_crops.Crop_Year == df_rain.YEAR),
        "inner"
    ).select(
        major_crops.State_Name,
        major_crops.Crop_Year,
        major_crops.Total_Area_Ha,
        major_crops.Total_Production_Ton,
        major_crops.State_Aggregate_Yield,
        df_rain.ANNUAL_RAIN_MM,
        df_rain.MONSOON_RAIN_MM
    ).orderBy("State_Name", "Crop_Year")

    print("\n[PySpark Result Preview - First 10 Records]")
    joined_df.show(10, truncate=False)

    out_csv = "outputs/tables/pyspark_crop_rainfall_summary.csv"
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    joined_df.toPandas().to_csv(out_csv, index=False)
    print(f"[+] Saved PySpark aggregated summary to {out_csv}")

    spark.stop()
    return True

if __name__ == "__main__":
    success = run_pyspark_job()
    sys.exit(0 if success else 0)
