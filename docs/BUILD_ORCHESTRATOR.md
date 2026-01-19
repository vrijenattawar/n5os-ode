---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_KezoDDvMSxCNIYd0
---

# Build Orchestrator System

The Build Orchestrator is a human-in-the-loop distributed cognition pattern for complex builds that exceed a single conversation's context window.

---

## 1. Overview

### The Problem

Large builds—refactoring a site, creating a multi-document system, or executing a complex research project—often exceed what a single conversation can hold. Context windows fill up. Zo loses track of earlier decisions. Quality degrades.

The naive solution is API-based parallelization (`/zo/ask`), but this creates coordination nightmares: no human oversight, no ability to adapt mid-build, and child invocations that can't see each other's work.

### The Solution: Orchestrator as Document

The Build Orchestrator inverts the model:

- **The orchestrator is a document, not a conversation.** `BUILD.md` is the living record the user returns to throughout the build.
- **Workers are separate conversations.** the user manually opens new threads and pastes worker briefs.
- **State flows through files, not APIs.** Workers write completions to disk; the orchestrator reads them on user return.
- **Human-in-the-loop at every step.** the user decides when to launch workers, reviews completions, and approves adaptations.

This is distributed cognition with the user as the coordinator, not fire-and-forget automation.

### When to Use Build Orchestration

Use the build orchestrator when:

- The work is too large for a single conversation (>30 minutes sustained work)
- Multiple independent tracks can run in parallel
- You need to preserve context across conversation boundaries
- Quality requires human review at each stage

Do NOT use when:

- The task fits comfortably in one conversation
- There's no natural decomposition into parallel tracks
- Speed matters more than coordination (use `/zo/ask` instead)

---

## 2. Folder Structure

Every build lives at `N5/builds/<slug>/`:

```
N5/builds/<slug>/
├── BUILD.md          # Living orchestrator document
├── PLAN.md           # Architect's execution plan (waves, workers, deps)
├── STATUS.md         # Human-readable progress tracking
├── meta.json         # Machine-readable state (current wave, blocked workers)
├── workers/          # Worker briefs (paste into new threads)
│   ├── W1.1-<name>.md
│   ├── W1.2-<name>.md
│   └── W2.1-<name>.md
└── completions/      # Worker completion reports
    ├── W1.1.json
    └── W1.2.json
```

### File Purposes

| File | Purpose | Who Writes | Who Reads |
|------|---------|------------|-----------|
| `BUILD.md` | Living orchestrator doc; the user returns here | Architect initially, updated throughout | the user, Orchestrator persona |
| `PLAN.md` | Execution plan with waves, dependencies | Architect | the user, all workers (context) |
| `STATUS.md` | Progress dashboard | Updated after each completion | the user (quick status check) |
| `meta.json` | Machine state for scripts | Scripts, orchestrator | Scripts, close hooks |
| `workers/*.md` | Self-contained worker briefs | Architect | the user pastes into new threads |
| `completions/*.json` | Structured completion reports | Worker close hooks | Orchestrator on user return |

---

## 3. The Flow

### Phase 1: Initialization

1. **the user invokes build orchestrator** — Says "build X" or describes a complex system to create
2. **Operator routes to Architect** — Architect plans the decomposition
3. **Architect creates plan** — Writes `PLAN.md` with waves, workers, and dependencies
4. **Architect creates worker briefs** — One file per worker in `workers/`
5. **Architect initializes BUILD.md** — The living document the user will return to

### Phase 2: Execution Loop

6. **the user opens new thread** — Creates a fresh conversation
7. **the user pastes worker brief** — The brief contains all context needed
8. **Worker executes** — Follows the brief, creates artifacts
9. **Worker closes (NO COMMIT)** — Only the orchestrator commits code builds
10. **Close hook fires** — Writes structured completion to `completions/<worker_id>.json`
11. **the user returns to orchestrator** — Opens original conversation or fresh thread with BUILD.md
12. **Orchestrator reviews completions** — Reads new completion files, updates status
13. **Orchestrator adapts if needed** — May update remaining worker briefs based on learnings
14. **Repeat for next wave** — Continue until all workers complete

### Phase 3: Finalization

15. **All workers complete** — Orchestrator confirms via STATUS.md
16. **Orchestrator does final review** — Coherence check across all artifacts
17. **Orchestrator commits (code builds only)** — Single atomic commit for the entire build
18. **Build closes** — meta.json marked complete

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                            │
│                        (the user returns here)                         │
│                                                                 │
│   BUILD.md ← living doc    STATUS.md ← progress dashboard       │
│   PLAN.md ← execution plan meta.json ← machine state            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
    ┌──────────┐         ┌──────────┐         ┌──────────┐
    │ Worker   │         │ Worker   │         │ Worker   │
    │   1.1    │         │   1.2    │         │   1.3    │
    │          │         │          │         │          │
    │ (thread) │         │ (thread) │         │ (thread) │
    └────┬─────┘         └────┬─────┘         └────┬─────┘
         │                    │                    │
         ▼                    ▼                    ▼
    completions/         completions/         completions/
    W1.1.json            W1.2.json            W1.3.json
