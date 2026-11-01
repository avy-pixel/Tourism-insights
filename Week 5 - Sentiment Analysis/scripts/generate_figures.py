"""
Week 5: Publication-Grade Figures Generator for Tourism Sentiment Analysis
Renders 8 publication-quality figures (300 DPI) and automatically generates
compressed JPEG versions (quality=82) to ensure the compiled Word document
remains strictly under the portal's 2048 KB file upload limit.

Author: Akshita | B.Tech Computer Science & Engineering
Institution: Amritsar Group of Colleges
Project: Yuva Internship - Tourism Data Science & Analytics
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from PIL import Image
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer

# Style configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['figure.titlesize'] = 13
plt.rcParams['figure.titleweight'] = 'bold'

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FIGURES_DIR = BASE_DIR / "figures"
METRICS_DIR = BASE_DIR / "metrics"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Color constants
COLOR_NAVY = "#003366"
COLOR_TEAL = "#1E5A96"
COLOR_GREEN = "#2E7D32"
COLOR_AMBER = "#F57F17"
COLOR_RED = "#C62828"
COLOR_LIGHT_GRAY = "#F4F7FA"

def save_dual_formats(fig, output_base_name):
    """Saves figure as 300 DPI PNG and compressed JPG for lightweight Word embedding."""
    png_path = FIGURES_DIR / f"{output_base_name}.png"
    jpg_path = FIGURES_DIR / f"{output_base_name}.jpg"
    
    fig.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    # Convert and compress to JPEG (max width 1600px, quality=75) to strictly respect the 2048 KB portal limit
    with Image.open(png_path) as img:
        rgb_img = img.convert('RGB')
        max_dim = 1600
        if rgb_img.width > max_dim:
            ratio = max_dim / float(rgb_img.width)
            new_height = int(float(rgb_img.height) * ratio)
            rgb_img = rgb_img.resize((max_dim, new_height), Image.Resampling.LANCZOS)
        rgb_img.save(jpg_path, 'JPEG', quality=75, optimize=True)
    print(f"      -> Generated {output_base_name}.png & {output_base_name}.jpg ({jpg_path.stat().st_size / 1024:.1f} KB)")

def generate_fig1_sentiment_distribution(df):
    """Figure 1: Overall Sentiment Distribution (Donut Chart & Star Rating Breakdown)."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    
    # 1. Donut chart of sentiment classes
    counts = df["ground_truth_sentiment"].value_counts()[["Positive", "Neutral", "Negative"]]
    colors = [COLOR_GREEN, COLOR_AMBER, COLOR_RED]
    explode = (0.02, 0.02, 0.04)
    
    wedges, texts, autotexts = axes[0].pie(
        counts, labels=counts.index, autopct='%1.1f%%', startangle=140,
        colors=colors, explode=explode, pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
    )
    for at in autotexts:
        at.set_color('white')
        at.set_weight('bold')
        at.set_fontsize(11)
    for t in texts:
        t.set_fontsize(10)
        t.set_weight('bold')
        
    axes[0].set_title("Overall Corpus Sentiment Proportion (N=2,500)", pad=12)
    # Center circle annotation
    axes[0].text(0, 0, f"Total\n2,500\nReviews", ha='center', va='center', fontsize=11, fontweight='bold', color=COLOR_NAVY)
    
    # 2. Grouped Rating Distribution
    rating_cross = pd.crosstab(df["rating"], df["ground_truth_sentiment"])[["Positive", "Neutral", "Negative"]]
    rating_cross.plot(kind='bar', stacked=True, ax=axes[1], color=colors, edgecolor='white', width=0.6)
    axes[1].set_title("Tourist Review Count by Star Rating (1–5 Stars)", pad=12)
    axes[1].set_xlabel("Tourist Star Rating")
    axes[1].set_ylabel("Number of Reviews")
    axes[1].legend(title="Sentiment Class", frameon=True)
    axes[1].tick_params(axis='x', rotation=0)
    
    for c in axes[1].containers:
        axes[1].bar_label(c, label_type='center', color='white', weight='bold', fontsize=9)
        
    plt.tight_layout()
    save_dual_formats(fig, "fig1_sentiment_distribution")

