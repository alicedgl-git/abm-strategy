"""
ABM Engine — Module 4: Recalibration Engine
Assignment Deliverable 4: The AI System — How This Improves Over Time

This module answers one question: "I have new data. What changed?"

When new lead data arrives (e.g., Q2 brings 150 new leads with S1 outcomes),
the recalibration engine:
1. Merges old + new data into a combined dataset
2. Reruns the scoring weight derivation on the bigger dataset
3. Compares EVERYTHING before vs after
4. Saves updated weights so the scoring engine evolves
5. Regenerates all module reports with the improved model

What gets better with more data:
- Scoring weights (5 firmographic dimensions)
- Tier assignments (accounts shift as weights change)
- Channel performance insights
- Persona conversion patterns
- Messaging theme effectiveness
- Engagement signal analysis

What stays fixed (strategic frameworks, not data-derived):
- Tier thresholds (T1 >= 60, T2 >= 40)
- Persona definitions and title mappings
- 13-week quarterly plan structure
- Tier playbooks (1:1 vs 1:few vs 1:many)
"""

import os
import sys
from collections import Counter

# Add parent and sibling module paths
base = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base, "01_account_tiering"))
sys.path.insert(0, os.path.join(base, "02_persona_and_messaging"))
sys.path.insert(0, os.path.join(base, "03_strategy_and_plan"))

from utils import (
    load_weights, get_conversion_rates,
    get_engagement_lift, write_markdown, ALL_ENGAGEMENT_ACTIONS,
)
from account_tiering_model import score_account, assign_tier


# ─────────────────────────────────────────────
# CORE: Compare before vs after
# ─────────────────────────────────────────────

def compare_weights(old_weights, new_weights):
    """Compare every value in every dimension. Return list of changes."""
    changes = []
    dimensions = ["industry", "crm", "revenue", "employee_band", "country"]

    for dim in dimensions:
        old_dim = old_weights.get(dim, {})
        new_dim = new_weights.get(dim, {})

        # All values across both
        all_values = set(old_dim.keys()) | set(new_dim.keys())
        for value in sorted(all_values):
            if value.startswith("_"):
                continue  # Skip _default, _max
            old_score = old_dim.get(value, old_dim.get("_default", 0))
            new_score = new_dim.get(value, new_dim.get("_default", 0))
            if old_score != new_score:
                changes.append({
                    "dimension": dim,
                    "value": value,
                    "old": old_score,
                    "new": new_score,
                    "direction": "UP" if new_score > old_score else "DOWN",
                    "delta": new_score - old_score,
                })

    return changes


def compare_tiers(old_scored, new_scored):
    """Compare tier assignments before vs after. Return actual mobility."""
    old_tiers = {a["company"]: {"tier": a["tier"], "score": a["score"]} for a in old_scored}

    promotions = []
    demotions = []
    stable = 0

    for account in new_scored:
        company = account["company"]
        if company in old_tiers:
            old = old_tiers[company]
            if account["tier"] != old["tier"]:
                tier_order = {"T3": 0, "T2": 1, "T1": 2}
                if tier_order[account["tier"]] > tier_order[old["tier"]]:
                    promotions.append({
                        "company": company,
                        "old_tier": old["tier"],
                        "new_tier": account["tier"],
                        "old_score": old["score"],
                        "new_score": account["score"],
                    })
                else:
                    demotions.append({
                        "company": company,
                        "old_tier": old["tier"],
                        "new_tier": account["tier"],
                        "old_score": old["score"],
                        "new_score": account["score"],
                    })
            else:
                stable += 1

    return {"promotions": promotions, "demotions": demotions, "stable": stable}


def compare_channels(old_leads, new_leads):
    """Compare channel conversion rates before vs after."""
    old_rates = get_conversion_rates(old_leads, "channel")
    new_rates = get_conversion_rates(new_leads, "channel")

    changes = []
    all_channels = set(old_rates.keys()) | set(new_rates.keys())
    for ch in sorted(all_channels):
        old = old_rates.get(ch, {"rate": 0, "total": 0, "converted": 0})
        new = new_rates.get(ch, {"rate": 0, "total": 0, "converted": 0})
        changes.append({
            "channel": ch,
            "old_rate": old["rate"],
            "new_rate": new["rate"],
            "old_total": old["total"],
            "new_total": new["total"],
            "delta": new["rate"] - old["rate"],
        })

    return sorted(changes, key=lambda x: abs(x["delta"]), reverse=True)


