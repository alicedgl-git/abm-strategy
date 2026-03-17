"""
ABM Engine — Module 2: Buyer Committee Mapping & Messaging Framework
Assignment Deliverable 2: Buyer Committee Messaging Framework

This module:
1. Maps each contact's title to a buying committee persona
2. Identifies multi-threading gaps (missing personas per account)
3. Generates messaging frameworks per persona per tier
4. Outputs persona_map.md + messaging_frameworks.md
"""

import os
from collections import Counter, defaultdict
from utils import load_leads, write_markdown

# ─────────────────────────────────────────────
# PERSONA DEFINITIONS
# ─────────────────────────────────────────────

PERSONA_MAP = {
    "Champion / User Buyer": {
        "titles": [
            "VP of Sales", "CRO", "Director of Sales", "Sales Manager",
            "Account Executive", "Business Development Manager", "Sales Representative",
            "Proposal Manager", "Revenue Operations Manager", "Revenue Analyst",
        ],
        "cares_about": "Deal velocity, proposal speed, rep productivity, pipeline visibility",
        "pandadoc_value": "Close deals faster with professional proposals in minutes. Real-time tracking shows when prospects open documents.",
        "pain_points": ["Slow proposal turnaround", "No visibility into document engagement", "Manual formatting wasting rep time", "Inconsistent branding across proposals"],
    },
    "Economic Buyer": {
        "titles": [
            "CFO", "VP of Finance", "Director of Finance", "Finance Manager",
            "Financial Analyst", "CEO", "President", "Managing Director",
        ],
        "cares_about": "ROI, cost reduction, consolidation, risk mitigation",
        "pandadoc_value": "Reduce document cycle time by 65%. Consolidate proposals, contracts, and payments in one platform. Clear ROI from day one.",
        "pain_points": ["Too many point solutions", "No visibility into deal economics", "Contract errors causing revenue leakage", "High cost of current tools"],
    },
    "Legal / Compliance": {
        "titles": [
            "General Counsel", "Legal Counsel", "Contracts Manager",
            "Contract Specialist",
        ],
        "cares_about": "Compliance, audit trails, version control, redlining, clause libraries",
        "pandadoc_value": "Enterprise-grade audit trail, version locking, custom clause libraries, and built-in redlining. SOC 2 compliant.",
        "pain_points": ["No version control on contracts", "Manual redlining process", "Missing audit trails", "Compliance risk from contract errors"],
    },
    "Technical Evaluator": {
        "titles": [
            "CTO", "VP of Operations", "Director of Operations",
            "Operations Manager", "Operations Analyst", "Business Analyst",
        ],
        "cares_about": "Integrations, security, implementation ease, scalability",
        "pandadoc_value": "Native integrations with Salesforce, HubSpot, Pipedrive + 30 more. API-first architecture. Implement in days, not months.",
        "pain_points": ["Disconnected tools", "Long implementation timelines", "Security/compliance concerns", "Lack of CRM integration"],
    },
    "Executive Sponsor": {
        "titles": [
            "COO", "CMO",
        ],
        "cares_about": "Strategic alignment, competitive advantage, organizational efficiency",
        "pandadoc_value": "Transform your document workflow from a bottleneck into a competitive advantage. One platform for the entire revenue cycle.",
        "pain_points": ["Document processes holding back growth", "Lack of operational visibility", "Competitive disadvantage vs faster-moving companies"],
    },
    "Marketing / Other": {
        "titles": [
            "Marketing Manager", "Marketing Specialist",
        ],
        "cares_about": "Brand consistency, content management, campaign enablement",
        "pandadoc_value": "Template library ensures brand consistency. Content analytics show what resonates with prospects.",
        "pain_points": ["Inconsistent branding in sales materials", "No analytics on content performance"],
    },
}


def classify_persona(title):
    """Map a contact title to a buying committee persona."""
    title_lower = title.lower().strip()
    for persona, config in PERSONA_MAP.items():
        for persona_title in config["titles"]:
            if persona_title.lower() == title_lower:
                return persona
    # Fuzzy matching for edge cases
    if any(kw in title_lower for kw in ["sales", "revenue", "proposal", "business dev"]):
        return "Champion / User Buyer"
    if any(kw in title_lower for kw in ["financ", "cfo", "ceo", "president", "managing"]):
        return "Economic Buyer"
    if any(kw in title_lower for kw in ["legal", "counsel", "contract"]):
        return "Legal / Compliance"
    if any(kw in title_lower for kw in ["operation", "analyst", "cto", "technical", "it "]):
        return "Technical Evaluator"
    if any(kw in title_lower for kw in ["coo", "cmo", "chief"]):
        return "Executive Sponsor"
    return "Marketing / Other"


# ─────────────────────────────────────────────
# PERSONA MAPPING PER ACCOUNT
# ─────────────────────────────────────────────

