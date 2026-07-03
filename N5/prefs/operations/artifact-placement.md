# Artifact Placement Protocol

**Purpose:** Sandbox-first file creation with strict enforcement to prevent scattered files  
**Principles:** P5 (Anti-Overwrite), P7 (Dry-Run), P18 (Verify State), P21 (Document Assumptions)

---

## Core Rule

**SANDBOX FIRST: All files created in conversation sandbox by default**

```
Conversation Start → Sandbox established at /home/.z/workspaces/{convo_id}/
                                    ↓
             ALL file creation defaults to sandbox
                                    ↓
      Unless explicitly declared as permanent artifact
                                    ↓
           Conversation End → Review → Promote finals to workspace
```

**Strict Enforcement:** AI will ERROR/WARN if attempting to create file outside sandbox without prior declaration

---

## Routing Logic

### Scenario A: Temporary/Iterative Work
**Examples:** Experiments, drafts, scratch scripts, intermediate data

**Action:**
- No declaration needed
- Create directly in sandbox
- Fast, low friction

**At conversation end:** Reviewed and discarded unless promoted

### Scenario B: Permanent Artifacts  
**Examples:** N5 components, Knowledge docs, final scripts, production configs

**Action:**
1. **Declare FIRST:** 
   ```bash
   python3 /home/workspace/N5/scripts/session_state_manager.py declare-artifact \
     --convo-id con_XXX \
     --path "N5/scripts/foo.py" \
     --classification permanent \
     --rationale "Production script for X workflow"
   ```

2. **Then create** at declared path
3. Tracked in SESSION_STATE.md

**Path flexibility:** Can declare directory (e.g., "Knowledge/") and AI picks specific filename

---

## Validation

Before creating any file, validation checks:

1. **Exception paths** (always allowed):
   - `/home/workspace/N5/logs/`
   - `/home/workspace/N5/data/`
   - `/tmp/`

2. **Sandbox paths** (always allowed):
   - `/home/.z/workspaces/{convo_id}/*`

3. **Workspace paths** (require declaration):
   - `/home/workspace/*` → MUST be declared as permanent
   - Validation: `sandbox_enforcer.py` checks SESSION_STATE.md

4. **Violation response:**
   ```
   ⛔ SANDBOX VIOLATION ⛔
   File: /home/workspace/foo.py
   
   RULE: All files must be in sandbox unless declared permanent
   
   To fix: Declare first, then create
   OR: Create in sandbox instead
   ```

---

## Classification Guide

### Temporary (Conversation Workspace)

**Location:** `/home/.z/workspaces/{convo_id}/`

**Use for:**
- Scratch files, intermediate processing
- Downloaded web content (HTML, JSON responses)
- Analysis scripts that only run once
- Notes/planning specific to this conversation
- Any file that has no value after conversation ends

**Examples:**
- `search_results.json` — temporary API response
- `analyze_data.py` — one-off analysis script
- `planning_notes.md` — brainstorming doc
- `temp_output.txt` — intermediate data

### Permanent (User Workspace)

**Location:** `/home/workspace/`

**Use for:**
- Documents user wants to keep
- Reusable scripts/tools
- Knowledge base additions
- Data files for future reference
- System/N5 components

**Examples:**
- `Documents/analysis_report.md` — deliverable
- `N5/scripts/new_tool.py` — reusable utility
- `Knowledge/concepts/topic.md` — knowledge capture
- `Lists/project_tasks.jsonl` — action items

---

## Workflow

### 1. Declare Artifact

```bash
python3 /home/workspace/N5/scripts/session_state_manager.py \
  declare-artifact \
  --convo-id {current_convo_id} \
  --path "path/to/file" \
  --classification temporary|permanent \
  --rationale "Why this file, why this location"
```

**Or programmatically:**
```python
from session_state_manager import SessionStateManager
manager = SessionStateManager(convo_id)
manager.declare_artifact(
    path="Documents/report.md",
    classification="permanent",
    rationale="User deliverable for project analysis"
)
```

### 2. Verify No Conflicts

Check for:
- Existing file at path (would overwrite)
- Protected paths (`.n5protected` file present)
- Path makes sense for classification (temporary in user workspace = wrong)

### 3. Create Artifact

Use appropriate tool: `create_or_rewrite_file`, `edit_file`, shell commands, etc.

### 4. Update Status

```bash
python3 /home/workspace/N5/scripts/session_state_manager.py \
  update-artifact \
  --convo-id {current_convo_id} \
  --path "path/to/file" \
  --status created
```

---

## Status Lifecycle

