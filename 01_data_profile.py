import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 150)

df = pd.read_csv('building-permits-active-permits.csv', low_memory=False)

print("=" * 80)
print("SHAPE:", df.shape)
print("=" * 80)

print("\n--- DTYPES ---")
print(df.dtypes)

print("\n--- NULL COUNTS (% of rows) ---")
null_summary = pd.DataFrame({
    'nulls': df.isnull().sum(),
    'pct_null': (df.isnull().sum() / len(df) * 100).round(1)
})
print(null_summary[null_summary['nulls'] > 0].sort_values('pct_null', ascending=False))

print("\n--- DUPLICATE ROWS (full) ---")
print("Exact duplicate rows:", df.duplicated().sum())
print("Duplicate PERMIT_NUM:", df.duplicated(subset=['PERMIT_NUM']).sum())

print("\n--- CATEGORICAL COLUMN CARDINALITY ---")
cat_cols = ['PERMIT_TYPE', 'STRUCTURE_TYPE', 'WORK', 'STATUS', 'CURRENT_USE', 'PROPOSED_USE', 'STREET_TYPE', 'STREET_DIRECTION', 'WARD_GRID']
for c in cat_cols:
    if c in df.columns:
        print(f"\n{c}: {df[c].nunique()} unique values")
        print(df[c].value_counts(dropna=False).head(10))

print("\n--- DATE COLUMNS - RAW SAMPLE + RANGE ---")
for c in ['APPLICATION_DATE', 'ISSUED_DATE', 'COMPLETED_DATE']:
    print(f"\n{c}: dtype={df[c].dtype}")
    parsed = pd.to_datetime(df[c], errors='coerce')
    print(f"  parseable: {parsed.notna().sum()} / {len(df)}")
    print(f"  min: {parsed.min()}, max: {parsed.max()}")

print("\n--- EST_CONST_COST sample raw values (likely messy) ---")
print(df['EST_CONST_COST'].astype(str).sample(15, random_state=1).tolist())

print("\n--- DWELLING_UNITS_CREATED / LOST ---")
print(df[['DWELLING_UNITS_CREATED', 'DWELLING_UNITS_LOST']].describe())

print("\n--- Rows where ISSUED_DATE < APPLICATION_DATE (potential anomaly) ---")
app = pd.to_datetime(df['APPLICATION_DATE'], errors='coerce')
iss = pd.to_datetime(df['ISSUED_DATE'], errors='coerce')
print((iss < app).sum())
