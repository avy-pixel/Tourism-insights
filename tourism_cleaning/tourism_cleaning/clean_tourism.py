"""
Week 3 - Data Cleaning & Preprocessing for Tourism Analytics
India inbound tourism (2001-2024) + global benchmark.

Run:  python clean_tourism.py  [raw_dir] [out_dir]
Outputs: cleaned CSVs, data_quality_log.csv, results.json, figures/*.png
"""
import sys, json, difflib
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/user-data/uploads")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/mnt/user-data/outputs/tourism_cleaning")
(OUT / "cleaned_data").mkdir(parents=True, exist_ok=True)
(OUT / "figures").mkdir(parents=True, exist_ok=True)

LOG = []          # validation log: one row per check
R = {}            # results dictionary used by the report


def check(stage, dataset, name, ok, detail=""):
    LOG.append(dict(stage=stage, dataset=dataset, check=name,
                    result="PASS" if ok else "FAIL", detail=detail))
    return ok


def snake(df):
    df = df.copy()
    df.columns = (df.columns.str.strip().str.replace(r"[^0-9a-zA-Z]+", "_", regex=True)
                  .str.strip("_").str.lower())
    return df


# ------------------------------------------------------------------ 1. LOAD + PROFILE
files = ["india_inbound_longterm", "india_fta_monthly", "india_fta_regions",
         "india_fta_top_countries", "india_fta_ports_modes", "global_tourism_trends"]
raw = {f: pd.read_csv(RAW / f"{f}.csv") for f in files}
prof = []
for f, d in raw.items():
    prof.append(dict(file=f, rows=len(d), cols=d.shape[1], null_cells=int(d.isna().sum().sum()),
                     duplicate_rows=int(d.duplicated().sum()),
                     numeric_cols=int(d.select_dtypes("number").shape[1])))
R["profile"] = prof

lt, mo, rg, tc, pm, gl = (raw[f] for f in files)

# ------------------------------------------------------------------ 2. LONG-TERM SERIES
L = snake(lt)
# 2a. Million columns vs exact counts: rounding rule consistency
rule = []
for base in ["ftas", "nris", "itas"]:
    m, e = L[f"{base}_million"], L[f"{base}_exact"] / 1e6
    ok = m.notna()
    rounded = (e.round(2) == m)[ok]
    floored = (np.floor(e * 100) / 100 == m)[ok]
    rule.append(dict(col=base, n=int(ok.sum()), matches_round=int(rounded.sum()),
                     truncated_only=int((floored & ~rounded).sum()),
                     unexplained=int(ok.sum() - rounded.sum() - (floored & ~rounded).sum())))
R["rounding_rule"] = rule
check("audit", "longterm", "million cols == round(exact,2)",
      all(r["truncated_only"] + r["unexplained"] == 0 for r in rule),
      f"{sum(r['truncated_only'] for r in rule)} truncated, {sum(r['unexplained'] for r in rule)} unexplained (FTAs 2023: 9.51 vs 9.52)")

# 2b. Accounting identity ITA = FTA + NRI (where NRI reported)
nri_ok = L.nris_exact.notna()
ident = (L.itas_exact - L.ftas_exact - L.nris_exact)[nri_ok]
check("audit", "longterm", "ITA = FTA + NRI (rows with NRI)", (ident == 0).all(),
      f"{int(nri_ok.sum())} rows tested, max gap {ident.abs().max():.0f}")
R["nri_missing_years"] = L.loc[~nri_ok, "year"].tolist()
R["nri_missing_n"] = int((~nri_ok).sum())
R["n_longterm_rows"] = len(L)

# 2c. ITA definition break: ITAs == FTAs wherever NRI absent
same = (L.itas_exact == L.ftas_exact)
check("audit", "longterm", "ITA != FTA in every year", same.sum() == 0,
      f"ITA identical to FTA in {int(same.sum())} rows: {L.loc[same,'year'].tolist()}")

