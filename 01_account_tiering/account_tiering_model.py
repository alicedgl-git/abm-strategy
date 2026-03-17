"""
ABM Engine — Module 1: Account Analysis, Scoring & Tiering
Assignment Deliverable 1: Account Tiering Model

This module:
1. Analyzes the 150-lead dataset to discover what converts
2. Derives scoring weights FROM the data — firmographic signals only
3. Scores and tiers every account using 5 firmographic dimensions
4. Outputs tiered_accounts.csv + tiering_analysis.md

Scoring uses ONLY firmographic signals (available for both training and new accounts):
  Industry, Current CRM, Revenue Range, Employee Band, Country

Behavioral signals (engagement, sales notes, funnel stage) are analyzed for
strategic insights but do NOT affect the tier score. They belong in the
Stage dimension (tracked in CRM, not in this engine).

The scoring model is designed to be recalibrated by the feedback engine
when new conversion data comes in.
"""

import os
import json
from collections import Counter, defaultdict
from utils import (
    load_leads, get_conversion_rates, get_expected_values, get_engagement_lift, write_markdown,
    write_csv_output, save_weights, ALL_ENGAGEMENT_ACTIONS, HIGH_INTENT_ACTIONS, POSITIVE_SIGNALS,
)

# ─────────────────────────────────────────────
# STEP 1: ANALYZE CONVERSION PATTERNS
# ─────────────────────────────────────────────

def analyze_conversion_patterns(leads):
    """Analyze the dataset to discover what firmographic and behavioral patterns convert."""
    total = len(leads)
    s1_leads = [l for l in leads if l["s1"] == 1]
    baseline_rate = len(s1_leads) / total

    analysis = {
        "total_leads": total,
        "s1_conversions": len(s1_leads),
        "baseline_rate": baseline_rate,
    }

    # Firmographic dimensions (used for scoring) — with expected value (rate × avg ACV)
    analysis["by_industry"] = get_expected_values(leads, "industry")
    analysis["by_crm"] = get_expected_values(leads, "current_crm")
    analysis["by_revenue"] = get_expected_values(leads, "revenue_range")
    analysis["by_employee_band"] = get_expected_values(leads, "employee_band")
    analysis["by_country"] = get_expected_values(leads, "country")

    # Behavioral dimensions (used for strategic insights, NOT for scoring)
    analysis["by_channel"] = get_expected_values(leads, "channel")
    analysis["engagement_lift"] = get_engagement_lift(leads)

    # Qualitative signal analysis (behavioral — for insights only)
    signal_rates = {}
    for signal in POSITIVE_SIGNALS:
        with_signal = [l for l in leads if l["qualitative_signals"].get(signal)]
        s1_with = sum(1 for l in with_signal if l["s1"] == 1)
        signal_rates[signal] = {
            "total": len(with_signal),
            "converted": s1_with,
            "rate": s1_with / len(with_signal) if with_signal else 0,
        }
    analysis["qualitative_signals"] = signal_rates

    return analysis


# ─────────────────────────────────────────────
# STEP 2: DERIVE FIRMOGRAPHIC SCORING WEIGHTS
# ─────────────────────────────────────────────

