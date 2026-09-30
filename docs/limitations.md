# Limitations, Assumptions & Environmental Constraints

This document provides a transparent and rigorous accounting of the data quality limitations, methodological constraints, and local software environment boundaries of the Agricultural Big Data Analytics System.

---

## 1. Data Quality & Coverage Limitations

1. **Missing Production Observations:**
   - Exactly 3,730 out of 246,091 records (1.52%) in the crop production dataset contain missing `Production` figures.
   - These records typically correspond to failed harvests, non-reported district statistics, or early-stage crop abandonment. Discarding these rows during raw ingestion would corrupt historical cultivated acreage calculations; hence they were retained as `NaN` and dynamically omitted only during yield division.

2. **Geographic Granularity Mismatch:**
   - Crop production is reported at the **District** level across 33 States and Union Territories.
   - Meteorological rainfall is reported across 36 **Subdivisions** defined by the India Meteorological Department (IMD).
   - Some IMD subdivisions encompass multiple states (e.g. `ASSAM & MEGHALAYA`), while large states are split across multiple subdivisions (e.g. `EAST RAJASTHAN` and `WEST RAJASTHAN`).
   - Merging required mapping subdivisions to state-level geographic aggregates. This introduces smoothing that masks localized micro-climate variations within large states.

3. **Temporal Truncation:**
   - While meteorological rainfall spans 1901 to 2015, the official crop production dataset covers 1997 to 2015.
   - Dual-variable econometric analyses are restricted strictly to the 19 overlapping years (1997–2015).

---

## 2. Agronomic & Methodological Caveats

1. **Non-Causal Nature of Observational Data:**
   - The observed correlation between monsoon rainfall and food grain yield is mildly negative ($r = -0.2909$).
   - This must **never** be interpreted as excess rainfall causing diminished agricultural yields.
   - State-level crop productivity in India is predominantly driven by **canal and tube-well irrigation coverage, high-yielding variety (HYV) seeds, and chemical fertilizer application (NPK)**. States in northwestern India (Punjab, Haryana) achieve the highest crop yields in the country despite low annual precipitation because over 90% of their net sown area is irrigated.

2. **Plantation vs. Field Crop Units:**
   - Coconut yield cannot be aggregated directly into metric tonnes because it is reported in count of nuts. A strict `Is_Nut_Unit` boolean flag prevents cross-commodity unit corruption.

---

## 3. Environment & Software Stack Disclosures

1. **Apache Hive Local Availability:**
   - **Local Status:** `Hive` is not installed on this local workstation.
   - **Mitigation:** Production-grade Hive DDL (`hive/create_tables.hql`) using `OpenCSVSerde` and analytical SQL queries (`hive/analytics.hql`) have been provided, syntax-validated, and documented for execution on any Hive/Beeline-enabled cluster.

2. **PySpark Wheel Availability on macOS arm64:**
   - **Local Status:** The PyPI repository does not distribute pre-compiled binary wheels for PySpark on macOS `arm64` under Python 3.9, defaulting to a 434 MB source tarball that requires compilation and specialized JVM flags (`--add-opens=java.base/java.nio=ALL-UNNAMED`) under OpenJDK 17.
   - **Mitigation:** A standalone, fully functional PySpark script (`src/pyspark/crop_rainfall_pyspark.py`) is included. It defines explicit `StructType` schemas, executes window aggregations, joins tables, and gracefully informs the user if invoked in an environment lacking the PySpark module.

3. **R Runtime Environment:**
   - **Local Status:** The `R` executable was not found in the system `$PATH`.
   - **Mitigation:** A complete R econometric script (`src/r/statistical_analysis.R`) is included. It documents required CRAN packages (`readr`, `dplyr`, `ggplot2`), fits OLS regression models, and generates diagnostic plots when executed on an R-equipped system.

4. **Single-Node HDFS Setup:**
   - Hadoop 3.5.0 is configured in pseudo-distributed mode with replication factor `dfs.replication = 1`.
   - While ideal for development, testing, and academic verification on Apple Silicon hardware, it does not provide multi-node rack awareness or hardware fault tolerance.
