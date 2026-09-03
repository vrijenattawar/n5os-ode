---
name: pulse
description: |
  Automated build orchestration system. Spawns headless Zo workers (Drops) in parallel Waves,
  monitors health, validates Deposits via LLM judgment, handles dead Drops, and escalates via SMS.
  Supports sequential Streams within Waves. Replaces manual Build Orchestrator for unattended execution.
---

# Pulse: Automated Build Orchestration

## Overview

Pulse orchestrates complex builds by:
1. **Spawning Drops** (workers) via `/zo/ask` API (or generating launchers for manual Drops)
2. **Monitoring** for deposits, timeouts, failures
3. **Filtering** deposits via LLM judgment
4. **Checkpoint verification** at strategic quality gates
5. **Escalating** via email/SMS when issues arise
6. **Finalizing** with safety checks, integration tests, and learning harvest

## Terminology (Flow Metaphor)

| Term | Meaning |
|------|---------|
| **Build** | The complete orchestrated work |
| **Wave** | Parallel execution round — a hard barrier; Wave N+1 cannot start until all blocking Drops in Wave N are complete |
| **Stream** | Sequential workflow within a Wave — Drops in a Stream run in order (D1.1 → D1.2 → D1.3) |
| **Drop** | Individual worker/task — one conversation's worth of context |
| **Checkpoint** | Strategic quality gate verifying cross-Drop consistency |
| **Deposit** | Worker's completion report (JSON in `deposits/`) |
| **Filter** | LLM judgment of deposit quality |
| **Dredge** | Forensics worker for dead Drops |
| **Launcher** | Generated markdown file for manual Drops with paste-ready prompt |
| **Jettison** | Connected-but-independent build spawned as tangent off-ramp |
| **Lineage** | Parent-child relationship graph between builds |

### Execution Model

```
Wave 1 (barrier)
├── Stream 1: D1.1 → D1.2 → D1.3  (sequential)
├── Stream 2: D2.1 → D2.2         (sequential, parallel to Stream 1)
└── Stream 3: D3.1                (parallel to Streams 1 & 2)

    ↓ (all blocking Drops in Wave 1 must complete)

Wave 2 (barrier)
├── Stream 1: D1.4 → D1.5
└── Stream 2: D2.3
```

- **Waves are hard barriers**: No Drop from Wave 2 spawns until all blocking Drops in Wave 1 are complete.
- **Streams are sequential**: Within a stream, D1.2 waits for D1.1 to complete.
- **Streams run in parallel**: D1.1 and D2.1 can run simultaneously (same Wave, different Streams).

## Quick Start

```bash
# Contract gate (required before start)
python3 N5/scripts/build_contract_check.py <slug>

# Validate plan before starting (recommended)
python3 Skills/pulse/scripts/pulse.py validate <slug>

# Stress-test build assumptions before starting
python3 Skills/pulse/scripts/pulse.py grill <slug>

# Check build status
python3 Skills/pulse/scripts/pulse.py status <slug>

# Start automated orchestration
python3 Skills/pulse/scripts/pulse.py start <slug>

# Manual tick (for testing)
python3 Skills/pulse/scripts/pulse.py tick <slug>

# Render worker implementation notes
python3 Skills/pulse/scripts/pulse.py notes <slug>

# Review worker deviations before adapting later waves
python3 Skills/pulse/scripts/pulse.py review-wave <slug>

# Stop gracefully
python3 Skills/pulse/scripts/pulse.py stop <slug>

# Resume stopped build
python3 Skills/pulse/scripts/pulse.py resume <slug>

# Post-build finalization
python3 Skills/pulse/scripts/pulse.py finalize <slug>

# Launch a manual Drop (prints launcher content)
python3 Skills/pulse/scripts/pulse.py launch <slug> <drop_id>

# Retry a failed Drop (reset + update brief)
python3 Skills/pulse/scripts/pulse.py retry <slug> <drop_id> --reason "Why it failed"

# Create jettison (off-ramp build)
pulse jettison "<task>" [--from <parent>] [--type <type>]

# View build lineage DAG
pulse lineage [<slug>] [--format tree|json]
```

## Required Contract Gate

Before starting any Pulse build, both checks must pass:

