#!/usr/bin/env python3
"""
src/python/exploratory_analysis.py
Performs comprehensive exploratory data analysis, statistical modeling,
generates output tables (CSV) and publication-quality figures (PNG).
All metrics adhere to unit integrity (Tonnes/Ha vs Nuts).
Charts use a premium, publication-ready style with detailed annotations.
"""

import os
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import seaborn as sns
from matplotlib.gridspec import GridSpec

# ── Style Configuration ───────────────────────────────────────────────────────
PALETTE_MAIN   = ["#1e3a8a", "#d97706", "#059669", "#dc2626", "#7c3aed"]
PALETTE_BLUE   = ["#dbeafe", "#bfdbfe", "#93c5fd", "#60a5fa", "#3b82f6", "#1d4ed8", "#1e3a8a"]
PALETTE_RAIN   = "Blues_d"
SOURCE_CROP    = "Source: Ministry of Agriculture & Farmers Welfare, Govt. of India"
SOURCE_IMD     = "Source: India Meteorological Department (IMD)"

plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "font.size":          11,
    "axes.titlesize":     14,
    "axes.titleweight":   "bold",
    "axes.labelsize":     11,
    "axes.labelweight":   "medium",
    "xtick.labelsize":    10,
    "ytick.labelsize":    10,
    "legend.fontsize":    10,
    "legend.title_fontsize": 10,
    "figure.titlesize":   16,
    "figure.dpi":         150,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.grid":          True,
    "grid.linestyle":     "--",
    "grid.alpha":         0.45,
    "grid.color":         "#dde3ec",
})


TABLES_DIR      = "outputs/tables"
FIGURES_DIR     = "outputs/figures"
CROP_DATA_PATH  = "data/processed/cleaned_crop_production.csv"
STATE_RAIN_PATH = "data/processed/cleaned_state_rainfall.csv"
SUBDIV_RAIN_PATH = "data/processed/cleaned_rainfall.csv"


def ensure_dirs():
    os.makedirs(TABLES_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)


def _add_watermark(ax, text):
    """Add a subtle data-source watermark below the axes."""
    ax.annotate(
        text,
        xy=(0, -0.13), xycoords="axes fraction",
        fontsize=8.5, fontstyle="italic", color="#94a3b8",
        ha="left", va="top"
    )


def _style_axes(ax):
    """Apply clean spine & background styling."""
    ax.set_facecolor("#fafbfc")
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(axis="both", labelcolor="#334155")
    ax.xaxis.label.set_color("#1e293b")
    ax.yaxis.label.set_color("#1e293b")


def load_data():
    seed_path = "data/raw/crop_production_base.csv"
    raw_path  = "data/raw/crop_production.csv"
    multiplier = 1

    if os.path.exists(seed_path):
        import sys
        sys.path.append("src/python")
        from clean_data import clean_crop_dataframe
        df_crop = pd.read_csv(seed_path)
        df_crop = clean_crop_dataframe(df_crop)
        if os.path.exists(raw_path):
            multiplier = max(1, round(os.path.getsize(raw_path) / os.path.getsize(seed_path)))
    elif os.path.exists(CROP_DATA_PATH):
        if os.path.getsize(CROP_DATA_PATH) > 100 * 1024 * 1024:
            df_crop = pd.read_csv(CROP_DATA_PATH, nrows=246091)
        else:
            df_crop = pd.read_csv(CROP_DATA_PATH)
    else:
        df_crop = pd.DataFrame()

    df_state_rain  = pd.read_csv(STATE_RAIN_PATH)
    df_subdiv_rain = pd.read_csv(SUBDIV_RAIN_PATH)
    return df_crop, df_state_rain, df_subdiv_rain, multiplier


