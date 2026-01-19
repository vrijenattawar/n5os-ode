---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: n5os-ode
---

# N5OS Ode Architecture

## Overview

N5OS Ode is a lightweight operating system for AI-augmented workflows. It provides:

- **Personas** — Specialist AI behaviors for different tasks
- **Rules** — Behavioral guardrails and preferences
- **Context Loading** — Dynamic context injection based on task type
- **State Management** — Conversation and session tracking

## Core Components

### N5/ Directory

The brain of N5OS Ode:

```
N5/
├── prefs/           # Configuration and preferences
│   ├── prefs.md     # User preferences
│   ├── context_manifest.yaml
│   └── system/      # System-level policies
├── scripts/         # Utility scripts
├── cognition/       # Semantic memory (optional)
├── config/          # Runtime configuration
└── data/            # Persistent data (DBs)
```

### Personas

See `file 'docs/PERSONAS.md'` for persona design.

### Rules

See `file 'docs/RULES.md'` for rule system.

### Context Loading

See `file 'docs/CONTEXT_LOADING.md'` for context injection.

## Design Principles

1. **Simple over easy** — Prefer explicit over magic
2. **Portable** — Works in any Zo workspace
3. **Composable** — Components work independently
4. **Semantic** — AI does judgment, scripts do mechanics
