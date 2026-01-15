---
description: Generate R02 Learning Note block from reflection input
tags: [reflection, block, r02, learning, knowledge]
tool: true
version: 2.0
---

# R02: Learning Note — Deep Analytical Framework

**Block ID:** R02
**Block Name:** Learning Note
**Purpose:** Extract skill acquisition, knowledge gaps, mental model updates, and learning transfer opportunities from reflection content.

---

## 1. Domain Definition

### What This Lens Sees
R02 captures **learning and knowledge development**:

- **Skill acquisition:** New capabilities being developed or needed
- **Knowledge gaps:** Areas where understanding is insufficient
- **Mental model updates:** "I used to think X, now I think Y"
- **Expertise development:** Trajectory toward mastery
- **Learning transfer:** Applying insights from one domain to another
- **Technical breakthroughs:** "Aha" moments in understanding

### What This Lens Ignores
- **Strategic implications of learning** → R03
- **Market context that prompted learning** → R04
- **Emotional reactions to learning** → R01
- **Content to teach others** → R09

### Boundary Cases
- If learning has strategic implications: The learning here; strategic decision in R03
- If failure taught a lesson: The lesson here; emotional processing in R01

---

## 2. Extraction Framework

### Trigger Patterns
```
Learning words: learned, realized, discovered, understood, figured out,
                finally get, clicked, made sense, breakthrough

Gap words: don't know, need to learn, gap in, confused about, unclear,
           struggling with, knowledge gap

Model words: used to think, now I think, changed my mind, updated,
             realized that, turns out, actually
```

### Counter-Indicators
- Knowledge is assumed rather than newly acquired
- Content is teaching rather than learning
- Learning is mentioned only as context for another insight

---

## 3. Analysis Dimensions

### Dimension 1: Learning Type
| Type | Definition |
|------|------------|
| **Skill acquisition** | Learning to DO something |
| **Knowledge acquisition** | Learning FACTS or information |
| **Mental model update** | Changing HOW you think |
| **Framework development** | Building an organizing structure |

### Dimension 2: Source
| Source | Retention Likelihood |
|--------|---------------------|
| **Direct experience** | High |
| **Conversation/teaching** | Medium-high |
| **Reading/research** | Medium |
| **Failure/mistake** | Very high |

### Dimension 3: Depth
| Depth | Can... |
|-------|--------|
| **Surface** | Recognize |
| **Working** | Do |
| **Deep** | Teach |

### Dimension 4: Transfer Potential
- **Domain-specific:** Only applies in original context
- **Adjacent transfer:** Applies to related domains
- **General principle:** Applies broadly

### Dimension 5: Gap vs Gain
| Direction | Follow-up |
|-----------|-----------|
| **Gained** | Consolidate, apply |
| **Gap identified** | Plan learning |
| **Both** | Prioritize |

---

## 4. Output Schema

```markdown
## R02: Learning Note

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Learning Summary
**Topic:** [What was learned or identified as gap]
**Type:** [Skill | Knowledge | Mental Model | Framework]
**Direction:** [Gained | Gap Identified | Both]

### The Learning
[2-3 paragraphs on the substance of the learning]

**Source:** [Experience | Conversation | Reading | Failure]


### Edge Candidates
[Entities/concepts from this analysis that should be checked for connections]
- `{concept_1}` — {potential_connection_domain}
- `{concept_2}` — {potential_connection_domain}

### Evidence
> [Direct quote showing learning moment]

### Depth Assessment
**Current level:** [Surface | Working | Deep]

### Transfer Potential
**Scope:** [Domain-specific | Adjacent | General principle]
[Where else this learning might apply]

### Consolidation Actions
- [Specific actions to solidify this learning]
```

---

## 5. Connection Hooks

### Upstream
- "Building on what I learned about..."
- References to books, courses, or prior conversations

### Downstream
- Tag the knowledge domain
- Flag if this fills a previously identified gap

---

## 6. Worked Example

### Sample Input
```
Had a really clarifying conversation with Marcus about pricing. I always
thought pricing was about cost-plus — figure out your costs, add margin,
done. But he explained value-based pricing and it clicked: the price
should reflect the value to the customer, not your cost to deliver.
```

### Final Output
```markdown
## R02: Learning Note

**Generated:** 2026-01-09T12:00:00Z
**Source:** 2026-01-09_pricing-conversation/transcript.md

### Learning Summary
**Topic:** Value-based pricing vs cost-plus pricing
**Type:** Mental Model
**Direction:** Both (Gained insight + identified pricing gap)

### The Learning
The fundamental frame for pricing should be customer value, not delivery cost. Cost-plus pricing leaves value on the table when delivery cost is low but customer value is high.

**Source:** Conversation

### Evidence
> "the price should reflect the value to the customer, not your cost to deliver"

### Depth Assessment
**Current level:** Working

### Transfer Potential
**Scope:** General principle — value-based pricing applies broadly

### Consolidation Actions
- [ ] Review current pricing with value-based lens
- [ ] Read up on value-based pricing frameworks
```

---

## Quality Checklist

- [ ] Learning substance is actually explained (not just named)
- [ ] Before/after state is clear for mental model updates
- [ ] Depth assessment is honest (not inflated)
- [ ] Transfer potential includes concrete examples

## Not Applicable Criteria

```markdown
## R02: Learning Note

**Status:** Not applicable

**Reason:** Reflection does not contain learning moments, knowledge gaps,
or mental model updates.

**Alternative blocks that may apply:** [R01, R03, R04, etc.]
```

---

*Template Version: 2.0 | R-Block Framework*

