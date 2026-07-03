# File Creation Protocol (AI Workflow)

**Purpose:** Step-by-step protocol for AI to follow when creating files  
**Enforcement:** Active validation before file creation  
**Principles:** P5 (Anti-Overwrite), P7 (Dry-Run), P18 (Verify State), P21 (Document Assumptions)

---

## Core Rule

**VALIDATE BEFORE CREATE:** All file creation must validate path first against sandbox-first protocol.

---

## AI Workflow (MANDATORY)

### Step 1: Determine Target Path

```python
# Where does this file need to go?
if temporary_work_in_progress or conversation_specific:
    target_path = f"/home/.z/workspaces/{current_convo_id}/filename.ext"
elif permanent_deliverable:
    # Declare first (see Step 2)
    target_path = "/home/workspace/appropriate/location/filename.ext"
```

### Step 2: Validate Path (BEFORE CREATION)

```python
import subprocess
from pathlib import Path

# Get current conversation ID
current_convo_id = "con_XXX"  # From context or environment

# Validate path
result = subprocess.run(
    ["python3", "/home/workspace/N5/scripts/validate_file_path.py",
     target_path, "--convo-id", current_convo_id],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    # ⛔ SANDBOX VIOLATION
    print(result.stdout)  # Shows remediation steps
    
    # Option A: Declare as permanent first
    subprocess.run([
        "python3", "/home/workspace/N5/scripts/session_state_manager.py",
        "declare-artifact",
        "--convo-id", current_convo_id,
        "--path", "relative/path/to/file.ext",
        "--classification", "permanent",
        "--rationale", "Why this file needs to be permanent"
    ])
    # Then retry validation with --declared flag
    
    # Option B: Create in sandbox instead
    target_path = f"/home/.z/workspaces/{current_convo_id}/filename.ext"
    
    return  # Stop and fix before proceeding
```

### Step 3: Create File

```python
# ✅ Validation passed or path declared - safe to create
create_or_rewrite_file(target_path, content)
```

### Step 4: Update Artifact Status (if declared)

```python
# If file was declared permanent, update status
if permanent_file:
    subprocess.run([
        "python3", "/home/workspace/N5/scripts/session_state_manager.py",
        "update-artifact",
        "--convo-id", current_convo_id,
        "--path", "relative/path/to/file.ext",
        "--status", "created"
    ])
```

---

## Exception Paths (Always Allowed)

These paths bypass sandbox enforcement:

- `/home/workspace/N5/logs/` - System logs
- `/home/workspace/N5/data/` - Data files
- `/tmp/` - Temporary system files

---

## Quick Decision Tree

```
Need to create a file?
│
├─ Is it N5/logs/, N5/data/, or /tmp/?
│  └─ ✅ Create directly (exception path)
│
├─ Is it temporary/work-in-progress?
│  └─ ✅ Create in sandbox: /home/.z/workspaces/{convo_id}/
│
└─ Is it permanent/deliverable?
   ├─ 1. Declare artifact first
   ├─ 2. Validate path
   └─ 3. Create file
```

---

## Common Patterns

### Pattern 1: Sandbox Work File (Most Common)

```python
# No declaration needed - just create in sandbox
target = f"/home/.z/workspaces/{convo_id}/draft_analysis.md"
create_or_rewrite_file(target, content)
```

### Pattern 2: Permanent Knowledge File

```python
# 1. Declare
subprocess.run([
    "python3", "/home/workspace/N5/scripts/session_state_manager.py",
    "declare-artifact", "--convo-id", convo_id,
    "--path", "Knowledge/topic/new_concept.md",
    "--classification", "permanent",
    "--rationale", "Canonical reference for X concept"
])

# 2. Validate
result = validate_path("/home/workspace/Knowledge/topic/new_concept.md", convo_id, 
                       declared=["Knowledge/topic/new_concept.md"])
if result != 0:
    return

# 3. Create
create_or_rewrite_file("/home/workspace/Knowledge/topic/new_concept.md", content)

# 4. Update status
update_artifact_status(convo_id, "Knowledge/topic/new_concept.md", "created")
```

### Pattern 3: N5 System Component

```python
# 1. Declare
subprocess.run([
    "python3", "/home/workspace/N5/scripts/session_state_manager.py",
    "declare-artifact", "--convo-id", convo_id,
    "--path", "N5/scripts/new_tool.py",
    "--classification", "permanent",
    "--rationale", "New system utility for X"
])

# 2. Validate
result = validate_path("/home/workspace/N5/scripts/new_tool.py", convo_id,
                       declared=["N5/scripts/new_tool.py"])
if result != 0:
    return

# 3. Create
create_or_rewrite_file("/home/workspace/N5/scripts/new_tool.py", content)

# 4. Update status
update_artifact_status(convo_id, "N5/scripts/new_tool.py", "created")
```

---

## Violation Response

When validation fails:

```
⛔ SANDBOX VIOLATION ⛔

Attempted to create file outside sandbox without declaration:
  Path: /home/workspace/Documents/report.md
  
RULE: All files must be created in sandbox unless explicitly declared as permanent.

Sandbox: /home/.z/workspaces/con_XXX

To create this file in workspace:
1. Declare it first:
   python3 /home/workspace/N5/scripts/session_state_manager.py declare-artifact \
     --convo-id con_XXX \
     --path "Documents/report.md" \
     --classification permanent \
     --rationale "Why this file needs to be permanent"

2. Then create the file

OR: Create in sandbox instead (recommended for iterative work)
```

**Action:** Follow the remediation steps. Do NOT bypass validation.

---

## Integration Points

**Loaded by:**
- `file 'N5/prefs/prefs.md'` → Safety & Review section
- `file 'N5/prefs/operations/artifact-placement.md'` → High-level protocol
- This file → Detailed AI workflow

**Tools:**
- `validate_file_path.py` - Pre-creation validation (convenience wrapper)
- `sandbox_enforcer.py` - Core validation engine
- `session_state_manager.py` - Artifact declaration/tracking

**Related:**
- `file 'Documents/N5.md'` → Core System Paths
- `recipe 'Close Conversation'` → End-of-conversation promotion workflow

---

## Testing

```bash
# Test sandbox path (should pass)
python3 /home/workspace/N5/scripts/validate_file_path.py \
  "/home/.z/workspaces/con_XXX/test.md" \
  --convo-id con_XXX

# Test workspace path without declaration (should fail)
python3 /home/workspace/N5/scripts/validate_file_path.py \
  "/home/workspace/test.md" \
  --convo-id con_XXX

# Test workspace path with declaration (should pass)
python3 /home/workspace/N5/scripts/validate_file_path.py \
  "/home/workspace/test.md" \
  --convo-id con_XXX \
  --declared "test.md"

# Test exception path (should pass)
python3 /home/workspace/N5/scripts/validate_file_path.py \
  "/home/workspace/N5/logs/test.log" \
  --convo-id con_XXX
```

---

**Version:** 1.0  
**Last Updated:** 2025-10-28  
**Status:** Production - Mandatory for all file creation
