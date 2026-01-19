---
description: Generate R05 Product Idea block from reflection input
tags: [reflection, block, r05, product, careerspan]
tool: true
version: 2.0
---

# R05: Product Idea — Deep Analytical Framework

**Block ID:** R05
**Block Name:** Product Idea
**Purpose:** Extract user problems, solution sketches, MVP scope, and validation approaches for YOUR_COMPANY features.

---

## 1. Domain Definition

### What This Lens Sees
R05 captures **product thinking** for YOUR_COMPANY:

- **User problems:** Observed or hypothesized pain points
- **Solution sketches:** Feature ideas, workflow improvements
- **Build vs buy analysis:** Make or integrate decisions
- **MVP scope thinking:** What's the minimum viable version
- **Validation approaches:** How to test if this works
- **User workflow insights:** How users actually behave

### What This Lens Ignores
- **Business model innovation** → R08 (Venture Idea)
- **Market dynamics driving features** → R04 (Market Signal)
- **Strategic fit decisions** → R03 (Strategic Thought)
- **Non-YOUR_COMPANY product ideas** → R08 (Venture Idea)

### Boundary Cases
- If market signal suggests product direction: Market observation in R04; product response here
- If idea is for a new business: Goes to R08, not here

---

## 2. Extraction Framework

### Trigger Patterns
```
Problem words: user needs, pain point, frustration, problem, struggle,
               workflow, friction, manual, tedious

Solution words: feature, build, should have, what if we, imagine if,
                add a, create a, implement

Scope words: MVP, minimum, first version, start with, later we can,
             phase 1, initially, simple version

Validation words: test, validate, measure, would users, do they want
```

### Counter-Indicators
- Idea is for a business outside YOUR_COMPANY
- Discussion is purely strategic without product specifics

---

## 3. Analysis Dimensions

### Dimension 1: Problem Clarity
| Level | Confidence |
|-------|------------|
| **Clear, validated** | User feedback confirms problem |
| **Hypothesized** | Inferred from behavior/context |
| **Solution seeking problem** | Needs validation |

### Dimension 2: User Segment
| Segment | YOUR_COMPANY Priority |
|---------|---------------------|
| **Recruiters** | Primary |
| **Employers** | Secondary |
| **Candidates** | Tertiary |
| **Platform** | Enabling |

### Dimension 3: Effort Estimate
| Level | Timeframe |
|-------|-----------|
| **Quick win** | Days |
| **Medium build** | Weeks |
| **Major feature** | Months |

### Dimension 4: Validation Status
| Status | Next Step |
|--------|-----------|
| **Validated** | Build |
| **Partially validated** | Targeted validation |
| **Untested** | Validation required |

### Dimension 5: Priority Signal
| Priority | Action |
|----------|--------|
| **Urgent** | Do now |
| **Important** | Plan for next cycle |
| **Nice to have** | Backlog |

---

## 4. Memory Integration

```python
from N5.cognition.n5_memory_client import N5MemoryClient

profiles_to_query = ["knowledge", "positions", "meetings"]

def enrich_product_idea(transcript_key_concepts: list[str]) -> dict:
    client = N5MemoryClient()

    product_knowledge = client.search_profile(
        profile="knowledge",
        query=f"product feature user careerspan {' '.join(transcript_key_concepts)}",
        limit=5
    )

    user_feedback = client.search_profile(
        profile="meetings",
        query=f"user feedback feature request {' '.join(transcript_key_concepts)}",
        limit=5
    )

    return {"product_knowledge": product_knowledge, "user_feedback": user_feedback}
```

---

## 5. Output Schema

```markdown
## R05: Product Idea

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Product Summary
**Idea:** [One-line description]
**Problem:** [What user problem this solves]
**User Segment:** [Recruiters | Employers | Candidates | Platform]
**Validation Status:** [Validated | Partial | Untested]

### Product Thinking

#### The Problem
[1-2 paragraphs on the user problem]

#### The Solution Sketch
[1-2 paragraphs on the proposed feature]


### Edge Candidates
[Entities/concepts from this analysis that RIX should check for connections]
- `{concept_1}` — {potential_connection_domain}
- `{concept_2}` — {potential_connection_domain}

### Evidence
> [Direct quote showing product insight]

### Effort vs Impact
**Effort:** [Quick | Medium | Major]
**Priority:** [Urgent | Important | Nice to have]

### Validation Plan
**Current status:** [What we know]
**How to validate:** [Specific validation approach]

### MVP Scope
**Minimum version:** [What's the smallest useful version]
**Future expansion:** [What could be added later]

### Memory Connections
- **Related features:** [Existing or planned features]
- **User feedback:** [Prior feedback supporting this]
```

---

## 6. Connection Hooks

### Upstream
- "Users have been asking for..."
- References to roadmap or prior product conversations

### Downstream
- Tag the user segment
- Tag the product area (matching, messaging, analytics, etc.)

---

## 7. Worked Example

### Sample Input
```
Talking to Sarah at RecruitCorp, she mentioned spending hours every week
manually tracking which candidates she's already reached out to. She has
a spreadsheet but it's always out of date. We should have a simple
outreach tracker in YOUR_COMPANY.
```

### Final Output
```markdown
## R05: Product Idea

**Generated:** 2026-01-09T12:00:00Z
**Source:** 2026-01-09_sarah-conversation/transcript.md

### Product Summary
**Idea:** Outreach tracker — log candidate outreach with channel and response status
**Problem:** Recruiters spend hours manually tracking outreach in spreadsheets
**User Segment:** Recruiters
**Validation Status:** Validated

### Product Thinking

#### The Problem
Recruiters spend significant time manually tracking which candidates they've contacted. Current solutions (spreadsheets) are manual and get out of date.

#### The Solution Sketch
Simple outreach tracker: log an outreach (date, channel, response status) when viewing a candidate. Surface in a list view.

### Evidence
> "spending hours every week manually tracking which candidates she's already reached out to"

### Effort vs Impact
**Effort:** Quick — three fields, list view
**Priority:** Important — saves user time, increases stickiness

### Validation Plan
**Current status:** Validated by Sarah's direct feedback
**How to validate:** Confirm with 5 more recruiters

### MVP Scope
**Minimum version:** Date, channel, response status, list view
**Future expansion:** Sequences, analytics, team coordination
```

---

## Quality Checklist

- [ ] Problem is stated from user perspective
- [ ] MVP scope is actually minimal
- [ ] User segment is in YOUR_COMPANY's target
- [ ] Doesn't overlap with existing features

## Not Applicable Criteria

```markdown
## R05: Product Idea

**Status:** Not applicable

**Reason:** Reflection does not contain product ideas, user problems,
or feature thinking for YOUR_COMPANY.

**Alternative blocks that may apply:** [R03, R04, R08, etc.]
```

---

*Template Version: 2.0 | R-Block Framework | 2026-01-09*