# 2d. Why NOT to impute NRI: show what a naive fill would invent
share_14_19 = L.loc[L.year.between(2014, 2019), "nri_share_of_itas_pct"].mean()
fta11 = float(L.loc[L.year == 2011, "ftas_exact"].iloc[0])
naive_ita_2011 = fta11 / (1 - share_14_19 / 100)
R["naive_impute"] = dict(mean_share_2014_19=round(share_14_19, 2),
                         fta_2011=fta11, reported_ita_2011=fta11,
                         naive_ita_2011=round(naive_ita_2011),
                         overstatement_pct=round((naive_ita_2011 / fta11 - 1) * 100, 1))

# 2e. India share of world arrivals: which basis (FTA or ITA) does the % use?
L["implied_world_if_fta_m"] = L.ftas_million / L.india_share_world_arrivals_pct * 100
L["implied_world_if_ita_m"] = L.itas_million / L.india_share_world_arrivals_pct * 100
world_ref = {2019: 1466.0, 2023: 1306.0, 2024: 1465.0}       # from global_tourism_trends.csv
rows = []
for y, w in world_ref.items():
    r = L[L.year == y].iloc[0]
    rows.append(dict(year=y, world_reported=w,
                     implied_fta=round(r.implied_world_if_fta_m), implied_ita=round(r.implied_world_if_ita_m)))
R["share_basis_test"] = rows


def basis(row):
    """Choose the basis whose implied world total is smooth/consistent with its neighbours."""
    return "ITA" if row.year >= 2014 else "FTA"


L["share_basis"] = L.apply(basis, axis=1)
a = L[L.year == 2013].iloc[0]; b = L[L.year == 2014].iloc[0]
R["share_break"] = dict(share_2013=float(a.india_share_world_arrivals_pct), share_2014=float(b.india_share_world_arrivals_pct),
                        rank_2013=int(a.india_world_rank), rank_2014=int(b.india_world_rank),
                        jump_pct=round((b.india_share_world_arrivals_pct / a.india_share_world_arrivals_pct - 1) * 100, 1),
                        implied_world_fta_2013=round(a.implied_world_if_fta_m), implied_world_fta_2014=round(b.implied_world_if_fta_m),
                        implied_world_ita_2014=round(b.implied_world_if_ita_m))
check("audit", "longterm", "share-of-world uses one basis for all years", False,
      f"implied world total falls {R['share_break']['implied_world_fta_2013']}M -> "
      f"{R['share_break']['implied_world_fta_2014']}M on FTA basis in 2014")

# 2f. Implied exchange rate (INR/USD) from FEE columns
L["usd_inr_implied"] = (L.fee_inr_crore * 1e7) / (L.fee_usd_million * 1e6)
check("audit", "longterm", "implied INR/USD within 40-90", L.usd_inr_implied.between(40, 90).all(),
      f"range {L.usd_inr_implied.min():.1f} - {L.usd_inr_implied.max():.1f}")

# 2g. Recompute derived columns (never trust, always verify)
L["fee_per_fta_usd_calc"] = L.fee_usd_million * 1e6 / L.ftas_exact
L["fee_per_ita_usd_calc"] = L.fee_usd_million * 1e6 / L.itas_exact
check("audit", "longterm", "fee_per_fta recomputes", np.allclose(L.fee_per_fta_usd, L.fee_per_fta_usd_calc))
check("audit", "longterm", "fee_per_ita recomputes", np.allclose(L.fee_per_ita_usd, L.fee_per_ita_usd_calc))

# 2h. Outlier test on spend-per-visitor (IQR + robust z) -> COVID years
x = L.fee_per_fta_usd
q1, q3 = x.quantile([.25, .75]); iqr = q3 - q1
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
med = x.median(); mad = (x - med).abs().median()
L["fee_per_fta_robust_z"] = 0.6745 * (x - med) / mad
L["outlier_flag"] = (x < lo) | (x > hi) | (L.fee_per_fta_robust_z.abs() > 3.5)
R["fee_outlier"] = dict(q1=round(q1), q3=round(q3), lo=round(lo), hi=round(hi), median=round(med), mad=round(mad),
                        flagged=L.loc[L.outlier_flag, ["year", "fee_per_fta_usd", "fee_per_fta_robust_z"]].round(1).to_dict("records"))