def map_personas(scored_accounts):
    """Map each account's contacts to personas and identify gaps."""
    account_personas = {}
    for account in scored_accounts:
        company = account["company"]
        persona = classify_persona(account["title"])
        contact_name = f"{account['first_name']} {account['last_name']}"

        if company not in account_personas:
            account_personas[company] = {
                "tier": account["tier"],
                "score": account["score"],
                "industry": account["industry"],
                "contacts": [],
                "personas_present": set(),
                "sales_notes": account["sales_notes"],
                "current_crm": account["current_crm"],
                "revenue_range": account["revenue_range"],
            }

        account_personas[company]["contacts"].append({
            "name": contact_name,
            "title": account["title"],
            "persona": persona,
            "email": account["email"],
        })
        account_personas[company]["personas_present"].add(persona)

    # Identify missing personas (multi-threading gaps)
    all_key_personas = {"Champion / User Buyer", "Economic Buyer", "Legal / Compliance", "Technical Evaluator"}
    for company, data in account_personas.items():
        data["missing_personas"] = all_key_personas - data["personas_present"]
        # Extract additional stakeholders mentioned in sales notes
        data["mentioned_stakeholders"] = extract_mentioned_stakeholders(data["sales_notes"])

    return account_personas


def extract_mentioned_stakeholders(notes):
    """Extract stakeholder roles mentioned in sales notes."""
    if not notes:
        return []
    stakeholders = []
    role_keywords = {
        "General Counsel": "Legal / Compliance",
        "CFO": "Economic Buyer",
        "CTO": "Technical Evaluator",
        "VP of Sales": "Champion / User Buyer",
        "VP of Operations": "Technical Evaluator",
        "Head of RevOps": "Champion / User Buyer",
        "Head of Legal": "Legal / Compliance",
        "Director of Finance": "Economic Buyer",
        "Director of Contracts": "Legal / Compliance",
        "Chief of Staff": "Executive Sponsor",
        "COO": "Executive Sponsor",
        "CRO": "Champion / User Buyer",
    }
    for role, persona in role_keywords.items():
        if role.lower() in notes.lower():
            stakeholders.append({"role": role, "persona": persona})
    return stakeholders


# ─────────────────────────────────────────────
# DATA-DERIVED PERSONA INSIGHTS
# ─────────────────────────────────────────────

# Pain point categories to extract from sales notes
PAIN_CATEGORIES = {
    "manual_process": ["manually", "google docs", "word docs", "email attachments", "spreadsheet"],
    "contract_issues": ["contract error", "version control", "audit trail", "redlining", "clause"],
    "slow_proposals": ["proposal", "turnaround", "slow", "template"],
    "compliance_risk": ["compliance", "legal blocker", "soc 2", "security", "gdpr"],
    "integration_need": ["integration", "salesforce", "hubspot", "api", "connect"],
    "cost_concerns": ["cost", "budget", "roi", "expensive", "pricing", "save"],
    "tool_consolidation": ["consolidat", "too many tools", "multiple platforms", "point solution"],
    "visibility_gaps": ["visibility", "tracking", "analytics", "reporting", "no insight"],
}

# Human-readable pain labels
PAIN_LABELS = {
    "manual_process": "Manual document processes (Google Docs, Word, email)",
    "contract_issues": "Contract errors, version control, and audit trail gaps",
    "slow_proposals": "Slow proposal turnaround and lack of templates",
    "compliance_risk": "Compliance and legal review bottlenecks",
    "integration_need": "Need for CRM integration (Salesforce, HubSpot, etc.)",
    "cost_concerns": "Cost of current tools and ROI concerns",
    "tool_consolidation": "Too many point solutions — need consolidation",
    "visibility_gaps": "No visibility into document engagement or deal status",
}


def derive_persona_insights(leads):
    """
    Derive persona statistics directly from the 150-lead dataset.

    This function analyzes every lead's title, S1 outcome, sales notes, and industry
    to build a data-driven picture of each buying committee persona. Nothing is assumed —
    every metric comes from the CSV.

    Returns dict of persona → {total, converted, rate, avg_acv, top_pain_points, top_industries, titles_seen}
    """
    persona_stats = defaultdict(lambda: {
        "total": 0, "converted": 0, "acv": 0,
        "industries": Counter(), "pain_keywords": Counter(),
        "titles_seen": Counter(),
    })

    for lead in leads:
        persona = classify_persona(lead["title"])
        stats = persona_stats[persona]
        stats["total"] += 1
        stats["titles_seen"][lead["title"]] += 1
        stats["industries"][lead["industry"]] += 1

        if lead["s1"] == 1:
            stats["converted"] += 1
            stats["acv"] += lead["opportunity_acv"]

        # Extract pain points from sales notes
        notes = (lead.get("sales_notes") or "").lower()
        if notes:
            for pain, keywords in PAIN_CATEGORIES.items():
                if any(kw in notes for kw in keywords):
                    stats["pain_keywords"][pain] += 1

    # Compute rates and build results
    results = {}
    for persona, stats in persona_stats.items():
        rate = stats["converted"] / stats["total"] if stats["total"] > 0 else 0
        avg_acv = stats["acv"] / stats["converted"] if stats["converted"] > 0 else 0
        top_pains = [PAIN_LABELS.get(p, p) for p, _ in stats["pain_keywords"].most_common(4)]
        top_industries = [i for i, _ in stats["industries"].most_common(5)]

        results[persona] = {
            "total": stats["total"],
            "converted": stats["converted"],
            "rate": rate,
            "avg_acv": avg_acv,
            "total_pipeline": stats["acv"],
            "top_pain_points": top_pains,
            "top_industries": top_industries,
            "titles_seen": dict(stats["titles_seen"]),
        }

    return results


