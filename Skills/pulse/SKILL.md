---
name: pulse
description: |
  Automated build orchestration system. Spawns headless Zo workers (Drops) in parallel Streams,
  monitors health, validates Deposits via LLM judgment, handles dead Drops, and escalates via SMS.
  Supports sequential Currents within Streams. Replaces manual Build Orchestrator for unattended execution.
---

# Pulse: Automated Build Orchestration

## Overview

Pulse orchestrates complex builds by:
1. **Spawning Drops** (workers) via `/zo/ask` API
2. **Monitoring** for deposits, timeouts, failures
3. **Filtering** deposits via LLM judgment
4. **Checkpoint verification** at strategic quality gates
5. **Escalating** via email/SMS when issues arise
6. **Finalizing** with safety checks, integration tests, and learning harvest

## Terminology (Flow Metaphor)

| Term | Meaning |
|------|---------|
| **Build** | The complete orchestrated work |
| **Stream** | Parallel execution batch (like Wave) |
| **Drop** | Individual worker/task (synonym: Worker) |
| **Current** | Sequential chain within a Stream |
| **Checkpoint** | Strategic quality gate verifying cross-Drop consistency |
| **Deposit** | Worker's completion report |
| **Filter** | LLM judgment of deposit quality |
| **Dredge** | Forensics worker for dead Drops |
| **Jettison** | Connected-but-independent build spawned as tangent off-ramp |
| **Lineage** | Parent-child relationship graph between builds |
| **Launch Mode** | How a build was spawned: orchestrated, manual, or jettison |

## Quick Start

```bash
# Check build status
python3 Skills/pulse/scripts/pulse.py status <slug>

# Start automated orchestration
python3 Skills/pulse/scripts/pulse.py start <slug>

# Manual tick (for testing)
python3 Skills/pulse/scripts/pulse.py tick <slug>

# Stop gracefully
python3 Skills/pulse/scripts/pulse.py stop <slug>

# Resume stopped build
python3 Skills/pulse/scripts/pulse.py resume <slug>

# Post-build finalization
python3 Skills/pulse/scripts/pulse.py finalize <slug>

# Create jettison (off-ramp build)
pulse jettison "<task>" [--from <parent>] [--type <type>]

# View build lineage DAG
pulse lineage [<slug>] [--format tree|json]
```

## Jettison Launch Mode

Jettisons are **off-ramp builds** — when you hit a tangent worth pursuing without derailing your current thread.

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

Jettison auto-detects build type from keywords:

| Keywords | Detected Type |
|----------|---------------|
| fix, bug, debug, error, refactor | `code_build` |
| research, explore, investigate, analyze | `research` |
| draft, write, content, blog, email | `content` |
| plan, design, architect, strategy | `planning` |
| (default) | `code_build` |

### Output

```
╔══════════════════════════════════════════════════════════════╗
║  JETTISON CREATED                                            ║
╚══════════════════════════════════════════════════════════════╝

Build:  j-fix-rate-limit-0126-0410
Type:   code_build
Folder: N5/builds/j-fix-rate-limit-0126-0410/

Launch prompt (copy to new thread):
────────────────────────────────────────────────────────────────
Load and execute: file 'N5/builds/j-fix-rate-limit-0126-0410/drops/D1.1-jettison-task.md'
────────────────────────────────────────────────────────────────
```

### Jettison Workflow

1. **Trigger**: You're in a conversation, hit a tangent
2. **Create**: Run `pulse jettison "<task>"` 
3. **Launch**: Copy the launch prompt to a new thread
4. **Execute**: The new thread loads the brief and executes
5. **Complete**: Worker writes deposit to jettison's own folder
6. **Notify**: Email sent on completion

### Jettison vs Regular Build

