"""
PandaDoc ABM Engine — Orchestrator
===================================
Main entry point for the AI-Driven ABM System.

Two modes:
  TRAIN — Analyze data, derive scoring weights, generate all reports.
          If previous weights exist, automatically generates a recalibration
          report showing what changed (before/after diff).
  SCORE — Load trained weights, score new accounts, output enriched CSV.

Usage:
    python orchestrator.py                                      # First run — full pipeline
    python orchestrator.py --input data/q2_leads.csv            # New data — recalibrates + shows diff
    python orchestrator.py --score data/demo_accounts.csv       # Score new accounts

Built with Claude Code as the AI orchestration layer.
"""

import argparse
import os
import sys
import time

# Add agent folders to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "01_account_tiering"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "02_persona_and_messaging"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "03_strategy_and_plan"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "04_feedback_engine"))

from utils import load_leads, load_new_accounts, load_weights, write_csv_output
from account_tiering_model import score_account, assign_tier, get_top_signals
from persona_and_messaging import (
    classify_persona, get_recommended_content, get_recommended_channel_for_persona,
    get_industry_messaging, PERSONA_MAP,
)

# Each agent writes outputs into its own folder
AGENT_DIRS = {
    "tiering": "01_account_tiering",
    "persona": "02_persona_and_messaging",
    "strategy": "03_strategy_and_plan",
    "feedback": "04_feedback_engine",
}

WEIGHTS_PATH = "01_account_tiering/scoring_weights.json"

# Messaging themes — maps qualitative signals and industry patterns to angles
MESSAGING_THEMES = {
    "Compliance focus": {
        "signals": ["contract_pain", "multi_stakeholder"],
        "keywords": ["audit", "compliance", "legal", "redlining", "clause"],
    },
    "Manual process pain": {
        "signals": ["manual_process_pain"],
        "keywords": ["google docs", "manually", "word docs", "email", "spreadsheet"],
    },
    "Proposal automation": {
        "signals": ["high_proposal_volume"],
        "keywords": ["proposal", "template", "standardize", "automate"],
    },
    "Integration focus": {
        "signals": [],
        "keywords": ["integrations", "crm", "salesforce", "hubspot", "api"],
    },
    "Competitor displacement": {
        "signals": ["competitor_evaluation"],
        "keywords": ["conga", "ironclad", "adobe sign", "proposify", "docusign"],
    },
}

# Key personas for multi-threading gap analysis
KEY_PERSONAS = {"Champion / User Buyer", "Economic Buyer", "Legal / Compliance", "Technical Evaluator"}


def determine_messaging_angle(lead):
    """Determine the best messaging angle for an account based on signals and notes."""
    notes = (lead.get("sales_notes") or "").lower()
    engagement = " ".join(lead.get("engagement_actions") or []).lower()
    combined = notes + " " + engagement
    signals = lead.get("qualitative_signals", {})

    # Check themes in order of conversion effectiveness
    for theme, config in MESSAGING_THEMES.items():
        # Check qualitative signals
        if any(signals.get(s) for s in config["signals"]):
            return theme
        # Check keywords in notes/engagement
        if any(kw in combined for kw in config["keywords"]):
            return theme

    # Default based on CRM status
    crm = (lead.get("current_crm") or "").lower()
    if not crm or "spreadsheet" in crm or "none" in crm or "google" in crm:
        return "Manual process pain"

    return "Proposal automation"


