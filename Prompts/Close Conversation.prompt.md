---
title: Close Conversation
description: |
  Unified conversation close - auto-detects mode (Worker vs Full) and tier.
  Workers do partial close (handoff to orchestrator). Full close includes commits.
tool: true
tags:
  - session
  - cleanup
  - conversation
  - positions
created: 2025-10-15
last_edited: 2026-01-18
version: 5.3
provenance: con_acsL39swzoCxrfWs
---

# Close Conversation

Runs the formal **conversation-end workflow** with automatic mode and tier detection.

## Two Modes

| Mode | Detection | Purpose | Commits? |
|------|-----------|---------|----------|
| **Worker Close** | `build_id` + `worker_num` in SESSION_STATE frontmatter | Package work for orchestrator review | ❌ NO |
| **Full Close** | Normal thread OR orchestrator | Complete close with finalization | ✅ YES |

## Core Principles

- Scripts handle mechanics (file lists, git status, raw content)
- LLM (Librarian) handles ALL semantic work (summaries, AARs, decisions, title)
- Title generation is semantic (3-slot emoji system: State | Type | Content)
- **Workers defer commits** to orchestrator - their job is clean handoff

---

## Step 0: Detect Mode

Check SESSION_STATE.md frontmatter for build context:

**V2 Build System (preferred):**
```yaml
worker_id: W1.1              # V2 worker identifier
build_slug: my-project       # Build folder name
thread_title: "[my-project] W1.1: Task Name"  # Pre-decided title
```

**Legacy format:**
```yaml
build_id: my-project       # If present → Worker Close
worker_num: 1              # Worker number
parent_topic: My Project   # For greppable tags
```

**Detection priority:**
1. `worker_id` + `build_slug` in SESSION_STATE frontmatter → Worker Close (v2)
2. `build_id` + `worker_num` in SESSION_STATE frontmatter → Worker Close (legacy)
3. `## Build Context` section in SESSION_STATE → Worker Close  
4. `mode: worker` in SESSION_STATE frontmatter → Worker Close
5. Otherwise → Full Close mode

**If Worker Close mode → Follow Worker Steps below**
**Otherwise → Follow Full Close mode**

---

# WORKER CLOSE MODE

For threads spawned by an orchestrator. Goal: **clean handoff**, not finalization.

## Worker Step 1: Verify Deliverables

Check all work products exist and are in correct locations:
- Files created? In the right paths?
- Any artifacts promised but not delivered?
- Any loose ends or caveats?

## Worker Step 2: Generate Post-Close Title

**Two-phase title system:**
- **Pre-decided title** (from worker brief): Used by V to rename thread immediately after opening
- **Post-close title** (generated now): Adds 3-slot emoji prefix based on what actually happened

**3-Slot Emoji System (from `N5/config/emoji-legend.json`):**
- **Slot 1 (State):** ✅ complete | ❌ failed | 🚧 in_progress | ⏸️ paused
- **Slot 2 (Type):** 👷🏽‍♂️ worker (always for workers)
- **Slot 3 (Content):** 🏗️ build | 🛠️ repair | 🔎 research | etc. (based on work done)

**Generation Process:**

1. **Get base title** from SESSION_STATE frontmatter `thread_title`
   - If missing, construct: `[{build_slug}] W{worker_id}: {task_name}`

2. **Determine State emoji** from completion status:
   - All deliverables complete, no blockers → ✅
   - Completed with caveats or partial → 🚧
   - Blocked, cannot proceed → ⏸️
   - Failed with errors → ❌

3. **Type emoji** is always 👷🏽‍♂️ (worker)

4. **Determine Content emoji** semantically from work done:
   - Built features/systems → 🏗️
   - Fixed bugs/debugged → 🛠️
   - Research/investigation → 🔎
   - Site/web work → 🕸️
   - Content writing → ✍️
   - Data/analytics → 📊
   - Organization/cleanup → 🗂️
   - Planning/design → 📝

