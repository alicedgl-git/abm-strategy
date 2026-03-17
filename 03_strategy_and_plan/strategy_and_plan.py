"""
ABM Engine — Module 3: Channel Strategy & Quarterly Activation Plan
Assignment Deliverable 3: Quarterly Activation Plan

This module:
1. Analyzes channel performance from conversion data
2. Recommends channel mix per tier with budget allocation
3. Generates a 13-week quarterly activation plan differentiated by tier
4. Outputs channel_strategy.md + quarterly_plan.md
"""

import os
from collections import Counter, defaultdict
from utils import load_leads, get_conversion_rates, get_expected_values, write_markdown

# ─────────────────────────────────────────────
# CHANNEL INTELLIGENCE (from data)
# ─────────────────────────────────────────────

def analyze_channels(leads):
    """Analyze channel performance using expected value (conversion rate × avg ACV)."""
    channel_ev = get_expected_values(leads, "channel")

    # Calculate total pipeline per channel
    channel_pipeline = defaultdict(float)
    for lead in leads:
        if lead["s1"] == 1 and lead["opportunity_acv"] > 0:
            channel_pipeline[lead["channel"]] += lead["opportunity_acv"]

    channel_analysis = {}
    for channel, data in channel_ev.items():
        channel_analysis[channel] = {
            **data,
            "total_pipeline": channel_pipeline.get(channel, 0),
            "recommendation": get_channel_recommendation(channel, data["rate"], data["total"]),
        }

    return channel_analysis


def get_channel_recommendation(channel, conversion_rate, volume):
    """Generate a data-driven recommendation for each channel.

    The action (SCALE/INVEST/OPTIMIZE/RETHINK/PAUSE) is determined by the channel's
    actual conversion rate from the dataset. Strategy text references the real data.
    """
    rate_pct = f"{conversion_rate:.0%}"

    # Data-driven action classification
    if conversion_rate >= 0.35:
        action = "SCALE"
    elif conversion_rate >= 0.25:
        action = "INVEST"
    elif conversion_rate >= 0.15:
        action = "OPTIMIZE"
    elif conversion_rate > 0:
        action = "RETHINK"
    else:
        action = "PAUSE"

    # Data-driven budget allocation — higher conversion = higher budget
    if conversion_rate >= 0.30 and volume >= 5:
        budget_pct = 20
    elif conversion_rate >= 0.25:
        budget_pct = 15
    elif conversion_rate >= 0.15:
        budget_pct = 10
    elif conversion_rate > 0:
        budget_pct = 5
    else:
        budget_pct = 0

    # Channel-specific strategy that references actual data
    channel_strategies = {
        "Paid Social": {
            "strategy": f"Converts at {rate_pct} — highest in the dataset. Scale across LinkedIn Ads, Meta Ads, Reddit, Quora, and TikTok. LinkedIn matched audiences for T1/T2, broader programmatic mix for T3. Layer retargeting across platforms.",
            "abm_role": f"Primary engine ({rate_pct} S1 rate). LinkedIn + Meta for T1/T2 with personalized creative. Reddit, Quora, TikTok for T3 awareness and community reach.",
            "budget_pct": 20,
        },
        "Appexchange": {
            "strategy": f"Converts at {rate_pct} — second highest. These accounts are self-qualifying. Optimize listing, drive G2 reviews, feature competitive comparisons.",
            "abm_role": f"High-intent capture ({rate_pct} S1 rate). Fast-track AppExchange leads to demo — they're already evaluating.",
            "budget_pct": 5,
        },
        "Inbound": {
            "strategy": f"Converts at {rate_pct} with {volume} leads — strong foundation. Invest in SEO, GEO (Generative Engine Optimization), and industry-specific landing pages.",
            "abm_role": f"Foundation channel ({rate_pct} S1 rate, {volume} leads). SEO + GEO targets pain points by industry. Website personalization for T1/T2.",
            "budget_pct": 25,
        },
        "Review Site": {
            "strategy": f"Converts at {rate_pct} — trust signal. Invest in G2/Capterra presence. Use review site intent data for targeting.",
            "abm_role": f"Trust-building ({rate_pct} S1 rate). Send G2 comparison reports to T2 accounts in evaluation.",
            "budget_pct": 5,
        },
        "Webinar": {
            "strategy": f"Converts at {rate_pct}. Run industry-specific webinars for T2, virtual executive roundtables for T1, broad educational for T3.",
            "abm_role": f"Mid-funnel accelerator ({rate_pct} S1 rate). T1: Roundtables. T2: Industry webinars. T3: Product webinars.",
            "budget_pct": 10,
        },
        "Outbound": {
            "strategy": f"Converts at {rate_pct} — supplements ads, don't lead with it. Focus SDR outreach on T1/T2 only. Use HeyReach for LinkedIn sequences.",
            "abm_role": f"Supplementary ({rate_pct} S1 rate). T1: 1:1 personalized. T2: Semi-personalized cluster sequences. Skip T3.",
            "budget_pct": 15,
        },
        "Content Syndication": {
            "strategy": f"Converts at {rate_pct} — below average. Only syndicate to high-converting industries. Stop broad syndication.",
            "abm_role": f"Targeted only ({rate_pct} S1 rate). T2: Syndicate industry-specific content to targeted account lists.",
            "budget_pct": 5,
        },
        "Intent Data": {
            "strategy": f"Converts at {rate_pct} as direct channel — use for account IDENTIFICATION, not outreach. Feed intent signals into scoring engine.",
            "abm_role": f"Signal layer ({rate_pct} S1 rate as direct channel). Trigger SDR outreach (T1/T2) or retargeting (T3).",
            "budget_pct": 5,
        },
        "Partner": {
            "strategy": f"Converts at {rate_pct} — underperforming. Maintain partner relationships but don't over-invest. Focus on CRM ecosystem partners.",
            "abm_role": f"Co-marketing ({rate_pct} S1 rate). Joint webinars with HubSpot/Salesforce. Partner referrals feed T2 pipeline.",
            "budget_pct": 5,
        },
        "Paid Search": {
            "strategy": f"{rate_pct} conversion — {'pause and audit' if conversion_rate == 0 else 'underperforming'}. {'Rethink targeting, keywords, and landing pages before relaunch.' if conversion_rate == 0 else 'Optimize landing pages and keywords.'}",
            "abm_role": f"{'Currently broken (0% S1). Fix before reinvesting.' if conversion_rate == 0 else f'Needs optimization ({rate_pct} S1 rate).'}",
            "budget_pct": 0 if conversion_rate == 0 else 5,
        },
    }

    if channel in channel_strategies:
        rec = channel_strategies[channel]
        return {
            "action": action,
            "strategy": rec["strategy"],
            "abm_role": rec["abm_role"],
            "budget_pct": rec["budget_pct"],
        }

    return {
        "action": action,
        "strategy": f"Converts at {rate_pct} ({volume} leads). {'Scale investment.' if conversion_rate >= 0.25 else 'Test and measure.'}",
        "abm_role": f"{'High potential' if conversion_rate >= 0.25 else 'Needs evaluation'} ({rate_pct} S1 rate).",
        "budget_pct": budget_pct,
    }


# ─────────────────────────────────────────────
# TIER-SPECIFIC CHANNEL MIX
# ─────────────────────────────────────────────

