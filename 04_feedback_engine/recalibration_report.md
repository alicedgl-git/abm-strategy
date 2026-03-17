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

No weight changes. The model is stable — current weights are well-calibrated.

## 3. Tier Mobility

Accounts that changed tier after re-scoring with the updated weights:

| Tier | Before | After | Change |
|------|--------|-------|--------|
| T1 | 21 accounts (43% S1) | 21 accounts (43% S1) | +0 |
| T2 | 77 accounts (27% S1) | 77 accounts (27% S1) | +0 |
| T3 | 52 accounts (6% S1) | 52 accounts (6% S1) | +0 |

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