```bash
python3 N5/scripts/build_contract_check.py <slug>
python3 Skills/pulse/scripts/pulse.py validate <slug>
python3 Skills/pulse/scripts/pulse.py grill <slug>
```

If either command fails, do not run `start` yet. Fix missing artifacts first (`PLAN.md`, `meta.json`, and drop briefs in `drops/`).

## Grill Gate

`grill` is the pre-build interrogation gate. It has broad latitude to inspect
the build folder, referenced workspace paths, existing skills, architecture
patterns, validators, and graph-risk output. It should auto-answer anything the
workspace can answer and ask only for real orchestrator decisions: authority,
priority, product intent, irreversible scope, or unresolved path/contract drift.

The report is written to:

```bash
N5/builds/<slug>/artifacts/GRILL_GATE.md
N5/builds/<slug>/artifacts/grill_gate.json
```

Use the report to fix the plan and briefs before `start`. If `grill` exits
non-zero, treat that as a "do not start yet" signal unless V explicitly
overrides it.

## Implementation Notes

Workers must report deterministic implementation-note fields in their deposit.
Pulse records the fields into locked append-only JSONL and renders Markdown for
the orchestrator:

```bash
N5/builds/<slug>/implementation_notes.jsonl
N5/builds/<slug>/IMPLEMENTATION_NOTES.md
```

Workers do not directly edit `IMPLEMENTATION_NOTES.md`; concurrent Markdown
append is collision-prone. Deposits should include:

- `files_touched`: exact workspace-relative files created or modified.
- `plan_deviations`: changes from assigned plan, brief, task order, or success criteria.
- `schema_deviations`: changes to data shapes, deposit formats, config keys, API contracts, or compatibility behavior.
- `assumption_changes`: assumptions made, invalidated, or discovered during execution.
- `scope_deviations`: out-of-brief work or extra files touched because the brief was incomplete.
- `collision_risks`: files, interfaces, or decisions likely to conflict with parallel Drops.
- `followup_required`: concrete orchestrator actions needed before later waves proceed.

Examples:

- Plan deviation: "Implemented locked JSONL notes instead of direct Markdown append because concurrent workers can collide."
- Schema deviation: "Added optional `collision_risks[]` to deposits; older deposits remain valid with empty defaults."
- Assumption change: "Assumed all target files existed; discovered a referenced review script is missing."
- Scope deviation: "Touched `pulse.py` routing in addition to the notes module so operators can render notes."
- Collision risk: "D2 and D4 both modify `Skills/pulse/scripts/pulse.py`; orchestrator should sequence router edits."
- Follow-up required: "Review this before spawning Wave 2 because D3 depends on the new deposit fields."

The orchestrator owns adaptation. Workers may read prior notes for context and
propose plan updates in `followup_required`, but they should not independently
rewrite future plans. The orchestrator reviews `IMPLEMENTATION_NOTES.md`, then
updates `PLAN.md`, Drop briefs, sequencing, or status centrally.

## Plan Validation

**Principle (from Theo):** Plans are context vehicles, not spec documents. An incomplete plan means the model will guess, and guessing compounds errors across Drops.

Before starting any build, validate the plan is complete:

```bash
python3 Skills/pulse/scripts/pulse.py validate <slug>
```

The validator checks for:
- **Unfilled placeholders** (`{{PLACEHOLDER}}`, `TODO:`, etc.)
- **Missing required sections** (Objective, Open Questions, Phase 1, Success Criteria)
- **Empty sections** (headers without content)
- **Missing Scenarios** — Drop briefs without a `## Scenarios` section get warnings
- **Spec completeness** — Drops with `spawn_mode: auto` but `spec_completeness: partial|ambiguous` get warnings
- **Warnings** (unchecked open questions, stale plans >14 days)

A build should NOT start until validation, contract, and grill gates pass. Treat `start` as an execution command, not a planner.

**Pre-build workflow (mandatory):**
1. Extract scenarios from intent using `Skills/spec-writing/SKILL.md` when behavior is ambiguous, user-facing, or failure-prone.
2. Run pulse-interview to decompose into Streams/Drops.
3. Architect creates `PLAN.md` with scenarios distributed into Drop briefs.
4. Optionally write holdout scenarios in `holdout_scenarios/`.
5. Run `python3 N5/scripts/build_contract_check.py <slug>`.
6. Run `python3 Skills/pulse/scripts/pulse.py validate <slug>`.
7. Run `python3 Skills/pulse/scripts/pulse.py grill <slug>`.
8. Start build only after gates pass.

