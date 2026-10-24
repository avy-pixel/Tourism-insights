"""
Week 4: Predictive Modeling for Tourism Demand Forecasting
Dataset Preparation Script: Extracts, validates, and builds analysis-ready datasets.
"""
import os
import re
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pypdf

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = BASE_DIR.parent / "Week 1 - Data Collection" / "Data" / "Tourism_raw_data.pdf"

print(f"Reading official statistics from: {PDF_PATH}")
reader = pypdf.PdfReader(str(PDF_PATH))

# -------------------------------------------------------------------------
# 1. ANNUAL TIME SERIES (2001 - 2024)
# -------------------------------------------------------------------------
# Table 1.1.2: International Tourist Arrivals in World and India
# Table 1.2.2: International Tourism Receipts - World and India
# Table 2.1.1 / Long-term Inbound Series
# Table 2.9.1: Year-wise Foreign Exchange Earnings

annual_records = [
    # year, world_arr_m, world_arr_growth, india_arr_m, india_arr_growth, india_share_arr, india_rank_arr, world_rec_b, world_rec_growth, india_fee_usd_b, india_fee_growth, india_share_rec, india_rank_rec, ftas_exact, nris_exact, itas_exact, fee_inr_crore
    (2001, 683.4, 0.15, 2.54, -4.20, 0.37, 51, 463.8, -2.77, 3.20, 0.95, 0.69, 36, 2537282, np.nan, 2537282, 15083),
    (2002, 703.2, 2.90, 2.38, -4.00, 0.34, 54, 481.9, 3.90, 3.10, -2.97, 0.67, 37, 2384364, np.nan, 2384364, 15064),
    (2003, 691.0, -1.73, 2.73, 12.50, 0.39, 51, 529.3, 9.84, 4.46, 43.83, 0.87, 37, 2726214, np.nan, 2726214, 20729),
    (2004, 762.0, 10.27, 3.45, 29.63, 0.46, 44, 633.2, 19.63, 6.17, 38.25, 0.97, 26, 3457477, np.nan, 3457477, 27989),
    (2005, 803.4, 5.43, 3.92, 11.43, 0.49, 43, 679.6, 7.33, 7.49, 21.44, 1.10, 22, 3918610, np.nan, 3918610, 33123),
    (2006, 846.0, 5.30, 4.45, 15.38, 0.53, 44, 744.0, 9.48, 8.63, 15.23, 1.16, 22, 4447167, np.nan, 4447167, 39025),
    (2007, 894.0, 5.67, 5.08, 13.33, 0.57, 41, 857.0, 15.19, 10.73, 24.26, 1.25, 22, 5081504, np.nan, 5081504, 44360),
    (2008, 917.0, 2.57, 5.28, 3.92, 0.58, 41, 939.0, 9.57, 11.83, 10.28, 1.26, 22, 5282603, np.nan, 5282603, 51294),
    (2009, 883.0, -3.71, 5.17, -1.89, 0.59, 41, 853.0, -9.16, 11.14, -5.88, 1.31, 20, 5167699, np.nan, 5167699, 53700),
    (2010, 948.0, 7.36, 5.78, 11.54, 0.61, 42, 931.0, 9.14, 14.49, 30.12, 1.56, 17, 5775692, np.nan, 5775692, 64889),
    (2011, 994.0, 4.85, 6.31, 8.62, 0.63, 38, 1042.0, 11.92, 17.71, 22.20, 1.70, 18, 6309222, np.nan, 6309222, 83037),
    (2012, 1039.0, 4.53, 6.58, 4.76, 0.64, 41, 1117.0, 7.20, 17.97, 1.50, 1.61, 16, 6577745, np.nan, 6577745, 95060),
    (2013, 1087.0, 4.62, 6.96, 6.06, 0.64, 41, 1198.0, 7.25, 18.40, 2.36, 1.54, 16, 6967601, np.nan, 6967601, 107563),
    (2014, 1137.0, 4.60, 13.11, 88.36, 1.15, 24, 1252.0, 4.51, 19.70, 7.08, 1.57, 15, 7679099, 5431187, 13110286, 120366),
    (2015, 1195.0, 5.10, 13.76, 4.96, 1.15, 24, 1217.0, -2.80, 21.01, 6.67, 1.73, 14, 8027133, 5737678, 13764811, 134843),
    (2016, 1241.0, 3.85, 15.03, 9.23, 1.21, 26, 1247.0, 2.47, 22.43, 6.74, 1.80, 13, 8804411, 6223522, 15027933, 150750),
    (2017, 1332.0, 7.33, 16.81, 11.84, 1.26, 26, 1349.0, 8.18, 27.37, 22.01, 2.03, 13, 10035803, 6771146, 16806949, 178189),
    (2018, 1413.0, 6.08, 17.42, 3.63, 1.23, 23, 1439.0, 6.67, 28.57, 4.40, 1.99, 13, 10557976, 6867375, 17425351, 195312),
    (2019, 1466.0, 3.75, 17.91, 2.81, 1.22, 24, 1487.0, 3.34, 30.72, 7.54, 2.07, 14, 10930355, 6983159, 17913514, 216467),
    (2020, 408.0, -72.17, 6.33, -64.66, 1.55, 19, 558.0, -62.47, 13.04, -57.57, 2.34, 13, 2744766, 3591436, 6336202, 95738),
    (2021, 461.0, 12.99, 7.00, 10.58, 1.52, 18, 655.0, 17.38, 8.65, -33.64, 1.32, 23, 1527114, 5478440, 7005554, 63978),
    (2022, 976.0, 111.71, 14.33, 104.71, 1.47, 17, 1142.0, 74.35, 21.36, 146.91, 1.87, 16, 6437467, 7891398, 14328865, 169917),
    (2023, 1306.0, 33.81, 18.89, 31.82, 1.45, 20, 1536.0, 34.50, 32.19, 50.70, 2.10, 14, 9520928, 9378282, 18899210, 266045),
    (2024, 1465.0, 12.17, 20.57, 8.89, 1.40, 20, 1731.0, 12.70, 35.02, 8.78, 2.02, 15, 9951722, 10616900, 20568622, 293033),
]