def run_scoring_pipeline(input_file):
    """Score new accounts using trained weights. Output enriched CSV."""

    print("=" * 60)
    print("  PANDADOC ABM ENGINE — SCORE MODE")
    print("  Scoring new accounts with trained firmographic weights")
    print("=" * 60)

    # Load trained weights
    if not os.path.exists(WEIGHTS_PATH):
        print(f"\n  ERROR: No trained weights found at {WEIGHTS_PATH}")
        print("  Run training first: python3 orchestrator.py")
        sys.exit(1)

    print(f"\n  Loading trained weights from {WEIGHTS_PATH}...")
    weights = load_weights(WEIGHTS_PATH)
    print(f"  Weights loaded: {len(weights)} categories")

    # Load new accounts
    print(f"\n  Loading new accounts from {input_file}...")
    leads = load_new_accounts(input_file)
    print(f"  Loaded {len(leads)} accounts")

    start_time = time.time()

    # Score, tier, and enrich each account
    print("\n  Scoring and enriching accounts (firmographic signals only)...")
    enriched = []

    for lead in leads:
        # Score and tier (Agent 1)
        score, breakdown = score_account(lead, weights)
        tier = assign_tier(score)
        top_signals = get_top_signals(breakdown)

        # Persona mapping (Agent 2)
        persona = classify_persona(lead["title"])
        present_personas = {persona}
        missing = KEY_PERSONAS - present_personas

        # Messaging angle
        angle = determine_messaging_angle(lead)

        # Recommended content and channels (Agent 2 helpers)
        context_hooks = []
        notes_lower = (lead.get("sales_notes") or "").lower()
        if any(comp in notes_lower for comp in ["conga", "ironclad", "adobe sign", "proposify"]):
            context_hooks.append("comparing document automation solutions")

        content = get_recommended_content(persona, lead["industry"], context_hooks)
        channel = get_recommended_channel_for_persona(persona, tier)

        enriched.append({
            "Company": lead["company"],
            "Industry": lead["industry"],
            "Score": score,
            "Tier": tier,
            "Contact": f"{lead['first_name']} {lead['last_name']}",
            "Title": lead["title"],
            "Persona": persona,
            "Missing Personas": "; ".join(sorted(missing)) if missing else "None",
            "Messaging Angle": angle,
            "Recommended Content": "; ".join(content),
            "Recommended Channels": channel,
            "Top Signals": " | ".join(top_signals),
            "Revenue Range": lead["revenue_range"],
            "Employee Band": lead["employee_band"],
            "Current CRM": lead["current_crm"],
            "Engagement Actions": "; ".join(lead["engagement_actions"]),
            "Sales Notes": (lead["sales_notes"] or "")[:200],
        })

    # Sort by score descending
    enriched.sort(key=lambda x: x["Score"], reverse=True)

    # Write enriched CSV
    output_path = "enriched_accounts.csv"
    headers = list(enriched[0].keys())
    write_csv_output(output_path, headers, enriched)

    elapsed = time.time() - start_time

    # Summary
    from collections import Counter
    tier_counts = Counter(a["Tier"] for a in enriched)

    print("\n" + "=" * 60)
    print("  SCORING COMPLETE")
    print("=" * 60)
    print(f"\n  Time: {elapsed:.1f}s")
    print(f"\n  RESULTS:")
    print(f"    Total Accounts:  {len(enriched)}")
    for tier in ["T1", "T2", "T3"]:
        count = tier_counts.get(tier, 0)
        print(f"    {tier}:              {count} accounts")
    print(f"\n  OUTPUT: {output_path}")
    print(f"\n  Share this CSV with your team or import back into your CRM.")
    print("=" * 60)


