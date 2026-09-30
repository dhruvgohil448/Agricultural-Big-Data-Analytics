#!/usr/bin/env python3
"""
src/mapreduce/rainfall_mapper.py
MapReduce Mapper for Meteorological Rainfall Aggregation.
Input: Comma-separated records:
       SUBDIVISION,YEAR,JAN,...,DEC,ANNUAL,Jan-Feb,Mar-May,Jun-Sep,Oct-Dec
Output: Tab-delimited key-value pairs with composite key:
       Key:   SUBDIVISION##Decade
       Value: Annual_Rainfall\tMonsoon_Rainfall\t1
"""

import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if not row:
            continue
        # Skip header
        if len(row) >= 15 and row[0].strip().upper() == "SUBDIVISION":
            continue

        try:
            subdivision = row[0].strip().upper()
            year_val = int(row[1].strip())
            annual_val = float(row[14].strip())
            monsoon_val = float(row[17].strip()) if len(row) > 17 and row[17].strip() else 0.0

            decade = (year_val // 10) * 10
            composite_key = f"{subdivision}##{decade}s"

            print(f"{composite_key}\t{annual_val:.2f}\t{monsoon_val:.2f}\t1")
        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()
