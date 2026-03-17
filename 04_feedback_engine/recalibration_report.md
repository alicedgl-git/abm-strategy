# Recalibration Report

This report shows what changed when new data was fed into the ABM scoring model.
Every section compares **before** (old data) vs **after** (old + new data combined).

## 1. Dataset Growth

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total leads | 150 | 150 | +0 |
| S1 conversions | 33 | 33 | +0 |
| Baseline S1 rate | 22% | 22% | +0% |

## 2. Scoring Weight Changes

**32 weights adjusted** across the 5 firmographic dimensions.

| Dimension | Value | Before | After | Change |
|-----------|-------|--------|-------|--------|
| Industry | Logistics | 27 | 13 | -14 DOWN |
| Industry | Real Estate | 18 | 7 | -11 DOWN |
| Industry | Construction | 18 | 8 | -10 DOWN |
| Industry | Consulting | 17 | 7 | -10 DOWN |
| Industry | Legal | 11 | 20 | +9 UP |
| Crm | Monday CRM | 7 | 15 | +8 UP |
| Crm | None / Spreadsheets | 14 | 6 | -8 DOWN |
| Revenue | $25M – $100M | 13 | 20 | +7 UP |
| Industry | Technology | 10 | 4 | -6 DOWN |
| Revenue | $500M+ | 8 | 2 | -6 DOWN |
| Industry | Retail | 9 | 4 | -5 DOWN |
| Crm | Copper CRM | 11 | 16 | +5 UP |
| Country | Germany | 12 | 7 | -5 DOWN |
| Industry | Engineering | 11 | 7 | -4 DOWN |
| Industry | Healthcare | 5 | 1 | -4 DOWN |
| Revenue | $100M – $500M | 8 | 12 | +4 UP |
| Country | United Kingdom | 8 | 4 | -4 DOWN |
| Industry | Education | 6 | 3 | -3 DOWN |
| Industry | Media | 5 | 2 | -3 DOWN |
| Industry | SaaS | 8 | 5 | -3 DOWN |
| Crm | Freshsales | 3 | 0 | -3 DOWN |
| Crm | Zoho CRM | 9 | 12 | +3 UP |
| Revenue | $5M – $25M | 7 | 10 | +3 UP |
| Employee Band | 501–1,000 | 4 | 7 | +3 UP |
| Country | Australia | 4 | 7 | +3 UP |
| Crm | HubSpot | 4 | 2 | -2 DOWN |
| Crm | Pipedrive | 14 | 16 | +2 UP |
| Country | United States | 7 | 9 | +2 UP |
| Crm | Microsoft Dynamics | 4 | 3 | -1 DOWN |
| Crm | Salesforce | 3 | 2 | -1 DOWN |
| Revenue | < $5M | 6 | 5 | -1 DOWN |
| Employee Band | 201–500 | 8 | 9 | +1 UP |

## 3. Tier Mobility

Accounts that changed tier after re-scoring with the updated weights:

| Tier | Before | After | Change |
|------|--------|-------|--------|
| T1 | 10 accounts (70% S1) | 21 accounts (43% S1) | +11 |
| T2 | 79 accounts (30% S1) | 77 accounts (27% S1) | -2 |
| T3 | 61 accounts (3% S1) | 52 accounts (6% S1) | -9 |

### Promotions (32 accounts moved up)

| Company | Old Tier | New Tier | Old Score | New Score |
|---------|----------|----------|-----------|-----------|
| Axiom Legal Partners | T2 | T1 | 46 | 73 |
| Foxbrook Legal | T2 | T1 | 48 | 70 |
| Forgepoint Capital | T2 | T1 | 50 | 67 |
| Praxis Finance | T2 | T1 | 52 | 67 |
| Nordic Capital | T2 | T1 | 52 | 67 |
| Windfall Finance | T2 | T1 | 49 | 65 |
| Granite Financial | T2 | T1 | 56 | 62 |
| Pinnacle Legal | T2 | T1 | 45 | 62 |
| Terrace Consulting | T2 | T1 | 58 | 62 |
| Bastion Legal | T2 | T1 | 43 | 61 |
| Delphi Consulting | T2 | T1 | 54 | 61 |
| Broadleaf Consulting | T2 | T1 | 54 | 61 |
| Bridgeline Capital | T2 | T1 | 49 | 61 |
| Vantage Legal | T2 | T1 | 42 | 60 |
| Juncture Legal | T2 | T1 | 42 | 60 |
| Archway Legal | T3 | T2 | 39 | 55 |
| Meridian Education | T3 | T2 | 38 | 54 |
| Paragon Law | T3 | T2 | 39 | 54 |
| Keyframe Studios | T3 | T2 | 36 | 46 |
| Junction Finance | T3 | T2 | 38 | 46 |
| Zenova Capital | T3 | T2 | 39 | 45 |
| PeakFlow Inc | T3 | T2 | 38 | 44 |
| Upland Analytics | T3 | T2 | 38 | 44 |
| Pulse Analytics | T3 | T2 | 38 | 44 |
| Crestview Media | T3 | T2 | 38 | 43 |
| Kelvin Energy | T3 | T2 | 26 | 43 |
| Zenith Operations | T3 | T2 | 39 | 42 |
| Glyph Studios | T3 | T2 | 35 | 41 |
| Whitecap Insurance | T3 | T2 | 23 | 41 |
| Elara Health | T3 | T2 | 33 | 41 |
| Yarn Commerce | T3 | T2 | 39 | 40 |
| Frontier Insurance | T3 | T2 | 28 | 40 |

