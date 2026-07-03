---
created: 2026-04-23
last_edited: 2026-04-23
version: 1.0
provenance: con_jL5x88AR1IB8Mvab
---

# Session State Policy

This file governs when `SESSION_STATE.md` is required, optional, or skipped.

## Default: OFF
**Session state is opt-in.** Most conversations do not need it and should not create it. A fresh install should never auto-generate `SESSION_STATE.md` for ordinary Q&A, lookups, or small edits — that is pure ceremony. Only initialize it when the lane below genuinely calls for continuity, resumability, or structured closeout. When in doubt, skip it; the close pipeline degrades gracefully when the file is absent.

## Core Principle
Keep runtime compatibility intact while reducing unnecessary startup work.

Do not remove session-state consumers first. Change initialization policy first, then improve fallback behavior over time.

## Policy Levels

### Required (opt-in — the only lanes that create session state by default)
Initialize or refresh conversation-local `SESSION_STATE.md` when the thread is in any of these lanes:
- build or orchestration work
- Pulse/drop/build-close flows
- multi-step debugging likely to span turns
- work expected to produce structured closeout or resume later
- worker / action conversations that depend on tracked state
- larger file mutations where explicit progress/state helps prevent drift

### Optional
Session state is beneficial but not mandatory for:
- medium-complexity planning
- longer research threads
- substantive multi-step writing
- exploratory work likely to branch into execution

### Skippable
Session state may be skipped for:
- quick Q&A
- single-shot lookups
- tiny edits with no closeout or resume value
- lightweight brainstorming that is unlikely to persist

## Decision Procedure
Before non-trivial work:
1. identify lane (`explore` or `commit`)
2. estimate blast radius (`small` / `medium` / `large`)
3. ask whether the work needs continuity, resumability, closeout routing, or worker/build identity
4. if yes, initialize or refresh session state
5. if no, proceed without forcing session state

## Compatibility Rules
- Existing runtime consumers of `SESSION_STATE.md` must continue to work
- If a workflow requires build/drop identity, session state remains required unless an equivalent compatibility source exists
- Missing session state should degrade gracefully to thread/default mode where safe
- Hard failures are acceptable only when invariants truly require state, such as drop/build-close context

## Current Known Dependencies
High-sensitivity consumers include:
- `N5/lib/close/guards.py`
- `Skills/thread-close/scripts/router.py`
- `Skills/drop-close/scripts/close.py`
- `N5/scripts/n5_thread_export.py`
- `N5/scripts/auto_init_conversation.py`
- registry/closure/telemetry/struggle tracking flows

## Operational Guidance
- When session state is required, prefer the conversation-local file in `/home/.z/workspaces/<convo-id>/SESSION_STATE.md`
- Keep updates proportional to the work; do not turn every trivial exchange into a state-management routine
- For existing workflows that assume universal init, maintain compatibility until fallback logic is improved

## Migration Guidance
### Phase 1
Remove universal mandates from the rule layer. Keep runtime behavior intact.

### Phase 2
Use conditional initialization by lane.

### Phase 3
Improve fallback inference for close/router/export flows.

### Phase 4
Reassess how often session state is truly needed.
