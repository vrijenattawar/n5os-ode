---
description: Generate R06 Synthesis block from reflection input
tags: [reflection, block, r06, synthesis, patterns]
tool: true
version: 2.0
---

# R06: Synthesis — Deep Analytical Framework

**Block ID:** R06
**Block Name:** Synthesis
**Purpose:** Extract cross-domain connections, pattern recognition, framework building, and theory development.

---

## 1. Domain Definition

### What This Lens Sees
R06 captures **integrative thinking**:

- **Cross-domain connections:** "X is like Y" insights spanning different areas
- **Pattern recognition:** Recurring structures across experiences
- **Framework building:** Creating organizing structures
- **Mental model integration:** Combining multiple models
- **Theory development:** Articulating underlying principles
- **Principle extraction:** Drawing generalizable lessons

### What This Lens Ignores
- **Single-domain learning** → R02 (Learning Note)
- **Predictions based on synthesis** → R07 (Prediction)
- **Content ideas about synthesis** → R09 (Content Idea)

### Boundary Cases
- If synthesis creates a prediction: The connection here; prediction in R07
- If synthesis is primarily about one domain: Likely R02 unless genuinely cross-domain

---

## 2. Extraction Framework

### Trigger Patterns
```
Connection words: connects to, reminds me of, same pattern, just like,
                  analogous, similar to, parallel

Pattern words: pattern, always, never, tends to, every time, structure,
               recurring, common thread

Framework words: framework, model, theory, principle, way of thinking,
                 mental model, lens

Synthesis words: synthesis, integrate, combine, unify, brings together
```

### Counter-Indicators
- Connection is within a single domain
- Pattern is observed but not articulated
- Framework is being applied (not created)

---

## 3. Analysis Dimensions

### Dimension 1: Synthesis Type
| Type | Definition |
|------|------------|
| **Cross-domain connection** | Linking different fields |
| **Pattern recognition** | Seeing recurring structure |
| **Framework building** | Creating organizing structure |
| **Theory development** | Articulating underlying principle |

### Dimension 2: Domains Connected
Document the specific domains bridged (e.g., Business + Psychology)

### Dimension 3: Abstraction Level
| Level | Definition |
|-------|------------|
| **Concrete analogy** | Specific comparison |
| **Working principle** | Actionable guideline |
| **Abstract theory** | General truth |

### Dimension 4: Novelty
| Level | Value |
|-------|-------|
| **New synthesis** | High — document carefully |
| **Refinement** | Medium — note evolution |
| **Rediscovery** | Lower — note application |

### Dimension 5: Applicability
| Scope | Use |
|-------|-----|
| **Narrow** | Context-specific insight |
| **Moderate** | Useful heuristic |
| **Broad** | Foundational thinking |

---

## 4. Output Schema

```markdown
## R06: Synthesis

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Synthesis Summary
**Synthesis:** [One-line description]
**Type:** [Connection | Pattern | Framework | Theory]
**Domains Connected:** [List the domains]

### The Synthesis

#### The Insight
[2-3 paragraphs developing the connection]

#### Why This Matters
[What this synthesis enables or explains]


### Edge Candidates
[Entities/concepts from this analysis that should be checked for connections]
- `{concept_1}` — {potential_connection_domain}
- `{concept_2}` — {potential_connection_domain}

### Evidence
> [Direct quote showing synthesis moment]

### Domains Bridged
**Domain 1:** [First area]
**Domain 2:** [Second area]
**Connection:** [What's being linked]

### Abstraction Assessment
**Level:** [Concrete | Working Principle | Abstract]
**Applicability:** [Narrow | Moderate | Broad]

### Novelty Check
**Status:** [New | Refinement | Rediscovery]

### Applications
[Where this synthesis could be applied]
```

---

## 5. Connection Hooks

### Upstream
- "Building on that idea that..."
- References to books, models, or prior insights

### Downstream
- Tag domains bridged
- Flag if this should become a documented framework

---

## 6. Worked Example

### Sample Input
```
Interesting pattern: both in coaching and in sales, the best outcomes
happen when you stop trying to convince and start trying to understand.
In coaching, we call it "holding space." In sales, the best closes
happen when you deeply understand what the customer actually needs.
It's the same principle: genuine curiosity beats persuasion.
```

### Final Output
```markdown
## R06: Synthesis

**Generated:** 2026-01-09T12:00:00Z
**Source:** 2026-01-09_coaching-sales-pattern/transcript.md

### Synthesis Summary
**Synthesis:** Genuine curiosity beats persuasion — same principle in coaching and sales
**Type:** Pattern Recognition → Theory Development
**Domains Connected:** Coaching, Sales

### The Synthesis

#### The Insight
Across multiple influence contexts, the most effective approach is not persuasion but understanding. In coaching, this is "holding space." In sales, the best outcomes emerge from understanding customer needs.

The underlying principle: genuine curiosity creates better outcomes than persuasive skill.

#### Why This Matters
If true broadly, this inverts common assumptions about influence.

### Evidence
> "genuine curiosity beats persuasion"

### Domains Bridged
**Domain 1:** Coaching — "holding space," non-agenda presence
**Domain 2:** Sales — understanding customer needs
**Connection:** Both involve influence; both work better through understanding

### Abstraction Assessment
**Level:** Working Principle
**Applicability:** Broad — applies to any influence context

### Novelty Check
**Status:** New synthesis

### Applications
- Sales philosophy and training
- Hiring criteria for customer-facing roles
- Content idea: "Why the best salespeople are the best listeners"
```

---

## Quality Checklist

- [ ] Synthesis is genuinely cross-domain
- [ ] Connection is explained, not just asserted
- [ ] Abstraction level is accurately assessed
- [ ] Pattern/framework is actionable or predictive

## Not Applicable Criteria

```markdown
## R06: Synthesis

**Status:** Not applicable

**Reason:** Reflection does not contain cross-domain connections, pattern
recognition, or framework building.

**Alternative blocks that may apply:** [R02, R03, R04, etc.]
```

---

*Template Version: 2.0 | R-Block Framework*

