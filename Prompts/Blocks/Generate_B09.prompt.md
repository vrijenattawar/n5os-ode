---
description: Generate B09 Collaboration Terms block with deal and partnership tracking
tags:
  - meeting-intelligence
  - block-generation
  - b09
  - collaboration
  - partnership
  - terms
  - deals
  - semantic-memory
version: 1.1
tool: true
created: 2026-01-03
---
# Generate Block B09: Collaboration Terms

Structured capture of partnership terms, collaboration frameworks, commercial agreements, and deal progression.

## Purpose

Track all collaboration and partnership terms discussed - including but not limited to financial terms. This enables deal tracking across meetings for partnerships, joint ventures, integrations, and commercial relationships.

## Trigger Conditions

Generate B09 if ANY of these apply:
- Partnership or collaboration terms discussed
- Pricing or payment terms mentioned
- Revenue models or economics explored
- Scope of work or deliverables defined
- Roles and responsibilities allocated
- Timeline or milestone commitments made
- Investment or funding terms raised
- Contract or agreement terms negotiated
- Pilot or trial parameters defined

**Skip B09 if:** Pure networking/informational meeting with no collaboration discussion.

---

## Semantic Memory Context (Load First)

**CRITICAL:** Load prior collaboration discussions with this stakeholder:

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()

# 1. Check for prior B09 blocks with this stakeholder
prior_terms = client.search(
    query=f"{stakeholder_name} {organization} partnership collaboration terms",
    metadata_filters={"path": ("contains", "B09")},
    limit=5
)

# 2. Load CRM profile for deal stage context
crm = client.search_profile(
    profile="crm",
    query=f"{stakeholder_name} {organization}",
    limit=1
)