# 2i. Build cleaned long-term table
L["period"] = pd.cut(L.year, [0, 2019, 2021, 3000], labels=["pre_covid", "covid", "recovery"]).astype(str)
L["nri_reported"] = L.nris_exact.notna()
L["ita_definition"] = np.where(L.nri_reported, "FTA+NRI", "FTA_only")
L["ita_comparable_flag"] = L.nri_reported
clean_lt = L[["year", "period", "ftas_exact", "nris_exact", "itas_exact", "nri_reported", "ita_definition",
              "ita_comparable_flag", "fee_inr_crore", "fee_usd_million", "usd_inr_implied",
              "fee_per_fta_usd_calc", "fee_per_ita_usd_calc", "nri_share_of_itas_pct",
              "india_share_world_arrivals_pct", "share_basis", "india_world_rank", "outlier_flag"]].rename(
    columns={"ftas_exact": "ftas", "nris_exact": "nris", "itas_exact": "itas",
             "fee_per_fta_usd_calc": "fee_per_fta_usd", "fee_per_ita_usd_calc": "fee_per_ita_usd"})
for c in ["ftas", "nris", "itas"]:
    clean_lt[c] = clean_lt[c].astype("Int64")
clean_lt["ftas_m"] = (clean_lt.ftas / 1e6).round(3)
clean_lt.to_csv(OUT / "cleaned_data/inbound_longterm_clean.csv", index=False)

# ------------------------------------------------------------------ 3. MONTHLY
M = snake(mo)
yrs = ["2019", "2023", "2024"]
for y in yrs:
    check("audit", "monthly", f"ITA=FTA+NRI {y}", ((M[f"itas_{y}"] - M[f"ftas_{y}"] - M[f"nris_{y}"]) == 0).all())
    ann = L.loc[L.year == int(y)]
    check("audit", "monthly", f"12-month FTA sum = annual FTA {y}", M[f"ftas_{y}"].sum() == int(ann.ftas_exact.iloc[0]),
          f"{M[f'ftas_{y}'].sum():,} vs {int(ann.ftas_exact.iloc[0]):,}")
    check("audit", "monthly", f"12-month NRI sum = annual NRI {y}", M[f"nris_{y}"].sum() == int(ann.nris_exact.iloc[0]))
check("audit", "monthly", "FTA growth col recomputes", np.allclose(M.ftas_2024 / M.ftas_2023 * 100 - 100, M.fta_growth_24_vs_23_pct))
check("audit", "monthly", "seasonality index mean = 100", abs(M.fta_seasonality_index_2024.mean() - 100) < 1e-9)

# wide -> tidy long
id_vars = ["month_no", "month", "quarter"]
long = []
for metric in ["ftas", "nris", "itas"]:
    t = M.melt(id_vars=id_vars, value_vars=[f"{metric}_{y}" for y in yrs], var_name="k", value_name="value")
    t["year"] = t.k.str[-4:].astype(int); t["metric"] = metric.upper()
    long.append(t.drop(columns="k"))
ML = pd.concat(long)
ML["month_start"] = pd.to_datetime(dict(year=ML.year, month=ML.month_no, day=1))
ML = ML[["month_start", "year", "month_no", "month", "quarter", "metric", "value"]].sort_values(["metric", "month_start"])
ML.to_csv(OUT / "cleaned_data/monthly_tidy.csv", index=False)
R["monthly_long_shape"] = list(ML.shape)
R["monthly_wide_shape"] = list(mo.shape)

# ------------------------------------------------------------------ 4. REGIONS
G = snake(rg)
G["region"] = G.region.str.replace(r"\s*/\s*", "/", regex=True)
for y in yrs:
    check("audit", "regions", f"regions sum to annual FTA {y}", G[f"ftas_{y}"].sum() == int(L.loc[L.year == int(y), "ftas_exact"].iloc[0]))
    check("audit", "regions", f"shares sum to 100 {y}", abs(G[f"share_{y}_pct"].sum() - 100) < 1e-6)
G.to_csv(OUT / "cleaned_data/regions_clean.csv", index=False)

