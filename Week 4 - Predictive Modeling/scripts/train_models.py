"""
Week 4: Comprehensive Predictive Modeling Engine
Author: Akshita (Yuva Internship - Tourism Data Science)

Benchmarks:
1. Baseline: Naive Seasonal Drift
2. Classical Time Series: Holt-Winters Triple Exponential Smoothing
3. Classical Econometrics: SARIMA(1,0,1)x(0,1,1)_4
4. Exogenous Econometric: SARIMAX with Structural Shock Interventions
5. Regularized Regression: Ridge Regression (L2)
6. Regularized Regression: ElasticNet (L1 + L2)
7. Non-Linear Ensemble: Random Forest Regressor
8. Non-Linear Ensemble: HistGradientBoosting Regressor
9. Champion Meta-Model: Blended Hybrid Ensemble (Ridge 50% + SARIMA 30% + Random Forest 20%)

Validation:
- Walk-forward expanding window cross validation (5 folds)
- Out-of-sample holdout testing (2023Q1 to 2024Q4, 8 quarters)
- Statistical residual diagnostic tests (Durbin-Watson, Jarque-Bera, Ljung-Box)
- Multi-scenario forward projections (2025Q1 - 2027Q4) with 95% confidence bounds
- Foreign Exchange Earnings (FEE) predictive elasticity model
"""

import sys
import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from sklearn.linear_model import Ridge, ElasticNet, LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit

import statsmodels.api as sm
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson

warnings.filterwarnings("ignore")

# Directory setup
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
METRICS_DIR = BASE_DIR / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# 1. LOAD DATASETS
# -------------------------------------------------------------------------
df_quarterly = pd.read_csv(DATA_DIR / "quarterly_series_2001_2024.csv")
df_annual = pd.read_csv(DATA_DIR / "annual_series_2001_2024.csv")
df_monthly = pd.read_csv(DATA_DIR / "monthly_demand_features_2019_2024.csv")

print(f"Loaded {len(df_quarterly)} quarterly observations (2011Q1 to 2024Q4)")

# Helper metric calculation
def calc_metrics(y_true, y_pred):
    y_true, y_pred = np.array(y_true, dtype=float), np.array(y_pred, dtype=float)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100.0
    r2 = r2_score(y_true, y_pred)
    
    # Directional accuracy
    if len(y_true) > 1:
        dir_true = np.sign(np.diff(y_true))
        dir_pred = np.sign(np.diff(y_pred))
        mda = np.mean(dir_true == dir_pred) * 100.0
    else:
        mda = 100.0
        
    return {
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "MAPE_pct": round(float(mape), 2),
        "R2": round(float(r2), 4),
        "MDA_pct": round(float(mda), 2)
    }

# -------------------------------------------------------------------------
# 2. FEATURE ENGINEERING & PREPARATION
# -------------------------------------------------------------------------
df_q = df_quarterly.copy()
for col in ["fta_lag1", "fta_lag2", "fta_lag4"]:
    df_q[col] = df_q[col].bfill()

feature_cols = [
    "q1_dummy", "q2_dummy", "q3_dummy", "q4_dummy",
    "covid_shock", "covid_lockdown_peak", "recovery_phase",
    "implied_usd_inr", "world_arr_growth_pct",
    "fta_lag1", "fta_lag2", "fta_lag4"
]

train_mask = df_q["year"] <= 2022
test_mask = df_q["year"] >= 2023

df_train = df_q[train_mask].reset_index(drop=True)
df_test = df_q[test_mask].reset_index(drop=True)

y_train = df_train["fta_volume"].values
y_test = df_test["fta_volume"].values

X_train = df_train[feature_cols].values
X_test = df_test[feature_cols].values

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

predictions = {"Actual": list(y_test)}

# -------------------------------------------------------------------------
# MODEL 0: Naive Seasonal Drift Baseline
# -------------------------------------------------------------------------
preds_baseline = []
for idx, row in df_test.iterrows():
    prev_yr = row["year"] - 1
    prev_q = row["quarter"]
    prev_val = df_q.loc[(df_q["year"] == prev_yr) & (df_q["quarter"] == prev_q), "fta_volume"].values
    if len(prev_val) > 0:
        preds_baseline.append(prev_val[0] * 1.045)  # Historical 4.5% drift
    else:
        preds_baseline.append(y_train[-4] * 1.045)
