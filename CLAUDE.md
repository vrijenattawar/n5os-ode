---
created: 2026-05-15
last_edited: 2026-05-15
version: 1.0
provenance: con_H7bSTDBcsH0gBtFG
---

# N5OS Environment — Claude Code Adapter

**Owner:** _(your name — set during PERSONALIZE)_
**System:** N5OS on Zo Computer
**Fast map:** `WORKSPACE_MAP.md` · **Canonical contract:** `AGENTS.md` · **Shared harness contract:** `N5/HARNESS_CONTRACT.md` · **Session-state policy:** `N5/SESSION_STATE_POLICY.md` · **Placement authority:** `POLICY.md`

This file contains Claude Code-specific mechanics only. For workspace navigation, start with `WORKSPACE_MAP.md`. For workspace governance, precedence, build invariants, and operating defaults, follow `AGENTS.md`. For session-state decisions, follow `N5/SESSION_STATE_POLICY.md`. For folder placement rules, follow `POLICY.md`.

---

## MCP Bridge

Claude Code has access to three N5OS MCP tools:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `n5_protect_check` | Warns before destructive ops on protected paths | Before delete/move on `N5/`, `Sites/`, `Personal/`, `Prompts/`, `Knowledge/` |
| `n5_log_bio` | Logs significant milestones to V's bio timeline | Major life/career events, not routine task completions |
| `n5_close_conversation` | Logs session to N5OS alongside Zo conversations | At session close via `/n5-close` or the Stop hook |

These tools warn but do not block. You decide whether to proceed based on context.

---

## Session Lifecycle

- **Session context:** `.claude/session-context.md` tracks progress, decisions, and loaded context modules for this Claude Code session.
- **Session close:** Use `/n5-close` to log the session to N5OS.
- **Auto-logging:** The `Stop` hook automatically logs sessions on exit.
- **Conversation-local state:** Use the conversation workspace `SESSION_STATE.md` when the current lane or workflow requires it per `N5/SESSION_STATE_POLICY.md`.

---

## On-Demand Context Loading

For non-trivial work, load shared docs in this order:

1. `WORKSPACE_MAP.md`
2. `AGENTS.md`
3. `N5/HARNESS_CONTRACT.md`
4. `N5/SESSION_STATE_POLICY.md`
5. Specialized protocol docs only as needed

Then load domain context with the context loader (the Operator persona runs this as its first action):

```bash
python3 N5/scripts/n5_load_context.py "<group-or-intent>"
```

Available groups (authoritative source: `N5/prefs/context_manifest.yaml`):

| Group | Use For |
|---------|---------|
| `build` | Implementation, refactoring, coding, engineering |
| `strategy` | High-level thinking, planning, decisions, reasoning |
| `system` | Lists, index, system operations, database |
| `safety` | Destructive ops, moves, deletes |
| `scheduler` | Agents, scheduled tasks, automation |
| `writer` | Content creation, writing, polished communication |
| `research` | Deep dive, analysis, web research |
| `health` | Health planning, bio-context (empty until personalized) |
| `general` | Fallback for novel or undefined tasks |

You can also pass a natural-language intent (e.g. `"fix the failing script"`) or a specific file path. Run `python3 N5/scripts/n5_load_context.py --list` to see all groups.

Default state: only core principles and safety rules are loaded. Load additional context as tasks require it.

---

## System Architecture (Quick Reference)

N5OS is organized as a layered system:

```
N5/
├── prefs/       # Architectural principles + operational protocols
├── scripts/     # Python automation scripts
├── config/      # Centralized configuration (ports, webhooks, integrations)
├── data/        # Runtime state, databases, caches
├── builds/      # Project workspaces
├── commands/    # Executable recipes for AI execution
└── logs/        # Thread exports, system logs

Sites/           # Production websites (protected)
Personal/        # Personal data and records (protected)
Skills/          # Deployed skill definitions with SKILL.md docs
Knowledge/       # Curated knowledge artifacts
```

---

## Protected Paths

Before delete/move operations on these directories, use `n5_protect_check`:

| Path | Protection Level |
|------|-----------------|
| `N5/` | High — system infrastructure |
| `Sites/` | High — production websites |
| `Personal/` | High — personal data |
| `N5/prefs/**/*.md` | Manual-edit only |
| `Prompts/` | Medium |
| `Knowledge/**/*.md` | Medium |

---

## Configuration Quick Reference

**Context manifest:** `N5/prefs/context_manifest.yaml` — the groups the context loader reads.

**Config templates:** `N5/templates/configs/*.template` — copied into place by `install.sh`. Personal registries (port registry, commands registry, Drive folder mapping) are **not** shipped in the base distribution; create them under `N5/config/` if and when you need those subsystems.

---

## Key Protocol Pointers

These are not rules to memorize — search for them when the task requires specialized guidance.

| Domain | File |
|--------|------|
| **Persona / specialist routing** (the conversation-orientation brain) | `N5/prefs/system/persona_routing_contract.md` |
| Think-Plan-Execute | `N5/prefs/operations/planning_prompt.md` |
| Recipe execution | `N5/prefs/operations/recipe-execution-guide.md` |
| Message→task automation (example integration; genericize before use) | `N5/prefs/protocols/task_routing_protocol.md` |
| File creation | `N5/prefs/operations/file-creation-protocol.md` |
| Artifact placement | `N5/prefs/operations/artifact-placement.md` |
| File protection | `N5/prefs/system/file-protection.md` |
| Folder policy | `N5/prefs/system/folder-policy.md` |
| Scheduled tasks | `N5/prefs/operations/scheduled-task-protocol.md` |
| Digest creation | `N5/prefs/operations/digest-creation-protocol.md` |
| Conversation close | `N5/prefs/operations/conversation-end-v5.md` |
| Thread closure triggers | `N5/prefs/operations/thread-closure-triggers.md` |
| Conversation init | `N5/prefs/operations/conversation-initialization.md` |
| Backpressure | `N5/prefs/operations/backpressure-protocol.md` |
| Refactoring | `N5/prefs/operations/refactoring-protocol.md` |
| Debug logging | `N5/prefs/operations/debug-logging-auto-behavior.md` |

---

## What This Adapter Provides

1. **Protection warnings** via `n5_protect_check` MCP tool
2. **Session continuity** via `.claude/session-context.md`
3. **N5OS logging** via `n5_close_conversation` MCP tool
4. **Bio event logging** via `n5_log_bio` MCP tool

## What This Adapter Does NOT Do

- Override your planning capabilities or judgment
- Block any operations (MCP tools warn only)
- Require specific workflows (protocols are guidance, not mandates)
- Load all context by default (you control what's loaded per P08)
- Replace `WORKSPACE_MAP.md`, `AGENTS.md`, `N5/HARNESS_CONTRACT.md`, or `N5/SESSION_STATE_POLICY.md`

---

**Last Updated:** 2026-04-06
**Fast Map:** `WORKSPACE_MAP.md`
**Canonical Contract:** `AGENTS.md`
**Shared Harness Contract:** `N5/HARNESS_CONTRACT.md`
**Session-State Policy:** `N5/SESSION_STATE_POLICY.md`
**Placement Authority:** `POLICY.md`
**Full Preferences:** N5/prefs/ (load on-demand per P08)