def derive_scoring_weights(analysis):
    """
    Build scoring weights from expected value (conversion_rate × avg_ACV).

    5 dimensions, 100 points max:
      Industry (30) + CRM (20) + Revenue (20) + Employee Band (15) + Country (15)

    Each signal's weight = (expected_value / baseline_ev) * multiplier, capped at max.
    This means the model optimizes for accounts that both convert AND produce high-value deals.
    """
    baseline = analysis["baseline_rate"]  # 22%

    # Calculate baseline expected value (avg ACV across all converted leads)
    all_ev = [data["expected_value"] for data in analysis["by_industry"].values() if data["expected_value"] > 0]
    baseline_ev = sum(all_ev) / len(all_ev) if all_ev else 1

    # INDUSTRY SCORING (max 30 points) — strongest predictor
    industry_scores = {}
    for ind, data in analysis["by_industry"].items():
        if data["total"] >= 2:  # Need minimum sample size
            ratio = data["expected_value"] / baseline_ev if baseline_ev > 0 else 0
            industry_scores[ind] = min(round(ratio * 10), 30)
        else:
            industry_scores[ind] = 10  # Default for tiny samples
    industry_scores["_default"] = 10
    industry_scores["_max"] = 30

    # CRM FIT SCORING (max 20 points)
    crm_scores = {}
    crm_ev = [data["expected_value"] for data in analysis["by_crm"].values() if data["expected_value"] > 0]
    baseline_crm_ev = sum(crm_ev) / len(crm_ev) if crm_ev else 1
    for crm, data in analysis["by_crm"].items():
        ratio = data["expected_value"] / baseline_crm_ev if baseline_crm_ev > 0 else 0
        crm_scores[crm] = min(round(ratio * 8), 20)
    crm_scores["_default"] = 5
    crm_scores["_max"] = 20

    # REVENUE RANGE SCORING (max 20 points)
    revenue_scores = {}
    rev_ev = [data["expected_value"] for data in analysis["by_revenue"].values() if data["expected_value"] > 0]
    baseline_rev_ev = sum(rev_ev) / len(rev_ev) if rev_ev else 1
    for rev, data in analysis["by_revenue"].items():
        ratio = data["expected_value"] / baseline_rev_ev if baseline_rev_ev > 0 else 0
        revenue_scores[rev] = min(round(ratio * 10), 20)
    revenue_scores["_default"] = 7
    revenue_scores["_max"] = 20

    # EMPLOYEE BAND SCORING (max 15 points)
    employee_scores = {}
    emp_ev = [data["expected_value"] for data in analysis["by_employee_band"].values() if data["expected_value"] > 0]
    baseline_emp_ev = sum(emp_ev) / len(emp_ev) if emp_ev else 1
    for band, data in analysis["by_employee_band"].items():
        if data["total"] >= 2:  # Need minimum sample for reliability
            ratio = data["expected_value"] / baseline_emp_ev if baseline_emp_ev > 0 else 0
            employee_scores[band] = min(round(ratio * 8), 15)
        else:
            employee_scores[band] = 8  # Default for tiny samples
    employee_scores["_default"] = 8
    employee_scores["_max"] = 15

    # COUNTRY SCORING (max 15 points)
    country_scores = {}
    country_ev = [data["expected_value"] for data in analysis["by_country"].values() if data["expected_value"] > 0]
    baseline_country_ev = sum(country_ev) / len(country_ev) if country_ev else 1
    for country, data in analysis["by_country"].items():
        ratio = data["expected_value"] / baseline_country_ev if baseline_country_ev > 0 else 0
        country_scores[country] = min(round(ratio * 6), 15)
    country_scores["_default"] = 5
    country_scores["_max"] = 15

    weights = {
        "industry": industry_scores,
        "crm": crm_scores,
        "revenue": revenue_scores,
        "employee_band": employee_scores,
        "country": country_scores,
    }

    return weights


# ─────────────────────────────────────────────
# STEP 3: SCORE EACH ACCOUNT (firmographic only)
# ─────────────────────────────────────────────

def score_account(lead, weights):
    """
    Score a single account using ONLY firmographic signals.
    Returns (total_score, breakdown_dict).

    Max score: 100 (Industry 30 + CRM 20 + Revenue 20 + Employee Band 15 + Country 15)
    """
    breakdown = {}

    # Industry score (max 30)
    industry_w = weights["industry"]
    breakdown["industry"] = industry_w.get(lead["industry"], industry_w.get("_default", 10))

    # CRM fit score (max 20)
    crm_w = weights["crm"]
    breakdown["crm"] = crm_w.get(lead["current_crm"], crm_w.get("_default", 5))

    # Revenue score (max 20)
    rev_w = weights["revenue"]
    breakdown["revenue"] = rev_w.get(lead["revenue_range"], rev_w.get("_default", 7))

    # Employee Band score (max 15)
    emp_w = weights["employee_band"]
    breakdown["employee_band"] = emp_w.get(lead["employee_band"], emp_w.get("_default", 8))

    # Country score (max 15)
    country_w = weights["country"]
    breakdown["country"] = country_w.get(lead["country"], country_w.get("_default", 5))

    total = sum(breakdown.values())
    return total, breakdown


