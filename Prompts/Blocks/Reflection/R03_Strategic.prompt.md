---
description: Generate R03 Strategic Thought block from reflection input
tags: [reflection, block, r03, strategic, decision]
tool: true
version: 2.0
---

# R03: Strategic Thought — Deep Analytical Framework

**Block ID:** R03
**Block Name:** Strategic Thought
**Purpose:** Extract directional decisions, resource allocation thinking, opportunity costs, strategic bets, and trap doors from reflection content.

---

## 1. Domain Definition

### What This Lens Sees
R03 captures **strategic thinking**:

- **Directional decisions:** "We should go X not Y"
- **Resource allocation:** Where to invest time, money, attention
- **Opportunity cost analysis:** What's being given up
- **Strategic bets:** Hypotheses about what will work
- **Path dependencies:** Decisions that constrain future options
- **Trap doors:** Irreversible decisions requiring extra scrutiny
- **Positioning choices:** How to compete, where to play

### What This Lens Ignores
- **Market signals informing strategy** → R04
- **Product feature decisions** → R05
- **Personal feelings about decisions** → R01
- **Predictions about outcomes** → R07

### Boundary Cases
- If market signal drives strategy: Market data in R04; strategic response here
- If strategic decision has emotional weight: Decision logic here; feelings in R01

---

## 2. Extraction Framework

### Trigger Patterns
```
Direction words: should, strategy, direction, priority, focus, bet,
                 decision, choice, path, option

Resource words: invest, allocate, spend, time on, money on, attention,
                capacity, bandwidth

Trade-off words: instead of, rather than, opportunity cost, trade-off,
                 sacrifice, give up, prioritize

Commitment words: commit, all-in, focus, double down, abandon, pivot
```

### Counter-Indicators
- Discussion is purely tactical (how, not what/why)
- Content is market observation without strategic response
- Decision is personal life choice without business dimension

---

## 3. Analysis Dimensions

### Dimension 1: Decision Type
| Type | Definition |
|------|------------|
| **Direction** | Where to go, what to pursue |
| **Resource** | What to invest |
| **Positioning** | How to compete |
| **Timing** | When to act |

### Dimension 2: Reversibility
| Level | Scrutiny Required |
|-------|-------------------|
| **Easily reversible** | Standard |
| **Costly to reverse** | Elevated |
| **Trap door** | Maximum |

### Dimension 3: Time Horizon
| Horizon | Timeframe |
|---------|-----------|
| **Tactical** | Days to weeks |
| **Operational** | Months |
| **Strategic** | Years |

### Dimension 4: Confidence
| Level | Approach |
|-------|----------|
| **High conviction** | Execute |
| **Hypothesis** | Experiment |
| **Speculation** | Research more |

### Dimension 5: Dependencies
- **Standalone:** Can be made independently
- **Depends on prior:** Requires previous decision validated
- **Enables future:** Opens up subsequent choices

---

## 4. Memory Integration

```python
from N5.cognition.n5_memory_client import N5MemoryClient

profiles_to_query = ["positions", "knowledge", "meetings"]

def enrich_strategic_thought(transcript_key_concepts: list[str]) -> dict:
    client = N5MemoryClient()

    strategic_positions = client.search_profile(
        profile="positions",
        query=f"strategy direction priority {' '.join(transcript_key_concepts)}",
        limit=5
    )

    market_context = client.search_profile(
        profile="knowledge",
        query=f"market competitive {' '.join(transcript_key_concepts)}",
        limit=3
    )

    return {"positions": strategic_positions, "market_context": market_context}
```

---

## 5. Output Schema

```markdown
## R03: Strategic Thought

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Strategic Summary
**Decision/Insight:** [One sentence]
**Type:** [Direction | Resource | Positioning | Timing]
**Reversibility:** [Easy | Costly | Trap Door]
**Time Horizon:** [Tactical | Operational | Strategic]

### Strategic Analysis
[2-3 paragraphs developing the strategic reasoning]

### Alternatives Considered
[What other options exist and why this one is preferred]


### Edge Candidates
[Entities/concepts from this analysis that RIX should check for connections]
- `{concept_1}` — {potential_connection_domain}
- `{concept_2}` — {potential_connection_domain}

### Evidence
> [Direct quote showing strategic reasoning]

### Opportunity Cost
**What's being given up:** [Explicit trade-offs]
**Why it's worth it:** [Logic for accepting the cost]

### Dependencies
**Requires:** [Prior decisions or conditions needed]
**Enables:** [Future decisions this opens up]

### Trap Door Check
**Reversibility assessment:** [Easy | Costly | Trap Door]
**If trap door:** [Required validation before proceeding]

### Confidence & Validation
**Current confidence:** [High | Hypothesis | Speculation]
**What would increase confidence:** [Validation steps]

### Memory Connections
- **Related positions:** [Strategic positions this extends/challenges]
- **Supporting knowledge:** [Market intel that informs this]
```

---

## 6. Connection Hooks

### Upstream
- "Building on our decision to..."
- References to prior strategic discussions or pivots

### Downstream
- Tag the strategic domain
- Flag if this is a trap door requiring extra review

---

## 7. Worked Example

### Sample Input
```
I've been going back and forth on whether to build our own AI sourcing
capability or partner with someone like Marvin. The more I think about
it, the more I'm convinced we should partner. Our core strength is the
recruiter network. Building AI sourcing would take 6-12 months and
distract us from distribution.
```

### Final Output
```markdown
## R03: Strategic Thought

**Generated:** 2026-01-09T12:00:00Z
**Source:** 2026-01-09_build-vs-partner/transcript.md

### Strategic Summary
**Decision/Insight:** Partner for AI sourcing rather than build in-house, preserving focus on distribution strength
**Type:** Resource + Direction
**Reversibility:** Costly
**Time Horizon:** Operational

### Strategic Analysis
The decision to partner is based on focus preservation: YOUR_COMPANY's core strength is the recruiter network, not AI/ML engineering. Building internally would take 6-12 months and compete for attention with distribution efforts.

### Alternatives Considered
1. **Build in-house:** Full control but 6-12 month delay
2. **Partner:** Fast capacity, maintains focus, creates dependency

### Evidence
> "our core strength is the recruiter network... Building AI sourcing would take 6-12 months and distract us from distribution"

### Opportunity Cost
**What's being given up:** Full control of sourcing technology
**Why it's worth it:** Speed to market, focus preservation

### Trap Door Check
**Reversibility assessment:** Costly (not trap door)
Can switch partners eventually but with migration cost.

### Confidence & Validation
**Current confidence:** High conviction
**What would increase confidence:** Partner conversations confirming mutual interest
```

---

## Quality Checklist

- [ ] Decision is one clear sentence
- [ ] Reversibility is assessed accurately
- [ ] Opportunity cost is explicit
- [ ] If trap door: Explicit flag and validation requirements

## Not Applicable Criteria

```markdown
## R03: Strategic Thought

**Status:** Not applicable

**Reason:** Reflection does not contain strategic decisions, resource allocation
thinking, or directional choices.

**Alternative blocks that may apply:** [R01, R02, R04, etc.]
```

---

*Template Version: 2.0 | R-Block Framework | 2026-01-09*
