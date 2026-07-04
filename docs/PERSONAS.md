---
created: 2026-01-15
last_edited: 2026-07-03
version: 2.0
provenance: n5os-ode-personas-as-code
---

# N5OS Ode Personas

N5OS Ode stores personas as code. The canonical prompt files live in `N5/personas/`; Zo's live persona settings are a deploy target, not the source of truth.

## Canonical Files

| Path | Purpose |
|---|---|
| `N5/personas/registry.json` | Persona roster, slugs, files, and installed live IDs |
| `N5/personas/*.md` | One persona prompt per file |
| `N5/scripts/persona_sync.py` | Offline check plus optional live export/diff/push |
| `N5/prefs/system/persona_routing_contract.md` | Routing rules and persona boundaries |

## Roster

| Persona | Domain | Use When |
|---|---|---|
| Operator | Coordination, navigation, state, safety | Default home base and routing |
| Builder | Backend, scripts, automation, services | Something needs implementation |
| Debugger | Root cause, QA, verification | Something is failing or needs proof |
| Designer | UI, UX, frontend, visual polish | A surface needs to look and feel right |
| Illustrator | Images, visual assets, generative visuals | The work is asset production |
| Writer | Communication, docs, editing | The output is prose |
| Researcher | Research, evidence, synthesis | The work needs sources or verification |
| Strategist | Tradeoffs, decisions, positioning | The work needs a recommendation |
| Architect | System design, build planning, MECE | Major work needs a plan |
| Teacher | Explanation and learning | The user needs understanding |
| Level Upper | Counterintuitive review, quality elevation | Major/risky work needs a second lens |

## Validation

Run these before shipping persona-system changes:

```bash
python3 N5/scripts/persona_sync.py check
python3 N5/scripts/persona_sync.py --self-test
```

`check` is offline and should pass in this repository. `diff` and `push` require a live Zo workspace with real persona IDs. The packaged registry uses `PERSONA_ID_*` placeholders until bootloader installation creates live personas.

## Routing

Use `docs/ROUTING.md` for user-facing choreography and `N5/prefs/system/persona_routing_contract.md` for the operational contract.
