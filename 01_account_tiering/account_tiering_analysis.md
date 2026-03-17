# Account Tiering Model & Analysis Report

**Dataset:** 150 leads | 33 S1 conversions | Baseline rate: 22.0%

## Tier Summary
| Tier | Accounts | S1 Conversions | S1 Rate | Pipeline ACV |
|------|----------|----------------|---------|-------------|
| T1 | 21 | 9 | 43% | $236,900 |
| T2 | 77 | 21 | 27% | $230,000 |
| T3 | 52 | 3 | 6% | $20,600 |

## Scoring Methodology
Tier scores use **firmographic signals only** — these are the attributes available
for both training data and new accounts. Weights are derived from **expected value
(conversion rate × avg ACV)**, not just conversion rates or arbitrary assignments.

| Signal Category | Max Points | How It's Calculated |
|----------------|-----------|-------------------|
| Industry Fit | 30 | Conversion rate vs baseline. HR Tech 67% = 30pts, Insurance 0% = 0pts |
| CRM Fit | 20 | Mid-market CRMs (Copper, Pipedrive) = high EV, enterprise CRMs (Salesforce) = low EV |
| Revenue Fit | 20 | $25M-$100M = highest (30% convert), <$5M = lowest (14%) |
| Employee Band | 15 | 51-200 = highest (28% convert), 501-1000 = lowest (10%) |
| Country | 15 | Germany = highest (44% convert), France = lowest (0%) |
| **Total** | **100** | |

### Why firmographic-only scoring?
Behavioral signals (engagement actions, sales notes, funnel stage) are powerful
predictors — but they only exist for accounts already in our funnel. New accounts
entering the system have zero behavioral data. By scoring on firmographics alone,
the tiering model works identically for training data AND new accounts.

Behavioral signals are tracked separately in the **Stage** dimension (Identified →
Aware → Engaged → Considering → Selecting), managed through CRM workflows.
**Tier** (firmographic fit) tells us *what resources* to allocate.
**Stage** (behavioral progression) tells us *what to say and when*.

## Tier Thresholds
- **T1 (Strategic, 1:1):** Score >= 60 — Best firmographic fit, high-touch outreach
- **T2 (Growth, 1:few):** Score 40-59 — Good fit, industry-cluster campaigns
- **T3 (Scale, 1:many):** Score < 40 — Weaker fit, programmatic nurture

## Industry Conversion Analysis
| Industry | Leads | S1 | Rate | Score (/30) |
|----------|-------|-----|------|-------------|
| HR Tech | 6 | 4 | 67% | 30 |
| Logistics | 5 | 3 | 60% | 13 |
| Real Estate | 5 | 2 | 40% | 7 |
| Construction | 5 | 2 | 40% | 8 |
| Consulting | 8 | 3 | 38% | 7 |
| Financial Services | 18 | 5 | 28% | 13 |
| Engineering | 4 | 1 | 25% | 7 |
| Legal | 8 | 2 | 25% | 20 |
| Technology | 18 | 4 | 22% | 4 |
| Retail | 5 | 1 | 20% | 4 |
| SaaS | 17 | 3 | 18% | 5 |
| Education | 7 | 1 | 14% | 3 |
| Healthcare | 10 | 1 | 10% | 1 |
| Media | 10 | 1 | 10% | 2 |
| Professional Services | 2 | 0 | 0% | 0 |
| Manufacturing | 6 | 0 | 0% | 0 |
| Marketing Agency | 5 | 0 | 0% | 0 |
| Insurance | 7 | 0 | 0% | 0 |
| Energy | 4 | 0 | 0% | 0 |

## CRM Fit Analysis
| Current CRM | Leads | S1 | Rate | Score (/20) |
|-------------|-------|-----|------|-------------|
| Pipedrive | 13 | 5 | 38% | 16 |
| None / Spreadsheets | 21 | 8 | 38% | 6 |
| Copper CRM | 16 | 5 | 31% | 16 |
| Zoho CRM | 20 | 5 | 25% | 12 |
| Monday CRM | 20 | 4 | 20% | 15 |
| Microsoft Dynamics | 17 | 2 | 12% | 3 |
| HubSpot | 10 | 1 | 10% | 2 |
| Salesforce | 21 | 2 | 10% | 2 |
| Freshsales | 12 | 1 | 8% | 0 |

## Revenue Range Analysis
| Revenue Range | Leads | S1 | Rate | Score (/20) |
|---------------|-------|-----|------|-------------|
| $25M – $100M | 61 | 18 | 30% | 20 |
| $100M – $500M | 49 | 9 | 18% | 12 |
| $500M+ | 6 | 1 | 17% | 2 |
| $5M – $25M | 20 | 3 | 15% | 10 |
| < $5M | 14 | 2 | 14% | 5 |

## Employee Band Analysis
| Employee Band | Leads | S1 | Rate | Score (/15) |
|---------------|-------|-----|------|-------------|
| 1,001+ | 1 | 1 | 100% | 8 |
| 51–200 | 61 | 17 | 28% | 10 |
| 201–500 | 57 | 12 | 21% | 9 |
| 501–1,000 | 30 | 3 | 10% | 7 |
| 1–50 | 1 | 0 | 0% | 8 |

