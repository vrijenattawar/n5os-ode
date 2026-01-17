---
created: 2025-10-15
last_edited: 2025-12-26
version: 3.0
description: |
  Spawn parallel worker threads through deliberate decomposition.
  
  YOU (the LLM) write the complete worker assignment.
  The script ONLY saves the file and links to parent.
  
  This is a CONSCIOUS process:
  1. Read context (SESSION_STATE + immediate request)
  2. Scope the work deliberately
  3. Write complete worker assignment(s)
  4. Call script to save
tool: true
tags:
  - workers
  - parallel
  - orchestration
  - decomposition
---

# Spawn Worker Thread

## Philosophy

Spawning a worker is a **deliberate decomposition act**, not a mechanical handoff.

You already have:
- **Immediate context:** What was just asked
- **SESSION_STATE:** The larger context of what's being built

Your job is to:
1. **Read and understand** both contexts
2. **Scope the work** - What exactly should this worker do?
3. **Write a complete assignment** - Everything the worker needs
4. **Save via script** - Pure plumbing

## The Workflow

### Step 1: Gather Context

Read the parent's SESSION_STATE:
```bash
cat /home/.z/workspaces/con_XXXXX/SESSION_STATE.md
```

Combine with the immediate request from the conversation.

### Step 2: Scope the Work

Ask yourself:
- What is the discrete unit of work?
- What does the worker need to know?
- What are the deliverables?
- What are the success criteria?

### Step 3: Write the Assignment

Write a complete worker assignment file. Use this structure:

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: con_PARENT_ID
---

# WORKER ASSIGNMENT: [Descriptive Title]

**Assigned to:** Zo ([Mode: Builder/Researcher/Writer/etc.])
**Objective:** [One clear sentence describing the mission]

## Context from Parent

[Brief summary of parent context - what larger thing is being built, key decisions already made, relevant constraints]

## Your Mission

[Detailed description of what this worker should accomplish]

## Information Containers / Deliverables

[Specific, structured outputs the worker should produce]

### 1. [Deliverable Name]
- [Specific items to include]

### 2. [Deliverable Name]
- [Specific items to include]

## Success Criteria

1. [Measurable criterion]
2. [Measurable criterion]
3. [Measurable criterion]

## Reference Files

- `file 'path/to/relevant/file'`
- `file 'path/to/another/file'`

---

**INSTRUCTION FOR SUB-AGENT:**
[Direct, actionable instruction for the worker. Be specific about tools to use, approach to take, and how to report completion.]
```

### Step 4: Save via Script

Write your assignment to a temp file, then call the script:

```bash
# Write assignment to conversation workspace
cat > /home/.z/workspaces/con_XXXXX/worker_assignment_draft.md << 'EOF'
[Your complete assignment content]
EOF

# Save and link to parent
python3 N5/scripts/spawn_worker.py \
    --parent con_XXXXX \
    --content-file /home/.z/workspaces/con_XXXXX/worker_assignment_draft.md
```

### Step 5: Report

Tell the user:
- What worker was spawned
- Where the assignment file is
- How to start the worker (open file in new conversation)

## Good vs Bad Assignments

### ❌ BAD: Template Garbage
```markdown
# Worker Assignment - Parallel Thread

**Parent Focus:** _Not specified_
**Parent Objective:** TBD

## Your Mission
No specific instruction provided
```
This is useless. The worker has no idea what to do.

### ✅ GOOD: Deliberate Assignment
```markdown
# WORKER ASSIGNMENT: Zorg Research Phase

**Assigned to:** Zo (Researcher Mode)
**Objective:** Research best practices for puzzle-based adventures.

## Context from Parent
Building "Zorg" - an ARG/puzzle game for N5 onboarding. Core elements locked in CORE_ELEMENTS_LOCKDOWN.md. Need research on game design patterns before implementation.

## Your Mission
Research DEF CON CTF and ARG design patterns. Focus on puzzle taxonomy, player flow, and scaffolding.

## Deliverables
### 1. Puzzle Taxonomy
- Ciphers, file mechanics, logic puzzles, social engineering

### 2. Flow & Scaffolding
- The "Aha!" moment, failure handling, skip paths

## Success Criteria
1. Create RESEARCH_DOSSIER.yaml with findings
2. Provide reflection on what's missing from current plan
3. 3-paragraph executive summary

## Reference Files
- `file 'N5/builds/vibe-arg/CORE_ELEMENTS_LOCKDOWN.md'`
- `file 'N5/builds/vibe-arg/PLAN.md'`

---
**INSTRUCTION FOR SUB-AGENT:**
Use web_research and web_search. Focus on "Game Design for CTFs" and "ARG narrative scaffolding." Write the dossier, then respond with reflection.
```

This tells the worker exactly what to do, why, and how to succeed.

## ID-Only Mode

If you want to generate IDs first and write the file yourself:

```bash
python3 N5/scripts/spawn_worker.py --parent con_XXXXX --generate-ids
```

Returns:
```json
{
  "worker_id": "WORKER_XXXXX_20251226_143000",
  "timestamp": "2025-12-26T14:30:00.000000+00:00",
  "filename": "WORKER_ASSIGNMENT_20251226_143000_000000_XXXXX.md",
  "output_path": "/home/workspace/Records/Temporary/WORKER_ASSIGNMENT_...",
  "parent_workspace": "/home/.z/workspaces/con_XXXXX",
  "worker_updates_dir": "/home/.z/workspaces/con_XXXXX/worker_updates"
}
```

Then write your assignment directly to `output_path`.

## Worker Communication

Workers write status to `{parent_workspace}/worker_updates/`:

| File | Purpose |
|------|---------|
| `WORKER_XXX_status.md` | Progress updates |
| `WORKER_XXX_completion.md` | Final summary |
| `WORKER_XXX_artifacts/` | Generated files |

## Version History

- **v3.0** (2025-12-26): LLM-first rewrite. Script is pure plumbing. LLM writes all content.
- **v2.1** (2025-12-10): Added --context JSON (deprecated)
- **v1.0**: Initial implementation