| Aspect | Regular Build | Jettison |
|--------|---------------|----------|
| Launch mode | Orchestrated (Pulse spawns) | Manual (you copy-paste) |
| Folder | `N5/builds/<slug>/` | `N5/builds/j-<slug>/` |
| Parent tracking | Optional | Always tracked (lineage) |
| Learnings | Build-specific | Inherits from parent |
| Worker count | Multiple (streams) | Single (D1.1 only) |

## Lineage Tracking

Builds can have parent-child relationships, forming a DAG (directed acyclic graph).

### Lineage Schema

Every build's `meta.json` can include:

```json
{
  "lineage": {
    "parent_type": "build",           // build, jettison, conversation, or null
    "parent_ref": "adhd-todo-research", // slug or convo_id
    "parent_conversation": "con_xyz",   // where jettison was triggered
    "moment": "D1.2 hit rate limits",   // what triggered this
    "branched_at": "2026-01-25T23:00:00Z"
  }
}
```

### Visualizing Lineage

```bash
# Show full lineage DAG
pulse lineage

# Show specific build's ancestry and descendants
pulse lineage adhd-todo-research

# JSON output for scripting
pulse lineage --format json
```

### Example Output

```
Build Lineage
========================================

adhd-todo-research [R] ✓
├── j-ratelimit-debug ⚡ ●
│   └── j-api-redesign [P]⚡ ○
└── j-gamification-tangent [R]⚡ ✓

pulse-variants ✓

Legend: ✓ complete  ● running  ○ pending  ✗ failed  ⚡ jettison
Types: [R] research  [C] content  [P] planning
```

### Learnings Inheritance

When a jettison is created from a parent build:
1. Parent's `BUILD_LESSONS.json` is copied to jettison
2. Lessons are marked with "inherited from: <parent>"
3. Jettison can add its own lessons
4. Learnings do NOT flow back to parent (one-way branch)

## Sentinel Setup

Pulse requires a **Sentinel** scheduled agent to monitor builds and report via email (preferred) or SMS.

### Email Sentinel (Recommended)

Email provides richer updates and allows detailed replies.

**Create Email Sentinel at build start:**
```
RRULE: FREQ=MINUTELY;INTERVAL=5;COUNT=100
Delivery: email

Instruction:
Pulse Sentinel for build: <slug>

1. Run: python3 Skills/pulse/scripts/pulse.py status <slug> --json
2. Parse the status and compose an email update.

EMAIL FORMAT:
Subject: [PULSE] <slug> - <status_summary>

Body:
## Build: <slug>
**Status:** <stream X of Y> | **Progress:** <completed>/<total> Drops (<pct>%)

### Stream Status
| Stream | Status | Drops |
|--------|--------|-------|
| S1 | complete | D1.1 ✓, D1.2 ✓ |
| S2 | running | D2.1 ✓, D2.2 ⏳ (8 min) |
| S3 | pending | - |

### Recent Activity (since last email)
- D2.1 completed: "Implemented webhook handler" 
- D2.2 started 8 minutes ago

### Concerns
- ⚠️ D2.2 running >15 min → may be stuck
- ⚠️ D1.2 deposit has WARN: "Consider extracting to skill"

### Reply Commands
Reply to this email with any of:
- `status` — Get detailed status
- `retry D2.2` — Retry a stuck/failed Drop
- `skip D2.2` — Skip a Drop and continue
- `pause` — Pause the build
- `resume` — Resume paused build
- `stop` — Stop the build entirely
- `<other instructions>` — Free-form guidance

---
Build folder: N5/builds/<slug>/
Orchestrator: <conversation_id>

3. ONLY send email if:
   - New completions since last check
   - Drop running >15 min (potential dead drop)
   - Build complete
   - Stream advanced
   - Any FAIL verdict from Filter
   
4. If build complete: Send final summary email, then delete yourself.

5. If no meaningful changes, stay silent (don't spam).
```

### SMS Sentinel (Fallback)

Use SMS for brief, urgent alerts when email isn't being checked.

