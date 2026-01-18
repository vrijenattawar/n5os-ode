---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: worker_006_build_planning
---

# Build Planning System

The Build Planning System provides structured workflows for planning and executing builds (new capabilities, features, or systems) in N5OS Ode.

---

## Core Philosophy

**Plans are FOR AI execution, not human review.**

This is the fundamental principle that shapes the entire build planning system:

- The human sets up the plan through guided interaction
- The AI reads the plan and executes it step-by-step without human intervention
- Plans contain sufficient detail for autonomous execution
- No exploration or discovery happens during execution — that happens before plan creation

This approach eliminates the "read, understand, ask clarifying questions, get stuck" loop that plagues traditional AI coding workflows.

---

## The Build Flow

The complete build flow involves three specialized personas working in sequence:

### 1. Initialization (`init_build.py`)

When you want to build something new, the system initializes a build workspace:

```bash
python3 N5/scripts/init_build.py <slug> --title "<Capability Name>"
```

This creates:
- `N5/builds/<slug>/PLAN.md` — Build plan (from template)
- `N5/builds/<slug>/STATUS.md` — Progress tracking (from template)
- `N5/builds/<slug>/.n5protected` — Protection marker

### 2. Planning Phase (Architect Persona)

The Architect persona creates the detailed build plan:

1. **Activates automatically** after `init_build.py` runs
2. **Reads the plan template** to understand structure
3. **Creates detailed plan** in `PLAN.md` following the template:
   - Open questions (surface unknowns first)
   - Phases with checklists, affected files, and changes
   - Success criteria and risks
4. **Invokes Level Upper** for counterintuitive review
5. **Presents plan** for approval

### 3. Review Phase (Level Upper Persona)

Level Upper provides divergent thinking and catches blind spots:

1. **Receives the draft plan**
2. **Identifies counterintuitive approaches** or hidden risks
3. **Documents suggestions** in the plan's Level Upper Review section
4. **Architect incorporates** what makes sense, rejects with rationale

### 4. Execution Phase (Builder Persona)

Once approved, Builder executes autonomously:

1. **Reads the approved plan**
2. **Executes phases sequentially** without asking for clarification
3. **Updates checklists** (☐ → ☑) as work completes
4. **Updates STATUS.md** with progress
5. **Runs tests** specified in each phase
6. **Reports completion** with success criteria met

---

## Plan Template Structure

The plan template (`templates/build/plan_template.md`) follows Ben Guo's Velocity Coding approach:

### Frontmatter
```yaml
---
created: {{DATE}}
last_edited: {{DATE}}
version: 1.0
type: build_plan
status: draft
---
```

### Open Questions (First!)
Surface unknowns at the TOP of the plan. Resolve before proceeding.

```
## Open Questions

- [ ] What data source do we use for X?
- [ ] Should this be synchronous or async?
```

### Checklist
Concise one-liners organized by phase. Uses checkboxes for progress tracking.

```
## Checklist

### Phase 1: Core Implementation
- ☐ Create database schema
- ☐ Implement CRUD operations
- ☐ Test: Create and retrieve record
```

### Phases
Each phase has three sections:

**Affected Files**
- List EVERY file this phase touches
- Format: `path/to/file.py` - CREATE/UPDATE/DELETE - description

**Changes**
- Detailed descriptions of what to change
- Specific enough for AI to execute without clarification
- Numbered subsections (1.1, 1.2, etc.)

**Unit Tests**
- Tests for THIS phase
- Run after phase completion
- Expected outcomes specified

### Success Criteria
Measurable outcomes that define "done":

1. Feature X works as specified
2. Unit tests pass (100% coverage)
3. Documentation is complete

### Risks & Mitigations
Known risks and how to handle them:

| Risk | Mitigation |
|------|------------|
| Performance issue | Implement caching |
| API rate limit | Add retry logic with backoff |

### Level Upper Review
Document divergent thinking input:

**Counterintuitive Suggestions Received:**
1. Consider using event sourcing instead of direct DB writes
2. Make the service stateless from the start

**Incorporated:**
- Event sourcing architecture adopted

**Rejected (with rationale):**
- Stateless service: Too complex for this use case, needs local cache

---

## Status Tracking

The status file (`templates/build/status_template.md`) provides real-time progress visibility:

### Quick Status Table
| Metric | Value |
|--------|-------|
| Overall Progress | 45% |
| Current Phase | Phase 2 |
| Blocked? | No |

### Phase Progress
Checklist showing which phases are done/in progress/not started.

### Activity Log
Timestamped entries of key events:
- Build initialized
- Phase 1 complete
- Phase 2 started
- Blocker resolved

### Blockers
List any blockers preventing progress.

### Artifacts Created
Files generated during the build.

### Notes
Free-form notes, decisions, learnings.

---

## Key Principles

### 1. Plans are Execution Instructions
Write plans as if you're instructing a competent engineer who will execute autonomously. Be specific but concise.