- **📋 declared** — Planned but not yet created
- **✅ created** — File successfully created
- **📦 moved** — Relocated to different path
- **🗑️ deleted** — Removed (cleanup or mistake)

---

## Decision Tree

```
Need to create a file?
├─ User asked for it explicitly? → Permanent
├─ Reusable beyond this conversation? → Permanent
├─ Part of N5 system? → Permanent
├─ Intermediate/scratch? → Temporary
├─ Web download? → Temporary (unless user wants it)
└─ When in doubt? → Temporary (can always move later)
```

---

## Path Conventions

### Temporary Files
- `{convo_id}/scratch/` — general scratch space
- `{convo_id}/downloads/` — web content
- `{convo_id}/analysis/` — analysis scripts/outputs
- `{convo_id}/planning/` — conversation-specific planning

### Permanent Files
Follow existing structure:
- `Documents/` — user-facing docs
- `Knowledge/` — knowledge base additions
- `Lists/` — action items, tasks
- `N5/scripts/` — reusable tools
- `N5/data/` — persistent data
- `Records/` — staging for processing

---

## Conversation-End Review

When conversation ends, review artifacts:

1. List all artifacts: `session_state_manager.py list-artifacts`
2. For each **temporary** artifact:
   - Delete if truly scratch
   - Move to permanent if valuable
3. For each **permanent** artifact:
   - Verify it's in the right location
   - Add to appropriate index/registry
   - Tag for discoverability

---

## Anti-Patterns

❌ **Creating first, declaring later** — defeats the purpose  
❌ **"I'll put it anywhere and move it later"** — creates mess  
❌ **Temporary in user workspace** — wrong classification  
❌ **Permanent with no rationale** — undocumented decision  
❌ **Skipping conflict check** — potential overwrite  
❌ **Not updating status after creation** — stale registry

---

## Integration with Other Systems

### N5 Safety (`n5_protect.py`)
Before declaring permanent artifact in service directory:
```bash
python3 /home/workspace/N5/scripts/n5_protect.py check <path>
```

### Conversation End Workflow
Artifact registry feeds into conversation review process.

### Knowledge System
Permanent artifacts in `Knowledge/` should be added to appropriate indices.

---

## Examples

### Example 1: Analysis Script (Temporary)

```python
# BEFORE creating the script
manager.declare_artifact(
    path="/home/.z/workspaces/con_ABC123/analyze_logs.py",
    classification="temporary",
    rationale="One-off script to analyze service logs for debugging"
)

# CREATE the script
create_or_rewrite_file(
    "/home/.z/workspaces/con_ABC123/analyze_logs.py",
    content=script_content
)

# UPDATE status
manager.update_artifact_status(
    path="/home/.z/workspaces/con_ABC123/analyze_logs.py",
    new_status="created"
)
```

### Example 2: User Document (Permanent)

```python
# BEFORE creating the document
manager.declare_artifact(
    path="Documents/quarterly_review.md",
    classification="permanent",
    rationale="User-requested analysis summary for Q3 2025"
)

# CHECK for conflicts
if Path("/home/workspace/Documents/quarterly_review.md").exists():
    logger.warning("File exists, user confirm overwrite")

# CREATE the document
create_or_rewrite_file(
    "/home/workspace/Documents/quarterly_review.md",
    content=report_content
)

# UPDATE status
manager.update_artifact_status(
    path="Documents/quarterly_review.md",
    new_status="created"
)
```

### Example 3: N5 System Component (Permanent)

```python
# BEFORE creating the tool
manager.declare_artifact(
    path="N5/scripts/backup_manager.py",
    classification="permanent",
    rationale="New N5 utility for automated backup workflows"
)

# CHECK for safety
run_bash_command("python3 /home/workspace/N5/scripts/n5_protect.py check N5/scripts/")

# CREATE the tool
create_or_rewrite_file(
    "/home/workspace/N5/scripts/backup_manager.py",
    content=tool_content
)

# UPDATE status
manager.update_artifact_status(
    path="N5/scripts/backup_manager.py",
    new_status="created"
)
```

---

## Benefits

✅ **Reduces false placements** — forced to think before creating  
✅ **Prevents overwrites** — conflict check before creation  
✅ **Creates audit trail** — decision history for artifact locations  
✅ **Enables better cleanup** — clear temp vs. permanent distinction  
✅ **Improves organization** — intentional placement decisions  
✅ **Supports review** — conversation-end artifact review is systematic

---

**Version:** 1.0  
**Last Updated:** 2025-10-28  
**Related:** `file 'N5/scripts/session_state_manager.py'`, `file 'N5/prefs/prefs.md'`
