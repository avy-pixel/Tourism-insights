# INTERNSHIP REMEDIATION ADDENDUM: QUANTITATIVE DATA QUALITY AUDIT & RISK MANAGEMENT ENGINEERING
**Addressing Instructor Feedback on Week 1 Submission**  
**Student Name**: Akshita | **Programme**: B.Tech Computer Science and Engineering  
**Institution**: Amritsar Group of Colleges  
**Project**: Yuva Internship - Tourism Data Science & Analytics (Week 1 Addendum)  
**Evaluator Score Addressed**: 40.2 / 100  

---

## 1. Executive Response to Instructor Feedback
The evaluator noted:
> *"The report is well-structured and covers most of the required deliverables, but it lacks specific data, worked examples, and original analysis. The sections on data quality issues and risk mitigation are shallow and generic. Improve by providing concrete numbers, detailed examples, and more thorough analysis."*

This document serves as an empirical upgrade to Sections 14 and 15 of the Week 1 report, providing concrete numbers, worked mathematical examples, table-by-table inconsistency documentation, and a formal Risk Priority Number (RPN) matrix backed by automated verification code.

---

## 2. Upgraded Section 14: Comprehensive Quantitative Data Quality Audit

### 14.1 Definition Divergence Trap: Quantifying the Distortion of FTAs vs NRIs vs ITAs
In tourism analytics, terminology conflation is the single largest source of policy error. The Ministry of Tourism records three distinct inbound metrics: Foreign Tourist Arrivals (**FTAs**, foreign passport holders), Non-Resident Indians (**NRIs**, Indian passport holders residing overseas), and International Tourist Arrivals (**ITAs** = FTAs + NRIs).

| Year | FTAs (Million) | NRIs (Million) | ITAs (Million) | NRI Share of ITAs (%) |
| :--- | :---: | :---: | :---: | :---: |
| **2014 (Series Start)** | 7.68 | 5.43 | 13.11 | 41.43% |
| **2019 (Pre-Pandemic)** | 10.93 | 6.98 | 17.91 | 38.98% |
| **2020 (Pandemic Shock)** | 2.74 | 3.59 | 6.33 | 56.68% |
| **2023 (Reopening)** | 9.51 | 9.38 | 18.89 | 49.66% |
| **2024 (Current P)** | 9.95 | 10.62 | 20.57 | 51.62% |

#### Worked Mathematical Example of Policy Distortion:
Suppose an econometrician calculates the post-pandemic recovery of Indian tourism in 2024 relative to the 2019 baseline. If they naively select the 'International Tourist Arrivals' (ITA) column (as published in PDF Table 1.1.2):
$$	ext{Naive ITA Recovery Ratio} = rac{20,568,622}{17,913,514} 	imes 100 = 114.82\% \quad (+14.82\% 	ext{ boom})$$
However, evaluating actual Foreign Tourist Arrivals (FTAs, foreign citizens) yields:
$$	ext{Actual FTA Recovery Ratio} = rac{9,951,722}{10,930,355} 	imes 100 = 91.05\% \quad (-8.95\% 	ext{ contraction})$$
$$	ext{Quantitative Error Magnitude} = 114.82\% - 91.05\% = +23.77 	ext{ percentage points!}$$

**Policy Hazard**: If the Ministry of Tourism or hospitality developers base infrastructure planning on the 114.8% figure, they conclude foreign leisure tourism has boomed, when in reality there is an active deficit of 978,633 foreign tourists that is entirely masked by a +52.0% surge in overseas diaspora visits (10.62M NRIs).

---

### 14.2 Global Receipts Accounting Discrepancy: The $7.50 Billion Surplus in Table 1.2.1
In PDF Table 1.2.1 (UN Tourism Receipts by Region), summing individual continental totals reveals an unexplained accounting discrepancy when evaluated against the printed World Total:

| Region / Sub-Region | Receipts 2019 (USD B) | Receipts 2023 (USD B) | Receipts 2024* (USD B) |
| :--- | :---: | :---: | :---: |
| **Europe** | $585.40 | $666.60 | $732.50 |
| **Asia and the Pacific** | $447.10 | $342.50 | $415.90 |
| **Americas** | $331.00 | $353.50 | $392.30 |
| **Middle East** | $90.30 | $136.80 | $147.60 |
| **Africa** | $48.50 | $45.50 | $50.20 |
| **Calculated Continental Sum** | **$1,502.30** | **$1,544.90** | **$1,738.50** |
| **Reported World Total in PDF** | **$1,487.00** | **$1,536.00** | **$1,731.00** |
| **Accounting Discrepancy (Delta)** | **+$15.30B (+1.03%)** | **+$8.90B (+0.58%)** | **+$7.50B (+0.43%)** |

**Root Cause & Mitigation**: Sub-regional figures within each continent sum with 100.0% precision to the continental total (e.g. Northern + Western + Central/Eastern + Southern Europe = 732.50B). The macro discrepancy arises because UN Tourism compiles national totals using different reporting systems (visitor surveys vs central bank balance of payments) and applies top-level global revisions that are not back-propagated into regional line items. **Mitigation**: When computing regional market shares, the calculated sum ($1,738.5B) must be used as the denominator to guarantee additive closure.

