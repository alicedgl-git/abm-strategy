---
name: recalibrate
description: Recalibrate the ABM scoring model with new lead data. Use when new funnel data (CSV with S1 outcomes) arrives and you want to update the model. Shows before/after comparison of weights, tiers, channels, personas, and messaging themes.
argument-hint: <path-to-new-data.csv>
allowed-tools: Bash, Read, Write
---

# Recalibrate the ABM Scoring Model

Feed new lead data into the ABM engine and show what changed.

## What You Need

A CSV file with new lead data that includes S1 outcomes (conversions). The CSV should have the same format as `data/funnel_leads.csv` — with columns for Company, Industry, CRM, Revenue Range, Employee Band, Country, S1, and ideally Sales Notes and Engagement History.

## Steps

1. **Run the pipeline with the new data:**

```bash
cd "/Users/alicedoglioli/Desktop/ABM STRATEGY"
python3 orchestrator.py --input $ARGUMENTS
```

The system automatically detects that previous weights exist and generates a before/after recalibration report.

2. **Read the recalibration report** at `04_feedback_engine/recalibration_report.md` and summarize the key changes for the user:
   - How the dataset grew (old count vs new count)
   - Which scoring weights changed and in which direction
   - Which accounts changed tiers (promotions and demotions)
   - Any channel or messaging theme performance shifts

3. **Highlight the most important changes** — focus on:
   - Weight changes with the largest magnitude (these shift the most accounts)
   - Tier promotions/demotions (concrete impact on account strategy)
   - Any channel that flipped recommendation (e.g., PAUSE to INVEST)
   - New industries or CRMs that appeared in the data

4. **Remind the user** that:
   - Updated weights are saved to `01_account_tiering/scoring_weights.json`
   - They can score new prospects with the improved model: `python3 orchestrator.py --score new_prospects.csv`
   - They can run the pipeline again with even more data to keep improving

## If No CSV Path Is Provided

Ask the user for the path to their new data CSV. Remind them it needs S1 outcome columns to be useful for recalibration.
