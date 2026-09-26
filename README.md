# Toronto Building Permits: Processing Time & Volume Analysis

**An exploratory data analysis of 205,000+ building permit records from the City of Toronto Open Data Portal**

## Executive Summary

- Permit application volume has nearly **quadrupled since 2010** (5,220 → 20,549 in 2025), with a sharp acceleration since 2021 — the city's permitting system is under growing load.
- Median approval time is **31 days**, but the distribution is heavily right-skewed (mean 100 days) — a small number of complex projects take years, dragging down average performance metrics.
- **Geographic inequity is severe**: the slowest ward (median 820 days) processes permits **68x slower** than the fastest ward (median 12 days), even after filtering to wards with 200+ permits for statistical reliability.
- Median processing time **rose from ~28 days (2010-2018) to ~46-49 days (2021-2023)**, coinciding with the volume surge, before easing slightly to 34 days in 2025 — suggestive of a capacity strain that the city has begun to address.
- Permit type drives timeline more than anything else: **New Building** permits take a median of 276 days vs. **19 days** for Small Residential Projects.

## Business Context

A building permit is formal city approval to construct, demolish, renovate, or add to a property. Permits move through five stages: Application → Review → Issue → Inspection → Close. This dataset (Toronto Open Data, "Building Permits — Active Permits") is refreshed daily and covers permits currently in process or closed within the last month.

**Who this matters to:** city planning/operations staff (capacity planning, service equity), contractors and developers (setting client expectations), real estate professionals and buyers (property history/renovation flags), and residents (transparency on municipal service delivery).

## Business Questions Answered

1. **Is permit demand growing?** Yes — application volume grew ~4x from 2010 to 2025, with the steepest growth 2021-2025.
2. **Which permit types take longest, and why does it matter?** New Building and New Houses permits take 4-9x longer than routine permits (plumbing, mechanical, small residential) — useful for setting applicant expectations by permit type.
3. **Is there seasonality?** Yes — applications peak in **May** (spring construction season) and are lowest in **January**, a ~35% swing.
4. **Which wards are underperforming on turnaround time?** A small number of wards (E2330, E2226, W0538) show median processing times of 360-820 days — 10-60x slower than the fastest wards — a strong candidate for a staffing/process audit.
5. **Has service level improved or worsened over time?** Processing time worsened notably 2019-2023 (coinciding with the demand surge and pandemic-era disruption), with early signs of improvement in 2024-2025.

## Data Quality Issues Found & How They Were Handled

| Issue | Handling |
|---|---|
| `COMPLETED_DATE` 100% null | Dropped column |
| `EST_CONST_COST` stored as text with commas and a literal placeholder string (`"DO NOT UPDATE OR DELETE THIS INFO FIELD"`) instead of null | Parsed to numeric, placeholder text converted to `NaN` |
| `CURRENT_USE` / `PROPOSED_USE` had 8,000-11,000+ inconsistent free-text variants of the same categories (e.g. `Sfd`, `Sfd-Detached`, `SFD Detached`) | Normalized via case-folding, whitespace/hyphen collapsing, and explicit mapping for top variants |
| 14 records with `ISSUED_DATE` before `APPLICATION_DATE` (logically impossible) | Flagged as data anomalies, excluded from processing-time calculations |
| 6 records with negative `DWELLING_UNITS_CREATED` | Flagged as data anomalies |
| `STATUS` had 51 raw values, too granular for trend analysis | Grouped into 6 categories (In Progress, Issued, Issued - Not Started, Pending, On Hold, Other) |
| 22,248 rows sharing a `PERMIT_NUM` | Confirmed as legitimate permit *revisions* (via `REVISION_NUM`), not duplicate records — kept as-is |

<img width="1383" height="754" alt="image" src="https://github.com/user-attachments/assets/75c09d81-47bb-41c6-be94-f6327af49dbc" />


## Repository Structure

```
├── README.md                          # This file
├── 01_data_profile.py                 # Data quality assessment
├── 02_cleaning.py                     # Cleaning & feature engineering
├── 03_eda.py                          # Exploratory analysis & business questions
├── permits_cleaned.csv                # Cleaned dataset
├── charts/
│   ├── 01_volume_by_year.png
│   ├── 02_processing_time_by_type.png
│   ├── 03_seasonality.png
│   ├── 04_ward_comparison.png
│   └── 05_processing_time_trend.png
└── requirements.txt
```

## Data Source

City of Toronto Open Data Portal — [Building Permits: Active Permits](https://open.toronto.ca/dataset/building-permits-active-permits/), refreshed daily, published under the Open Government Licence – Toronto.