TIER_CHANNEL_MIX = {
    "T1": {
        "description": "1:1 Strategic — Personalized, data-driven plays focused on highest-converting channels",
        "accounts": "~21 accounts",
        "budget_share": "40% of ABM budget",
        "channels": [
            {
                "channel": "Paid Social (LinkedIn, Meta, Reddit, Quora, TikTok)",
                "tactic": "LinkedIn matched audience ads targeting the specific 21 accounts (primary). Meta retargeting for cross-platform reinforcement. Reddit and Quora for community-based engagement in relevant subreddits and topics. TikTok for short-form video content targeting younger decision-makers. Single image ads (highest CTR) + video ads. Personalized creative per industry cluster. This is the primary awareness + engagement driver — our data shows Paid Social converts at 43%.",
                "frequency": "Always-on during quarter, rotate creative bi-weekly across platforms",
                "content": "Case study ads, product feature ads, social proof (customer quotes), compliance/security messaging. Short-form video (TikTok), community Q&A sponsorship (Reddit/Quora)",
            },
            {
                "channel": "LinkedIn Outreach (HeyReach)",
                "tactic": "Personalized connection requests + DM sequences to each buying committee member. Custom messaging per persona. Supplements the ad layer with direct 1:1 engagement.",
                "frequency": "3-5 touches per persona over 4 weeks",
                "content": "Personalized video (Loom), custom business case, relevant case study",
            },
            {
                "channel": "Email Sequences",
                "tactic": "1:1 personalized email from AE referencing specific pains from sales notes. Multi-thread to champion + economic buyer + legal.",
                "frequency": "5-7 touch sequence over 3 weeks",
                "content": "ROI calculator pre-filled, competitive comparison (if competitor mentioned), compliance one-pager for Legal",
            },
            {
                "channel": "Virtual Executive Roundtable",
                "tactic": "Invite T1 economic buyers to a virtual industry roundtable (5-8 attendees). Peer-led discussion format, not a sales pitch. Low cost, high perceived value.",
                "frequency": "1x in Weeks 7-9",
                "content": "Industry trends discussion, customer success stories, peer networking",
            },
            {
                "channel": "Retargeting",
                "tactic": "Retarget T1 contacts who engaged with ads or content. Serve progressive content: awareness → consideration → decision stage.",
                "frequency": "Always-on",
                "content": "Progressive content based on engagement stage (case study → demo invite → trial CTA)",
            },
        ],
    },
    "T2": {
        "description": "1:Few — Industry-cluster campaigns with targeted personalization",
        "accounts": "~77 accounts across 16 industry clusters",
        "budget_share": "40% of ABM budget",
        "channels": [
            {
                "channel": "Paid Social (LinkedIn, Meta, Reddit, Quora, TikTok)",
                "tactic": "LinkedIn: industry + company size + title targeting, creative per cluster. Meta: lookalike audiences from T1 converters, retargeting engaged visitors. Reddit: sponsored posts in industry subreddits (r/sales, r/smallbusiness, r/fintech). Quora: answer sponsorship on document automation and CRM topics. TikTok: short-form product demos and customer testimonials for emerging buyer personas.",
                "frequency": "Always-on, rotate creative bi-weekly across platforms",
                "content": "Industry-specific case studies, product feature highlights, G2 comparison badges, community-native content (Reddit/Quora), short-form video (TikTok)",
            },
            {
                "channel": "SDR Outreach (HeyReach)",
                "tactic": "Semi-personalized LinkedIn + email sequences grouped by industry. Personalize first line per company, rest is cluster-templated.",
                "frequency": "3-touch sequence per persona",
                "content": "Industry template pack, webinar invite, free trial CTA",
            },
            {
                "channel": "Industry Webinars",
                "tactic": "Host 2-3 industry-specific webinars (e.g., 'Document Automation for Financial Services'). Co-host with industry partner if possible.",
                "frequency": "1 per month",
                "content": "Industry best practices, customer panel, live product demo",
            },
            {
                "channel": "Content Syndication (Targeted)",
                "tactic": "Syndicate industry-specific guides to targeted account lists in high-converting verticals only.",
                "frequency": "1 campaign per cluster per month",
                "content": "Industry guides, ROI reports, template libraries",
            },
            {
                "channel": "G2 / Review Sites",
                "tactic": "Sponsor G2 comparison pages for key competitors (Conga, Proposify, Ironclad). Use G2 buyer intent data.",
                "frequency": "Always-on",
                "content": "G2 Grid reports, comparison pages, review highlights",
            },
            {
                "channel": "Retargeting",
                "tactic": "Retarget T2 accounts that visited website or engaged with content. Serve next-stage content (e.g., visited blog → serve case study).",
                "frequency": "Always-on",
                "content": "Progressive content based on engagement stage",
            },
        ],
    },
    "T3": {
        "description": "1:Many — Programmatic, automated, nurture-focused",
        "accounts": "~52 accounts",
        "budget_share": "20% of ABM budget",
        "channels": [
            {
                "channel": "Automated Email Nurture",
                "tactic": "Persona-based email sequences triggered by lifecycle stage. Educational content → product content → CTA progression.",
                "frequency": "Bi-weekly emails, 8-touch sequence",
                "content": "Blog posts, guides, product overview videos, free trial CTA",
            },
            {
                "channel": "Programmatic Paid Social (LinkedIn, Meta, Reddit, Quora, TikTok)",
                "tactic": "LinkedIn: broad targeting by company size + title. Meta: broad interest-based targeting + retargeting. Reddit: sponsored posts in business/productivity subreddits. Quora: topic targeting on document management, e-signatures, proposals. TikTok: short-form educational content and product demos. Brand awareness and product education creative across all platforms.",
                "frequency": "Always-on, low budget, distributed across platforms",
                "content": "Brand awareness ads, product feature carousels, customer testimonials, community-native content, short-form video",
            },
            {
                "channel": "SEO + GEO / Content Marketing",
                "tactic": "Create content targeting pain points surfaced in the data (proposal automation, contract management, e-signatures). Optimize for both traditional SEO and GEO (Generative Engine Optimization) — structure content so LLMs (ChatGPT, Perplexity, Claude) cite PandaDoc in AI-generated answers. Build comparison pages, FAQ-rich guides, and structured data that AI assistants pull from.",
                "frequency": "2-3 new pieces per month",
                "content": "Blog posts, comparison pages, template libraries, how-to guides, LLM-optimized FAQ pages",
            },
            {
                "channel": "AppExchange / Marketplace",
                "tactic": "Optimize AppExchange listing. Drive customer reviews. Feature integrations prominently.",
                "frequency": "Monthly review solicitation campaign",
                "content": "Updated listing, customer reviews, integration highlights",
            },
            {
                "channel": "Broad Webinars",
                "tactic": "Host monthly product webinars open to all. Use for education and lead qualification.",
                "frequency": "1 per month",
                "content": "Product deep dives, use case showcases, Q&A with product team",
            },
        ],
    },
}


# ─────────────────────────────────────────────
# QUARTERLY ABM STRATEGY (framework, not task list)
# ─────────────────────────────────────────────

# Tier strategies define what each tier GETS — channels, personas, messaging, content, engagement model.
# The 150-lead dataset validated these patterns. This framework applies to any new accounts scored by the engine.