def derive_industry_messaging(leads):
    """
    Generate industry messaging from actual data — only for industries present in the dataset.
    Ordered by S1 conversion rate so the strategy prioritizes what actually converts.

    Returns dict of industry → {s1_rate, leads, converted, messaging}
    """
    from utils import get_conversion_rates
    rates = get_conversion_rates(leads, "industry")

    # PandaDoc value angles per industry (product knowledge layer — the HOW, not the WHETHER)
    # The data tells us WHICH industries to target; this tells us WHAT to say
    industry_angles = {
        "HR Tech": "offer letters, onboarding documents, and hiring contracts",
        "Logistics": "vendor agreements, shipping contracts, and supply chain documents",
        "Real Estate": "listing agreements, purchase contracts, and closing documents",
        "Construction": "bids, proposals, change orders, and subcontractor contracts",
        "Consulting": "SOWs, engagement letters, and client proposals",
        "Financial Services": "compliance-ready client agreements, investment documents, and audit trails",
        "Engineering": "SOWs, project proposals, and technical change orders",
        "Legal": "contract lifecycle management, clause libraries, and redlining",
        "Technology": "sales proposals, SaaS agreements, and renewal contracts",
        "Retail": "vendor agreements, franchise documents, and purchase orders",
        "SaaS": "subscription agreements, proposals, and renewal automation",
        "Education": "enrollment forms, vendor contracts, and grant proposals",
        "Healthcare": "patient agreements, vendor contracts, and compliance documentation",
        "Media": "client proposals, media buying agreements, and content contracts",
        "Professional Services": "SOWs, NDAs, and professional service agreements",
        "Manufacturing": "RFQs, purchase orders, and supplier contracts",
        "Marketing Agency": "client proposals, media plans, and campaign agreements",
        "Insurance": "policy documents, renewal notices, and claims forms",
        "Energy": "energy contracts, permits, and compliance documents",
    }

    messaging = {}
    for industry, data in sorted(rates.items(), key=lambda x: x[1]["rate"], reverse=True):
        angle = industry_angles.get(industry, "document workflows")
        rate_pct = f"{data['rate']:.0%}"

        if data["rate"] >= 0.30:
            priority = "PRIMARY TARGET"
            msg = f"Top-converting vertical ({rate_pct} S1 rate). Streamline {angle} with PandaDoc — proposals, e-signatures, and CRM integration in one platform."
        elif data["rate"] >= 0.15:
            priority = "GROWTH TARGET"
            msg = f"Solid conversion ({rate_pct} S1 rate). Automate {angle} with PandaDoc's template library and CRM integration."
        elif data["rate"] > 0:
            priority = "NURTURE"
            msg = f"Below-average conversion ({rate_pct} S1 rate). Test messaging around {angle} — may respond to different value prop."
        else:
            priority = "DEPRIORITIZE"
            msg = f"Zero conversion in dataset (0/{data['total']} leads). Do not invest in targeted campaigns until data changes."

        messaging[industry] = {
            "s1_rate": data["rate"],
            "leads": data["total"],
            "converted": data["converted"],
            "priority": priority,
            "messaging": msg,
        }

    return messaging


# ─────────────────────────────────────────────
# MESSAGING FRAMEWORK GENERATION
# ─────────────────────────────────────────────

def generate_messaging_frameworks(account_personas, industry_messaging_data=None):
    """Generate messaging frameworks differentiated by tier and persona."""
    frameworks = {
        "T1": generate_t1_messaging(account_personas),
        "T2": generate_t2_messaging(account_personas, industry_messaging_data),
        "T3": generate_t3_messaging(),
    }
    return frameworks


def generate_t1_messaging(account_personas):
    """T1: Fully personalized messaging per account per persona."""
    t1_accounts = {k: v for k, v in account_personas.items() if v["tier"] == "T1"}
    messages = {}

    for company, data in t1_accounts.items():
        messages[company] = {
            "strategy": build_t1_strategy(company, data),
            "persona_messages": {},
        }
        for contact in data["contacts"]:
            persona = contact["persona"]
            msg = build_personalized_message(
                company=company,
                contact_name=contact["name"],
                title=contact["title"],
                persona=persona,
                industry=data["industry"],
                crm=data["current_crm"],
                notes=data["sales_notes"],
                revenue=data["revenue_range"],
            )
            messages[company]["persona_messages"][contact["name"]] = msg

    return messages


