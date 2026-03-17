# Research Notes — PandaDoc & ABM Best Practices

## PandaDoc Key Facts
- Founded 2011, $1B valuation (Series C, 2021), $100M+ ARR, 60K+ customers
- Sweet spot: SMB/mid-market, 50-1000 employees, $10M-$100M revenue
- 91% of customers <1000 employees, 76% <$50M revenue
- Pricing: Free eSign, Essentials $19/mo, Business $49/mo, Enterprise custom
- Median ACV: ~$16,447/year
- Core differentiator: ONLY all-in-one platform (create + sign + pay + CRM + analytics)
- Primary buyers: VP/Director of Sales, Sales Ops/RevOps
- Top integrations: Salesforce (AppExchange), HubSpot (deepest, native CPQ), Pipedrive

## Competitors
- DocuSign: Pure e-sign, PandaDoc wins on breadth
- Proposify: Proposal-only, PandaDoc wins on all-in-one
- Conga: Enterprise CLM, wins upmarket — PandaDoc wins mid-market
- Ironclad: Legal-focused, expensive — PandaDoc is sales-focused
- Qwilr: Better visual proposals — PandaDoc wins on functionality
- Loopio: RFP-only, different use case
- Adobe Sign: PDF ecosystem — PandaDoc wins on CRM integration

## ABM Best Practices
*Sources: Oracle ABM Guide, Growth Unhinged "A Very Tactical Guide to ABM" (Emilia Korczynska, VP Marketing @ Userpilot, Feb 2025)*

### What ABM Actually Is (Oracle)
- ABM is a focused strategic approach that brings sales and marketing together. It's about the **right leads, not more leads**
- Marketing resources are dedicated to a specific set of target accounts and the contacts within them — highly targeted, personalized content and messaging
- ABM requires marketing and sales to be aligned from day one. Both teams must work toward the same goal with clearly defined roles
- 60% of companies using ABM for 1+ year attribute revenue increase to its use (Demand Metric)
- 70% of ABM users report sales/marketing mostly or completely aligned, vs 51% for non-ABM users

### What Makes a Good ABM Account (Oracle)
- Must have **revenue potential** that justifies the higher cost of ABM campaigns
- Past purchase history and any relationship with you or competitors
- Position within the sales funnel
- Alignment to Ideal Customer Profile
- Can help meet strategic goals (logo acquisition, geographic/industry expansion, re-engagement)

### ABM Benefits (Oracle)
1. **Marketing + sales alignment** — forced by the approach. Shared data-driven decisions throughout the cycle
2. **Higher ROI** — more precise, targeted, personalized. Fewer opt-outs, higher response rates. Highest ROI among B2B marketing tactics
3. **Shorter sales cycles** — unqualified prospects eliminated early. Focus on accounts most likely to convert

### ABM KPIs to Track (Oracle)
- Marketing qualified leads / marketing qualified accounts
- Cost per lead
- Time on page (digital asset engagement)
- Email open rate / reply rate
- Number of additional contacts per account (multi-threading depth)
- Engagement rate by account
- Pipeline velocity
- In-funnel conversion rate
- Number of sales meetings per account
- Number of proposals sent
- Close rate / churn rate
- Average selling price

### Oracle's 6-Step ABM Framework
1. Define goals, timeline, budget, and KPIs across marketing and sales
2. Select targeted accounts — ensure right data, right channels, right insights
3. Expand footprint within accounts — identify key stakeholders, create stakeholder-specific content
4. Provide timely and personalized messaging to the right influencers
5. Measure efforts — leverage insights for cross-sell and up-sell
6. Review campaign metrics, make adjustments, optimize

### Content Marketing + ABM (Oracle)
- Content plays a huge role — everything is highly personalized
- May need to create industry-specific content that doesn't exist for generic inbound campaigns
- Content must be managed consistently across marketing and sales — CX must be consistent within the sales cycle
- Content goals for ABM should be concrete: pipeline velocity, lead generation, revenue — not soft metrics like shares or followers

### Sales-Marketing Alignment Roles (Oracle)
**Marketing focuses on:**
- Developing high-quality content, managing it so sales can access needed pieces
- Educating the sales team on how the campaign works
- Using reliable lead scoring, sending high-quality leads to sales in a timely fashion

