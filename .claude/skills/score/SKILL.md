---
name: score
description: Score a CSV of contacts/accounts using the trained ABM model. Use when someone has a list of prospects and wants to launch an ABM campaign. Outputs an enriched CSV with scores, tiers, personas, messaging angles, and recommended channels.
argument-hint: <path-to-contacts.csv>
allowed-tools: Bash, Read, Write
---

# Score New Accounts

Score a list of contacts using the trained ABM model and output an enriched CSV ready for campaign activation.

## What You Need

A CSV file with contact/account data. The CSV should have columns for: Company, Industry, First Name, Last Name, Title, Revenue Range, Employee Band, Country, Current CRM. Engagement History and Sales Notes are optional but improve messaging recommendations.

## Steps

1. **Run score mode:**

```bash
cd "/Users/alicedoglioli/Desktop/ABM STRATEGY"
python3 orchestrator.py --score $ARGUMENTS
```

2. **Read the output** at `enriched_accounts.csv` and summarize the results for the user:
   - How many accounts landed in each tier (T1, T2, T3)
   - Highlight the top T1 accounts (these get 1:1 strategic plays)
   - Note any interesting patterns (e.g., most accounts in a specific industry)

3. **Explain what the columns mean:**
   - **Score / Tier**: Firmographic fit score (0-100) and resulting tier
   - **Persona**: Which buying committee role this contact maps to
   - **Missing Personas**: Which roles are missing for multi-threading
   - **Messaging Angle**: Recommended messaging theme based on signals
   - **Recommended Content**: What to send this persona
   - **Recommended Channels**: Best channels to reach them

4. **Remind the user** that:
   - The enriched CSV can be imported into their CRM or used to build campaign lists
   - T1 accounts should get personalized 1:1 outreach
   - T2 accounts work best in industry-cluster campaigns
   - T3 accounts go into programmatic nurture flows

## If No CSV Path Is Provided

Ask the user for the path to their contacts CSV. Remind them it needs at minimum: Company, Industry, Title, Revenue Range, Employee Band, Country, and Current CRM columns.

## If No Trained Model Exists

If scoring fails because `01_account_tiering/scoring_weights.json` doesn't exist, tell the user they need to run train mode first:
```
python3 orchestrator.py
```