def build_t1_strategy(company, data):
    """Build a high-level engagement strategy for a T1 account."""
    strategy = []
    strategy.append(f"**Account:** {company}")
    strategy.append(f"**Industry:** {data['industry']} | **Revenue:** {data['revenue_range']} | **CRM:** {data['current_crm']}")
    strategy.append(f"**Score:** {data['score']} | **Personas Present:** {', '.join(data['personas_present'])}")

    if data["missing_personas"]:
        strategy.append(f"**Multi-threading Gap:** Missing {', '.join(data['missing_personas'])} — need to identify and engage")

    if data["mentioned_stakeholders"]:
        mentioned = [f"{s['role']} ({s['persona']})" for s in data["mentioned_stakeholders"]]
        strategy.append(f"**Mentioned Stakeholders:** {', '.join(mentioned)}")

    if data["sales_notes"]:
        strategy.append(f"**Key Intel:** {data['sales_notes'][:300]}")

    return "\n".join(strategy)


def build_personalized_message(company, contact_name, title, persona, industry, crm, notes, revenue):
    """Build a personalized message for a specific contact at a T1 account."""
    persona_config = PERSONA_MAP.get(persona, PERSONA_MAP["Marketing / Other"])

    # Build context-aware hooks
    hooks = []
    if notes:
        notes_lower = notes.lower()
        if "google docs" in notes_lower or "manually" in notes_lower:
            hooks.append("manual document processes")
        if "contract error" in notes_lower or "version" in notes_lower:
            hooks.append("contract version control challenges")
        if "proposal" in notes_lower:
            hooks.append("proposal workflow optimization")
        if any(comp in notes_lower for comp in ["conga", "ironclad", "adobe sign", "proposify", "loopio", "qwilr"]):
            hooks.append("comparing document automation solutions")
        if "budget approved" in notes_lower or "budget pre-approved" in notes_lower:
            hooks.append("active buying cycle")

    message = {
        "persona": persona,
        "value_prop": persona_config["pandadoc_value"],
        "pain_addressed": persona_config["pain_points"][0] if persona_config["pain_points"] else "",
        "context_hooks": hooks,
        "recommended_content": get_recommended_content(persona, industry, hooks),
        "recommended_channel": get_recommended_channel_for_persona(persona, "T1"),
    }

    # Build the actual outreach angle
    if hooks:
        message["opening_angle"] = f"Based on {company}'s focus on {hooks[0]}, here's how PandaDoc helps {industry} companies like yours..."
    else:
        message["opening_angle"] = f"Many {industry} companies using {crm} are switching to PandaDoc to {persona_config['pain_points'][0].lower() if persona_config['pain_points'] else 'streamline document workflows'}..."

    return message


def generate_t2_messaging(account_personas, industry_messaging_data=None):
    """T2: Industry-cluster messaging with light personalization."""
    t2_accounts = {k: v for k, v in account_personas.items() if v["tier"] == "T2"}

    # Group by industry
    industry_clusters = defaultdict(list)
    for company, data in t2_accounts.items():
        industry_clusters[data["industry"]].append((company, data))

    messages = {}
    for industry, accounts in industry_clusters.items():
        # Use data-derived messaging if available, fall back to static
        if industry_messaging_data and industry in industry_messaging_data:
            ind_data = industry_messaging_data[industry]
            messaging_angle = ind_data["messaging"]
            s1_rate = ind_data["s1_rate"]
            priority = ind_data["priority"]
        else:
            messaging_angle = get_industry_messaging(industry)
            s1_rate = None
            priority = None

        messages[industry] = {
            "cluster_size": len(accounts),
            "messaging_angle": messaging_angle,
            "accounts": [a[0] for a in accounts],
            "s1_rate": s1_rate,
            "priority": priority,
        }

    return messages


def generate_t3_messaging():
    """T3: Persona-based template messaging (not company-specific)."""
    messages = {}
    for persona, config in PERSONA_MAP.items():
        if persona == "Marketing / Other":
            continue
        messages[persona] = {
            "subject_line_template": get_t3_subject(persona),
            "value_prop": config["pandadoc_value"],
            "cta": get_t3_cta(persona),
            "recommended_content": get_t3_content(persona),
        }
    return messages


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

