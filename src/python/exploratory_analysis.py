#!/usr/bin/env python3
"""
src/python/exploratory_analysis.py
Performs comprehensive exploratory data analysis, statistical modeling,
generates output tables (CSV) and publication-quality figures (PNG).
All metrics adhere to unit integrity (Tonnes/Ha vs Nuts).
"""

import os
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14
})

TABLES_DIR = "outputs/tables"
FIGURES_DIR = "outputs/figures"
CROP_DATA_PATH = "data/processed/cleaned_crop_production.csv"
STATE_RAIN_PATH = "data/processed/cleaned_state_rainfall.csv"
SUBDIV_RAIN_PATH = "data/processed/cleaned_rainfall.csv"

def ensure_dirs():
    os.makedirs(TABLES_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

def load_data():
    df_crop = pd.read_csv(CROP_DATA_PATH)
    df_state_rain = pd.read_csv(STATE_RAIN_PATH)
    df_subdiv_rain = pd.read_csv(SUBDIV_RAIN_PATH)
    return df_crop, df_state_rain, df_subdiv_rain

def analyze_crop_production(df_crop):
    print("[1] Analyzing Crop Production Trends...")

    # Filter out nuts unit for mass/tonnage aggregations
    food_crops = df_crop[~df_crop["Is_Nut_Unit"] & df_crop["Production"].notnull()].copy()

    # Table 1: Production by Crop and Year (Top 10 major crops)
    top_crops = food_crops.groupby("Crop")["Production"].sum().nlargest(10).index
    df_top_crops = food_crops[food_crops["Crop"].isin(top_crops)]

    crop_year_prod = df_top_crops.groupby(["Crop", "Crop_Year"]).agg(
        Total_Area_Ha=("Area", "sum"),
        Total_Production_Ton=("Production", "sum"),
        Mean_Yield_Ton_Ha=("Yield", "mean")
    ).reset_index()

    crop_year_prod.to_csv(os.path.join(TABLES_DIR, "production_by_crop_year.csv"), index=False)

    # Figure 1: National Production Trends for Key Crops (Rice, Wheat, Sugarcane, Maize)
    plt.figure(figsize=(10, 6))
    key_crops = ["Rice", "Wheat", "Sugarcane", "Maize", "Cotton(lint)"]
    for crop in key_crops:
        subset = crop_year_prod[crop_year_prod["Crop"] == crop]
        if not subset.empty:
            plt.plot(subset["Crop_Year"], subset["Total_Production_Ton"] / 1e6, marker="o", label=crop, linewidth=2)

    plt.title("National Production Trends of Major Indian Crops (1997–2015)")
    plt.xlabel("Crop Year")
    plt.ylabel("Total Production (Million Metric Tonnes)")
    plt.legend(title="Crop")
    plt.annotate("Source: Ministry of Agriculture & Farmers Welfare, Govt. of India",
                 xy=(0.01, -0.12), xycoords="axes fraction", fontsize=9, fontstyle="italic")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig1_national_crop_production_trends.png"), dpi=300)
    plt.close()

    # Table 2: Regional / State Comparisons
    state_prod = food_crops.groupby("State_Name").agg(
        Total_Cultivated_Area_Ha=("Area", "sum"),
        Total_Production_Ton=("Production", "sum"),
        Mean_Yield_Ton_Ha=("Yield", "mean"),
        District_Count=("District_Name", "nunique")
    ).reset_index().sort_values(by="Total_Production_Ton", ascending=False)

    state_prod.to_csv(os.path.join(TABLES_DIR, "top_states_production.csv"), index=False)

    # Figure 2: Top 10 Agricultural Producer States
    plt.figure(figsize=(10, 6))
    top_states = state_prod.head(10)
    sns.barplot(data=top_states, x="Total_Production_Ton", y="State_Name", color="#2b5c8f")
    plt.title("Top 10 States by Cumulative Food Crop Production (1997–2015)")
    plt.xlabel("Total Production (Metric Tonnes)")
    plt.ylabel("State / UT")
    plt.annotate("Source: Ministry of Agriculture & Farmers Welfare, Govt. of India",
                 xy=(0.01, -0.12), xycoords="axes fraction", fontsize=9, fontstyle="italic")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig2_state_production_comparison.png"), dpi=300)
    plt.close()

    # Table 3: Yield Trends over Time
    staples = food_crops[food_crops["Crop"].isin(["Rice", "Wheat", "Maize", "Groundnut"])]
    yield_trends = staples.groupby(["Crop", "Crop_Year"]).agg(
        Aggregated_Yield=("Production", lambda x: x.sum() / staples.loc[x.index, "Area"].sum())
    ).reset_index()
    yield_trends.to_csv(os.path.join(TABLES_DIR, "crop_yield_trends.csv"), index=False)

    # Figure 3: Yield Productivity Trends (Tonnes/Ha)
    plt.figure(figsize=(10, 6))
    for crop in ["Rice", "Wheat", "Maize", "Groundnut"]:
        sub = yield_trends[yield_trends["Crop"] == crop]
        plt.plot(sub["Crop_Year"], sub["Aggregated_Yield"], marker="s", label=crop, linewidth=2)

    plt.title("Crop Productivity Trends (Yield: Tonnes per Hectare, 1997–2015)")
    plt.xlabel("Crop Year")
    plt.ylabel("Yield (Metric Tonnes / Hectare)")
    plt.legend(title="Crop")
    plt.annotate("Source: Ministry of Agriculture & Farmers Welfare, Govt. of India",
                 xy=(0.01, -0.12), xycoords="axes fraction", fontsize=9, fontstyle="italic")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig3_crop_yield_evolution.png"), dpi=300)
    plt.close()

    return food_crops

def analyze_rainfall(df_subdiv_rain, df_state_rain):
    print("[2] Analyzing Meteorological Rainfall Data...")

    # Table 4: Decadal Rainfall Summary
    df_subdiv_rain["Decade"] = (df_subdiv_rain["YEAR"] // 10) * 10
    decadal_summary = df_subdiv_rain.groupby("Decade").agg(
        Mean_Annual_Rain_mm=("ANNUAL", "mean"),
        Mean_Monsoon_Rain_mm=("Jun-Sep", "mean"),
        Std_Annual_Rain_mm=("ANNUAL", "std"),
        Records_Count=("ANNUAL", "count")
    ).reset_index()
    decadal_summary.to_csv(os.path.join(TABLES_DIR, "rainfall_decadal_summary.csv"), index=False)

    # Figure 4: Decadal Monsoon Rainfall Distribution across Subdivisions
    plt.figure(figsize=(11, 6))
    recent_decades = df_subdiv_rain[df_subdiv_rain["Decade"] >= 1950].copy()
    recent_decades["Decade_Label"] = recent_decades["Decade"].astype(str) + "s"
    sns.boxplot(data=recent_decades, x="Decade_Label", y="Jun-Sep", hue="Decade_Label", legend=False, palette="Blues_d")
    plt.title("Distribution of Monsoon Rainfall (Jun–Sep) across Indian Subdivisions (1950–2015)")
    plt.xlabel("Decade")
    plt.ylabel("Monsoon Rainfall (mm)")
    plt.annotate("Source: India Meteorological Department (IMD)",
                 xy=(0.01, -0.12), xycoords="axes fraction", fontsize=9, fontstyle="italic")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig4_monsoon_rainfall_distribution.png"), dpi=300)
    plt.close()

def analyze_crop_rainfall_association(food_crops, df_state_rain):
    print("[3] Analyzing Aligned Crop-Rainfall Associations...")

    # Align state food grain production with state rainfall (1997 to 2015)
    staples = food_crops[food_crops["Crop"].isin(["Rice", "Wheat", "Maize"])]

    state_annual_crops = staples.groupby(["State_Name", "Crop_Year"]).agg(
        Total_Area=("Area", "sum"),
        Total_Production=("Production", "sum")
    ).reset_index()

    state_annual_crops["Foodgrain_Yield_Ton_Ha"] = (
        state_annual_crops["Total_Production"] / state_annual_crops["Total_Area"]
    )

    merged = pd.merge(
        state_annual_crops,
        df_state_rain,
        left_on=["State_Name", "Crop_Year"],
        right_on=["State_Name", "YEAR"],
        how="inner"
    )

    # Filter out states with fewer than 5 years of observations
    valid_states = merged["State_Name"].value_counts()[merged["State_Name"].value_counts() >= 5].index
    merged = merged[merged["State_Name"].isin(valid_states)]

    # Compute correlation metrics
    pearson_corr = merged["MONSOON_RAIN_MM"].corr(merged["Foodgrain_Yield_Ton_Ha"], method="pearson")
    # Spearman rank correlation equals Pearson correlation between the ranked variables
    spearman_corr = merged["MONSOON_RAIN_MM"].rank().corr(merged["Foodgrain_Yield_Ton_Ha"].rank())

    print(f"    Aligned Records: {len(merged):,}")
    print(f"    Pearson Correlation (Monsoon Rain vs Yield): {pearson_corr:.4f}")
    print(f"    Spearman Correlation (Monsoon Rain vs Yield): {spearman_corr:.4f}")

    # Table 5: Aligned Correlation and Association Data
    summary_corr = pd.DataFrame([{
        "metric": "Monsoon_Rain_vs_Foodgrain_Yield",
        "aligned_records": len(merged),
        "aligned_states": merged["State_Name"].nunique(),
        "year_min": merged["Crop_Year"].min(),
        "year_max": merged["Crop_Year"].max(),
        "pearson_r": round(pearson_corr, 4),
        "spearman_rho": round(spearman_corr, 4),
        "note": "Observational correlation only; non-causal due to irrigation and agronomic confounding."
    }])
    summary_corr.to_csv(os.path.join(TABLES_DIR, "aligned_crop_rainfall_correlation.csv"), index=False)

    # Figure 5: Scatter Plot with Linear Trend
    plt.figure(figsize=(10, 6))
    sns.regplot(
        data=merged,
        x="MONSOON_RAIN_MM",
        y="Foodgrain_Yield_Ton_Ha",
        scatter_kws={"alpha": 0.4, "color": "#2b5c8f"},
        line_kws={"color": "#d95f02", "linewidth": 2}
    )
    plt.title(f"State Foodgrain Yield vs. Monsoon Rainfall (1997–2015)\nPearson r = {pearson_corr:.3f}, Spearman rho = {spearman_corr:.3f}")
    plt.xlabel("Monsoon Rainfall (Jun–Sep, mm)")
    plt.ylabel("Foodgrain Yield (Tonnes / Hectare)")
    plt.annotate("Note: Association does not imply causation. High-yield states (e.g. Punjab, Haryana) rely heavily on canal/groundwater irrigation.\nSource: Ministry of Agriculture & IMD (Govt. of India)",
                 xy=(0.01, -0.15), xycoords="axes fraction", fontsize=8.5, fontstyle="italic")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig5_rainfall_vs_crop_yield_scatter.png"), dpi=300)
    plt.close()

def main():
    ensure_dirs()
    df_crop, df_state_rain, df_subdiv_rain = load_data()
    food_crops = analyze_crop_production(df_crop)
    analyze_rainfall(df_subdiv_rain, df_state_rain)
    analyze_crop_rainfall_association(food_crops, df_state_rain)
    print("\n[SUCCESS] Exploratory data analysis, 5 tables, and 5 figures generated successfully.")

if __name__ == "__main__":
    main()
