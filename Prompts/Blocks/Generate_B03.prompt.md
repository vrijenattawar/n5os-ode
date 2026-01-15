---
description: Generate B03 Decisions block from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b03
  - decisions
version: 1.0
tool: true
created: 2025-11-15
last_edited: 2026-01-03
---

# Generate Block B03: Decisions Made

## Objective

Capture explicit decisions, resolutions, and agreed-upon directions that emerged from the meeting. Focus on WHAT was decided, WHY, and WHO made/approved the decision.

## What Qualifies as a Decision

**Include:**
- Explicit agreements ("We're going with Option A")
- Direction chosen between alternatives ("Let's prioritize X over Y")
- Go/no-go determinations ("We'll proceed with the pilot")
- Policy or process changes agreed upon
- Resource allocation decisions
- Timeline or deadline agreements
- Scope changes or pivots

**Exclude:**
- Options still being considered (put in B04_OPEN_QUESTIONS)
- Tasks to execute (those go in B05_ACTION_ITEMS)
- Commitments to deliver something (those go in B02_COMMITMENTS)
- Vague inclinations without clear resolution

## Input Variables

- **Meeting Transcript:** `{{transcript}}`
- **Meeting Metadata:** `{{metadata}}`

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B03
---

# B03: Decisions Made

## Decision 1: [Clear Title]

**DECISION:** [Clear statement of what was decided]
**CONTEXT:** Why this decision was made, what problem it solves
**DECIDED BY:** Who made or approved the decision
**IMPLICATIONS:** What changes or follows from this decision
**ALTERNATIVES CONSIDERED:** Other options discussed (if mentioned)

## Decision 2: [Clear Title]
...
```

## Generation Guidelines

1. Listen for resolution language:
   - "Let's go with..."
   - "We've decided to..."
   - "The plan is..."
   - "We're moving forward with..."
   - "I think we should... [agreement follows]"

2. Capture the reasoning:
   - Why was this chosen?
   - What problem does it solve?
   - What were the tradeoffs?

3. Note implications:
   - What changes because of this?
   - Who is affected?
   - What happens next?

4. Distinguish from commitments:
   - Decision = WHAT direction to take
   - Commitment = WHO will DO what

5. Be precise about scope:
   - Was it a final decision or tentative?
   - Are there conditions or caveats?

## Edge Cases

**Tentative Decisions:**
If decision is conditional, note it clearly:
"DECISION (TENTATIVE): Will proceed with X, pending approval from Y"

**Implicit Decisions:**
If strong consensus emerges without explicit declaration, you can infer:
"DECISION (IMPLIED): Team aligned on approach X based on discussion"

**Deferred Decisions:**
If decision was explicitly postponed, note that too:
"DEFERRED: Decision on X postponed until after Y completes"

Generate B03 now.

