---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# N5OS-Ode Architecture

High-level architecture of the N5OS-Ode personal operating system layer.

## Overview

N5OS-Ode is a file-based personal operating system that runs on top of Zo Computer. It provides:

- **Structured Prompts** — Reusable workflows as `.prompt.md` files
- **Context Loading** — Dynamic context injection via manifest files
- **State Management** — Session tracking and conversation continuity
- **Knowledge Organization** — Files-as-truth storage patterns

## Directory Structure

```
/
├── N5/                    # Core system files
│   ├── scripts/           # Python utilities
│   ├── prefs/             # Configuration and context
│   ├── schemas/           # JSON schemas
│   └── docs/              # Documentation
├── Prompts/               # User-facing workflows
│   ├── Blocks/            # Reusable components
│   └── reflections/       # Reflection workflows
├── Knowledge/             # Long-term knowledge storage
├── Lists/                 # Tracked lists and collections
└── templates/             # File templates
```

## Key Components

### Context Loader (`n5_load_context.py`)
Loads contextual files based on task type. Reads from `context_manifest.yaml` to determine which files to inject.

### Session State Manager (`session_state_manager.py`)
Tracks conversation progress in SESSION_STATE.md files. Provides continuity across conversation boundaries.

### Journal System (`journal.py`)
Guided reflection workflows with structured output formats.

## Design Principles

See `Knowledge/architectural/principles.md` for core architectural principles.

## Extension Points

1. **New Prompts** — Add `.prompt.md` files to `/Prompts/`
2. **New Context Groups** — Edit `N5/prefs/context_manifest.yaml`
3. **New Scripts** — Add to `N5/scripts/` with CLI interface