predictions["Naive Seasonal Drift"] = [round(x) for x in preds_baseline]

# -------------------------------------------------------------------------
# MODEL 1: Holt-Winters Triple Exponential Smoothing
# -------------------------------------------------------------------------
hw = ExponentialSmoothing(
    y_train,
    seasonal_periods=4,
    trend="add",
    seasonal="add",
    damped_trend=True,
    initialization_method="estimated"
).fit(optimized=True)

preds_hw = hw.forecast(len(y_test))
predictions["Holt-Winters"] = [round(x) for x in preds_hw]

# -------------------------------------------------------------------------
# MODEL 2: Univariate SARIMA(1,0,1)x(0,1,1)_4
# -------------------------------------------------------------------------
sarima = SARIMAX(
    y_train,
    order=(1, 0, 1),
    seasonal_order=(0, 1, 1, 4),
    enforce_stationarity=False,
    enforce_invertibility=False
).fit(disp=False)

preds_sarima = sarima.forecast(steps=len(y_test))
predictions["SARIMA"] = [round(x) for x in preds_sarima]

# -------------------------------------------------------------------------
# MODEL 3: Econometric SARIMAX with Exogenous Shock Indicators
# -------------------------------------------------------------------------
exog_cols = ["covid_shock", "covid_lockdown_peak", "recovery_phase"]
exog_train = df_train[exog_cols].values
exog_test = df_test[exog_cols].values

sarimax = SARIMAX(
    y_train,
    exog=exog_train,
    order=(1, 0, 1),
    seasonal_order=(0, 1, 1, 4),
    enforce_stationarity=False,
    enforce_invertibility=False
).fit(disp=False)

preds_sarimax = sarimax.forecast(steps=len(y_test), exog=exog_test)
predictions["SARIMAX (Exog)"] = [round(x) for x in preds_sarimax]

# -------------------------------------------------------------------------
# MODEL 4: Regularized Ridge Regression (L2)
# -------------------------------------------------------------------------
ridge = Ridge(alpha=10.0, random_state=42)
ridge.fit(X_train_sc, y_train)
preds_ridge = ridge.predict(X_test_sc)
predictions["Ridge Regression"] = [round(x) for x in preds_ridge]

# -------------------------------------------------------------------------
# MODEL 5: ElasticNet Regression (L1 + L2)
# -------------------------------------------------------------------------
elastic = ElasticNet(alpha=1.0, l1_ratio=0.5, random_state=42)
elastic.fit(X_train_sc, y_train)
preds_elastic = elastic.predict(X_test_sc)
predictions["ElasticNet"] = [round(x) for x in preds_elastic]

# -------------------------------------------------------------------------
# MODEL 6: Random Forest Regressor
# -------------------------------------------------------------------------
rf = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=3, random_state=42)
rf.fit(X_train, y_train)
preds_rf = rf.predict(X_test)
predictions["Random Forest"] = [round(x) for x in preds_rf]

# -------------------------------------------------------------------------
# MODEL 7: HistGradientBoosting Regressor
# -------------------------------------------------------------------------
hgb = HistGradientBoostingRegressor(max_iter=100, max_depth=4, learning_rate=0.08, random_state=42)
hgb.fit(X_train, y_train)
preds_hgb = hgb.predict(X_test)
predictions["Gradient Boosting"] = [round(x) for x in preds_hgb]

# -------------------------------------------------------------------------
# MODEL 8: Champion Blended Hybrid Ensemble
# -------------------------------------------------------------------------
# Combines regularized regression (50%), classical seasonal SARIMA (30%), and non-linear RF (20%)
preds_blend = (0.50 * np.array(preds_ridge)) + (0.30 * np.array(preds_sarima)) + (0.20 * np.array(preds_rf))
predictions["Blended Hybrid Ensemble"] = [round(x) for x in preds_blend]

# -------------------------------------------------------------------------
# 3. BENCHMARK EVALUATION TABLE
# -------------------------------------------------------------------------
benchmark_rows = []
for model_name, preds in predictions.items():
    if model_name == "Actual":
        continue
    m = calc_metrics(y_test, preds)
    m["Model"] = model_name
    benchmark_rows.append(m)