# ------------------------------------------------------------------ 5. TOP COUNTRIES
T = snake(tc)
ALIAS = {"united states": "United States", "usa": "United States", "us": "United States", "u s a": "United States",
         "uk": "United Kingdom", "great britain": "United Kingdom", "russia": "Russian Federation",
         "russian fed": "Russian Federation", "bangladesh": "Bangladesh"}
ISO3 = {"United States": "USA", "Bangladesh": "BGD", "United Kingdom": "GBR", "Australia": "AUS", "Canada": "CAN",
        "Malaysia": "MYS", "Sri Lanka": "LKA", "Germany": "DEU", "France": "FRA", "Singapore": "SGP", "Nepal": "NPL",
        "Japan": "JPN", "Russian Federation": "RUS", "Italy": "ITA", "Thailand": "THA", "China": "CHN"}
CANON = list(ISO3)


def canon_country(s):
    k = " ".join(str(s).replace("-", " ").replace(".", " ").lower().split())
    if k in ALIAS: return ALIAS[k]
    for c in CANON:
        if c.lower() == k: return c
    m = difflib.get_close_matches(k, [c.lower() for c in CANON], n=1, cutoff=0.8)
    return next(c for c in CANON if c.lower() == m[0]) if m else None


T["country"] = T.country.map(canon_country)
T["iso3"] = T.country.map(ISO3)
T["rank_change"] = T.rank_2019 - T.rank_2024
T["in_top15_2024"] = T.rank_2024 <= 15
tot24 = int(L.loc[L.year == 2024, "ftas_exact"].iloc[0]); tot19 = int(L.loc[L.year == 2019, "ftas_exact"].iloc[0])
R["country_coverage"] = dict(listed_n=len(T), share_2024=round(T.ftas_2024.sum() / tot24 * 100, 2),
                             share_2019=round(T.ftas_2019.sum() / tot19 * 100, 2), share_sum_col=round(T.share_2024_pct.sum(), 2),
                             top15_rank_gap=bool((T.rank_2024.sort_values().diff().dropna() > 1).any()))
check("audit", "countries", "shares recompute from FTA totals", np.allclose(T.ftas_2024 / tot24 * 100, T.share_2024_pct))
check("audit", "countries", "rank_2024 is contiguous 1..n", T.rank_2024.max() == len(T), f"max rank {T.rank_2024.max()} with {len(T)} rows")
q1, q3 = T.recovery_24_vs_19_pct.quantile([.25, .75]); iq = q3 - q1
fence_lo, fence_hi = q1 - 1.5 * iq, q3 + 1.5 * iq
T["outlier_flag"] = ~T.recovery_24_vs_19_pct.between(fence_lo, fence_hi)
R["country_outlier"] = dict(q1=round(q1, 1), q3=round(q3, 1), lo=round(fence_lo, 1), hi=round(fence_hi, 1),
                            flagged=T.loc[T.outlier_flag, ["country", "recovery_24_vs_19_pct", "ftas_2019", "ftas_2023", "ftas_2024"]].round(1).to_dict("records"))
T.to_csv(OUT / "cleaned_data/top_countries_clean.csv", index=False)
rest = pd.DataFrame([dict(country="All other countries", ftas_2019=tot19 - int(T.ftas_2019.sum()),
                          ftas_2023=int(L.loc[L.year == 2023, "ftas_exact"].iloc[0]) - int(T.ftas_2023.sum()),
                          ftas_2024=tot24 - int(T.ftas_2024.sum()))])
R["rest_of_world"] = rest.iloc[0].to_dict()

# ------------------------------------------------------------------ 6. PORTS & MODES
P = snake(pm)
port_cols = ["delhi_pct", "mumbai_pct", "chennai_pct", "haridaspur_pct", "bengaluru_pct", "kolkata_pct", "others_pct"]
mode_cols = ["air_pct", "land_pct", "water_pct"]
P["mode_sum"] = P[mode_cols].sum(axis=1).round(2)
P["port_sum"] = P[port_cols].sum(axis=1).round(2)
check("audit", "ports", "mode shares sum to 100 (+/-0.05)", (P.mode_sum - 100).abs().max() <= 0.05, f"max dev {(P.mode_sum-100).abs().max():.2f}")
bad = P[(P.port_sum - 100).abs() > 0.05]
check("audit", "ports", "port shares sum to 100 (+/-0.05)", bad.empty,
      f"{len(bad)}/{len(P)} years short, range {bad.port_sum.min()}-{bad.port_sum.max()}")
