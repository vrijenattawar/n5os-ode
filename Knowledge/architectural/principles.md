---
created: 2025-12-15
last_edited: 2026-01-15
version: 1.0
provenance: n5os-ode-bootstrap
---

# N5OS-Ode Architectural Principles

Core design principles that guide the system.

## Philosophy

n5OS-Ode is a **cognitive operating system** — a framework that helps you think, plan, build, and reflect.

Key tenets:
- **Persistence**: Everything is stored; nothing is lost
- **Transparency**: All decisions and reasoning is recorded
- **Leverage**: Build once, reuse everywhere
- **Integration**: Systems talk to each other seamlessly

## Core Components

1. **Conversation System** — Persistent threads with state
2. **Block Intelligence** — Structured meeting analysis
3. **Knowledge Graph** — Semantic memory and recall
4. **Prompts** — Reusable workflows and procedures
5. **Scripts** — Mechanical automation and utilities

## Design Patterns

### Separation of Concerns

- **Scripts = Mechanics** (file operations, database queries)
- **LLM (AI) = Semantics** (understanding, analysis, judgment)
- Never let scripts make semantic decisions

### Atomic Operations

- Each script/prompt does one thing well
- Compose through orchestration, not monolithic functions
- Each operation is reversible where possible

### Configuration Over Code

- User preferences in `N5/prefs/`
- Context manifests define what's available
- Minimal hardcoding; maximum configurability

## Quality Standards

- **No Speculation**: Claims must have evidence (N=X)
- **Operational**: Frameworks must be usable by others
- **Documented**: All systems have clear README
- **Tested**: Critical paths have validation

See `docs/PHILOSOPHY.md` for more.

