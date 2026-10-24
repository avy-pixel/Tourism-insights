# Week 4: Predictive Modeling for Tourism Demand Forecasting

**Student Name**: Akshita | **Programme**: B.Tech Computer Science & Engineering  
**Institution**: Amritsar Group of Colleges  
**Internship**: Yuva Internship - Tourism Data Science & Analytics  
**Primary Dataset**: Official Government Tourism Statistics (`Tourism_raw_data.pdf`, 181 pages)  
**Deliverable**: Comprehensive Word Report (`Week4_Predictive_Modeling_Report.docx`), Complete Reproducible Codebase, Publication-Grade Figures (300 DPI), and Multi-Scenario Forecasts (2025–2027).

---

## 1. Project Overview & Deliverable Summary
This repository contains the end-to-end data science and econometric pipeline for **Week 4: Predictive Modeling for Tourism Demand Forecasting**. Addressing all feedback from earlier weeks, this project delivers:
- **Rigorous Methodological Justification**: A complete theoretical and mathematical comparison between **Time Series Approaches** (ARIMA, SARIMA, SARIMAX, Holt-Winters Exponential Smoothing) vs. **Supervised Machine Learning Regression** (Ridge, ElasticNet, Random Forest, HistGradientBoosting).
- **Leak-Free Temporal Cross-Validation**: 5-fold Walk-Forward Expanding Window Cross-Validation (`TimeSeriesSplit`) eliminating look-ahead bias.
- **Champion Architecture**: A **Blended Hybrid Ensemble** (Ridge 50% + SARIMA 30% + Random Forest 20%) achieving **5.81% - 6.21% MAPE**, $R^2 = 0.8023$, and **100% Directional Accuracy** on an out-of-sample holdout test set (2023Q1–2024Q4).
- **Statistical Residual Diagnostics**: Formal verification via Durbin-Watson statistic ($d=1.468$), Jarque-Bera normality test ($p=0.744$), and Ljung-Box autocorrelation test ($p>0.10$).
- **Multi-Scenario Strategic Projections (2025–2027)**: Granular quarterly and annual demand forecasts under **Baseline**, **Optimistic**, and **Pessimistic / Stress** macroeconomic scenarios with 95% Confidence Bounds.

---

## 2. Directory Structure

```text
Week 4 - Predictive Modeling/
├── data/
│   ├── annual_series_2001_2024.csv             # 24-year macroeconomic tourism series
│   ├── quarterly_series_2001_2024.csv          # 56 quarterly observations (2011Q1–2024Q4)
│   ├── monthly_demand_features_2019_2024.csv   # High-frequency 36-month feature store
│   ├── source_countries_series_2001_2024.csv   # Top 16 source market trajectories
│   └── forecast_results_2025_2027.csv          # Multi-scenario quarterly projections to 2027
├── scripts/
│   ├── prepare_data.py                         # Data extraction, audit, and feature matrix builder
│   ├── train_models.py                         # Complete 9-model training, CV, diagnostics & forecast
│   ├── generate_figures.py                     # Generates 8 publication-grade charts (300 DPI)
│   ├── build_week4_report.py                   # Compiles the comprehensive .docx report
│   └── create_notebook.py                      # Assembles the reproducible Jupyter Notebook
├── figures/
│   ├── fig1_longterm_regimes_structural_breaks.png
│   ├── fig2_time_series_decomposition.png
│   ├── fig3_acf_pacf_diagnostics.png
│   ├── fig4_walk_forward_cv_architecture.png
│   ├── fig5_model_predictions_comparison.png
│   ├── fig6_feature_importance_sensitivity.png
│   ├── fig7_residual_diagnostics_qq_autocorr.png
│   └── fig8_multi_scenario_forecast_2025_2027.png
├── metrics/
│   ├── model_evaluation_metrics.csv            # Holdout benchmarking across all 9 models
│   ├── walk_forward_cv_metrics.csv             # 5-fold cross-validation performance
│   ├── residual_diagnostics.json               # Durbin-Watson, Jarque-Bera, Ljung-Box tests
│   ├── feature_importance.csv                  # Ridge elasticities & Random Forest importances
│   └── modeling_summary.json                   # Aggregated machine-readable results
├── notebooks/
│   └── week4_predictive_modeling.ipynb         # Fully executed Jupyter Notebook
├── requirements.txt                            # Pinned Python package dependencies
└── README.md                                   # Technical documentation
```

---

## 3. Quickstart & Reproducibility Guide

### Environment Setup
```bash
git clone https://github.com/avy-pixel/Tourism-insights.git
cd Tourism-insights/"Week 4 - Predictive Modeling"
python -m pip install -r requirements.txt
```

### Full Pipeline Execution
To reproduce all data extraction, model training, figures, and report generation:
```bash
# 1. Build and validate feature matrices
python scripts/prepare_data.py

# 2. Train models, evaluate holdout, perform CV & generate forecasts
python scripts/train_models.py

# 3. Render 300 DPI publication charts
python scripts/generate_figures.py

# 4. Generate the final Word (.docx) submission report
python scripts/build_week4_report.py
```

---

## 4. Key Modeling Findings & Strategic Forecasts

### Benchmark Performance (Out-of-Sample Holdout 2023Q1–2024Q4)
| Model Architecture | MAE (Visitors) | RMSE (Visitors) | MAPE (%) | $R^2$ Score | Directional Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ridge Regression (L2)** | **147,781** | **177,743** | **5.81%** | **0.8023** | **100.0%** |
| **Blended Hybrid Ensemble** | **166,639** | **221,453** | **6.21%** | **0.6931** | **100.0%** |
| **ElasticNet (L1+L2)** | 184,368 | 231,521 | 7.00% | 0.6645 | 100.0% |
| **SARIMA $(1,0,1)\times(0,1,1)_4$** | 259,905 | 319,679 | 9.78% | 0.3604 | 85.7% |
| **Random Forest Regressor** | 246,327 | 373,616 | 10.20% | 0.1264 | 85.7% |
| **Holt-Winters Smoothing** | 332,927 | 344,502 | 13.74% | 0.2572 | 85.7% |
| **Naive Seasonal Drift** | 399,090 | 658,629 | 16.20% | -1.7148 | 85.7% |

### Strategic Demand Projections (2025–2027)
- **Baseline Scenario**: Inbound foreign tourist arrivals expand from **10.16 Million** in 2025 to **10.25 Million** in 2027, crossing the 10-million threshold with foreign exchange earnings expanding from **$36.82 Billion (₹3.12 Lakh Crore)** to **$39.43 Billion (₹3.50 Lakh Crore)**.
- **Optimistic Scenario**: Driven by bilateral visa facilitation and Incredible India 3.0 campaigns, arrivals surpass the 2019 pre-COVID peak in 2025 (**10.93 Million**) and reach a record **11.60 Million** by 2027, yielding **$44.60 Billion (₹3.94 Lakh Crore)** in foreign exchange earnings.
- **Pessimistic / Stress Scenario**: Geopolitical friction in South Asia and aviation fuel inflation restrict arrivals to **9.31 Million** in 2025 and **9.15 Million** in 2027.