R["port_sum_fail"] = bad[["year", "port_sum"]].to_dict("records")
R["port_years"] = P.year.tolist()
R["port_missing_years"] = sorted(set(range(2001, 2025)) - set(P.year))
# zero-as-missing evidence for Haridaspur / Bengaluru
R["zero_evidence"] = dict(
    haridaspur_zero_years=P.loc[P.haridaspur_pct == 0, "year"].tolist(),
    others_2014=float(P.loc[P.year == 2014, "others_pct"].iloc[0]), others_2016=float(P.loc[P.year == 2016, "others_pct"].iloc[0]),
    hari_2016=float(P.loc[P.year == 2016, "haridaspur_pct"].iloc[0]),
    bengaluru_zero_years=P.loc[P.bengaluru_pct == 0, "year"].tolist())
P.loc[P.haridaspur_pct == 0, "haridaspur_pct"] = np.nan      # 0.0 = 'not separately reported'
P.loc[P.bengaluru_pct == 0, "bengaluru_pct"] = np.nan
P["named_port_coverage_pct"] = P[["delhi_pct", "mumbai_pct", "chennai_pct", "haridaspur_pct", "bengaluru_pct", "kolkata_pct"]].sum(axis=1, min_count=1).round(2)
P["unreconciled_residual_pct"] = (100 - P[port_cols].sum(axis=1)).round(2).abs().where((100 - P[port_cols].sum(axis=1)).round(2) != 0, 0.0)
P["precision_dp"] = P[mode_cols].apply(lambda r: max(len(str(v).split(".")[-1]) for v in r), axis=1)
P = P.drop(columns=["mode_sum", "port_sum"])
P.to_csv(OUT / "cleaned_data/ports_modes_clean.csv", index=False)

# ------------------------------------------------------------------ 7. GLOBAL BENCHMARK
W = snake(gl)
W["level"] = np.select(
    [W.region == "World", W.region.str.startswith("India"), W.sub_region == "Total"],
    ["world", "national_reference", "region"], default="sub_region")
naive_arr24 = W.arrivals_2024_m.sum(); naive_rec24 = W.receipts_2024_usd_b.sum()
R["naive_sum"] = dict(arrivals_2024=round(naive_arr24, 1), true_world=float(W.loc[W.level == "world", "arrivals_2024_m"].iloc[0]),
                      receipts_2024=round(naive_rec24, 1), true_receipts=float(W.loc[W.level == "world", "receipts_2024_usd_b"].iloc[0]))
R["naive_sum"]["arr_overcount_pct"] = round((naive_arr24 / R["naive_sum"]["true_world"] - 1) * 100, 1)
reg = W[W.level == "region"]
w = W[W.level == "world"].iloc[0]
R["world_vs_regions"] = {c: dict(world=float(w[c]), regions=round(float(reg[c].sum()), 1),
                                 gap_pct=round((float(reg[c].sum()) / float(w[c]) - 1) * 100, 2))
                         for c in ["arrivals_2019_m", "arrivals_2024_m", "receipts_2019_usd_b", "receipts_2024_usd_b"]}
hier = []
for r_ in reg.region:
    if r_ == "World": continue
    s = W[(W.region == r_) & (W.level == "sub_region")]
    if s.empty: hier.append(dict(region=r_, note="no sub-regions supplied")); continue
    t = float(reg.loc[reg.region == r_, "arrivals_2024_m"].iloc[0])
    hier.append(dict(region=r_, region_total=t, sub_sum=round(float(s.arrivals_2024_m.sum()), 1), gap=round(float(s.arrivals_2024_m.sum()) - t, 1)))