5. **Compose final title:**
   ```
   {state} {type} {content} {base_title}
   ```

**Example:**
- Pre-decided (from brief): `[build-orchestrator-v2] W3.1: Build Status Script`
- Post-close (generated): `✅ 👷🏽‍♂️ 🏗️ [build-orchestrator-v2] W3.1: Build Status Script`

**Output format:**
```markdown
## Worker Close Complete

**Thread Title:** `✅ 👷🏽‍♂️ 🏗️ [build-orchestrator-v2] W3.1: Build Status Script`

**Summary:** [1-2 sentence summary of what was accomplished]
```

## Worker Step 3: Write Handoff Summary

Create a clear handoff package for the orchestrator to review:

```markdown
## Worker Handoff: [Task Name]

**Parent:** con_XXXXX (orchestrator)
**Status:** ✅ Complete | ⚠️ Partial | ❌ Blocked

### What Was Done
- [Specific accomplishments with file paths]

### Artifacts Created
- `file 'path/to/artifact1.py'` — [purpose]
- `file 'path/to/artifact2.md'` — [purpose]

### Caveats / Notes for Orchestrator
- [Anything the orchestrator should know]
- [Decisions made, assumptions, edge cases]

### Ready for Commit
- [ ] [List of files ready for git commit]
```

## Worker Step 4: Update SESSION_STATE

```bash
python3 N5/scripts/session_state_manager.py update --convo-id {CONVO_ID} \
  --status complete --message "Worker handoff ready for orchestrator review"
```

## Worker Step 5: Write Structured Completion

**For v2 builds:** Use `update_build.py` to write structured completion data:

```bash
# First verify the script exists (graceful degradation)
if [ -f "N5/scripts/update_build.py" ]; then
  python3 N5/scripts/update_build.py complete {build_slug} {worker_id} \
    --status "complete" \
    --summary "What was accomplished" \
    --artifacts "comma,separated,file,paths" \
    --learnings "Key insights, decisions made, things that worked" \
    --concerns "Issues for orchestrator attention, blockers, risks" \
    --dependencies "W1.1,W1.2"  # Workers this work depended on
else
  # Fallback to legacy script
  python3 N5/scripts/build_worker_complete.py \
    --build-id {build_slug} \
    --worker-num {worker_num} \
    --status complete
fi
```

**Gather this information by reviewing:**
- What was the mission? Was it accomplished?
- What files were created/modified?
- What did you learn that the orchestrator should know?
- Any concerns, blockers, or risks to flag?

**Completion JSON format:**
```json
{
  "worker_id": "W1.1",
  "status": "complete",
  "completed_at": "2026-01-18T15:30:00Z",
  "convo_id": "con_XXXXX",
  "summary": "What was accomplished",
  "artifacts": ["path/to/file1.py", "path/to/file2.md"],
  "learnings": "Key insights and decisions",
  "concerns": "Issues needing orchestrator attention",
  "dependencies_used": ["W1.1", "W1.2"]
}
```

**For legacy builds (build_id + worker_num):**

Use the legacy notification script:

```bash
python3 N5/scripts/build_worker_complete.py --build-id {build_id} --worker-num {worker_num} \
  --status {complete|partial|blocked} --summary "..."
```

## Worker Step 6: DO NOT COMMIT

⚠️ **Workers do NOT git commit.** The orchestrator reviews all worker handoffs and does a single atomic commit.

**Worker close ends here.** Return control to V.

---

# FULL CLOSE MODE

For normal threads and orchestrators. Includes commits and full finalization.

## Tier Reference

| Tier | When | Cost | Time |
|------|------|------|------|
| 1 (Quick) | Default - simple discussions | ~$0.03 | <30s |
| 2 (Standard) | ≥3 artifacts, research | ~$0.06 | <90s |
| 3 (Full) | Builds, orchestrator, debug | ~$0.15 | <180s |