### Demotions (12 accounts moved down)

| Company | Old Tier | New Tier | Old Score | New Score |
|---------|----------|----------|-----------|-----------|
| Mast Logistics | T1 | T2 | 61 | 57 |
| Monarch Realty | T1 | T2 | 62 | 52 |
| Jetstream Logistics | T1 | T2 | 64 | 49 |
| Orbit Logistics | T1 | T2 | 61 | 47 |
| Motive Logistics | T2 | T3 | 49 | 39 |
| TerraFirm Construction | T2 | T3 | 40 | 38 |
| Radius Construction | T2 | T3 | 40 | 38 |
| Atlas Networks | T2 | T3 | 44 | 38 |
| Inkwell Publishing | T2 | T3 | 43 | 37 |
| Datum Analytics | T2 | T3 | 47 | 35 |
| Flint Engineering | T2 | T3 | 41 | 34 |
| Prism Analytics | T2 | T3 | 50 | 33 |

## 4. Channel & Engagement Shifts

### Channel Performance

| Channel | Before S1 Rate | After S1 Rate | Change |
|---------|---------------|---------------|--------|
| Appexchange | 40% (15 leads) | 40% (15 leads) | +0% |
| Content Syndication | 14% (14 leads) | 14% (14 leads) | +0% |
| Inbound | 33% (33 leads) | 33% (33 leads) | +0% |
| Intent Data | 10% (29 leads) | 10% (29 leads) | +0% |
| Outbound | 18% (17 leads) | 18% (17 leads) | +0% |
| Paid Search | 0% (7 leads) | 0% (7 leads) | +0% |
| Paid Social | 43% (7 leads) | 43% (7 leads) | +0% |
| Partner | 8% (13 leads) | 8% (13 leads) | +0% |
| Review Site | 29% (7 leads) | 29% (7 leads) | +0% |
| Webinar | 25% (8 leads) | 25% (8 leads) | +0% |

### Engagement Signal Effectiveness

| Engagement Action | Before Lift | After Lift | Change |
|-------------------|------------|------------|--------|
| Visited /integrations page | +12% | +12% | +0% |
| Opened 3+ emails | +11% | +11% | +0% |
| Downloaded contract template | +8% | +8% | +0% |
| Downloaded ROI guide | +7% | +7% | +0% |
| Visited pricing page | +4% | +4% | +0% |
| Requested a demo | +3% | +3% | +0% |
| Attended webinar | +2% | +2% | +0% |
| Started free trial | -1% | -1% | +0% |
| Visited competitor comparison page | -3% | -3% | +0% |
| Watched demo video | -3% | -3% | +0% |
| Reviewed G2 listing | -5% | -5% | +0% |

## 5. Messaging & Persona Shifts

### Messaging Theme Conversion

| Theme | Before | After | Change |
|-------|--------|-------|--------|
| Compliance focus | 43% (23 leads) | 43% (23 leads) | +0% |
| Manual process pain | 41% (49 leads) | 41% (49 leads) | +0% |
| Proposal automation | 33% (52 leads) | 33% (52 leads) | +0% |
| Integration focus | 31% (39 leads) | 31% (39 leads) | +0% |
| Cost/ROI focus | 29% (68 leads) | 29% (68 leads) | +0% |
| Competitor displacement | 26% (43 leads) | 26% (43 leads) | +0% |

### Persona Conversion

| Persona | Before S1 Rate | After S1 Rate | Before Avg ACV | After Avg ACV |
|---------|---------------|---------------|----------------|---------------|
| Champion / User Buyer | 25% | 25% | $12,764 | $12,764 |
| Economic Buyer | 26% | 26% | $12,836 | $12,836 |
| Executive Sponsor | 20% | 20% | $18,300 | $18,300 |
| Legal / Compliance | 5% | 5% | $55,100 | $55,100 |
| Marketing / Other | 25% | 25% | $9,600 | $9,600 |
| Technical Evaluator | 23% | 23% | $17,080 | $17,080 |

---
## Next Steps

The updated weights have been saved to `01_account_tiering/scoring_weights.json`.

To score new accounts with the improved model:
```
python3 orchestrator.py --score new_prospects.csv
```

To regenerate all reports with the updated data:
```
python3 orchestrator.py --input data/combined_leads.csv
```