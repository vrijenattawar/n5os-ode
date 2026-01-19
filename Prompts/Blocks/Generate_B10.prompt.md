---
description: Generate B10 Relationship Trajectory block with progression tracking
tags:
  - meeting-intelligence
  - block-generation
  - b10
  - relationship
  - trajectory
  - trust
  - semantic-memory
version: 1.0
tool: true
created: 2026-01-03
---
# Generate Block B10: Relationship Trajectory

Track relationship progression, trust evolution, and engagement depth across meetings.

## Purpose

Enables long-term relationship management by tracking how relationships evolve over time. This block provides the longitudinal view that B08 (single-meeting snapshot) cannot.

## Trigger Conditions

Generate B10 for:
- **Every external meeting** (helps with relationship management across multiple touches)
- Particularly valuable for recurring contacts

---

## Semantic Memory Context (Load First)

**CRITICAL:** This block REQUIRES historical context to be meaningful:

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()

# 1. Load ALL prior meetings with this stakeholder
all_meetings = client.search_profile(
    profile="meetings",
    query=f"{stakeholder_name}",
    limit=20  # Get full history
)

# 2. Load CRM profile for relationship metadata
crm = client.search_profile(
    profile="crm",
    query=f"{stakeholder_name} {organization}",
    limit=1
)

# 3. Load prior B10 blocks for trajectory comparison
prior_b10s = client.search(
    query=f"{stakeholder_name} relationship trajectory",
    metadata_filters={"path": ("contains", "B10")},
    limit=5
)

# 4. Load prior B08 resonance data
prior_b08s = client.search(
    query=f"{stakeholder_name} resonated",
    metadata_filters={"path": ("contains", "B08")},
    limit=5
)
```

**Use this context to:**
- Count total meetings and calculate frequency
- Track relationship stage progression
- Detect trust signal evolution
- Identify consistent resonance patterns vs. emerging concerns

---

## Input

- **Meeting Transcript:** `{{transcript}}`
- **Meeting Metadata:** `{{metadata}}`
- **Enrichment Context:** `{{enrichment_context}}` (from Step 2b)
- **Prior B08s:** `{{prior_b08s}}` (for resonance history)

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B10
semantic_enrichment: true
---

# B10: Relationship Trajectory

## Relationship Summary

| Field | Value |
|-------|-------|
| **Stakeholder** | [Name] |
| **Organization** | [Company] |
| **Category** | [New Contact / Warm Lead / Active Opportunity / Strategic Partner / Champion / Dormant] |
| **Meeting Count** | [This is meeting #N] |
| **Relationship Age** | [X months since first contact] |
| **Last Contact** | [Date of previous meeting] |

---

## Section 1: Relationship Status ⭐ MEMORY-ENRICHED

### History Overview
- **First Contact:** [Date of first meeting]
- **Total Meetings:** [N] meetings over [X] months
- **Meeting Frequency:** [Weekly / Bi-weekly / Monthly / Sporadic]
- **Communication Pattern:** [Meetings / Async / Mixed]

### Meeting Timeline
| Date | Type | Key Outcome | Sentiment |
|------|------|-------------|-----------|
| [Date N] | [This meeting] | [Outcome] | [Score/10] |
| [Date N-1] | [Prior] | [Outcome] | [Score/10] |
| [Date N-2] | [Prior] | [Outcome] | [Score/10] |

---

## Section 2: Trust & Engagement Signals

### Trust Indicators (This Meeting)

| Signal | Evidence | Score |
|--------|----------|-------|
| **Specificity** | [Vague ↔ Detailed discussion] | [1-5] |
| **Sharing** | [Guarded ↔ Open with info/challenges] | [1-5] |
| **Transparency** | [Corporate speak ↔ Candid] | [1-5] |
| **Reciprocity** | [Taking ↔ Offering help/intros] | [1-5] |
| **Vulnerability** | [Defensive ↔ Admits gaps/asks for help] | [1-5] |

**Trust Score:** [X]/25 → [Low / Medium / High]

### Trust Evolution ⭐ MEMORY-ENRICHED
- **Prior Trust Score:** [X]/25 (from last B10)
- **Change:** [+N / -N / Stable]
- **Trend:** [Building / Stable / Eroding]
- **Evidence:** [What specifically improved or declined]

### Engagement Sentiment
- **Enthusiasm Level:** [High / Medium / Low]
  - Evidence: [Specific signals]
- **Urgency Signals:** [Timeline compression, proactive follow-ups, or none]
- **Commitment Signals:** [Resource allocation, calendar priority, or none]
- **Investment in Relationship:** [Time spent, preparation shown]

---

## Section 3: Relationship Stage Assessment

### Current Stage
```
[Discovery] → [Education] → [Exploration] → [Negotiation] → [Partnership] → [Maintenance]
                                    ↑
                              CURRENT STAGE