## Flags

- `--tier=1` / `--tier=2` / `--tier=3`: Force specific tier
- `--dry-run`: Preview without changes
- `--skip-positions`: Skip position extraction even if detected

---

## Full Step 1: Detect Tier

```bash
python3 N5/scripts/conversation_end_router.py --convo-id {CONVO_ID}
```

Review the recommendation. Override with `--tier=N` if needed.

## Full Step 2: Execute Mechanical Close

```bash
# Tier 1
python3 N5/scripts/conversation_end_quick.py --convo-id {CONVO_ID}

# Tier 2
python3 N5/scripts/conversation_end_standard.py --convo-id {CONVO_ID}

# Tier 3
python3 N5/scripts/conversation_end_full.py --convo-id {CONVO_ID}
```

## Full Step 3: PII Audit

```bash
python3 N5/scripts/conversation_pii_audit.py --convo-id {CONVO_ID} --auto-mark
```

Skip if conversation was purely discussion with no file creation.

## Full Step 4: If Orchestrator — Review Workers

**For orchestrator threads only:**

### Standard Orchestrator Review

1. List spawned workers:
   ```bash
   grep -r "parent_convo_id: {CONVO_ID}" /home/.z/workspaces/*/SESSION_STATE.md 2>/dev/null
   ```

2. For each worker, check:
   - Did it complete? (Check SESSION_STATE status)
   - Read its handoff summary
   - Verify artifacts exist

### V2 Build Orchestrator Review

For v2 builds with a build folder:

1. **Read all completions:**
   ```bash
   python3 N5/scripts/update_build.py status {build_slug}
   ```

2. **Review learnings and concerns** from all workers:
   ```bash
   ls N5/builds/{build_slug}/completions/
   # Read each W*.json file for details
   ```

3. **Aggregate worker summaries:**
   ```markdown
   ## Workers Summary
   - **W1.1:** ✅ Complete — [summary from completion]
     - Learnings: [key insights]
     - Concerns: [any flags]
   - **W1.2:** ✅ Complete — [summary]
   - **W2.1:** ⚠️ Partial — [what's missing]
   ```

4. **Close the build (after all commits):**
   ```bash
   python3 N5/scripts/update_build.py close {build_slug}
   ```

## Full Step 5: Invoke Librarian for Semantic Close

```
set_active_persona("1bb66f53-9e2a-4152-9b18-75c2ee2c25a3")
```

### Title Generation (ALL Tiers)

**Format:** `MMM DD | {State} {Type} {Content} Semantic Title`

**3-Slot Emoji System (from `N5/config/emoji-legend.json`):**

| Slot | Purpose | Options |
|------|---------|---------|
| **State** | Thread completion | ✅ complete, ⏸️ paused, ‼️ critical, 🚧 in-progress, ❌ failed |
| **Type** | Thread structure | 📌 normal, 🐙 orchestrator, 👷🏽‍♂️ worker, 🔗 linked |
| **Content** | Work type | 🏗️ build, 🔎 research, 🛠️ repair, 🕸️ site, 🪵 log, ✍️ content, 🪞 reflection, 🤳 social, 📊 data, 💬 comms, 🗂️ organize, 📝 planning |

**Examples:**
- `Jan 15 | ✅ 📌 🏗️ CRM Query Interface Refactor`
- `Jan 15 | ✅ 🐙 🏗️ CRM Consolidation Build`
- `Jan 15 | ✅ 👷🏽‍♂️ 🛠️ [CRM-Consolidation] Fix Import Paths`

### All Tiers (Tier 1+)

1. Read SESSION_STATE.md from `/home/.z/workspaces/{CONVO_ID}/`
2. Audit: `python3 N5/scripts/session_state_manager.py audit --convo-id {CONVO_ID}`
3. **Generate title** using 3-slot emoji system + semantic description
4. Write 2-3 sentence summary (semantic, not template)
5. Verify artifacts in correct locations