### 2. No Exploration in Plans
Research happens BEFORE plan creation. Plans contain only execution steps, not discovery.

### 3. 2-4 Phases Max
Logically stacking phases, not overly granular. Each phase should be completable in one session.

### 4. Tests Inline with Phases
Don't have a separate "testing phase." Test each phase as you complete it.

### 5. Affected Files Explicit
List every file the build touches. This prevents scope creep and makes changes traceable.

### 6. Open Questions First
Surface unknowns at the top. Resolve before writing execution steps. This prevents planning around assumptions.

---

## Usage Examples

### Simple Feature Build

**User:** "I want to add a search feature to my notes app"

**System:**
1. Slug: `notes-search`
2. Initialize workspace
3. Architect creates plan:
   - Phase 1: Add search endpoint
   - Phase 2: Implement search logic
   - Phase 3: Add UI and tests
4. Level Upper suggests: "Consider full-text search library instead of regex"
5. Architect incorporates
6. Builder executes all phases

### Complex System Build

**User:** "I want to build an email intelligence system that summarizes and categorizes incoming emails"

**System:**
1. Slug: `email-intelligence-system`
2. Initialize workspace
3. Architect creates 4-phase plan:
   - Phase 1: Email ingestion pipeline
   - Phase 2: Summarization logic
   - Phase 3: Categorization engine
   - Phase 4: Dashboard and notifications
4. Level Upper suggests: "Batch processing for efficiency"
5. Architect incorporates
6. Builder executes each phase, updating status as they go

---

## Template Usage Guide

### Creating a Build Plan

1. **Initialize workspace:**
   ```bash
   python3 N5/scripts/init_build.py my-feature --title "My Feature"
   ```

2. **Edit PLAN.md:**
   - Replace `{{TITLE}}` with your feature name
   - Replace `{{SLUG}}` with your slug
   - Fill in open questions first
   - Define 2-4 phases
   - Write detailed changes for each phase
   - Specify success criteria

3. **Invoke Level Upper:**
   - Ask for counterintuitive suggestions
   - Document in Level Upper Review section
   - Incorporate what makes sense

4. **Get approval** and hand off to Builder

### Tracking Progress

Builder updates STATUS.md as work progresses:

```markdown
## Quick Status

| Metric | Value |
|--------|-------|
| Overall Progress | 75% |
| Current Phase | Phase 3 |
| Blocked? | No |

## Activity Log

| Timestamp | Event |
|-----------|-------|
| 2026-01-18 14:00 | Phase 1 complete |
| 2026-01-18 15:30 | Phase 2 complete |
| 2026-01-18 16:00 | Phase 3 started |
```

---

## Integration with N5OS Ode

### Persona Routing
The build flow integrates with the persona routing system:

- Operator routes to Architect when "build" is detected
- Architect routes to Level Upper for review
- Level Upper routes back to Architect
- Architect routes to Builder for execution

### Session State
Builds are tracked in session state:

```python
{
  "active_builds": {
    "notes-search": {
      "status": "in_progress",
      "current_phase": "Phase 2",
      "percent_complete": 45
    }
  }
}
```

### Protection
Build directories are protected with `.n5protected` to prevent accidental deletion.

---

## Advanced Features

### Parallel Execution
For builds with independent sub-tasks, phases can be split into parallel tracks:

```
### Phase 2: Parallel Work

**Track A: Backend**
- ☐ Implement API endpoints
- ☐ Add database layer

**Track B: Frontend**
- ☐ Create UI components
- ☐ Wire up API calls
```

### Conditional Phases
Phases that run only under certain conditions:

```
### Phase 4: Deployment (if deploying to production)
- ☐ Run integration tests
- ☐ Deploy to staging
- ☐ Run smoke tests
- ☐ Promote to production
```

### Rollback Plans
Include rollback steps in risky phases:

```
### Phase 3: Database Migration

**Rollback if migration fails:**
1. Restore database from backup
2. Verify data integrity
3. Alert team
```

---

## Best Practices

### DO
- Surface unknowns first in Open Questions
- Write execution steps, not exploration
- Be specific enough for autonomous execution
- Update checklists as you complete tasks
- Run tests after each phase
- Document blockers immediately

### DON'T
- Write plans that require clarification during execution
- Include research or discovery in execution steps
- Over-plan with too many granular phases
- Skip testing phases
- Forget to update STATUS.md
- Ignore risks — document them even if they seem unlikely

---

## References

- **Ben Guo's planning prompt**: https://www.zo.computer/prompts/plan-code-changes
- **Velocity Coding article**: https://0thernet.substack.com/p/velocity-coding
- **Plan template**: `templates/build/plan_template.md`
- **Status template**: `templates/build/status_template.md`
- **Templates README**: `templates/build/README.md`

---

## Version History

**v1.0** (2026-01-18)
- Initial build planning system
- Architect → Level Upper → Builder flow
- Plan and status templates
- Documentation