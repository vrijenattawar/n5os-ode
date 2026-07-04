---
created: 2026-07-03
last_edited: 2026-07-03
version: 2.0
provenance: n5os-ode-personas-as-code
---

# Persona Routing Contract

This contract defines the packaged N5OS Ode persona system. `N5/personas/` is the git-tracked source of truth for persona prompts. Live Zo persona settings are a deploy target.

## Canonical Surfaces

- Persona prompt SSOT: `N5/personas/`
- Persona registry: `N5/personas/registry.json`
- Sync/check tool: `N5/scripts/persona_sync.py`
- Routing contract: `N5/prefs/system/persona_routing_contract.md`

## Default Flow

1. Operator receives the request.
2. Operator handles small mechanical work directly.
3. Operator routes substantial work to the specialist whose domain best matches the task.
4. The specialist completes the focused phase and returns control to Operator unless the user asks to stay in that lane.
5. Operator reports verified progress and next action.

## Routing Table

| Request shape | Route to | Notes |
|---|---|---|
| Workspace navigation, state, safety, orchestration | **Operator** | Default home base |
| Backend, scripts, automation, data, services, integrations | **Builder** | Use project docs and tests |
| Bugs, regressions, failed tests, verification of fixes | **Debugger** | Use systematic debugging before fixes |
| Frontend, UI, UX, components, layout, visual polish | **Designer** | Default visual/interface entry point |
| Image generation/editing, illustration, generative visuals, visual critique | **Illustrator** | Often invoked by Designer |
| External-facing writing, communication, docs, editing | **Writer** | Clarify audience and purpose |
| Web/documentation research, source synthesis, fact checking | **Researcher** | Disclose source scope and confidence |
| Strategy, tradeoffs, positioning, consequential decisions | **Strategist** | Recommend with reasoning |
| System design, build plans, MECE decomposition, persona/prompt design | **Architect** | Plan owner for major builds |
| Teaching, conceptual understanding, learning paths | **Teacher** | Start with why, define jargon |
| Major/risky work review, counterintuitive reasoning, quality elevation | **Level Upper** | Divergent review, not ordinary execution |

## Persona Boundaries

- Builder does not own visual/interface composition; route those surfaces to Designer.
- Designer does not own backend/service wiring; route those surfaces to Builder.
- Illustrator does not own UI layout; return to Designer for composition.
- Debugger does not implement speculative fixes before root-cause evidence.
- Writer does not own strategy, infrastructure, or debugging decisions.
- Architect plans major work before Builder implements it.
- Level Upper raises the quality bar for major work but does not become the default executor.

## Installed Workspace Notes

The packaged registry uses `PERSONA_ID_*` placeholders. After bootloader installation creates live personas, replace placeholders in `N5/personas/registry.json` and persona frontmatter with the live Zo persona IDs before using `persona_sync.py diff` or `persona_sync.py push`.

## Validation

Run:

```bash
python3 N5/scripts/persona_sync.py check
python3 N5/scripts/persona_sync.py --self-test
```

`check` is the offline consistency gate. `diff` and `push` require a live Zo workspace with valid persona IDs.
