# Tourism Insights — Data Science & Predictive Analytics Internship

**Intern**: Akshita | B.Tech Computer Science & Engineering  
**Institution**: Amritsar Group of Colleges (Autonomous)  
**Project**: Yuva Internship — Tourism Data Science & Analytics  
**Repository**: [https://github.com/avy-pixel/Tourism-insights](https://github.com/avy-pixel/Tourism-insights)  
**Official Data Source**: Ministry of Tourism & Bureau of Immigration, Government of India (`Tourism_raw_data.pdf`, 181 pages)

---

## Executive Overview
This repository contains the complete 4-week deliverables for the Yuva Tourism Data Science Internship, establishing an end-to-end analytical pipeline from raw government statistics ingestion and audit, through exploratory data analysis, validation-first data cleaning, to econometric time-series forecasting and machine learning demand modeling.

---

## Project Structure & Weekly Deliverables

### Week 1 — Data Collection & Strategy Planning
- `Week 1 - Data Collection/Data/` — Original tourism source PDF (`Tourism_raw_data.pdf`, 181 pages).
- `Week 1 - Data Collection/Report/` — Comprehensive data acquisition strategy, quality frameworks, and worked examples.

### Week 2 — Exploratory Data Analysis (EDA)
- `Week 2 -EDA/data/` — Six curated baseline CSV datasets extracted from official statistics.
- `Week 2 -EDA/notebooks/week2_eda.ipynb` — Reproducible Jupyter Notebook for exploratory statistical profiling.
- `Week 2 -EDA/visualizations/` — Ten publication-grade analytical charts (300 DPI) examining long-term inbound trajectories, origin-country market concentration, seasonality bimodality, and foreign exchange earnings decoupling.
- `Week 2 -EDA/Report/Week2_EDA_Report_Akshita.md` — Detailed technical report documenting distributions, hypothesis testing, and economic implications.

### Week 3 — Data Cleaning & Preprocessing
- `tourism_cleaning/` — Modular, reproducible cleaning pipeline:
  - `clean_tourism.py` — Automated ingestion, schema sanitization, deductive identity repair, and validation script.
  - `cleaned_data/` — Six analysis-ready CSV datasets.
  - `data_quality_log.csv` & `log.json` — 47 automated validation checks (PASS/FAIL audits).
  - `figures/` — Cleaning figures and outlier diagnostic charts.
- `Week3_Data_Cleaning_Report.docx` — Formal technical report on structural missingness, identity repair, and definition break harmonization.

### Week 4 — Predictive Modeling for Tourism Demand Forecasting
- `Week 4 - Predictive Modeling/` — Complete predictive modeling framework:
  - `data/` — Annual series (2001–2024), quarterly series (56 quarters), monthly feature store (36 months), and multi-scenario forecasts.
  - `scripts/prepare_data.py` — Ingestion and feature store creation script.
  - `scripts/train_models.py` — Model training, walk-forward cross-validation, residual diagnostics, and multi-scenario forecasting engine.
  - `scripts/generate_figures.py` — Renders eight publication-grade 300 DPI visualization figures.
  - `scripts/build_week4_report.py` — Automated compiler for the submission Word report.
  - `notebooks/week4_predictive_modeling.ipynb` — Interactive, fully documented Jupyter Notebook.
  - `figures/` — Eight publication-grade figures (STL decomposition, ACF/PACF, CV architecture, holdout curves, feature importance, residual diagnostics, multi-scenario forecast).
  - `metrics/` — Machine-readable model benchmark CSV/JSON files.
  - `requirements.txt` — Pinned Python package dependencies.
- `Week4_Predictive_Modeling_Report.docx` — Comprehensive 2.2 MB executive Word submission deliverable.

---

## Modeling Benchmark Summary (Week 4 Holdout 2023Q1–2024Q4)

| Rank | Model Architecture | Family | MAE (Visitors) | RMSE (Visitors) | MAPE (%) | R² Score | Directional Accuracy |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **Ridge Regression (L2)** | Regularized ML | **147,781** | **177,743** | **5.81%** | **0.8023** | **100.0%** |
| **2** | **Blended Hybrid Ensemble** | Meta-Stacking | **166,639** | **221,453** | **6.21%** | **0.6931** | **100.0%** |
| **3** | **ElasticNet (L1 + L2)** | Regularized ML | 184,368 | 231,521 | 7.00% | 0.6645 | 100.0% |
| **4** | **SARIMA $(1,0,1)\times(0,1,1)_4$** | Time Series | 259,905 | 319,679 | 9.78% | 0.3604 | 85.7% |
| **5** | **Random Forest Regressor** | Tree Ensemble | 246,327 | 373,616 | 10.20% | 0.1264 | 85.7% |
| **6** | **Holt-Winters Smoothing** | Time Series | 332,927 | 344,502 | 13.74% | 0.2572 | 85.7% |
| **7** | **Naive Seasonal Drift** | Baseline | 399,090 | 658,629 | 16.20% | -1.7148 | 85.7% |

---

## Multi-Scenario Demand Forecast (2025–2027)

- **Baseline Scenario**: Inbound foreign tourist arrivals expand from **10.16 Million** in 2025 to **10.25 Million** in 2027, crossing the 10-million threshold with foreign exchange earnings expanding from **$36.82 Billion (₹3.12 Lakh Crore)** to **$39.43 Billion (₹3.50 Lakh Crore)**.
- **Optimistic Scenario**: Driven by bilateral visa facilitation and Incredible India 3.0 campaigns, arrivals surpass the 2019 pre-COVID peak in 2025 (**10.93 Million**) and reach a record **11.60 Million** by 2027, yielding **$44.60 Billion (₹3.94 Lakh Crore)** in foreign exchange earnings.
- **Pessimistic / Stress Scenario**: Geopolitical friction in South Asia and aviation fuel inflation restrict arrivals to **9.31 Million** in 2025 and **9.15 Million** in 2027.

---

## Reproducibility
To reproduce the full pipeline:
```bash
pip install -r "Week 4 - Predictive Modeling/requirements.txt"

# Run data preparation, model training, and figure generation
python "Week 4 - Predictive Modeling/scripts/prepare_data.py"
python "Week 4 - Predictive Modeling/scripts/train_models.py"
python "Week 4 - Predictive Modeling/scripts/generate_figures.py"
python "Week 4 - Predictive Modeling/scripts/build_week4_report.py"
```