**Sales focuses on:**
- Working on leads from marketing in a timely fashion
- Communicating customer objections or messaging gaps to marketing
- Being transparent about why and how deals are won and lost

---

### Userpilot Case Study: ABM from Zero to $655K Pipeline in 90 Days

**Context:** Userpilot (product adoption platform, similar ACV range to PandaDoc) went from 100% inbound/SEO to launching ABM from scratch. Generated $655K pipeline in 90 days at **$12 pipeline per $1 spent**.

### Their 5-Stage ABM Funnel
| Stage | Trigger | What Happens |
|-------|---------|-------------|
| Identified | Account added to target list | Ads begin — awareness content |
| Aware | 50+ ad impressions | Brand recognition established |
| Interested/Engaged | 5+ ad clicks OR 10+ engagements | Active interest confirmed — personalized BDR outreach begins |
| Considering | Demo booked or trial started | In active evaluation |
| Selecting | Open deal created | Making buying decision |

**Key insight:** Accounts at each stage see **different ad content** — the further down the funnel, the more product-oriented the creative.

### Their Tech Stack (~$2,500/month total)
| Tool | Function |
|------|----------|
| HubSpot | CRM, workflows, ABM stage tracking, active lists, reporting |
| LinkedIn Campaign Manager | Only ad channel (so far) |
| Fibbler | Pushes quantitative LinkedIn data (impressions, clicks per account) to HubSpot |
| ZenABM | Pushes qualitative data (which campaigns account engaged with) to HubSpot |
| Clay + BuiltWith | Technographic targeting + account enrichment |
| Apollo | Contact list building for matched audiences |
| SalesLoft | BDR sequencing / outreach |
| Notion | Campaign asset management |

### How They Connect LinkedIn → CRM (critical architecture)
1. HubSpot active lists → synced to LinkedIn Campaign Manager as ad audiences (~48h sync time)
2. LinkedIn serves ads to those audiences
3. Fibbler pushes engagement data (impressions, clicks per account) back to HubSpot company properties
4. ZenABM pushes campaign-specific data (which content the account engaged with) to HubSpot
5. HubSpot workflows auto-update "ABM Stage" company property based on threshold rules
6. Updated stage → account moves to new active list → synced back to LinkedIn → different ads served
7. When BDRs create leads, company intent tags auto-copy to lead level via workflow

### Campaign Structure Lessons
- **Initially structured by persona** (PM, UI/UX, PMM, CXO) → caused massive campaign sprawl + hit LinkedIn API limitations
- **Restructured around shared intent** — much more manageable and scalable
- LinkedIn obfuscates engagement data if fewer than 3 members from an account engage
- Need minimum 300 contacts for persona-targeted audiences at later stages
- **Website visitor deanonymization was too unreliable** — abandoned in favor of LinkedIn engagement data

### Ad Performance Benchmarks
| Format | CTR | CPC | Notes |
|--------|-----|-----|-------|
| Single image | 0.35% | $19 | **Best performer** |
| Video | 0.28% | $24 | Good but more expensive |
| Thought Leader Ads | 4.42% | $68 | Misleading — LinkedIn counts "see more" as clicks |
| DM ads | — | Very high | Extremely expensive per conversion |
| Text ads | Negligible | Negligible | High impressions, no clicks |

### List Building Criteria (their example)
**Firmographic:** 50-2,000 employees, $5M+ revenue, digital-first industries (SaaS, eCommerce, EdTech, FinTech, HealthTech), PLG model, USA/Canada/Western Europe

**Technographic (via BuiltWith):** Currently or previously using a competitor, using redundant tool combinations, using a direct competitor lacking a specific feature

**CRM mining:** Right-sized accounts previously lost to competitors due to missing features

### Key Takeaways for Our Strategy
1. **Don't start without Marketing Ops** — the RevOps setup work is "brutal"
2. **Simplify scoring** — quantitative engagement data first, qualitative later
3. **Cold outbound took 2x longer and cost 51% more** for the same pipeline vs LinkedIn ads
4. **Campaign sprawl from over-personalization** hits LinkedIn API limits — structure by intent, not persona
5. **$52K total spend → $655K pipeline in 90 days** — 12.55x return. Proves ABM works at mid-market ACV
6. **LinkedIn Campaign Manager is the only ad channel they use** — no Google, no Meta. LinkedIn is enough for B2B ABM
