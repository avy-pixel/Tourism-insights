"""
Week 5: Sentiment Analysis Model Training, Benchmarking & Diagnostics
Trains and benchmarks Lexicon-based (VADER, TextBlob) and Supervised ML
(Multinomial Naive Bayes, Logistic Regression, LinearSVC, Blended Ensemble)
models on the tourism reviews corpus using leak-free train/test splitting.

Author: Akshita | B.Tech Computer Science & Engineering
Institution: Amritsar Group of Colleges
Project: Yuva Internship - Tourism Data Science & Analytics
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, cohen_kappa_score, balanced_accuracy_score
)
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
METRICS_DIR = BASE_DIR / "metrics"
DATA_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

# Sentiment mapping
CLASS_LABELS = ["Negative", "Neutral", "Positive"]

def run_vader(texts):
    """Evaluates NLTK VADER sentiment analyzer on a collection of texts."""
    sia = SentimentIntensityAnalyzer()
    preds = []
    compounds = []
    for t in texts:
        scores = sia.polarity_scores(t)
        comp = scores['compound']
        compounds.append(comp)
        if comp >= 0.05:
            preds.append("Positive")
        elif comp <= -0.05:
            preds.append("Negative")
        else:
            preds.append("Neutral")
    return np.array(preds), np.array(compounds)

def run_textblob(texts):
    """Evaluates TextBlob pattern analyzer on a collection of texts."""
    preds = []
    polarities = []
    subjectivities = []
    for t in texts:
        blob = TextBlob(t)
        pol = blob.sentiment.polarity
        subj = blob.sentiment.subjectivity
        polarities.append(pol)
        subjectivities.append(subj)
        if pol > 0.10:
            preds.append("Positive")
        elif pol < -0.05:
            preds.append("Negative")
        else:
            preds.append("Neutral")
    return np.array(preds), np.array(polarities), np.array(subjectivities)

def calculate_metrics(y_true, y_pred, model_name):
    """Computes exhaustive classification metrics."""
    acc = accuracy_score(y_true, y_pred)
    bal_acc = balanced_accuracy_score(y_true, y_pred)
    p_macro = precision_score(y_true, y_pred, labels=CLASS_LABELS, average='macro', zero_division=0)
    p_wt = precision_score(y_true, y_pred, labels=CLASS_LABELS, average='weighted', zero_division=0)
    r_macro = recall_score(y_true, y_pred, labels=CLASS_LABELS, average='macro', zero_division=0)
    r_wt = recall_score(y_true, y_pred, labels=CLASS_LABELS, average='weighted', zero_division=0)
    f1_macro = f1_score(y_true, y_pred, labels=CLASS_LABELS, average='macro', zero_division=0)
    f1_wt = f1_score(y_true, y_pred, labels=CLASS_LABELS, average='weighted', zero_division=0)
    kappa = cohen_kappa_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=CLASS_LABELS).tolist()
    
    # Per-class breakdown
    report = classification_report(y_true, y_pred, labels=CLASS_LABELS, output_dict=True, zero_division=0)
    
    return {
        "model": model_name,
        "accuracy": round(acc * 100, 2),
        "balanced_accuracy": round(bal_acc * 100, 2),
        "precision_macro": round(p_macro * 100, 2),
        "precision_weighted": round(p_wt * 100, 2),
        "recall_macro": round(r_macro * 100, 2),
        "recall_weighted": round(r_wt * 100, 2),
        "f1_macro": round(f1_macro * 100, 2),
        "f1_weighted": round(f1_wt * 100, 2),
        "cohen_kappa": round(kappa, 4),
        "confusion_matrix": cm,
        "class_breakdown": {
            cls: {
                "precision": round(report[cls]["precision"] * 100, 2),
                "recall": round(report[cls]["recall"] * 100, 2),
                "f1_score": round(report[cls]["f1-score"] * 100, 2),
                "support": int(report[cls]["support"])
            }
            for cls in CLASS_LABELS
        }
    }

def main():
    print("=" * 80)
    print("WEEK 5: SENTIMENT ANALYSIS MODEL TRAINING & BENCHMARKING")
    print("=" * 80)
    
    # 1. Load Data
    cleaned_path = DATA_DIR / "tourist_reviews_cleaned.csv"
    df = pd.read_csv(cleaned_path)
    print(f"[1/5] Loaded cleaned corpus: {len(df)} reviews.")
    
    # 2. Stratified Train-Test Split (80/20)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df["raw_text"], df["ground_truth_sentiment"],
        test_size=0.20, random_state=42, stratify=df["ground_truth_sentiment"]
    )
    X_train_clean, X_test_clean = df.loc[X_train_raw.index, "cleaned_text"], df.loc[X_test_raw.index, "cleaned_text"]
    
    print(f"[2/5] Stratified split: {len(X_train_raw)} train samples, {len(X_test_raw)} holdout test samples.")
    print("      Class counts in Test Set:", dict(y_test.value_counts()))
    
    # 3. Benchmark Lexicon Models (Evaluated on Holdout Test Set)
    print("[3/5] Evaluating Lexicon-Based Approaches...")
    vader_preds, vader_compounds = run_vader(X_test_raw)
    vader_res = calculate_metrics(y_test, vader_preds, "NLTK VADER (Rule-Based)")
    
    tb_preds, tb_polarities, tb_subjectivities = run_textblob(X_test_raw)
    tb_res = calculate_metrics(y_test, tb_preds, "TextBlob (Pattern-Based)")
    
    print(f"      -> VADER: Accuracy = {vader_res['accuracy']}% | Macro F1 = {vader_res['f1_macro']}% | Kappa = {vader_res['cohen_kappa']}")
    print(f"      -> TextBlob: Accuracy = {tb_res['accuracy']}% | Macro F1 = {tb_res['f1_macro']}% | Kappa = {tb_res['cohen_kappa']}")
    
    # 4. Supervised ML Pipelines (TF-IDF + ML Classifiers)
    print("[4/5] Training Supervised Machine Learning Models...")
    
    # Build TF-IDF Feature Representation
    tfidf = TfidfVectorizer(
        max_features=2500,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2
    )
    X_train_vec = tfidf.fit_transform(X_train_clean)
    X_test_vec = tfidf.transform(X_test_clean)
    print(f"      -> TF-IDF Matrix Shape: {X_train_vec.shape} (Vocabulary: {len(tfidf.vocabulary_)} features)")
    
    # Model 1: Multinomial Naive Bayes
    nb_clf = MultinomialNB(alpha=0.5)
    nb_clf.fit(X_train_vec, y_train)
    nb_preds = nb_clf.predict(X_test_vec)
    nb_res = calculate_metrics(y_test, nb_preds, "TF-IDF + Multinomial Naive Bayes")
    
    # Model 2: Logistic Regression (L2 Regularized)
    lr_clf = LogisticRegression(C=2.0, max_iter=1000, class_weight='balanced', random_state=42)
    lr_clf.fit(X_train_vec, y_train)
    lr_preds = lr_clf.predict(X_test_vec)
    lr_res = calculate_metrics(y_test, lr_preds, "TF-IDF + Logistic Regression (L2)")
    
    # Model 3: Linear Support Vector Classifier (LinearSVC)
    svm_clf = LinearSVC(C=1.0, class_weight='balanced', random_state=42, max_iter=2000)
    calibrated_svm = CalibratedClassifierCV(svm_clf, cv=5)
    calibrated_svm.fit(X_train_vec, y_train)
    svm_preds = calibrated_svm.predict(X_test_vec)
    svm_res = calculate_metrics(y_test, svm_preds, "TF-IDF + Linear Support Vector Machine")
    
    # Model 4: Hybrid Ensemble (Blended Probabilities)
    prob_nb = nb_clf.predict_proba(X_test_vec)
    prob_lr = lr_clf.predict_proba(X_test_vec)
    prob_svm = calibrated_svm.predict_proba(X_test_vec)
    
    # Blended weights: 45% Logistic Regression + 35% SVM + 20% Naive Bayes
    blended_probs = 0.45 * prob_lr + 0.35 * prob_svm + 0.20 * prob_nb
    class_order = lr_clf.classes_
    ensemble_preds = class_order[np.argmax(blended_probs, axis=1)]
    ensemble_res = calculate_metrics(y_test, ensemble_preds, "Blended NLP Ensemble (Champion)")
    
    # 5-Fold Stratified Cross-Validation on Training Set
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_lr = cross_val_score(lr_clf, X_train_vec, y_train, cv=skf, scoring='f1_macro')
    cv_svm = cross_val_score(calibrated_svm, X_train_vec, y_train, cv=skf, scoring='f1_macro')
    cv_nb = cross_val_score(nb_clf, X_train_vec, y_train, cv=skf, scoring='f1_macro')
    
    lr_res["cv_f1_macro_mean"] = round(cv_lr.mean() * 100, 2)
    lr_res["cv_f1_macro_std"] = round(cv_lr.std() * 100, 2)
    svm_res["cv_f1_macro_mean"] = round(cv_svm.mean() * 100, 2)
    svm_res["cv_f1_macro_std"] = round(cv_svm.std() * 100, 2)
    nb_res["cv_f1_macro_mean"] = round(cv_nb.mean() * 100, 2)
    nb_res["cv_f1_macro_std"] = round(cv_nb.std() * 100, 2)
    
    print(f"      -> Naive Bayes: Accuracy = {nb_res['accuracy']}% | Macro F1 = {nb_res['f1_macro']}% | 5-Fold CV = {nb_res['cv_f1_macro_mean']} +/- {nb_res['cv_f1_macro_std']}%")
    print(f"      -> Logistic Regression: Accuracy = {lr_res['accuracy']}% | Macro F1 = {lr_res['f1_macro']}% | 5-Fold CV = {lr_res['cv_f1_macro_mean']} +/- {lr_res['cv_f1_macro_std']}%")
    print(f"      -> Linear SVM: Accuracy = {svm_res['accuracy']}% | Macro F1 = {svm_res['f1_macro']}% | 5-Fold CV = {svm_res['cv_f1_macro_mean']} +/- {svm_res['cv_f1_macro_std']}%")
    print(f"      -> Blended Ensemble: Accuracy = {ensemble_res['accuracy']}% | Macro F1 = {ensemble_res['f1_macro']}% | Kappa = {ensemble_res['cohen_kappa']}")
    
    # 5. Export Metrics and Summaries
    print("[5/5] Exporting Benchmarking Tables & Confusion Matrices...")
    all_results = [vader_res, tb_res, nb_res, lr_res, svm_res, ensemble_res]
    
    # Benchmark table
    benchmark_rows = []
    for r in all_results:
        benchmark_rows.append({
            "Model Architecture": r["model"],
            "Accuracy (%)": r["accuracy"],
            "Balanced Acc (%)": r["balanced_accuracy"],
            "Macro Precision (%)": r["precision_macro"],
            "Macro Recall (%)": r["recall_macro"],
            "Macro F1-Score (%)": r["f1_macro"],
            "Weighted F1 (%)": r["f1_weighted"],
            "Cohen's Kappa": r["cohen_kappa"]
        })
    df_benchmarks = pd.DataFrame(benchmark_rows)
    df_benchmarks.to_csv(DATA_DIR / "model_evaluation_benchmarks.csv", index=False)
    
    # JSON summaries
    with open(METRICS_DIR / "model_comparison_metrics.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
        
    # Per-class summary table for champion model
    class_rows = []
    for cls in CLASS_LABELS:
        class_rows.append({
            "Sentiment Class": cls,
            "Precision (%)": ensemble_res["class_breakdown"][cls]["precision"],
            "Recall (%)": ensemble_res["class_breakdown"][cls]["recall"],
            "F1-Score (%)": ensemble_res["class_breakdown"][cls]["f1_score"],
            "Support (Test Count)": ensemble_res["class_breakdown"][cls]["support"]
        })
    df_classes = pd.DataFrame(class_rows)
    df_classes.to_csv(METRICS_DIR / "per_class_metrics.csv", index=False)
    
    # Enrich worked examples with exact model inference outputs
    with open(METRICS_DIR / "worked_examples.json", "r", encoding="utf-8") as f:
        worked = json.load(f)
        
    sia = SentimentIntensityAnalyzer()
    for item in worked:
        text = item["raw_text"]
        clean = item["step5_final_string"]
        vec = tfidf.transform([clean])
        
        scores_vader = sia.polarity_scores(text)
        blob = TextBlob(text)
        pred_lr = lr_clf.predict(vec)[0]
        prob_lr_sample = lr_clf.predict_proba(vec)[0]
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(lr_clf.classes_, prob_lr_sample)}
        
        item["vader_scores"] = {k: round(v, 4) for k, v in scores_vader.items()}
        item["textblob_polarity"] = round(blob.sentiment.polarity, 4)
        item["textblob_subjectivity"] = round(blob.sentiment.subjectivity, 4)
        item["logistic_regression_prediction"] = pred_lr
        item["logistic_regression_probabilities"] = prob_dict
        
    with open(METRICS_DIR / "worked_examples.json", "w", encoding="utf-8") as f:
        json.dump(worked, f, indent=2)
        
    print(f"      -> Saved benchmarks to {DATA_DIR / 'model_evaluation_benchmarks.csv'}")
    print(f"      -> Updated worked examples with inference breakdowns in {METRICS_DIR / 'worked_examples.json'}")
    print("=" * 80)
    print("MODEL TRAINING & EVALUATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
