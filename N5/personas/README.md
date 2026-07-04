---
created: 2026-07-03
last_edited: 2026-07-03
version: 1.0
provenance: n5os-ode-personas-as-code
---

# Persona SSOT

`N5/personas/` is the git-tracked source of truth for N5OS Ode persona prompts. Zo's live persona settings are a deploy target, not the canonical copy.

## Files

- `registry.json` maps persona slugs to prompt files and placeholder live IDs.
- `*.md` files contain one persona prompt each.
- `.snapshots/` is reserved for local backups before live pushes.

## Commands

```bash
python3 N5/scripts/persona_sync.py check
python3 N5/scripts/persona_sync.py --self-test
```

`export`, `diff`, and `push` are intended for an installed Zo workspace with live persona access and valid persona IDs. For packaged `n5os-ode`, replace `PERSONA_ID_*` placeholders after bootloader installation before using live sync.