df_benchmark = pd.DataFrame(benchmark_rows)[["Model", "MAE", "RMSE", "MAPE_pct", "R2", "MDA_pct"]]
df_benchmark.sort_values(by="RMSE", inplace=True)
df_benchmark.to_csv(METRICS_DIR / "model_evaluation_metrics.csv", index=False)
print("\n=== Model Benchmark on Holdout (2023Q1 - 2024Q4) ===")
print(df_benchmark.to_string(index=False))

# -------------------------------------------------------------------------
# 4. WALK-FORWARD CROSS-VALIDATION
# -------------------------------------------------------------------------
tscv = TimeSeriesSplit(n_splits=5)
cv_rows = []

for fold, (tr_idx, va_idx) in enumerate(tscv.split(X_train)):
    y_tr, y_va = y_train[tr_idx], y_train[va_idx]
    X_tr_sc_fold = scaler.fit_transform(X_train[tr_idx])
    X_va_sc_fold = scaler.transform(X_train[va_idx])
    
    # Ridge
    r_fold = Ridge(alpha=10.0, random_state=42).fit(X_tr_sc_fold, y_tr)
    p_ridge_fold = r_fold.predict(X_va_sc_fold)
    
    # SARIMA
    try:
        s_fold = SARIMAX(y_tr, order=(1,0,1), seasonal_order=(0,1,1,4),
                         enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        p_sarima_fold = s_fold.forecast(steps=len(y_va))
    except Exception:
        p_sarima_fold = np.full(len(y_va), np.mean(y_tr))
        
    # RF
    rf_fold = RandomForestRegressor(n_estimators=50, max_depth=4, random_state=42).fit(X_train[tr_idx], y_tr)
    p_rf_fold = rf_fold.predict(X_train[va_idx])
    
    # Hybrid Blend
    p_blend_fold = 0.50 * p_ridge_fold + 0.30 * p_sarima_fold + 0.20 * p_rf_fold
    
    cv_rows.append({
        "Fold": fold + 1,
        "Train_Quarters": len(tr_idx),
        "Val_Quarters": len(va_idx),
        "Ridge_MAPE": round(float(np.mean(np.abs((y_va - p_ridge_fold) / y_va)) * 100.0), 2),
        "SARIMA_MAPE": round(float(np.mean(np.abs((y_va - p_sarima_fold) / y_va)) * 100.0), 2),
        "RF_MAPE": round(float(np.mean(np.abs((y_va - p_rf_fold) / y_va)) * 100.0), 2),
        "Hybrid_MAPE": round(float(np.mean(np.abs((y_va - p_blend_fold) / y_va)) * 100.0), 2),
    })

df_cv = pd.DataFrame(cv_rows)
df_cv.to_csv(METRICS_DIR / "walk_forward_cv_metrics.csv", index=False)
print("\n=== Walk-Forward Cross Validation Results ===")
print(df_cv.to_string(index=False))

# -------------------------------------------------------------------------
# 5. RESIDUAL DIAGNOSTICS FOR CHAMPION MODELS
# -------------------------------------------------------------------------
res_ridge = y_test - np.array(predictions["Ridge Regression"])
res_blend = y_test - np.array(predictions["Blended Hybrid Ensemble"])
res_sarima = y_test - np.array(predictions["SARIMA"])

dw_ridge = durbin_watson(res_ridge)
dw_blend = durbin_watson(res_blend)
dw_sarima = durbin_watson(res_sarima)

jb_stat_ridge, jb_p_ridge = stats.jarque_bera(res_ridge)
jb_stat_blend, jb_p_blend = stats.jarque_bera(res_blend)
jb_stat_sarima, jb_p_sarima = stats.jarque_bera(res_sarima)

lb_ridge = acorr_ljungbox(res_ridge, lags=[2, 4], return_df=True)
lb_blend = acorr_ljungbox(res_blend, lags=[2, 4], return_df=True)

diagnostics = {
    "Ridge_Regression": {
        "Durbin_Watson": round(float(dw_ridge), 3),
        "Jarque_Bera_Stat": round(float(jb_stat_ridge), 3),
        "Jarque_Bera_pValue": round(float(jb_p_ridge), 4),
        "Ljung_Box_Lag2_pValue": round(float(lb_ridge.loc[2, "lb_pvalue"]), 4),
        "Ljung_Box_Lag4_pValue": round(float(lb_ridge.loc[4, "lb_pvalue"]), 4),
    },
    "Blended_Hybrid_Ensemble": {
        "Durbin_Watson": round(float(dw_blend), 3),
        "Jarque_Bera_Stat": round(float(jb_stat_blend), 3),
        "Jarque_Bera_pValue": round(float(jb_p_blend), 4),
        "Ljung_Box_Lag2_pValue": round(float(lb_blend.loc[2, "lb_pvalue"]), 4),
        "Ljung_Box_Lag4_pValue": round(float(lb_blend.loc[4, "lb_pvalue"]), 4),
    },
    "SARIMA": {
        "Durbin_Watson": round(float(dw_sarima), 3),
        "Jarque_Bera_Stat": round(float(jb_stat_sarima), 3),
        "Jarque_Bera_pValue": round(float(jb_p_sarima), 4),
    }
}

with open(METRICS_DIR / "residual_diagnostics.json", "w") as f:
    json.dump(diagnostics, f, indent=2)

print("\n=== Residual Diagnostics ===")
print(json.dumps(diagnostics, indent=2))

# -------------------------------------------------------------------------
# 6. FEATURE IMPORTANCE & COEFFICIENTS
# -------------------------------------------------------------------------
feat_imp = []
for col, coef, imp in zip(feature_cols, ridge.coef_, rf.feature_importances_):
    feat_imp.append({
        "Feature": col,
        "Ridge_Coefficient": round(float(coef), 2),
        "RF_Importance": round(float(imp), 4)
    })
df_feat = pd.DataFrame(feat_imp).sort_values(by="RF_Importance", ascending=False)
df_feat.to_csv(METRICS_DIR / "feature_importance.csv", index=False)
print("\n=== Feature Importances & Ridge Coefficients ===")
print(df_feat.to_string(index=False))

# -------------------------------------------------------------------------
# 7. MULTI-SCENARIO FORWARD PROJECTIONS (2025 - 2027)
# -------------------------------------------------------------------------
# Train champion model on full dataset (56 quarters: 2011Q1 to 2024Q4)
X_all = df_q[feature_cols].values
y_all = df_q["fta_volume"].values

scaler_full = StandardScaler()
X_all_sc = scaler_full.fit_transform(X_all)

full_ridge = Ridge(alpha=10.0, random_state=42).fit(X_all_sc, y_all)
full_rf = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=3, random_state=42).fit(X_all, y_all)
full_sarima = SARIMAX(y_all, order=(1,0,1), seasonal_order=(0,1,1,4),
                      enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)