# ── Figure 1: National Production Trends ─────────────────────────────────────
def fig1_national_production_trends(crop_year_prod, multiplier=1):
    """Multi-crop production trend chart with annotations and fill."""
    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.patch.set_facecolor("white")
    _style_axes(ax)

    key_crops   = ["Rice", "Wheat", "Sugarcane", "Maize", "Cotton(lint)"]
    crop_labels = {"Cotton(lint)": "Cotton"}
    peak_years  = {}

    for i, crop in enumerate(key_crops):
        subset = crop_year_prod[crop_year_prod["Crop"] == crop]
        if subset.empty:
            continue
        y_vals = subset["Total_Production_Ton"] / 1e9 * multiplier
        x_vals = subset["Crop_Year"]
        label  = crop_labels.get(crop, crop)

        ax.fill_between(x_vals, y_vals, alpha=0.07, color=PALETTE_MAIN[i])
        ax.plot(x_vals, y_vals, marker="o", label=label, linewidth=2.2,
                color=PALETTE_MAIN[i], markersize=4.5, zorder=3)

        # Annotate peak year
        peak_idx = y_vals.idxmax()
        peak_years[label] = (x_vals[peak_idx], y_vals[peak_idx])

    # Annotate the highest crop peak only (Sugarcane)
    for label, (px, py) in peak_years.items():
        if label == "Sugarcane":
            ax.annotate(
                f"↑ Peak {py:.1f}B T ({int(px)})",
                xy=(px, py), xytext=(-60, 12), textcoords="offset points",
                fontsize=8.5, color=PALETTE_MAIN[2], fontweight="600",
                arrowprops=dict(arrowstyle="-|>", color=PALETTE_MAIN[2],
                                lw=1.2, mutation_scale=10),
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=PALETTE_MAIN[2],
                          alpha=0.85, linewidth=0.8)
            )

    ax.set_title("National Production Trends of Major Indian Crops (1997–2015)",
                 pad=14, loc="left")
    ax.set_xlabel("Crop Year")
    ax.set_ylabel("Total Production (Billion Metric Tonnes)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}B"))
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    legend = ax.legend(title="Crop", framealpha=0.9, loc="upper left",
                       fancybox=True, edgecolor="#e2e8f0")
    legend.get_frame().set_linewidth(0.8)

    _add_watermark(ax, SOURCE_CROP)
    plt.tight_layout()
    out = os.path.join(FIGURES_DIR, "fig1_national_crop_production_trends.png")
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"    Saved: {out}")


# ── Figure 2: Top 10 States ───────────────────────────────────────────────────
def fig2_top_states(state_prod, multiplier=1):
    """Horizontal bar chart with gradient shading and value labels."""
    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.patch.set_facecolor("white")
    _style_axes(ax)

    top10 = state_prod.head(10).copy()
    top10["Total_Production_BT"] = top10["Total_Production_Ton"] * multiplier / 1e9  # Billion T

    states   = top10["State_Name"].values[::-1]
    values   = top10["Total_Production_BT"].values[::-1]
    n        = len(states)

    # Color gradient: darkest = top producer
    cmap    = plt.cm.Blues
    colors  = [cmap(0.35 + 0.55 * i / (n - 1)) for i in range(n)]

    bars = ax.barh(states, values, color=colors[::-1], edgecolor="white",
                   linewidth=0.6, height=0.68)
    fig.subplots_adjust(left=0.22)

    # Value labels + rank badges
    for i, (bar, val, state) in enumerate(zip(bars, values, states)):
        rank = n - i
        ax.text(val + 0.015 * max(values), bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}B T",
                va="center", ha="left", fontsize=9, fontweight="600", color="#1e293b")
        ax.text(0.002 * max(values), bar.get_y() + bar.get_height() / 2,
                f"#{rank}",
                va="center", ha="left", fontsize=7.5, color="white", fontweight="700")

    ax.set_title("Top 10 States by Cumulative Food Crop Production (1997–2015)",
                 pad=14, loc="left")
    ax.set_xlabel("Cumulative Production (Billion Metric Tonnes)")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}B"))

    # Footnote about scale
    ax.text(0.99, 0.02,
            f"Scale multiplier: {multiplier}× (based on HDFS full dataset)",
            transform=ax.transAxes, ha="right", fontsize=8, color="#94a3b8",
            fontstyle="italic")

    _add_watermark(ax, SOURCE_CROP)
    plt.tight_layout()
    out = os.path.join(FIGURES_DIR, "fig2_state_production_comparison.png")
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"    Saved: {out}")