## Design Context Integration (teach-impeccable)

For builds with frontend/design work, the validator checks for `.impeccable.md` in the target project directory. This is a **soft gate** — it recommends but does not block.

**How it works:**
1. `validate` scans Drop titles and briefs for design/frontend keywords (ui, layout, styling, component, aesthetic, etc.)
2. If design work is detected, it looks for `Sites/` path references in the plan and briefs
3. It checks whether `.impeccable.md` exists in the referenced project directory
4. Reports a recommendation in the `🎨 Design Context` section of the validation output

**If `.impeccable.md` is missing:**
Run `/teach-impeccable` on the target project before briefing design Drops. This captures brand personality, aesthetic direction, and design principles in a persistent file that can be injected into Drop briefs.

**If `.impeccable.md` exists:**
Inject its content into design-related Drop briefs as shared context so all workers have the same aesthetic guardrails.

**Not a blocker:** Builds can proceed without design context. The recommendation surfaces during `validate` so you can make an informed choice.

## Visual References For Design Drops

This export does not include `google-stitch` or the former Stitch helper. For design-heavy Pulse builds, create visual references manually or through the active frontend/design skills, then place them under `N5/builds/<slug>/context/` and mention them in the relevant Drop briefs.

## Required Graph Review For Refactor Drops

If a Drop will modify shared code in `N5/`, `Skills/`, `Prompts/`, or `Integrations/`, the brief should include a graph-review pre-check using `file 'N5/prefs/operations/dependency-graph-review.md'`.

Minimum sequence:

```bash
python3 Skills/codebase-graph/scripts/query.py index
python3 Skills/codebase-graph/scripts/query.py review <target>
```

If the review is `HIGH`, also run:

```bash
python3 Skills/codebase-graph/scripts/query.py rdeps <target>
```

Use the result to narrow scope or split the work into staged Drops before editing a shared hub.

## Retry Failed Drops

**Principle (from Theo):** If output is bad, don't keep appending corrections. Revert and restart with corrected input.

When a Drop fails or produces bad output:

```bash
# Reset Drop and optionally explain why
python3 Skills/pulse/scripts/pulse.py retry <slug> <drop_id> --reason "Missed the auth requirements"
```

The retry command:
1. Archives the old deposit (preserves history)
2. Resets Drop status to `pending`
3. Appends retry context to the brief (if `--reason` provided)
4. Increments retry counter

This gives the model a clean slate with better context rather than compounding errors by appending fix requests to a polluted history.

## Manual Drops & Launchers

Some Drops need human oversight — close prompting control, high-risk changes, or work requiring V's judgment.

### spawn_mode Options

| Mode | Behavior | Use When |
|------|----------|----------|
| `auto` (default) | Pulse spawns via `/zo/ask` headless | Standard automated execution |
| `manual` | Pulse generates launcher, waits for V to execute | High-risk, requires judgment, voice-sensitive |

### Automatic Recommendation

If a Drop's `spawn_mode` is not explicitly set, Pulse analyzes the brief and recommends:
- **Manual** if brief contains: "preferences", "voice protocol", "HITL", "requires V review", "Careerspan voice", "ask V", "judgment", "sensitive"
- **Auto** otherwise

The recommendation is stored as `spawn_recommendation` and applied if no explicit mode is set.

### Manual Drop Workflow

1. **Tick detects ready Drop with `spawn_mode: manual`**
2. **Launcher generated** at `N5/builds/<slug>/launchers/<drop_id>.md`
3. **Status set to `awaiting_manual`**
4. **STATUS.md updated** with:
   ```
   ## Awaiting Manual (1)
   - [ ] D1.2 → run: `python3 Skills/pulse/scripts/pulse.py launch <slug> D1.2`
   ```
5. **V runs the launch command** (or opens launcher file directly)
6. **V pastes prompt into new thread**, executes, writes deposit
7. **Next tick detects deposit**, runs Filter, advances

### Launcher File Format

```markdown
# Launcher: my-build / D1.2

## Paste into a new thread

```text
Load and execute: example file path `N5/builds/my-build/drops/D1.2-voice-sensitive-task.md`