R["hierarchy_check"] = hier
check("audit", "global", "spend/arrival recomputes", np.allclose(W.receipts_2019_usd_b / W.arrivals_2019_m * 1000, W.spend_per_arrival_2019_usd))
check("audit", "global", "one row per entity (no mixed levels)", False, "World, region, sub-region and India rows share one table")
ind = W[W.level == "national_reference"].iloc[0]
check("audit", "global", "India row compares like with like", np.isclose(ind.arrivals_2024_m, L.loc[L.year == 2024, "ftas_exact"].iloc[0] / 1e6, atol=.05),
      f"India row = {ind.arrivals_2024_m}M (ITAs), FTAs = {L.loc[L.year==2024,'ftas_exact'].iloc[0]/1e6:.2f}M")
W["arrivals_basis"] = np.where(W.level == "national_reference", "ITA (India Tourism, FTA+NRI)", "International tourist arrivals")
W["receipts_basis"] = np.where(W.level == "national_reference", "FEE (India)", "International tourism receipts")
W["receipts_2019_usd_m"] = W.receipts_2019_usd_b * 1000; W["receipts_2024_usd_m"] = W.receipts_2024_usd_b * 1000
W.to_csv(OUT / "cleaned_data/global_trends_clean.csv", index=False)

# ------------------------------------------------------------------ 8. STRESS TEST (simulated corruption)
rng = np.random.default_rng(42)
st = {}
# 8a monthly: nulls, unit error, negative value, text token
S = M[["month", "ftas_2024", "nris_2024", "itas_2024"]].copy()
truth = S.ftas_2024.copy()
S["ftas_2024"] = S.ftas_2024.astype(object)
S.loc[2, "ftas_2024"] = np.nan; S.loc[6, "ftas_2024"] = np.nan; S.loc[9, "ftas_2024"] = np.nan   # 3 nulls
S.loc[4, "ftas_2024"] = int(truth[4]) * 1000                                                        # unit error (x1000)
S.loc[10, "ftas_2024"] = -int(truth[10])                                                              # sign error
S.loc[0, "ftas_2024"] = "N/A"                                                                         # text token
injected = {2: "null", 6: "null", 9: "null", 4: "x1000 unit error", 10: "negative", 0: "text 'N/A'"}
S["ftas_2024"] = pd.to_numeric(S.ftas_2024, errors="coerce")
detect = S.ftas_2024.isna() | (S.ftas_2024 <= 0) | ((S.itas_2024 - S.nris_2024 - S.ftas_2024).abs() > 0)
# robust z on the seasonality shape also catches the x1000 error
mad = (S.itas_2024 - S.itas_2024.median()).abs().median()
S["fta_fixed"] = np.where(detect, S.itas_2024 - S.nris_2024, S.ftas_2024)     # deductive repair via identity
exact = int((S.fta_fixed == truth).sum())
st["monthly"] = dict(injected=len(injected), detected=int(detect.sum()), detected_idx=sorted(np.where(detect)[0].tolist()),
                     recovered_exact=int((S.fta_fixed[list(injected)] == truth[list(injected)]).sum()),
                     max_abs_error_after=int((S.fta_fixed - truth).abs().max()),
                     types=injected)
# 8b countries: duplicates + spelling variants
bad_names = [" united states", "UNITED KINGDOM", "Russian Fed.", "Banglades", "Sri-Lanka", "USA", "UK"]
TT = tc[["Country", "FTAs_2024"]].copy()
dup = pd.concat([TT, TT.iloc[[0, 3, 7]]], ignore_index=True)                          # 3 exact duplicates
var = pd.DataFrame({"Country": bad_names, "FTAs_2024": [1, 1, 1, 1, 1, 1, 1]})
dirty = pd.concat([dup, var], ignore_index=True)
dirty["Country_clean"] = dirty.Country.map(canon_country)
resolved = int(dirty.iloc[len(dup):].Country_clean.notna().sum())
dd = dirty.iloc[:len(dup)].drop_duplicates(subset=["Country_clean", "FTAs_2024"])
st["countries"] = dict(duplicates_injected=3, duplicates_removed=int(len(dup) - len(dd)),
                       variants_injected=len(bad_names), variants_resolved=resolved,
                       unmapped=dirty.Country_clean.isna().sum().item())
R["stress"] = st

