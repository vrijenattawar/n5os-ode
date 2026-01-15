# N5 Preferences Index

**Version:** 1.0.0 (n5OS-Ode)
**Last Updated:** 2026-01-15
**Purpose:** Lightweight index to modular preferences, loaded selectively by context

---

## Quick Start

This file serves as the entry point for N5 preferences. Use context-aware loading:

```bash
python3 N5/scripts/n5_load_context.py <context>
```

**Available contexts:** `build`, `strategy`, `system`, `safety`, `scheduler`, `writer`, `research`

---

## Critical Always-Load Rules

**These rules apply universally and cannot be overridden:**

### Safety & Review
- Never schedule anything without explicit consent
- Always support `--dry-run`; sticky safety may enforce it
- Require explicit approval for side-effect actions
- Always search for existing protocols before creating new ones

### Sandbox-First Artifact Protocol
- ALL files default to conversation sandbox (`/home/.z/workspaces/{convo_id}/`)
- Permanent workspace files require explicit declaration + validation before creation
- Exception paths: N5/logs/, N5/data/, /tmp/

### Approach Articulation
Before executing any non-trivial task, include an explicit **Approach** block stating:

- **Task**: Classification (trivial/scripting/system-work/refactor/content/workflow)
- **Method**: Tool choices, language selection, execution approach
- **Principles**: Which architectural principles apply
- **Risk**: Key failure modes or dependencies

**Format**: Keep concise (3-5 bullets), front-loaded before tool calls.

---

## Directory Structure

```
N5/
├── prefs/                    # Preferences and configuration
│   ├── prefs.md             # This file - main index
│   ├── context_manifest.yaml # Context loading definitions
│   ├── operations/          # Operational procedures
│   └── communication/       # Writing and communication guides
├── scripts/                  # Core operational scripts
├── data/                     # SQLite databases and runtime data
├── runtime/                  # Logs, runs, temporary files
└── schemas/                  # JSON schemas for validation
```

---

## Core Scripts Reference

| Script | Purpose |
|--------|---------|
| `session_state_manager.py` | Manage conversation state files |
| `n5_protect.py` | File/directory protection system |
| `n5_load_context.py` | Load context bundles by task type |
| `debug_logger.py` | Track debugging attempts, detect patterns |
| `journal.py` | Personal journaling with typed entries |
| `content_ingest.py` | Ingest content into knowledge library |

---

## Customization

To customize n5OS-Ode for your workflow:

1. **Edit `context_manifest.yaml`** to define your own context groups
2. **Add files to `N5/prefs/`** for domain-specific preferences
3. **Use `N5/data/`** for SQLite databases
4. **Create custom scripts in `N5/scripts/`**

---

## Further Reading

- [n5OS-Ode README](../README.md) - Project overview
- [Architecture](../docs/ARCHITECTURE.md) - System design
- [Contributing](../docs/CONTRIBUTING.md) - How to contribute