---

### 14.3 Cross-Table Inconsistencies and Typographical Parsing Hazards
1. **Four-Passenger Inconsistency in 2023 Totals**: PDF Table 2.1.3 (Top 15 Source Markets) reports total 2023 arrivals as **9,520,928**, whereas PDF Table 2.1.5 (Selected Countries) reports **9,520,924** ($\Delta = 4$ arrivals). While negligible in magnitude, this discrepancy causes database relational constraints to fail if primary key checksums are enforced.
2. **The China Zero-Imputation Bias**: In PDF Table 1.1.3, China's arrivals are reported as `"-"` for 2023 and 2024. If a standard pandas `fillna(0)` function is run, it records 0 Chinese tourists, falsely implying complete market extinction. Cross-referencing PDF Table 2.1.5 shows India received **30,585** Chinese arrivals in 2023 and **38,960** in 2024 (-88.52% vs 2019 baseline of 339,442). Imputing zero introduces a 38,960-unit measurement error.
3. **1,000x Monetary Typo in PDF Table 2.9.1**: The 2021 Foreign Exchange Earnings in US$ terms is printed as `"86,51"` instead of **8,651** Million US$. A standard string parser converting commas to decimals parses this as $86.51M rather than $8,651.0M—a catastrophic 100-fold error that invalidates economic growth models.
4. **Percentage Typo in PDF Table 2.4.4**: In the port distribution table, the North East regional share in the Grand Total row is printed as `"160"` instead of **1.60%**, introducing an obvious decimal omission.

---

## 3. Upgraded Section 15: Quantitative Risk Priority Number (RPN) Matrix & Mitigation Engineering

To replace generic risk descriptions with formal data engineering standards, we deploy the Failure Mode and Effects Analysis (FMEA) framework. Each risk is evaluated across three dimensions scored from 1 (lowest) to 5 (highest):
- **Severity (S)**: The severity of analytical distortion or policy misdirection if the failure occurs.
- **Likelihood (L)**: The empirical probability of encountering the failure in the raw dataset.
- **Detectability (D)**: How difficult the issue is to detect (1 = trivial to spot; 5 = silent, deeply buried flaw).
- **Risk Priority Number**: $RPN = S 	imes L 	imes D$ (Range: 1 to 125. Action Threshold: $RPN \ge 30$ requires automated architectural guardrails).

| Risk ID | Failure Mode / Risk | S | L | D | RPN | Engineered Programmatic Mitigation |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **R-01** | FTA vs ITA Metric Splicing (2014 break) | 5 | 5 | 2 | **50** | Enforce strict Pydantic schema validation: schema rejects any calculation joining pre-2014 FTA with post-2014 ITA without explicit user override. |
| **R-02** | Global Receipts Continental Sum Mismatch | 3 | 4 | 3 | **36** | Implement additive reconciliation layer: re-normalize regional shares against computed regional sum ($1,738.5B) rather than printed world total. |
| **R-03** | Missing Values Imputed as Zero (e.g. China) | 4 | 4 | 2 | **32** | Deploy three-valued logic: distinguish explicitly between NaN (unrecorded), NULL (inapplicable), and 0 (true zero count); log automated warning. |
| **R-04** | Extreme Covid Shock Skewing Time-Series | 5 | 5 | 1 | **25** | Dummy variable intervention: in Week 3 ARIMA/SARIMA models, encode 2020-2021 with step-intervention impulse variables to prevent forecast bias. |
| **R-05** | Cross-Table Record Discrepancies (Table 2.1.3 vs 2.1.5) | 2 | 4 | 2 | **16** | Design single-source-of-truth hierarchy: prioritize detailed country table 2.1.6 as canonical master dataset; flag delta variances in audit logs. |
| **R-06** | Typographical Parsing Errors (86,51 FEE typo) | 4 | 3 | 1 | **12** | Implement automated regex sanitization: `re.sub(r'(\d+),(\d{2})$', r'\1\2', val)` and cross-validate against YoY percentage change formula. |

### Automated Verification Pipeline Code:
```python
def validate_inbound_integrity(df_monthly, df_inbound):
    # 1. Additive ITA identity test across all 12 months
    monthly_sum = df_monthly['FTAs_2024'] + df_monthly['NRIs_2024']
    assert (monthly_sum == df_monthly['ITAs_2024']).all(), "CRITICAL: ITA Additive Identity Failed!"
    
    # 2. Reconcile monthly sum to annual total
    assert df_monthly['FTAs_2024'].sum() == 9951722, "CRITICAL: Annual FTA checksum failed!"
    
    # 3. Detect and correct monetary typographical anomalies
    clean_fee_2021 = int(str(df_inbound.loc[df_inbound['Year']==2021, 'FEE_USD_Million'].values[0]).replace(',', ''))
    assert clean_fee_2021 == 8651, "CRITICAL: FEE 2021 Typo detected!"
    
    print("All Automated Data Quality Audits Passed (100% Integrity)")
```
