---
created: 2025-12-15
last_edited: 2026-01-15
version: 3.0
provenance: n5os-ode-bootstrap
---

# Conversation Close Specification (v3)

Detailed specification for the Close Conversation prompt system.

## Overview

Conversations have a formal "close" ceremony that captures learning, extracts position changes, and commits artifacts to long-term storage.

Two modes:
- **Worker Close**: For parallel work threads (no commits)
- **Full Close**: For normal/orchestrator threads (with commits)

## Tier System

| Tier | Cost | Time | When |
|------|------|------|------|
| 1 | $0.03 | <30s | Simple discussion |
| 2 | $0.06 | <90s | ≥3 artifacts |
| 3 | $0.15 | <180s | Build/orchestrator |

## Key Concepts

- **Handoff** (Worker): Package for orchestrator review
- **AAR**: After-Action Report (Tier 3 only)
- **Position**: A captured belief or stance
- **Commit**: Save to long-term storage (git, Knowledge, Records)

## Implementation Notes

For distributed setups:
- SESSION_STATE.md drives mode/tier detection
- Scripts are minimal; LLM does semantic work
- Commits are atomic (all or nothing)

See `Prompts/Close Conversation.prompt.md` for the executable version.

