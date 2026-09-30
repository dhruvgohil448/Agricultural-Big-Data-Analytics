# ==============================================================================
# src/r/statistical_analysis.R
# Independent Statistical Analysis & Econometric Cross-Check in R
# Fits linear regression models (Yield vs Rainfall) and computes correlation matrices.
# ==============================================================================

# Required packages:
# install.packages(c("readr", "dplyr", "ggplot2", "broom"))

suppressPackageStartupMessages({
  if (!requireNamespace("readr", quietly = TRUE)) install.packages("readr", repos="https://cloud.r-project.org")
  if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr", repos="https://cloud.r-project.org")
  if (!requireNamespace("ggplot2", quietly = TRUE)) install.packages("ggplot2", repos="https://cloud.r-project.org")
})

library(readr)
library(dplyr)
library(ggplot2)

cat("=================================================================\n")
cat("      Agricultural Big Data Analytics: R Statistical Analysis    \n")
cat("=================================================================\n\n")

# File paths
crop_file <- "data/processed/cleaned_crop_production.csv"
rain_file <- "data/processed/cleaned_state_rainfall.csv"
output_dir_tables <- "outputs/tables"
output_dir_figs <- "outputs/figures"

if (!dir.exists(output_dir_tables)) dir.create(output_dir_tables, recursive = TRUE)
if (!dir.exists(output_dir_figs)) dir.create(output_dir_figs, recursive = TRUE)

if (!file.exists(crop_file) || !file.exists(rain_file)) {
  stop("Input CSV files missing. Run data cleaning pipeline before executing R script.")
}

# 1. Ingestion
cat("[+] Reading cleaned datasets...\n")
crops <- read_csv(crop_file, show_col_types = FALSE)
rainfall <- read_csv(rain_file, show_col_types = FALSE)

# 2. Aggregation for Major Foodgrains (Rice, Wheat)
major_crops <- crops %>%
  filter(!Is_Nut_Unit, Crop %in% c("Rice", "Wheat"), !is.na(Production), Area > 0) %>%
  group_by(State_Name, Crop_Year) %>%
  summarise(
    Total_Area_Ha = sum(Area),
    Total_Prod_Ton = sum(Production),
    State_Yield = sum(Production) / sum(Area),
    .groups = "drop"
  )

# 3. Aligned Join with State Rainfall
analysis_df <- major_crops %>%
  inner_join(rainfall, by = c("State_Name" = "State_Name", "Crop_Year" = "YEAR"))

cat(sprintf("Aligned State-Year Observations: %d\n\n", nrow(analysis_df)))

# 4. Statistical Models
cat("[+] Fitting Linear Regression: State_Yield ~ MONSOON_RAIN_MM + ANNUAL_RAIN_MM\n")
model_ols <- lm(State_Yield ~ MONSOON_RAIN_MM + ANNUAL_RAIN_MM, data = analysis_df)
model_summary <- summary(model_ols)
print(model_summary)

# Correlation Matrix
cor_pearson <- cor(analysis_df$State_Yield, analysis_df$MONSOON_RAIN_MM, use = "complete.obs", method = "pearson")
cor_spearman <- cor(analysis_df$State_Yield, analysis_df$MONSOON_RAIN_MM, use = "complete.obs", method = "spearman")

cat(sprintf("\nPearson Correlation (Monsoon Rain vs Yield):  %.4f\n", cor_pearson))
cat(sprintf("Spearman Rank Correlation (Monsoon vs Yield): %.4f\n\n", cor_spearman))

# 5. Export Model Summary
sink(file.path(output_dir_tables, "r_statistical_summary.txt"))
cat("Agricultural Big Data Analytics: R Econometric & Statistical Verification\n")
cat("========================================================================\n\n")
print(model_summary)
cat(sprintf("\nPearson Correlation:  %.4f\n", cor_pearson))
cat(sprintf("Spearman Correlation: %.4f\n", cor_spearman))
sink()

# 6. Generate Regression Diagnostic Plot
p <- ggplot(analysis_df, aes(x = MONSOON_RAIN_MM, y = State_Yield)) +
  geom_point(alpha = 0.5, color = "#2b5c8f") +
  geom_smooth(method = "lm", color = "#d95f02", se = TRUE) +
  theme_minimal() +
  labs(
    title = "State Foodgrain Yield vs. Monsoon Rainfall (1997-2015)",
    subtitle = "Analysis of Rice and Wheat Production across Indian States",
    x = "Monsoon Rainfall (Jun-Sep, mm)",
    y = "Crop Yield (Tonnes / Hectare)",
    caption = "Source: Ministry of Agriculture & IMD (Govt. of India)"
  )

ggsave(file.path(output_dir_figs, "r_rainfall_yield_regression.png"), plot = p, width = 8, height = 5, dpi = 300)
cat("[+] Analysis and regression figures saved successfully.\n")