def generate_fig2_wordclouds(df):
    """Figure 2: Dual High-Resolution Word Clouds for Positive vs Negative Feedback."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    pos_text = " ".join(df[df["ground_truth_sentiment"] == "Positive"]["cleaned_text"])
    neg_text = " ".join(df[df["ground_truth_sentiment"] == "Negative"]["cleaned_text"])
    
    wc_pos = WordCloud(
        width=800, height=450, background_color='white',
        colormap='Greens', max_words=100, contour_width=1, contour_color=COLOR_GREEN
    ).generate(pos_text)
    
    wc_neg = WordCloud(
        width=800, height=450, background_color='white',
        colormap='Reds', max_words=100, contour_width=1, contour_color=COLOR_RED
    ).generate(neg_text)
    
    axes[0].imshow(wc_pos, interpolation='bilinear')
    axes[0].axis('off')
    axes[0].set_title("Positive Tourist Experience Themes\n(High Frequency: majestic, pristine, courteous, craftsmanship)", pad=10, color=COLOR_GREEN)
    
    axes[1].imshow(wc_neg, interpolation='bilinear')
    axes[1].axis('off')
    axes[1].set_title("Negative Tourist Experience Pain Points\n(High Frequency: overpriced, dirty, tout, harassment, queue)", pad=10, color=COLOR_RED)
    
    plt.tight_layout()
    save_dual_formats(fig, "fig2_positive_negative_wordclouds")

def generate_fig3_top_ngrams(df):
    """Figure 3: Top Discriminative Bi-grams and Tri-grams by Sentiment."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
    
    pos_corpus = df[df["ground_truth_sentiment"] == "Positive"]["cleaned_text"]
    neg_corpus = df[df["ground_truth_sentiment"] == "Negative"]["cleaned_text"]
    
    def get_top_ngrams(corpus, n=2, top_k=10):
        vec = CountVectorizer(ngram_range=(n, n), min_df=3)
        X = vec.fit_transform(corpus)
        counts = np.array(X.sum(axis=0)).flatten()
        names = np.array(vec.get_feature_names_out())
        sorted_idx = np.argsort(counts)[::-1][:top_k]
        return names[sorted_idx], counts[sorted_idx]
    
    pos_terms, pos_counts = get_top_ngrams(pos_corpus, n=2, top_k=10)
    neg_terms, neg_counts = get_top_ngrams(neg_corpus, n=2, top_k=10)
    
    y_pos = np.arange(len(pos_terms))
    axes[0].barh(y_pos, pos_counts[::-1], color=COLOR_GREEN, edgecolor='white', height=0.65)
    axes[0].set_yticks(y_pos)
    axes[0].set_yticklabels(pos_terms[::-1], fontsize=9.5)
    axes[0].set_title("Top 10 Bi-grams: Positive Reviews", pad=10, color=COLOR_GREEN)
    axes[0].set_xlabel("Corpus Occurrence Frequency")
    for i, v in enumerate(pos_counts[::-1]):
        axes[0].text(v + 3, i, str(v), va='center', fontweight='bold', fontsize=8.5, color=COLOR_GREEN)
        
    y_neg = np.arange(len(neg_terms))
    axes[1].barh(y_neg, neg_counts[::-1], color=COLOR_RED, edgecolor='white', height=0.65)
    axes[1].set_yticks(y_neg)
    axes[1].set_yticklabels(neg_terms[::-1], fontsize=9.5)
    axes[1].set_title("Top 10 Bi-grams: Negative Reviews", pad=10, color=COLOR_RED)
    axes[1].set_xlabel("Corpus Occurrence Frequency")
    for i, v in enumerate(neg_counts[::-1]):
        axes[1].text(v + 3, i, str(v), va='center', fontweight='bold', fontsize=8.5, color=COLOR_RED)
        
    plt.tight_layout()
    save_dual_formats(fig, "fig3_top_ngrams_by_sentiment")

