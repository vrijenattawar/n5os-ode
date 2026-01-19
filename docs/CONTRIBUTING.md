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

## Questions?

Open an issue on GitHub.