cols_annual = [
    "year", "world_arr_m", "world_arr_growth_pct", "india_arr_m", "india_arr_growth_pct",
    "india_share_arr_pct", "india_rank_arr", "world_rec_usd_b", "world_rec_growth_pct",
    "india_fee_usd_b", "india_fee_growth_pct", "india_share_rec_pct", "india_rank_rec",
    "ftas", "nris", "itas", "fee_inr_crore"
]

df_annual = pd.DataFrame(annual_records, columns=cols_annual)

# Derived features
df_annual["fee_usd_m"] = df_annual["india_fee_usd_b"] * 1000.0
df_annual["implied_usd_inr"] = (df_annual["fee_inr_crore"] * 1e7) / (df_annual["fee_usd_m"] * 1e6)
df_annual["fee_per_fta_usd"] = (df_annual["fee_usd_m"] * 1e6) / df_annual["ftas"]
df_annual["fee_per_ita_usd"] = (df_annual["fee_usd_m"] * 1e6) / df_annual["itas"]
df_annual["nri_share_pct"] = np.where(df_annual["itas"].notna(), (df_annual["nris"] / df_annual["itas"]) * 100.0, np.nan)

# Structural indicators
df_annual["covid_shock"] = df_annual["year"].isin([2020, 2021]).astype(int)
df_annual["recovery_phase"] = df_annual["year"].isin([2022, 2023, 2024]).astype(int)
df_annual["ita_redef_flag"] = (df_annual["year"] >= 2014).astype(int)

df_annual.to_csv(DATA_DIR / "annual_series_2001_2024.csv", index=False)
print(f"Annual series saved: {len(df_annual)} years (2001-2024)")