INDUSTRY_MESSAGING = {
    "HR Tech": "Streamline your hiring and onboarding documents. From offer letters to contracts, PandaDoc automates the entire HR document lifecycle.",
    "Logistics": "Speed up vendor agreements and shipping contracts. PandaDoc's template library and CRM integration eliminate manual document bottlenecks.",
    "Financial Services": "Secure, compliant document workflows for financial services. Audit trails, version control, and e-signatures built for regulated industries.",
    "Real Estate": "Close deals faster with PandaDoc. From listing agreements to closing documents, automate your entire transaction workflow.",
    "Construction": "Standardize bids, proposals, and contracts. PandaDoc helps construction firms scale their document process without adding headcount.",
    "Consulting": "Win more engagements with professional proposals. Track when prospects view your SOWs and follow up at the perfect moment.",
    "Technology": "Accelerate your sales cycle with proposal automation. PandaDoc integrates natively with your CRM to build proposals from deal data.",
    "SaaS": "Scale your sales motion without scaling your ops team. PandaDoc automates proposals, contracts, and renewals from one platform.",
    "Legal": "Enterprise-grade contract management with built-in redlining, clause libraries, and compliance. PandaDoc is built for legal teams.",
    "Healthcare": "HIPAA-aware document workflows. Streamline patient agreements, vendor contracts, and compliance documentation.",
    "Education": "Simplify enrollment forms, vendor contracts, and grant proposals. PandaDoc's template library gets you started in minutes.",
    "Media": "Create stunning proposals that win clients. Track engagement and close deals faster with PandaDoc's all-in-one platform.",
    "Retail": "From vendor agreements to franchise documents, PandaDoc streamlines the retail document lifecycle end-to-end.",
    "Engineering": "Standardize SOWs, project proposals, and change orders. PandaDoc integrates with your project management tools.",
    "Insurance": "Automate policy documents, renewals, and claims forms. PandaDoc helps insurance teams reduce turnaround time by 65%.",
    "Manufacturing": "Streamline RFQs, purchase orders, and supplier contracts. PandaDoc brings manufacturing document workflows into the modern era.",
    "Marketing Agency": "Win more clients with stunning proposals. Track opens, time spent, and follow up when engagement peaks.",
    "Energy": "Manage complex energy contracts, permits, and compliance documents. PandaDoc provides the audit trail and version control you need.",
    "Professional Services": "From SOWs to NDAs, automate your professional services document workflow. PandaDoc integrates with your PSA tools.",
}


def get_industry_messaging(industry):
    return INDUSTRY_MESSAGING.get(industry, f"Streamline your {industry} document workflows with PandaDoc — proposals, contracts, and e-signatures in one platform.")


def get_recommended_content(persona, industry, hooks):
    """Recommend content pieces based on persona and context."""
    content = []
    if persona == "Champion / User Buyer":
        content.append(f"{industry} Proposal Template Pack")
        content.append("ROI Calculator: Time Saved Per Rep")
    elif persona == "Economic Buyer":
        content.append("PandaDoc ROI One-Pager")
        content.append(f"{industry} Cost Savings Case Study")
    elif persona == "Legal / Compliance":
        content.append("Security & Compliance Whitepaper")
        content.append("Contract Management Feature Guide")
    elif persona == "Technical Evaluator":
        content.append("Integration Architecture Guide")
        content.append("Implementation Timeline & Process")
    elif persona == "Executive Sponsor":
        content.append(f"{industry} Digital Transformation Brief")
        content.append("Competitive Landscape Overview")

    if "comparing document automation solutions" in hooks:
        content.append("Competitive Comparison: PandaDoc vs Alternatives")

    return content


def get_recommended_channel_for_persona(persona, tier):
    """Recommend the best outreach channel per persona per tier."""
    if tier == "T1":
        channels = {
            "Champion / User Buyer": "LinkedIn DM (HeyReach) + personalized email sequence",
            "Economic Buyer": "Executive-to-executive intro email + LinkedIn connection",
            "Legal / Compliance": "Dedicated compliance-focused demo invite via email",
            "Technical Evaluator": "Technical deep-dive webinar invite + integration documentation",
            "Executive Sponsor": "Executive briefing invitation + thought leadership content",
        }
    else:
        channels = {
            "Champion / User Buyer": "SDR email sequence + paid social (LinkedIn, Meta, Reddit, Quora, TikTok)",
            "Economic Buyer": "ROI-focused email nurture",
            "Legal / Compliance": "Compliance webinar invite",
            "Technical Evaluator": "Integration-focused content nurture",
            "Executive Sponsor": "Industry report + paid social (LinkedIn, Meta, TikTok)",
        }
    return channels.get(persona, "Multi-channel nurture sequence")


def get_t3_subject(persona):
    subjects = {
        "Champion / User Buyer": "How {industry} sales teams are closing deals 50% faster",
        "Economic Buyer": "Reducing document costs by 65% — here's the data",
        "Legal / Compliance": "Audit trails, redlining, and compliance — built in",
        "Technical Evaluator": "PandaDoc + {crm} integration: 5-minute setup guide",
        "Executive Sponsor": "Why leading {industry} companies are switching to PandaDoc",
    }
    return subjects.get(persona, "Streamline your document workflow with PandaDoc")


def get_t3_cta(persona):
    ctas = {
        "Champion / User Buyer": "Start free trial — build your first proposal in 10 minutes",
        "Economic Buyer": "Download ROI calculator",
        "Legal / Compliance": "Request security/compliance review",
        "Technical Evaluator": "Explore integrations",
        "Executive Sponsor": "Schedule executive briefing",
    }
    return ctas.get(persona, "Learn more about PandaDoc")


