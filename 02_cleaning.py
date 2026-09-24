import pandas as pd
import numpy as np
import re

df = pd.read_csv('building-permits-active-permits.csv', low_memory=False)
print("Raw shape:", df.shape)

# 1. Drop fully-empty column
df = df.drop(columns=['COMPLETED_DATE'])

# 2. Parse dates
df['APPLICATION_DATE'] = pd.to_datetime(df['APPLICATION_DATE'], errors='coerce')
df['ISSUED_DATE'] = pd.to_datetime(df['ISSUED_DATE'], errors='coerce')

# 3. Clean EST_CONST_COST: strip commas, convert placeholder junk to NaN, coerce to float
def clean_cost(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if 'DO NOT' in s.upper():
        return np.nan
    s = s.replace(',', '').replace('$', '')
    try:
        return float(s)
    except ValueError:
        return np.nan

df['EST_CONST_COST'] = df['EST_CONST_COST'].apply(clean_cost)

# 4. Standardize CURRENT_USE / PROPOSED_USE text
def normalize_use(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip().lower()
    s = re.sub(r'[\s\-]+', ' ', s)  # collapse spaces/hyphens
    mapping = {
        'sfd': 'single family dwelling',
        'sfd detached': 'single family dwelling',
        'single family dwelling': 'single family dwelling',
        'sfd semi detached': 'single family dwelling (semi)',
        'sfd townhouse': 'single family dwelling (townhouse)',
    }
    return mapping.get(s, s)

df['CURRENT_USE_CLEAN'] = df['CURRENT_USE'].apply(normalize_use)
df['PROPOSED_USE_CLEAN'] = df['PROPOSED_USE'].apply(normalize_use)

# 5. Flag and remove impossible records (data integrity anomalies)
bad_dates = df['ISSUED_DATE'] < df['APPLICATION_DATE']
bad_units = df['DWELLING_UNITS_CREATED'] < 0
print(f"\nFlagging {bad_dates.sum()} rows with issued < application date")
print(f"Flagging {bad_units.sum()} rows with negative dwelling units created")
df['DATA_ANOMALY'] = bad_dates | bad_units.fillna(False)

# 6. Engineer key metric: processing time in days (Application -> Issued)
df['PROCESSING_DAYS'] = (df['ISSUED_DATE'] - df['APPLICATION_DATE']).dt.days
# Guard against the anomalies we flagged producing negative processing time
df.loc[df['DATA_ANOMALY'], 'PROCESSING_DAYS'] = np.nan

# 7. Extract time features for trend analysis
df['APPLICATION_YEAR'] = df['APPLICATION_DATE'].dt.year
df['APPLICATION_MONTH'] = df['APPLICATION_DATE'].dt.month
df['APPLICATION_QUARTER'] = df['APPLICATION_DATE'].dt.quarter

# 8. Standardize STATUS into broader groups for cleaner analysis
status_map = {
    'Inspection': 'In Progress',
    'Permit Issued': 'Issued',
    'Revision Issued': 'Issued',
    'Under Review': 'In Progress',
    'Work Not Started': 'Issued - Not Started',
    'Not Started': 'Issued - Not Started',
    'Issuance Pending': 'Pending',
    'Revocation Pending': 'Pending',
    'Application On Hold': 'On Hold',
    "Examiner's Notice Sent": 'In Progress',
}
df['STATUS_GROUP'] = df['STATUS'].map(status_map).fillna('Other')

print("\nCleaned shape:", df.shape)
print("\nProcessing time (days) describe:")
print(df['PROCESSING_DAYS'].describe())

print("\nSTATUS_GROUP distribution:")
print(df['STATUS_GROUP'].value_counts())

# Save cleaned dataset
df.to_csv('permits_cleaned.csv', index=False)
print("\nSaved cleaned dataset to permits_cleaned.csv")