def compare_personas(old_leads, new_leads):
    """Compare persona conversion rates before vs after."""
    from persona_and_messaging import classify_persona, derive_persona_insights

    old_insights = derive_persona_insights(old_leads)
    new_insights = derive_persona_insights(new_leads)

    changes = []
    all_personas = set(old_insights.keys()) | set(new_insights.keys())
    for persona in sorted(all_personas):
        old = old_insights.get(persona, {})
        new = new_insights.get(persona, {})
        old_rate = old.get("rate", 0)
        new_rate = new.get("rate", 0)
        old_acv = old.get("avg_acv", 0)
        new_acv = new.get("avg_acv", 0)
        changes.append({
            "persona": persona,
            "old_rate": old_rate,
            "new_rate": new_rate,
            "rate_delta": new_rate - old_rate,
            "old_acv": old_acv,
            "new_acv": new_acv,
        })

    return changes


def compare_messaging_themes(old_leads, new_leads):
    """Compare messaging theme conversion rates before vs after."""
    old_themes = _analyze_themes(old_leads)
    new_themes = _analyze_themes(new_leads)

    changes = []
    for theme in old_themes:
        old = old_themes[theme]
        new = new_themes.get(theme, {"rate": 0, "total": 0})
        changes.append({
            "theme": theme,
            "old_rate": old["rate"],
            "new_rate": new["rate"],
            "old_total": old["total"],
            "new_total": new["total"],
            "delta": new["rate"] - old["rate"],
        })

    return sorted(changes, key=lambda x: x["new_rate"], reverse=True)


def compare_engagement(old_leads, new_leads):
    """Compare engagement signal effectiveness before vs after."""
    old_lift = get_engagement_lift(old_leads)
    new_lift = get_engagement_lift(new_leads)

    changes = []
    for action in ALL_ENGAGEMENT_ACTIONS:
        old = old_lift.get(action, {"lift": 0})
        new = new_lift.get(action, {"lift": 0})
        changes.append({
            "action": action,
            "old_lift": old["lift"],
            "new_lift": new["lift"],
            "delta": new["lift"] - old["lift"],
        })

    return sorted(changes, key=lambda x: x["new_lift"], reverse=True)


def _analyze_themes(leads):
    """Analyze messaging theme conversion rates from leads."""
    themes = {
        "Compliance focus": ["audit", "compliance", "legal", "redlining", "clause"],
        "Manual process pain": ["google docs", "manually", "word docs", "email"],
        "Proposal automation": ["proposal", "template", "standardize", "automate"],
        "Integration focus": ["integrations", "crm", "salesforce", "hubspot"],
        "Cost/ROI focus": ["cost", "roi", "budget", "pricing", "save"],
        "Competitor displacement": ["conga", "ironclad", "adobe sign", "proposify", "competitor"],
    }

    results = {}
    for theme, keywords in themes.items():
        total = 0
        converted = 0
        for lead in leads:
            notes = (lead.get("sales_notes") or "").lower()
            engagement = " ".join(lead.get("engagement_actions") or []).lower()
            combined = notes + " " + engagement
            if any(kw in combined for kw in keywords):
                total += 1
                if lead["s1"] == 1:
                    converted += 1
        results[theme] = {
            "total": total,
            "converted": converted,
            "rate": converted / total if total > 0 else 0,
        }

    return results


# ─────────────────────────────────────────────
# REPORT GENERATION
# ─────────────────────────────────────────────