# Multi-step future simulation for 12 quarters: 2025Q1 to 2027Q4
scenarios = {
    "Baseline": {
        "description": "Historical trajectory, 4.5% global tourism growth, USD/INR reaching 89.5 by 2027",
        "usd_inr": [84.0, 84.5, 85.0, 85.5, 86.0, 86.5, 87.0, 87.5, 88.0, 88.5, 89.0, 89.5],
        "world_growth": 4.5,
        "growth_adj": 1.00
    },
    "Optimistic": {
        "description": "Incredible India 3.0, rapid e-Visa expansion, +6.5% global growth, USD/INR stable",
        "usd_inr": [83.5, 84.0, 84.5, 85.0, 85.5, 86.0, 86.5, 87.0, 87.5, 88.0, 88.5, 89.0],
        "world_growth": 6.5,
        "growth_adj": 1.06
    },
    "Pessimistic": {
        "description": "Geopolitical friction in South Asia, aviation fuel price spikes, +2.0% global growth",
        "usd_inr": [85.0, 86.0, 87.0, 88.0, 89.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0],
        "world_growth": 2.0,
        "growth_adj": 0.93
    }
}

future_quarters = []
for yr in [2025, 2026, 2027]:
    for q in [1, 2, 3, 4]:
        future_quarters.append((yr, q, f"{yr}Q{q}"))

