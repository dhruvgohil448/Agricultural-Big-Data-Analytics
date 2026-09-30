-- ==============================================================================
-- hive/analytics.hql
-- Analytical queries for Agricultural Big Data Analytics System
-- Executes aggregations, decadal trends, and crop-rainfall correlations
-- ==============================================================================

USE agriculture_db;

-- 1. Top 10 Crops by Total Cultivated Area in India (Excluding Coconut)
SELECT 
    crop,
    ROUND(SUM(area_ha), 2) AS total_cultivated_area_ha,
    ROUND(SUM(production_ton), 2) AS total_production_ton,
    ROUND(SUM(production_ton) / NULLIF(SUM(area_ha), 0), 4) AS national_yield_ton_per_ha
FROM crop_production
WHERE is_nut_unit = false AND production_ton IS NOT NULL
GROUP BY crop
ORDER BY total_cultivated_area_ha DESC
LIMIT 10;

-- 2. State-wise Wheat and Rice Production Trends (2000-2015)
SELECT 
    state_name,
    crop,
    crop_year,
    ROUND(SUM(area_ha), 2) AS total_area,
    ROUND(SUM(production_ton), 2) AS total_production,
    ROUND(SUM(production_ton) / NULLIF(SUM(area_ha), 0), 3) AS yield_ton_per_ha
FROM crop_production
WHERE crop IN ('Rice', 'Wheat') AND crop_year BETWEEN 2000 AND 2015
GROUP BY state_name, crop, crop_year
ORDER BY state_name, crop, crop_year;

-- 3. Decadal Average Annual and Monsoon Rainfall by Meteorological Subdivision
SELECT 
    subdivision,
    FLOOR(year / 10) * 10 AS decade,
    ROUND(AVG(annual), 2) AS avg_annual_rainfall_mm,
    ROUND(AVG(jun_sep), 2) AS avg_monsoon_rainfall_mm,
    COUNT(1) AS years_recorded
FROM rainfall
WHERE annual IS NOT NULL
GROUP BY subdivision, FLOOR(year / 10) * 10
ORDER BY subdivision, decade;

-- 4. Aligned State-Level Crop Yield vs. Annual Rainfall (1997-2015)
WITH state_rain AS (
    SELECT 
        state_name,
        year,
        AVG(annual) AS avg_state_rainfall,
        AVG(jun_sep) AS avg_state_monsoon
    FROM rainfall
    GROUP BY state_name, year
),
state_crops AS (
    SELECT 
        state_name,
        crop_year,
        SUM(production_ton) / NULLIF(SUM(area_ha), 0) AS state_foodgrain_yield
    FROM crop_production
    WHERE crop IN ('Rice', 'Wheat', 'Maize') AND is_nut_unit = false
    GROUP BY state_name, crop_year
)
SELECT 
    c.state_name,
    c.crop_year,
    ROUND(c.state_foodgrain_yield, 3) AS foodgrain_yield_ton_per_ha,
    ROUND(r.avg_state_rainfall, 2) AS annual_rainfall_mm,
    ROUND(r.avg_state_monsoon, 2) AS monsoon_rainfall_mm
FROM state_crops c
JOIN state_rain r 
  ON c.state_name = r.state_name AND c.crop_year = r.year
ORDER BY c.state_name, c.crop_year;
