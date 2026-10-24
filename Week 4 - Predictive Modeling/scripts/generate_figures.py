"""
Week 4: Publication-Grade Figures Generator (300 DPI)
Author: Akshita (Yuva Internship - Tourism Data Science)

Generates:
1. Fig 1: Multi-Decade Tourism Regimes & Structural Breaks (2001-2024)
2. Fig 2: Quarterly STL Time Series Decomposition (Observed, Trend, Seasonal, Residual)
3. Fig 3: Autocorrelation (ACF) and Partial Autocorrelation (PACF) Diagnostics
4. Fig 4: Walk-Forward Cross-Validation Expanding Window Schematic
5. Fig 5: Model Benchmark: Actual vs. Forecast on Holdout (2023Q1 - 2024Q4)
6. Fig 6: Feature Elasticities (Ridge Coefficients) & Non-Linear Importance (Random Forest)
7. Fig 7: Residual Diagnostics Suite (Time plot, Histogram KDE, Q-Q Plot, ACF)
8. Fig 8: Multi-Scenario Demand Forecast (2025 - 2027) with 95% Confidence Intervals
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from scipy import stats

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FIGURES_DIR = BASE_DIR / "figures"
METRICS_DIR = BASE_DIR / "metrics"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Load data
df_annual = pd.read_csv(DATA_DIR / "annual_series_2001_2024.csv")
df_quarterly = pd.read_csv(DATA_DIR / "quarterly_series_2001_2024.csv")
df_holdout = pd.read_csv(METRICS_DIR / "holdout_predictions_comparison.csv")
df_scenarios = pd.read_csv(DATA_DIR / "forecast_results_2025_2027.csv")
df_feat = pd.read_csv(METRICS_DIR / "feature_importance.csv")

# -------------------------------------------------------------------------
# FIGURE 1: Multi-Decade Tourism Regimes & Structural Breaks (2001-2024)
# -------------------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(11, 5.5))

years = df_annual["year"].values
ftas = df_annual["ftas"].values / 1e6
itas = df_annual["itas"].values / 1e6
fee_usd = df_annual["india_fee_usd_b"].values

ax1.plot(years, itas, color="#1f77b4", marker="o", linewidth=2.2, label="International Tourist Arrivals (ITAs)")
ax1.plot(years, ftas, color="#ff7f0e", marker="s", linewidth=2.0, linestyle="--", label="Foreign Tourist Arrivals (FTAs)")

ax1.set_xlabel("Year", fontweight="bold")
ax1.set_ylabel("Arrival Volume (Millions)", fontweight="bold", color="#1f77b4")
ax1.tick_params(axis='y', labelcolor="#1f77b4")
ax1.set_ylim(0, 24)

# Secondary axis for Foreign Exchange Earnings
ax2 = ax1.twinx()
ax2.plot(years, fee_usd, color="#2ca02c", marker="^", linewidth=2.0, linestyle=":", label="Foreign Exchange Earnings (USD Billion)")
ax2.set_ylabel("FEE (USD Billion)", fontweight="bold", color="#2ca02c")
ax2.tick_params(axis='y', labelcolor="#2ca02c")
ax2.set_ylim(0, 42)
ax2.grid(False)

# Highlight structural regimes
ax1.axvspan(2001, 2013.5, color="#f0f0f0", alpha=0.5, label="_nolegend_")
ax1.axvspan(2013.5, 2019.5, color="#e6f2ff", alpha=0.5, label="_nolegend_")
ax1.axvspan(2019.5, 2021.5, color="#ffe6e6", alpha=0.6, label="_nolegend_")
ax1.axvspan(2021.5, 2024.5, color="#e6ffe6", alpha=0.5, label="_nolegend_")

ax1.text(2007, 21.5, "Regime I: Pre-Redefinition\n(FTA reporting only)", ha="center", fontsize=8.5, fontstyle="italic")
ax1.text(2016.5, 21.5, "Regime II: Golden Growth\n(ITA = FTA + NRI definition)", ha="center", fontsize=8.5, fontstyle="italic")
ax1.text(2020.5, 21.5, "Regime III\nCOVID Shock", ha="center", fontsize=8, fontweight="bold", color="#d62728")
ax1.text(2023, 21.5, "Regime IV\nRebound", ha="center", fontsize=8.5, fontstyle="italic")

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True, framealpha=0.9)

plt.title("Figure 1: Multi-Decade India Tourism Dynamics & Macroeconomic Structural Regimes (2001–2024)", fontweight="bold", pad=12)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig1_longterm_regimes_structural_breaks.png", dpi=300)
plt.close()
print("Saved fig1_longterm_regimes_structural_breaks.png")

# -------------------------------------------------------------------------
# FIGURE 2: Quarterly STL Time Series Decomposition
# -------------------------------------------------------------------------
# Create time series
ts_series = pd.Series(df_quarterly["fta_volume"].values, index=pd.date_range("2011-01-01", periods=len(df_quarterly), freq="QE-DEC"))
decomp = seasonal_decompose(ts_series, model="additive", period=4)

fig, axes = plt.subplots(4, 1, figsize=(10, 7), sharex=True)

axes[0].plot(ts_series.index, ts_series.values / 1e6, color="#003f5c", linewidth=1.8)
axes[0].set_ylabel("Observed (M)", fontweight="bold")
axes[0].set_title("Figure 2: Classical STL Seasonal & Trend Decomposition of Quarterly FTAs (2011–2024)", fontweight="bold", pad=10)

axes[1].plot(ts_series.index, decomp.trend.values / 1e6, color="#7a5195", linewidth=2.0)
axes[1].set_ylabel("Trend (M)", fontweight="bold")

axes[2].plot(ts_series.index, decomp.seasonal.values / 1e6, color="#ef5675", linewidth=1.5)
axes[2].set_ylabel("Seasonal (M)", fontweight="bold")
axes[2].axhline(0, color="gray", linestyle="--", linewidth=0.8)

axes[3].scatter(ts_series.index, decomp.resid.values / 1e6, color="#ffa600", s=18, alpha=0.85)
axes[3].plot(ts_series.index, decomp.resid.values / 1e6, color="#ffa600", linewidth=1.0, alpha=0.5)
axes[3].set_ylabel("Residual (M)", fontweight="bold")
axes[3].axhline(0, color="gray", linestyle="--", linewidth=0.8)
axes[3].set_xlabel("Timeline (Quarterly)", fontweight="bold")

for ax in axes:
    ax.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig2_time_series_decomposition.png", dpi=300)
plt.close()
print("Saved fig2_time_series_decomposition.png")

# -------------------------------------------------------------------------
# FIGURE 3: Autocorrelation (ACF) and Partial Autocorrelation (PACF) Diagnostics
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

plot_acf(df_quarterly["fta_volume"].values, ax=ax1, lags=16, color="#1f77b4", title="Autocorrelation Function (ACF)")
plot_pacf(df_quarterly["fta_volume"].values, ax=ax2, lags=16, color="#ff7f0e", method="ywm", title="Partial Autocorrelation Function (PACF)")

ax1.set_xlabel("Lag (Quarters)", fontweight="bold")
ax1.set_ylabel("Autocorrelation", fontweight="bold")
ax2.set_xlabel("Lag (Quarters)", fontweight="bold")
ax2.set_ylabel("Partial Autocorrelation", fontweight="bold")

ax1.axvline(4, color="red", linestyle=":", alpha=0.7, label="Annual Cycle (Lag 4)")
ax2.axvline(4, color="red", linestyle=":", alpha=0.7, label="Annual Cycle (Lag 4)")
ax1.legend(loc="upper right")
ax2.legend(loc="upper right")

plt.suptitle("Figure 3: Autocorrelation & Partial Autocorrelation Diagnostic Profiles for Inbound FTAs", fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig3_acf_pacf_diagnostics.png", dpi=300)
plt.close()
print("Saved fig3_acf_pacf_diagnostics.png")

# -------------------------------------------------------------------------
# FIGURE 4: Walk-Forward Cross-Validation Architecture Diagram
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.5))

folds = 5
train_lengths = [8, 16, 24, 32, 40]
val_length = 8
total_quarters = 48

for f in range(folds):
    tr_len = train_lengths[f]
    # Train bar
    ax.barh(f, tr_len, color="#2b5c8f", edgecolor="black", height=0.55, align="center")
    # Validation bar
    ax.barh(f, val_length, left=tr_len, color="#e28743", edgecolor="black", height=0.55, align="center")
    # Remaining unobserved
    rem = total_quarters - (tr_len + val_length)
    if rem > 0:
        ax.barh(f, rem, left=tr_len + val_length, color="#e0e0e0", edgecolor="gray", height=0.55, align="center", hatch="//")

ax.set_yticks(range(folds))
ax.set_yticklabels([f"Fold {i+1}" for i in range(folds)], fontweight="bold")
ax.set_xlabel("Temporal Sequence (Quarterly Timeline 2011Q1 to 2022Q4)", fontweight="bold")
ax.set_title("Figure 4: Temporal Walk-Forward Expanding Window Cross-Validation Architecture", fontweight="bold", pad=12)

# Custom legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#2b5c8f", edgecolor="black", label="Expanding Training Window (Historical Data)"),
    Patch(facecolor="#e28743", edgecolor="black", label="Out-of-Sample Validation Window (Forecast Horizon)"),
    Patch(facecolor="#e0e0e0", edgecolor="gray", hatch="//", label="Future Unseen Quarters (No Look-Ahead)")
]
ax.legend(handles=legend_elements, loc="lower right", framealpha=0.95)
ax.invert_yaxis()
ax.grid(True, axis="x", linestyle=":", alpha=0.7)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig4_walk_forward_cv_architecture.png", dpi=300)
plt.close()
print("Saved fig4_walk_forward_cv_architecture.png")

# -------------------------------------------------------------------------
# FIGURE 5: Model Benchmark: Actual vs. Forecast on Holdout (2023Q1 - 2024Q4)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5.5))

q_labels = df_holdout["q_label"].values
x_ticks = np.arange(len(q_labels))

ax.plot(x_ticks, df_holdout["fta_volume"].values / 1e6, marker="o", color="black", linewidth=2.5, label="Actual Observed FTAs")
ax.plot(x_ticks, df_holdout["Ridge Regression"].values / 1e6, marker="s", color="#1f77b4", linewidth=2.0, linestyle="--", label="Ridge Regression (MAPE: 5.81%)")
ax.plot(x_ticks, df_holdout["Blended Hybrid Ensemble"].values / 1e6, marker="^", color="#2ca02c", linewidth=2.2, label="Blended Hybrid (MAPE: 6.21%)")
ax.plot(x_ticks, df_holdout["SARIMA"].values / 1e6, marker="D", color="#ff7f0e", linewidth=1.8, linestyle=":", label="SARIMA (MAPE: 9.78%)")
ax.plot(x_ticks, df_holdout["Random Forest"].values / 1e6, marker="x", color="#9467bd", linewidth=1.8, linestyle="-.", label="Random Forest (MAPE: 10.20%)")
ax.plot(x_ticks, df_holdout["Holt-Winters"].values / 1e6, marker="v", color="#8c564b", linewidth=1.5, linestyle="--", label="Holt-Winters (MAPE: 13.74%)")
ax.plot(x_ticks, df_holdout["Naive Seasonal Drift"].values / 1e6, color="#7f7f7f", linewidth=1.2, linestyle=":", label="Naive Drift (MAPE: 16.20%)")

ax.set_xticks(x_ticks)
ax.set_xticklabels(q_labels, fontweight="bold")
ax.set_ylabel("Foreign Tourist Arrivals (Millions)", fontweight="bold")
ax.set_xlabel("Quarterly Holdout Timeline (2023Q1 to 2024Q4)", fontweight="bold")
ax.set_title("Figure 5: Predictive Performance on Out-of-Sample Holdout (2023Q1–2024Q4)", fontweight="bold", pad=12)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=True)
ax.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig5_model_predictions_comparison.png", dpi=300)
plt.close()
print("Saved fig5_model_predictions_comparison.png")

# -------------------------------------------------------------------------
# FIGURE 6: Feature Elasticities (Ridge Coefficients) & RF Importance
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))

df_feat_sorted_rf = df_feat.sort_values(by="RF_Importance", ascending=True)
ax1.barh(df_feat_sorted_rf["Feature"], df_feat_sorted_rf["RF_Importance"], color="#3b528b", edgecolor="black", height=0.6)
ax1.set_xlabel("Gini Feature Importance", fontweight="bold")
ax1.set_title("Random Forest Gini Feature Importance", fontweight="bold")
ax1.grid(True, axis="x", linestyle=":", alpha=0.6)

df_feat_sorted_ridge = df_feat.sort_values(by="Ridge_Coefficient", ascending=True)
colors = ["#d73027" if x < 0 else "#1a9850" for x in df_feat_sorted_ridge["Ridge_Coefficient"]]
ax2.barh(df_feat_sorted_ridge["Feature"], df_feat_sorted_ridge["Ridge_Coefficient"] / 1e3, color=colors, edgecolor="black", height=0.6)
ax2.set_xlabel("Standardized Coefficient (Thousand Visitors)", fontweight="bold")
ax2.set_title("Ridge Regression Directional Feature Elasticity", fontweight="bold")
ax2.axvline(0, color="black", linewidth=0.8)
ax2.grid(True, axis="x", linestyle=":", alpha=0.6)

plt.suptitle("Figure 6: Driver Analysis: Linear Ridge Elasticity vs. Non-Linear Random Forest Importance", fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig6_feature_importance_sensitivity.png", dpi=300)
plt.close()
print("Saved fig6_feature_importance_sensitivity.png")

# -------------------------------------------------------------------------
# FIGURE 7: Residual Diagnostics Suite
# -------------------------------------------------------------------------
res = df_holdout["fta_volume"].values - df_holdout["Ridge Regression"].values

fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# 1. Residuals over time
axes[0, 0].plot(range(len(res)), res / 1e3, marker="o", color="#1f77b4", linewidth=1.8)
axes[0, 0].axhline(0, color="red", linestyle="--", linewidth=1.0)
axes[0, 0].set_xticks(range(len(q_labels)))
axes[0, 0].set_xticklabels(q_labels, rotation=45, fontsize=8)
axes[0, 0].set_ylabel("Residual (Thousands)", fontweight="bold")
axes[0, 0].set_title("Residuals Across Test Quarters", fontweight="bold")
axes[0, 0].grid(True, linestyle=":", alpha=0.6)

# 2. Histogram with Normal Distribution fit
sns.histplot(res / 1e3, kde=True, ax=axes[0, 1], color="#2ca02c", stat="density", bins=6)
# Overlay theoretical normal
x_norm = np.linspace(min(res / 1e3) - 50, max(res / 1e3) + 50, 100)
p_norm = stats.norm.pdf(x_norm, np.mean(res / 1e3), np.std(res / 1e3))
axes[0, 1].plot(x_norm, p_norm, 'r--', linewidth=1.5, label="Normal Curve")
axes[0, 1].set_xlabel("Residual Error (Thousands)", fontweight="bold")
axes[0, 1].set_ylabel("Density", fontweight="bold")
axes[0, 1].set_title("Residual Distribution & Normality", fontweight="bold")
axes[0, 1].legend()
axes[0, 1].grid(True, linestyle=":", alpha=0.6)

# 3. Q-Q Plot
stats.probplot(res / 1e3, dist="norm", plot=axes[1, 0])
axes[1, 0].get_lines()[0].set_markerfacecolor('#1f77b4')
axes[1, 0].get_lines()[0].set_markersize(6.0)
axes[1, 0].get_lines()[1].set_color('red')
axes[1, 0].set_title("Quantile-Quantile (Q-Q) Plot", fontweight="bold")
axes[1, 0].grid(True, linestyle=":", alpha=0.6)

# 4. Residual Autocorrelation
plot_acf(res, ax=axes[1, 1], lags=3, color="#ff7f0e", title="Residual Autocorrelation (ACF)")
axes[1, 1].set_xlabel("Lag (Quarters)", fontweight="bold")
axes[1, 1].set_ylabel("Autocorrelation", fontweight="bold")
axes[1, 1].grid(True, linestyle=":", alpha=0.6)

plt.suptitle("Figure 7: Residual Diagnostics Suite for Champion Predictive Model (Ridge Regression)", fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig7_residual_diagnostics_qq_autocorr.png", dpi=300)
plt.close()
print("Saved fig7_residual_diagnostics_qq_autocorr.png")

# -------------------------------------------------------------------------
# FIGURE 8: Multi-Scenario Demand Forecast (2025 - 2027)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5.8))

# Historical observations (2018Q1 to 2024Q4)
hist_sub = df_quarterly[df_quarterly["year"] >= 2018].reset_index(drop=True)
hist_dates = np.arange(len(hist_sub))
hist_labels = hist_sub["q_label"].values

ax.plot(hist_dates, hist_sub["fta_volume"].values / 1e6, marker="o", color="black", linewidth=2.2, label="Historical Actuals (2018–2024)")

# Future timeline
future_start = len(hist_sub)
future_dates = np.arange(future_start, future_start + 12)

sc_base = df_scenarios[df_scenarios["scenario"] == "Baseline"]
sc_opt = df_scenarios[df_scenarios["scenario"] == "Optimistic"]
sc_pess = df_scenarios[df_scenarios["scenario"] == "Pessimistic"]

# Connect last historical point to first future point
con_dates = np.insert(future_dates, 0, hist_dates[-1])
con_base = np.insert(sc_base["projected_fta"].values / 1e6, 0, hist_sub["fta_volume"].iloc[-1] / 1e6)
con_opt = np.insert(sc_opt["projected_fta"].values / 1e6, 0, hist_sub["fta_volume"].iloc[-1] / 1e6)
con_pess = np.insert(sc_pess["projected_fta"].values / 1e6, 0, hist_sub["fta_volume"].iloc[-1] / 1e6)

ax.plot(con_dates, con_opt, marker="^", color="#1a9850", linewidth=2.0, linestyle="--", label="Optimistic Scenario (Visa Ease / High Connectivity)")
ax.plot(con_dates, con_base, marker="s", color="#1f77b4", linewidth=2.4, label="Baseline Scenario (Current Trajectory)")
ax.plot(con_dates, con_pess, marker="v", color="#d73027", linewidth=2.0, linestyle="--", label="Pessimistic Scenario (Geopolitical / Macro Drag)")

# Shaded 95% Confidence Interval for baseline
ci_low = np.insert(sc_base["ci_lower_95"].values / 1e6, 0, hist_sub["fta_volume"].iloc[-1] / 1e6)
ci_high = np.insert(sc_base["ci_upper_95"].values / 1e6, 0, hist_sub["fta_volume"].iloc[-1] / 1e6)
ax.fill_between(con_dates, ci_low, ci_high, color="#1f77b4", alpha=0.15, label="Baseline 95% Confidence Interval")

# Format X axis
all_dates = np.concatenate([hist_dates, future_dates])
all_labels = np.concatenate([hist_labels, sc_base["q_label"].values])

# Subsample tick labels to avoid overcrowding
tick_indices = np.arange(0, len(all_dates), 2)
ax.set_xticks(tick_indices)
ax.set_xticklabels(all_labels[tick_indices], rotation=45, fontsize=8.5)

ax.axvline(hist_dates[-1], color="gray", linestyle=":", linewidth=1.5)
ax.text(hist_dates[-1] - 0.5, 3.4, "Historical", ha="right", fontsize=9, fontstyle="italic", color="gray")
ax.text(hist_dates[-1] + 0.5, 3.4, "Forecast Horizon (2025–2027)", ha="left", fontsize=9, fontstyle="italic", color="blue")

ax.set_ylabel("Quarterly FTAs (Millions)", fontweight="bold")
ax.set_title("Figure 8: India Tourism Demand Forecast: Multi-Scenario Projections to 2027 with 95% Confidence Bounds", fontweight="bold", pad=12)
ax.legend(loc="upper left", frameon=True, framealpha=0.9)
ax.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "fig8_multi_scenario_forecast_2025_2027.png", dpi=300)
plt.close()
print("Saved fig8_multi_scenario_forecast_2025_2027.png")

print("All 8 publication figures generated successfully at 300 DPI!")