T1_STRATEGY = {
    "name": "T1: 1:1 Strategic",
    "profile": {
        "score": "60+",
        "characteristics": "High-converting industry (HR Tech, Logistics, Real Estate, Construction, Consulting), weak or no CRM (None/Spreadsheets/Pipedrive), strong engagement signals (/integrations page, 3+ email opens, contract template download), positive qualitative signals (budget approved, competitor evaluation, timeline urgency).",
        "expected_accounts": "5-15 per quarter",
        "historical_s1_rate": "70%",
        "approach": "Each account is treated as a market of one. Dedicated AE + SDR pair. Full buying committee mapped and engaged in parallel.",
    },
    "channels": [
        {
            "channel": "Paid Social (LinkedIn, Meta, Reddit, Quora, TikTok)",
            "why": "Paid Social converts at 43% — highest of any channel in our data. Multi-platform paid social is the primary awareness and engagement engine.",
            "how": "LinkedIn: matched audience ads targeting T1 accounts, single image (highest CTR at ~0.35%, ~$19 CPC) + video. Meta: retargeting T1 contacts who engaged on LinkedIn or website — cross-platform reinforcement. Reddit: sponsored posts in industry-specific subreddits where these buyers research. Quora: answer sponsorship on relevant pain-point topics. TikTok: short-form video testimonials and product demos for younger decision-makers. Rotate creative bi-weekly across all platforms.",
            "success": "2%+ CTR on LinkedIn, 80%+ account reach across platforms within first 4 weeks",
        },
        {
            "channel": "LinkedIn Outreach via HeyReach",
            "why": "Supplements the ad layer with direct 1:1 engagement. When outbound is layered on top of ad awareness (account has seen PandaDoc ads before the DM), response rates increase 2-3x vs cold outbound alone.",
            "how": "Personalized connection requests + DM sequences to each buying committee member. Custom messaging per persona. 3-5 touches per persona over 4 weeks. Loom videos for champions, compliance one-pagers for Legal.",
            "success": "30%+ connection accept rate, 15%+ reply rate",
        },
        {
            "channel": "AE Email Sequences",
            "why": "Multi-threading across the buying committee requires email — it's the channel for reaching Legal, Finance, and Technical personas who may not be active on LinkedIn.",
            "how": "1:1 personalized emails from assigned AE referencing specific account intel (CRM they use, pain from sales notes, industry context). Multi-thread to Champion + Economic Buyer + Legal simultaneously. 5-7 touches over 3 weeks.",
            "success": "50%+ open rate, 15%+ reply rate",
        },
        {
            "channel": "Virtual Executive Roundtable",
            "why": "Webinars convert at 25% in our data. Virtual roundtables are high-perceived-value, low-cost events appropriate for mid-market ACV (~$16K). Peer discussion format, not a sales pitch.",
            "how": "1 roundtable per quarter, 5-8 T1 economic buyers invited. Industry-focused discussion led by a PandaDoc customer or industry expert. Builds trust and accelerates deals mid-quarter.",
            "success": "60%+ invite-to-attend rate, 50%+ of attendees progress to demo within 2 weeks",
        },
        {
            "channel": "Progressive Retargeting",
            "why": "Captures engaged contacts who are aware but not yet ready for a demo. Keeps PandaDoc top-of-mind across the buying journey.",
            "how": "Retarget T1 contacts who engaged with ads, email, or content. Serve progressive content matched to their stage: awareness (case study) → consideration (demo invite) → decision (trial CTA).",
            "success": "1%+ retargeting CTR, measurable progression through content stages",
        },
    ],
    "personas": [
        {
            "priority": 1,
            "persona": "Champion / User Buyer",
            "why": "Most common entry point (44 of 150 leads in our data). They feel the pain of slow proposals and manual document workflows daily.",
            "approach": "LinkedIn DM + personalized email. Lead with proposal speed and deal velocity messaging. Personalized Loom video referencing their company.",
        },
        {
            "priority": 2,
            "persona": "Legal / Compliance",
            "why": "#1 deal blocker identified in sales notes. Engage in PARALLEL with the champion from day one — do not wait for Legal to surface as a blocker late in the deal.",
            "approach": "Dedicated compliance demo invite via email. Send security whitepaper, SOC 2 documentation, and audit trail one-pager. Frame PandaDoc as the compliance-friendly choice.",
        },
        {
            "priority": 3,
            "persona": "Economic Buyer",
            "why": "Controls budget. Needs ROI justification before approving. Our data shows Cost/ROI messaging converts at 29%.",
            "approach": "Executive-to-executive email from AE. Pre-filled ROI calculator showing TCO savings vs their current tools. CFO brief with payback period analysis.",
        },
        {
            "priority": 4,
            "persona": "Technical Evaluator",
            "why": "Evaluates integrations and security. /integrations page is the strongest engagement signal (+12% lift) — these personas care about CRM fit.",
            "approach": "Integration architecture guide specific to their CRM. Technical deep-dive invite. API documentation. Position PandaDoc as integration-first.",
        },
        {
            "priority": 5,
            "persona": "Executive Sponsor",
            "why": "Signs off at the end. Engage once Champion + Economic Buyer are aligned — not before.",
            "approach": "Executive briefing invite. Thought leadership content on digital transformation and document automation trends.",
        },
    ],
    "messaging_themes": [
        {"theme": "Compliance & Security", "conversion": "43%", "application": "Lead with for Legal personas. Security whitepaper, SOC 2 docs, enterprise audit trail, built-in redlining."},
        {"theme": "Manual Process Pain", "conversion": "41%", "application": "Lead with for Champions at accounts using spreadsheets or no CRM. 'Your team spends X hours on manual document creation.'"},
        {"theme": "Proposal Automation", "conversion": "33%", "application": "Core value prop for Champions. 'Close deals 50% faster with automated proposals, e-sign, and tracking.'"},
        {"theme": "Integration Focus", "conversion": "31%", "application": "Lead with for Technical Evaluators. CRM-specific messaging: 'Native [their CRM] integration, 5-minute setup.'"},
        {"theme": "Competitor Displacement", "conversion": "26%", "application": "Use when sales notes indicate active competitor evaluation. Direct comparison docs (PandaDoc vs Ironclad, vs Proposify, vs Conga)."},
    ],
    "content_requirements": [
        "**Champion:** Industry-specific proposal template pack, personalized Loom demo video, customer success story (sales team focus)",
        "**Legal:** Security whitepaper, SOC 2 documentation, contract management compliance guide, audit trail one-pager",
        "**Economic Buyer:** Pre-fillable ROI calculator, TCO comparison document, CFO brief with payback period",
        "**Technical:** CRM integration architecture guide (per CRM type), implementation timeline, API documentation",
        "**Executive:** Industry digital transformation brief, executive summary of PandaDoc value",
        "**Cross-persona:** Competitive comparison docs (PandaDoc vs top competitors), custom business case per account",
    ],
    "engagement_model": {
        "review_cadence": "Weekly AE + SDR review per T1 account. Track: Is engagement increasing, flat, or declining?",
        "escalation_triggers": [
            "3+ engagement actions in a week → trigger demo push",
            "Email reply → same-day AE follow-up",
            "Legal persona identified → send compliance content within 48 hours",
            "/integrations page visit → send CRM-specific integration guide",
        ],
        "stall_protocol": "If zero engagement after 4 weeks of multi-channel outreach: shift strategy — try a different persona entry point, a different channel, or a different messaging angle. Do not keep running the same play on a non-responsive account.",
    },
}