### Tier 2+ Only

6. Extract key decisions WITH RATIONALE
7. Identify open items and next steps
8. Recommend file moves if needed

### Tier 3 Only (AAR Generation)

9. Read context bundle from script output
10. **WRITE the After-Action Report** (see AAR template in spec)
11. Save to `Records/AARs/{DATE}_{Slug}.md`
12. Check capability graduation: `python3 N5/scripts/capability_graduation.py check --build-slug <slug>`
13. Extract lessons worth logging

## Full Step 6: Position Detection (Conditional)

**Detect if this conversation developed worldview positions:**

Ask: Did this conversation involve:
- Deep thinking about a topic?
- V articulating a belief, stance, or position?
- New evidence/reasoning for an existing belief?
- Strategic or philosophical insights?

**If YES → Execute Position Extraction:**

```bash
python3 N5/scripts/positions.py list
python3 N5/scripts/positions.py audit
```

**For each position candidate:**

1. Check overlap: `python3 N5/scripts/positions.py check-overlap "INSIGHT_TEXT" --threshold 0.4`
2. Action based on similarity:
   - ≥0.60: EXTEND existing position
   - 0.50-0.59: Review carefully
   - <0.50: CREATE new position
3. Create or extend accordingly

**If NO positions detected → Skip.**

## Full Step 7: Commit Target Suggestions

Load registry: `cat N5/config/commit_targets.json`

Present options (do NOT auto-commit):

```markdown
## Commit Opportunities

☐ **Learning Profile** — [Concepts learned, if any]
☐ **Content Library** — [Articles saved, if any]
☐ **Voice Library** — [Distinctive phrases, if any]
☐ **Positions** — [Worldview claims extracted, if any]
☐ **Git** — [Code changes, if any]

Reply with which items to commit, or skip to close.
```

## Full Step 8: Execute Commits

Based on V's selection, execute the relevant commits.

For orchestrators with workers, this is the **atomic commit point** - all worker changes committed together.

## Full Step 9: Return to Operator

```
set_active_persona("90a7486f-46f9-41c9-a98c-21931fa5c5f6")
```

Present formatted close output. End with:

```
✅ Conversation closed (Tier N)
```

---

## Anti-Patterns

❌ **Script-based title generation** — Title is semantic (LLM), not pattern matching
❌ **Regex decision extraction** — Produces garbage
❌ **Template-filled AARs** — Produces hollow documents
❌ **Claiming "Done" without reading** — Must understand before writing
❌ **Workers committing directly** — Defers to orchestrator for atomic commit

## Documentation

- **Spec:** `file 'N5/prefs/operations/conversation-end-v3.md'`
- **Emoji Legend:** `file 'N5/config/emoji-legend.json'`
- **Positions System:** `file 'N5/scripts/positions.py'`

## Version History

- **v5.3** (2026-01-18): Fixed Worker Step 2 - post-close title now generates 3-slot emoji prefix based on outcome while preserving pre-decided base title. Pre-decided title is for thread naming at launch; post-close title reflects what actually happened.
- **v5.2** (2026-01-18): V2 build orchestration support. Pre-decided title from `thread_title`. Structured completion via `update_build.py` with learnings/concerns fields. Orchestrator close reads completions before commit.
- **v5.1** (2026-01-18): Added build_id/worker_num detection. Added Worker Step 5 (build_worker_complete.py notification). Clearer mode detection priority.
- **v5.0** (2026-01-15): Two-mode system (Worker Close vs Full Close). Workers defer commits. 3-slot emoji required (📌 for normal). Greppable [Parent-Topic] tags for workers.
- **v4.0** (2026-01-15): Folded Type B position extraction. Title generation now semantic.
- **v3.2** (2026-01-14): Added PII Audit step
- **v3.1** (2026-01-13): Added Commit Target Suggestions
- **v3.0** (2026-01-12): AAR generation moved to Librarian

