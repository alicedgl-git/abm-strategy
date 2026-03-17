"""
Shared utilities for the PandaDoc ABM Engine.
Handles data loading, normalization, and common helpers.
"""

import csv
import os
import json
from collections import Counter, defaultdict

# Column mapping for the funnel leads CSV
COLUMNS = [
    "date", "channel", "first_name", "last_name", "title", "email", "phone",
    "country", "company", "industry", "employee_count", "employee_band",
    "revenue_range", "account_owner", "current_crm", "engagement_history",
    "lifecycle_stage", "mql", "meeting_booked", "meeting_held", "s1",
    "opportunity_acv", "sales_notes"
]

# High-intent engagement actions (derived from conversion analysis)
HIGH_INTENT_ACTIONS = [
    "Visited /integrations page",
    "Opened 3+ emails",
    "Downloaded contract template",
    "Downloaded ROI guide",
    "Visited pricing page",
    "Requested a demo",
]

# All trackable engagement actions
ALL_ENGAGEMENT_ACTIONS = [
    "Visited pricing page",
    "Downloaded contract template",
    "Clicked LinkedIn ad",
    "Opened 3+ emails",
    "Attended webinar",
    "Downloaded ROI guide",
    "Requested a demo",
    "Started free trial",
    "Visited /integrations page",
    "Visited competitor comparison page",
    "Watched demo video",
    "Reviewed G2 listing",
]

# Qualitative signals to extract from sales notes
POSITIVE_SIGNALS = {
    "budget_approved": ["budget approved", "budget pre-approved"],
    "competitor_evaluation": ["conga", "ironclad", "adobe sign", "proposify", "loopio", "qwilr", "docusign"],
    "urgency": ["urgency", "fiscal year-end", "30 days", "next month", "q1 rollout", "next week", "end of quarter"],
    "familiar_with_pandadoc": ["familiar with pandadoc", "used it at a previous"],
    "manual_process_pain": ["google docs", "manually", "word docs", "email"],
    "multi_stakeholder": ["multi-stakeholder"],
    "high_proposal_volume": ["proposal volume", "proposals/month", "40 proposals"],
    "contract_pain": ["contract error", "version control", "audit trail", "version locking"],
}


def load_leads(filepath):
    """Load and normalize lead data from CSV."""
    leads = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row 1 (category headers)
        next(reader)  # Skip header row 2 (column names)
        for row in reader:
            if len(row) < len(COLUMNS):
                row.extend([""] * (len(COLUMNS) - len(row)))
            lead = dict(zip(COLUMNS, row))
            # Normalize numeric fields
            lead["mql"] = int(lead["mql"]) if lead["mql"] else 0
            lead["meeting_booked"] = int(lead["meeting_booked"]) if lead["meeting_booked"] else 0
            lead["meeting_held"] = int(lead["meeting_held"]) if lead["meeting_held"] else 0
            lead["s1"] = int(lead["s1"]) if lead["s1"] else 0
            lead["opportunity_acv"] = parse_acv(lead["opportunity_acv"])
            lead["employee_count"] = parse_int(lead["employee_count"])
            lead["engagement_actions"] = parse_engagement(lead["engagement_history"])
            lead["qualitative_signals"] = extract_qualitative_signals(lead["sales_notes"])
            leads.append(lead)
    return leads


def parse_acv(acv_str):
    """Parse ACV string like '$54,800' to float."""
    if not acv_str:
        return 0.0
    return float(acv_str.replace("$", "").replace(",", "").strip() or "0")


def parse_int(s):
    """Parse integer from string, handling commas."""
    if not s:
        return 0
    return int(s.replace(",", "").strip() or "0")


def parse_engagement(engagement_str):
    """Parse engagement history string into list of actions."""
    if not engagement_str:
        return []
    return [action.strip() for action in engagement_str.split(";") if action.strip()]


def extract_qualitative_signals(notes):
    """Extract qualitative intent signals from sales notes."""
    if not notes:
        return {}
    notes_lower = notes.lower()
    signals = {}
    for signal_name, keywords in POSITIVE_SIGNALS.items():
        signals[signal_name] = any(kw in notes_lower for kw in keywords)
    return signals


def get_conversion_rates(leads, group_field):
    """Calculate S1 conversion rate by a given field."""
    totals = Counter()
    conversions = Counter()
    for lead in leads:
        value = lead[group_field]
        totals[value] += 1
        if lead["s1"] == 1:
            conversions[value] += 1
    rates = {}
    for value in totals:
        rates[value] = {
            "total": totals[value],
            "converted": conversions[value],
            "rate": conversions[value] / totals[value] if totals[value] > 0 else 0,
        }
    return rates


def get_expected_values(leads, group_field):
    """Calculate expected value (conversion_rate × avg_ACV) by a given field."""
    from collections import defaultdict
    totals = Counter()
    conversions = Counter()
    acv_sums = defaultdict(float)
    acv_counts = defaultdict(int)
    for lead in leads:
        value = lead[group_field]
        totals[value] += 1
        if lead["s1"] == 1:
            conversions[value] += 1
            if lead["opportunity_acv"] > 0:
                acv_sums[value] += lead["opportunity_acv"]
                acv_counts[value] += 1
    results = {}
    for value in totals:
        rate = conversions[value] / totals[value] if totals[value] > 0 else 0
        avg_acv = acv_sums[value] / acv_counts[value] if acv_counts[value] > 0 else 0
        results[value] = {
            "total": totals[value],
            "converted": conversions[value],
            "rate": rate,
            "avg_acv": avg_acv,
            "expected_value": rate * avg_acv,
        }
    return results


