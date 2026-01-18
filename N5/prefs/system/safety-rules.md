# File Flow Safety Rules

**Purpose**: Prevent catastrophic mistakes in autonomous file routing

Updated: 2025-10-25

---

## Never Auto-Route (Always Queue for Review)

### Protected File Types
- `.db`, `.sqlite`, `.sqlite3` - Databases
- `.env`, `.credentials`, `.secret` - Secrets
- `.git`, `.gitignore` - Version control
- System configs: `.bashrc`, `.zshrc`, `.profile`

### Protected Paths
- Anything in `N5/` (system files)
- Anything in `Knowledge/` (SSOT)
- Anything in `Lists/` (action registry)
- Files starting with `.` (hidden/system)

### Directory Protection Markers (`.n5protected`)
- Directories containing `.n5protected` marker files are protected from accidental moves/deletes
- Used for:
  - Registered user service working directories (auto-protected)
  - Manually protected critical paths
  - Any directory that should not be moved without explicit confirmation
- AI must check for `.n5protected` markers before suggesting move/delete operations
- Commands: `n5-protect`, `n5-unprotect`, `n5-list-protected`, `n5-check-protected`

### Size Limits
- Files > 100MB → always review
- Files < 1KB → suspicious, always review

### Age Limits
- Files modified in last 24 hours → always review (might be active work)
- Files older than 2 years untouched → always review (might be archived for reason)

---

## Whitelist for Auto-Route

Only auto-route if ALL conditions met:
1. Confidence > threshold
2. File type recognized (resume, log, export)
3. NOT in protected paths
4. Size between 1KB - 100MB
5. Age between 1 day - 2 years
6. Extension in whitelist: `.pdf`, `.docx`, `.txt`, `.log`, `.md`, `.png`, `.jpg`

---

## Reversibility

All moves must be:
- Logged with source + destination
- Non-destructive (move, not delete)
- Reversible via rollback command

---

## Override Protocol

V can override safety rules by:
1. Explicitly correcting a queued file
2. Adding exception to file 'N5/config/safety_exceptions.json'
3. Adjusting thresholds in file 'N5/config/confidence_thresholds.json'

---

## Audit Requirements

- Daily: Review auto-routed files in digest
- Weekly: Review safety violations log
- Monthly: Review all moves for false positives
