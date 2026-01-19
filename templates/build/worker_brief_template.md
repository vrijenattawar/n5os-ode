---
worker_id: W{{WAVE}}.{{SEQ}}
title: "[{{SLUG}}] W{{WAVE}}.{{SEQ}}: {{TASK_NAME}}"
build_slug: {{SLUG}}
wave: {{WAVE}}
depends_on: []
thread_title: "[{{SLUG}}] W{{WAVE}}.{{SEQ}}: {{TASK_NAME}}"
---

# Worker Brief: {{TASK_NAME}}

**Your Mission:** {{ONE_SENTENCE_MISSION}}

**Output(s):**
- `{{OUTPUT_PATH_1}}` (CREATE/UPDATE)
- `{{OUTPUT_PATH_2}}` (CREATE/UPDATE)

---

## Context from Previous Waves

<!-- 
ORCHESTRATOR: Update this section with learnings from completed workers before launching.
Include:
- Relevant outputs from dependencies
- Recommendations from earlier workers
- Schema/format decisions that affect this task
- Warnings or pitfalls identified
-->

{{CONTEXT_FROM_COMPLETED_WORKERS}}

---

## Context

<!-- Everything the worker needs to know. Self-contained — worker should not need to read other files to understand the task. -->

{{CONTEXT_DESCRIPTION}}

---

## Detailed Requirements

### {{REQUIREMENT_SECTION_1}}

{{REQUIREMENT_DETAILS}}

### {{REQUIREMENT_SECTION_2}}

{{REQUIREMENT_DETAILS}}

---

## Success Criteria

- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}
- [ ] {{CRITERION_3}}
- [ ] {{CRITERION_4}}

---

## Report Back

When complete, include in your completion:
- List of files created/modified
- Any decisions made (and rationale)
- Recommendations for dependent workers
- Blockers encountered (if any)

### Notes for Orchestrator (Speak Up!)

**Workers are encouraged to provide feedback.** If you observe anything during implementation that should inform:
- How other workers should approach their tasks
- Gaps in the current plan or system design
- Better approaches than what was specified
- Warnings about potential issues
- Decisions that affect downstream workers

...include it in your completion under `notes_for_orchestrator`. The orchestrator reviews these and updates remaining briefs accordingly. Your ground-level observations are valuable.

---

## Important

**DO NOT COMMIT.** Write completion to `N5/builds/{{SLUG}}/completions/W{{WAVE}}.{{SEQ}}.json`

Completion format:
```json
{
  "worker_id": "W{{WAVE}}.{{SEQ}}",
  "status": "complete",
  "completed_at": "{{ISO_TIMESTAMP}}",
  "files_created": [],
  "files_modified": [],
  "decisions": [],
  "recommendations": [],
  "blockers": [],
  "notes_for_orchestrator": [
    {
      "type": "warning|suggestion|gap|decision",
      "for": "W#.# or general",
      "message": "Description of the observation or recommendation"
    }
  ]
}
```
