---
description: Generate B04 Open Questions block from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b04
  - questions
  - unresolved
version: 1.0
tool: true
created: 2025-11-15
last_edited: 2026-01-03
---

# Generate Block B04: Open Questions & Unresolved Items

## Objective

Capture questions, uncertainties, and unresolved issues that emerged during the meeting but weren't definitively answered or decided.

## What Qualifies as an Open Question

**Include:**
- Explicit questions asked but not answered
- Decisions deferred for later
- Information gaps identified ("We need to find out...")
- Uncertainties acknowledged ("Not sure if...")
- Topics requiring further exploration
- Assumptions that need validation
- Pending clarifications

**Exclude:**
- Questions that WERE answered (capture answer in B01_RECAP)
- Rhetorical questions
- Questions about logistics/scheduling (unless strategic)

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
block_type: B04
---

# B04: Open Questions & Unresolved Items

## Question 1: [Summary]

**QUESTION:** [Clear statement of what's unresolved]
**CONTEXT:** Why this matters, what decision/action depends on it
**WHO NEEDS TO ANSWER:** Person or team responsible for resolution
**BLOCKING:** What is waiting on this answer (if anything critical)
**NEXT STEP:** How/when this will be resolved (if discussed)

## Question 2: [Summary]
...
```

## Generation Guidelines

1. Listen for uncertainty language:
   - "We need to figure out..."
   - "I'm not sure about..."
   - "The question is..."
   - "We should check on..."
   - "Does anyone know...?"
   - "Let me get back to you on..."

2. Capture the significance:
   - Why does this question matter?
   - What's at stake?
   - What can't proceed until resolved?

3. Note ownership:
   - Who should answer this?
   - Who is best positioned to resolve?

4. Track dependencies:
   - What decisions depend on this?
   - What tasks are blocked?

5. Distinguish types:
   - Information gaps (facts to find)
   - Strategic questions (analysis needed)
   - Decisions deferred (judgment calls)

## Edge Cases

**Partially Answered Questions:**
If question was partially addressed but not fully resolved:
"QUESTION (PARTIALLY RESOLVED): X clarified that Y, but Z remains unclear"

**Implicit Questions:**
If an issue was discussed inconclusively without explicit question:
"OPEN ISSUE: Discussion about X didn't reach conclusion; unclear whether..."

**Time-Sensitive Questions:**
Flag urgency if mentioned:
"QUESTION (URGENT): Decision needed by [date]..."

Generate B04 now.

