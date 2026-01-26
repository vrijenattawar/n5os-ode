---
created: 2026-01-24
last_edited: 2026-01-25
version: 1.1
provenance: con_xrhltA7BHuQGYNyw
---

# Drop Brief Template

Use this template when creating Drop briefs for Pulse builds.

---

```markdown
---
drop_id: D<stream>.<seq>
build_slug: <slug>
stream: <n>
depends_on: []
spawn_mode: auto  # Options: auto (default) = /zo/ask headless | manual = V pastes into new thread
thread_title: "[<slug>] D<stream>.<seq>: <Task Name>"
---

# Drop Brief: <Task Name>

**Mission:** <One sentence describing the goal>

**Output:** <Specific file paths or artifacts to create>

---

## Context

<Everything the Drop needs to understand the task. Include:>
- Why this task exists
- How it fits into the larger build
- Any relevant decisions already made
- Links to reference files if needed

<IMPORTANT: Drops have NO context from the orchestrator. Everything needed must be here.>

## Requirements

<Detailed requirements, organized by section if complex>

### Section 1
- Requirement A
- Requirement B

### Section 2
- Requirement C

## Success Criteria

The Filter will verify these criteria. Be specific and verifiable.

- [ ] <Specific criterion that can be checked>
- [ ] <Another criterion>
- [ ] <File exists at path X>
- [ ] <Function Y is exported>

## Anti-Patterns (Avoid)

<List things the Drop should NOT do>

- Don't X
- Don't Y

## Technique Selection

**Skills-First:**
Before building new functionality, check if a relevant skill exists:
```bash
find /home/workspace/Skills -name "SKILL.md"
```
- If reusable skill exists → USE IT
- If building reusable functionality → CREATE A SKILL under `Skills/<name>/`
- One-off scripts are OK for: build-specific glue, simple file ops, throwaway validation

**LLM vs Python/Regex:**
| Task | Use LLM (`/zo/ask`) | Use Python/Regex |
|------|---------------------|------------------|
| Extract meaning from text | ✅ | ❌ |
| Classify/categorize content | ✅ | ❌ |
| Parse unstructured/natural language | ✅ | ❌ |
| Structured JSON/CSV parsing | ❌ | ✅ |
| Math/calculations | ❌ | ✅ |
| File operations | ❌ | ✅ |

**Red flags (switch to LLM):** Regex has 3+ alternations, parsing human text, pattern keeps breaking on edge cases.

Log technique decisions to BUILD_LESSONS.json for other Drops.

---

## On Completion

Write deposit to `N5/builds/<slug>/deposits/<drop_id>.json`:

```json
{
  "drop_id": "<drop_id>",
  "status": "complete",
  "timestamp": "<ISO timestamp>",
  "summary": "<One paragraph describing what was done>",
  "artifacts": [
    "<path to created file 1>",
    "<path to created file 2>"
  ],
  "decisions": [
    "<Decision made during execution>"
  ],
  "concerns": [
    "<Any concerns for the orchestrator>"
  ],
  "notes_for_orchestrator": "<Anything the next Drop or orchestrator should know>"
}
```

If blocked, use status "blocked" and explain in notes_for_orchestrator.

**DO NOT COMMIT CODE.** The orchestrator commits at build completion.
```

---

## Current (Sequential Chain) Variant

For Drops that must execute in sequence, add the `current_chain` field:

```yaml
---
drop_id: D1.3
current_chain: "C1"  # Part of Current C1
---
```

And ensure `meta.json` has:

```json
"currents": {
  "C1": ["D1.3", "D1.4", "D1.5"]
}
```

D1.4 won't spawn until D1.3's Deposit passes Filter.

---

## Naming Convention

| Pattern | Meaning |
|---------|---------|
| `D1.1-schema.md` | Stream 1, Drop 1: "schema" |
| `D1.2-api.md` | Stream 1, Drop 2: "api" |
| `D2.1-frontend.md` | Stream 2, Drop 1: "frontend" |
| `C1.3-auth.md` | Current chain, position 3: "auth" (sequential) |