```

**Stage:** [Discovery / Education / Exploration / Negotiation / Partnership / Maintenance / Dormant]

**Stage Definition:**
- **Discovery:** Learning about each other
- **Education:** Understanding fit and value
- **Exploration:** Actively discussing collaboration
- **Negotiation:** Working out terms
- **Partnership:** Active collaboration
- **Maintenance:** Ongoing relationship management
- **Dormant:** No recent activity

### Stage Transition ⭐ MEMORY-ENRICHED
- **Previous Stage:** [Stage from last meeting]
- **Transition:** [Progressing / Stable / Stalling / Declining]
- **Time in Current Stage:** [N meetings / X weeks]

### Progression Signals
- **Moving Forward:** [Evidence of advancement]
- **Stall Risks:** [What could cause stagnation]
- **Blockers:** [Current obstacles to progression]

---

## Section 4: Collaboration Style

### Working Preferences (Observed)
| Dimension | Assessment | Evidence |
|-----------|------------|----------|
| **Working Style** | [Independent / Collaborative / Consensus-seeker] | [How they make decisions] |
| **Decision Type** | [Data-driven / Values-driven / Relationship-driven] | [What they prioritize] |
| **Communication** | [Async / Meetings / Quick calls / Detailed docs] | [Preferred mode] |
| **Pace** | [Fast-moving / Deliberate / Slow] | [How quickly they act] |

### Values Alignment
- **Where we align:** [Shared values, priorities]
- **Where we diverge:** [Differences in approach]
- **Potential friction points:** [Areas to navigate carefully]

---

## Section 5: Cross-Meeting Patterns ⭐ MEMORY-ENRICHED

### Consistent Resonance
Topics that consistently generate enthusiasm across meetings:
- [Topic 1] - resonated in [N] of [M] meetings
- [Topic 2] - resonated in [N] of [M] meetings

### Recurring Concerns
Issues that keep coming up:
- [Concern 1] - raised in [N] meetings
- [Concern 2] - raised in [N] meetings

### Communication Insights
What works best with this stakeholder:
- [Communication pattern that works]
- [What to avoid]

---

## Section 6: Recommended Follow-Up

### Next Touch
| Field | Recommendation |
|-------|----------------|
| **Timing** | [N] days until next contact |
| **Contact Type** | [Email / Call / Coffee / Meeting / Async] |
| **Primary Purpose** | [Continue discussion / Send resources / Seek intro / etc.] |
| **Key Topics** | [What to discuss next time] |

### Relationship Investment
- **Priority Level:** [High priority / Standard / Low maintenance]
- **Rationale:** [Why this level of investment]

### Suggested Actions
- [ ] [Specific action 1]
- [ ] [Specific action 2]
- [ ] [Specific action 3]

---

## Section 7: First Contact Baseline (if applicable)

**If this is the first meeting:**

```markdown
## First Contact - Baseline Established

This is the first recorded meeting with [Name].

**Initial Impressions:**
- [Key observations about working style]
- [Initial trust signals]
- [Potential for relationship development]

**Baseline Metrics:**
- Trust Score: [X]/25 (baseline)
- Engagement: [High/Medium/Low]
- Stage: Discovery

**Watch for in Future Meetings:**
- [What to track as relationship develops]
```

---
**Feedback**: - [ ] Useful
---
```

## Quality Requirements

- **MUST use memory context** - this block is meaningless without historical comparison
- **Count meetings accurately** from search results
- **Track stage progression** across meetings
- **Identify patterns** that span multiple conversations
- **Provide actionable follow-up** recommendations

## Anti-patterns

- ❌ Generating B10 without loading meeting history
- ❌ Treating as first contact when prior meetings exist
- ❌ Missing trust score comparison to baseline
- ❌ Generic follow-up recommendations
- ❌ No stage transition assessment

## Special Handling

**First Contact:** If no prior meetings found, explicitly note "First Contact - Baseline Established" and set baseline metrics for future comparison.

Generate B10 now with comprehensive relationship trajectory analysis.
