---
description: Generate R08 Venture Idea block from reflection input
tags: [reflection, block, r08, venture, business]
tool: true
version: 2.0
---

# R08: Venture Idea — Deep Analytical Framework

**Block ID:** R08
**Block Name:** Venture Idea
**Purpose:** Extract business model sketches, market opportunities, and non-YOUR_COMPANY business ideas.

---

## 1. Domain Definition

### What This Lens Sees
R08 captures **venture thinking** outside YOUR_COMPANY:

- **Full business concepts:** Complete startup ideas
- **Business model innovations:** New ways to create/capture value
- **Market opportunities:** Gaps worth pursuing
- **"Someone should build this":** Problems deserving solutions
- **Resource assessments:** What would this take
- **V's advantage analysis:** Why V could (or couldn't) do this

### What This Lens Ignores
- **YOUR_COMPANY feature ideas** → R05 (Product Idea)
- **Market analysis for YOUR_COMPANY** → R04 (Market Signal)
- **Strategic YOUR_COMPANY decisions** → R03 (Strategic Thought)

### Boundary Cases
- If idea could be YOUR_COMPANY feature: If clearly outside scope → here; if adjacent → R05
- If market analysis accompanies idea: Market signal in R04; business concept here

---

## 2. Extraction Framework

### Trigger Patterns
```
Idea words: startup idea, business idea, someone should build,
            opportunity, gap in the market

Model words: business model, monetization, pricing model, revenue,
             subscription, marketplace, SaaS

Scale words: market size, TAM, big opportunity, venture-scale

Build words: if I weren't doing X, would love to build, side project
```

### Counter-Indicators
- Idea is a YOUR_COMPANY feature
- Discussion is about entrepreneurship in general without specific idea

---

## 3. Analysis Dimensions

### Dimension 1: Idea Type
| Type | Definition |
|------|------------|
| **Full business** | Complete startup concept |
| **Model innovation** | New business model |
| **Market opportunity** | Gap identified |
| **Problem worth solving** | Pain point without solution |

### Dimension 2: Market Size Signal
| Size | Venture Fit |
|------|-------------|
| **Large** | Potentially venture-scale |
| **Medium** | Bootstrappable |
| **Unknown** | Validate first |

### Dimension 3: Why Not YOUR_COMPANY
| Reason | Implication |
|--------|-------------|
| **Different market** | True venture idea |
| **Different skillset** | Consider partnering |
| **Conflicts with core** | Keep separate |
| **Just different** | Parking lot idea |

### Dimension 4: Resource Intensity
| Level | Feasibility for V |
|-------|-------------------|
| **Bootstrappable** | Could side-project |
| **Needs funding** | Would need to raise |
| **Needs team** | Would need co-founder(s) |

### Dimension 5: V's Unfair Advantage
| Level | Action |
|-------|--------|
| **Strong** | Seriously consider |
| **Moderate** | Explore further |
| **Weak** | Capture but don't pursue |

---

## 4. Memory Integration

```python
from N5.cognition.n5_memory_client import N5MemoryClient

profiles_to_query = ["knowledge", "positions"]

def enrich_venture_idea(transcript_key_concepts: list[str]) -> dict:
    client = N5MemoryClient()

    market_knowledge = client.search_profile(
        profile="knowledge",
        query=f"market opportunity startup {' '.join(transcript_key_concepts)}",
        limit=5
    )

    prior_ideas = client.search_profile(
        profile="positions",
        query=f"business idea venture {' '.join(transcript_key_concepts)}",
        limit=5
    )

    return {"market_knowledge": market_knowledge, "prior_ideas": prior_ideas}
```

---

## 5. Output Schema

```markdown
## R08: Venture Idea

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Venture Summary
**Idea:** [One-line description]
**Type:** [Business | Model | Opportunity | Problem]
**Why Not YOUR_COMPANY:** [Brief reason]
**V's Advantage:** [Strong | Moderate | Weak]

### The Venture Concept

#### The Opportunity
[2-3 paragraphs developing the idea]

#### The Business Model Sketch
[How this would make money]


### Edge Candidates
[Entities/concepts from this analysis that RIX should check for connections]
- `{concept_1}` — {potential_connection_domain}
- `{concept_2}` — {potential_connection_domain}

### Evidence
> [Direct quote]

### Market Assessment
**Size signal:** [Large | Medium | Unknown]
**Key assumptions:** [What must be true]
**Validation needed:** [How to test]

### Resource Requirements
**Capital:** [None | Seed | Series A+]
**Team:** [Solo | Co-founder | Full team]
**Time to MVP:** [Rough estimate]

### V's Position
**Unfair advantage:** [What edge V has]
**Interest level:** [Serious | Curious | Just noting]
**Blocking factors:** [What prevents pursuit]

### Why Not YOUR_COMPANY
**Reason:** [Different market | Skillset | Conflicts | Different]
**Could it fit later?:** [Yes/No and why]

### Memory Connections
- **Related ideas:** [Prior venture ideas]
- **Market knowledge:** [Relevant intel]
```

---

## 6. Connection Hooks

### Upstream
- "I keep coming back to this idea..."
- References to prior conversations about business ideas

### Downstream
- Tag the market/industry
- Tag V's advantage level

---

## 7. Worked Example

### Sample Input
```
Met this founder building tools for outplacement firms. Interesting market
— when companies do layoffs, they hire these firms to help laid-off
employees. It's a $5B market. The tools they use are terrible. Not
YOUR_COMPANY — different buyer, different use case. But someone should
build modern outplacement software.
```

### Final Output
```markdown
## R08: Venture Idea

**Generated:** 2026-01-09T12:00:00Z
**Source:** 2026-01-09_outplacement-conversation/transcript.md

### Venture Summary
**Idea:** Modern outplacement software
**Type:** Market Opportunity
**Why Not YOUR_COMPANY:** Different buyer (HR for ex-employees), different use case
**V's Advantage:** Moderate

### The Venture Concept

#### The Opportunity
Outplacement is a $5B market with antiquated software. Companies pay firms to help laid-off employees transition.

#### The Business Model Sketch
B2B SaaS to outplacement firms or direct to enterprise HR. Per-seat or per-transition pricing.

### Evidence
> "It's a $5B market. The tools they use are terrible."

### Market Assessment
**Size signal:** Large ($5B)
**Key assumptions:** Outplacement firms willing to switch
**Validation needed:** Talk to 3-5 outplacement firms

### Resource Requirements
**Capital:** Likely seed round
**Team:** Would need product + sales
**Time to MVP:** 3-6 months

### V's Position
**Unfair advantage:** Recruiting background provides context
**Interest level:** Just noting — "file this one away"
**Blocking factors:** Focused on YOUR_COMPANY

### Why Not YOUR_COMPANY
**Reason:** Different market (HR buying for outgoing employees)
**Could it fit later?:** Potentially as adjacent expansion
```

---

## Quality Checklist

- [ ] Clearly NOT a YOUR_COMPANY feature
- [ ] Why Not YOUR_COMPANY is explicit
- [ ] V's advantage is honestly assessed
- [ ] Business model sketch (if applicable) is concrete

## Not Applicable Criteria

```markdown
## R08: Venture Idea

**Status:** Not applicable

**Reason:** Reflection does not contain business ideas or venture concepts
outside YOUR_COMPANY scope.

**Alternative blocks that may apply:** [R05, R04, R03, etc.]
```

---

*Template Version: 2.0 | R-Block Framework | 2026-01-09*