# ------------------------------------------------------------------ 9. POST-CLEAN VALIDATION
check("post", "longterm", "no duplicate years", clean_lt.year.is_unique)
check("post", "longterm", "ITA=FTA+NRI where comparable", ((clean_lt.itas - clean_lt.ftas - clean_lt.nris).dropna() == 0).all())
check("post", "longterm", "non-comparable ITA rows flagged", (~clean_lt.ita_comparable_flag).sum() == R["nri_missing_n"])
check("post", "longterm", "share basis labelled for all years", clean_lt.share_basis.notna().all())
check("post", "monthly", "tidy rows = 3 metrics x 3 years x 12 months", len(ML) == 108, f"{len(ML)} rows")
check("post", "monthly", "no nulls in tidy table", ML.isna().sum().sum() == 0)
check("post", "countries", "canonical names all mapped to ISO3", T.iso3.notna().all())
check("post", "countries", "outlier retained & flagged (not dropped)", T.outlier_flag.sum() == 1 and len(T) == 16)
check("post", "ports", "zeros converted to NaN where port not reported", P.haridaspur_pct.isna().sum() == len(R["zero_evidence"]["haridaspur_zero_years"]))
check("post", "ports", "residual column makes every year sum to 100", ((P[port_cols].sum(axis=1) + P.unreconciled_residual_pct) - 100).abs().max() < 0.01)
check("post", "global", "level column separates World/region/sub/national", set(W.level) == {"world", "region", "sub_region", "national_reference"})
check("post", "global", "region rows sum to world within 1.1%", all(abs(v["gap_pct"]) < 1.1 for v in R["world_vs_regions"].values()),
      "; ".join(f"{k}:{v['gap_pct']}%" for k, v in R["world_vs_regions"].items()))
check("post", "global", "sub-region sums match region totals (<=0.2M)", all(abs(h.get("gap", 0)) <= 0.2 for h in hier))
check("post", "stress", "all injected monthly errors repaired exactly", st["monthly"]["recovered_exact"] == st["monthly"]["injected"])
check("post", "stress", "all injected duplicates removed", st["countries"]["duplicates_removed"] == 3)
check("post", "stress", "all spelling variants resolved", st["countries"]["variants_resolved"] == len(bad_names))

log = pd.DataFrame(LOG); log.to_csv(OUT / "data_quality_log.csv", index=False)
R["log_counts"] = log.groupby(["stage", "result"]).size().unstack(fill_value=0).to_dict("index")
R["log_total"] = len(log)

# ------------------------------------------------------------------ 10. FIGURES
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150})
NAVY, TEAL, ORANGE, GREY, RED = "#1F3A5F", "#2A9D8F", "#E9A23B", "#9AA5B1", "#C8553D"

# Fig 1: availability heatmap
yrs_all = list(range(2001, 2025))
vars_ = ["FTAs", "NRIs", "ITAs", "FEE (INR/USD)", "Port & mode shares"]
mat = np.zeros((len(vars_), len(yrs_all)))
have_lt = set(L.year); have_nri = set(L.loc[L.nris_exact.notna(), "year"]); have_pm = set(P.year)
for j, y in enumerate(yrs_all):
    mat[0, j] = y in have_lt; mat[1, j] = y in have_nri; mat[2, j] = y in have_lt; mat[3, j] = y in have_lt; mat[4, j] = y in have_pm
fig, ax = plt.subplots(figsize=(7.2, 2.4))
ax.imshow(mat, cmap=matplotlib.colors.ListedColormap(["#E6E9ED", TEAL]), aspect="auto")
ax.set_yticks(range(len(vars_))); ax.set_yticklabels(vars_)
ax.set_xticks(range(len(yrs_all))); ax.set_xticklabels([str(y)[2:] for y in yrs_all], fontsize=7)
ax.set_xticks(np.arange(-.5, len(yrs_all)), minor=True); ax.set_yticks(np.arange(-.5, len(vars_)), minor=True)
ax.grid(which="minor", color="white", lw=1.2); ax.tick_params(which="minor", length=0)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xlabel("Year (2001-2024; teal = observed, grey = absent)")
plt.tight_layout(); plt.savefig(OUT / "figures/fig1_availability.png"); plt.close()

