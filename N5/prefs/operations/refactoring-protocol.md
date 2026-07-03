# Refactoring Safety Protocol

**Purpose:** Prevent data loss during system reorganizations  
**Version:** 1.0  
**Created:** 2025-10-28  
**Trigger:** ANY "refactor," "reorganize," "consolidate," or "migrate" operation

---

## MANDATORY CHECKLIST

Before ANY refactoring operation involving file moves or deletions:

### Phase 1: PLANNING (THINK)
- [ ] Load `file 'Knowledge/architectural/planning_prompt.md'`
- [ ] Load `file 'N5/prefs/operations/dependency-graph-review.md'`
- [ ] Identify trap doors (irreversible decisions)
- [ ] List affected directories/files
- [ ] Estimate scope: number of files, total size
- [ ] Define success criteria explicitly
- [ ] Run graph review on each shared target:
  ```bash
  python3 Skills/codebase-graph/scripts/query.py index
  python3 Skills/codebase-graph/scripts/query.py review <target>
  ```
- [ ] If graph review returns `HIGH`, inspect `rdeps` and stage the work before moving files or rewriting shared code

### Phase 2: PREPARATION (PLAN)
- [ ] Create explicit backup:
  ```bash
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  cp -r SOURCE_DIR /home/workspace/.n5_backups/refactor_${TIMESTAMP}_$(basename SOURCE_DIR)
  ```
- [ ] Document backup location
- [ ] Git commit current state: `git add -A && git commit -m "Pre-refactor snapshot: [description]"`

### Phase 3: DRY RUN (VERIFY)
- [ ] **Count source files:**
  ```bash
  SOURCE_COUNT=$(find SOURCE_DIR -type f | wc -l)
  echo "Source files: $SOURCE_COUNT"
  ```
- [ ] **Execute with --dry-run:**
  ```bash
  rsync -av --dry-run SOURCE_DIR/ DEST_DIR/
  # OR
  mv --dry-run SOURCE_DIR DEST_DIR  # if supported
  # OR
  ls -R SOURCE_DIR > /tmp/pre_move.txt
  ```
- [ ] **Review dry-run output** - verify intended behavior

### Phase 4: EXECUTE (MOVE FAST, DON'T BREAK THINGS)
- [ ] Execute migration/copy:
  ```bash
  rsync -av SOURCE_DIR/ DEST_DIR/
  # OR
  cp -r SOURCE_DIR DEST_DIR/
  ```
- [ ] **Count destination files:**
  ```bash
  DEST_COUNT=$(find DEST_DIR -type f | wc -l)
  echo "Destination files: $DEST_COUNT"
  ```
- [ ] **Verify counts match:**
  ```bash
  if [ "$SOURCE_COUNT" -ne "$DEST_COUNT" ]; then
    echo "ERROR: File count mismatch! Source=$SOURCE_COUNT, Dest=$DEST_COUNT"
    exit 1
  fi
  ```

### Phase 5: SAMPLE VERIFICATION
- [ ] **Verify 3-5 sample files** (compare SHA256 or manually inspect):
  ```bash
  sha256sum SOURCE_DIR/file1.md DEST_DIR/file1.md
  sha256sum SOURCE_DIR/file2.md DEST_DIR/file2.md
  sha256sum SOURCE_DIR/file3.md DEST_DIR/file3.md
  ```
- [ ] **Verify content integrity** (spot-check critical files)

### Phase 6: DELETION (ONLY IF ALL ABOVE PASS)
- [ ] **Re-verify destination exists and is complete**
- [ ] Execute deletion:
  ```bash
  rm -rf SOURCE_DIR
  # OR
  mv SOURCE_DIR /home/workspace/.trash/$(date +%Y%m%d_%H%M%S)_$(basename SOURCE_DIR)
  ```
- [ ] **Final verification** - ensure destination still intact after source deletion

### Phase 7: POST-OPERATION VERIFICATION (REVIEW)
- [ ] Confirm operation succeeded:
  ```bash
  ls -la DEST_DIR/
  find DEST_DIR -type f | wc -l
  ```
- [ ] Test accessing 3-5 files from new location
- [ ] Update any references to old paths
- [ ] Document in system bulletins:
  ```bash
  echo "Refactored: moved N files from SOURCE to DEST" >> N5/logs/refactors.log
  ```
- [ ] Git commit with accurate message

---

## RED FLAGS - STOP IMMEDIATELY IF:

🚨 **File counts don't match**  
🚨 **Sample files don't match (different SHA256)**  
🚨 **Dry-run shows unexpected behavior**  
🚨 **Operation involves >100 files and no backup created**  
🚨 **Any step fails or produces errors**

---

## Example: Correct Refactoring Flow

```bash
# 1. PLAN
echo "Refactoring meetings from Projects/Meetings to N5/records/meetings"

# 2. BACKUP
cp -r Projects/Meetings /home/workspace/.n5_backups/refactor_example_Meetings
git add -A && git commit -m "Pre-refactor: backup Projects/Meetings"

# 3. DRY RUN & COUNT
SOURCE_COUNT=$(find Projects/Meetings -type f | wc -l)
echo "Source has $SOURCE_COUNT files"
rsync -av --dry-run Projects/Meetings/ N5/records/meetings/

# 4. EXECUTE
rsync -av Projects/Meetings/ N5/records/meetings/

# 5. VERIFY
DEST_COUNT=$(find N5/records/meetings -type f | wc -l)
echo "Destination has $DEST_COUNT files"

if [ "$SOURCE_COUNT" -ne "$DEST_COUNT" ]; then
  echo "ABORT: Counts don't match!"
  exit 1
fi

# 6. SAMPLE CHECK
sha256sum Projects/Meetings/2025-10-12_file1.md N5/records/meetings/2025-10-12_file1.md

# 7. DELETE (only if all above passed)
mv Projects/Meetings /home/workspace/.trash/20251028_Meetings

# 8. FINAL VERIFY
ls -la N5/records/meetings/
find N5/records/meetings -type f | wc -l
```

---

## When to Use This Protocol

**REQUIRED for:**
- Moving >10 files
- Deleting >10 files
- Any "refactor," "reorganize," "consolidate," "migrate" operation
- Any changes to N5/records/, N5/data/, Knowledge/, Lists/

**OPTIONAL for:**
- Single file operations
- Creating new files (no deletion involved)
- Editing existing files in place

---

## Integration with Principles

This protocol enforces:
- **P5 (Anti-Overwrite):** Explicit backups before destructive operations
- **P7 (Dry-Run First):** Mandatory dry-run phase
- **P11 (Failure Modes):** Red flags and abort conditions
- **P15 (Complete Before Claiming):** Verify migration succeeded before deletion
- **P18 (Verify State):** Multiple verification checkpoints
- **P19 (Error Handling):** Explicit error detection and rollback
- **P30/P36:** Structural coupling made visible before refactor work

---

**Authority:** Vibe Builder Persona  
**Status:** ACTIVE  
**Incident Reference:** 2025-10-28 Meeting Data Loss (RCA: file '/home/.z/workspaces/con_sArdmG34hyHA7q6N/ROOT_CAUSE_ANALYSIS.md')
