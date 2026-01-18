---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: worker_008_safety_system
---

# Safety System - Folder Policy and File Protection

**Overview**: N5OS Ode includes a comprehensive safety layer that prevents catastrophic mistakes through folder-specific policies, file protection markers, and controlled blast radius operations.

---

## .n5protected Marker System

The `.n5protected` marker file provides lightweight directory protection against accidental moves, deletions, and bulk operations.

### How It Works

Place a `.n5protected` file in any directory to mark it as protected:

```bash
python3 N5/scripts/n5_protect.py protect <path> --reason "description"
```

This creates a JSON marker file containing:
- Protection status
- Reason for protection
- Creation timestamp
- Optional PII flags

### Commands

```bash
# Protect a directory
python3 N5/scripts/n5_protect.py protect /path/to/dir --reason "Critical system files"

# Check if a path is protected
python3 N5/scripts/n5_protect.py check /path/to/dir

# List all protected directories
python3 N5/scripts/n5_protect.py list

# Remove protection
python3 N5/scripts/n5_protect.py unprotect /path/to/dir

# Mark a directory as containing PII
python3 N5/scripts/n5_protect.py mark-pii /path/to/dir --categories email,phone --note "User records"
```

### PII Tracking

The protection system can track directories containing personally identifiable information (PII):

**Valid PII Categories**: `email`, `phone`, `name`, `health`, `financial`, `ssn`, `address`, `dob`

```bash
# Protect with PII flags
python3 N5/scripts/n5_protect.py protect /path/to/data --reason "User database" --pii --pii-categories email,phone

# List only PII directories
python3 N5/scripts/n5_protect.py list-pii
```

---

## Protected Paths and File Types

### Never Auto-Route (Always Queue for Review)

The following are protected from automated routing operations:

#### Protected File Types
- `.db`, `.sqlite`, `.sqlite3` — Databases
- `.env`, `.credentials`, `.secret` — Secrets and credentials
- `.git`, `.gitignore` — Version control
- System configs: `.bashrc`, `.zshrc`, `.profile`

#### Protected Paths
- **`N5/`** — All system files and configuration
- **`Knowledge/`** — Single source of truth knowledge base
- **`Lists/`** — Action registry and lists
- Any file starting with `.` — Hidden/system files
- Any directory containing `.n5protected` marker

#### Size and Age Limits
- **Files > 100MB** — Always review
- **Files < 1KB** — Suspicious, always review
- **Modified in last 24 hours** — Active work, always review
- **Older than 2 years** — Archived, always review

### Whitelist for Auto-Route

Files are only auto-routed if ALL conditions are met:
1. Confidence above threshold
2. File type recognized (resume, log, export)
3. NOT in protected paths
4. Size between 1KB - 100MB
5. Age between 1 day - 2 years
6. Extension in whitelist: `.pdf`, `.docx`, `.txt`, `.log`, `.md`, `.png`, `.jpg`

---

## POLICY.md Override Pattern

The Folder Policy System establishes a clear precedence hierarchy for determining how files should be handled.

### Precedence Hierarchy

1. **Folder POLICY.md** (highest precedence)
2. **N5/prefs/prefs.md** critical rules
3. **Specialized preference modules** (system, operations, communication)
4. **Global defaults** (lowest precedence)

### POLICY.md Structure

Every structured folder should have a `POLICY.md` file with these sections:

```markdown
# [Folder Name] Policy

## Purpose
Brief description of folder role and contents.

## Handling Rules
- Rule 1
- Rule 2

## Safety Flags
- Flag 1
- Flag 2

## Dependencies
- Anchors to: [Related files/policies]
- Relies on: [Commands/schemas]

## Overrides
- Overrides: [Global rules]
- Exempts: [Still-applicable rules]

## Anchors
- [Root Policy](../N5/prefs/prefs.md)
- [Related Schema](../N5/schemas/index.schema.json)
```

### Required Sections