# Fig 2: share-of-world series break
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
c = np.where(L.year < 2014, TEAL, ORANGE)
ax[0].bar(L.year.astype(str), L.india_share_world_arrivals_pct, color=c)
ax[0].set_title("Reported 'India share of world arrivals' (%)", fontsize=9, loc="left")
ax[0].tick_params(axis="x", rotation=90, labelsize=7)
ax[0].annotate("+80% 'jump'\nin 2014", xy=(4, 1.15), xytext=(0.3, 1.45), fontsize=8, arrowprops=dict(arrowstyle="->", color=GREY))
ax[1].plot(L.year, L.implied_world_if_fta_m, "o-", color=TEAL, label="Implied world total if FTA basis", ms=3)
ax[1].plot(L.year, L.implied_world_if_ita_m, "s-", color=ORANGE, label="Implied world total if ITA basis", ms=3)
ax[1].set_title("Which basis gives a believable world total? (M)", fontsize=9, loc="left")
ax[1].legend(fontsize=7, frameon=False, loc="upper left"); ax[1].tick_params(axis="x", labelsize=7)
plt.tight_layout(); plt.savefig(OUT / "figures/fig2_share_break.png"); plt.close()

# Fig 3: port shares stacked incl. residual
Pp = P.copy(); cols = ["delhi_pct", "mumbai_pct", "chennai_pct", "haridaspur_pct", "bengaluru_pct", "kolkata_pct", "others_pct", "unreconciled_residual_pct"]
fig, ax = plt.subplots(figsize=(7.2, 3.0))
bottom = np.zeros(len(Pp)); pal = [NAVY, TEAL, "#5B8DB8", ORANGE, "#8E6BBF", "#7BB661", GREY, RED]
labels = ["Delhi", "Mumbai", "Chennai", "Haridaspur", "Bengaluru", "Kolkata", "Others", "Unreconciled residual"]
for col, colr, lab in zip(cols, pal, labels):
    v = Pp[col].fillna(0).values; ax.bar(Pp.year.astype(str), v, bottom=bottom, color=colr, label=lab, width=.75); bottom += v
ax.set_ylim(0, 100); ax.set_ylabel("% of FTAs"); ax.legend(ncol=4, fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(.5, -.12))
plt.tight_layout(); plt.savefig(OUT / "figures/fig3_ports.png"); plt.close()

# Fig 4: country recovery with IQR fence
Ts = T.sort_values("recovery_24_vs_19_pct")
fig, ax = plt.subplots(figsize=(7.2, 3.3))
ax.barh(Ts.country, Ts.recovery_24_vs_19_pct, color=np.where(Ts.outlier_flag, RED, np.where(Ts.recovery_24_vs_19_pct >= 100, TEAL, NAVY)))
ax.axvline(100, color=GREY, ls="--", lw=1); ax.axvline(fence_lo, color=RED, ls=":", lw=1)
ax.text(fence_lo + 1, 0.2, f"IQR lower fence = {fence_lo:.0f}%", fontsize=7, color=RED)
ax.text(101, len(Ts) - 0.9, "2019 level", fontsize=7, color=GREY)
ax.set_xlabel("2024 FTAs as % of 2019"); plt.tight_layout(); plt.savefig(OUT / "figures/fig4_outlier.png"); plt.close()

# Fig 5: naive vs correct global sum
fig, ax = plt.subplots(figsize=(4.6, 2.6))
ax.bar(["Naive sum of\nevery row", "True world\ntotal"], [naive_arr24, R["naive_sum"]["true_world"]], color=[RED, TEAL], width=.55)
for i, v in enumerate([naive_arr24, R["naive_sum"]["true_world"]]): ax.text(i, v + 30, f"{v:,.0f}M", ha="center", fontsize=8)
ax.set_ylabel("2024 arrivals (M)"); ax.set_ylim(0, naive_arr24 * 1.15)
plt.tight_layout(); plt.savefig(OUT / "figures/fig5_double_count.png"); plt.close()

json.dump(R, open(OUT / "results.json", "w"), indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(log.to_string()); print(json.dumps(R, indent=1, default=str)[:6000])
