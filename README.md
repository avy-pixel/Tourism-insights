# Tourism Insights — Data Science & Predictive Analytics Internship

**Intern**: Akshita | B.Tech Computer Science & Engineering  
**Institution**: Amritsar Group of Colleges (Autonomous)  
**Project**: Yuva Internship — Tourism Data Science & Analytics  
**Repository**: [https://github.com/avy-pixel/Tourism-insights](https://github.com/avy-pixel/Tourism-insights)  
**Official Data Source**: Ministry of Tourism & Bureau of Immigration, Government of India (`Tourism_raw_data.pdf`, 181 pages)

---

## Executive Overview
This repository contains the complete 5-week deliverables for the Yuva Tourism Data Science Internship, establishing an end-to-end analytical pipeline from raw government statistics ingestion and audit, through exploratory data analysis, validation-first data cleaning, econometric time-series forecasting, to NLP sentiment analysis and aspect-based customer intelligence on tourist feedback.

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
- `Week4_Predictive_Modeling_Report.docx` — Comprehensive executive Word submission deliverable (1,014 KB).

### Week 5 — Sentiment Analysis on Tourist Reviews
- `Week 5 - Sentiment Analysis/` — Complete NLP sentiment analysis and aspect-based intelligence framework:
  - `data/` — 2,500 multi-touchpoint tourist reviews corpus, cleaned feature store, aspect summary, destination sentiment index, and model evaluation benchmarks.
  - `scripts/prepare_reviews_data.py` — Six-stage NLP preprocessing pipeline (contraction expansion, noise filtering, tokenization, negation scope tagging, POS-guided WordNet lemmatization).
  - `scripts/train_sentiment_models.py` — Lexicon (VADER, TextBlob) and Supervised ML (Multinomial Naive Bayes, Logistic Regression, Linear SVM, Blended Ensemble) benchmarking with 5-fold stratified cross-validation.
  - `scripts/generate_figures.py` — Renders eight publication-grade figures (300 DPI + lightweight JPGs under 1MB total).
  - `scripts/create_notebook.py` — Reproducible Jupyter Notebook generator.
  - `scripts/build_week5_report.py` — Automated compiler for the formal submission Word report.
  - `figures/` — Eight publication-grade figures (sentiment donut, dual word clouds, top n-grams, model benchmark bar chart, multi-panel confusion matrices, aspect scorecard, quarterly temporal trends, destination heatmap).
  - `metrics/` — Machine-readable evaluation metrics, per-class classification reports, and 3 detailed worked walkthrough examples.
  - `notebooks/week5_sentiment_analysis.ipynb` — Executed, self-contained Jupyter Notebook.
  - `Report/Week5_Sentiment_Analysis_Report.docx` — Formatted Word report (723.5 KB, strictly under portal limit).
  - `Report/Week5_Sentiment_Analysis_Report.md` — Complete markdown technical report.
  - `requirements.txt` — Pinned Python package dependencies.
- `Week5_Sentiment_Analysis_Report.docx` — Formal technical report deliverable (723.5 KB).

---

## Modeling Benchmark Summary

### Week 4: Demand Forecasting Holdout (2023Q1–2024Q4)
| Rank | Model Architecture | Family | MAE (Visitors) | RMSE (Visitors) | MAPE (%) | $R^2$ Score | Directional Accuracy |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **Ridge Regression (L2)** | Regularized ML | **147,781** | **177,743** | **5.81%** | **0.8023** | **100.0%** |
| **2** | **Blended Hybrid Ensemble** | Meta-Stacking | **166,639** | **221,453** | **6.21%** | **0.6931** | **100.0%** |
| **3** | **ElasticNet (L1 + L2)** | Regularized ML | 184,368 | 231,521 | 7.00% | 0.6645 | 100.0% |
| **4** | **SARIMA $(1,0,1)\times(0,1,1)_4$** | Time Series | 259,905 | 319,679 | 9.78% | 0.3604 | 85.7% |
| **5** | **Random Forest Regressor** | Tree Ensemble | 246,327 | 373,616 | 10.20% | 0.1264 | 85.7% |
| **6** | **Holt-Winters Smoothing** | Time Series | 332,927 | 344,502 | 13.74% | 0.2572 | 85.7% |
| **7** | **Naive Seasonal Drift** | Baseline | 399,090 | 658,629 | 16.20% | -1.7148 | 85.7% |

### Week 5: Sentiment Classification Holdout (500 Reviews)
| Model Architecture | Accuracy (%) | Balanced Acc (%) | Macro Precision (%) | Macro Recall (%) | Macro F1 (%) | Cohen's Kappa (κ) | 5-Fold Stratified CV |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Blended NLP Ensemble (Champion)** | **96.60%** | **96.05%** | **96.80%** | **96.05%** | **96.26%** | **0.9429** | **Ensemble Blend** |
| **TF-IDF + Logistic Regression (L2)** | 96.60% | 96.05% | 96.80% | 96.05% | 96.26% | 0.9429 | 96.24% ± 0.30% |
| **TF-IDF + Multinomial Naive Bayes** | 96.60% | 96.10% | 96.80% | 96.10% | 96.30% | 0.9429 | 96.15% ± 0.41% |
| **TF-IDF + Linear Support Vector Machine** | 96.60% | 95.95% | 96.75% | 95.95% | 96.14% | 0.9429 | 95.55% ± 0.75% |
| **NLTK VADER (Rule-Based)** | 72.40% | 69.15% | 64.20% | 69.15% | 55.72% | 0.5069 | N/A (Unsupervised) |
| **TextBlob (Pattern-Based)** | 68.20% | 66.40% | 61.50% | 66.40% | 59.59% | 0.4485 | N/A (Unsupervised) |

---

## Aspect-Based Sentiment Scores (Net Sentiment Score: NSS = %Pos - %Neg)
1. **Heritage & Cultural Experience**: NSS = **+94.2** (High delight in architectural majesty and spiritual reverence)
2. **Hospitality & Staff Behavior**: NSS = **+48.6** (Courteous registered guides contrasted by tout harassment)
3. **Cleanliness & Hygiene**: NSS = **+42.1** (Clean central monuments, but unhygienic washroom facilities near exits)
4. **Accessibility & Infrastructure**: NSS = **+38.5** (Good metro/shuttle transit, but poor elderly wheelchair ramps)
5. **Value for Money**: NSS = **+18.4** (Extreme friction over 15x dual pricing for international tourists)
6. **Crowd Management & Queuing**: NSS = **-18.4** (Systemic failure; 2–3 hour queues, bottlenecks, lack of shade)

---

## Multi-Scenario Demand Forecast (2025–2027)
- **Baseline Scenario**: Inbound foreign tourist arrivals expand from **10.16 Million** in 2025 to **10.25 Million** in 2027, crossing the 10-million threshold with foreign exchange earnings expanding from **$36.82 Billion (₹3.12 Lakh Crore)** to **$39.43 Billion (₹3.50 Lakh Crore)**.
- **Optimistic Scenario**: Driven by bilateral visa facilitation and Incredible India 3.0 campaigns, arrivals surpass the 2019 pre-COVID peak in 2025 (**10.93 Million**) and reach a record **11.60 Million** by 2027, yielding **$44.60 Billion (₹3.94 Lakh Crore)** in foreign exchange earnings.
- **Pessimistic / Stress Scenario**: Geopolitical friction in South Asia and aviation fuel inflation restrict arrivals to **9.31 Million** in 2025 and **9.15 Million** in 2027.

---

## Reproducibility
To reproduce the complete pipeline across all weeks:
```bash
# Week 4: Demand Forecasting
pip install -r "Week 4 - Predictive Modeling/requirements.txt"
python "Week 4 - Predictive Modeling/scripts/prepare_data.py"
python "Week 4 - Predictive Modeling/scripts/train_models.py"
python "Week 4 - Predictive Modeling/scripts/generate_figures.py"
python "Week 4 - Predictive Modeling/scripts/build_week4_report.py"

# Week 5: Sentiment Analysis
pip install -r "Week 5 - Sentiment Analysis/requirements.txt"
python "Week 5 - Sentiment Analysis/scripts/prepare_reviews_data.py"
python "Week 5 - Sentiment Analysis/scripts/train_sentiment_models.py"
python "Week 5 - Sentiment Analysis/scripts/generate_figures.py"
python "Week 5 - Sentiment Analysis/scripts/create_notebook.py"
python "Week 5 - Sentiment Analysis/scripts/build_week5_report.py"
```
