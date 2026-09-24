import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['figure.dpi'] = 110
df = pd.read_csv('permits_cleaned.csv', low_memory=False,
                  parse_dates=['APPLICATION_DATE', 'ISSUED_DATE'])

CHART_DIR = 'charts'

# Restrict "current" trend analysis to reasonably complete years (drop partial 2026 and pre-2010 sparse years)
yearly = df[df['APPLICATION_YEAR'].between(2010, 2025)]

# ---- Q1: Has permit volume grown over time? ----
vol_by_year = yearly.groupby('APPLICATION_YEAR').size()
plt.figure(figsize=(9, 5))
vol_by_year.plot(kind='line', marker='o')
plt.title('Building Permit Applications by Year (Toronto)')
plt.xlabel('Year')
plt.ylabel('Number of Applications')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/01_volume_by_year.png')
plt.close()
print("Q1 - Volume by year:\n", vol_by_year, "\n")

# ---- Q2: Which permit types take longest to process? ----
top_types = df['PERMIT_TYPE'].value_counts().head(10).index
proc_by_type = (df[df['PERMIT_TYPE'].isin(top_types)]
                .groupby('PERMIT_TYPE')['PROCESSING_DAYS']
                .median().sort_values(ascending=False))
plt.figure(figsize=(9, 6))
proc_by_type.plot(kind='barh')
plt.title('Median Processing Time by Permit Type (Top 10 by Volume)')
plt.xlabel('Median Days: Application -> Issued')
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/02_processing_time_by_type.png')
plt.close()
print("Q2 - Median processing days by permit type:\n", proc_by_type, "\n")

# ---- Q3: Is there seasonality in applications? ----
seasonal = yearly.groupby('APPLICATION_MONTH').size()
plt.figure(figsize=(9, 5))
seasonal.plot(kind='bar', color='steelblue')
plt.title('Permit Applications by Month (2010-2025 combined)')
plt.xlabel('Month')
plt.ylabel('Number of Applications')
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/03_seasonality.png')
plt.close()
print("Q3 - Applications by month:\n", seasonal, "\n")

# ---- Q4: Which wards have the slowest approvals (min 200 permits for reliability)? ----
ward_stats = df.groupby('WARD_GRID').agg(
    n_permits=('PERMIT_NUM', 'count'),
    median_days=('PROCESSING_DAYS', 'median')
)
ward_stats = ward_stats[ward_stats['n_permits'] >= 200].sort_values('median_days', ascending=False)
print("Q4 - Slowest 10 wards (min 200 permits):\n", ward_stats.head(10))
print("\nFastest 10 wards (min 200 permits):\n", ward_stats.tail(10))

plt.figure(figsize=(9, 6))
pd.concat([ward_stats.head(8), ward_stats.tail(8)])['median_days'].sort_values().plot(kind='barh', color='coral')
plt.title('Median Processing Time: Slowest vs Fastest Wards (min 200 permits)')
plt.xlabel('Median Days')
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/04_ward_comparison.png')
plt.close()

# ---- Q5: Trend in processing time itself - improving or worsening? ----
proc_trend = yearly.groupby('APPLICATION_YEAR')['PROCESSING_DAYS'].median()
plt.figure(figsize=(9, 5))
proc_trend.plot(kind='line', marker='o', color='darkred')
plt.title('Median Processing Time by Application Year')
plt.xlabel('Year')
plt.ylabel('Median Days to Issue')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/05_processing_time_trend.png')
plt.close()
print("\nQ5 - Median processing days by year:\n", proc_trend)

print("\nAll charts saved to", CHART_DIR)