When complete, write deposit to:
example file path `N5/builds/my-build/deposits/D1.2.json`
```

## After you finish

- Confirm the deposit exists at the path above.
- Then run:
  - `python3 Skills/pulse/scripts/pulse.py tick my-build`
  - (or run periodic tick via your scheduler of choice)
```

## blocking Field (Non-Blocking Drops)

By default, all Drops are **blocking** — the next Wave cannot start until they complete.

Set `blocking: false` on a Drop to make it **non-blocking**:
- The Drop still runs and is tracked
- But it does NOT hold up Wave advancement
- Useful for: logging, notifications, optional enrichment, async cleanup

```json
{
  "drops": {
    "D1.1": { "name": "Core work", "wave": "W1", "blocking": true },
    "D1.2": { "name": "Send notification", "wave": "W1", "blocking": false }
  }
}
```

Wave 2 can start once D1.1 completes, even if D1.2 is still running.

**STATUS.md** explicitly surfaces non-blocking Drops so nothing is silently left behind.

## meta.json Structure (v3)

```json
{
  "schema_version": 3,
  "slug": "my-build",
  "title": "Build Title",
  "build_type": "code_build",
  "status": "pending",
  "model": "inherit",
  "max_total_spawns": 0,
  "launch_mode": "orchestrated|manual|jettison",
  "delegate_only": false,
  "first_wins": false,
  "hypothesis_group": [],
  "broadcasts": [],
  "task_pool": {
    "enabled": false,
    "tasks": [],
    "max_concurrent_claims": 4,
    "worker_drops": []
  },
  
  "waves": {
    "W1": ["D1.1", "D1.2", "D2.1"],
    "W2": ["D1.3", "D2.2"]
  },
  "active_wave": "W1",
  
  "drops": {
    "D1.1": {
      "name": "Task name",
      "stream": 1,
      "order": 1,
      "depends_on": [],
      "spawn_mode": "auto",
      "blocking": true,
      "status": "pending"
    },
    "D1.2": {
      "name": "Voice-sensitive task",
      "stream": 1,
      "order": 2,
      "spawn_mode": "manual",
      "blocking": true,
      "status": "pending"
    }
  },
  
  "lineage": {
    "parent_type": "build|jettison|conversation|null",
    "parent_ref": "slug or convo_id",
    "parent_conversation": "convo_id",
    "moment": "description",
    "branched_at": "ISO timestamp"
  }
}
```

### Legacy Compatibility

Builds with `currents` or `current_stream`/`total_streams` (schema v1/v2) still work:
- Pulse normalizes them in-memory
- No migration required for old builds
- New builds should use `waves` schema

## Build Folder Structure

```
N5/builds/<slug>/
├── meta.json           # Build state (status, drops, waves)
├── STATUS.md           # Human-readable progress dashboard
├── BUILD_LESSONS.json  # Build-specific learnings
├── INTEGRATION_TESTS.json  # Test definitions
├── INTEGRATION_RESULTS.json  # Test results
├── FINALIZATION.json   # Post-build report
├── drops/              # Drop briefs
│   ├── D1.1-task-a.md
│   ├── D1.2-voice-task.md
│   └── D2.1-combine.md
├── deposits/           # Completion reports
│   ├── D1.1.json
│   ├── D1.1_filter.json
│   └── D1.1_forensics.json  (if dead)
├── launchers/          # Manual drop launchers (auto-generated)
│   └── D1.2.md
├── holdout_scenarios/  # Hidden acceptance scenarios (not visible to workers)
│   └── D1.1_holdouts.yaml
├── context/            # Pyramid summary context files (for large builds)
│   ├── overview.md
│   └── D1.1-context.md
└── artifacts/          # Build outputs
```

## Jettison Launch Mode

Jettisons are **off-ramp builds** — when you hit a tangent worth pursuing without derailing your current thread.

Jettison is not automatically a Git branch. Use the existing conversation workspace or `N5/builds/<slug>/` for exploratory work by default. Create a Git branch only when the jettison will change shared source, runtime behavior, `Sites/`, deployed skills, schema/data contracts, public/canonical outputs, or another risky surface that needs isolated review.

Before creating or switching a branch/worktree for Pulse or jettison work, run:

```bash
python3 N5/scripts/n5_git_context_check.py --intent "<build or jettison intent>"
```