def get_t3_content(persona):
    content = {
        "Champion / User Buyer": ["Proposal Templates Gallery", "Product Demo Video", "Customer Story: Sales Team"],
        "Economic Buyer": ["ROI Guide", "Total Cost of Ownership Calculator", "CFO Brief"],
        "Legal / Compliance": ["Security Whitepaper", "SOC 2 Documentation", "Contract Management Guide"],
        "Technical Evaluator": ["API Documentation", "Integration Marketplace", "Implementation Guide"],
        "Executive Sponsor": ["Industry Report", "Digital Transformation Brief", "Executive Summary"],
    }
    return content.get(persona, ["Product Overview", "Getting Started Guide"])


# ─────────────────────────────────────────────
# OUTPUT GENERATION
# ─────────────────────────────────────────────

def run_persona_and_messaging(scored_accounts, output_dir="output", leads=None):
    """Run the complete persona mapping and messaging pipeline.

    Args:
        scored_accounts: Accounts with tier scores from Module 1
        output_dir: Output directory for reports
        leads: Raw leads for data-derived persona insights and industry messaging
    """
    print("\n" + "=" * 60)
    print("MODULE 2: BUYER COMMITTEE & MESSAGING FRAMEWORK")
    print("=" * 60)

    # Step 1: Derive persona insights from data
    persona_insights = None
    industry_messaging_data = None
    if leads:
        print("\n[1/4] Deriving persona insights from data (S1 conversion analysis)...")
        persona_insights = derive_persona_insights(leads)
        for persona, data in sorted(persona_insights.items(), key=lambda x: x[1]["rate"], reverse=True):
            if persona == "Marketing / Other":
                continue
            print(f"    {persona}: {data['rate']:.0%} S1 rate ({data['converted']}/{data['total']}), ${data['avg_acv']:,.0f} avg ACV")
            if data["top_pain_points"]:
                print(f"      Top pains: {', '.join(data['top_pain_points'][:2])}")

        print("\n[2/4] Deriving industry messaging from conversion data...")
        industry_messaging_data = derive_industry_messaging(leads)
        for industry, data in list(industry_messaging_data.items())[:5]:
            print(f"    {industry}: {data['s1_rate']:.0%} S1 ({data['converted']}/{data['leads']}) → {data['priority']}")
    else:
        print("\n[1/4] No raw leads provided — using static persona map")
        print("[2/4] Skipping data-derived industry messaging")

    # Step 2: Map personas per account
    print("\n[3/4] Mapping contacts to buying committee personas...")
    account_personas = map_personas(scored_accounts)

    # Persona distribution
    persona_counts = Counter()
    for company, data in account_personas.items():
        for contact in data["contacts"]:
            persona_counts[contact["persona"]] += 1

    print("\n  PERSONA DISTRIBUTION:")
    for persona, count in persona_counts.most_common():
        print(f"    {persona}: {count} contacts")

    # Multi-threading gap analysis
    accounts_with_gaps = sum(1 for d in account_personas.values() if d["missing_personas"])
    print(f"\n  MULTI-THREADING GAPS: {accounts_with_gaps}/{len(account_personas)} accounts missing key personas")

    # Step 3: Generate messaging
    print("\n[4/4] Generating messaging frameworks by tier...")
    frameworks = generate_messaging_frameworks(account_personas, industry_messaging_data)

    t1_count = len(frameworks["T1"])
    t2_clusters = len(frameworks["T2"])
    t3_personas = len(frameworks["T3"])
    print(f"  T1: {t1_count} fully personalized account strategies")
    print(f"  T2: {t2_clusters} industry cluster messaging frameworks")
    print(f"  T3: {t3_personas} persona-based templates")

    # Step 4: Output
    print("\n  Generating outputs...")

    # Persona map report (with data-derived insights)
    persona_report = generate_persona_report(account_personas, persona_counts, persona_insights)
    write_markdown(os.path.join(output_dir, "persona_map.md"), persona_report)

    # Messaging frameworks report
    messaging_report = generate_messaging_report(frameworks, account_personas, persona_insights, industry_messaging_data)
    write_markdown(os.path.join(output_dir, "messaging_frameworks.md"), messaging_report)

    print("\n✓ Module 2 complete.")
    return account_personas, frameworks


