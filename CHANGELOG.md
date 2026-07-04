---
created: 2026-01-15
last_edited: 2026-02-18
version: 2.0
provenance: sanitized
---

# Changelog

All notable changes to n5OS-Ode are documented here.

## [2.3.0] - 2026-07-03

### Added
- Added personas-as-code support with `N5/personas/` as the packaged persona prompt SSOT.
- Added `N5/scripts/persona_sync.py` for offline persona consistency checks and optional live Zo export/diff/push in installed workspaces.
- Added a generic 11-persona registry using `PERSONA_ID_*` placeholders until bootloader installation creates live Zo persona IDs.

### Changed
- Updated the persona routing contract to align with the SSOT registry and remove stale mirror-file assumptions.
- Updated persona documentation and Pulse learning-drop references to use `N5/personas/` instead of retired `Documents/System/personas/` mirrors.

## [2.0.1] - 2026-05-07

### Fixed
- Added the missing `Knowledge/architectural/building_fundamentals.md` artifact referenced by the bootloader context manifest and the v2.0.0 changelog.
- Clarified bootloader persona scope setup: create personas, capture IDs, set recommended scopes, verify scopes where possible, and warn without blocking if scope tooling is unavailable.
- Added an existing-user update path to the README so users can pull/apply the patch, rerun the idempotent bootloader, and validate their installation.
- Added `install.sh --update` so existing users can refresh root prompt/docs while preserving non-clobbering directory merges for personal workspace state.

### Notes
- This patch targets the public/export package repair path. Broader inherited documentation reference warnings from `N5/scripts/validate_repo.py --verbose` remain separate drift-cleanup work.

## [2.0.0] - 2026-02-18

### Added
- **Personas**: Expanded from 6 to 9 — added Architect (system design, build planning), Teacher (learning, conceptual understanding), Librarian (state sync, coherence audits)
- **Rules**: Expanded from 6 to 13 — added Persona Routing (master table), Session State Updates, Honest Workflow Reporting, Agent Conflict Gate, Pulse Orchestration, Anti-Hallucination, Debug Logging Discipline
- **Principles**: Expanded from 18 to 37 — added P0.1 (LLM-First), P3-P6, P9-P10, P12, P14, P22-P26, P29-P31, P33-P35, P37. Complete P35-P39 Building Fundamentals set
- **Skills**: Added `close/` (universal close router), `thread-close/`, `systematic-debugging/` (root cause analysis methodology), `frontend-design/` (production-grade UI with anti-slop guardrails)
- **Scripts**: Added `agent_conflict_gate.py` (agent sprawl prevention)
- **Workflows**: Added `architect_workflow.md`, `teacher_workflow.md`, `librarian_workflow.md`
- **Knowledge**: Added `Knowledge/architectural/building_fundamentals.md` (P35-P39 reference)

### Changed
- **BOOTLOADER.prompt.md**: Complete v2 rewrite — 9 personas, 13 rules, expanded phases for principles/skills/workflows
- **README.md**: Updated to reflect v2 scope (9 personas, 13 rules, 37 principles, 6 skills)
- **docs/PERSONAS.md**: Updated with Architect, Teacher, Librarian documentation
- **Context manifest**: Updated with build/strategy/system/safety/writer/research groups
- **Persona routing**: Full semantic routing table with 9-persona support
- **All persona definitions**: Leveled up to v2.0 depth (matching live system quality)

### Fixed
- **Sanitization**: Removed all personal/business references from repo files
- **Script references**: All persona/rule references now point to scripts that exist in the repo
- **Principle coverage**: Complete principle set (was missing P0.1, P3-P6, P9-P10, P12, P14, P22-P26, P29-P31, P33-P35, P37)

## [1.0.1] - 2026-01-15

### Added
- **Scripts**: `scripts/init_build.py`, `scripts/validate_repo.py`
- **Core Scripts**: `N5/scripts/conversation_end_router.py`, `N5/scripts/n5_safety.py` (Note: `N5/scripts/positions.py` is available in the extended installation)
- **Configuration**: `N5/config/emoji-legend.json`, `N5/config/commit_targets.json`
- **Documentation**: All missing context files (planning_prompt.md, style-guide.md, conversation-end-v3.md, etc.)
- **Quality**: `.gitignore` with Python/cache patterns, GitHub Actions CI workflow

### Fixed
- ✅ **Day-1 Zero-Errors**: All prompts now reference existing files and scripts
- ✅ **File References**: Standardized backtick syntax for all file mentions
- ✅ **Context Manifest**: All referenced files now exist in the repository
- ✅ **Prompts**: Close Conversation and block prompts functional
- ✅ **Placeholders**: Replaced repository placeholder references where needed

### Notes
- All scripts have minimal but functional implementations
- n5OS-Ode is designed to be **dumped into another Zo workspace and work immediately**
- No external dependencies beyond Python 3.7+
- Runtime database files are git-ignored and created as needed

## [1.0.0] - 2025-12-15

### Initial Release
- Core N5OS-Ode philosophy and architecture
- Core prompts including Close Conversation and block generation
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
3. Ensure all tests pass (run `python3 N5/scripts/validate_repo.py`)
4. Update this CHANGELOG

---

## Support

For issues or questions:
- Check `docs/PHILOSOPHY.md` for design principles
- See `BOOTLOADER.prompt.md` for setup
- Run `python3 N5/scripts/validate_repo.py` to diagnose problems
