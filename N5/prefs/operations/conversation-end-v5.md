---
title: Conversation End Workflow v5
description: Specification for conversation closure - now implemented via skills
related: Skills/thread-close/, Skills/drop-close/, Skills/build-close/
version: 5.1
updated: 2026-01-24
---

> **Note (2026-02-14):** This specification is implemented via three close skills, and execution is coordinated through the Close Conversation prompt:
> - `Skills/thread-close/` — Interactive threads (Full Close)
> - `Skills/drop-close/` — Pulse Drop workers (Worker Close)  
> - `Skills/build-close/` — Post-Pulse build synthesis (Build Close)
>
> Canonical operator entrypoint: `file 'Prompts/Close Conversation.prompt.md'`.
> Shared close logic lives in `N5/lib/close/`.

# Conversation End Workflow v5

> **Single Source of Truth** for conversation closure workflow.
> Executable prompt: `file 'Prompts/Close Conversation.prompt.md'`

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
6. Git close check: if the session created or edited tracked files, commit them (work commits separate from `chore(data):` churn) or explicitly declare the dirty state and why it is being left uncommitted. Never end a session on a non-main branch without stating the return plan. (`Documents/System/Live-System-Git-Spec.md`)

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

---

## Knowledge Capture (Tier 2+)

**⚠️ PROACTIVE SCANNING REQUIRED** — This step was being skipped too often. Always scan, even if you don't expect to find anything.

Conversations often produce artifacts and insights worth preserving beyond the conversation itself. At close, actively scan for:

### A. Position Extraction → `positions.db`

**Detection Heuristics:**
- Socratic dialogue with the user articulating beliefs/worldviews
- Documents named with "POV", "position", "thesis", "take", "stance"
- Explicit statements like "my view is...", "I believe...", "the way I see it..."
- Arguments with reasoning and stakes attached
- Contrarian takes or distinctive framing

**Extraction Flow:**
1. Read conversation for position-worthy content
2. For each candidate, draft using the position schema:
   - `insight` (2-3 sentences - the belief)
   - `reasoning` (transferable principle - WHY)
   - `stakes` (implications - SO WHAT)
   - `conditions` (boundaries - WHEN)
   - `domain` (personal | professional | technical | strategy | worldview | epistemology)
3. Present to the user: "📍 **Position Candidates Detected:**" with previews
4. On approval: `python3 N5/scripts/positions.py add --domain <domain> --title "<title>" --insight "<insight>" --source-conversation <convo_id>`

**Key Distinction:** Positions are worldview-level beliefs, not tactical decisions or contextual observations.

### B. Content Library Candidates → `Knowledge/content-library/`

**Detection Heuristics:**
- Artifacts named with "POV-", "framework-", "guide-", "how-to-"
- Reusable documents (not conversation-specific)
- Research memos or dossiers
- Templates or frameworks created
- Polished writing intended for reuse

**Content Types for Library:**
| Type | When to Ingest |
|------|----------------|
| `personal` | the user's POVs, worldview documents, personal frameworks |
| `article` | Polished written pieces |
| `framework` | Reusable mental models, decision frameworks |
| `snippet` | Quotable passages, key paragraphs |

**Ingest Flow:**
1. Identify artifacts that have value beyond this conversation
2. Present to the user: "📚 **Content Library Candidates:**" with file list and suggested types
3. On approval: `python3 N5/scripts/content_ingest.py "<path>" --type <type> --move`

### C. Close Output Format (when candidates exist)

Add to the standard close output:

```markdown
---

### 📍 Position Candidates

**[Position Title]**
> [2-3 sentence insight preview]

Domain: [domain] | Confidence: [low/med/high]
→ Add to positions.db? [Yes/No]

---

### 📚 Content Library Candidates

- `the user-POV-Topic-Name.md` → suggested type: `personal`
- `Framework-X.md` → suggested type: `framework`

→ Ingest to Content Library? [Yes/No/Select]
```

**If the user approves:** Execute the ingests. If declined or no candidates, omit sections.

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

- **v5.5** (2026-01-19): Added emphasis on proactive scanning for knowledge capture. Synced with prompt v5.5.
- **v5.1** (2026-01-19): Knowledge Capture section — position extraction to positions.db + Content Library ingest hook at conversation-end. Detection heuristics and offer-based flow.
- **v5.0** (2026-01-15): Two-mode system. Worker Close (partial) vs Full Close. Workers defer commits. 3-slot emoji required. [Parent-Topic] greppable tags.
- **v4.0** (2026-01-12): AAR generation owned by Librarian
- **v3.2** (2026-01-09): Capability graduation flow
- **v3.0** (2025-12-18): Tiered system with Librarian ownership