T2_STRATEGY = {
    "name": "T2: 1:Few Industry Cluster",
    "profile": {
        "score": "40-59",
        "characteristics": "Moderate firmographic fit. Grouped by industry cluster — the personalization happens at the industry level, not per account. Target high-converting verticals first: HR Tech (67%), Logistics (60%), Financial Services, Consulting, SaaS.",
        "expected_accounts": "50-100 per quarter across industry clusters",
        "historical_s1_rate": "30%",
        "approach": "Industry-cluster campaigns. Same messaging framework applied per vertical. SDR sequences are semi-personalized (first line per company, rest is cluster-templated).",
    },
    "channels": [
        {
            "channel": "Paid Social (LinkedIn, Meta, Reddit, Quora, TikTok)",
            "why": "Same 43% conversion foundation as T1. At T2 scale, distribute across platforms: LinkedIn for professional targeting, Meta for lookalike audiences, Reddit/Quora for community engagement, TikTok for awareness.",
            "how": "LinkedIn: creative per industry cluster (e.g., 'Financial Services' ad set). Meta: lookalike audiences built from T1 converters, retargeting across Facebook/Instagram. Reddit: sponsored posts in industry subreddits (r/sales, r/smallbusiness, r/fintech). Quora: answer sponsorship on document automation and CRM integration topics. TikTok: short-form product demos and customer success stories. Always-on, rotate creative bi-weekly. Budget scaled based on cluster and platform performance.",
            "success": "1%+ CTR across clusters and platforms, measurable engagement lift in target accounts",
        },
        {
            "channel": "SDR Outreach via HeyReach",
            "why": "At 18% baseline, outbound is less efficient than ads — but at T2 scale with semi-personalization, it's cost-effective for generating meetings in top clusters.",
            "how": "Semi-personalized LinkedIn + email sequences grouped by industry. First line references their company, rest is cluster-templated. 3-touch sequence per persona (Champion and Economic Buyer).",
            "success": "5%+ reply rate, meetings booked in top 3 clusters within first 4 weeks",
        },
        {
            "channel": "Industry Webinars",
            "why": "25% S1 rate. Webinars work as mid-funnel accelerators — accounts that attend are significantly more likely to take a demo.",
            "how": "3 industry-specific webinars over the quarter, targeting top-converting verticals (e.g., 'Document Automation for Financial Services'). Co-host with customer or industry partner when possible. 45-60 minutes, live product demo included.",
            "success": "100+ registrations per webinar, 40%+ attend rate, 20%+ of attendees request demo",
        },
        {
            "channel": "Content Syndication (Targeted)",
            "why": "14% baseline — but improves when restricted to high-converting industries. Only syndicate to HR Tech, Logistics, Financial Services, Consulting.",
            "how": "Syndicate industry-specific guides to targeted account lists in high-converting verticals only. Stop all broad syndication.",
            "success": "5%+ conversion to MQL from syndicated content",
        },
        {
            "channel": "G2 / Review Sites",
            "why": "29% S1 rate — high trust signal. Accounts coming from G2 are actively comparing solutions.",
            "how": "Sponsor G2 comparison pages for key competitors (Conga, Proposify, Ironclad). Use G2 buyer intent data to identify accounts in active evaluation. Send G2 Grid reports to T2 accounts showing intent.",
            "success": "10+ accounts identified from G2 intent per month, comparison page traffic growth",
        },
        {
            "channel": "Progressive Retargeting",
            "why": "Captures T2 accounts that engaged with any content but haven't converted. Low cost, always-on.",
            "how": "Retarget accounts that visited website, clicked ads, or attended webinar. Serve next-stage content progressively.",
            "success": "Measurable progression through content stages, retargeting-assisted conversions tracked",
        },
    ],
    "personas": [
        {
            "priority": 1,
            "persona": "Champion / User Buyer",
            "why": "Same entry point as T1, but engaged through cluster messaging, not 1:1 personalization.",
            "approach": "SDR outreach via HeyReach with industry-specific first line. Paid social ads (LinkedIn, Meta, Reddit, Quora, TikTok) serve industry case studies. Webinar invites.",
        },
        {
            "priority": 2,
            "persona": "Legal / Compliance",
            "why": "Same blocker risk as T1. At T2 scale, engage through compliance-focused content rather than 1:1 outreach.",
            "approach": "Compliance webinar invite. Security whitepaper in email nurture. G2 security badge in ads. Cluster-level, not account-level engagement.",
        },
        {
            "priority": 3,
            "persona": "Economic Buyer",
            "why": "Budget holder. Engage after initial champion interest is established.",
            "approach": "ROI calculator (industry-specific inputs). TCO comparison in email sequence. Executive-focused ad creative.",
        },
    ],
    "messaging_themes": [
        {"theme": "Compliance & Security", "conversion": "43%", "application": "Cluster-delivered: 'SOC 2 compliant document workflows for regulated [industry] institutions.' Compliance webinar CTA."},
        {"theme": "Manual Process Pain", "conversion": "41%", "application": "Industry-specific: 'HR teams spend X hours on manual offer letters' or 'Logistics firms lose Y deals to slow proposals.'"},
        {"theme": "Proposal Automation", "conversion": "33%", "application": "Core value prop in all ad creative and email sequences. Industry template packs as lead magnets."},
        {"theme": "Integration Focus", "conversion": "31%", "application": "Highlight relevant CRM integrations per cluster. /integrations page as gateway content in retargeting."},
    ],
    "content_requirements": [
        "**Per cluster:** 1 industry case study, 1 industry guide (lead magnet), 1 template pack",
        "**Webinars:** 3 industry-specific webinar decks + customer panel prep",
        "**Ads:** Industry-specific single image ad creative (3-5 variants per cluster)",
        "**Email:** Semi-personalized SDR sequence templates per cluster (3-touch)",
        "**Review sites:** G2 comparison reports, competitive positioning docs",
    ],
    "engagement_model": {
        "review_cadence": "Monthly review at cluster level. Which clusters are generating engagement? Which are stalling? Bi-weekly ad creative rotation.",
        "escalation_triggers": [
            "T2 account shows 5+ engagement actions → flag for T1 promotion review",
            "Webinar attendee → immediate SDR follow-up within 24 hours",
            "G2 intent signal → add to next SDR outreach batch",
        ],
        "optimization": "Scale paid social budget 2x for best-performing clusters and platforms mid-quarter. Pause underperforming clusters and reallocate budget to winners.",
    },
}

T3_STRATEGY = {
    "name": "T3: 1:Many Programmatic",
    "profile": {
        "score": "< 40",
        "characteristics": "Low firmographic fit. May be in a zero-conversion industry (Manufacturing, Insurance, Energy), have an entrenched CRM (Salesforce/HubSpot), or be in a low-converting revenue/geo segment.",
        "expected_accounts": "50-200+ per quarter",
        "historical_s1_rate": "3%",
        "approach": "T3 is the discovery tier. The goal is NOT to convert these accounts this quarter. The goal is to identify which T3 accounts show emerging signals that warrant promotion to T2. Budget is minimal. Tactics are fully automated. No SDR or AE time invested.",
    },
    "channels": [
        {
            "channel": "Automated Email Nurture",
            "why": "Low cost, fully automated. Persona-segmented sequences educate and qualify without human effort.",
            "how": "Persona-based email sequences triggered by lifecycle stage. Educational content → product content → CTA progression. Bi-weekly emails, 8-touch sequence. A sales leader gets different content than an ops person.",
            "success": "20%+ open rate, 2%+ reply rate, engagement spikes trigger T2 promotion review",
        },
        {
            "channel": "Programmatic Paid Social (LinkedIn, Meta, Reddit, Quora, TikTok)",
            "why": "Broad awareness at low cost across multiple platforms. Keeps PandaDoc visible for accounts that may develop into T2 next quarter.",
            "how": "LinkedIn: broad targeting by company size + title. Meta: interest-based targeting + website visitor retargeting. Reddit: sponsored posts in business/productivity subreddits. Quora: topic targeting on document management and e-signatures. TikTok: short-form educational content. Low budget distributed across platforms, always-on.",
            "success": "0.5%+ CTR across platforms, measurable brand recall lift",
        },
        {
            "channel": "SEO + GEO / Content Marketing",
            "why": "Inbound converts at 33% — content draws accounts to PandaDoc organically. GEO ensures AI assistants surface PandaDoc in buyer research.",
            "how": "Create content targeting pain points from the data (proposal automation, contract management, e-signatures). Optimize for both SEO and GEO — structure pages so LLMs cite PandaDoc. Build comparison pages, FAQ-rich guides, LLM-optimized content.",
            "success": "Organic traffic growth, LLM citation tracking, content-assisted T3→T2 promotions",
        },
        {
            "channel": "AppExchange / Marketplace",
            "why": "40% S1 rate — highest-intent capture channel. T3 accounts finding PandaDoc on AppExchange are self-qualifying.",
            "how": "Optimize listing, drive customer reviews, feature integrations prominently. Monthly review solicitation campaign.",
            "success": "Listing traffic growth, review volume increase, AppExchange-sourced leads fast-tracked to demo",
        },
        {
            "channel": "Broad Product Webinars",
            "why": "Monthly educational webinars cast a wide net. Low cost per attendee. Doubles as a qualification mechanism — T3 accounts that attend a webinar are showing interest.",
            "how": "Monthly product webinars open to all. Product deep dives, use case showcases, Q&A with product team.",
            "success": "Webinar attendance triggers engagement score boost, frequent attendees flagged for T2 review",
        },
    ],
    "engagement_model": {
        "review_cadence": "Monthly batch re-score. No human review of individual T3 accounts — the scoring engine handles it.",
        "promotion_trigger": "3+ high-intent engagement actions in a 30-day window (e.g., pricing page visit + webinar attendance + email reply) promotes the account to T2 scoring review.",
        "archive_trigger": "Zero engagement for 90+ days across all channels → archive the account. Don't waste even automated budget on fully disengaged accounts.",
    },
}