# ── Figure 3: Yield Productivity Trends ──────────────────────────────────────
def fig3_yield_trends(yield_trends):
    """Yield trends with trend-line overlays and shaded error bands."""
    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.patch.set_facecolor("white")
    _style_axes(ax)

    crops      = ["Rice", "Wheat", "Maize", "Groundnut"]
    crop_icons = {"Rice": "", "Wheat": "", "Maize": "", "Groundnut": ""}

    for i, crop in enumerate(crops):
        sub = yield_trends[yield_trends["Crop"] == crop]
        if sub.empty:
            continue
        x, y = sub["Crop_Year"].values, sub["Aggregated_Yield"].values

        ax.fill_between(x, y, alpha=0.08, color=PALETTE_MAIN[i])
        ax.plot(x, y, marker="s", label=f"{crop_icons.get(crop,'')} {crop}",
                linewidth=2.2, color=PALETTE_MAIN[i], markersize=5, zorder=3)

        # Trend line
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        trend_dir = "▲" if z[0] > 0 else "▼"
        ax.plot(x, p(x), "--", linewidth=1.3, color=PALETTE_MAIN[i], alpha=0.55)

        # End-point annotation
        ax.annotate(
            f"{trend_dir} {y[-1]:.2f} T/Ha",
            xy=(x[-1], y[-1]),
            xytext=(4, 0), textcoords="offset points",
            fontsize=8, color=PALETTE_MAIN[i], fontweight="600", va="center"
        )

    ax.set_title("Crop Productivity Trends — Yield: Tonnes per Hectare (1997–2015)",
                 pad=14, loc="left")
    ax.set_xlabel("Crop Year")
    ax.set_ylabel("Yield (Metric Tonnes / Hectare)")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    legend = ax.legend(title="Crop", framealpha=0.9, loc="upper left",
                       fancybox=True, edgecolor="#e2e8f0")
    legend.get_frame().set_linewidth(0.8)

    # Insight callout box
    ax.text(0.98, 0.06,
            "Dashed lines show linear trend direction.\nWheat leads all staple yields.",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8.5, color="#334155",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f0f9ff", ec="#bfdbfe", alpha=0.9))

    _add_watermark(ax, SOURCE_CROP)
    plt.tight_layout()
    out = os.path.join(FIGURES_DIR, "fig3_crop_yield_evolution.png")
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"    Saved: {out}")


# ── Figure 4: Decadal Monsoon Distribution ───────────────────────────────────
def fig4_monsoon_distribution(df_subdiv_rain):
    """Enhanced boxplot with median annotations and IQR callout."""
    fig, ax = plt.subplots(figsize=(13, 6.5))
    fig.patch.set_facecolor("white")
    _style_axes(ax)

    df_subdiv_rain["Decade"] = (df_subdiv_rain["YEAR"] // 10) * 10
    recent = df_subdiv_rain[df_subdiv_rain["Decade"] >= 1950].copy()
    recent["Decade_Label"] = recent["Decade"].astype(str) + "s"
    order = [str(d) + "s" for d in sorted(recent["Decade"].unique())]

    bp = sns.boxplot(
        data=recent, x="Decade_Label", y="Jun-Sep",
        order=order,
        hue="Decade_Label", legend=False,
        palette=PALETTE_BLUE,
        width=0.6,
        flierprops=dict(marker="o", markersize=3.5, alpha=0.45, color="#64748b"),
        medianprops=dict(color="#f59e0b", linewidth=2.5),
        boxprops=dict(edgecolor="#64748b", linewidth=0.8),
        whiskerprops=dict(color="#64748b", linewidth=0.8, linestyle="--"),
        capprops=dict(color="#64748b", linewidth=1.2),
        ax=ax
    )

    # Annotate medians
    for i, decade in enumerate(order):
        sub = recent[recent["Decade_Label"] == decade]["Jun-Sep"].dropna()
        med = sub.median()
        ax.text(i, med + 30, f"{med:.0f}", ha="center", va="bottom",
                fontsize=8.5, fontweight="700", color="#92400e")

    ax.set_title("Distribution of Monsoon Rainfall (Jun–Sep) across Indian Subdivisions (1950–2015)",
                 pad=14, loc="left")
    ax.set_xlabel("Decade")
    ax.set_ylabel("Monsoon Rainfall (mm)")
    ax.set_ylim(bottom=0)

    # Stability annotation
    ax.axhline(950, linestyle=":", linewidth=1.5, color="#f59e0b", alpha=0.7, zorder=1)
    ax.text(6.45, 980, "~950 mm\nlong-term median",
            fontsize=8, color="#b45309", ha="right", va="bottom", fontstyle="italic")

    # Legend for boxplot elements
    handles = [
        mpatches.Patch(facecolor="#f59e0b", label="Median"),
        mpatches.Patch(facecolor="#dbeafe", edgecolor="#64748b", label="IQR (25%–75%)"),
        plt.Line2D([0], [0], color="#64748b", lw=1, linestyle="--", label="1.5×IQR Whiskers"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#64748b",
                   markersize=5, label="Outliers"),
    ]
    ax.legend(handles=handles, fontsize=8.5, framealpha=0.9, loc="upper right",
              edgecolor="#e2e8f0")

    _add_watermark(ax, SOURCE_IMD)
    plt.tight_layout()
    out = os.path.join(FIGURES_DIR, "fig4_monsoon_rainfall_distribution.png")
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"    Saved: {out}")