def run_full_pipeline(input_file="data/funnel_leads.csv"):
    """Execute the complete ABM engine pipeline.

    If previous weights exist (from an earlier run), Module 4 automatically
    generates a recalibration report showing what changed — no separate
    recalibrate command needed.
    """

    # Lazy imports — only needed in train mode
    from account_tiering_model import run_tiering
    from persona_and_messaging import run_persona_and_messaging
    from strategy_and_plan import run_strategy_and_plan
    from recalibration_engine import run_recalibration_report

    print("=" * 60)
    print("  PANDADOC AI-DRIVEN ABM ENGINE")
    print("  Built with Claude Code")
    print("=" * 60)
    print(f"\n  Input: {input_file}")

    # ── Snapshot previous state (if exists) for recalibration diff ──
    old_weights = None
    old_scored = None
    is_recalibration = os.path.exists(WEIGHTS_PATH)

    if is_recalibration:
        old_weights = load_weights(WEIGHTS_PATH)
        print(f"  Mode: RECALIBRATION (previous model found — will show before/after diff)")
        # Score current leads with OLD weights to get the "before" snapshot
        old_leads_for_snapshot = load_leads(input_file)
        old_scored = []
        for lead in old_leads_for_snapshot:
            score, breakdown = score_account(lead, old_weights)
            tier = assign_tier(score)
            old_scored.append({**lead, "score": score, "tier": tier})
    else:
        print(f"  Mode: INITIAL TRAINING (no previous model — building from scratch)")

    print(f"  {'=' * 56}")

    # Ensure agent output dirs exist
    for agent_dir in AGENT_DIRS.values():
        os.makedirs(agent_dir, exist_ok=True)


    # Load data
    print("\n  Loading lead data...")
    leads = load_leads(input_file)
    print(f"  Loaded {len(leads)} leads")

    start_time = time.time()

    # ── AGENT 1: Account Analysis & Tiering ──
    scored_accounts, weights, analysis = run_tiering(leads, AGENT_DIRS["tiering"])

    # ── AGENT 2: Buyer Committee & Messaging ──
    account_personas, frameworks = run_persona_and_messaging(scored_accounts, AGENT_DIRS["persona"], leads=leads)

    # ── AGENT 3: Channel Strategy & Quarterly Plan ──
    channel_analysis = run_strategy_and_plan(leads, scored_accounts, AGENT_DIRS["strategy"])

    # ── AGENT 4: Recalibration Report ──
    mobility = run_recalibration_report(
        leads, scored_accounts, weights,
        old_weights=old_weights,
        old_scored=old_scored,
        output_dir=AGENT_DIRS["feedback"],
    )

    # ── FINAL SUMMARY ──
    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\n  Time: {elapsed:.1f}s")
    print(f"\n  OUTPUTS GENERATED:")

    outputs = [
        ("01_account_tiering/scoring_weights.json", "Trained scoring weights (reusable)"),
        ("01_account_tiering/tiered_accounts.csv", "All accounts scored + tiered"),
        ("01_account_tiering/account_tiering_analysis.md", "Account tiering analysis & scoring methodology"),
        ("02_persona_and_messaging/persona_map.md", "Buyer committee mapping per account"),
        ("02_persona_and_messaging/messaging_frameworks.md", "Messaging by persona x tier"),
        ("03_strategy_and_plan/channel_strategy.md", "Channel performance & recommendations"),
        ("03_strategy_and_plan/quarterly_plan.md", "Quarterly ABM activation strategy"),
        ("04_feedback_engine/recalibration_report.md", "Recalibration engine report"),
    ]

    for filepath, description in outputs:
        exists = "OK" if os.path.exists(filepath) else "MISSING"
        print(f"    [{exists}] {filepath} — {description}")

    # Key metrics
    from collections import Counter
    tier_counts = Counter(a["tier"] for a in scored_accounts)
    tier_s1 = Counter(a["tier"] for a in scored_accounts if a["s1"] == 1)

    print(f"\n  KEY METRICS:")
    print(f"    Total Accounts:     {len(leads)}")
    print(f"    T1 (Strategic):     {tier_counts['T1']} accounts, {tier_s1.get('T1', 0)} S1 ({tier_s1.get('T1', 0)/tier_counts['T1']*100:.0f}% accuracy)")
    print(f"    T2 (Growth):        {tier_counts['T2']} accounts, {tier_s1.get('T2', 0)} S1 ({tier_s1.get('T2', 0)/tier_counts['T2']*100:.0f}% accuracy)")
    print(f"    T3 (Scale):         {tier_counts['T3']} accounts, {tier_s1.get('T3', 0)} S1 ({tier_s1.get('T3', 0)/tier_counts['T3']*100:.0f}% accuracy)")
    print(f"    Total Pipeline:     ${sum(a['opportunity_acv'] for a in scored_accounts):,.0f}")
    if mobility and mobility.get("promotions"):
        print(f"    Tier Mobility:      {len(mobility['promotions'])} promotions, {len(mobility['demotions'])} demotions")

    print(f"\n  Weights saved to {WEIGHTS_PATH} — ready to score new accounts.")
    print(f"  Usage: python3 orchestrator.py --score new_accounts.csv")
    if is_recalibration:
        print(f"\n  Recalibration report: 04_feedback_engine/recalibration_report.md")
    print("=" * 60)

    return {
        "scored_accounts": scored_accounts,
        "weights": weights,
        "analysis": analysis,
        "account_personas": account_personas,
        "frameworks": frameworks,
        "channel_analysis": channel_analysis,
        "mobility": mobility,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PandaDoc AI-Driven ABM Engine")
    parser.add_argument("--input", default="data/funnel_leads.csv", help="Path to lead data CSV")
    parser.add_argument("--score", metavar="CSV", help="Score new accounts using trained weights")
    args = parser.parse_args()

    if args.score:
        run_scoring_pipeline(args.score)
    else:
        run_full_pipeline(args.input)