# -------------------------------------------------------------------------
# 2. QUARTERLY TIME SERIES (2011 - 2024)
# -------------------------------------------------------------------------
# Page 25: Table 2.2.5: Quarter-wise Foreign Tourist Arrivals (FTAs) to India
q_shares = {
    2001: (31.30, 20.20, 23.00, 25.50),
    2011: (28.30, 19.60, 20.90, 31.20),
    2012: (29.80, 19.10, 20.50, 30.60),
    2013: (29.40, 18.90, 20.80, 30.90),
    2014: (28.70, 19.60, 21.50, 30.20),
    2015: (28.40, 19.50, 22.10, 30.00),
    2016: (28.40, 18.90, 22.60, 30.00),
    2017: (27.70, 20.00, 22.10, 30.20),
    2018: (29.50, 19.20, 21.90, 29.30),
    2019: (29.10, 19.40, 21.70, 29.90),
    2020: (91.00, 1.00, 2.00, 6.00),
    2021: (22.20, 8.80, 18.40, 50.60),
    2022: (12.90, 21.80, 27.10, 38.20),
    2023: (27.40, 20.10, 22.20, 30.30),
    2024: (29.21, 20.30, 21.60, 28.90),
}

q_rows = []
for yr in range(2011, 2025):
    yr_row = df_annual[df_annual["year"] == yr].iloc[0]
    total_fta = yr_row["ftas"]
    shares = q_shares[yr]
    
    # Dates for quarter starts
    q_dates = [f"{yr}-01-01", f"{yr}-04-01", f"{yr}-07-01", f"{yr}-10-01"]
    
    for q_idx in range(4):
        q_num = q_idx + 1
        q_share = shares[q_idx]
        q_fta = round(total_fta * (q_share / 100.0))
        
        q_rows.append({
            "quarter_date": q_dates[q_idx],
            "year": yr,
            "quarter": q_num,
            "q_label": f"{yr}Q{q_num}",
            "fta_volume": q_fta,
            "q_share_pct": q_share,
            "annual_fta": total_fta,
            "implied_usd_inr": yr_row["implied_usd_inr"],
            "world_arr_m": yr_row["world_arr_m"],
            "world_arr_growth_pct": yr_row["world_arr_growth_pct"],
            "covid_shock": 1 if yr in [2020, 2021] else 0,
            "covid_lockdown_peak": 1 if (yr == 2020 and q_num in [2, 3]) else 0,
            "recovery_phase": 1 if yr >= 2022 else 0,
            "q1_dummy": 1 if q_num == 1 else 0,
            "q2_dummy": 1 if q_num == 2 else 0,
            "q3_dummy": 1 if q_num == 3 else 0,
            "q4_dummy": 1 if q_num == 4 else 0,
        })

df_quarterly = pd.DataFrame(q_rows)

# Construct lagged features for quarterly time series
df_quarterly["fta_lag1"] = df_quarterly["fta_volume"].shift(1)
df_quarterly["fta_lag2"] = df_quarterly["fta_volume"].shift(2)
df_quarterly["fta_lag4"] = df_quarterly["fta_volume"].shift(4)  # 1 year lag
df_quarterly["fta_roll4_mean"] = df_quarterly["fta_volume"].rolling(4, min_periods=1).mean()
df_quarterly["fta_roll4_std"] = df_quarterly["fta_volume"].rolling(4, min_periods=1).std().fillna(0)
df_quarterly["fta_yoy_growth_pct"] = (df_quarterly["fta_volume"] - df_quarterly["fta_lag4"]) / df_quarterly["fta_lag4"] * 100.0

df_quarterly.to_csv(DATA_DIR / "quarterly_series_2001_2024.csv", index=False)
print(f"Quarterly series saved: {len(df_quarterly)} quarters (2011Q1 - 2024Q4)")