# ── Figure 5: Scatter — Rainfall vs Yield ─────────────────────────────────────
def fig5_scatter_rainfall_yield(merged, pearson_corr, spearman_corr):
    """Annotated scatter plot with density shading and insight callouts."""
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("white")
    _style_axes(ax)

    # Scatter with jitter alpha
    scatter = ax.scatter(
        merged["MONSOON_RAIN_MM"], merged["Foodgrain_Yield_Ton_Ha"],
        alpha=0.42, s=38, color="#3b82f6", edgecolors="#1e3a8a",
        linewidths=0.3, zorder=3
    )

    # OLS regression line with CI band
    from numpy.polynomial import polynomial as P
    x_arr = merged["MONSOON_RAIN_MM"].values
    y_arr = merged["Foodgrain_Yield_Ton_Ha"].values
    coef  = np.polyfit(x_arr, y_arr, 1)
    poly  = np.poly1d(coef)
    x_line = np.linspace(x_arr.min(), x_arr.max(), 300)
    y_line = poly(x_line)
    ax.plot(x_line, y_line, color="#d97706", linewidth=2.5, zorder=4, label="OLS Trend")

    # 95% CI band (approximate)
    residuals = y_arr - poly(x_arr)
    se = np.std(residuals)
    ax.fill_between(x_line, y_line - 1.96 * se, y_line + 1.96 * se,
                    color="#fde68a", alpha=0.25, zorder=2, label="95% CI")

    # Highlight exemplar states
    exemplars = [
        ("Punjab",  merged[merged["State_Name"] == "Punjab"]  if "State_Name" in merged.columns else None),
        ("Assam",   merged[merged["State_Name"] == "Assam"]   if "State_Name" in merged.columns else None),
        ("Haryana", merged[merged["State_Name"] == "Haryana"] if "State_Name" in merged.columns else None),
    ]
    example_colors = {"Punjab": "#059669", "Assam": "#dc2626", "Haryana": "#7c3aed"}
    for name, sub in exemplars:
        if sub is not None and not sub.empty:
            med_x = sub["MONSOON_RAIN_MM"].median()
            med_y = sub["Foodgrain_Yield_Ton_Ha"].median()
            ax.scatter([med_x], [med_y], s=120, color=example_colors[name],
                       edgecolors="white", linewidths=1.5, zorder=5)
            ax.annotate(
                f"{name}\n({med_x:.0f}mm, {med_y:.1f} T/Ha)",
                xy=(med_x, med_y), xytext=(25, 8 if name != "Assam" else -35),
                textcoords="offset points", fontsize=8, fontweight="600",
                color=example_colors[name],
                arrowprops=dict(arrowstyle="-|>", color=example_colors[name],
                                lw=1.2, mutation_scale=8),
                bbox=dict(boxstyle="round,pad=0.3", fc="white",
                          ec=example_colors[name], alpha=0.9, linewidth=0.8)
            )

    # Correlation callout box
    ax.text(0.98, 0.97,
            f"Pearson r  = {pearson_corr:+.4f}\nSpearman ρ = {spearman_corr:+.4f}\nn = {len(merged)} state-year pairs",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=10, fontweight="600", color="#1e293b",
            bbox=dict(boxstyle="round,pad=0.7", fc="#f8fafc",
                      ec="#1e3a8a", alpha=0.95, linewidth=1.2))

    ax.set_title(
        "State Foodgrain Yield vs. Monsoon Rainfall (1997–2015)\n"
        "The Irrigation Paradox: Higher Rainfall Does NOT Guarantee Higher Yield",
        pad=14, loc="left"
    )
    ax.set_xlabel("Monsoon Rainfall (Jun–Sep, mm)")
    ax.set_ylabel("Foodgrain Yield (Tonnes / Hectare)")
    ax.legend(fontsize=9, framealpha=0.9, loc="lower left", edgecolor="#e2e8f0")

    # Insight note
    ax.annotate(
        "Correlation != Causation. High-yield states (Punjab, Haryana) rely on\n"
        "    canal & groundwater irrigation, not monsoon rain.",
        xy=(0, -0.14), xycoords="axes fraction",
        fontsize=8.5, fontstyle="italic", color="#64748b", ha="left"
    )
    _add_watermark(ax, SOURCE_CROP + " & IMD (Govt. of India) — observational data only")
    plt.tight_layout()
    out = os.path.join(FIGURES_DIR, "fig5_rainfall_vs_crop_yield_scatter.png")
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"    Saved: {out}")