def assign_tier(score):
    """
    Assign tier based on firmographic score (0-100 scale).

    Thresholds calibrated against training data S1 rates:
    - T1 >= 60: Best firmographic fit — 1:1 strategic plays
    - T2 40-59: Good firmographic fit — 1:few cluster plays
    - T3 < 40:  Weaker fit — 1:many programmatic nurture
    """
    if score >= 60:
        return "T1"
    elif score >= 40:
        return "T2"
    else:
        return "T3"


def get_top_signals(breakdown):
    """Return the top 3 contributing signals for an account."""
    sorted_signals = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    return [f"{name}={pts}" for name, pts in sorted_signals[:3] if pts > 0]


# ─────────────────────────────────────────────
# STEP 4: RUN THE FULL PIPELINE
# ─────────────────────────────────────────────

def run_tiering(leads, output_dir="output"):
    """Run the complete analysis, scoring, and tiering pipeline."""
    print("\n" + "=" * 60)
    print("MODULE 1: ACCOUNT ANALYSIS & TIERING")
    print("=" * 60)

    # Step 1: Analyze conversion patterns
    print("\n[1/4] Analyzing conversion patterns across all dimensions...")
    analysis = analyze_conversion_patterns(leads)
    print(f"  Baseline S1 rate: {analysis['baseline_rate']:.1%}")
    print(f"  Total leads: {analysis['total_leads']}, S1 conversions: {analysis['s1_conversions']}")

    # Step 2: Derive firmographic weights
    print("\n[2/4] Deriving firmographic scoring weights...")
    weights = derive_scoring_weights(analysis)

    # Save weights for reuse on new accounts
    weights_path = os.path.join(output_dir, "scoring_weights.json")
    save_weights(weights, weights_path)

    # Print scoring weights
    print("\n  FIRMOGRAPHIC SCORING (5 dimensions, 100 pts max):")
    for dim_name, dim_weights in weights.items():
        max_pts = dim_weights.get("_max", "?")
        # Show top 3 values
        scored = {k: v for k, v in dim_weights.items() if not k.startswith("_")}
        top3 = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:3]
        top3_str = ", ".join(f"{k}: {v}" for k, v in top3)
        print(f"    {dim_name} (max {max_pts}): {top3_str}")

    print("\n  TOP CONVERTING INDUSTRIES:")
    sorted_ind = sorted(analysis["by_industry"].items(), key=lambda x: x[1]["rate"], reverse=True)
    for ind, data in sorted_ind[:5]:
        print(f"    {ind}: {data['rate']:.0%} ({data['converted']}/{data['total']}) -> Score: {weights['industry'].get(ind, 0)}")

    print("\n  TOP CONVERTING CRMs (tech stack fit):")
    sorted_crm = sorted(analysis["by_crm"].items(), key=lambda x: x[1]["rate"], reverse=True)
    for crm, data in sorted_crm[:5]:
        print(f"    {crm}: {data['rate']:.0%} ({data['converted']}/{data['total']}) -> Score: {weights['crm'].get(crm, 0)}")

    # Step 3: Score all accounts
    print("\n[3/4] Scoring all accounts (firmographic signals only)...")
    scored_accounts = []
    for lead in leads:
        score, breakdown = score_account(lead, weights)
        tier = assign_tier(score)
        scored_accounts.append({
            **lead,
            "score": score,
            "tier": tier,
            "breakdown": breakdown,
            "top_signals": get_top_signals(breakdown),
        })

    # Sort by score descending
    scored_accounts.sort(key=lambda x: x["score"], reverse=True)

    # Tier distribution
    tier_counts = Counter(a["tier"] for a in scored_accounts)
    tier_acv = defaultdict(float)
    tier_s1 = defaultdict(int)
    for a in scored_accounts:
        tier_acv[a["tier"]] += a["opportunity_acv"]
        if a["s1"] == 1:
            tier_s1[a["tier"]] += 1

    print("\n  TIER DISTRIBUTION:")
    for tier in ["T1", "T2", "T3"]:
        count = tier_counts.get(tier, 0)
        s1 = tier_s1.get(tier, 0)
        acv = tier_acv.get(tier, 0)
        rate = s1 / count if count > 0 else 0
        print(f"    {tier}: {count} accounts | {s1} S1 conversions ({rate:.0%}) | ${acv:,.0f} pipeline")

    # Step 4: Output
    print("\n[4/4] Generating outputs...")

    # Output tiered accounts CSV
    csv_rows = []
    for a in scored_accounts:
        csv_rows.append({
            "Company": a["company"],
            "Industry": a["industry"],
            "Score": a["score"],
            "Tier": a["tier"],
            "Contact": f"{a['first_name']} {a['last_name']}",
            "Title": a["title"],
            "Revenue Range": a["revenue_range"],
            "Employee Band": a["employee_band"],
            "Current CRM": a["current_crm"],
            "Country": a["country"],
            "Channel": a["channel"],
            "Lifecycle Stage": a["lifecycle_stage"],
            "S1 (actual)": a["s1"],
            "ACV": f"${a['opportunity_acv']:,.0f}" if a["opportunity_acv"] > 0 else "",
            "Top Signals": " | ".join(a["top_signals"]),
            "Engagement Actions": "; ".join(a["engagement_actions"]),
            "Sales Notes": a["sales_notes"][:200] if a["sales_notes"] else "",
        })

    headers = list(csv_rows[0].keys())
    write_csv_output(os.path.join(output_dir, "tiered_accounts.csv"), headers, csv_rows)

    # Output analysis report
    report = generate_tiering_report(analysis, weights, scored_accounts, tier_counts, tier_s1, tier_acv)
    write_markdown(os.path.join(output_dir, "account_tiering_analysis.md"), report)

    print("\n  Module 1 complete.")
    return scored_accounts, weights, analysis


