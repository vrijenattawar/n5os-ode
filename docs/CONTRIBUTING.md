---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: n5os-ode
---

# Contributing to N5OS Ode

## Getting Started

1. Fork the repository
2. Clone to your Zo workspace
3. Run the bootloader: `@BOOTLOADER`

## Development Guidelines

### File Changes

- All markdown files need YAML frontmatter (created, last_edited, version, provenance)
- Scripts should have `--help` support
- Test changes locally before committing

### Code Style

- Python: Follow PEP 8
- Markdown: Use consistent heading levels

### Commit Messages

Format: `<type>: <description>`

Types:
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `refactor` — Code restructure
- `chore` — Maintenance

### Pull Requests

1. Create a feature branch
2. Make changes
3. Run `python3 N5/scripts/validate_repo.py`
4. Submit PR with description

## Sync Protocol

Before starting any work on N5OS Ode:

1. **Always pull first:**
   ```bash
   cd N5/export/n5os-ode
   git pull origin main
   ```

2. **Before pushing, run sync check:**
   ```bash
   python3 N5/scripts/ode_sync_check.py
   ```

3. **Never force push** unless restoring from a known good state.

4. **If working from multiple machines** (local, Devin, etc.), designate one as source of truth.

### Recovery

If history is accidentally lost:
1. Check for backup branches: `git branch -r | grep backup`
2. Restore: `git reset --hard origin/backup-<name>`
3. Force push the restored history: `git push --force-with-lease origin main`

## Questions?

Open an issue on GitHub.