def get_engagement_lift(leads):
    """Calculate conversion lift for each engagement action."""
    s1_leads = [l for l in leads if l["s1"] == 1]
    non_s1 = [l for l in leads if l["s1"] == 0]
    lifts = {}
    for action in ALL_ENGAGEMENT_ACTIONS:
        s1_rate = sum(1 for l in s1_leads if action in l["engagement_actions"]) / len(s1_leads) if s1_leads else 0
        non_rate = sum(1 for l in non_s1 if action in l["engagement_actions"]) / len(non_s1) if non_s1 else 0
        lifts[action] = {
            "s1_pct": s1_rate,
            "non_s1_pct": non_rate,
            "lift": s1_rate - non_rate,
        }
    return lifts


def write_markdown(filepath, content):
    """Write content to a markdown file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"  -> Written: {filepath}")


def write_csv_output(filepath, headers, rows):
    """Write rows to a CSV file."""
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> Written: {filepath}")


def save_weights(weights, filepath):
    """Save scoring weights to JSON for reuse on new accounts."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(weights, f, indent=2)
    print(f"  -> Weights saved: {filepath}")


def load_weights(filepath):
    """Load previously trained scoring weights from JSON."""
    with open(filepath, "r") as f:
        return json.load(f)


# Column name mapping — maps common CRM export variants to our internal names
COLUMN_ALIASES = {
    "company": ["company", "company name", "account", "account name", "organization"],
    "industry": ["industry", "sector", "vertical"],
    "first_name": ["first name", "first_name", "firstname"],
    "last_name": ["last name", "last_name", "lastname"],
    "title": ["title", "job title", "job_title", "role", "position"],
    "email": ["email", "email address", "e-mail"],
    "phone": ["phone", "phone number", "telephone"],
    "country": ["country", "location", "region"],
    "employee_count": ["employee count", "employee_count", "employees", "company size", "headcount"],
    "employee_band": ["employee band", "employee_band", "size band", "company size band"],
    "revenue_range": ["revenue range", "revenue_range", "annual revenue", "annual revenue range", "revenue"],
    "current_crm": ["current crm", "current_crm", "crm", "crm system"],
    "channel": ["channel", "source", "lead source", "acquisition channel"],
    "engagement_history": ["engagement history", "engagement_history", "engagement", "engagement actions"],
    "lifecycle_stage": ["lifecycle stage", "lifecycle_stage", "hubspot lifecycle stage", "stage"],
    "sales_notes": ["sales notes", "sales_notes", "notes", "comments"],
    "account_owner": ["account owner", "account_owner", "owner", "rep"],
    "date": ["date", "member first responded date", "created date", "created_date"],
    "mql": ["mql"],
    "meeting_booked": ["meeting booked", "meeting_booked", "initial meeting booked"],
    "meeting_held": ["meeting held", "meeting_held", "initial meeting held"],
    "s1": ["s1", "opportunity", "converted"],
    "opportunity_acv": ["opportunity acv", "opportunity_acv", "acv", "opportunity acv ($)", "deal value"],
}


def _map_column_name(header):
    """Map a CSV column header to our internal field name."""
    header_lower = header.lower().strip()
    for internal_name, aliases in COLUMN_ALIASES.items():
        if header_lower in aliases:
            return internal_name
    return None


def load_new_accounts(filepath):
    """
    Load new accounts from a standard single-header CSV (CRM export format).
    Maps column names flexibly and defaults missing fields gracefully.
    """
    leads = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        raw_headers = next(reader)

        # Map headers to internal names
        column_map = {}
        for i, header in enumerate(raw_headers):
            internal = _map_column_name(header)
            if internal:
                column_map[i] = internal

        if "company" not in column_map.values():
            raise ValueError(f"CSV must have a Company column. Found headers: {raw_headers}")

        for row in reader:
            if not any(cell.strip() for cell in row):
                continue  # Skip empty rows

            lead = {col: "" for col in COLUMNS}  # Default all fields to empty
            for i, internal_name in column_map.items():
                if i < len(row):
                    lead[internal_name] = row[i].strip()

            # Normalize numeric fields (default to 0 for new accounts)
            lead["mql"] = int(lead["mql"]) if lead["mql"] else 0
            lead["meeting_booked"] = int(lead["meeting_booked"]) if lead["meeting_booked"] else 0
            lead["meeting_held"] = int(lead["meeting_held"]) if lead["meeting_held"] else 0
            lead["s1"] = int(lead["s1"]) if lead["s1"] else 0
            lead["opportunity_acv"] = parse_acv(lead["opportunity_acv"])
            lead["employee_count"] = parse_int(lead["employee_count"])
            lead["engagement_actions"] = parse_engagement(lead["engagement_history"])
            lead["qualitative_signals"] = extract_qualitative_signals(lead["sales_notes"])

            leads.append(lead)

    return leads