```

---

## 4. Worker Brief Format

Worker briefs must be **completely self-contained**. The worker has no access to the orchestrator's context.

### Template

```markdown
---
worker_id: W<wave>.<seq>
title: "[<slug>] W<wave>.<seq>: <Task Name>"
build_slug: <slug>
wave: <n>
depends_on: [W1.1, W1.2]  # empty array if none
thread_title: "[<slug>] W<wave>.<seq>: <Task Name>"
---

# Worker Brief: <Task Name>

**Your Mission:** <One sentence describing the goal>

**Output:** <Specific file paths or artifacts to create>

---

## Context

<Everything the worker needs to understand the task. Include:>
- Why this task exists
- How it fits into the larger build
- Any relevant decisions already made
- Links to reference files if needed

## Requirements

<Detailed requirements, organized by section if complex>

## Success Criteria

- [ ] <Specific, verifiable criterion>
- [ ] <Another criterion>
- [ ] <Final criterion>

---

## Report Back

When closing this worker, include:
- <What to confirm>
- <What decisions were made>
- <Any concerns or follow-up items>

**DO NOT COMMIT.** Write completion to `N5/builds/<slug>/completions/<worker_id>.json`
```

### Key Principles

1. **Self-contained context** — Worker can't see orchestrator. Everything needed must be in the brief.
2. **Clear success criteria** — Checkboxes that can be verified.
3. **Explicit output paths** — No ambiguity about what to create.
4. **Report-back guidance** — What the orchestrator needs to know.
5. **No-commit reminder** — Workers don't commit; orchestrator does.

---

## 5. Thread Title Convention

Consistent thread titles make it easy to find build conversations later.

### Format

```
[<build-slug>] W<wave>.<sequence>: <Task Name>
```

### Examples

| Thread Title | Meaning |
|--------------|---------|
| `[calendar-v2] ORCH: Orchestrator` | Main orchestrator thread |
| `[calendar-v2] W1.1: Database Schema` | Wave 1, Worker 1: Database Schema |
| `[calendar-v2] W1.2: API Endpoints` | Wave 1, Worker 2: API Endpoints |
| `[calendar-v2] W2.1: Frontend Components` | Wave 2, Worker 1: Frontend Components |

### Special Designations

- `ORCH` — The orchestrator conversation
- `W<n>.<m>` — Wave n, Worker m
- `REVIEW` — Final review/integration thread

---

## 6. Build Types

The orchestrator supports different build types with different finalization behavior.

### `code_build`

For software/site development:

- Workers create code artifacts
- **Workers do NOT commit** — No git commits during execution
- **Orchestrator commits once** — Single atomic commit after all workers complete
- Commit message summarizes entire build

### `content`

For multi-document content creation:

- Workers create articles, docs, or other content
- No git operations
- Orchestrator reviews for consistency and coherence

### `research`

For multi-angle research projects:

- Workers explore different research vectors
- Orchestrator synthesizes findings
- May spawn follow-up research workers

### `general`

For any task distribution that doesn't fit above:

- Custom finalization logic
- Orchestrator determines completion criteria

### Specifying Build Type

In `meta.json`:

```json
{
  "build_type": "code_build",
  "slug": "calendar-v2",
  "current_wave": 1,
  "status": "in_progress"
}
```

---

## 7. Dependency Management

### Waves

Workers are grouped into waves. All workers in a wave can run in parallel (no dependencies within a wave).

```
Wave 1: [W1.1, W1.2, W1.3]  ← Can all run simultaneously
           ↓
Wave 2: [W2.1, W2.2]        ← Depend on Wave 1 completion
           ↓
