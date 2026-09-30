-- ==============================================================================
-- hive/create_tables.hql
-- DDL schema definitions for Agricultural Big Data Analytics System
-- External tables mapped to HDFS storage locations
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS agriculture_db;
USE agriculture_db;

-- 1. Crop Production Cleaned Table
DROP TABLE IF EXISTS crop_production;
CREATE EXTERNAL TABLE IF NOT EXISTS crop_production (
    state_name      STRING,
    district_name   STRING,
    crop_year       INT,
    season          STRING,
    crop            STRING,
    area_ha         DOUBLE,
    production_ton  DOUBLE,
    is_nut_unit     BOOLEAN,
    yield_metric    DOUBLE
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
LOCATION '/user/dhruvgohil/agriculture/processed/crop_production_tbl'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 2. Meteorological Rainfall Cleaned Table
DROP TABLE IF EXISTS rainfall;
CREATE EXTERNAL TABLE IF NOT EXISTS rainfall (
    subdivision     STRING,
    year            INT,
    jan             DOUBLE,
    feb             DOUBLE,
    mar             DOUBLE,
    apr             DOUBLE,
    may             DOUBLE,
    jun             DOUBLE,
    jul             DOUBLE,
    aug             DOUBLE,
    sep             DOUBLE,
    oct             DOUBLE,
    nov             DOUBLE,
    dec             DOUBLE,
    annual          DOUBLE,
    jan_feb         DOUBLE,
    mar_may         DOUBLE,
    jun_sep         DOUBLE,
    oct_dec         DOUBLE,
    state_name      STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
LOCATION '/user/dhruvgohil/agriculture/processed/rainfall_tbl'
TBLPROPERTIES ("skip.header.line.count"="1");