def generate_persona_report(account_personas, persona_counts, persona_insights=None):
    """Generate the persona mapping markdown report with data-derived insights."""
    lines = []
    lines.append("# Buyer Committee Mapping Report")
    lines.append("")

    # Data-derived persona analysis
    if persona_insights:
        lines.append("## Persona Conversion Analysis (from 150-lead dataset)")
        lines.append("")
        lines.append("Each persona's S1 conversion rate, pipeline value, and pain points are derived directly from the data.")
        lines.append("These metrics determine persona priority in the engagement strategy.")
        lines.append("")
        lines.append("| Persona | Leads | S1 | S1 Rate | Pipeline | Avg ACV | Top Industries |")
        lines.append("|---------|-------|-----|---------|----------|---------|---------------|")
        for persona, data in sorted(persona_insights.items(), key=lambda x: x[1]["rate"], reverse=True):
            if persona == "Marketing / Other" and data["total"] < 3:
                continue
            industries = ", ".join(data["top_industries"][:3])
            lines.append(f"| {persona} | {data['total']} | {data['converted']} | {data['rate']:.0%} | ${data['total_pipeline']:,.0f} | ${data['avg_acv']:,.0f} | {industries} |")
        lines.append("")

        # Data-derived pain points per persona
        lines.append("### Pain Points by Persona (from Sales Notes)")
        lines.append("")
        lines.append("These pain points are extracted from actual sales notes in the dataset, not assumed.")
        lines.append("")
        for persona, data in sorted(persona_insights.items(), key=lambda x: x[1]["rate"], reverse=True):
            if persona == "Marketing / Other" and data["total"] < 3:
                continue
            if data["top_pain_points"]:
                lines.append(f"**{persona}** ({data['rate']:.0%} S1 rate):")
                for pain in data["top_pain_points"]:
                    lines.append(f"- {pain}")
                lines.append("")

        # Titles seen in data
        lines.append("### Actual Titles in Dataset → Persona Mapping")
        lines.append("")
        lines.append("| Title | Persona | Count |")
        lines.append("|-------|---------|-------|")
        all_titles = []
        for persona, data in persona_insights.items():
            for title, count in data["titles_seen"].items():
                all_titles.append((title, persona, count))
        for title, persona, count in sorted(all_titles, key=lambda x: x[2], reverse=True):
            lines.append(f"| {title} | {persona} | {count} |")
        lines.append("")

    lines.append("## PandaDoc Buying Committee")
    lines.append("Based on analysis of 150 leads and sales notes, PandaDoc deals typically involve 3-5 stakeholders:")
    lines.append("")
    lines.append("| Persona | Role Examples | What They Care About | # in Dataset |")
    lines.append("|---------|-------------|---------------------|-------------|")
    for persona, config in PERSONA_MAP.items():
        count = persona_counts.get(persona, 0)
        titles = ", ".join(config["titles"][:3])
        lines.append(f"| {persona} | {titles} | {config['cares_about']} | {count} |")
    lines.append("")

    # Key insight from data
    lines.append("## Key Insight: Legal is the Blocker")
    lines.append("Sales notes repeatedly show Legal/Compliance as the primary blocker in PandaDoc deals:")
    lines.append("- *'Legal team is the primary blocker — they want custom clause libraries and redlining'*")
    lines.append("- *'General Counsel needs a separate demo'*")
    lines.append("- *'VP of Operations (General Counsel) needs a separate demo'*")
    lines.append("")
    lines.append("**Implication:** Every ABM play should include Legal-specific content and a path to a compliance-focused demo.")
    lines.append("")

    # Multi-threading analysis
    lines.append("## Multi-Threading Gap Analysis")
    lines.append("Most accounts have only 1 known contact. Key personas to map and engage:")
    lines.append("")

    # T1 accounts detail
    t1_accounts = {k: v for k, v in account_personas.items() if v["tier"] == "T1"}
    if t1_accounts:
        lines.append("### T1 Account Persona Coverage")
        lines.append("| Company | Known Persona | Missing Personas | Mentioned in Notes |")
        lines.append("|---------|--------------|-----------------|-------------------|")
        for company, data in sorted(t1_accounts.items(), key=lambda x: x[1]["score"], reverse=True):
            present = ", ".join(data["personas_present"])
            missing = ", ".join(data["missing_personas"]) if data["missing_personas"] else "None"
            mentioned = ", ".join([s["role"] for s in data["mentioned_stakeholders"]]) if data["mentioned_stakeholders"] else "-"
            lines.append(f"| {company} | {present} | {missing} | {mentioned} |")
        lines.append("")

    return "\n".join(lines)


