---
created: 2025-12-14
last_edited: 2025-12-14
version: 1.0
---

# Build Templates

Templates for N5 build planning system. Used by `init_build.py` to scaffold new build workspaces.

## Files

| Template | Purpose |
|----------|---------|
| `plan_template.md` | Standardized build plan following Ben Guo's format |
| `status_template.md` | Progress tracking for active builds |

## Plan Template Structure

Based on Ben Guo's Velocity Coding approach:

1. **Open Questions** - Surface unknowns at TOP, resolve before proceeding
2. **Checklist** - Concise one-liners by phase, ☐/☑ format
3. **Phases** - Each has: Affected Files, Changes, Unit Tests
4. **Success Criteria** - Measurable outcomes
5. **Risks & Mitigations** - Known risks and how to handle
6. **Level Upper Review** - Divergent thinking input (experimental)

## Key Principles

- **Plans are for AI execution** - V sets up; Zo executes autonomously
- **No exploration in plans** - Research done BEFORE plan creation
- **2-4 phases max** - Logically stacking, not overly granular
- **Tests inline with phases** - Not separate "testing phase"
- **Affected files explicit** - Every file touched is listed

## Usage

```bash
# Initialize new build workspace
python3 N5/scripts/init_build.py my-new-feature

# Creates:
# N5/builds/my-new-feature/
# ├── PLAN.md        (from plan_template.md)
# ├── STATUS.md      (from status_template.md)
# └── .n5protected   (prevents accidental deletion)
```

## Reference

- Ben Guo's planning prompt: https://www.zo.computer/prompts/plan-code-changes
- Velocity Coding article: https://0thernet.substack.com/p/velocity-coding
- N5 Planning Discipline: `N5/prefs/operations/planning_prompt.md`

