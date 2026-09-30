#!/usr/bin/env python3
"""
src/mapreduce/crop_reducer.py
MapReduce Reducer for Agricultural Crop Production.
Input: Sorted tab-delimited streams from mapper:
       State_Name##Crop##Crop_Year\tArea\tProduction
Output: Tab-delimited aggregated summaries:
       State_Name\tCrop\tCrop_Year\tTotal_Area\tTotal_Production\tMean_Yield\tRecord_Count
"""

import sys

def main():
    current_key = None
    total_area = 0.0
    total_production = 0.0
    record_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        key, area_str, prod_str = parts

        try:
            area = float(area_str)
            prod = float(prod_str)
        except ValueError:
            continue

        if current_key == key:
            total_area += area
            total_production += prod
            record_count += 1
        else:
            if current_key:
                c_state, c_crop, c_year = current_key.split("##")
                mean_yield = (total_production / total_area) if total_area > 0 else 0.0
                print(f"{c_state}\t{c_crop}\t{c_year}\t{total_area:.2f}\t{total_production:.2f}\t{mean_yield:.4f}\t{record_count}")

            current_key = key
            total_area = area
            total_production = prod
            record_count = 1

    # Emit final group
    if current_key:
        c_state, c_crop, c_year = current_key.split("##")
        mean_yield = (total_production / total_area) if total_area > 0 else 0.0
        print(f"{c_state}\t{c_crop}\t{c_year}\t{total_area:.2f}\t{total_production:.2f}\t{mean_yield:.4f}\t{record_count}")

if __name__ == "__main__":
    main()