sarima_full_forecast = full_sarima.get_forecast(steps=12)
sarima_future_mean = sarima_full_forecast.predicted_mean
sarima_ci = np.asarray(sarima_full_forecast.conf_int(alpha=0.05))

all_scenario_records = []

for sc_name, sc_info in scenarios.items():
    lags = list(y_all[-4:])  # last 4 quarters (2024Q1..Q4)
    adj = sc_info["growth_adj"]
    
    for i, (yr, q, q_lbl) in enumerate(future_quarters):
        q1_d = 1 if q == 1 else 0
        q2_d = 1 if q == 2 else 0
        q3_d = 1 if q == 3 else 0
        q4_d = 1 if q == 4 else 0
        usd_inr = sc_info["usd_inr"][i]
        w_growth = sc_info["world_growth"]
        
        # Build feature vector for ML models
        feat_vec = np.array([
            q1_d, q2_d, q3_d, q4_d,
            0, 0, 1,  # covid_shock=0, lockdown=0, recovery=1
            usd_inr, w_growth,
            lags[-1], lags[-2], lags[-4]
        ]).reshape(1, -1)
        
        feat_vec_sc = scaler_full.transform(feat_vec)
        
        pred_r = full_ridge.predict(feat_vec_sc)[0] * adj
        pred_rf = full_rf.predict(feat_vec)[0] * adj
        pred_s = sarima_future_mean[i] * adj
        
        # Blended forecast
        final_forecast = (0.50 * pred_r) + (0.30 * pred_s) + (0.20 * pred_rf)
        ci_lower = sarima_ci[i, 0] * adj * 0.95
        ci_upper = sarima_ci[i, 1] * adj * 1.05
        
        # Foreign exchange earnings projection (Yield per FTA = $3,518 expanding with inflation/rupee)
        projected_spend_per_fta_usd = 3518.59 * ((1 + 0.03) ** (yr - 2024))
        projected_fee_usd_m = (final_forecast * projected_spend_per_fta_usd) / 1e6
        projected_fee_inr_cr = (projected_fee_usd_m * 1e6 * usd_inr) / 1e7
        
        # Append for recursive next step
        lags.append(final_forecast)
        
        all_scenario_records.append({
            "scenario": sc_name,
            "year": yr,
            "quarter": q,
            "q_label": q_lbl,
            "projected_fta": round(float(final_forecast)),
            "ci_lower_95": round(float(ci_lower)),
            "ci_upper_95": round(float(ci_upper)),
            "projected_usd_inr": usd_inr,
            "fee_usd_million": round(float(projected_fee_usd_m), 1),
            "fee_inr_crore": round(float(projected_fee_inr_cr), 1)
        })

df_scenarios = pd.DataFrame(all_scenario_records)
df_scenarios.to_csv(DATA_DIR / "forecast_results_2025_2027.csv", index=False)

# Annual aggregates
annual_agg = df_scenarios.groupby(["scenario", "year"]).agg({
    "projected_fta": "sum",
    "fee_usd_million": "sum",
    "fee_inr_crore": "sum"
}).reset_index()

print("\n=== Annual Projected Tourism Demand (2025 - 2027) ===")
print(annual_agg.to_string(index=False))

# Save holdout comparison
df_holdout_compare = df_test[["year", "quarter", "q_label", "fta_volume"]].copy()
for m_name in predictions.keys():
    if m_name != "Actual":
        df_holdout_compare[m_name] = predictions[m_name]
df_holdout_compare.to_csv(METRICS_DIR / "holdout_predictions_comparison.csv", index=False)

# Summary JSON
summary = {
    "models_evaluated": list(predictions.keys())[1:],
    "benchmark_metrics": df_benchmark.to_dict(orient="records"),
    "walk_forward_cv": df_cv.to_dict(orient="records"),
    "residual_diagnostics": diagnostics,
    "feature_importances": df_feat.to_dict(orient="records"),
    "annual_scenario_projections": annual_agg.to_dict(orient="records")
}

with open(METRICS_DIR / "modeling_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nModel training, cross-validation, diagnostics, and multi-scenario forecasting completed successfully!")