Respect the disposition: `main-ok` stays on `main`, `branch-required` uses a scoped feature branch, `worktree-required` uses a separate worktree, and `blocked` pauses until dirty state is classified.

### When to Use

- Debugging issue surfaces mid-build that needs isolated investigation
- Interesting idea emerges that deserves its own exploration
- Current task has a prerequisite that should be handled separately
- You want to branch off without losing the parent context

### Command Syntax

```bash
# Basic jettison
pulse jettison "fix the rate limiting issue"

# Explicit parent build
pulse jettison "debug the API" --from adhd-todo-research

# Explicit type (overrides auto-detection)
pulse jettison "explore gamification approaches" --type research

# Custom moment description
pulse jettison "handle auth edge case" --moment "Discovered during D1.2 execution"
```

### Type Auto-Detection

| Keywords | Detected Type |
|----------|---------------|
| fix, bug, debug, error, refactor | `code_build` |
| research, explore, investigate, analyze | `research` |
| draft, write, content, blog, email | `content` |
| plan, design, architect, strategy | `planning` |
| (default) | `code_build` |

## Tick Runner (No Sentinel Dependency)

Pulse does not require a Sentinel agent. Orchestration runs directly via `start`, `tick`, and `status`.

### Recommended Operation

```bash
# Start one build
python3 Skills/pulse/scripts/pulse.py start <slug>

# Run periodic ticks from scheduler/cron if desired
python3 Skills/pulse/scripts/pulse.py tick <slug>

# Inspect progress
python3 Skills/pulse/scripts/pulse.py status <slug>
```

### Optional Scheduler Pattern

If you want unattended progression, schedule:

```bash
python3 Skills/pulse/scripts/pulse.py tick <slug>
```

every 3-5 minutes using your own scheduler.

**Read before scheduling.** A scheduled tick is itself a billed agent session,
and every Drop it spawns is another full session. Before handing a build to a
recurring automation:

1. Tick the first wave manually and watch it complete cleanly.
2. Confirm the build's model policy (see *Model and Spend Policy*).
3. Check your Zo billing balance; do not launch multi-hour builds near $0.
4. Make the automation's instruction stop itself when `pulse.py status <slug>`
   reports `blocked`, `stopped`, or `complete`. Pulse will refuse to spawn in
   those states, but the automation session itself still costs money each time
   it fires.

### Model and Spend Policy

- **No hardcoded model.** Drops inherit the workspace's default model unless
  `meta.json["model"]` or the `ZO_ASK_MODEL_NAME` env var sets an explicit
  override. `"inherit"` (or omitting the key) means "use whatever the workspace
  default is." Provider connection ids (`byok:...`) are workspace-specific and
  must never be committed to shared code.
- **No silent fallback.** If an explicit model fails, the Drop fails. Pulse no
  longer re-issues the same prompt on a different model.
- **Concurrency cap.** `/zo/ask` allows 5 concurrent sessions per workspace.
  Pulse spawns at most `PULSE_MAX_CONCURRENT_SPAWNS` (default 3) Drops at once
  and defers the rest to later ticks instead of firing a whole wave into 429s.
- **Total spawn ceiling.** A build may spawn at most
  `meta.max_total_spawns` (or `PULSE_MAX_TOTAL_SPAWNS`; default
  `3 x number of drops`) sessions in its lifetime, including retries. Hitting
  the ceiling blocks the build.
- **Non-retryable failures block immediately.** HTTP 402 (out of credits),
  401/403 (auth), and missing model config set the build to `blocked`. Ticks
  then no-op until you run `pulse.py resume <slug>`.

### Recovery Behavior

Pulse recovery is handled inline in the tick loop (`assess_and_recover`):

- **R0** non-retryable (402/401/403/model config) → build `blocked`, no retry
- **R1** dead (timeout) → auto-retry while `retry_count < max_auto_retries` (default 2)
- **R2** transient spawn error (429, 5xx, connection) → auto-retry under the same cap
- **R3** content/logic error → escalate for judgment
- **R4** whole wave dead with retries exhausted → build `blocked`
- **R5** stale build → escalate
- retries are subject to the concurrency cap and total spawn ceiling above
- actions are logged to `N5/builds/<slug>/RECOVERY_LOG.jsonl`