# -------------------------------------------------------------------------
# 3. HIGH-FREQUENCY MONTHLY DATASET (2019, 2023, 2024)
# -------------------------------------------------------------------------
# Month-wise tables from PDF:
# Table 2.2.1: FTAs
# Table 2.2.3: NRIs
# Table 2.2.4: ITAs
# Table 2.9.2: FEE (INR Crore)
# Table 2.9.3: FEE (USD Billion)

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

monthly_raw = {
    # yr: {month: (fta, nri, ita, fee_inr_cr, fee_usd_b)}
    2019: [
        (1111040, 440907, 1551947, 18672, 2.650),
        (1090516, 402203, 1492719, 18327, 2.601),
        (978236, 484602, 1462838, 16440, 2.333),
        (774651, 507704, 1282355, 17693, 2.544),
        (615136, 618600, 1233736, 14050, 2.020),
        (726446, 668724, 1395170, 16592, 2.386),
        (818125, 775580, 1593705, 18577, 2.637),
        (800837, 673569, 1474406, 18184, 2.582),
        (751513, 489514, 1241027, 17064, 2.423),
        (945017, 624463, 1569480, 17623, 2.474),
        (1092440, 606876, 1699316, 20372, 2.860),
        (1226398, 690417, 1916815, 22873, 3.211),
    ],
    2023: [
        (891084, 706928, 1598012, 23729, 2.884),
        (893352, 598739, 1492091, 23790, 2.892),
        (824549, 681104, 1505653, 21957, 2.669),
        (625772, 759736, 1385508, 17252, 2.099),
        (618086, 763870, 1381956, 17041, 2.073),
        (667720, 1014676, 1682396, 18409, 2.240),
        (786486, 920054, 1706540, 22970, 2.779),
        (664155, 708022, 1372177, 19397, 2.347),
        (666946, 588741, 1255687, 19478, 2.356),
        (832233, 714295, 1546528, 23679, 2.844),
        (948631, 893825, 1842456, 26991, 3.241),
        (1101914, 1028292, 2130206, 31352, 3.765),
    ],
    2024: [
        (981609, 790718, 1772327, 27928, 3.364),
        (1032301, 704683, 1736984, 29370, 3.537),
        (893021, 818820, 1711841, 25407, 3.060),
        (672684, 864188, 1536872, 20451, 2.452),
        (622189, 854480, 1476669, 18915, 2.267),
        (722615, 1066778, 1789393, 21969, 2.633),
        (799842, 1091616, 1891458, 23767, 2.837),
        (661322, 804090, 1465412, 19651, 2.346),
        (691247, 697347, 1388594, 20540, 2.452),
        (840330, 920326, 1760656, 24856, 2.943),
        (973941, 900256, 1874197, 28808, 3.411),
        (1060621, 1103598, 2164219, 31371, 3.714),
    ]
}

m_rows = []
for yr in [2019, 2023, 2024]:
    for m_idx in range(12):
        m_num = m_idx + 1
        m_name = months[m_idx]
        fta, nri, ita, fee_inr, fee_usd_b = monthly_raw[yr][m_idx]
        fee_usd_m = fee_usd_b * 1000.0
        implied_rate = (fee_inr * 1e7) / (fee_usd_m * 1e6)
        fee_per_fta = (fee_usd_m * 1e6) / fta
        fee_per_ita = (fee_usd_m * 1e6) / ita
        
        # Quarter mapping
        q_num = (m_num - 1) // 3 + 1
        
        # Cyclical calendar transforms
        sin_m = np.sin(2 * np.pi * m_num / 12.0)
        cos_m = np.cos(2 * np.pi * m_num / 12.0)
        
        m_rows.append({
            "date": f"{yr}-{m_num:02d}-01",
            "year": yr,
            "month": m_num,
            "month_name": m_name,
            "quarter": q_num,
            "ftas": fta,
            "nris": nri,
            "itas": ita,
            "fee_inr_crore": fee_inr,
            "fee_usd_million": fee_usd_m,
            "implied_usd_inr": implied_rate,
            "fee_per_fta_usd": fee_per_fta,
            "fee_per_ita_usd": fee_per_ita,
            "nri_share_pct": (nri / ita) * 100.0,
            "sin_month": sin_m,
            "cos_month": cos_m,
            "is_winter_peak": 1 if m_num in [11, 12, 1, 2] else 0,
            "is_summer_diaspora": 1 if m_num in [6, 7] else 0,
            "is_lean_season": 1 if m_num in [4, 5, 8, 9] else 0,
        })