```
RRULE: FREQ=MINUTELY;INTERVAL=3;COUNT=120
Delivery: sms

Instruction:
Pulse SMS Sentinel for build: <slug>

1. Run: python3 Skills/pulse/scripts/pulse.py status <slug>
2. ONLY text if:
   - Drop FAILED → "[PULSE] ❌ D#.# FAILED: <reason>. Reply 'retry' or 'skip'"
   - Drop dead (>15 min) → "[PULSE] ⚠️ D#.# may be dead. Reply 'retry' or 'skip'"
   - Build complete → "[PULSE] ✅ <slug> COMPLETE"
3. For routine progress, stay silent (email handles that).
```

### Dual Sentinel (Email + SMS)

For critical builds, run both:
- Email Sentinel: Every 5 min, detailed updates
- SMS Sentinel: Every 3 min, urgent alerts only (failures, dead drops)

### Email Reply Processing

When V replies to a Sentinel email, the reply is processed as a conversation with Zo. The Sentinel instruction should include:

```
If this is a reply to a previous Sentinel email, parse the command:
- "status" → Run full status and reply
- "retry D#.#" → Mark drop for retry, run: python3 Skills/pulse/scripts/pulse.py retry <slug> D#.#
- "skip D#.#" → Skip drop: python3 Skills/pulse/scripts/pulse.py skip <slug> D#.#
- "pause" → python3 Skills/pulse/scripts/pulse.py pause <slug>
- "resume" → python3 Skills/pulse/scripts/pulse.py resume <slug>
- "stop" → python3 Skills/pulse/scripts/pulse.py stop <slug>
- Free-form text → Log as guidance to N5/builds/<slug>/guidance.md and acknowledge
```

### Delete Sentinel When Done

After build completes, the Sentinel should delete itself. If it doesn't, manually delete via:
- SMS: `pulse done` or `pulse stop`
- Chat: Delete the scheduled agent

**Note:** Sentinel creation requires the Zo agent API (create_agent tool), which is only available in interactive/scheduled contexts — not from Python scripts. The LLM orchestrating the build must create the Sentinel.

## Pulse v2 Features

### Task Queue
- Multi-channel intake: `n5 task <description>` via SMS, email "Task: X", or chat
- Task types: code_build, research, content, analysis, hybrid
- Commands: `python3 N5/pulse/queue_manager.py add|list|prioritize|advance|next`

### Interview System
- Fragment-based async collection
- Multi-channel aggregation (SMS + email + chat)
- JSONL storage: `N5/pulse/interviews/<task-id>/fragments.jsonl`
- Seeded judgment with LLM evaluation
- Commands: `python3 N5/pulse/interview_manager.py start|add|status|seed`

### Plan Review
- Auto-sync to Google Drive: `Zo/Pulse Builds/<slug>/`
- SMS notification with shareable link
- Approval flow: "go" to build, "revise: X" for feedback
- Commands: `python3 N5/pulse/plan_sync.py sync|notify|approve`

### Tidying Swarm
- 5 hygiene Drops post-build:
  - Artifact verification
  - Dead code detection
  - Import cleanup
  - Documentation gaps
  - Test coverage check
- Auto-fix for safe issues
- Escalation for ambiguous findings

### Telemetry
- Persona + model attribution on all events
- Requirements tracking during builds
- Feedback → learnings pipeline
- Commands: `python3 N5/pulse/telemetry_manager.py log|query|export`
- Requirements: `python3 N5/pulse/requirements_tracker.py capture|list|export`

## Pulse v3 Features (Lifecycle Automation)

### Automated Lifecycle
Pulse v3 automates the entire pre-build pipeline:

```
queued → interviewing → seeded → planning → plan_review → building → tidying → complete
```

The **Lifecycle Agent** polls every 5 minutes and advances tasks automatically:

| From State | To State | Trigger |
|------------|----------|---------|
| queued | interviewing | Automatic on task creation |
| interviewing | seeded | Seeded judgment confidence ≥ 0.8 |
| seeded | planning | Plan generated |
| planning | plan_review | V available (respects calendar/quiet hours) |
| approved | building | Automatic |

### Lifecycle Commands

```bash
# Start lifecycle automation
python3 Skills/pulse/scripts/pulse.py lifecycle start

# Stop lifecycle automation  
python3 Skills/pulse/scripts/pulse.py lifecycle stop

# Check lifecycle status
python3 Skills/pulse/scripts/pulse.py lifecycle status

# Manual single tick (useful for testing)
python3 Skills/pulse/scripts/pulse.py lifecycle tick
python3 Skills/pulse/scripts/pulse.py lifecycle tick --dry-run
```

### Fragment Tagging

Tag SMS responses to route to specific interviews:

```
#task-my-build This is my response about the feature requirements
```

If you have one open interview, responses auto-route. With multiple open interviews, you'll be prompted to use a tag.

### Auto-Fix Dispatch

Tidying findings with confidence ≥ 0.9 auto-fix. Lower confidence findings escalate for manual review.

Configure in `pulse_v2_config.json`:
```json
{
  "auto_fix": {
    "enabled": true,
    "confidence_threshold": 0.9
  }
}
```

### Availability-Aware Reviews

HITL plan reviews respect V's availability:
- Checks Google Calendar for meetings
- Respects quiet hours (configurable, default 10pm-7am ET)
- Looks for `[DW]` (Deep Work) markers in calendar events
- Defers review until next available window

Force review regardless of availability:
```bash
python3 N5/pulse/review_manager.py initiate my-build --force
```

## v2 Lifecycle

```
pending → interviewing → seeded → planning → plan_review → building → tidying → complete
```

### Stage Transitions

| From | To | Trigger |
|------|----|---------|
| pending | interviewing | Task intake via any channel |
| interviewing | seeded | LLM judges ≥0.8 confidence |
| seeded | planning | `pulse.py plan <task>` |
| planning | plan_review | `plan_sync.py sync <slug>` |
| plan_review | building | V responds "go" |
| building | tidying | All Drops complete |
| tidying | complete | Health score ≥0.9 or V approves |