# 3. Search for prior negotiation context
prior_negotiations = client.search_profile(
    profile="meetings",
    query=f"{stakeholder_name} partnership terms scope",
    limit=5
)
```

**Use this context to:**
- Track term evolution across meetings
- Detect deal progression or regression
- Compare current terms to prior discussions
- Identify changes in scope or structure

---

## Input

- **Meeting Transcript:** `{{transcript}}`
- **Meeting Metadata:** `{{metadata}}`
- **Enrichment Context:** `{{enrichment_context}}` (from Step 2b)

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B09
semantic_enrichment: true
---

# B09: Collaboration Terms

## Collaboration Summary

| Field | Value |
|-------|-------|
| **Partner** | [Name / Organization] |
| **Collaboration Type** | [Partnership / Integration / Joint Venture / Customer / Investment / Pilot] |
| **Stage** | [Exploratory / Scoping / Proposal / Negotiating / Agreed / Active] |
| **Confidence** | [Firm / Tentative / Exploratory] |

---

## Section 1: Collaboration Framework

### Structure
- **Type:** [Co-development / Reseller / Integration / White-label / Revenue share / Service / Investment]
- **Duration:** [One-time / Fixed term / Ongoing / TBD]
- **Exclusivity:** [Exclusive / Non-exclusive / Territory-specific / TBD]

### Scope Definition
| Element | Description | Status |
|---------|-------------|--------|
| **What we provide** | [Our contribution] | [Agreed / Proposed / TBD] |
| **What they provide** | [Their contribution] | [Agreed / Proposed / TBD] |
| **Joint deliverables** | [What we build/do together] | [Agreed / Proposed / TBD] |

### Roles & Responsibilities
| Party | Responsibility | Notes |
|-------|---------------|-------|
| **Us** | [What we own] | [Context] |
| **Them** | [What they own] | [Context] |
| **Shared** | [Joint responsibilities] | [How decided] |

---

## Section 2: Commercial Terms (if applicable)

### Financial Model
- **Model Type:** [CPC / CPA / Revenue Share / Subscription / Flat Fee / Hybrid / Investment / None defined]
- **Pricing Confidence:** [Firm / Proposed / Exploratory / TBD]

### Pricing Details
| Element | Value | Confidence | Notes |
|---------|-------|------------|-------|
| **Rate/Amount** | [specific pricing] | [Firm/Proposed/TBD] | [context] |
| **Unit** | [per click/action/month/user] | - | - |
| **Volume** | [quantity or scale] | [Estimated/Committed] | [assumptions] |

### Payment Terms
| Term | Value |
|------|-------|
| **Frequency** | [Monthly / Quarterly / Annual / Milestone-based / N/A] |
| **Method** | [Wire / Card / ACH / Invoice / N/A] |
| **Special Terms** | [Discounts, bonuses, conditions] |

---

## Section 3: Timeline & Milestones

### Key Dates
| Milestone | Target Date | Status | Dependencies |
|-----------|-------------|--------|--------------|
| [Milestone 1] | [Date] | [Firm/Tentative/TBD] | [What's needed] |
| [Milestone 2] | [Date] | [Firm/Tentative/TBD] | [What's needed] |

### Phase Plan (if discussed)
| Phase | Scope | Duration | Success Criteria |
|-------|-------|----------|------------------|
| Phase 1 | [What] | [How long] | [How measured] |
| Phase 2 | [What] | [How long] | [How measured] |

---

## Section 4: Success Metrics & KPIs

### Defined Success Criteria
| Metric | Target | Measurement | Owner |
|--------|--------|-------------|-------|
| [Metric 1] | [Target value] | [How measured] | [Who tracks] |
| [Metric 2] | [Target value] | [How measured] | [Who tracks] |

### Review Cadence
- **Check-in frequency:** [Weekly / Monthly / Quarterly / TBD]
- **Review format:** [Call / Report / Dashboard / TBD]
- **Decision points:** [When to evaluate continuation/expansion]

---

## Section 5: Deal Status ⭐ MEMORY-ENRICHED

### Current State
- **Stage:** [Exploratory / Scoping / Proposal / Negotiating / Agreed / Active]
- **Last Action:** [What happened in this meeting]
- **Next Step:** [Immediate next action]
- **Decision Timeline:** [When decision expected]
- **Decision Maker:** [Who has final approval]

### Open Items
| Item | Category | Owner | Needed By | Status |
|------|----------|-------|-----------|--------|
| [Open item 1] | [Scope/Terms/Technical] | [Who] | [Date] | [Open/Resolved] |
| [Open item 2] | [Scope/Terms/Technical] | [Who] | [Date] | [Open/Resolved] |

### Evolution from Prior Discussions ⭐
- **Previous stage:** [Where we were]
- **What changed:** [Key developments]
- **Direction:** [Advancing / Stable / Stalling / Regressing]
- **Blockers resolved:** [What got unstuck]
- **New blockers:** [What emerged]

---

## Section 6: Commitments & Dependencies

### Commitments Made
| Commitment | By Whom | To Whom | By When |
|------------|---------|---------|---------|
| [Commitment 1] | [Party] | [Party] | [Date] |
| [Commitment 2] | [Party] | [Party] | [Date] |

### Dependencies
- **Blocking us:** [What we need from them]
- **Blocking them:** [What they need from us]
- **External:** [Third-party dependencies]

---

## Section 7: Risk Assessment

### Collaboration Risks
| Risk | Category | Probability | Impact | Mitigation |
|------|----------|-------------|--------|------------|
| [Risk 1] | [Scope/Timeline/Resource/Commitment] | [H/M/L] | [H/M/L] | [Action] |
| [Risk 2] | [Scope/Timeline/Resource/Commitment] | [H/M/L] | [H/M/L] | [Action] |

### Red Flags (if any)
- [Any concerning signals about collaboration viability]

### Assumptions
- [Key assumptions underlying this collaboration]

---

## Cross-References

- **B06 (Pilot Intelligence):** [If pilot discussed, link here]
- **B12 (Technical Infrastructure):** [Link to technical requirements]
- **B13 (Plan of Action):** [Link to execution timeline]
- **B02 (Commitments):** [Link to action items]

---
**Feedback**: - [ ] Useful
---
```

## Quality Requirements

- **Capture ALL terms discussed** - not just financial
- **Track scope and responsibilities** clearly
- **Note confidence levels** (Firm vs. Tentative vs. TBD)
- **Compare to prior discussions** if history exists
- **Identify open items** that need resolution

## Anti-patterns

- ❌ Only capturing financial terms (miss scope, roles, timelines)
- ❌ Missing confidence indicators
- ❌ No evolution tracking from prior meetings
- ❌ Generic risk assessment
- ❌ Ignoring non-commercial collaboration terms

Generate B09 now with comprehensive collaboration terms extraction.
