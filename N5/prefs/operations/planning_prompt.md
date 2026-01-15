---
created: 2025-12-15
last_edited: 2026-01-15
version: 1.0
provenance: n5os-ode-bootstrap
---

# Planning Prompt Protocol

Guidelines for planning-heavy work (strategy, builds, capability design).

## Before You Start

Ask yourself:
1. What specific problem are we solving?
2. What would "done" look like?
3. What constraints exist? (time, resources, dependencies)
4. Who needs to sign off?

If any are unclear, spend 5 min clarifying before proceeding.

## Structure

1. **Objective** — One sentence. If it needs more, you don't understand it yet.
2. **Scope** — What's in scope? What's explicitly out?
3. **Constraints** — Time, budget, dependencies, non-negotiables
4. **Approach** — High-level strategy (not step-by-step yet)
5. **Risks** — What could go wrong?
6. **Success Criteria** — How do we know it's done?

## Anti-Patterns

❌ Plans that are step-by-step without strategy  
❌ Plans that ignore constraints  
❌ Plans with no success criteria  
❌ Plans that assume unlimited resources/time  

## Output

Plans live in `builds/<slug>/PLAN.md` or `Knowledge/plans/` depending on scope.

All plans include YAML frontmatter with version and provenance.

