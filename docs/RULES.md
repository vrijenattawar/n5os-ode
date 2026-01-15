---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: worker_005_bootloader
---

# N5OS Ode Rules

This document describes the rule system in N5OS Ode — what each rule does, why it exists, and how to customize them.

---

## Overview

N5OS Ode includes **6 core rules** that govern AI behavior across all conversations. Rules are global instructions that apply automatically based on conditions.

| Rule | Condition | Purpose |
|------|-----------|---------|
| **Session State Init** | Conversation start | Track conversation context |
| **YAML Frontmatter** | Creating markdown | Trace document provenance |
| **Progress Reporting (P15)** | Reporting completion | Prevent false "done" claims |
| **File Protection** | Destructive operations | Prevent accidental data loss |
| **Debug Logging** | Recurring build errors | Break out of failure loops |
| **Clarifying Questions** | Always | Reduce mistakes from ambiguity |

---

## Rule Details

### 1. Session State Initialization

**Condition**: At the start of every conversation

**Instruction**: Check if SESSION_STATE.md exists. If missing, create it with:
- Conversation type (build, research, discussion, planning)
- Focus/objective
- Conversation ID for tracking

**Why This Exists**:
Without state tracking, long conversations lose context. The AI forgets what was accomplished, what's pending, and what the original goal was. SESSION_STATE.md provides continuity.

**Format**:
```yaml
# SESSION_STATE.md
type: build
focus: "Implementing user authentication"
objective: "Complete login flow with OAuth"
progress:
  - [x] Design auth schema
  - [ ] Implement OAuth flow
  - [ ] Add session management
```

---

### 2. YAML Frontmatter

**Condition**: When creating any markdown document

**Instruction**: Include frontmatter with created date, version, and provenance (which conversation or agent created it).

**Why This Exists**:
Documents accumulate over time. Without metadata, you can't tell:
- When something was created
- Which version you're looking at
- Where it came from (manual vs. AI-generated)

**Format**:
```yaml
---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: con_abc123xyz
---
```

**Provenance Values**:
- `con_[id]` — Created in conversation
- `agent_[id]` — Created by scheduled agent
- `manual` — Created by user directly

---

### 3. Progress Reporting (P15)

**Condition**: When reporting completion status on multi-step work

**Instruction**: Report honest progress as "X/Y done (Z%)" not "✓ Done" unless ALL subtasks are complete.

**Why This Exists**:
Premature "Done" claims are one of the most expensive AI failure modes. You think work is complete, move on, then discover hours later that critical pieces were never finished.

**Bad Example**:
```
✓ Done! Created the user authentication system.
(Actually only created 2 of 5 required files)
```

**Good Example**:
```
Completed: Schema design, OAuth config (2/5)
Remaining: Token handler, session manager, logout flow
Status: 40% complete
```

**The Name "P15"**:
Internal shorthand for "Problem 15" — the pattern of claiming completion prematurely. Named to make it easy to reference.

---

### 4. File Protection

**Condition**: Before destructive file operations (delete, move, bulk changes)

**Instruction**: Check for `.n5protected` marker files. If protected, require explicit confirmation before proceeding.

**Why This Exists**:
Some directories should never be casually deleted or reorganized:
- Configuration that breaks things if moved
- Data that can't be reconstructed
- Carefully organized structures

**How It Works**:
1. A `.n5protected` file marks a directory as protected
2. Before any destructive operation, AI checks for this marker
3. If found, shows warning and asks for confirmation
4. For bulk operations (>5 files), shows preview first

**Creating Protection**:
```bash
# Protect a directory
echo "Core system files" > N5/.n5protected

# Remove protection
rm N5/.n5protected
```

---

### 5. Debug Logging

**Condition**: When repeatedly encountering bugs or recurring issues during builds

**Instruction**: After 3 failed attempts on the same issue, stop and step back. Question assumptions, look for patterns, consider if the approach is fundamentally wrong.

**Why This Exists**:
AI can get stuck in loops — trying the same broken approach repeatedly. This rule forces a meta-cognitive break: stop trying to fix the symptom, examine the root cause.

**Reflection Questions**:
- Am I missing vital information?
- Am I executing in the right order?
- Are there dependencies I haven't considered?
- Is this approach fundamentally unsound?
- Would zooming out help?

**What Changes After This Rule Triggers**:
- Systematic review of recent attempts
- Check for circular patterns
- Consider alternative approaches
- Possibly route to Debugger persona

---

### 6. Clarifying Questions

**Condition**: Always (unconditional rule)

**Instruction**: If in doubt about objectives, priorities, or any detail that would materially affect the response, ask 2-3 clarifying questions before proceeding.

**Why This Exists**:
Most AI mistakes come from acting on assumptions. A few clarifying questions upfront can prevent hours of wasted work going in the wrong direction.

**When to Ask**:
- Ambiguous terms ("make it better" — better how?)
- Unclear scope ("handle the data" — which data? what handling?)
- Missing context ("like we discussed" — which discussion?)
- Multiple interpretations ("update the system" — which part?)

**Format**:
```
Before I proceed, a few clarifying questions:

1. [Specific question about scope/target]
2. [Question about constraints or preferences]
3. [Question about success criteria]
```

---

## Rule Hierarchy

Rules have priorities:

1. **Safety rules** (file protection) — Always apply
2. **Quality rules** (P15, frontmatter) — Always apply
3. **Workflow rules** (session state) — Apply at boundaries
4. **Guidance rules** (clarifying questions) — Apply when relevant

---

## Customizing Rules

### Edit Rules
Go to Settings > Your AI > Rules to modify existing rules:
- Change conditions to be more/less specific
- Adjust instructions for your workflow
- Add domain-specific requirements

### Add Rules
Create new rules for your specific needs:
- Company-specific terminology
- Project conventions
- Communication preferences
- Domain knowledge

### Remove Rules
Delete rules that don't fit your workflow. The 6 core rules are recommendations, not requirements.

---

## Conditional vs. Always Rules

**Conditional Rules**: Only apply when the condition is true
```
Condition: When creating markdown
Instruction: Include YAML frontmatter
```

**Always Rules**: Apply to every conversation
```
Condition: (empty)
Instruction: Ask clarifying questions when in doubt
```

Leave the condition empty for rules that should always apply.

---

## Rule Troubleshooting

**Rule not applying?**
- Rules take effect on new conversations (not current)
- Check condition matches the situation
- Verify rule is saved in Settings

**Rule too aggressive?**
- Make the condition more specific
- Add exceptions to the instruction

**Rules conflicting?**
- More specific conditions take precedence
- Consider combining related rules

---

*N5OS Ode v1.0 — Rules for consistent, reliable AI behavior*