`pulse.py resume <slug>` clears a `blocked` state after you fix the cause.

## Learnings System

Two tiers:
1. **Build-local** → `N5/builds/<slug>/BUILD_LESSONS.json`
2. **System-wide** → `N5/learnings/SYSTEM_LEARNINGS.json`

```bash
# Add build learning
python3 Skills/pulse/scripts/pulse_learnings.py add <slug> "lesson text"

# Add system learning
python3 Skills/pulse/scripts/pulse_learnings.py add <slug> "lesson text" --system

# List learnings
python3 Skills/pulse/scripts/pulse_learnings.py list <slug>
python3 Skills/pulse/scripts/pulse_learnings.py list-system

# Promote build learning to system
python3 Skills/pulse/scripts/pulse_learnings.py promote <slug> <index>

# Inject system learnings into briefs
python3 Skills/pulse/scripts/pulse_learnings.py inject <slug>

# Harvest learnings from deposits
python3 Skills/pulse/scripts/pulse_learnings.py harvest <slug>
```

## Forward Broadcast

Drops can share findings with subsequent Drops via the `broadcast` field in deposits.

### How It Works

1. Drop includes `broadcast` string in deposit JSON
2. Pulse collects all broadcasts from completed Drops
3. New Drops receive a "## Broadcasts from Prior Drops" section in their brief

### Deposit Schema

```json
{
  "drop_id": "D1.1",
  "status": "complete",
  "broadcast": "Auth tokens expire after 30 min—don't cache beyond that",
  ...
}
```

### Injected Format

```markdown
## Broadcasts from Prior Drops

These findings were shared by earlier Drops in this build:

- **D1.1:** Auth tokens expire after 30 min—don't cache beyond that
```

### Best Practices

- Keep broadcasts short (~500 chars max)
- Broadcast discoveries that affect other Drops
- Don't broadcast obvious things already in briefs

## Hypothesis Racing

For debugging or exploration builds where you want to test multiple theories in parallel.

### Enabling

In `meta.json`:

```json
{
  "first_wins": true,
  "hypothesis_group": ["D1.1", "D1.2", "D1.3"]  // optional
}
```

### Verdict Field

Racing Drops include `verdict` in their deposit:

```json
{
  "drop_id": "D1.2",
  "status": "complete",
  "verdict": "confirmed",
  "summary": "Theory confirmed: rate limit is client-side"
}
```

Valid verdicts: `confirmed`, `rejected`, `inconclusive`

### Behavior

- When a Drop deposits `verdict: "confirmed"`, other Drops in the race are marked `superseded`
- Superseded Drops are not spawned (if pending) or ignored (if running)
- Wave can advance once winner confirms — superseded Drops don't block

### Use Cases

- Debugging with multiple theories
- A/B testing approaches
- Finding the first working solution among alternatives

## Delegate-Only Mode

Prevents the orchestrator from directly editing code, keeping all work in Drops.

### Enabling

In `meta.json`:

```json
{
  "delegate_only": true
}
```

### Constraints

When enabled, the orchestrator:
- **MAY**: Run pulse.py commands, read files, create/modify briefs, retry Drops
- **MUST NOT**: Edit source files, run application code, "fix" issues directly

### Why Use It

- Clear provenance (every change has a Drop source)
- Prevents long-build confusion
- Better audit trail

See `file 'Skills/pulse/references/delegate-only-mode.md'` for full details.

## Task Pool (Dynamic Claiming)

For builds with many similar tasks, Drops can claim work from a shared pool.

### Enabling

In `meta.json`:

```json
{
  "task_pool": {
    "enabled": true,
    "tasks": [
      {"id": "T001", "type": "enrich", "target": "file1.json", "status": "pending"},
      {"id": "T002", "type": "enrich", "target": "file2.json", "status": "pending"}
    ],
    "max_concurrent_claims": 4,
    "worker_drops": ["D1.1", "D1.2", "D1.3", "D1.4"]
  }
}
```

### Task States

- `pending` — Available for claiming
- `claimed` — Assigned to a Drop
- `complete` — Finished successfully
- `failed` — Failed, may be re-claimable

### Claiming

Pool workers claim tasks atomically (file-locked to prevent races):

```python
task = claim_task(slug, drop_id)
if task is None:
    # Pool exhausted, exit
```