1. **Purpose** — What this folder contains, how it should be interpreted
2. **Handling Rules** — How to interact with files (collective vs individual, commands vs direct edits)
3. **Safety Flags** — Data integrity concerns, automation risks, conflict resolution
4. **Dependencies** — Related folders, required schemas, cross-references
5. **Overrides** — Which global rules this policy overrides, explicit exemptions
6. **Anchors** — Links to root preferences, related issues, parent/child policies

### Override Mechanism

Folder policies can override **any global rule**:

- **Folder vs. global prefs** → Folder policy wins
- **Folder vs. safety rules** → Escalate to user for arbitration
- **Nested folder policies** → Child policy wins

---

## Blast Radius Control Philosophy

The safety system is designed to minimize the impact of any single mistake through controlled blast radius operations.

### Core Principles

1. **Never Auto-Route Protected Items** — Critical files always require human review
2. **Logging and Reversibility** — All moves are logged with source/destination and can be rolled back
3. **Protection Markers** — `.n5protected` prevents accidental bulk operations
4. **Override Protocol** — Clear paths for V to override safety rules when needed
5. **Audit Requirements** — Regular review of auto-routed files and safety violations

### Reversibility

All file operations must be:
- Logged with source + destination
- Non-destructive (move, not delete)
- Reversible via rollback command

### Override Protocol

V can override safety rules by:
1. Explicitly correcting a queued file
2. Adding exception to `N5/config/safety_exceptions.json`
3. Adjusting thresholds in `N5/config/confidence_thresholds.json`

### Audit Requirements

- **Daily**: Review auto-routed files in digest
- **Weekly**: Review safety violations log
- **Monthly**: Review all moves for false positives

---

## Implementation Files

### Core Files

- **`N5/prefs/system/folder-policy.md`** — POLICY.md governance system
- **`N5/prefs/system/safety-rules.md`** — File flow safety rules
- **`N5/scripts/n5_protect.py`** — Protection marker implementation

### Usage in AI Behavior

When working with files, the AI should:

1. **Check for POLICY.md** in the target folder before any interaction
2. **Check for .n5protected** markers before move/delete operations
3. **Apply safety rules** to determine if auto-routing is appropriate
4. **Log operations** for audit trail and reversibility
5. **Ask for confirmation** when override is needed

---

## Examples

### Example 1: Protecting a Critical Directory

```bash
# Protect the Knowledge base
python3 N5/scripts/n5_protect.py protect Knowledge --reason "SSOT knowledge base - must not be moved"

# AI checks before attempting operations
python3 N5/scripts/n5_protect.py check Knowledge
# Output: ⚠️ This path is protected
#        Reason: SSOT knowledge base - must not be moved
```

### Example 2: Folder-Specific Policy

The `Lists/` folder has a `POLICY.md` that overrides global file protection:

```markdown
# Lists Policy

## Purpose
Executable action registry - lists are programs, not data files

## Handling Rules
- Must use commands: lists-add, lists-set, lists-query
- Never edit JSONL files directly
- Commands validate schema on every operation

## Overrides
- Overrides: File protection for JSONL files
- Allows: Validated edits through command layer

## Anchors
- [Root Policy](../N5/prefs/prefs.md)
```

### Example 3: PII Protection

```bash
# Protect a directory containing user data
python3 N5/scripts/n5_protect.py protect Records/user-data --reason "PII user records" --pii --pii-categories email,phone,ssn

# List all PII directories
python3 N5/scripts/n5_protect.py list-pii
# Output: ⚠️  Records/user-data
#        Categories: email, phone, ssn
```

---

## See Also

- [Folder Policy System](../N5/prefs/system/folder-policy.md) — Full governance specification
- [File Flow Safety Rules](../N5/prefs/system/safety-rules.md) — Detailed safety rules
- [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) — Directory conventions
- [PRINCIPLES.md](PRINCIPLES.md) — Architectural principles including P15 (Complete Before Claiming)

---

*Documentation generated for N5OS Ode v1.0*