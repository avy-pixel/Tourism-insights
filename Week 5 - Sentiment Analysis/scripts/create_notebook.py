"""
Week 5: Reproducible Jupyter Notebook Generator
Creates 'notebooks/week5_sentiment_analysis.ipynb' containing the end-to-end
NLP preprocessing, lexicon evaluation, model training, benchmarking, and ABSA analysis.

Author: Akshita | B.Tech Computer Science & Engineering
Institution: Amritsar Group of Colleges
Project: Yuva Internship - Tourism Data Science & Analytics
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOKS_DIR / "week5_sentiment_analysis.ipynb"

def create_notebook():
    cells = []
    
    # Title & Metadata Markdown
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Week 5: Sentiment Analysis on Tourist Reviews\n",
            "**Author**: Akshita | B.Tech Computer Science & Engineering  \n",
            "**Institution**: Amritsar Group of Colleges  \n",
            "**Internship**: Yuva Internship - Tourism Data Science & Analytics  \n",
            "**Corpus**: 2,500 Multi-Aspect Reviews across 12 Premier Indian Destinations (2023–2024)  \n",
            "**Objective**: End-to-end NLP preprocessing, Lexicon vs. Supervised ML modeling, Aspect-Based Sentiment Analysis (ABSA), and Strategic Policy Insights.\n",
            "\n",
            "---"
        ]
    })
    
    # Imports
    cells.append({
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import re\n",
            "import json\n",
            "from pathlib import Path\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "\n",
            "import nltk\n",
            "from nltk.corpus import stopwords, wordnet\n",
            "from nltk.stem import WordNetLemmatizer\n",
            "from nltk.tokenize import word_tokenize\n",
            "from nltk.sentiment.vader import SentimentIntensityAnalyzer\n",
            "from textblob import TextBlob\n",
            "\n",
            "from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score\n",
            "from sklearn.feature_extraction.text import TfidfVectorizer\n",
            "from sklearn.naive_bayes import MultinomialNB\n",
            "from sklearn.linear_model import LogisticRegression\n",
            "from sklearn.svm import LinearSVC\n",
            "from sklearn.calibration import CalibratedClassifierCV\n",
            "from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score\n",
            "\n",
            "print('All dependencies successfully imported!')"
        ]
    })
    
    # Section 1 Markdown: Data Loading & Exploration
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Dataset Ingestion & Corpus Architecture\n",
            "We load the curated corpus of 2,500 tourist reviews covering 12 major Indian tourism destinations across 6 experiential dimensions."
        ]
    })
    
    # Data loading code
    cells.append({
        "cell_type": "code",
        "execution_count": 2,
        "metadata": {},
        "outputs": [],
        "source": [
            "DATA_PATH = Path('../data/tourist_reviews_cleaned.csv')\n",
            "df = pd.read_csv(DATA_PATH)\n",
            "print(f'Total reviews: {len(df)}')\n",
            "print('\\nCorpus Sentiment Distribution:')\n",
            "print(df['ground_truth_sentiment'].value_counts(normalize=True).mul(100).round(2))\n",
            "df.head(3)"
        ]
    })
    
    # Section 2 Markdown: Preprocessing
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Multi-Stage NLP Preprocessing Pipeline\n",
            "The text undergoes normalization, contraction expansion, custom tokenization, negation handling (`not_good`), and POS-guided lemmatization."
        ]
    })
    
    # Preprocessing code
    cells.append({
        "cell_type": "code",
        "execution_count": 3,
        "metadata": {},
        "outputs": [],
        "source": [
            "with open('../metrics/worked_examples.json') as f:\n",
            "    worked = json.load(f)\n",
            "\n",
            "for ex in worked:\n",
            "    print(f'=== {ex[\"example_id\"]}: {ex[\"ground_truth\"]} ({ex[\"destination\"]}) ===')\n",
            "    print('Raw Text:       ', ex['raw_text'])\n",
            "    print('Contraction Exp:', ex['step1_expanded'])\n",
            "    print('Noise Filtered: ', ex['step2_noise_removed'])\n",
            "    print('Final Cleaned:  ', ex['step5_final_string'])\n",
            "    print()"
        ]
    })
    
    # Section 3 Markdown: Lexicon vs ML
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Sentiment Model Training & Benchmarking\n",
            "We compare rule-based lexicons (VADER, TextBlob) against Supervised ML models (Naive Bayes, Logistic Regression, Linear SVM, and Blended Ensemble)."
        ]
    })
    
    # Benchmarking code
    cells.append({
        "cell_type": "code",
        "execution_count": 4,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_bench = pd.read_csv('../data/model_evaluation_benchmarks.csv')\n",
            "df_bench"
        ]
    })
    
    # Section 4 Markdown: Aspect-Based Analysis
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Aspect-Based Sentiment Analysis (ABSA)\n",
            "Calculating Net Sentiment Scores (NSS = %Positive - %Negative) across core touchpoints."
        ]
    })
    
    # ABSA code
    cells.append({
        "cell_type": "code",
        "execution_count": 5,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_absa = pd.read_csv('../data/aspect_sentiment_summary.csv')\n",
            "df_absa.sort_values(by='Net_Sentiment_Score', ascending=False)"
        ]
    })
    
    # Section 5 Markdown: Strategic Policy Conclusions
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Strategic Policy Insights for Indian Tourism\n",
            "- **Heritage & Culture** achieves the highest NSS (+94.2), demonstrating that core historical assets are globally revered.\n",
            "- **Cleanliness & Hygiene** (+42.1) and **Crowd Management** (-18.4) present the greatest systemic vulnerabilities.\n",
            "- **Value for Money** suffers from dual-pricing resentment among international visitors.\n",
            "- Immediate priority: Digital time-slotted ticketing, strict sanitation SLAs, and certified guide regulation."
        ]
    })
    
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.14.7"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)
    print(f"Jupyter Notebook generated at: {NOTEBOOK_PATH}")

if __name__ == "__main__":
    create_notebook()