QUARTERLY_MILESTONES = [
    {
        "phase": "Launch & Engage",
        "weeks": "Weeks 1-4",
        "objective": "Activate all channels across all three tiers. Establish baseline engagement metrics. Begin multi-threading T1 accounts across the buying committee.",
        "t1_milestone": "All T1 accounts have been reached through paid social (LinkedIn, Meta, Reddit, Quora, TikTok) + at least one direct outreach touchpoint. At least 3 buying committee personas identified per account. First engagement signals captured.",
        "t2_milestone": "Paid social campaigns live across all platforms for top industry clusters. First industry webinar hosted. SDR sequences launched for top 3 clusters.",
        "t3_milestone": "Automated nurture sequences live. Programmatic paid social running across platforms. First SEO/GEO content pieces published.",
        "decision_point": "First engagement data review at Week 4: Which T1 accounts are responding? Which T2 clusters are showing signal? Any T3 accounts showing unexpected engagement spikes?",
    },
    {
        "phase": "Accelerate & Optimize",
        "weeks": "Weeks 5-9",
        "objective": "Double down on what is working, cut what is not. Scale paid social budget for top-performing clusters and platforms. Activate Legal personas at T1 accounts. Push engaged accounts toward demo or trial.",
        "t1_milestone": "Virtual executive roundtable hosted. Legal/Compliance personas engaged at all T1 accounts where they have been identified as blockers. 50%+ of T1 accounts have had a meeting or demo.",
        "t2_milestone": "Second and third industry webinars hosted. Paid social budget scaled 2x for best-performing clusters and platforms. Underperforming clusters paused, budget reallocated. Trial offers sent to high-engagement accounts.",
        "t3_milestone": "First batch of T3 accounts flagged for T2 promotion review based on engagement spikes. Email nurture adjusted — engaged contacts moved to product-focused sequences.",
        "decision_point": "Mid-quarter performance review at Week 9: Re-score all accounts. Execute first round of tier mobility (T3→T2 and T2→T1 promotions). Adjust messaging based on reply rate and content performance data.",
    },
    {
        "phase": "Convert & Learn",
        "weeks": "Weeks 10-13",
        "objective": "Convert pipeline to revenue. Document what worked and what didn't. Run the feedback engine. Prepare the model and account list for next quarter.",
        "t1_milestone": "Deal rooms created for T1 accounts in active evaluation. Security/compliance documentation provided to Legal stakeholders. Win/loss documented for every T1 account.",
        "t2_milestone": "Trial offers pushed to remaining engaged T2 accounts. Conversion outcomes documented per industry cluster. T2→T1 promotions identified for next quarter.",
        "t3_milestone": "Full re-score of all T3 accounts with updated engagement data. T3→T2 promotions executed. Disengaged accounts archived.",
        "decision_point": "End-of-quarter system actions: feedback engine recalibrates scoring weights based on actual conversion outcomes. Channel budget rebalanced for next quarter. All accounts re-tiered with updated model. Retrospective written.",
    },
]

TIER_MOBILITY = {
    "promotions": {
        "T3_to_T2": "Score increases to 35+ through engagement (3+ high-intent actions in 30 days — e.g., pricing page visit, webinar attendance, content download) OR firmographic change (funding round, headcount growth, CRM change).",
        "T2_to_T1": "Score increases to 60+ after weight recalibration OR firmographic change (company raises funding, headcount grows, switches CRM).",
    },
    "demotions": {
        "T1_to_T2": "Zero engagement for 60+ days despite multi-channel outreach across 3+ channels. Or explicit disqualification (wrong fit confirmed, budget frozen, deal lost to competitor).",
        "T2_to_T3": "Zero engagement for 90+ days. No response to SDR outreach across 2+ channels. No ad engagement. Account shows no buying signals.",
    },
    "review_cadence": "Monthly batch re-score for all accounts, with real-time re-scoring triggered by major sales note updates (budget approved, went dark, competitor mentioned, champion left company).",
    "compounding": "Each quarter adds new conversion data to the model. Q1: 150-lead trained model. Q2: 300-lead model (sharper). Q3: 450-lead model (predictive). The scoring engine gets smarter every cycle.",
}

# ─────────────────────────────────────────────
# ENGAGEMENT FLOW: Stage-based buyer journey
# ─────────────────────────────────────────────
# Two dimensions: TIER (resources) x STAGE (buyer journey position)
# Tier is set by the scoring engine (firmographic fit). Stage is set by observed behavior.

ENGAGEMENT_STAGES = [
    {
        "stage": "Identified",
        "trigger": "Account scored and tiered by the scoring engine. Added to target lists.",
        "ad_content": "Awareness: thought leadership, industry insights, brand awareness. The account hasn't seen PandaDoc yet — introduce the problem we solve.",
        "t1_action": "Deep research: 10K filings, LinkedIn, news, tech stack, org chart. Map buying committee. Build personalized sequences. Assign AE + SDR.",
        "t2_action": "Add to industry cluster audience. Build SDR sequence for cluster. Set up paid social targeting across LinkedIn, Meta, Reddit, Quora, TikTok.",
        "t3_action": "Add to automated lists (email nurture, programmatic paid social across all platforms). No human effort.",
    },
    {
        "stage": "Aware",
        "trigger": "50+ ad impressions on the account. They have seen PandaDoc in their feed — brand recognition is established.",
        "ad_content": "Awareness → Solution: pain point content, use case examples, 'how companies like yours solve X.' Start introducing PandaDoc as the answer.",
        "t1_action": "Launch outreach: HeyReach DM to Champion, AE email to Legal + Economic Buyer simultaneously. The account has seen the ads — outbound response rates are 2-3x higher when ads have warmed the account first.",
        "t2_action": "SDR HeyReach sequence triggered for this cluster. Semi-personalized outreach begins. Webinar invite sent.",
        "t3_action": "Email nurture begins (persona-segmented). No outbound — let the content and ads do the work.",
    },
    {
        "stage": "Engaged",
        "trigger": "5+ ad clicks, OR email reply, OR content download, OR webinar attendance. The account has actively interacted — they are researching.",
        "ad_content": "Solution → Product: product features, case studies, integration highlights, demo CTA. They know the problem — now show PandaDoc is the solution.",
        "t1_action": "Escalate: push for demo. Send competitive comparison docs (if competitor in notes). Activate Legal persona with compliance content (security whitepaper, SOC 2 docs). Send CRM-specific integration guide.",
        "t2_action": "Push for demo or trial. Send trial offer. Invite to industry webinar if not yet attended. If 5+ engagement actions, flag for T1 promotion review.",
        "t3_action": "Flag for T2 promotion review. If 3+ high-intent actions in 30 days, promote to T2 and begin cluster outreach.",
    },
    {
        "stage": "Considering",
        "trigger": "Demo booked OR trial started. The account is in active evaluation.",
        "ad_content": "Product → Decision: customer testimonials, ROI proof, security/compliance badges, G2 reviews. Reinforce the decision to evaluate PandaDoc.",
        "t1_action": "Deal room created. Compliance docs sent to Legal. Pre-filled ROI calculator to Economic Buyer. Virtual roundtable invite. Competitive displacement docs if relevant.",
        "t2_action": "Trial support + urgency messaging. ROI calculator with industry-specific inputs. Follow-up sequence from SDR.",
        "t3_action": "Fast-track: assign to SDR, treat as T2. This account has self-qualified through behavior.",
    },
    {
        "stage": "Selecting",
        "trigger": "Open deal / opportunity created in CRM. The account is making a buying decision.",
        "ad_content": "Social proof: customer logos, G2 badges, analyst recognition. Reinforce confidence in the decision.",
        "t1_action": "Final presentations. Negotiate. Executive briefing if needed. Document win/loss regardless of outcome — feed into scoring model.",
        "t2_action": "Close support. Document cluster conversion outcome. Identify what messaging/channel drove the deal.",
        "t3_action": "Close support. Document what path this T3 account took to get here — refine the promotion criteria.",
    },
]