def generate_recalibration_report(is_first_run=False, **data):
    """Generate the before/after recalibration report (or baseline report on first run)."""
    lines = []

    lines.append("# Recalibration Report")
    lines.append("")
    if is_first_run:
        lines.append("**Initial training run** — this is the baseline. Future runs with new data will show before/after comparisons.")
        lines.append("")
    else:
        lines.append("This report shows what changed when new data was fed into the ABM scoring model.")
        lines.append("Every section compares **before** (old data) vs **after** (old + new data combined).")
        lines.append("")

    # ── Section 1: Dataset Growth ──
    lines.append("## 1. Dataset Growth")
    lines.append("")
    lines.append(f"| Metric | Before | After | Change |")
    lines.append(f"|--------|--------|-------|--------|")
    lines.append(f"| Total leads | {data['old_count']} | {data['new_total']} | +{data['new_total'] - data['old_count']} |")
    lines.append(f"| S1 conversions | {data['old_s1']} | {data['new_s1']} | +{data['new_s1'] - data['old_s1']} |")
    lines.append(f"| Baseline S1 rate | {data['old_baseline']:.0%} | {data['new_baseline']:.0%} | {data['new_baseline'] - data['old_baseline']:+.0%} |")
    if data["new_companies"]:
        lines.append(f"| New companies | — | {len(data['new_companies'])} | — |")
    lines.append("")

    # ── Section 2: Scoring Weight Changes ──
    lines.append("## 2. Scoring Weight Changes")
    lines.append("")
    if data["weight_changes"]:
        lines.append(f"**{len(data['weight_changes'])} weights adjusted** across the 5 firmographic dimensions.")
        lines.append("")
        lines.append("| Dimension | Value | Before | After | Change |")
        lines.append("|-----------|-------|--------|-------|--------|")
        for c in sorted(data["weight_changes"], key=lambda x: abs(x["delta"]), reverse=True):
            lines.append(f"| {c['dimension'].replace('_', ' ').title()} | {c['value']} | {c['old']} | {c['new']} | {c['delta']:+d} {c['direction']} |")
        lines.append("")
    else:
        lines.append("No weight changes. The model is stable — current weights are well-calibrated.")
        lines.append("")

    # ── Section 3: Tier Mobility ──
    lines.append("## 3. Tier Mobility")
    lines.append("")
    lines.append("Accounts that changed tier after re-scoring with the updated weights:")
    lines.append("")
    lines.append("| Tier | Before | After | Change |")
    lines.append("|------|--------|-------|--------|")
    for tier in ["T1", "T2", "T3"]:
        old_c = data["old_tier_counts"].get(tier, 0)
        new_c = data["new_tier_counts"].get(tier, 0)
        old_s1 = data["old_tier_s1"].get(tier, 0)
        new_s1 = data["new_tier_s1"].get(tier, 0)
        old_rate = old_s1 / old_c * 100 if old_c > 0 else 0
        new_rate = new_s1 / new_c * 100 if new_c > 0 else 0
        lines.append(f"| {tier} | {old_c} accounts ({old_rate:.0f}% S1) | {new_c} accounts ({new_rate:.0f}% S1) | {new_c - old_c:+d} |")
    lines.append("")

    mobility = data["tier_mobility"]
    if mobility["promotions"]:
        lines.append(f"### Promotions ({len(mobility['promotions'])} accounts moved up)")
        lines.append("")
        lines.append("| Company | Old Tier | New Tier | Old Score | New Score |")
        lines.append("|---------|----------|----------|-----------|-----------|")
        for p in mobility["promotions"]:
            lines.append(f"| {p['company']} | {p['old_tier']} | {p['new_tier']} | {p['old_score']} | {p['new_score']} |")
        lines.append("")

    if mobility["demotions"]:
        lines.append(f"### Demotions ({len(mobility['demotions'])} accounts moved down)")
        lines.append("")
        lines.append("| Company | Old Tier | New Tier | Old Score | New Score |")
        lines.append("|---------|----------|----------|-----------|-----------|")
        for d in mobility["demotions"]:
            lines.append(f"| {d['company']} | {d['old_tier']} | {d['new_tier']} | {d['old_score']} | {d['new_score']} |")
        lines.append("")

    # ── Section 4: Channel & Engagement Shifts ──
    lines.append("## 4. Channel & Engagement Shifts")
    lines.append("")
    lines.append("### Channel Performance")
    lines.append("")
    lines.append("| Channel | Before S1 Rate | After S1 Rate | Change |")
    lines.append("|---------|---------------|---------------|--------|")
    for c in data["channel_changes"]:
        if c["old_total"] > 0 or c["new_total"] > 0:
            lines.append(f"| {c['channel']} | {c['old_rate']:.0%} ({c['old_total']} leads) | {c['new_rate']:.0%} ({c['new_total']} leads) | {c['delta']:+.0%} |")
    lines.append("")

    lines.append("### Engagement Signal Effectiveness")
    lines.append("")
    lines.append("| Engagement Action | Before Lift | After Lift | Change |")
    lines.append("|-------------------|------------|------------|--------|")
    for e in data["engagement_changes"]:
        if abs(e["old_lift"]) > 0.01 or abs(e["new_lift"]) > 0.01:
            lines.append(f"| {e['action']} | {e['old_lift']:+.0%} | {e['new_lift']:+.0%} | {e['delta']:+.0%} |")
    lines.append("")

    # ── Section 5: Messaging & Persona Shifts ──
    lines.append("## 5. Messaging & Persona Shifts")
    lines.append("")
    lines.append("### Messaging Theme Conversion")
    lines.append("")
    lines.append("| Theme | Before | After | Change |")
    lines.append("|-------|--------|-------|--------|")
    for m in data["messaging_changes"]:
        if m["old_total"] > 0 or m["new_total"] > 0:
            lines.append(f"| {m['theme']} | {m['old_rate']:.0%} ({m['old_total']} leads) | {m['new_rate']:.0%} ({m['new_total']} leads) | {m['delta']:+.0%} |")
    lines.append("")

    lines.append("### Persona Conversion")
    lines.append("")
    lines.append("| Persona | Before S1 Rate | After S1 Rate | Before Avg ACV | After Avg ACV |")
    lines.append("|---------|---------------|---------------|----------------|---------------|")
    for p in data["persona_changes"]:
        lines.append(f"| {p['persona']} | {p['old_rate']:.0%} | {p['new_rate']:.0%} | ${p['old_acv']:,.0f} | ${p['new_acv']:,.0f} |")
    lines.append("")

    # ── How to use the updated model ──
    lines.append("---")
    lines.append("## Next Steps")
    lines.append("")
    lines.append("The updated weights have been saved to `01_account_tiering/scoring_weights.json`.")
    lines.append("")
    lines.append("To score new accounts with the improved model:")
    lines.append("```")
    lines.append("python3 orchestrator.py --score new_prospects.csv")
    lines.append("```")
    lines.append("")
    lines.append("To regenerate all reports with the updated data:")
    lines.append("```")
    lines.append("python3 orchestrator.py --input data/combined_leads.csv")
    lines.append("```")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# MAIN ENTRY POINT (called by orchestrator)
