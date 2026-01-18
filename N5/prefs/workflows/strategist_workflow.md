---
created: 2025-12-16
last_edited: 2025-12-16
version: 1.0
provenance: con_TU8sAIUts3Mzvqq6
---

# Strategist Workflow

## Overview

This workflow guides strategic analysis from raw input to actionable output. Load this file when doing substantive strategy work.

---

## Phase 1: Context Setting (REQUIRED START)

Before any analysis or ideation, establish:

### 1.1 Scope Definition
- **Decision/question**: What specific decision or question are we addressing?
- **Stakeholder/audience**: Who will use this output?
- **Constraints**: Time, resources, political, technical limitations?
- **Success criteria**: How will we know if the strategy is good?

### 1.2 Data Source Confirmation
- What data do we have? (transcripts, conversations, documents, observations)
- What data is missing? (flag gaps explicitly)
- Quality of data? (firsthand vs. secondhand, recent vs. stale)

### 1.3 Mode Selection
| Mode | Use When | Expected Output |
|------|----------|-----------------|
| **Analysis** | Have data, need patterns/frameworks | Validated patterns + operational framework |
| **Ideation** | Stuck, need options, exploring | 3-5 distinct options + reversible experiments |
| **Integrated** | Complex strategic work (default) | Full analysis → options → framework → recommendation |

### 1.4 Clarification Gate
**IF any of these are unclear, STOP and ask:**
- What's the actual decision being made?
- What would a "good" answer look like?
- What's off the table? (constraints)
- Who else has input on this?

---

## Phase 2: Exploration

### Analysis Path (when you have data)

```
Data → Tag → Cluster → Abstract → Validate → Operationalize
```

**Step 2A.1: Tag Examples**
- Mark each data point with emerging themes
- Use user's language where possible
- Count: need ≥3 examples per pattern

**Step 2A.2: Cluster**
- Group similar examples
- Look for natural boundaries
- Note outliers (they often reveal edge cases)

**Step 2A.3: Abstract Patterns**
- Name each cluster as a pattern
- Write pattern as: "When [context], then [behavior/outcome]"
- Test: Does this pattern predict behavior?

**Step 2A.4: Validate**
- Pattern must hold >70% of the time
- Explain exceptions explicitly
- If <70%, re-cluster or abandon

**Step 2A.5: Operationalize**
- Turn pattern into usable rubric/playbook
- Test: Can someone else use this without you?

### Ideation Path (when stuck or exploring)

**Ideation Moves:**
| Move | Description | Use When |
|------|-------------|----------|
| **Ladder** | Ask "why?" 5x to find root, "how?" to find mechanisms | Need to go deeper or broader |
| **Invert** | What's the opposite? What if we did nothing? | Options feel too similar |
| **Constraint Play** | What if budget was 10x? What if timeline was 1 week? | Stuck in current framing |
| **10x Thinking** | What would make this 10x better, not 10% better? | Incremental thinking trap |
| **Edge Scan** | What's the weirdest version? What would a competitor do? | Need creative options |

**Option Quality Check:**
- ❌ Options too similar → Use invert or 10x thinking
- ❌ No clear trade-offs → Options aren't distinct enough
- ❌ Can't test cheaply → Add reversible experiments to each

---

## Phase 3: Convergence (REQUIRED END)

### 3.1 Synthesize Findings

**For Pattern Analysis, deliver:**
```
## Patterns Identified (N=X examples)
- Pattern 1: [description] (N=Y, holds Z%)
- Pattern 2: [description] (N=Y, holds Z%)

## Framework
[Operational rubric/playbook someone else can use]

## Implications
- Decision: [what this means for the choice at hand]
- Action: [concrete next steps]
- Uncertainty: [what we still don't know]
```

**For Strategic Options, deliver:**
```
## Options (3-5 distinct paths)

### Option 1: [Name]
- Core bet: [what you're betting on]
- Trade-off: [what you give up]
- Test: [cheap way to validate]

### Option 2: [Name]
...

## Recommendation
- Pick: [which option and why]
- Hedge: [how to mitigate downside]
```

### 3.2 Quality Self-Check

Run before delivering:

**Pattern Work:**
- [ ] ≥3 clear examples per pattern?
- [ ] Pattern holds >70%?
- [ ] Exceptions explained?

**Ideation Work:**
- [ ] Options are genuinely distinct?
- [ ] Trade-offs are clear?
- [ ] Each option has a cheap test?

**Framework Work:**
- [ ] Can hand to someone else? (operational)
- [ ] Surfaces non-obvious insight?
- [ ] Connects to specific decision/action?

**Universal:**
- [ ] Example/claim count visible (N=X)?
- [ ] Each claim has evidence?
- [ ] Uncertainties explicit?
- [ ] Avoided "probably/likely" without data?

---

## Anti-Patterns (Avoid These)

| Anti-Pattern | Fix |
|--------------|-----|
| **Speculation** | No "probably/likely" without data. Say "Unknown" or "Assuming X, then Y" |
| **Premature Complete** | Show "X/Y (Z%)" not "✓ Done" |
| **Generic Frameworks** | Make context-specific or flag as "generic starting point" |
| **Insight Dumping** | >5 insights → synthesize to 2-3 themes |
| **Hidden Assumptions** | Prefix with "Assuming [X], then..." |
| **Analysis Paralysis** | >5 options → converge to top 3 |

---

## Handoff Triggers

| Situation | Hand to |
|-----------|---------|
| Strategy ready for implementation | Builder |
| Strategy needs polished documentation | Writer |
| Strategy needs more data/research | Researcher |
| Strategy requires new system design | Architect |
| Work complete | Operator |

---

## Example: Pattern Analysis Output

```
## Patterns Identified (N=12 examples)

### Pattern 1: "Warm intro decay" (N=5, holds 80%)
When a warm intro is made but no meeting scheduled within 7 days,
response rate drops from ~70% to ~20%.

### Pattern 2: "Context-first converts" (N=4, holds 100%)
When the intro email includes specific context about why the
connection matters, response rate is 90%+ regardless of timing.

### Pattern 3: "Cold re-warm" (N=3, holds 67%)
Re-warming a stale intro with new context can recover ~50% of
decayed intros.

## Framework: Warm Intro Velocity Playbook

1. Within 24h of intro: Send meeting request with specific context
2. Day 3: If no response, add new relevant context (not just "bumping")
3. Day 7: Final attempt with different angle or graceful close
4. Never: Generic "just following up" without new information

## Implications
- Decision: Prioritize intro velocity over volume
- Action: Add "intro aging" alert to CRM workflow
- Uncertainty: Sample size small (N=12), pattern 3 needs validation
```