def generate_messaging_report(frameworks, account_personas, persona_insights=None, industry_messaging_data=None):
    """Generate the messaging frameworks markdown report — PERSONA-FIRST structure."""
    lines = []
    lines.append("# Buyer Committee Messaging Frameworks")
    lines.append("")
    lines.append("One messaging framework per buying committee persona. Each framework defines:")
    lines.append("what they care about, PandaDoc's value prop for them, their pain points,")
    lines.append("recommended content, channels, and example messaging angles.")
    lines.append("")
    if persona_insights:
        lines.append("*All conversion rates and pain points are derived from the 150-lead dataset.*")
        lines.append("")

    # ── CORE: One framework per persona ──
    for persona, config in PERSONA_MAP.items():
        if persona == "Marketing / Other":
            continue

        lines.append("---")
        lines.append(f"## {persona}")
        lines.append("")

        # Add data-derived stats if available
        if persona_insights and persona in persona_insights:
            pi = persona_insights[persona]
            lines.append(f"**Data:** {pi['total']} leads in dataset | {pi['converted']} S1 conversions | **{pi['rate']:.0%} S1 rate** | ${pi['total_pipeline']:,.0f} pipeline")
            lines.append("")

        lines.append(f"**Typical Titles:** {', '.join(config['titles'][:5])}")
        lines.append(f"**What They Care About:** {config['cares_about']}")
        lines.append("")

        lines.append("### Value Proposition")
        lines.append(f"{config['pandadoc_value']}")
        lines.append("")

        lines.append("### Pain Points to Address")
        # Use data-derived pain points if available, supplement with product knowledge
        if persona_insights and persona in persona_insights and persona_insights[persona]["top_pain_points"]:
            lines.append("*(Derived from sales notes in the dataset:)*")
            for pain in persona_insights[persona]["top_pain_points"]:
                lines.append(f"- {pain}")
        else:
            for pain in config["pain_points"]:
                lines.append(f"- {pain}")
        lines.append("")

        lines.append("### Recommended Content")
        t3_content = get_t3_content(persona)
        for c in t3_content:
            lines.append(f"- {c}")
        lines.append("")

        lines.append("### Example Subject Lines")
        lines.append(f"- {get_t3_subject(persona)}")
        lines.append("")

        lines.append("### Call to Action")
        lines.append(f"- {get_t3_cta(persona)}")
        lines.append("")

        lines.append("### Channel Strategy")
        lines.append(f"- **T1 (1:1):** {get_recommended_channel_for_persona(persona, 'T1')}")
        lines.append(f"- **T2/T3:** {get_recommended_channel_for_persona(persona, 'T2')}")
        lines.append("")

    # ── SECONDARY: How delivery scales by tier ──
    lines.append("---")
    lines.append("## How Messaging Delivery Differs by Tier")
    lines.append("")
    lines.append("The frameworks above define WHAT to say to each persona. The tier determines HOW it gets delivered:")
    lines.append("")
    lines.append("| Dimension | T1 (1:1 Strategic) | T2 (1:Few Cluster) | T3 (1:Many Programmatic) |")
    lines.append("|-----------|-------------------|-------------------|------------------------|")
    lines.append("| Personalization | Fully custom — references their CRM, sales notes, specific pain | Industry-cluster — same vertical messaging, personalized intro | Persona template — role-specific but not company-specific |")
    lines.append("| Who writes it | AE + AI draft reviewed by human | AI-generated with human review of first batch | AI-generated, automated |")
    lines.append("| Channels | LinkedIn DM + email + direct mail + exec events | Paid social (LinkedIn, Meta, Reddit, Quora, TikTok) + SDR sequences + webinars | Automated email nurture + programmatic paid social |")
    lines.append("| Content | Custom business case, personalized video | Industry case study, ROI calculator | Blog posts, templates, product overview |")
    lines.append("| Cadence | 5-7 touches over 3 weeks per persona | 3-touch sequence per persona | Bi-weekly automated emails |")
    lines.append("")

    # ── BONUS: T1 personalized examples ──
    lines.append("---")
    lines.append("## T1 Personalized Messaging Examples")
    lines.append("Showing how the persona frameworks get applied to specific T1 accounts:")
    lines.append("")
    for company, data in frameworks["T1"].items():
        lines.append(f"### {company}")
        lines.append(data["strategy"])
        lines.append("")
        for contact_name, msg in data["persona_messages"].items():
            lines.append(f"**{contact_name}** ({msg['persona']})")
            lines.append(f"- Opening: {msg['opening_angle']}")
            lines.append(f"- Value Prop: {msg['value_prop']}")
            lines.append(f"- Channel: {msg['recommended_channel']}")
            lines.append(f"- Content: {', '.join(msg['recommended_content'])}")
            if msg["context_hooks"]:
                lines.append(f"- Context: {', '.join(msg['context_hooks'])}")
            lines.append("")
        lines.append("---")

    # ── BONUS: T2 industry clusters ──
    lines.append("")
    lines.append("## T2 Industry Cluster Messaging")
    lines.append("")

    # Sort by S1 rate if available, else by cluster size
    t2_items = list(frameworks["T2"].items())
    if any(d.get("s1_rate") is not None for _, d in t2_items):
        t2_items.sort(key=lambda x: (x[1].get("s1_rate") or 0), reverse=True)
        lines.append("*Ordered by S1 conversion rate from the dataset.*")
        lines.append("")
    else:
        t2_items.sort(key=lambda x: x[1]["cluster_size"], reverse=True)

    for industry, data in t2_items:
        rate_str = f" | **{data['s1_rate']:.0%} S1 rate**" if data.get("s1_rate") is not None else ""
        priority_str = f" | {data['priority']}" if data.get("priority") else ""
        lines.append(f"### {industry} ({data['cluster_size']} accounts{rate_str}{priority_str})")
        lines.append(f"**Messaging Angle:** {data['messaging_angle']}")
        lines.append(f"**Accounts:** {', '.join(data['accounts'][:10])}")
        if len(data['accounts']) > 10:
            lines.append(f"  + {len(data['accounts']) - 10} more")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# STANDALONE EXECUTION
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    base = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, base)
    sys.path.insert(0, os.path.join(base, "01_account_tiering"))
    from utils import load_leads
    from account_tiering_model import run_tiering
    leads = load_leads(os.path.join(base, "data", "funnel_leads.csv"))
    scored_accounts, weights, analysis = run_tiering(leads, os.path.join(base, "01_account_tiering"))
    run_persona_and_messaging(scored_accounts, os.path.dirname(__file__))