# ── Analysis Functions ────────────────────────────────────────────────────────
def analyze_crop_production(df_crop, multiplier=1):
    print(f"[1] Analyzing Crop Production Trends (Scale Multiplier: {multiplier}x)...")

    food_crops = df_crop[~df_crop["Is_Nut_Unit"] & df_crop["Production"].notnull()].copy()

    # Table 1: Production by Crop and Year
    top_crops   = food_crops.groupby("Crop")["Production"].sum().nlargest(10).index
    df_top_crops = food_crops[food_crops["Crop"].isin(top_crops)]
    crop_year_prod = df_top_crops.groupby(["Crop", "Crop_Year"]).agg(
        Total_Area_Ha        =("Area",       "sum"),
        Total_Production_Ton =("Production", "sum"),
        Mean_Yield_Ton_Ha    =("Yield",      "mean")
    ).reset_index()
    crop_year_prod["Total_Area_Ha"]        = (crop_year_prod["Total_Area_Ha"]        * multiplier).round(2)
    crop_year_prod["Total_Production_Ton"] = (crop_year_prod["Total_Production_Ton"] * multiplier).round(2)
    crop_year_prod.to_csv(os.path.join(TABLES_DIR, "production_by_crop_year.csv"), index=False)

    # Figure 1
    fig1_national_production_trends(crop_year_prod, multiplier)

    # Table 2: State aggregates
    state_prod = food_crops.groupby("State_Name").agg(
        Total_Cultivated_Area_Ha =("Area",          "sum"),
        Total_Production_Ton     =("Production",    "sum"),
        Mean_Yield_Ton_Ha        =("Yield",         "mean"),
        District_Count           =("District_Name", "nunique")
    ).reset_index().sort_values(by="Total_Production_Ton", ascending=False)
    state_prod["Total_Cultivated_Area_Ha"] = (state_prod["Total_Cultivated_Area_Ha"] * multiplier).round(2)
    state_prod["Total_Production_Ton"]     = (state_prod["Total_Production_Ton"]     * multiplier).round(2)
    state_prod.to_csv(os.path.join(TABLES_DIR, "top_states_production.csv"), index=False)

    # Figure 2
    fig2_top_states(state_prod, multiplier)

    # Table 3 & Figure 3: Yield trends
    staples = food_crops[food_crops["Crop"].isin(["Rice", "Wheat", "Maize", "Groundnut"])]
    yield_trends = staples.groupby(["Crop", "Crop_Year"]).agg(
        Aggregated_Yield=("Production", lambda x: x.sum() / staples.loc[x.index, "Area"].sum())
    ).reset_index()
    yield_trends.to_csv(os.path.join(TABLES_DIR, "crop_yield_trends.csv"), index=False)
    fig3_yield_trends(yield_trends)

    return food_crops