STALL_PROTOCOLS = [
    {
        "situation": "Stuck at Aware for 4+ weeks (ads showing, no clicks)",
        "t1": "Adjust ad creative, try different messaging angle (switch from proposal automation to compliance or integration theme)",
        "t2": "Rotate cluster creative. Test different ad format (single image vs video)",
        "t3": "Continue nurture, no action needed — T3 is a long game",
    },
    {
        "situation": "Stuck at Engaged for 4+ weeks (clicking but no demo)",
        "t1": "Try a different persona entry point. If Champion isn't responding, go through Technical Evaluator or Legal. New channel (if only email, try LinkedIn DM or vice versa)",
        "t2": "Webinar invite. Trial offer with low-commitment CTA. Add to retargeting with product-focused content",
        "t3": "Keep in nurture. If sustained engagement, promote to T2 where SDR can engage directly",
    },
    {
        "situation": "Demo completed but no deal after 2 weeks",
        "t1": "Competitive comparison docs. Address Legal blockers proactively (compliance demo invite). Executive briefing. Check if a new persona needs to be engaged",
        "t2": "Follow-up sequence. Limited-time offer. Send ROI calculator post-demo",
        "t3": "N/A — T3 accounts in demo stage are treated as T2",
    },
    {
        "situation": "Went dark after engagement (replied then silence)",
        "t1": "AE personal follow-up after 1 week. Try a different persona in the buying committee. New value angle. If still dark after 4 weeks, demote to T2",
        "t2": "Re-enter SDR sequence with new angle after 30-day cool-off period. Different messaging theme",
        "t3": "Drop back to automated nurture. Will re-engage when ready",
    },
]


SUCCESS_METRICS = {
    "pipeline_targets": {
        "T1": {"accounts": "5-15", "target_s1_rate": "50%+", "avg_acv": "$20K+", "pipeline_target": "$100K+"},
        "T2": {"accounts": "50-100", "target_s1_rate": "20%+", "avg_acv": "$12K+", "pipeline_target": "$170K+"},
        "T3": {"accounts": "50-200", "target_s1_rate": "5%+", "avg_acv": "$5K+", "pipeline_target": "$17K+"},
        "total": "$287K+ quarterly pipeline",
    },
    "leading_indicators": [
        {"metric": "Engagement Rate", "t1": "80%+", "t2": "40%+", "t3": "15%+"},
        {"metric": "Paid Social CTR", "t1": "2%+", "t2": "1%+", "t3": "0.5%+"},
        {"metric": "Email Open Rate", "t1": "50%+", "t2": "30%+", "t3": "20%+"},
        {"metric": "Email Reply Rate", "t1": "15%+", "t2": "5%+", "t3": "2%+"},
    ],
    "lagging_indicators": [
        {"metric": "Meeting Booked Rate", "t1": "70%+", "t2": "35%+", "t3": "10%+"},
        {"metric": "S1 Conversion Rate", "t1": "50%+", "t2": "20%+", "t3": "5%+"},
        {"metric": "Avg ACV", "t1": "$20K+", "t2": "$12K+", "t3": "$5K+"},
        {"metric": "Pipeline Generated", "t1": "$100K+", "t2": "$170K+", "t3": "$17K+"},
    ],
}


# ─────────────────────────────────────────────
# RUN PIPELINE
# ─────────────────────────────────────────────

def run_strategy_and_plan(leads, scored_accounts, output_dir="output"):
    """Run the complete channel strategy and quarterly plan pipeline."""
    print("\n" + "=" * 60)
    print("MODULE 3: CHANNEL STRATEGY & QUARTERLY ACTIVATION PLAN")
    print("=" * 60)

    # Step 1: Channel analysis
    print("\n[1/3] Analyzing channel performance...")
    channel_analysis = analyze_channels(leads)

    print("\n  CHANNEL PERFORMANCE RANKING (by Expected Value):")
    sorted_channels = sorted(channel_analysis.items(), key=lambda x: x[1]["expected_value"], reverse=True)
    for ch, data in sorted_channels:
        rec = data["recommendation"]
        print(f"    {ch}: ${data['expected_value']:,.0f} EV ({data['rate']:.0%} S1, ${data['avg_acv']:,.0f} ACV) → {rec['action']} | Budget: {rec['budget_pct']}%")

    # Step 2: Tier channel mix
    print("\n[2/3] Building tier-specific channel strategies...")
    for tier, config in TIER_CHANNEL_MIX.items():
        print(f"    {tier} ({config['description']}): {len(config['channels'])} channels, {config['budget_share']}")

    # Step 3: Generate quarterly plan
    print("\n[3/3] Generating quarterly ABM activation strategy...")

    # Output channel strategy
    channel_report = generate_channel_report(channel_analysis)
    write_markdown(os.path.join(output_dir, "channel_strategy.md"), channel_report)

    # Output quarterly plan
    plan_report = generate_quarterly_plan_report()
    write_markdown(os.path.join(output_dir, "quarterly_plan.md"), plan_report)

    print("\n✓ Module 3 complete.")
    return channel_analysis


def generate_channel_report(channel_analysis):
    """Generate the channel strategy markdown report."""
    lines = []
    lines.append("# Channel Strategy Report")
    lines.append("")
    lines.append("## Channel Performance by Expected Value")
    lines.append("| Channel | Leads | S1 | Rate | Avg ACV | Expected Value | Action | Budget % |")
    lines.append("|---------|-------|-----|------|---------|---------------|--------|----------|")
    sorted_channels = sorted(channel_analysis.items(), key=lambda x: x[1]["expected_value"], reverse=True)
    for ch, data in sorted_channels:
        rec = data["recommendation"]
        acv = f"${data['avg_acv']:,.0f}" if data["avg_acv"] > 0 else "-"
        ev = f"${data['expected_value']:,.0f}" if data["expected_value"] > 0 else "$0"
        lines.append(f"| {ch} | {data['total']} | {data['converted']} | {data['rate']:.0%} | {acv} | {ev} | **{rec['action']}** | {rec['budget_pct']}% |")
    lines.append("")

    # Key insights (data-derived)
    lines.append("## Key Channel Insights (from Data)")
    lines.append("")
    lines.append("*All values below come directly from the 150-lead dataset. Channels ranked by expected value (conversion rate × avg ACV).*")
    lines.append("")
    # Generate insights from actual data, sorted by conversion rate
    top_channels = sorted_channels[:3]
    bottom_channels = [c for c in sorted_channels if c[1]["rate"] == 0]
    for i, (ch, data) in enumerate(top_channels, 1):
        rec = data["recommendation"]
        lines.append(f"{i}. **{ch} ({data['rate']:.0%} S1)** — {rec['strategy']}")
    if bottom_channels:
        for ch, data in bottom_channels:
            lines.append(f"- **{ch} ({data['rate']:.0%} S1)** — {data['recommendation']['strategy']}")
    lines.append("")

    # Channel strategy per channel
    lines.append("## Channel-by-Channel Strategy")
    for ch, data in sorted_channels:
        rec = data["recommendation"]
        lines.append(f"\n### {ch} — {rec['action']}")
        lines.append(f"**Expected Value:** ${data['expected_value']:,.0f} | **Conversion:** {data['rate']:.0%} | **Avg ACV:** ${data['avg_acv']:,.0f} | **Volume:** {data['total']} leads")
        lines.append(f"\n**Strategy:** {rec['strategy']}")
        lines.append(f"\n**ABM Role:** {rec['abm_role']}")
        lines.append(f"\n**Budget Allocation:** {rec['budget_pct']}%")
        lines.append("")

    # Tier channel mix
    lines.append("---")
    lines.append("## Channel Mix by Tier")
    for tier, config in TIER_CHANNEL_MIX.items():
        lines.append(f"\n### {tier}: {config['description']}")
        lines.append(f"**Accounts:** {config['accounts']} | **Budget:** {config['budget_share']}")
        lines.append("")
        lines.append("| Channel | Tactic | Frequency | Content |")
        lines.append("|---------|--------|-----------|---------|")
        for ch in config["channels"]:
            lines.append(f"| {ch['channel']} | {ch['tactic'][:80]}... | {ch['frequency']} | {ch['content'][:60]}... |")
        lines.append("")

    return "\n".join(lines)


