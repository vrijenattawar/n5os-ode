---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: n5os-ode
---

# File Protection System

Directories containing `.n5protected` marker files are protected from accidental moves/deletes.

## Commands

- `python3 N5/scripts/n5_protect.py protect <path>` — Add protection
- `python3 N5/scripts/n5_protect.py unprotect <path>` — Remove protection
- `python3 N5/scripts/n5_protect.py check <path>` — Check if protected
- `python3 N5/scripts/n5_protect.py list` — List all protected paths

## Behavior

Before destructive operations (delete, move, bulk changes), the AI checks for `.n5protected` markers and requires explicit confirmation to proceed.

## See Also

- `file 'N5/prefs/system/safety-rules.md'` — Full safety rules
- `file 'N5/scripts/n5_protect.py'` — Implementation