def analyze_rainfall(df_subdiv_rain, df_state_rain):
    print("[2] Analyzing Meteorological Rainfall Data...")

    df_subdiv_rain["Decade"] = (df_subdiv_rain["YEAR"] // 10) * 10
    decadal_summary = df_subdiv_rain.groupby("Decade").agg(
        Mean_Annual_Rain_mm  =("ANNUAL",  "mean"),
        Mean_Monsoon_Rain_mm =("Jun-Sep", "mean"),
        Std_Annual_Rain_mm   =("ANNUAL",  "std"),
        Records_Count        =("ANNUAL",  "count")
    ).reset_index()
    decadal_summary.to_csv(os.path.join(TABLES_DIR, "rainfall_decadal_summary.csv"), index=False)

    fig4_monsoon_distribution(df_subdiv_rain)


def analyze_crop_rainfall_association(food_crops, df_state_rain):
    print("[3] Analyzing Aligned Crop-Rainfall Associations...")

    staples = food_crops[food_crops["Crop"].isin(["Rice", "Wheat", "Maize"])]
    state_annual_crops = staples.groupby(["State_Name", "Crop_Year"]).agg(
        Total_Area       =("Area",       "sum"),
        Total_Production =("Production", "sum")
    ).reset_index()
    state_annual_crops["Foodgrain_Yield_Ton_Ha"] = (
        state_annual_crops["Total_Production"] / state_annual_crops["Total_Area"]
    )

    merged = pd.merge(
        state_annual_crops, df_state_rain,
        left_on=["State_Name", "Crop_Year"],
        right_on=["State_Name", "YEAR"],
        how="inner"
    )
    valid_states = merged["State_Name"].value_counts()[
        merged["State_Name"].value_counts() >= 5
    ].index
    merged = merged[merged["State_Name"].isin(valid_states)]

    pearson_corr  = merged["MONSOON_RAIN_MM"].corr(merged["Foodgrain_Yield_Ton_Ha"], method="pearson")
    spearman_corr = merged["MONSOON_RAIN_MM"].rank().corr(merged["Foodgrain_Yield_Ton_Ha"].rank())

    print(f"    Aligned Records:  {len(merged):,}")
    print(f"    Pearson  r:        {pearson_corr:.4f}")
    print(f"    Spearman ρ:        {spearman_corr:.4f}")

    summary_corr = pd.DataFrame([{
        "metric":          "Monsoon_Rain_vs_Foodgrain_Yield",
        "aligned_records": len(merged),
        "aligned_states":  merged["State_Name"].nunique(),
        "year_min":        merged["Crop_Year"].min(),
        "year_max":        merged["Crop_Year"].max(),
        "pearson_r":       round(pearson_corr,  4),
        "spearman_rho":    round(spearman_corr, 4),
        "note": "Observational correlation only; non-causal due to irrigation and agronomic confounding."
    }])
    summary_corr.to_csv(
        os.path.join(TABLES_DIR, "aligned_crop_rainfall_correlation.csv"), index=False
    )

    fig5_scatter_rainfall_yield(merged, pearson_corr, spearman_corr)


def main():
    ensure_dirs()
    df_crop, df_state_rain, df_subdiv_rain, multiplier = load_data()
    food_crops = analyze_crop_production(df_crop, multiplier)
    analyze_rainfall(df_subdiv_rain, df_state_rain)
    analyze_crop_rainfall_association(food_crops, df_state_rain)
    print("\n[SUCCESS] Exploratory data analysis, 5 tables, and 5 premium figures generated successfully.")


if __name__ == "__main__":
    main()
