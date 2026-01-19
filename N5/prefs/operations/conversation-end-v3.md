---
created: 2025-12-18
last_edited: 2026-01-15
version: 5.0
provenance: con_A79BOqF7vZTQ8w0N
---

# Conversation-End System v5.0

> **Single Source of Truth** for conversation closure workflow.

## Overview

Two-mode system with tiered depth for Full Close.

| Mode | When | Purpose | Commits? |
|------|------|---------|----------|
| **Worker Close** | Thread has `parent_convo_id` or was spawned via `WORKER_ASSIGNMENT_*.md` | Clean handoff to orchestrator | ❌ NO |
| **Full Close** | Normal or orchestrator thread | Complete finalization | ✅ YES |

**CRITICAL Division of Labor:**
- **Scripts** = Mechanics ONLY (file scanning, git status, path gathering)
- **Librarian (LLM)** = ALL Semantics (titles, summaries, AARs, handoffs)

**Scripts DO NOT:**
- Generate titles (that's semantic)
- Extract decisions (no regex)
- Generate AARs (no template filling)

---

## Mode Detection

Check SESSION_STATE.md:
```yaml
parent_convo_id: con_XXXXX  # Present → Worker
orchestrator_id: con_XXXXX  # Present → Worker
```

Or check for `WORKER_ASSIGNMENT_*.md` spawn pattern.

---

## Worker Close Flow

Workers exist to complete a task for an orchestrator. Their close is about **handoff clarity**, not finalization.

### Worker Steps

1. **Verify deliverables** — All promised artifacts exist in correct locations
2. **Generate title** — `MMM DD | {State} 👷🏽‍♂️ {Content} [Parent-Topic] Task`
3. **Write handoff summary** — Clear package for orchestrator review
4. **Update SESSION_STATE** — Mark status complete
5. **DO NOT COMMIT** — Orchestrator does atomic commit of all worker work

### Worker Title Pattern

```
Jan 15 | ✅ 👷🏽‍♂️ 🛠️ [CRM-Consolidation] Fix Import Paths
```

The `[Parent-Topic]` tag = greppable lineage to orchestrator.

### Worker Handoff Template

```markdown
## Worker Handoff: [Task Name]

**Parent:** con_XXXXX
**Status:** ✅ Complete | ⚠️ Partial | ❌ Blocked

### What Was Done
- [Accomplishments with file paths]

### Artifacts Created
- `path/to/file.py` — [purpose]

### Caveats for Orchestrator
- [Decisions, assumptions, edge cases]

### Ready for Commit
- [ ] [Files list]
```

---

## Full Close Flow

For normal threads (📌) and orchestrators (🐙).

### Tiers

| Tier | Trigger | Steps |
|------|---------|-------|
| **Tier 1 (Quick)** | Default | Scan, title, summary |
| **Tier 2 (Standard)** | ≥3 artifacts, research | + Decisions, recommendations |
| **Tier 3 (Full)** | Builds, orchestrators | + AAR, lessons, graduation |

### Full Close Steps

**Tier 1 (All conversations):**
1. Run mechanical script: `conversation_end_quick.py`
2. PII audit (if files created)
3. Generate title (semantic, 3-slot emoji)
4. Write 2-3 sentence summary
5. Audit SESSION_STATE complete

**Tier 2 (Add):**
6. Extract key decisions WITH RATIONALE
7. Identify open items
8. Recommend file moves

**Tier 3 (Add):**
9. Read context bundle
10. Write After-Action Report
11. Check capability graduation
12. Extract lessons

**For Orchestrators (Add):**
- Review all worker handoffs
- Generate consolidated workers summary
- Execute atomic commit of all worker + orchestrator changes

**Position Extraction (Conditional):**
- If worldview positions developed → Extract and add to positions.db

---

## Title System

**Format:** `MMM DD | {State} {Type} {Content} Semantic Title`

### 3-Slot Emoji System

| Slot | Required | Options |
|------|----------|---------|
| **State** | ✅ | ✅ complete, ⏸️ paused, ‼️ critical, 🚧 in-progress, ❌ failed |
| **Type** | ✅ | 📌 normal, 🐙 orchestrator, 👷🏽‍♂️ worker, 🔗 linked |
| **Content** | ✅ | 🏗️ build, 🔎 research, 🛠️ repair, 🕸️ site, 🪵 log, ✍️ content, 🪞 reflection, 🤳 social, 📊 data, 💬 comms, 🗂️ organize, 📝 planning |

### Examples

```
Jan 15 | ✅ 📌 🏗️ CRM Query Interface Refactor
Jan 15 | ✅ 🐙 🏗️ CRM Consolidation Build
Jan 15 | ✅ 👷🏽‍♂️ 🛠️ [CRM-Consolidation] Fix Import Paths
Jan 15 | ⏸️ 📌 🔎 Market Research Competitor Analysis
```

### Emoji Suggestions

Librarian MAY suggest emojis based on detection hints in `N5/config/emoji-legend.json`, but final selection is semantic judgment, not pattern matching.

---

## Script Outputs

Scripts gather context for Librarian. They output:

```yaml
conversation_id: con_XXXXX
session_state: {parsed SESSION_STATE.md}
files:
  - path: /path/to/file
    type: code|doc|config
artifacts_count: N
git_status: {staged, unstaged, untracked counts}
```

**Scripts DO NOT output titles, summaries, or decisions.**

---

## Entry Points

```bash
# Auto-detect tier and mode
python3 N5/scripts/conversation_end_router.py --convo-id <id>

# Direct tier execution (Full Close only)
python3 N5/scripts/conversation_end_quick.py --convo-id <id>
python3 N5/scripts/conversation_end_standard.py --convo-id <id>
python3 N5/scripts/conversation_end_full.py --convo-id <id>
```

Or via prompt: `@Close Conversation`

---

## Version History

- **v5.0** (2026-01-15): Two-mode system. Worker Close (partial) vs Full Close. Workers defer commits. 3-slot emoji required. [Parent-Topic] greppable tags.
- **v4.0** (2026-01-12): AAR generation owned by Librarian
- **v3.2** (2026-01-09): Capability graduation flow
- **v3.0** (2025-12-18): Tiered system with Librarian ownership

