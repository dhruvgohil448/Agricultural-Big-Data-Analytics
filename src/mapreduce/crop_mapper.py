#!/usr/bin/env python3
"""
src/mapreduce/crop_mapper.py
MapReduce Mapper for Agricultural Crop Production.
Input: Comma-separated records:
       State_Name, District_Name, Crop_Year, Season, Crop, Area, Production
Output: Tab-delimited key-value pairs with composite key:
       Key:   State_Name##Crop##Crop_Year
       Value: Area\tProduction
"""

import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if not row:
            continue
        # Skip header row
        if len(row) >= 7 and row[0].strip().lower() in ["state_name", "state"]:
            continue

        try:
            state = row[0].strip().title()
            crop_year = row[2].strip()
            crop = row[4].strip()
            area_str = row[5].strip()
            prod_str = row[6].strip() if len(row) > 6 else ""

            # Validate numeric values
            area = float(area_str) if area_str else 0.0
            prod = float(prod_str) if prod_str and prod_str.lower() != "nan" else 0.0

            if not state or not crop or not crop_year:
                continue

            composite_key = f"{state}##{crop}##{crop_year}"
            print(f"{composite_key}\t{area:.2f}\t{prod:.2f}")

        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()
