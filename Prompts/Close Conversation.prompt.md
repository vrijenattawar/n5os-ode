---
title: Close Conversation
description: |
  Unified conversation close - auto-detects mode (Worker vs Full) and tier.
  Workers do partial close (handoff to orchestrator). Full close includes commits.
tool: true
tags:
  - workflow
  - state
  - close
---

# Close Conversation

Systematic conversation close procedure for N5OS-Ode.

## When to Use

Call `@Close Conversation` when:
- Ending a work session
- Switching contexts
- Before extended breaks
- After completing major deliverables

## Close Procedure

### 1. State Crystallization

Update SESSION_STATE.md with:
- What was accomplished this session
- Any decisions made
- Open questions or blockers
- Next steps

If SESSION_STATE.md doesn't exist, create a brief summary note instead.

### 2. Artifact Check

Verify all created/modified files:
- [ ] Files saved to correct locations
- [ ] No orphaned files in workspace root
- [ ] Temporary files cleaned up

### 3. Handoff Summary

Provide a clear handoff for the next session:

```
## Session Summary

**Accomplished:**
- [List completed items]

**In Progress:**
- [List partial work]

**Next Session:**
- [List priority items]

**Blockers:**
- [List any blockers, or "None"]
```

## Worker Mode (Partial Close)

If this is a worker thread spawned from an orchestrator:

1. Summarize what was completed
2. List any files created/modified
3. Note any issues encountered
4. Prepare handoff for orchestrator

Do NOT attempt git commits - the orchestrator handles that.

## Full Mode (Interactive Session)

If this is an interactive session:

1. Complete state crystallization
2. Verify all artifacts
3. Stage changes for git if appropriate
4. Provide handoff summary

---

## Tips

- Be specific about what changed
- Include file paths for modified files
- Flag any concerns or uncertainties
- Don't mark "done" until actually done