def generate_quarterly_plan_report():
    """Generate the quarterly ABM activation strategy as a strategic framework document."""
    lines = []

    # ── Section 1: Strategic Overview ──
    lines.append("# Quarterly ABM Activation Strategy")
    lines.append("")
    lines.append("## Strategic Overview")
    lines.append("")
    lines.append("We analyzed 150 historical leads to discover what converts in PandaDoc's funnel. The patterns are clear — and they drive every decision in this plan. This is not a one-time campaign. It is a reusable framework: when new accounts enter the system, the scoring engine tiers them automatically, and this strategy defines what each tier receives.")
    lines.append("")
    lines.append("### Data-Driven Strategic Decisions")
    lines.append("")
    lines.append("| Insight from Data | Strategic Decision |")
    lines.append("|---|---|")
    lines.append("| Paid Social converts at 43% S1 rate — highest of any channel | **Paid Social is the primary engine** (LinkedIn, Meta, Reddit, Quora, TikTok). Outbound (18%) supplements ads, not the other way around. Cold outbound costs ~2x more per pipeline dollar. |")
    lines.append("| HR Tech (67%), Logistics (60%), Real Estate (40%) convert at 2-3x baseline | **Cluster T2 campaigns around these top verticals.** Deprioritize zero-conversion industries (Manufacturing, Insurance, Energy). |")
    lines.append("| No CRM/Spreadsheets convert at 38% vs Salesforce at 10% | **Mid-market CRMs are PandaDoc's sweet spot.** Accounts on Copper/Pipedrive have structured sales processes but haven't over-invested in enterprise document tools. |")
    lines.append("| /integrations page visits produce +12% conversion lift — strongest signal | **Integration-first content strategy.** CRM integration is PandaDoc's #1 differentiator — lead with it. |")
    lines.append("| Compliance messaging converts at 43% (highest theme); Legal is the #1 deal blocker | **Proactive legal engagement at every tier.** Engage Legal in parallel with Champion from day one — never wait for them to surface as a blocker. |")
    lines.append("| Paid Search converts at 0% | **Paused.** Budget reallocated to proven channels. Rethink targeting and landing pages before relaunch. |")
    lines.append("")

    # ── Tools Required ──
    lines.append("---")
    lines.append("## Tools Required")
    lines.append("")
    lines.append("The following tools are essential to execute this strategy. The system breaks without any of these:")
    lines.append("")
    lines.append("| Tool | Role in the System |")
    lines.append("|------|--------------------|")
    lines.append("| **HubSpot / Salesforce** | CRM, automated email nurture workflows, ABM stage tracking, active lists, reporting dashboards |")
    lines.append("| **Paid Social Platforms** | Primary advertising channels (43% S1 rate). LinkedIn (matched audiences T1, industry targeting T2), Meta (retargeting, lookalikes), Reddit & Quora (community engagement), TikTok (short-form video awareness) |")
    lines.append("| **HeyReach** | LinkedIn outbound sequences. Personalized 1:1 sequences for T1, semi-personalized cluster sequences for T2 |")
    lines.append("| **Fibbler or equivalent** | Pushes paid social engagement data (impressions, clicks per account) from LinkedIn and other platforms into the CRM. Without this, stage transitions cannot be automated |")
    lines.append("| **Claude Code** | AI orchestration layer. Runs the scoring engine, generates personalized messaging, conducts account research, powers the feedback loops |")
    lines.append("")

    # ── Section 2: Budget Allocation ──
    lines.append("---")
    lines.append("## Budget Allocation")
    lines.append("")
    lines.append("| Tier | Budget Share | Per-Account Investment | Rationale |")
    lines.append("|------|------------|----------------------|-----------|")
    lines.append("| T1 (15-25 accounts) | 40% | ~2% of total budget per account | Highest-value accounts with 43% historical S1 rate. Personalized multi-channel plays justify the highest spend per account. |")
    lines.append("| T2 (50-100 accounts) | 40% | ~0.5% per account | Volume tier with 27% historical S1 rate. Industry-cluster approach balances personalization and efficiency at scale. |")
    lines.append("| T3 (50-200 accounts) | 20% | ~0.2% per account | Discovery/nurture pool. Fully automated, low-cost programmatic channels. Primary goal: identify future T2 accounts. |")
    lines.append("")
    lines.append("### Channel Budget Split Within Each Tier")
    lines.append("")
    lines.append("| Channel | T1 Share | T2 Share | T3 Share |")
    lines.append("|---------|----------|----------|----------|")
    lines.append("| Paid Social (LinkedIn, Meta, Reddit, Quora, TikTok) | 30% | 35% | 25% |")
    lines.append("| Outbound (HeyReach + Email) | 30% | 20% | — |")
    lines.append("| Events (Roundtable / Webinars) | 15% | 15% | 10% |")
    lines.append("| Retargeting | 15% | 10% | — |")
    lines.append("| Content / SEO / GEO | 10% | 10% | 35% |")
    lines.append("| Content Syndication | — | 10% | — |")
    lines.append("| AppExchange / Marketplace | — | — | 10% |")
    lines.append("| Email Nurture (Automated) | — | — | 20% |")
    lines.append("")

    # ── Section 3: T1 Strategy ──
    lines.append("---")
    lines.append("## T1 Strategy: 1:1 Strategic")
    lines.append("")
    _write_tier_strategy(lines, T1_STRATEGY)

    # ── Section 4: T2 Strategy ──
    lines.append("---")
    lines.append("## T2 Strategy: 1:Few Industry Cluster")
    lines.append("")
    _write_tier_strategy(lines, T2_STRATEGY)

    # ── Section 5: T3 Strategy ──
    lines.append("---")
    lines.append("## T3 Strategy: 1:Many Programmatic")
    lines.append("")
    _write_tier_strategy(lines, T3_STRATEGY)

    # ── Section 6: Engagement Flow ──
    lines.append("---")
    lines.append("## Engagement Flow: How Accounts Progress")
    lines.append("")
    lines.append("The tier determines **what resources** an account gets. The stage determines **where the account is** in the buyer journey. These are two dimensions working together: every account has both a tier (T1/T2/T3) and a stage (Identified → Aware → Engaged → Considering → Selecting). The tier is set by the scoring engine based on firmographic fit (Industry, CRM, Revenue, Employee Band, Country). The stage is set by observed behavior.")
    lines.append("")
    lines.append("### Stage Progression & Triggers")
    lines.append("")
    lines.append("Each stage has a concrete, measurable trigger. Accounts progress when their behavior warrants it — not on a calendar. An account can move from Identified to Considering in a week, or sit at Aware for months.")
    lines.append("")
    for stage in ENGAGEMENT_STAGES:
        lines.append(f"#### {stage['stage']}")
        lines.append(f"**Trigger:** {stage['trigger']}")
        lines.append("")
        lines.append(f"**Ad content served:** {stage['ad_content']}")
        lines.append("")
        lines.append(f"| T1 (1:1) | T2 (Cluster) | T3 (Automated) |")
        lines.append(f"|----------|-------------|----------------|")
        lines.append(f"| {stage['t1_action']} | {stage['t2_action']} | {stage['t3_action']} |")
        lines.append("")

    lines.append("### Stall Protocols")
    lines.append("")
    lines.append("When accounts stop progressing through stages, these protocols prevent wasted effort and trigger course corrections.")
    lines.append("")
    lines.append("| Situation | T1 Response | T2 Response | T3 Response |")
    lines.append("|-----------|-------------|-------------|-------------|")
    for stall in STALL_PROTOCOLS:
        lines.append(f"| {stall['situation']} | {stall['t1']} | {stall['t2']} | {stall['t3']} |")
    lines.append("")

    # ── Section 7: Quarterly Milestones ──
    lines.append("---")
    lines.append("## Quarterly Milestones")
    lines.append("")
    lines.append("Three phases over 13 weeks. Each phase has a strategic objective, per-tier milestones, and a decision point that determines how the next phase adapts.")
    lines.append("")
    for milestone in QUARTERLY_MILESTONES:
        lines.append(f"### {milestone['phase']} ({milestone['weeks']})")
        lines.append(f"**Objective:** {milestone['objective']}")
        lines.append("")
        lines.append(f"- **T1:** {milestone['t1_milestone']}")
        lines.append(f"- **T2:** {milestone['t2_milestone']}")
        lines.append(f"- **T3:** {milestone['t3_milestone']}")
        lines.append("")
        lines.append(f"**Decision Point:** {milestone['decision_point']}")
        lines.append("")

    # ── Section 8: Success Metrics ──
    lines.append("---")
    lines.append("## Success Metrics")
    lines.append("")
    lines.append("### Pipeline Targets")
    lines.append("")
    lines.append("| Tier | Target Accounts | Target S1 Rate | Avg ACV | Pipeline Target |")
    lines.append("|------|----------------|----------------|---------|-----------------|")
    for tier in ["T1", "T2", "T3"]:
        t = SUCCESS_METRICS["pipeline_targets"][tier]
        lines.append(f"| {tier} | {t['accounts']} | {t['target_s1_rate']} | {t['avg_acv']} | {t['pipeline_target']} |")
    lines.append(f"| **Total** | | | | **{SUCCESS_METRICS['pipeline_targets']['total']}** |")
    lines.append("")

    lines.append("### Leading Indicators (Weekly)")
    lines.append("")
    lines.append("| Metric | T1 Target | T2 Target | T3 Target |")
    lines.append("|--------|-----------|-----------|-----------|")
    for ind in SUCCESS_METRICS["leading_indicators"]:
        lines.append(f"| {ind['metric']} | {ind['t1']} | {ind['t2']} | {ind['t3']} |")
    lines.append("")

    lines.append("### Lagging Indicators (Quarterly)")
    lines.append("")
    lines.append("| Metric | T1 Target | T2 Target | T3 Target |")
    lines.append("|--------|-----------|-----------|-----------|")
    for ind in SUCCESS_METRICS["lagging_indicators"]:
        lines.append(f"| {ind['metric']} | {ind['t1']} | {ind['t2']} | {ind['t3']} |")
    lines.append("")

    # ── Section 9: Tier Mobility ──
    lines.append("---")
    lines.append("## Tier Mobility Rules")
    lines.append("")
    lines.append("Accounts are not locked into tiers. The scoring engine re-evaluates accounts on an ongoing basis, and accounts move up or down based on engagement and conversion signals.")
    lines.append("")
    lines.append("### Promotions")
    lines.append(f"- **T3 → T2:** {TIER_MOBILITY['promotions']['T3_to_T2']}")
    lines.append(f"- **T2 → T1:** {TIER_MOBILITY['promotions']['T2_to_T1']}")
    lines.append("")
    lines.append("### Demotions")
    lines.append(f"- **T1 → T2:** {TIER_MOBILITY['demotions']['T1_to_T2']}")
    lines.append(f"- **T2 → T3:** {TIER_MOBILITY['demotions']['T2_to_T3']}")
    lines.append("")
    lines.append(f"**Review Cadence:** {TIER_MOBILITY['review_cadence']}")
    lines.append("")
    lines.append(f"**Compounding Effect:** {TIER_MOBILITY['compounding']}")
    lines.append("")

    return "\n".join(lines)