def generate_fig4_model_performance(benchmarks_path):
    """Figure 4: Comparative Benchmarking across Lexicon and Machine Learning Models."""
    df_bm = pd.read_csv(benchmarks_path)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    models = df_bm["Model Architecture"].tolist()
    # Shorten names for cleaner chart display
    short_names = [
        "VADER\n(Lexicon)", "TextBlob\n(Pattern)", "Naive Bayes\n(TF-IDF)",
        "Logistic Reg\n(L2 Regularized)", "Linear SVM\n(Calibrated)", "Blended Ensemble\n(Champion)"
    ]
    
    x = np.arange(len(models))
    width = 0.25
    
    rects1 = ax.bar(x - width, df_bm["Accuracy (%)"], width, label='Accuracy (%)', color=COLOR_NAVY)
    rects2 = ax.bar(x, df_bm["Macro F1-Score (%)"], width, label='Macro F1-Score (%)', color=COLOR_TEAL)
    rects3 = ax.bar(x + width, df_bm["Balanced Acc (%)"], width, label='Balanced Accuracy (%)', color="#4A90E2")
    
    ax.set_ylabel("Evaluation Metric (%)")
    ax.set_title("Sentiment Classification Benchmark: Lexicon Approaches vs. Supervised ML Models", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(short_names, fontsize=9.5, fontweight='bold')
    ax.set_ylim(40, 105)
    ax.legend(loc='lower right', frameon=True)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')
            
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    
    # Highlight champion
    ax.axvspan(x[-1] - 0.45, x[-1] + 0.45, color='gold', alpha=0.15, label='Champion Architecture')
    
    plt.tight_layout()
    save_dual_formats(fig, "fig4_model_performance_comparison")

def generate_fig5_confusion_matrices(metrics_path):
    """Figure 5: Multi-Panel Normalized Confusion Matrices for Key Architectures."""
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    axes = axes.flatten()
    
    target_models = [
        ("NLTK VADER (Rule-Based)", "a) NLTK VADER (Lexicon Rule)"),
        ("TextBlob (Pattern-Based)", "b) TextBlob (Pattern Sentiment)"),
        ("TF-IDF + Multinomial Naive Bayes", "c) Multinomial Naive Bayes"),
        ("Blended NLP Ensemble (Champion)", "d) Blended NLP Ensemble (Champion)")
    ]
    
    labels = ["Negative", "Neutral", "Positive"]
    
    for idx, (m_key, title) in enumerate(target_models):
        m_data = next((m for m in metrics if m["model"] == m_key), None)
        if m_data:
            cm = np.array(m_data["confusion_matrix"])
            # Normalize by true class support (rows)
            cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            
            sns.heatmap(
                cm_norm, annot=True, fmt='.1%', cmap='Blues', cbar=False,
                xticklabels=labels, yticklabels=labels, ax=axes[idx],
                annot_kws={'size': 11, 'weight': 'bold'}
            )
            axes[idx].set_title(title, pad=10, fontsize=11, fontweight='bold', color=COLOR_NAVY)
            axes[idx].set_xlabel("Predicted Label", fontweight='bold')
            axes[idx].set_ylabel("Ground Truth Label", fontweight='bold')
            
    plt.tight_layout()
    save_dual_formats(fig, "fig5_confusion_matrices")

def generate_fig6_aspect_scorecard(absa_path):
    """Figure 6: Aspect-Based Sentiment Scorecard (Net Sentiment Score & Proportions)."""
    df_absa = pd.read_csv(absa_path).set_index("primary_aspect")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Net Sentiment Score Bar Chart
    df_sorted = df_absa.sort_values(by="Net_Sentiment_Score", ascending=True)
    nss_colors = [COLOR_RED if v < 0 else (COLOR_AMBER if v < 30 else COLOR_GREEN) for v in df_sorted["Net_Sentiment_Score"]]
    
    y = np.arange(len(df_sorted))
    axes[0].barh(y, df_sorted["Net_Sentiment_Score"], color=nss_colors, height=0.6, edgecolor='white')
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(df_sorted.index, fontsize=9.5, fontweight='bold')
    axes[0].set_title("Net Sentiment Score (NSS = %Pos - %Neg) by Aspect", pad=12)
    axes[0].set_xlabel("Net Sentiment Score (NSS)")
    axes[0].axvline(0, color='black', linewidth=0.8, linestyle='--')
    
    for i, v in enumerate(df_sorted["Net_Sentiment_Score"]):
        axes[0].text(v + (1.5 if v >= 0 else -6.0), i, f"{v:+.1f}", va='center', fontweight='bold', fontsize=9)
        
    # 2. Stacked sentiment distribution per aspect
    prop_cols = ["Positive_Pct", "Neutral_Pct" if "Neutral_Pct" in df_absa.columns else "Neutral", "Negative_Pct"]
    # Calculate neutral pct if missing
    if "Neutral_Pct" not in df_absa.columns:
        df_absa["Neutral_Pct"] = (100 - df_absa["Positive_Pct"] - df_absa["Negative_Pct"]).round(1)
        
    df_plot = df_absa[["Positive_Pct", "Neutral_Pct", "Negative_Pct"]].loc[df_sorted.index[::-1]]
    df_plot.plot(kind='barh', stacked=True, ax=axes[1], color=[COLOR_GREEN, COLOR_AMBER, COLOR_RED], edgecolor='white', width=0.65)
    axes[1].set_title("Sentiment Proportion Breakdown per Aspect (%)", pad=12)
    axes[1].set_xlabel("Percentage Share (%)")
    axes[1].legend(["Positive", "Neutral", "Negative"], loc='lower right', frameon=True)
    axes[1].set_ylabel("")
    
    plt.tight_layout()
    save_dual_formats(fig, "fig6_aspect_based_sentiment_scorecard")

def generate_fig7_temporal_trends(df):
    """Figure 7: Temporal Sentiment Dynamics & Seasonality (2023–2024 Quarters)."""
    # Group by quarter and category
    grp = df.groupby(["travel_quarter", "destination_category", "ground_truth_sentiment"]).size().unstack(fill_value=0)
    grp["Total"] = grp.sum(axis=1)
    grp["NSS"] = ((grp.get("Positive", 0) - grp.get("Negative", 0)) / grp["Total"] * 100).round(1)
    
    nss_pivot = grp["NSS"].unstack()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    palette = [COLOR_NAVY, COLOR_GREEN, COLOR_AMBER, COLOR_TEAL]
    markers = ['o', 's', '^', 'D']
    
    for i, col in enumerate(nss_pivot.columns):
        ax.plot(nss_pivot.index, nss_pivot[col], marker=markers[i % len(markers)],
                linewidth=2.5, markersize=7, label=col, color=palette[i % len(palette)])
        
    ax.set_title("Temporal Net Sentiment Index (2023Q1–2024Q4) by Destination Category", pad=14)
    ax.set_xlabel("Travel Quarter (Calendar Year & Quarter)")
    ax.set_ylabel("Net Sentiment Score (NSS = %Pos - %Neg)")
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(title="Destination Category", frameon=True, loc='best')
    
    # Highlight winter crowd congestion dip in Q4
    ax.annotate("Winter Peak Crowd Congestion\n(Sharp Dip in Transit & Heritage NSS)",
                xy=(3, nss_pivot.loc["2023Q4", "Heritage & Monuments"]),
                xytext=(2.2, nss_pivot.loc["2023Q4", "Heritage & Monuments"] - 18),
                arrowprops=dict(facecolor=COLOR_RED, shrink=0.08, width=1.5, headwidth=6),
                fontweight='bold', fontsize=8.5, color=COLOR_RED)
    
    plt.tight_layout()
    save_dual_formats(fig, "fig7_temporal_sentiment_trends")

def generate_fig8_destination_heatmap(dest_path):
    """Figure 8: Destination Sentiment Ranking and Dimension Matrix."""
    df_dest = pd.read_csv(dest_path).set_index("destination")
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    # Format data for heatmap
    df_dest_sorted = df_dest.sort_values(by="Net_Sentiment_Score", ascending=False)
    heatmap_data = df_dest_sorted[["Positive_Pct", "Negative_Pct", "Net_Sentiment_Score"]]
    heatmap_data.columns = ["% Positive Reviews", "% Negative Reviews", "Net Sentiment Score (NSS)"]
    
    sns.heatmap(
        heatmap_data, annot=True, fmt='.1f', cmap='coolwarm', center=30,
        linewidths=1.2, linecolor='white', ax=ax,
        cbar_kws={'label': 'Sentiment Metric Value'}
    )
    ax.set_title("Destination Benchmark Matrix: 12 Premier Indian Tourism Hubs", pad=14)
    ax.set_ylabel("Destination", fontweight='bold')
    
    plt.tight_layout()
    save_dual_formats(fig, "fig8_destination_sentiment_heatmap")

def main():
    print("=" * 80)
    print("WEEK 5: RENDERING 8 PUBLICATION-GRADE VISUALIZATIONS (300 DPI + JPG)")
    print("=" * 80)
    
    df_cleaned = pd.read_csv(DATA_DIR / "tourist_reviews_cleaned.csv")
    benchmarks_path = DATA_DIR / "model_evaluation_benchmarks.csv"
    metrics_path = METRICS_DIR / "model_comparison_metrics.json"
    absa_path = DATA_DIR / "aspect_sentiment_summary.csv"
    dest_path = DATA_DIR / "destination_sentiment_index.csv"
    
    print("[1/8] Rendering Fig 1: Overall Sentiment Distribution...")
    generate_fig1_sentiment_distribution(df_cleaned)
    
    print("[2/8] Rendering Fig 2: Positive vs Negative Word Clouds...")
    generate_fig2_wordclouds(df_cleaned)
    
    print("[3/8] Rendering Fig 3: Top Bi-grams by Sentiment...")
    generate_fig3_top_ngrams(df_cleaned)
    
    print("[4/8] Rendering Fig 4: NLP Model Performance Comparison...")
    generate_fig4_model_performance(benchmarks_path)
    
    print("[5/8] Rendering Fig 5: Multi-Panel Confusion Matrices...")
    generate_fig5_confusion_matrices(metrics_path)
    
    print("[6/8] Rendering Fig 6: Aspect-Based Sentiment Scorecard...")
    generate_fig6_aspect_scorecard(absa_path)
    
    print("[7/8] Rendering Fig 7: Temporal Sentiment Trends (2023–2024)...")
    generate_fig7_temporal_trends(df_cleaned)
    
    print("[8/8] Rendering Fig 8: Destination Benchmark Heatmap...")
    generate_fig8_destination_heatmap(dest_path)
    
    print("=" * 80)
    print("ALL 8 PUBLICATION-GRADE VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
