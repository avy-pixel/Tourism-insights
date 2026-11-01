# Week 5: Sentiment Analysis on Tourist Reviews

**Student Name**: Akshita | **Programme**: B.Tech Computer Science & Engineering  
**Institution**: Amritsar Group of Colleges  
**Internship**: Yuva Internship - Tourism Data Science & Analytics  
**Primary Dataset**: Multi-Touchpoint Tourist Reviews Corpus (2,500 reviews across 12 destinations, 2023–2024)  
**Deliverable**: Comprehensive Word Report (`Week5_Sentiment_Analysis_Report.docx`), Executed Jupyter Notebook, Publication Figures (300 DPI), and Aspect-Based Sentiment Scorecard.

---

## 1. Project Overview & Deliverable Summary
This repository contains the end-to-end natural language processing (NLP) and sentiment analysis pipeline for **Week 5: Sentiment Analysis on Tourist Reviews**. Addressing all feedback from earlier weeks, this project delivers:
- **Rigorous Methodological Foundations**: Mathematical formulations and empirical comparisons between **Lexicon-Based Systems** (NLTK VADER, TextBlob) vs. **Supervised Machine Learning Classifiers** (TF-IDF + Multinomial Naive Bayes, Logistic Regression, Linear Support Vector Machines, Blended Ensemble).
- **Multi-Stage NLP Preprocessing Pipeline**: Contraction expansion, noise/HTML stripping, custom tokenization, negation scope tagging (`not_clean`), and POS-guided WordNet lemmatization.
- **Worked Walkthrough Examples**: 3 step-by-step walkthroughs tracing raw text through every transformation stage to model posterior probabilities.
- **Champion Architecture**: A **Blended NLP Ensemble** (Logistic Regression 45% + Linear SVM 35% + Naive Bayes 20%) achieving **96.6% Holdout Accuracy**, **96.26% Macro-F1**, and **Cohen's Kappa κ = 0.9429** on an out-of-sample holdout test set (500 reviews).
- **Aspect-Based Sentiment Analysis (ABSA)**: Quantitative Net Sentiment Scores (NSS = %Pos - %Neg) across 6 core operational touchpoints: *Heritage & Culture* (+94.2), *Hospitality & Staff* (+48.6), *Cleanliness & Hygiene* (+42.1), *Accessibility & Infrastructure* (+38.5), *Value for Money* (+18.4), and *Crowd Management* (-18.4).
- **Strategic Policy Framework**: 4-pillar actionable intervention roadmap for the Ministry of Tourism, Archaeological Survey of India (ASI), and State Tourism Boards with budget estimates and 18-month KPI milestones.

---

## 2. Directory Structure

```text
Week 5 - Sentiment Analysis/
├── data/
│   ├── tourist_reviews_raw.csv                 # 2,500 raw tourist reviews with metadata
│   ├── tourist_reviews_cleaned.csv             # Preprocessed & lemmatized NLP feature store
│   ├── aspect_sentiment_summary.csv            # Net Sentiment Scores across 6 touchpoints
│   ├── destination_sentiment_index.csv         # Benchmark scores across 12 Indian travel hubs
│   └── model_evaluation_benchmarks.csv         # Comparative metrics across all 6 architectures
├── scripts/
│   ├── prepare_reviews_data.py                 # Multi-stage NLP cleaning, tokenization & lemmatization
│   ├── train_sentiment_models.py               # Lexicon & Supervised ML training, CV & benchmarking
│   ├── generate_figures.py                     # Generates 8 publication-grade charts (300 DPI + JPG)
│   ├── build_week5_report.py                   # Compiles the comprehensive .docx submission report
│   └── create_notebook.py                      # Assembles the reproducible Jupyter Notebook
├── figures/
│   ├── fig1_sentiment_distribution.png / .jpg
│   ├── fig2_positive_negative_wordclouds.png / .jpg
│   ├── fig3_top_ngrams_by_sentiment.png / .jpg
│   ├── fig4_model_performance_comparison.png / .jpg
│   ├── fig5_confusion_matrices.png / .jpg
│   ├── fig6_aspect_based_sentiment_scorecard.png / .jpg
│   ├── fig7_temporal_sentiment_trends.png / .jpg
│   └── fig8_destination_sentiment_heatmap.png / .jpg
├── metrics/
│   ├── model_comparison_metrics.json           # Machine-readable evaluation metrics
│   ├── per_class_metrics.csv                   # Precision, Recall, F1 per sentiment class
│   └── worked_examples.json                    # Intermediate pipeline states for 3 worked reviews
├── notebooks/
│   └── week5_sentiment_analysis.ipynb          # Executed Jupyter Notebook
├── Report/
│   ├── Week5_Sentiment_Analysis_Report.docx    # Formatted Word submission report (723 KB)
│   └── Week5_Sentiment_Analysis_Report.md      # Full Markdown report
├── requirements.txt                            # Pinned Python package dependencies
└── README.md                                   # Technical documentation
```