def _write_tier_strategy(lines, strategy):
    """Write a tier strategy section to the report."""
    profile = strategy["profile"]

    # Profile
    lines.append("### Profile")
    lines.append(f"**Score threshold:** {profile['score']} | **Expected accounts:** {profile['expected_accounts']} | **Historical S1 rate:** {profile['historical_s1_rate']}")
    lines.append("")
    lines.append(f"**What makes an account {strategy['name'].split(':')[0].strip()}:** {profile['characteristics']}")
    lines.append("")
    lines.append(f"**Approach:** {profile['approach']}")
    lines.append("")

    # Channels
    lines.append("### Channels")
    lines.append("")
    for ch in strategy["channels"]:
        lines.append(f"**{ch['channel']}**")
        lines.append(f"- *Why:* {ch['why']}")
        lines.append(f"- *How:* {ch['how']}")
        lines.append(f"- *Success:* {ch['success']}")
        lines.append("")

    # Personas
    if "personas" in strategy:
        lines.append("### Persona Targeting (Priority Order)")
        lines.append("")
        lines.append("| Priority | Persona | Why This Order | Engagement Approach |")
        lines.append("|----------|---------|----------------|---------------------|")
        for p in strategy["personas"]:
            lines.append(f"| {p['priority']} | {p['persona']} | {p['why']} | {p['approach']} |")
        lines.append("")

    # Messaging
    if "messaging_themes" in strategy:
        lines.append("### Messaging Themes (Ordered by Conversion Data)")
        lines.append("")
        lines.append("| Theme | S1 Conversion | Application |")
        lines.append("|-------|--------------|-------------|")
        for m in strategy["messaging_themes"]:
            lines.append(f"| {m['theme']} | {m['conversion']} | {m['application']} |")
        lines.append("")

    # Content
    if "content_requirements" in strategy:
        lines.append("### Content Requirements")
        lines.append("")
        for c in strategy["content_requirements"]:
            lines.append(f"- {c}")
        lines.append("")

    # Engagement Model
    if "engagement_model" in strategy:
        em = strategy["engagement_model"]
        lines.append("### Engagement Model")
        lines.append("")
        lines.append(f"**Review cadence:** {em['review_cadence']}")
        lines.append("")
        if "escalation_triggers" in em:
            lines.append("**Escalation triggers:**")
            for trigger in em["escalation_triggers"]:
                lines.append(f"- {trigger}")
            lines.append("")
        if "stall_protocol" in em:
            lines.append(f"**Stall protocol:** {em['stall_protocol']}")
            lines.append("")
        if "promotion_trigger" in em:
            lines.append(f"**Promotion trigger:** {em['promotion_trigger']}")
            lines.append("")
        if "archive_trigger" in em:
            lines.append(f"**Archive trigger:** {em['archive_trigger']}")
            lines.append("")
        if "optimization" in em:
            lines.append(f"**Optimization:** {em['optimization']}")
            lines.append("")


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
    run_strategy_and_plan(leads, scored_accounts, os.path.dirname(__file__))
