#!/usr/bin/env python3
"""
src/mapreduce/rainfall_reducer.py
MapReduce Reducer for Meteorological Rainfall Aggregation.
Input: Sorted tab-delimited stream:
       SUBDIVISION##Decade\tAnnual_Rainfall\tMonsoon_Rainfall\tCount
Output: Tab-delimited aggregated summaries:
       SUBDIVISION\tDecade\tAvg_Annual_Rainfall_mm\tAvg_Monsoon_Rainfall_mm\tYear_Count
"""

import sys

def main():
    current_key = None
    sum_annual = 0.0
    sum_monsoon = 0.0
    total_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 4:
            continue

        key, annual_str, monsoon_str, count_str = parts

        try:
            annual = float(annual_str)
            monsoon = float(monsoon_str)
            cnt = int(count_str)
        except ValueError:
            continue

        if current_key == key:
            sum_annual += annual
            sum_monsoon += monsoon
            total_count += cnt
        else:
            if current_key:
                c_sub, c_dec = current_key.split("##")
                avg_ann = (sum_annual / total_count) if total_count > 0 else 0.0
                avg_mon = (sum_monsoon / total_count) if total_count > 0 else 0.0
                print(f"{c_sub}\t{c_dec}\t{avg_ann:.2f}\t{avg_mon:.2f}\t{total_count}")

            current_key = key
            sum_annual = annual
            sum_monsoon = monsoon
            total_count = cnt

    if current_key:
        c_sub, c_dec = current_key.split("##")
        avg_ann = (sum_annual / total_count) if total_count > 0 else 0.0
        avg_mon = (sum_monsoon / total_count) if total_count > 0 else 0.0
        print(f"{c_sub}\t{c_dec}\t{avg_ann:.2f}\t{avg_mon:.2f}\t{total_count}")

if __name__ == "__main__":
    main()