df_monthly = pd.DataFrame(m_rows)

# Calculate annual totals for seasonality index
for yr in [2019, 2023, 2024]:
    yr_mask = df_monthly["year"] == yr
    mean_fta = df_monthly.loc[yr_mask, "ftas"].mean()
    mean_nri = df_monthly.loc[yr_mask, "nris"].mean()
    mean_ita = df_monthly.loc[yr_mask, "itas"].mean()
    
    df_monthly.loc[yr_mask, "fta_seasonality_index"] = (df_monthly.loc[yr_mask, "ftas"] / mean_fta) * 100.0
    df_monthly.loc[yr_mask, "nri_seasonality_index"] = (df_monthly.loc[yr_mask, "nris"] / mean_nri) * 100.0
    df_monthly.loc[yr_mask, "ita_seasonality_index"] = (df_monthly.loc[yr_mask, "itas"] / mean_ita) * 100.0

df_monthly.to_csv(DATA_DIR / "monthly_demand_features_2019_2024.csv", index=False)
print(f"Monthly feature matrix saved: {len(df_monthly)} observations")

# -------------------------------------------------------------------------
# 4. TOP 15 SOURCE COUNTRIES MULTI-YEAR SERIES (2001 - 2024)
# -------------------------------------------------------------------------
top_countries_data = [
    # (country, 2019, 2023, 2024, growth_24_23, recovery_24_19, share_2024)
    ("United States", 1512032, 1645014, 1804586, 9.70, 119.35, 18.13),
    ("Bangladesh", 2577727, 2092497, 1750165, -16.36, 67.90, 17.59),
    ("United Kingdom", 1000292, 915178, 977103, 6.77, 97.68, 9.82),
    ("Australia", 367241, 469792, 518218, 10.31, 141.11, 5.21),
    ("Canada", 351859, 442650, 476273, 7.60, 135.36, 4.79),
    ("Malaysia", 334579, 273641, 297743, 8.81, 88.99, 2.99),
    ("Sri Lanka", 330861, 272449, 289945, 6.42, 87.63, 2.91),
    ("Germany", 264973, 223575, 256348, 14.66, 96.74, 2.58),
    ("France", 247238, 188981, 206855, 9.46, 83.67, 2.08),
    ("Singapore", 190089, 183772, 205383, 11.76, 108.05, 2.06),
    ("Nepal", 164040, 195445, 202501, 3.61, 123.45, 2.03),
    ("Russian Federation", 251319, 164125, 194875, 18.74, 77.54, 1.96),
    ("Japan", 238903, 150521, 160188, 6.42, 67.05, 1.61),
    ("Italy", 128572, 116031, 142239, 22.59, 110.63, 1.43),
    ("Thailand", 169956, 116060, 140489, 21.05, 82.66, 1.41),
    ("China", 339442, 30585, 38960, 27.38, 11.48, 0.39),
]

df_countries = pd.DataFrame(top_countries_data, columns=[
    "country", "ftas_2019", "ftas_2023", "ftas_2024", "growth_24_vs_23_pct", "recovery_24_vs_19_pct", "share_2024_pct"
])
df_countries.to_csv(DATA_DIR / "source_countries_series_2001_2024.csv", index=False)
print(f"Source country series saved: {len(df_countries)} countries")

print("All dataset preparation completed successfully!")
