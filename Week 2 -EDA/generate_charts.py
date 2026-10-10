import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

os.makedirs('Week 2 -EDA/visualizations', exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

df_global = pd.read_csv('Week 2 -EDA/data/global_tourism_trends.csv')
df_inbound = pd.read_csv('Week 2 -EDA/data/india_inbound_longterm.csv')
df_monthly = pd.read_csv('Week 2 -EDA/data/india_fta_monthly.csv')
df_top = pd.read_csv('Week 2 -EDA/data/india_fta_top_countries.csv')
df_regions = pd.read_csv('Week 2 -EDA/data/india_fta_regions.csv')
df_ports = pd.read_csv('Week 2 -EDA/data/india_fta_ports_modes.csv')

# 1. Global Arrivals vs Receipts Recovery
fig, ax = plt.subplots(figsize=(10, 6))
regions_plot = df_global[df_global['Sub_Region'] == 'Total'].copy()
x = np.arange(len(regions_plot))
width = 0.35

rects1 = ax.bar(x - width/2, regions_plot['Arrivals_Recovery_24_vs_19_pct'], width, label='Arrivals Recovery (% of 2019)', color='#2b5c8f')
rects2 = ax.bar(x + width/2, regions_plot['Receipts_Recovery_24_vs_19_pct'], width, label='Receipts Recovery (% of 2019)', color='#e26d5c')

ax.axhline(100, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='2019 Baseline (100%)')
ax.set_ylabel('Recovery Ratio (% of 2019 Level)', fontsize=12, fontweight='bold')
ax.set_title('Global Tourism Recovery: Tourist Volume vs Economic Receipts (2024 vs 2019)', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(regions_plot['Region'], fontsize=11)
ax.legend(frameon=True, facecolor='white', framealpha=0.9)
ax.grid(axis='y', linestyle=':', alpha=0.7)

for bar in rects1:
    h = bar.get_height()
    ax.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                textcoords='offset points', ha='center', va='bottom', fontsize=9, fontweight='bold')
for bar in rects2:
    h = bar.get_height()
    ax.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                textcoords='offset points', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#c0392b')

plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/01_global_arrivals_vs_receipts_recovery.png')
plt.close()
print('Chart 1 created successfully.')

# 2. India Inbound Long-Term Trend
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

p1 = ax1.plot(df_inbound['Year'], df_inbound['FTAs_Million'], color='#1f77b4', marker='o', linewidth=2.5, label='FTAs (Foreign Tourist Arrivals, Millions)')
p2 = ax1.plot(df_inbound['Year'], df_inbound['ITAs_Million'], color='#2ca02c', marker='s', linestyle='--', linewidth=2, label='ITAs (Total International Arrivals, Millions)')
p3 = ax2.plot(df_inbound['Year'], df_inbound['FEE_USD_Million'] / 1000, color='#d62728', marker='^', linewidth=2, label='Foreign Exchange Earnings (FEE, USD Billion)')

ax1.axvline(2014, color='purple', linestyle=':', alpha=0.8, linewidth=1.5)
ax1.annotate('2014 Series Break:\nInclusion of NRIs in ITAs', xy=(2014, 13.11), xytext=(2008, 16),
             arrowprops=dict(facecolor='purple', arrowstyle='->', lw=1.2), fontsize=10, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#f4ecf7', edgecolor='purple', alpha=0.9))

ax1.axvspan(2020, 2021, color='red', alpha=0.1, label='COVID-19 Disruption')
ax1.annotate('COVID-19 Shock:\nFTAs: -74.9% (2020)', xy=(2020.5, 2.5), xytext=(2017, 4),
             arrowprops=dict(facecolor='red', arrowstyle='->', lw=1.2), fontsize=9, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', edgecolor='red', alpha=0.9))

ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Arrivals (Millions)', fontsize=12, fontweight='bold', color='#1f77b4')
ax2.set_ylabel('FEE (USD Billion)', fontsize=12, fontweight='bold', color='#d62728')
ax1.set_title('India Inbound Tourism Trajectory & Economic Earnings (2001-2024)', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(df_inbound['Year'])
ax1.set_xticklabels(df_inbound['Year'], rotation=45, ha='right')

lines = p1 + p2 + p3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white')
ax1.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/02_india_inbound_longterm_trend_2001_2024.png')
plt.close()
print('Chart 2 created successfully.')

# 3. FTA vs NRI Composition & Share
df_comp = df_inbound.dropna(subset=['NRIs_Million']).copy()
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

x = np.arange(len(df_comp))
width = 0.55

bar1 = ax1.bar(x, df_comp['FTAs_Million'], width, label='Foreign Tourists (FTAs)', color='#3498db')
bar2 = ax1.bar(x, df_comp['NRIs_Million'], width, bottom=df_comp['FTAs_Million'], label='Non-Resident Indians (NRIs)', color='#e67e22')
line = ax2.plot(x, df_comp['NRI_Share_of_ITAs_pct'], color='#8e44ad', marker='D', linewidth=2.5, label='NRI Share of Total ITAs (%)')

ax1.set_ylabel('Total International Arrivals (Millions)', fontsize=12, fontweight='bold')
ax2.set_ylabel('NRI Share (%)', fontsize=12, fontweight='bold', color='#8e44ad')
ax1.set_xticks(x)
ax1.set_xticklabels(df_comp['Year'].astype(int), fontsize=10)
ax1.set_title('Composition of Inbound Tourism to India: FTAs vs NRIs (2014-2024)', fontsize=14, fontweight='bold', pad=15)

for i, row in df_comp.reset_index().iterrows():
    val = row['NRI_Share_of_ITAs_pct']
    ax2.annotate(f'{val:.1f}%', (i, val), xytext=(0, 6), textcoords='offset points', ha='center', fontsize=9, fontweight='bold', color='#8e44ad')

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', frameon=True, facecolor='white')

plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/03_fta_vs_nri_divergence_breakdown.png')
plt.close()
print('Chart 3 created successfully.')

# 4. Top Source Countries Recovery & Growth
df_top_sorted = df_top[df_top['Country'] != 'China'].sort_values('FTAs_2024', ascending=True).copy()
fig, ax = plt.subplots(figsize=(12, 8))

y = np.arange(len(df_top_sorted))
height = 0.38

bars19 = ax.barh(y - height/2, df_top_sorted['FTAs_2019'] / 1000, height, label='2019 FTAs (Thousands)', color='#95a5a6')
bars24 = ax.barh(y + height/2, df_top_sorted['FTAs_2024'] / 1000, height, label='2024 FTAs (Thousands)', 
                 color=['#27ae60' if r >= 100 else '#e74c3c' for r in df_top_sorted['Recovery_24_vs_19_pct']])

ax.set_yticks(y)
ax.set_yticklabels(df_top_sorted['Country'], fontsize=11, fontweight='bold')
ax.set_xlabel('Foreign Tourist Arrivals (Thousands)', fontsize=12, fontweight='bold')
ax.set_title('Top Source Markets for India: 2019 vs 2024 Recovery Benchmark', fontsize=14, fontweight='bold', pad=15)
ax.legend(loc='lower right', frameon=True, facecolor='white')

for i, (_, row) in enumerate(df_top_sorted.iterrows()):
    rec = row['Recovery_24_vs_19_pct']
    val = row['FTAs_2024'] / 1000
    color = '#27ae60' if rec >= 100 else '#c0392b'
    prefix = '+' if rec >= 100 else ''
    ax.annotate(f'{rec:.1f}% ({prefix}{rec-100:.1f}%)', xy=(val, i + height/2), xytext=(5, 0),
                textcoords='offset points', ha='left', va='center', fontsize=9, fontweight='bold', color=color)

ax.set_xlim(0, 2100)
ax.grid(axis='x', linestyle=':', alpha=0.7)
plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/04_top10_source_countries_recovery_waterfall.png')
plt.close()
print('Chart 4 created successfully.')

# 5. Regional Market Share Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
colors = ['#34495e', '#3498db', '#e67e22', '#2ecc71', '#9b59b6', '#bdc3c7']

wedges1, texts1, autotexts1 = ax1.pie(df_regions['Share_2019_pct'], labels=df_regions['Region'], autopct='%1.1f%%',
                                      startangle=140, colors=colors, pctdistance=0.75, textprops={'fontsize': 10})
centre_circle1 = plt.Circle((0,0), 0.55, fc='white')
ax1.add_artist(centre_circle1)
ax1.set_title('Source Region Share 2019\n(Total: 10.93 Million FTAs)', fontsize=12, fontweight='bold')

wedges2, texts2, autotexts2 = ax2.pie(df_regions['Share_2024_pct'], labels=df_regions['Region'], autopct='%1.1f%%',
                                      startangle=140, colors=colors, pctdistance=0.75, textprops={'fontsize': 10})
centre_circle2 = plt.Circle((0,0), 0.55, fc='white')
ax2.add_artist(centre_circle2)
ax2.set_title('Source Region Share 2024\n(Total: 9.95 Million FTAs)', fontsize=12, fontweight='bold')

for at in autotexts1 + autotexts2:
    at.set_fontsize(9)
    at.set_fontweight('bold')

fig.suptitle('Structural Rebalancing of India Inbound Tourism Source Markets (2019 vs 2024)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/05_regional_market_share_distribution.png')
plt.close()
print('Chart 5 created successfully.')

# 6. Monthly Seasonality Patterns
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

ax1.plot(df_monthly['Month'], df_monthly['FTAs_2019'] / 1000, label='2019 FTAs', color='#95a5a6', marker='o', linewidth=2)
ax1.plot(df_monthly['Month'], df_monthly['FTAs_2023'] / 1000, label='2023 FTAs', color='#f39c12', marker='^', linewidth=2)
ax1.plot(df_monthly['Month'], df_monthly['FTAs_2024'] / 1000, label='2024 FTAs', color='#2980b9', marker='s', linewidth=2.5)
ax1.set_ylabel('FTAs (Thousands)', fontsize=11, fontweight='bold')
ax1.set_title('Monthly Inbound Volume Trajectory (2019, 2023, 2024)', fontsize=12, fontweight='bold')
ax1.legend(loc='lower center', ncol=3, frameon=True, facecolor='white')
ax1.grid(True, linestyle=':', alpha=0.7)

ax2.plot(df_monthly['Month'], df_monthly['FTA_Seasonality_Index_2024'], label='FTA Seasonality Index (2024)',
         color='#2980b9', marker='s', linewidth=2.5)
ax2.plot(df_monthly['Month'], df_monthly['NRI_Seasonality_Index_2024'], label='NRI Seasonality Index (2024)',
         color='#e67e22', marker='D', linewidth=2.5)
ax2.axhline(100, color='black', linestyle='--', linewidth=1, label='Neutral Seasonality Index (100 = Monthly Average)')
ax2.set_ylabel('Seasonality Index (100 = Mean)', fontsize=11, fontweight='bold')
ax2.set_title('Seasonal Dichotomy: Foreign Tourists (Winter Peaks) vs NRIs (Summer/Holiday Peaks)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper right', frameon=True, facecolor='white')
ax2.grid(True, linestyle=':', alpha=0.7)

plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/06_monthly_seasonality_patterns_heatmaps.png')
plt.close()
print('Chart 6 created successfully.')

# 7. Mode of Travel Long-Term Evolution
fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(df_ports['Year'], df_ports['Air_pct'], marker='o', color='#2980b9', linewidth=2.5, label='Air Mode (%)')
ax.plot(df_ports['Year'], df_ports['Land_pct'], marker='s', color='#27ae60', linewidth=2.5, label='Land Mode (%)')
ax.plot(df_ports['Year'], df_ports['Water_pct'], marker='^', color='#e74c3c', linewidth=1.5, label='Water/Sea Mode (%)')

ax.set_title('Evolution of Inbound Travel Modes into India (2001-2024)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Share of Total FTAs (%)', fontsize=12, fontweight='bold')
ax.set_xticks(df_ports['Year'])
ax.set_xticklabels(df_ports['Year'], rotation=45, ha='right')
ax.legend(frameon=True, facecolor='white')
ax.grid(True, linestyle=':', alpha=0.7)

ax.annotate('Land Share Surge to 21.7%\nDriven by Bangladesh Border Crossings', xy=(2019, 21.7), xytext=(2014, 25),
            arrowprops=dict(facecolor='green', arrowstyle='->', lw=1.2), fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f8f5', edgecolor='green', alpha=0.9))

plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/07_mode_of_travel_longterm_evolution.png')
plt.close()
print('Chart 7 created successfully.')

# 8. Port Entry Concentration Pareto Chart
airports_data = [
    ('Delhi', 3224675, 38.85),
    ('Mumbai', 1557196, 18.76),
    ('Chennai', 814594, 9.81),
    ('Bengaluru', 696924, 8.40),
    ('Hyderabad', 394824, 4.76),
    ('Cochin', 372217, 4.48),
    ('Kolkata', 276667, 3.33),
    ('Ahmedabad', 219993, 2.65),
    ('Amritsar', 148237, 1.79),
    ('Tiruchirappalli', 116499, 1.40)
]
df_air = pd.DataFrame(airports_data, columns=['Airport', 'FTAs', 'Share_pct'])
df_air['Cumulative_Share'] = df_air['Share_pct'].cumsum()

fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

bars = ax1.bar(df_air['Airport'], df_air['FTAs'] / 1000, color='#34495e', width=0.55, label='Air Arrivals (Thousands)')
line = ax2.plot(df_air['Airport'], df_air['Cumulative_Share'], color='#e74c3c', marker='o', linewidth=2.5, label='Cumulative Share (%)')

ax1.set_ylabel('Air Arrivals (Thousands)', fontsize=12, fontweight='bold', color='#34495e')
ax2.set_ylabel('Cumulative Share (%)', fontsize=12, fontweight='bold', color='#e74c3c')
ax1.set_title('Pareto Analysis of Inbound Air Gateways (Top 10 Airports, 2024)', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(range(len(df_air)))
ax1.set_xticklabels(df_air['Airport'], rotation=30, ha='right', fontsize=10, fontweight='bold')
ax2.axhline(80, color='gray', linestyle=':', label='80% Pareto Threshold')

for i, row in df_air.iterrows():
    c_val = row['Cumulative_Share']
    ax2.annotate(f'{c_val:.1f}%', (i, c_val),
                 xytext=(0, 6), textcoords='offset points', ha='center', fontsize=9, fontweight='bold', color='#c0392b')

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2, labels1 + labels2, loc='center right', frameon=True, facecolor='white')

plt.tight_layout()
plt.savefig('Week 2 -EDA/visualizations/08_port_entry_concentration_pareto.png')
plt.close()
print('Chart 8 created successfully.')