Wave 3: [W3.1]              ← Depends on Wave 2 completion
```

### Dependencies in Briefs

Worker briefs declare dependencies in frontmatter:

```yaml
---
worker_id: W2.1
depends_on: [W1.1, W1.2]
---
```

This means W2.1 cannot start until W1.1 AND W1.2 have completed.

### Checking Dependencies

Before launching a worker, the user (or the orchestrator) verifies:

1. All dependencies have completion files in `completions/`
2. All dependency completions have `status: "complete"`

### Adaptive Briefs

After a wave completes, the orchestrator may update subsequent worker briefs:

- Incorporate learnings from completions
- Adjust scope based on what was discovered
- Add warnings about pitfalls encountered

This is the power of human-in-the-loop: the orchestrator can adapt the plan mid-build.

---

## 8. Worker Close Behavior

### What Workers Must Do

1. **Complete their assigned work** — Create all specified artifacts
2. **Write completion report** — Structured JSON to `completions/<worker_id>.json`
3. **DO NOT COMMIT** — No git commits, even for code builds

### Completion Report Format

```json
{
  "worker_id": "W1.1",
  "status": "complete",
  "timestamp": "2026-01-18T18:30:00-05:00",
  "summary": "Created database schema with 5 tables...",
  "artifacts": [
    "Sites/calendar-v2/src/db/schema.ts",
    "Sites/calendar-v2/src/db/migrations/001_initial.sql"
  ],
  "learnings": [
    "Used Drizzle ORM for type safety",
    "Added soft-delete pattern for all entities"
  ],
  "concerns": [
    "May need index optimization for recurring events query"
  ],
  "decisions": [
    "Chose UUID over auto-increment for portability"
  ],
  "follow_up": []
}
```

### Field Definitions

| Field | Type | Purpose |
|-------|------|---------|
| `worker_id` | string | Matches the brief's worker_id |
| `status` | string | `"complete"`, `"blocked"`, or `"failed"` |
| `timestamp` | ISO 8601 | When the worker closed |
| `summary` | string | One paragraph describing what was done |
| `artifacts` | array | File paths created or modified |
| `learnings` | array | What was discovered during execution |
| `concerns` | array | Issues for orchestrator to consider |
| `decisions` | array | Choices made during execution |
| `follow_up` | array | Suggested future work |

### Why No Worker Commits

For code builds, workers don't commit because:

1. **Atomicity** — The build should be one logical commit
2. **Review** — Orchestrator may need to adjust before committing
3. **Rollback** — Easier to discard a failed build if nothing is committed
4. **Message coherence** — One commit message describes the whole build

---

## 9. Orchestrator Responsibilities

### During Execution

- Track which workers have completed (via `completions/`)
- Update `STATUS.md` after each completion
- Review completions for concerns or blockers
- Adapt remaining briefs if learnings require changes
- Answer questions if the user has them

### At Finalization

For `code_build`:

1. Verify all workers complete
2. Review artifacts for coherence
3. Run any validation (tests, linting)
4. Create atomic commit with comprehensive message
5. Mark build complete in `meta.json`

For other build types:

1. Verify all workers complete
2. Synthesize outputs as appropriate
3. Mark build complete

---

## 10. Example: Calendar Build

### PLAN.md

```markdown
# Build Plan: calendar-v2

## Wave 1: Foundation
- W1.1: Database Schema — Define tables, relations, types
- W1.2: API Routes — Stub all CRUD endpoints

## Wave 2: Core Features  
- W2.1: Event CRUD — Implement create/read/update/delete (depends: W1.1, W1.2)
- W2.2: Calendar Views — Month/week/day rendering (depends: W1.1)

## Wave 3: Polish
- W3.1: Recurring Events — Implement recurrence rules (depends: W2.1)
```

### STATUS.md (mid-build)

```markdown
# Build Status: calendar-v2

## Current Wave: 2

## Completed
- [x] W1.1: Database Schema — ✓ 5 tables, soft-delete pattern
- [x] W1.2: API Routes — ✓ 12 endpoints stubbed

## In Progress
- [ ] W2.1: Event CRUD — Worker launched
- [ ] W2.2: Calendar Views — Worker launched

## Blocked
(none)

## Remaining
- [ ] W3.1: Recurring Events (waiting for W2.1)
```

---

## 11. Quick Reference

### Commands

| To Do This | Command/Action |
|------------|----------------|
| Start a build | Tell Architect to plan decomposition |
| Launch a worker | Open new thread, paste worker brief |
| Check progress | Read `STATUS.md` |
| Review completion | Read `completions/<worker_id>.json` |
| Finalize code build | Orchestrator commits |

### File Quick Reference

| File | Location |
|------|----------|
| Orchestrator doc | `N5/builds/<slug>/BUILD.md` |
| Execution plan | `N5/builds/<slug>/PLAN.md` |
| Status dashboard | `N5/builds/<slug>/STATUS.md` |
| Worker briefs | `N5/builds/<slug>/workers/W*.md` |
| Completions | `N5/builds/<slug>/completions/W*.json` |

### Worker Checklist

Before closing a worker:

- [ ] All artifacts created per brief
- [ ] Success criteria met
- [ ] Completion JSON written to `completions/`
- [ ] NO git commits made
