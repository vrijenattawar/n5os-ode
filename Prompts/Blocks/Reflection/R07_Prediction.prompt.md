---
description: Generate R07 Prediction block from reflection input
tags: [reflection, block, r07, prediction, forecast]
tool: true
version: 2.0
---

# R07: Prediction — Deep Analytical Framework

**Block ID:** R07
**Block Name:** Prediction
**Purpose:** Extract future state hypotheses, confidence levels, timeframes, and falsification criteria.

---

## 1. Domain Definition

### What This Lens Sees
R07 captures **predictive thinking**:

- **Future state predictions:** "X will happen"
- **Trend extrapolations:** "This pattern will continue"
- **Hypotheses about outcomes:** "If we do X, Y will result"
- **Timeframe estimates:** When something will occur
- **Confidence levels:** How certain V is
- **Falsification criteria:** What would prove this wrong
- **Bet-worthy beliefs:** Claims strong enough to act on

### What This Lens Ignores
- **Current market state** → R04 (Market Signal)
- **Strategic choices based on predictions** → R03 (Strategic Thought)
- **Content about predictions** → R09 (Content Idea)

### Boundary Cases
- If prediction drives strategic decision: Prediction here; decision in R03
- If market signal suggests future: Current state → R04; future claim → R07

---

## 2. Extraction Framework

### Trigger Patterns
```
Future words: will, going to, expect, predict, forecast, anticipate,
              likely, probably, in X years/months

Trend words: accelerate, slow down, continue, increase, decrease,
             momentum, trajectory, heading toward

Confidence words: bet, confident, certain, unsure, might, maybe,
                  possibly, definitely

Conditional words: if we, when they, once X happens, assuming
```

### Counter-Indicators
- Statement is about current/past state
- Future is only mentioned as context for present decision

---

## 3. Analysis Dimensions

### Dimension 1: Prediction Type
| Type | Definition |
|------|------------|
| **Market/Industry** | Industry dynamics |
| **Technology** | Tech capabilities or adoption |
| **Personal/Career** | V's own trajectory |
| **YOUR_COMPANY-specific** | Company outcomes |

### Dimension 2: Timeframe
| Horizon | Tracking |
|---------|----------|
| **Near-term** | < 6 months |
| **Medium-term** | 6-24 months |
| **Long-term** | > 2 years |

### Dimension 3: Confidence
| Level | Appropriate Risk |
|-------|------------------|
| **High** | Can act on this |
| **Medium** | Act cautiously |
| **Low** | Don't act yet |

### Dimension 4: Falsifiability
| Level | Quality |
|-------|---------|
| **Clear criteria** | Good prediction |
| **Partial criteria** | Tighten up |
| **Hard to test** | Not useful |

### Dimension 5: Stakes
| Level | Attention Required |
|-------|-------------------|
| **High** | Track actively |
| **Medium** | Periodic check |
| **Low** | Revisit later |

---

## 4. Memory Integration

```python
from N5.cognition.n5_memory_client import N5MemoryClient

profiles_to_query = ["positions", "knowledge"]

def enrich_prediction(transcript_key_concepts: list[str]) -> dict:
    client = N5MemoryClient()

    related_predictions = client.search_profile(
        profile="positions",
        query=f"predict future expect {' '.join(transcript_key_concepts)}",
        limit=5
    )

    supporting_knowledge = client.search_profile(
        profile="knowledge",
        query=f"trend forecast {' '.join(transcript_key_concepts)}",
        limit=3
    )

    return {"related_predictions": related_predictions, "supporting_knowledge": supporting_knowledge}
```

---

## 5. Output Schema

```markdown
## R07: Prediction

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Prediction Summary
**Prediction:** [One-line statement]
**Type:** [Market | Technology | Personal | YOUR_COMPANY]
**Timeframe:** [Near | Medium | Long] — [specific estimate]
**Confidence:** [High | Medium | Low]

### The Prediction

#### What Will Happen
[2-3 paragraphs developing the prediction]

#### Underlying Logic
[Why V expects this]


### Edge Candidates
[Entities/concepts from this analysis that RIX should check for connections]
- `{concept_1}` — {potential_connection_domain}
- `{concept_2}` — {potential_connection_domain}

### Evidence/Reasoning
> [Direct quote with reasoning]

### Falsification Criteria
**The prediction is WRONG if:**
- [Specific criterion 1]
- [Specific criterion 2]

**The prediction is RIGHT if:**
- [Specific criterion 1]
- [Specific criterion 2]

### Check-in Schedule
**Review date:** [Specific date]
**Interim signals to watch:** [What would update confidence]

### Stakes Assessment
**What depends on this:** [Decisions affected]
**If wrong, impact:** [What changes]

### Memory Connections
- **Related predictions:** [Prior predictions]
- **Supporting knowledge:** [Data informing this]
```

---

## 6. Connection Hooks

### Upstream
- "Continuing my prediction that..."
- References to prior forecasts or bets

### Downstream
- Set calendar reminder for check-in date
- Tag the prediction domain

---

## 7. Worked Example

### Sample Input
```
I'm pretty confident that the AI recruiting space will consolidate
significantly in the next 18 months. There are too many point solutions
right now, and employers don't want to manage 10 different tools. The
big ATS players will either build or acquire. I'd bet on this.
```

### Final Output
```markdown
## R07: Prediction

**Generated:** 2026-01-09T12:00:00Z
**Source:** 2026-01-09_market-outlook/transcript.md

### Prediction Summary
**Prediction:** AI recruiting space will consolidate significantly within 18 months
**Type:** Market/Industry
**Timeframe:** Medium — 18 months
**Confidence:** High

### The Prediction

#### What Will Happen
The AI recruiting tool landscape will undergo significant consolidation. Major ATS players will build or acquire, and most standalone startups will be acquired or fail.

#### Underlying Logic
Too many point solutions create buyer fatigue. Platform advantage will drive consolidation.

### Evidence/Reasoning
> "There are too many point solutions right now, and employers don't want to manage 10 different tools"

### Falsification Criteria
**The prediction is WRONG if:**
- By mid-2027, funded AI recruiting startups have increased
- Major ATS players have not made acquisitions

**The prediction is RIGHT if:**
- 2+ major acquisitions by top 5 ATS players
- 50%+ of current startups acquired/shut down

### Check-in Schedule
**Review date:** July 2027
**Interim signals to watch:** M&A announcements, funding news, startup shutdowns

### Stakes Assessment
**What depends on this:** YOUR_COMPANY positioning strategy
**If wrong, impact:** May be over-investing in distribution vs product
```

---

## Quality Checklist

- [ ] Prediction is specific and falsifiable
- [ ] Timeframe is explicit
- [ ] Falsification criteria are measurable
- [ ] Check-in date is set

## Not Applicable Criteria

```markdown
## R07: Prediction

**Status:** Not applicable

**Reason:** Reflection does not contain predictions, forecasts, or future-state
hypotheses.

**Alternative blocks that may apply:** [R04, R03, R06, etc.]
```

---

## Tracking Hook

Every R07 should suggest:
```
### Tracking Action
- Prediction ID: [slug]
- Review date: [date]
- Key signal: [what to watch]
```

---

*Template Version: 2.0 | R-Block Framework | 2026-01-09*