# ─────────────────────────────────────────────

def run_recalibration_report(leads, scored_accounts, weights, old_weights=None, old_scored=None, output_dir="04_feedback_engine"):
    """
    Generate the recalibration report (Module 4).

    Two behaviors depending on whether old_weights exist:

    1. FIRST RUN (old_weights=None): No previous model. Generate a baseline report
       showing current state — no diffs, just the starting point.

    2. RECALIBRATION (old_weights provided): Previous model exists. Compare old vs new
       across all dimensions and generate a before/after diff report.

    Args:
        leads: Current lead dataset (the data we just trained on)
        scored_accounts: Accounts scored with NEW weights (from Module 1)
        weights: NEW weights (just derived by Module 1)
        old_weights: Previous weights (from scoring_weights.json before this run), or None
        old_scored: Accounts scored with OLD weights (for tier mobility), or None
        output_dir: Where to write the report

    Returns:
        mobility dict (or None if first run)
    """
    is_recalibration = old_weights is not None

    print("\n" + "=" * 60)
    print("MODULE 4: RECALIBRATION ENGINE")
    print("=" * 60)
    print(f"\n  Dataset size: {len(leads)} leads")

    if is_recalibration:
        print(f"  Previous model found — generating before/after diff")
    else:
        print(f"  First run — establishing baseline")

    # ── Compute current state ──
    new_tier_counts = Counter(a["tier"] for a in scored_accounts)
    new_tier_s1 = Counter(a["tier"] for a in scored_accounts if a["s1"] == 1)
    baseline = sum(1 for l in leads if l["s1"] == 1) / len(leads)
    s1_count = sum(1 for l in leads if l["s1"] == 1)

    # Current messaging themes
    themes = _analyze_themes(leads)
    print(f"\n  Messaging theme conversion rates:")
    for theme, data in sorted(themes.items(), key=lambda x: x[1]["rate"], reverse=True):
        if data["total"] > 0:
            print(f"    {theme}: {data['rate']:.0%} ({data['converted']}/{data['total']})")

    # Current engagement signals
    print(f"\n  Top engagement signals:")
    for action, data in sorted(get_engagement_lift(leads).items(), key=lambda x: x[1]["lift"], reverse=True)[:5]:
        total_with = sum(1 for l in leads if action in l["engagement_actions"])
        s1_with = sum(1 for l in leads if action in l["engagement_actions"] and l["s1"] == 1)
        rate = s1_with / total_with if total_with > 0 else 0
        print(f"    {action}: {rate:.0%} ({s1_with}/{total_with})")

    # ── Generate diff data (or baseline if first run) ──
    if is_recalibration:
        # Compare weights
        weight_changes = compare_weights(old_weights, weights)
        if weight_changes:
            print(f"\n  WEIGHT CHANGES ({len(weight_changes)} adjustments):")
            for c in weight_changes[:10]:
                print(f"    {c['dimension'].title()}: {c['value']}  {c['old']} → {c['new']}  {c['direction']}")
        else:
            print(f"\n  No weight changes — model is stable.")

        # Compare tiers
        tier_mobility = compare_tiers(old_scored, scored_accounts)
        old_tier_counts = Counter(a["tier"] for a in old_scored)
        old_tier_s1 = Counter(a["tier"] for a in old_scored if a["s1"] == 1)
        old_baseline = sum(1 for a in old_scored if a["s1"] == 1) / len(old_scored)
        old_s1_count = sum(1 for a in old_scored if a["s1"] == 1)

        print(f"\n  TIER DISTRIBUTION:")
        for tier in ["T1", "T2", "T3"]:
            old_c = old_tier_counts.get(tier, 0)
            new_c = new_tier_counts.get(tier, 0)
            print(f"    {tier}: {old_c} → {new_c} ({new_c - old_c:+d})")

        if tier_mobility["promotions"]:
            print(f"\n  PROMOTIONS ({len(tier_mobility['promotions'])} accounts):")
            for p in tier_mobility["promotions"][:5]:
                print(f"    {p['company']}: {p['old_tier']} → {p['new_tier']} (score {p['old_score']} → {p['new_score']})")
        if tier_mobility["demotions"]:
            print(f"\n  DEMOTIONS ({len(tier_mobility['demotions'])} accounts):")
            for d in tier_mobility["demotions"][:5]:
                print(f"    {d['company']}: {d['old_tier']} → {d['new_tier']} (score {d['old_score']} → {d['new_score']})")

        # Compare channels, personas, messaging, engagement
        # For recalibration with a new dataset, old_scored contains the old leads
        old_leads_list = [{k: v for k, v in a.items() if k not in ("score", "tier")} for a in old_scored]
        channel_changes = compare_channels(old_leads_list, leads)
        persona_changes = compare_personas(old_leads_list, leads)
        messaging_changes = compare_messaging_themes(old_leads_list, leads)
        engagement_changes = compare_engagement(old_leads_list, leads)

    else:
        # First run — no diff, just current state
        weight_changes = []
        tier_mobility = {"promotions": [], "demotions": [], "stable": len(scored_accounts)}
        old_tier_counts = new_tier_counts
        old_tier_s1 = new_tier_s1
        old_baseline = baseline
        old_s1_count = s1_count

        # Build baseline-only data (no deltas)
        channel_changes = []
        for ch, data in sorted(get_conversion_rates(leads, "channel").items(), key=lambda x: x[1]["rate"], reverse=True):
            channel_changes.append({"channel": ch, "old_rate": data["rate"], "new_rate": data["rate"],
                                    "old_total": data["total"], "new_total": data["total"], "delta": 0})

        messaging_changes = []
        for theme, data in sorted(themes.items(), key=lambda x: x[1]["rate"], reverse=True):
            messaging_changes.append({"theme": theme, "old_rate": data["rate"], "new_rate": data["rate"],
                                      "old_total": data["total"], "new_total": data["total"], "delta": 0})

        engagement_changes = []
        for action, data in get_engagement_lift(leads).items():
            engagement_changes.append({"action": action, "old_lift": data["lift"], "new_lift": data["lift"], "delta": 0})

        from persona_and_messaging import derive_persona_insights
        persona_changes = []
        for persona, data in derive_persona_insights(leads).items():
            persona_changes.append({"persona": persona, "old_rate": data.get("rate", 0), "new_rate": data.get("rate", 0),
                                    "rate_delta": 0, "old_acv": data.get("avg_acv", 0), "new_acv": data.get("avg_acv", 0)})

    # ── Generate report ──
    report = generate_recalibration_report(
        old_count=len(old_scored) if old_scored else len(leads),
        new_total=len(leads),
        new_companies=[],
        old_baseline=old_baseline,
        new_baseline=baseline,
        old_s1=old_s1_count,
        new_s1=s1_count,
        weight_changes=weight_changes,
        old_tier_counts=old_tier_counts,
        new_tier_counts=new_tier_counts,
        old_tier_s1=old_tier_s1,
        new_tier_s1=new_tier_s1,
        tier_mobility=tier_mobility,
        channel_changes=channel_changes,
        persona_changes=persona_changes,
        messaging_changes=messaging_changes,
        engagement_changes=engagement_changes,
        is_first_run=not is_recalibration,
    )
    os.makedirs(output_dir, exist_ok=True)
    write_markdown(os.path.join(output_dir, "recalibration_report.md"), report)

    print("\n✓ Module 4 complete.")
    return tier_mobility if is_recalibration else None


# ─────────────────────────────────────────────
# STANDALONE EXECUTION
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Run via orchestrator: python3 orchestrator.py --input data/your_leads.csv")
    print("The recalibration report is generated automatically when previous weights exist.")
