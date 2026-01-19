---
description: Generate B31 Stakeholder Research block with semantic memory and credibility weighting
tags:
  - meeting-intelligence
  - block-generation
  - b31
  - stakeholder-research
  - semantic-memory
  - insights
version: 1.0
tool: true
created: 2026-01-03
---
# Generate Block B31: Stakeholder Research

Extract essential landscape insights from this stakeholder's perspective with signal strength ratings and credibility weighting.

## Purpose

This is **intelligence gathering** - what did we learn about the WORLD from this conversation? Not just about the person, but about their industry, market, and domain.

## Semantic Memory Context (Load First)

**CRITICAL:** Load stakeholder's domain credibility before weighting insights:

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()

# 1. Check for prior B08 with domain authority section
prior_b08 = client.search_profile(
    profile="meetings",
    query=f"{stakeholder_name} B08 domain authority",
    limit=3
)

# 2. Load CRM profile for background context
crm_profile = client.search_profile(
    profile="crm",
    query=f"{stakeholder_name} {organization}",
    limit=1
)

# 3. Search for prior B31 insights from this stakeholder
prior_insights = client.search(
    query=f"{stakeholder_name} insight",
    metadata_filters={"path": ("contains", "B31")},
    limit=10
)
```

**Use this context to:**
- Check domain authority before assigning credibility scores
- Avoid duplicate insights already captured
- Track insight validation status over time
- Build cumulative source credibility

---

## Input

- **Meeting Transcript:** `{{transcript}}`
- **B08 Block:** `{{b08_content}}` (for domain authority reference)
- **Enrichment Context:** `{{enrichment_context}}` (from Step 2b)

---

## What to Extract

Extract insights when stakeholder speaks:
- **For their ORGANIZATION:** strategy, priorities, internal challenges, decision-making
- **For their INDUSTRY:** trends, competitive dynamics, emerging patterns, market shifts
- **As a STAKEHOLDER TYPE:** decision criteria, common objections, buying patterns

**Focus on NON-OBVIOUS information:**
- Things you couldn't get from Google
- Inside perspective on how decisions are made
- Unwritten rules or hidden dynamics
- Emerging trends not yet widely known

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B31
semantic_enrichment: true
---

# B31: Stakeholder Research

**Perspective:** Speaking as [career tech founder / early-stage investor / HR executive / etc.]

## Insight 1: [Clear, descriptive title - as many words as needed]

**Evidence:** "[Direct quote from transcript]"

**Why it matters:** [ONE SENTENCE combining implication + strategic value]

**Signal Strength:** ● ● ● ○ ○ (3/5)
- Rating rationale: [Why this rating]

**Category:** [Hiring Manager Pain Points / Product Strategy / Market Dynamics / etc.]

**Source Credibility:**
- **Stakeholder:** [Name] → See B08 Domain Authority
- **Relevant experience:** [Specific background that makes them knowledgeable on THIS topic]
- **Source type:** [PRIMARY / SECONDARY / SPECULATIVE]
  - PRIMARY = Firsthand operational experience on this exact topic
  - SECONDARY = Informed perspective but not direct experience
  - SPECULATIVE = Intelligent hypothesis but no direct evidence
- **Weight justification:** [Why we should/shouldn't weight this heavily]

---

## Insight 2: [Title]
...

## Insight 3: [Title]
...

---

## Signal Strength Legend

| Rating | Meaning |
|--------|---------|
| ● ○ ○ ○ ○ | Generic/obvious, heard before, not actionable |
| ● ● ○ ○ ○ | Somewhat specific, might be actionable |
| ● ● ● ○ ○ | Specific, actionable, not obvious |
| ● ● ● ● ○ | Highly specific, actionable, surprising, verified by 1-2 others |
| ● ● ● ● ● | Game-changing, highly actionable, surprising, verified by 3+ |

## Category Tags

Stakeholder-Specific:
- Hiring Manager Pain Points
- Community Owner Pain Points
- Job Seeker Pain Points
- Investor Pain Points
- Founder Pain Points

General:
- Product Strategy
- GTM & Distribution
- Market Dynamics & Competition
- Fundraising & Business Model

---

## Action: Update B08 Domain Authority

After generating B31, update B08's Domain Authority section:
- Add new domains if first insight on a topic
- Increment insight count for existing domains
- Note B31 reference in track record

---
**Feedback**: - [ ] Useful
---
```

## Requirements

- **3-5 insights MAX** per meeting (quality over quantity)
- **Evidence required** - direct quote for each insight
- **Credibility weighting** - use B08 domain authority or assess here
- **Category tagging** - enables aggregation across meetings
- **Signal strength rating** - be honest, most insights are 2-3 dots

## Anti-patterns

- ❌ Generic insights that could come from Google
- ❌ More than 5 insights (dilutes signal)
- ❌ Missing evidence quotes
- ❌ All insights rated 4-5 dots (inflation)
- ❌ Ignoring stakeholder's domain limitations

## Trigger Conditions

Generate B31 for:
- **STANDARD meetings:** IF non-obvious insights present
- **DEEP meetings:** ALWAYS

Skip B31 for:
- **BRIEF meetings:** Unless exceptionally high-signal
- Meetings with no landscape/industry discussion

Generate B31 now with insight extraction and credibility weighting.
