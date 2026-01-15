---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: n5os-ode-fix-day1-zero-errors
---

# Changelog

All notable changes to n5OS-Ode are documented here.

## [1.0.1] - 2026-01-15

### Added
- **Scripts**: `scripts/init_build.py`, `scripts/journal.py` (wrapper), `scripts/validate_repo.py`
- **Core Scripts**: `N5/scripts/positions.py`, `N5/scripts/conversation_end_router.py`, `N5/scripts/n5_safety.py`
- **Configuration**: `N5/config/emoji-legend.json`, `N5/config/commit_targets.json`
- **Documentation**: All missing context files (planning_prompt.md, style-guide.md, conversation-end-v3.md, etc.)
- **Quality**: `.gitignore` with Python/cache patterns, GitHub Actions CI workflow

### Fixed
- ✅ **Day-1 Zero-Errors**: All prompts now reference existing files and scripts
- ✅ **File References**: Standardized backtick syntax for all file mentions
- ✅ **Context Manifest**: All referenced files now exist in the repository
- ✅ **Prompts**: Build Capability, Close Conversation, Journal all functional
- ✅ **Placeholders**: Replaced PROJECT_REPO references where needed

### Notes
- All scripts have minimal but functional implementations
- n5OS-Ode is designed to be **dumped into another Zo workspace and work immediately**
- No external dependencies beyond Python 3.7+
- Database files (journal.db, etc.) are git-ignored and created at runtime

## [1.0.0] - 2025-12-15

### Initial Release
- Core N5OS-Ode philosophy and architecture
- 6 core prompts (Build Capability, Close Conversation, Journal, etc.)
- Block intelligence system (B01-B06)
- Semantic memory framework
- Session state management
- Comprehensive documentation

---

## How to Use This Changelog

- **[x] Added**: New features and files
- **[x] Fixed**: Bug fixes and corrections
- **[x] Changed**: Modifications to existing behavior
- **[x] Removed**: Deprecated or deleted items
- **[x] Security**: Security-related fixes

Each release is tagged in git (e.g., `v1.0.1`).

---

## Version Numbering

n5OS-Ode follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Example: `1.0.1` = Major 1, Minor 0, Patch 1 (first patch release)

---

## Contributing

To propose changes:
1. Open an issue describing the change
2. Submit a PR against the `develop` branch
3. Ensure all tests pass (run `python3 scripts/validate_repo.py`)
4. Update this CHANGELOG

---

## Support

For issues or questions:
- Check `docs/PHILOSOPHY.md` for design principles
- See `BOOTLOADER.prompt.md` for setup
- Run `python3 scripts/validate_repo.py` to diagnose problems