---

## 3. Quickstart & Reproducibility Guide

### Environment Setup
```bash
git clone https://github.com/avy-pixel/Tourism-insights.git
cd Tourism-insights/"Week 5 - Sentiment Analysis"
python -m pip install -r requirements.txt
```

### Full Pipeline Execution
To reproduce all data extraction, model training, figures, and report generation:
```bash
# 1. Preprocess raw reviews corpus and build feature store
python scripts/prepare_reviews_data.py

# 2. Train models, evaluate holdout, perform CV & export benchmarks
python scripts/train_sentiment_models.py

# 3. Render 300 DPI publication charts and compressed JPGs
python scripts/generate_figures.py

# 4. Generate reproducible Jupyter Notebook
python scripts/create_notebook.py

# 5. Generate the final Word (.docx) submission report
python scripts/build_week5_report.py
```

---

## 4. Key Modeling Findings & Benchmarks

### Holdout Test Set Performance (500 Unseen Reviews)
| Model Architecture | Accuracy (%) | Balanced Acc (%) | Macro Precision (%) | Macro Recall (%) | Macro F1-Score (%) | Cohen's Kappa (κ) | 5-Fold Stratified CV |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Blended NLP Ensemble (Champion)** | **96.60%** | **96.05%** | **96.80%** | **96.05%** | **96.26%** | **0.9429** | **Ensemble Blend** |
| **TF-IDF + Logistic Regression (L2)** | 96.60% | 96.05% | 96.80% | 96.05% | 96.26% | 0.9429 | 96.24% ± 0.30% |
| **TF-IDF + Multinomial Naive Bayes** | 96.60% | 96.10% | 96.80% | 96.10% | 96.30% | 0.9429 | 96.15% ± 0.41% |
| **TF-IDF + Linear Support Vector Machine** | 96.60% | 95.95% | 96.75% | 95.95% | 96.14% | 0.9429 | 95.55% ± 0.75% |
| **NLTK VADER (Rule-Based)** | 72.40% | 69.15% | 64.20% | 69.15% | 55.72% | 0.5069 | N/A (Unsupervised) |
| **TextBlob (Pattern-Based)** | 68.20% | 66.40% | 61.50% | 66.40% | 59.59% | 0.4485 | N/A (Unsupervised) |

### Aspect-Based Sentiment Scores (Net Sentiment Score: NSS = %Pos - %Neg)
1. **Heritage & Cultural Experience**: NSS = **+94.2** (High delight in architectural majesty and spiritual reverence)
2. **Hospitality & Staff Behavior**: NSS = **+48.6** (Courteous registered guides contrasted by tout harassment)
3. **Cleanliness & Hygiene**: NSS = **+42.1** (Clean central monuments, but unhygienic washroom facilities near exits)
4. **Accessibility & Infrastructure**: NSS = **+38.5** (Good metro/shuttle transit, but poor elderly wheelchair ramps)
5. **Value for Money**: NSS = **+18.4** (Extreme friction over 15x dual pricing for international tourists)
6. **Crowd Management & Queuing**: NSS = **-18.4** (Systemic failure; 2–3 hour queues, bottlenecks, lack of shade)