### v2 Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INTAKE (multi-channel)                                   │
│    - SMS: "n5 task <description>"                           │
│    - Email: Subject starts with "Task:"                     │
│    - Chat: Direct request                                   │
│    → Creates task in queue_manager.py                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. INTERVIEW (async, fragment-based)                        │
│    - Zo asks clarifying questions via same channel          │
│    - Fragments stored in interviews/<task-id>/              │
│    - LLM evaluates completeness (seeded judgment)           │
│    - Exits when confidence ≥0.8                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PLANNING (Architect creates PLAN.md)                     │
│    - Decompose into Streams/Drops                           │
│    - Generate meta.json + drop briefs                       │
│    - MECE validation on worker scopes                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. PLAN REVIEW (human-in-the-loop)                          │
│    - Sync to Google Drive: Zo/Pulse Builds/<slug>/          │
│    - SMS V with review link                                 │
│    - Wait for "go" or "revise: <feedback>"                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. BUILD (automated orchestration)                          │
│    - Create git snapshot (safety)                           │
│    - Inject system learnings into briefs                    │
│    - Spawn Drops via /zo/ask                                │
│    - Tick loop: monitor, filter, escalate                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. TIDYING (automated hygiene)                              │
│    - Spawn 5 tidying Drops                                  │
│    - Auto-fix safe issues                                   │
│    - Escalate ambiguous findings                            │
│    - Calculate health score                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. FINALIZE                                                 │
│    - Verify all artifacts exist                             │
│    - Run integration tests                                  │
│    - Harvest learnings from deposits                        │
│    - SMS: Finalization result                               │
└─────────────────────────────────────────────────────────────┘
```

## Build Folder Structure

```
N5/builds/<slug>/
├── meta.json           # Build state (status, drops, streams)
├── STATUS.md           # Human-readable progress dashboard
├── BUILD_LESSONS.json  # Build-specific learnings
├── INTEGRATION_TESTS.json  # Test definitions
├── INTEGRATION_RESULTS.json  # Test results
├── FINALIZATION.json   # Post-build report
├── drops/              # Drop briefs (D1.1-name.md)
│   ├── D1.1-task-a.md
│   ├── D1.2-task-b.md
│   └── D2.1-combine.md
├── deposits/           # Completion reports
│   ├── D1.1.json
│   ├── D1.1_filter.json
│   └── D1.1_forensics.json  (if dead)
└── artifacts/          # Build outputs
```

## Scripts

| Script | Purpose |
|--------|---------|
| `pulse.py` | Main orchestrator (start, tick, stop, finalize) |
| `sentinel.py` | Lightweight monitor for scheduled polling |
| `pulse_safety.py` | Pre-build checks, artifact verification, snapshots |
| `pulse_learnings.py` | Capture/propagate learnings (build + system) |
| `pulse_integration_test.py` | Post-build integration tests |

### v2 Scripts (in N5/pulse/)

| Script | Purpose |
|--------|---------|
| `queue_manager.py` | Task queue CRUD operations |
| `interview_manager.py` | Async interview orchestration |
| `plan_sync.py` | Google Drive sync + approval flow |
| `sms_intake.py` | SMS command routing |
| `telemetry_manager.py` | Event logging with attribution |
| `requirements_tracker.py` | Capture V's requirements/preferences |

## SMS Commands

Text these to control Pulse:
- `pulse stop` — Stop all builds, delete Sentinel
- `pulse done` — Mark builds complete, delete Sentinel
- `pulse pause` — Pause ticking (agent stays alive)
- `pulse resume` — Resume ticking
- `n5 task <description>` — Add task to queue (v2)

## meta.json Structure

```json
{
  "slug": "my-build",
  "title": "Build Title",
  "build_type": "code_build",
  "status": "pending",
  "total_streams": 2,
  "current_stream": 1,
  "model": "anthropic:claude-sonnet-4-20250514",
  "launch_mode": "orchestrated|manual|jettison",
  "lineage": {
    "parent_type": "build|jettison|conversation|null",
    "parent_ref": "slug or convo_id",
    "parent_conversation": "convo_id",
    "moment": "description",
    "branched_at": "ISO timestamp"
  },
  "drops": {
    "D1.1": {
      "name": "Task name",
      "stream": 1,
      "depends_on": [],
      "spawn_mode": "auto",
      "status": "pending"
    }
  },
  "currents": {}
}
```

### spawn_mode Options

| Mode | Behavior | Use When |
|------|----------|----------|
| `auto` (default) | Pulse spawns via `/zo/ask` headless | Most Drops - standard automated execution |
| `manual` | Pulse marks as "awaiting_manual", V pastes brief into new thread | High-risk work, requires human judgment, complex debugging |

When a Drop has `spawn_mode: "manual"`:
1. Pulse prints `[SPAWN] D1.1 is waiting for manual spawn`
2. Status changes to `awaiting_manual`
3. V opens new thread, pastes brief, executes
4. V writes deposit manually
5. Next tick detects deposit, runs Filter

**Mix and match:** Some Drops auto, some manual. Useful for builds where setup is automated but core logic needs human oversight.

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

## Related Files

- `file 'Skills/pulse-interview/SKILL.md'` — Pre-build interview skill
- `file 'N5/learnings/SYSTEM_LEARNINGS.json'` — System-wide learnings
- `file 'N5/config/pulse_control.json'` — Sentinel control state
- `file 'Documents/System/Build-Orchestrator-System.md'` — Legacy manual system
- `file 'N5/pulse/'` — v2 scripts directory
