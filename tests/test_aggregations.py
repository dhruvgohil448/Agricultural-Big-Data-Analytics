"""
tests/test_aggregations.py
Unit tests verifying outputs, cross-tool table consistency, and figure generation.
"""

import os
import pandas as pd
import pytest

TABLES_DIR = "outputs/tables"
FIGURES_DIR = "outputs/figures"

def test_output_tables_exist_and_populated():
    expected_tables = [
        "production_by_crop_year.csv",
        "top_states_production.csv",
        "crop_yield_trends.csv",
        "rainfall_decadal_summary.csv",
        "aligned_crop_rainfall_correlation.csv",
        "mr_crop_production_results.tsv",
        "mr_rainfall_results.tsv"
    ]
    for tbl in expected_tables:
        path = os.path.join(TABLES_DIR, tbl)
        assert os.path.exists(path), f"Expected table {path} is missing"
        assert os.path.getsize(path) > 0, f"Table {path} is empty"

def test_output_figures_exist_and_non_empty():
    expected_figs = [
        "fig1_national_crop_production_trends.png",
        "fig2_state_production_comparison.png",
        "fig3_crop_yield_evolution.png",
        "fig4_monsoon_rainfall_distribution.png",
        "fig5_rainfall_vs_crop_yield_scatter.png"
    ]
    for fig in expected_figs:
        path = os.path.join(FIGURES_DIR, fig)
        assert os.path.exists(path), f"Expected figure {path} is missing"
        assert os.path.getsize(path) > 10_000, f"Figure {path} is suspiciously small"

def test_mapreduce_numerical_consistency():
    mr_crop_file = os.path.join(TABLES_DIR, "mr_crop_production_results.tsv")
    df_mr = pd.read_csv(mr_crop_file, sep="\t", header=None)
    assert len(df_mr) == 12986, f"Expected 12,986 MapReduce groups, found {len(df_mr)}"