## Country Analysis
| Country | Leads | S1 | Rate | Score (/15) |
|---------|-------|-----|------|-------------|
| Germany | 9 | 4 | 44% | 7 |
| United Kingdom | 14 | 4 | 29% | 4 |
| United States | 82 | 20 | 24% | 9 |
| Australia | 13 | 2 | 15% | 7 |
| Canada | 25 | 3 | 12% | 3 |
| France | 7 | 0 | 0% | 0 |

## Behavioral Insights (Not in Tier Score)
These signals don't affect the tier score but inform the activation strategy.

### Channel Performance
| Channel | Leads | S1 | Rate |
|---------|-------|-----|------|
| Paid Social | 7 | 3 | 43% |
| Appexchange | 15 | 6 | 40% |
| Inbound | 33 | 11 | 33% |
| Review Site | 7 | 2 | 29% |
| Webinar | 8 | 2 | 25% |
| Outbound | 17 | 3 | 18% |
| Content Syndication | 14 | 2 | 14% |
| Intent Data | 29 | 3 | 10% |
| Partner | 13 | 1 | 8% |
| Paid Search | 7 | 0 | 0% |

### Engagement Signal Lift
| Action | S1 Rate | Non-S1 Rate | Lift |
|--------|---------|-------------|------|
| Visited /integrations page | 27% | 15% | +12% |
| Opened 3+ emails | 30% | 19% | +11% |
| Downloaded contract template | 30% | 22% | +8% |
| Downloaded ROI guide | 24% | 17% | +7% |
| Visited pricing page | 21% | 17% | +4% |
| Requested a demo | 24% | 21% | +3% |
| Attended webinar | 24% | 22% | +2% |
| Clicked LinkedIn ad | 24% | 24% | +0% |
| Started free trial | 18% | 20% | -1% |
| Visited competitor comparison page | 18% | 21% | -3% |
| Watched demo video | 18% | 21% | -3% |
| Reviewed G2 listing | 15% | 20% | -5% |

## How the Model Gets Refreshed
**Tier re-scoring** (firmographic weights change):
1. **Quarterly weight recalibration** — Feedback engine analyzes new S1 outcomes, recalculates conversion ratios, updates all 5 weight categories
2. **Firmographic change** — Company gets acquired, raises funding, headcount grows (via enrichment tools like Clay/Apollo) → re-score
3. **Growing dataset** — Each quarter, new funnel data (150 → 300 → 500 leads) makes weights more statistically reliable

**Stage progression** (behavioral, tracked in CRM):
1. Engagement event (pricing page, content download) → advance stage
2. Sales notes update (budget approved, competitor mentioned) → advance stage
3. Lifecycle stage change (MQL → SQL → Opportunity) → advance stage

## How AI Was Used
1. **Pattern Discovery:** Claude Code analyzed 150 leads across 7 dimensions to identify which firmographic attributes predict conversion
2. **Weight Derivation:** Each weight is mathematically derived: (segment_expected_value / baseline_expected_value) * multiplier, where expected value = conversion rate × avg ACV
3. **Separation of Concerns:** AI identified that behavioral signals shouldn't be in tier scores — they create a circular dependency (you need engagement to tier, but you need a tier to decide engagement strategy)
4. **Continuous Learning:** The feedback engine recalibrates weights as new conversion data arrives, and the model gets sharper with each cycle

## Top T1 Accounts
Total T1 accounts: 21

| Company | Score | Industry | Revenue | CRM | Country | S1? | ACV |
|---------|-------|----------|---------|-----|---------|-----|-----|
| Cornerstone HR | 85 | HR Tech | $25M – $100M | Copper CRM | United States | Yes | $55,100 |
| Pacific Staffing | 84 | HR Tech | $25M – $100M | Monday CRM | United States | Yes | $39,700 |
| Matrix Staffing | 79 | HR Tech | $25M – $100M | Copper CRM | Canada | Yes | $6,600 |
| Waverly HR | 75 | HR Tech | $25M – $100M | Zoho CRM | Canada | Yes | $19,000 |
| Axiom Legal Partners | 73 | Legal | $25M – $100M | Monday CRM | United States | Yes | $60,800 |
| Foxbrook Legal | 70 | Legal | $25M – $100M | Zoho CRM | United States | No | - |
| Forgepoint Capital | 67 | Financial Services | $25M – $100M | Monday CRM | United States | No | - |
| Praxis Finance | 67 | Financial Services | $25M – $100M | Copper CRM | United States | No | - |
| Nordic Capital | 67 | Financial Services | $25M – $100M | Copper CRM | United States | No | - |
| Grove Staffing | 66 | HR Tech | $25M – $100M | HubSpot | United Kingdom | No | - |
| Windfall Finance | 65 | Financial Services | $25M – $100M | Copper CRM | Australia | Yes | $25,300 |
| Lattice HR | 65 | HR Tech | $25M – $100M | HubSpot | Canada | No | - |
| Granite Financial | 62 | Financial Services | $25M – $100M | Pipedrive | United Kingdom | Yes | $10,500 |
| Pinnacle Legal | 62 | Legal | $25M – $100M | Microsoft Dynamics | United States | No | - |
| Terrace Consulting | 62 | Consulting | $25M – $100M | Copper CRM | United States | No | - |