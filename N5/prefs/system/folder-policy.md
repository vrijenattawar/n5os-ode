# Folder Policy System

**Module:** System Governance  
**Version:** 2.0.0  
**Date:** 2025-10-09  
**Priority:** HIGHEST — This principle overrides all other preferences

---

## Core Principle

**Folder-specific POLICY.md files take precedence over global preferences.**

If absent, default to global preferences in `file 'N5/prefs/prefs.md'` but flag for policy creation.

---

## Mandatory Check

**Always scan for and consult POLICY.md in the target folder before any interaction** (read, edit, add, delete).

If absent, default to global preferences in `file 'N5/prefs/prefs.md'` but flag for policy creation.

---

## POLICY.md Structure

### Required Sections

1. **Purpose**
   - What this folder contains
   - How it should be interpreted (program, database, documentation, etc.)

2. **Handling Rules**
   - How to interact with files in this folder
   - Collective vs. individual file handling
   - Required commands or workflows

3. **Safety Flags**
   - Data integrity concerns
   - Automation risks
   - Conflict resolution procedures

4. **Dependencies**
   - Related folders or systems
   - Required schemas or validation
   - Cross-references to other policies

5. **Overrides**
   - Which global rules this policy overrides
   - Explicit exemptions (what still applies)

6. **Anchors**
   - Links to root N5/prefs/prefs.md
   - Related issues or problems
   - Parent or child policies

### Example Structure

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
- [Root Policy](../prefs.md)
- Related schemas in `N5/schemas/` as needed
- Related Problems: [Issues this addresses]
```

---

## Naming Convention

Use **POLICY.md** (all caps) for consistency and easy sourcing by title.

Search pattern: `grep -r "POLICY.md" /home/workspace`

---

## Creation Protocol

When creating a new folder for structured content:

1. **Create POLICY.md first** before adding any files
2. **Include all required sections** (see above)
3. **Define handling rules explicitly** (commands vs. direct edits)
4. **Specify safety requirements** (validation, backups, dry-run)
5. **Link to relevant schemas** in N5/schemas/ or subfolder schemas/
6. **Anchor to parent policy** (usually N5/prefs/prefs.md)

---

## Override Mechanism

Folder policies can override **any global rule**. Document exemptions clearly.

### Precedence Hierarchy

1. **Folder POLICY.md** (highest precedence)
2. **N5/prefs/prefs.md** critical rules (safety overrides)
3. **Specialized preference modules** (system, operations, communication)
4. **Global defaults** (lowest precedence)

### Conflict Resolution

If conflict exists between:
- Folder policy and global prefs → **Folder policy wins**
- Folder policy and safety rules → **Escalate to user** for arbitration
- Two folder policies (nested) → **Child policy wins**

---

## Enforcement

### Manual Validation
Before any folder operation, AI must:
1. Check for POLICY.md existence
2. Read and parse policy if exists
3. Apply specified handling rules
4. Respect overrides and exemptions

### Automated Validation (Future)
- N5 command: `policy-validate` — Check policy adherence
- Timeline logging for manual overrides
- Audit trail for policy violations

---

## Example Policies

### Lists Folder
See `file 'Lists/POLICY.md'` for example:
- Treats lists as executable programs
- Requires command-based interaction (lists-add, lists-set)
- Overrides file protection for JSONL (allows validated edits)
- Links to schemas and knowledge base

### Knowledge Folder
- **Canonical knowledge root (SSOT):** `file 'Personal/Knowledge/'`
- **Compatibility shell:** `file 'Knowledge/'` (kept only for legacy paths; do not treat as primary)

The Knowledge compatibility shell SHOULD have `file 'Knowledge/POLICY.md'` (if not exists, create):
- Treats as a thin routing/compatibility layer, not the main repository
- SSOT requirements LIVE UNDER `Personal/Knowledge/**`
- Cross-reference standards
- MECE principles (from `file 'Personal/Knowledge/Architecture/ingestion_standards/INGESTION_STANDARDS.md'`)

---

## Tier Folders (Business Units)

Two top-level Tier roots are recognized and governed by this policy:

- `file 'Careerspan/'` — Primary business unit
- `file 'Zo Consultancy/'` — Parallel business unit

### Routing Rules
- Deliverables SSOT: all final deliverables live under `file 'Documents/Deliverables/'` with org buckets `Careerspan/` and `Zo Consultancy/`.
- Logs: centralized under `file 'N5/logs/'` with domain buckets (e.g., `knowledge/`, `records/`, `mirror/`).
- Staging raw assets: use `file 'Records/'` (Company/Personal) per existing conventions.
- System scripts, backups, runtime: under `file 'N5/'` (scripts/, backups/scripts/, runtime/...).

### Policy Requirements
- Each Tier root SHOULD contain a `POLICY.md` describing any additional handling rules.
- Cross-link Tier policies to this file and to `file 'N5/prefs/prefs.md'`.

---

## Related Files

- **Lists Policy Example:** `file 'Lists/POLICY.md'`
- **Ingestion Standards (canonical):** `file 'Personal/Knowledge/Architecture/ingestion_standards/INGESTION_STANDARDS.md'`
- **Operational Principles (canonical):** `file 'Personal/Knowledge/Architecture/principles/architectural_principles.md'`
- **Compatibility shells:**
  - `file 'Knowledge/architectural/ingestion_standards.md'`
  - `file 'Knowledge/architectural/operational_principles.md'`
- **File Protection:** `file 'N5/prefs/system/file-protection.md'`

---

## Change Log

### v2.0.0 — 2025-10-09
- Extracted from monolithic prefs.md
- Added detailed structure requirements
- Added creation protocol
- Clarified precedence hierarchy
- Added enforcement mechanisms
- Linked to example policies

