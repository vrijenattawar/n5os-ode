---
created: {{DATE}}
last_edited: {{DATE}}
version: 1.0
type: build_orchestrator
status: draft
provenance: {{CONVO_ID}}
---

# Build: {{TITLE}}

**Slug:** `{{SLUG}}`  
**Objective:** {{OBJECTIVE}}  
**Type:** {{TYPE}}  
**Created:** {{DATE}}  
**Orchestrator Thread:** This conversation

---

## Current Status

**Phase:** {{CURRENT_PHASE}}  
**Last Update:** {{LAST_UPDATE}}

{{STATUS_SUMMARY}}

---

## Wave Progress

| Wave | Workers | Status | Notes |
|------|---------|--------|-------|
| 1 | W1.1, W1.2, ... | 🟡 In Progress | {{WAVE_1_NOTES}} |
| 2 | W2.1, W2.2, ... | ⚪ Pending | Depends on Wave 1 |

**Legend:** ⚪ Pending | 🟡 In Progress | ✅ Complete | 🔴 Blocked

---

## Worker Status

| Worker | Title | Status | Thread | Notes |
|--------|-------|--------|--------|-------|
| W1.1 | {{W1.1_TITLE}} | ⚪ Pending | — | — |
| W1.2 | {{W1.2_TITLE}} | ⚪ Pending | — | — |
| W2.1 | {{W2.1_TITLE}} | ⚪ Pending | Depends: W1.1 | — |

**Status Key:**
- ⚪ **Pending** — Not started, waiting for dependencies or wave launch
- 🟡 **In Progress** — Worker thread active
- ✅ **Complete** — Worker reported completion, merged/verified
- 🔴 **Blocked** — Cannot proceed, needs intervention
- ⏸️ **Paused** — Started but on hold

---

## Learnings Log

<!-- Aggregated insights from worker completions. Add as workers report back. -->

### From W1.1:
- _Pending completion_

### From W1.2:
- _Pending completion_

---

## Blockers & Concerns

<!-- Active issues requiring attention. Remove when resolved. -->

| Issue | Worker | Severity | Action Needed |
|-------|--------|----------|---------------|
| _None currently_ | — | — | — |

---

## Next Actions

<!-- What the orchestrator should do next. Update after each action. -->

1. [ ] Launch Wave 1 workers
2. [ ] Monitor for completion reports
3. [ ] Review and merge completions
4. [ ] Launch Wave 2 when Wave 1 complete
5. [ ] Final integration and close

---

## References

- **PLAN.md:** `N5/builds/{{SLUG}}/PLAN.md`
- **Worker Briefs:** `N5/builds/{{SLUG}}/workers/`
- **Completions:** `N5/builds/{{SLUG}}/completions/`
- **meta.json:** `N5/builds/{{SLUG}}/meta.json`

---

## Closure Checklist

_Complete before marking build as done._

- [ ] All workers complete
- [ ] All completions reviewed
- [ ] Learnings aggregated
- [ ] meta.json status updated to "complete"
- [ ] PLAN.md checklist fully checked
- [ ] Final verification performed
