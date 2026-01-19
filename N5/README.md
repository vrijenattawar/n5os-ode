---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
---
# N5 Directory

Core system files for N5OS-Ode.

## Contents

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Python utilities for system operations |
| `prefs/` | Configuration, context manifests, style guides |
| `schemas/` | JSON schemas for data validation |
| `docs/` | System documentation |

## Scripts Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `session_state_manager.py` | Conversation state tracking | `python3 N5/scripts/session_state_manager.py init --convo-id X` |
| `n5_load_context.py` | Context file loading | `python3 N5/scripts/n5_load_context.py build` |
| `journal.py` | Guided reflection sessions | `python3 N5/scripts/journal.py start` |
| `n5_protect.py` | Path protection checks | `python3 N5/scripts/n5_protect.py check /path` |
| `n5_safety.py` | Safety validation | `python3 N5/scripts/n5_safety.py check delete /path` |
| `init_build.py` | Build workspace creation | `python3 N5/scripts/init_build.py my-build --title "Title"` |

## Configuration

Main configuration files:
- `prefs/context_manifest.yaml` — Defines context loading groups
- `prefs/prefs.md` — Human-readable preferences overview

## For More Information

- [Main README](../README.md) — Project overview
- [Architecture](../docs/ARCHITECTURE.md) — System design
- [Contributing](../docs/CONTRIBUTING.md) — How to contribute