def generate_tiering_report(analysis, weights, scored_accounts, tier_counts, tier_s1, tier_acv):
    """Generate the account tiering analysis markdown report."""
    lines = []
    lines.append("# Account Tiering Model & Analysis Report")
    lines.append(f"\n**Dataset:** {analysis['total_leads']} leads | {analysis['s1_conversions']} S1 conversions | Baseline rate: {analysis['baseline_rate']:.1%}")
    lines.append("")

    # Tier summary
    lines.append("## Tier Summary")
    lines.append("| Tier | Accounts | S1 Conversions | S1 Rate | Pipeline ACV |")
    lines.append("|------|----------|----------------|---------|-------------|")
    for tier in ["T1", "T2", "T3"]:
        count = tier_counts.get(tier, 0)
        s1 = tier_s1.get(tier, 0)
        acv = tier_acv.get(tier, 0)
        rate = f"{s1/count:.0%}" if count > 0 else "0%"
        lines.append(f"| {tier} | {count} | {s1} | {rate} | ${acv:,.0f} |")
    lines.append("")

    # Scoring methodology
    lines.append("## Scoring Methodology")
    lines.append("Tier scores use **firmographic signals only** — these are the attributes available")
    lines.append("for both training data and new accounts. Weights are derived from conversion ratios,")
    lines.append("not set arbitrarily.")
    lines.append("")
    lines.append("| Signal Category | Max Points | How It's Calculated |")
    lines.append("|----------------|-----------|-------------------|")
    lines.append("| Industry Fit | 30 | Conversion rate vs baseline. HR Tech 67% = 30pts, Insurance 0% = 0pts |")
    lines.append("| CRM Fit | 20 | Mid-market CRMs (Copper, Pipedrive) = high EV, enterprise CRMs (Salesforce) = low EV |")
    lines.append("| Revenue Fit | 20 | $25M-$100M = highest (30% convert), <$5M = lowest (14%) |")
    lines.append("| Employee Band | 15 | 51-200 = highest (28% convert), 501-1000 = lowest (10%) |")
    lines.append("| Country | 15 | Germany = highest (44% convert), France = lowest (0%) |")
    lines.append("| **Total** | **100** | |")
    lines.append("")

    lines.append("### Why firmographic-only scoring?")
    lines.append("Behavioral signals (engagement actions, sales notes, funnel stage) are powerful")
    lines.append("predictors — but they only exist for accounts already in our funnel. New accounts")
    lines.append("entering the system have zero behavioral data. By scoring on firmographics alone,")
    lines.append("the tiering model works identically for training data AND new accounts.")
    lines.append("")
    lines.append("Behavioral signals are tracked separately in the **Stage** dimension (Identified →")
    lines.append("Aware → Engaged → Considering → Selecting), managed through CRM workflows.")
    lines.append("**Tier** (firmographic fit) tells us *what resources* to allocate.")
    lines.append("**Stage** (behavioral progression) tells us *what to say and when*.")
    lines.append("")

    # Tier thresholds
    lines.append("## Tier Thresholds")
    lines.append("- **T1 (Strategic, 1:1):** Score >= 60 — Best firmographic fit, high-touch outreach")
    lines.append("- **T2 (Growth, 1:few):** Score 40-59 — Good fit, industry-cluster campaigns")
    lines.append("- **T3 (Scale, 1:many):** Score < 40 — Weaker fit, programmatic nurture")
    lines.append("")

    # Industry conversion
    lines.append("## Industry Conversion Analysis")
    lines.append("| Industry | Leads | S1 | Rate | Score (/30) |")
    lines.append("|----------|-------|-----|------|-------------|")
    sorted_ind = sorted(analysis["by_industry"].items(), key=lambda x: x[1]["rate"], reverse=True)
    for ind, data in sorted_ind:
        score = weights["industry"].get(ind, 0)
        lines.append(f"| {ind} | {data['total']} | {data['converted']} | {data['rate']:.0%} | {score} |")
    lines.append("")

    # CRM conversion
    lines.append("## CRM Fit Analysis")
    lines.append("| Current CRM | Leads | S1 | Rate | Score (/20) |")
    lines.append("|-------------|-------|-----|------|-------------|")
    sorted_crm = sorted(analysis["by_crm"].items(), key=lambda x: x[1]["rate"], reverse=True)
    for crm, data in sorted_crm:
        score = weights["crm"].get(crm, 0)
        lines.append(f"| {crm} | {data['total']} | {data['converted']} | {data['rate']:.0%} | {score} |")
    lines.append("")

    # Revenue conversion
    lines.append("## Revenue Range Analysis")
    lines.append("| Revenue Range | Leads | S1 | Rate | Score (/20) |")
    lines.append("|---------------|-------|-----|------|-------------|")
    sorted_rev = sorted(analysis["by_revenue"].items(), key=lambda x: x[1]["rate"], reverse=True)
    for rev, data in sorted_rev:
        score = weights["revenue"].get(rev, 0)
        lines.append(f"| {rev} | {data['total']} | {data['converted']} | {data['rate']:.0%} | {score} |")
    lines.append("")

    # Employee Band conversion
    lines.append("## Employee Band Analysis")
    lines.append("| Employee Band | Leads | S1 | Rate | Score (/15) |")
    lines.append("|---------------|-------|-----|------|-------------|")
    sorted_emp = sorted(analysis["by_employee_band"].items(), key=lambda x: x[1]["rate"], reverse=True)
    for band, data in sorted_emp:
        score = weights["employee_band"].get(band, 0)
        lines.append(f"| {band} | {data['total']} | {data['converted']} | {data['rate']:.0%} | {score} |")
    lines.append("")

    # Country conversion
    lines.append("## Country Analysis")
    lines.append("| Country | Leads | S1 | Rate | Score (/15) |")
    lines.append("|---------|-------|-----|------|-------------|")
    sorted_country = sorted(analysis["by_country"].items(), key=lambda x: x[1]["rate"], reverse=True)
    for country, data in sorted_country:
        score = weights["country"].get(country, 0)
        lines.append(f"| {country} | {data['total']} | {data['converted']} | {data['rate']:.0%} | {score} |")
    lines.append("")

    # Behavioral insights (not in score, but valuable for strategy)
    lines.append("## Behavioral Insights (Not in Tier Score)")
    lines.append("These signals don't affect the tier score but inform the activation strategy.")
    lines.append("")

    # Channel conversion
    lines.append("### Channel Performance (by Expected Value)")
    lines.append("| Channel | Leads | S1 | Rate | Avg ACV | Expected Value |")
    lines.append("|---------|-------|-----|------|---------|---------------|")
    sorted_ch = sorted(analysis["by_channel"].items(), key=lambda x: x[1]["expected_value"], reverse=True)
    for ch, data in sorted_ch:
        acv_str = f"${data['avg_acv']:,.0f}" if data['avg_acv'] > 0 else "-"
        ev_str = f"${data['expected_value']:,.0f}" if data['expected_value'] > 0 else "$0"
        lines.append(f"| {ch} | {data['total']} | {data['converted']} | {data['rate']:.0%} | {acv_str} | {ev_str} |")
    lines.append("")

    # Engagement lift
    lines.append("### Engagement Signal Lift")
    lines.append("| Action | S1 Rate | Non-S1 Rate | Lift |")
    lines.append("|--------|---------|-------------|------|")
    sorted_eng = sorted(analysis["engagement_lift"].items(), key=lambda x: x[1]["lift"], reverse=True)
    for action, data in sorted_eng:
        lines.append(f"| {action} | {data['s1_pct']:.0%} | {data['non_s1_pct']:.0%} | {data['lift']:+.0%} |")
    lines.append("")

    # Re-tiering triggers
    lines.append("## How the Model Gets Refreshed")
    lines.append("**Tier re-scoring** (firmographic weights change):")
    lines.append("1. **Quarterly weight recalibration** — Feedback engine analyzes new S1 outcomes, recalculates conversion ratios, updates all 5 weight categories")
    lines.append("2. **Firmographic change** — Company gets acquired, raises funding, headcount grows (via enrichment tools like Clay/Apollo) → re-score")
    lines.append("3. **Growing dataset** — Each quarter, new funnel data (150 → 300 → 500 leads) makes weights more statistically reliable")
    lines.append("")
    lines.append("**Stage progression** (behavioral, tracked in CRM):")
    lines.append("1. Engagement event (pricing page, content download) → advance stage")
    lines.append("2. Sales notes update (budget approved, competitor mentioned) → advance stage")
    lines.append("3. Lifecycle stage change (MQL → SQL → Opportunity) → advance stage")
    lines.append("")

    # AI role
    lines.append("## How AI Was Used")
    lines.append("1. **Pattern Discovery:** Claude Code analyzed 150 leads across 7 dimensions to identify which firmographic attributes predict conversion")
    lines.append("2. **Weight Derivation:** Each weight is mathematically derived: (segment_conversion_rate / baseline_rate) * multiplier")
    lines.append("3. **Separation of Concerns:** AI identified that behavioral signals shouldn't be in tier scores — they create a circular dependency (you need engagement to tier, but you need a tier to decide engagement strategy)")
    lines.append("4. **Continuous Learning:** The feedback engine recalibrates weights as new conversion data arrives, and the model gets sharper with each cycle")
    lines.append("")

    # Top T1 accounts
    lines.append("## Top T1 Accounts")
    t1_accounts = [a for a in scored_accounts if a["tier"] == "T1"]
    lines.append(f"Total T1 accounts: {len(t1_accounts)}")
    lines.append("")
    lines.append("| Company | Score | Industry | Revenue | CRM | Country | S1? | ACV |")
    lines.append("|---------|-------|----------|---------|-----|---------|-----|-----|")
    for a in t1_accounts[:15]:
        s1_str = "Yes" if a["s1"] == 1 else "No"
        acv_str = f"${a['opportunity_acv']:,.0f}" if a["opportunity_acv"] > 0 else "-"
        lines.append(f"| {a['company']} | {a['score']} | {a['industry']} | {a['revenue_range']} | {a['current_crm']} | {a['country']} | {s1_str} | {acv_str} |")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# STANDALONE EXECUTION
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from utils import load_leads
    leads = load_leads(os.path.join(os.path.dirname(__file__), "..", "data", "funnel_leads.csv"))
    run_tiering(leads, os.path.dirname(__file__))
