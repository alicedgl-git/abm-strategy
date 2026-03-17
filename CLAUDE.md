# PandaDoc AI-Driven ABM Engine

## What This Is
An AI-powered Account-Based Marketing system built for Alice's PandaDoc Growth Marketing Specialist interview. The system analyzes a 150-lead dataset, discovers what converts, and builds a repeatable ABM engine with 4 deliverables.

## Project Structure
```
orchestrator.py          — Runs the full 4-agent pipeline
utils.py                 — Shared data loading, parsing, helpers
data/                    — Raw input data (funnel_leads.csv, funnel_summary.csv)
01_account_tiering/      — Agent 1: Account analysis, firmographic scoring, tiering
02_persona_and_messaging/ — Agent 2: Buyer committee mapping, messaging frameworks
03_strategy_and_plan/    — Agent 3: Channel strategy, 13-week quarterly plan
04_feedback_engine/      — Agent 4: Recalibration engine (feed new data, update model)
research/                — Research notes, charts, supporting analysis
```

Each numbered folder is a self-contained agent: the Python engine + the outputs it generates live together.

## How to Run
```bash
python3 orchestrator.py                                        # First run — full pipeline, saves weights
python3 orchestrator.py --input data/q2_leads.csv              # New data — recalibrates + shows before/after diff
python3 orchestrator.py --score data/demo_accounts.csv         # Score mode — score new accounts, output enriched CSV
/recalibrate data/q2_leads.csv                                 # Claude Code skill — runs train with new data
```

## Two Modes
- **Train mode** (default): Analyzes lead data, derives firmographic scoring weights, generates all reports. If previous weights exist (from an earlier run), automatically generates a recalibration report showing what changed — no separate command needed. Saves weights to `01_account_tiering/scoring_weights.json`.
- **Score mode** (`--score`): Loads trained weights, scores new accounts from any CSV, outputs `enriched_accounts.csv` with scores, tiers, personas, messaging angles, recommended content, and channels. This is the reusable workflow for teammates.

## Key Data Insights (from 150-lead analysis)
- **Baseline S1 rate:** 22% (33/150 leads converted to opportunity)
- **Top industries:** HR Tech (67%), Logistics (60%), Real Estate (40%)
- **Top CRM signal:** None/Spreadsheets (38%) and Pipedrive (38%) — displacement opportunity
- **Strongest engagement signal:** /integrations page visit (+12% lift)
- **Best channels:** Paid Social (43%), AppExchange (40%), Inbound (33%)
- **Dead channels:** Paid Search (0%), Partner (8%)

## Tiering Model (Firmographic Scoring by Expected Value, 100 pts max)
- Industry (30) + CRM (20) + Revenue (20) + Employee Band (15) + Country (15)
- Scoring uses **expected value** (conversion rate × avg ACV), not just conversion rate
- **T1 (score >= 60):** 21 accounts, 43% S1 rate — 1:1 strategic plays
- **T2 (score 40-59):** 77 accounts, 27% S1 rate — 1:few cluster plays
- **T3 (score < 40):** 52 accounts, 6% S1 rate — 1:many programmatic
- Behavioral signals (engagement, sales notes) tracked in Stage dimension, not tier score

## PandaDoc Context
- All-in-one document workflow: proposals + e-sign + payments + CRM integration
- Sweet spot: SMB/mid-market, 50-1000 employees, $10M-$100M revenue
- Median ACV ~$16K. Competitors: DocuSign, Proposify, Conga, Ironclad, Qwilr
- CRM integration (especially Salesforce/HubSpot) is the #1 differentiator
- Legal teams are the most common blocker in deals — address with compliance content

## Interview Context
- 30-40 minute presentation with Q&A
- Audience: Marketing leadership + Growth/RevOps team
- Format: HTML slides (reveal.js) — to be built after the engine
- Key emphasis: systems thinking, AI-human collaboration, recalibration
- "Show your work" — include prompts, automations, agents built