### Use Cases

- Processing batches of similar items
- Parallelizing uniform work without pre-planning assignments
- Variable-duration tasks where fast Drops should grab more work

## Integration Tests

```bash
# Generate tests from artifacts
python3 Skills/pulse/scripts/pulse_integration_test.py generate <slug>

# Run tests
python3 Skills/pulse/scripts/pulse_integration_test.py run <slug>

# Add custom test
python3 Skills/pulse/scripts/pulse_integration_test.py add <slug> \
  --type file_exists \
  --name "Check output" \
  --config '{"path": "Sites/mysite/dist/index.html"}'
```

Test types: `file_exists`, `file_contains`, `command`, `http`, `service_running`

## Safety Layer

```bash
# Pre-build checks
python3 Skills/pulse/scripts/pulse_safety.py pre-check <slug>

# Verify artifacts after build
python3 Skills/pulse/scripts/pulse_safety.py verify <slug>

# Create git snapshot
python3 Skills/pulse/scripts/pulse_safety.py snapshot <slug>

# Restore from snapshot
python3 Skills/pulse/scripts/pulse_safety.py restore <slug>
```

## Scripts

| Script | Purpose |
|--------|---------|
| `pulse.py` | Main orchestrator (start, tick, stop, finalize, launch) |
| `pulse_common.py` | Shared paths, config, parsing utilities |
| `pulse_safety.py` | Pre-build checks, artifact verification, snapshots |
| `pulse_learnings.py` | Capture/propagate learnings (build + system) |
| `pulse_integration_test.py` | Post-build integration tests |

## Related Files

- `file 'Skills/spec-writing/SKILL.md'` — Scenario extraction subroutine for Pulse planning, not a separate build workflow
- `file 'Skills/spec-writing/references/scenario-patterns.md'` — Common scenario patterns by build type
- `file 'Skills/pulse/references/holdout-scenarios-template.md'` — Holdout scenario convention
- `file 'Skills/pulse/references/pyramid-summary-template.md'` — Multi-resolution context files
- `N5/learnings/SYSTEM_LEARNINGS.json` — Optional system-wide learnings file, created by the learning commands when needed
- `Documents/System/` — Optional local system manuals and maintainer playbooks

## Learning-Engaged Build Mode

When `build_mode: "learning"` in meta.json (the default):

### Orchestrator Responsibilities

1. **Generate Learning Landscape** — During planning, read `N5/config/understanding_bank.json` and analyze plan concepts against V's levels. Flag Decision Points and tag Drops.

2. **Present Decision Points** — Before launching Drops that involve flagged decisions:
   - Present the question in plain language
   - Offer 2-3 options with tradeoffs explained at V's level
   - Include a recommendation with reasoning
   - Support multi-round Socratic dialogue if V wants to explore
   - Log resolved decisions to `DECISIONS.md` in the build folder

3. **Spawn Learning Drops** — When V says "I want to deep dive into X":
   - Create an L-prefix Drop brief using `references/learning-drop-template.md`
   - The Learning Drop is always manual spawn
   - It never blocks the build — other Drops continue
   - When V completes the Learning Drop, integrate conclusions into subsequent briefs

4. **Generate Wave Reviews** — At wave boundaries:
   - Summarize what was accomplished
   - List concepts V was exposed to
   - Ask ONE Socratic question testing the most important concept
   - V can opt to deep dive (spawns Learning Drop) or continue

5. **Default Manual Spawn** — Pedagogical Drops use `spawn_mode: manual`. V opens them in new threads. Mechanical Drops (tagged in Learning Landscape) can be auto-spawned with V's approval.

### Rush Mode Override

V can override learning mode at any scope:
- **Per-Drop:** "Run D1.2 headless"
- **Per-Wave:** "Auto-spawn wave 2"
- **Per-Build:** `build_mode: "rush"` in meta.json, or V says "rush mode"

Rush mode reverts to Pulse v2 behavior: auto-spawn, no Decision Points, no Wave Reviews.

### Understanding Bank Integration

- **Read at plan time:** Architect reads `N5/config/understanding_bank.json` to calibrate Learning Landscape
- **Update at build close:** Pedagogical AAR updates concept levels based on V's demonstrated understanding
- **Updated by Learning Drops:** L-prefix deposits include `understanding_update` assessments
