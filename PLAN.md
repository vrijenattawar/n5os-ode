---
created: 2026-01-15
last_edited: 2026-01-15
version: 1
provenance: con_KsG8Cyc7SlXm5lHr
---
# N5OS-Ode Release Fix Plan

**Objective:** Bring n5os-ode to release quality by fixing broken references, missing files, and placeholder values.

**Estimated effort:** 2-3 hours  
**Repo:** https://github.com/vrijenattawar/n5os-ode  
**Local path:** `N5/export/n5os-ode/`

---

## Priority 1: Critical Blockers (Must Fix)

### Task 1.1: Fix PROJECT_REPO Placeholders

**Problem:** Six scripts have `https://github.com/PROJECT_REPO/n5os-ode` instead of real URL.

**Files to update:**
- [ ] `N5/scripts/n5_load_context.py` (line 12)
- [ ] `N5/scripts/content_ingest.py` (line 11)
- [ ] `N5/scripts/debug_logger.py` (line 15)
- [ ] `N5/scripts/journal.py` (line 28)
- [ ] `N5/scripts/n5_protect.py` (line 13)
- [ ] `N5/scripts/session_state_manager.py` (line 19)

**Action:** Replace `PROJECT_REPO` with `vrijenattawar`

**Verification:** `rg "PROJECT_REPO" .` returns no results

---

### Task 1.2: Create Missing `init_build.py` Script

**Problem:** `Prompts/Build Capability.prompt.md` references `scripts/init_build.py` which doesn't exist.

**Action:** Create `N5/scripts/init_build.py` with minimal functionality:
- Accept `<slug>` and `--title` arguments
- Create build workspace at `N5/builds/<slug>/`
- Generate `PLAN.md` and `STATUS.md` scaffolds
- Print confirmation message

**Scaffold structure:**
```
N5/builds/<slug>/
├── PLAN.md          # Build plan template
├── STATUS.md        # Progress tracker
└── artifacts/       # Output directory
```

**Verification:** `python3 N5/scripts/init_build.py test-build --title "Test Build"` creates the directory structure

---

### Task 1.3: Add 9 Missing Context Files

**Problem:** `N5/prefs/context_manifest.yaml` references files that don't exist, causing `n5_load_context.py` to fail or produce incomplete loads.

**Files to create (minimal stubs are acceptable):**

| File | Purpose | Stub Content |
|------|---------|--------------|
| `N5/prefs/operations/planning_prompt.md` | Build/research planning template | Planning principles + template |
| `Knowledge/architectural/principles.md` | System design principles | Core N5 architectural tenets |
| `N5/schemas/index.schema.json` | Index file JSON schema | Basic schema definition |
| `Lists/POLICY.md` | List management policies | SSOT principles |
| `N5/scripts/n5_safety.py` | Safety validation script | Basic safety checks |
| `N5/prefs/operations/scheduled-task-protocol.md` | Agent/scheduler guidelines | Scheduling best practices |
| `N5/prefs/communication/style-guide.md` | Writing style guide | Tone, voice, formatting |

**Note:** Create directory `N5/prefs/operations/` and `N5/prefs/communication/` if they don't exist.

**Verification:** `python3 N5/scripts/n5_load_context.py build` completes without errors

---

### Task 1.4: Fix or Remove Close Conversation Prompt

**Problem:** `Prompts/Close Conversation.prompt.md` references 10+ scripts/files that don't exist in the export.

**Options (choose one):**

**Option A (Recommended): Simplify the prompt**
- Remove references to non-existent scripts
- Keep the conceptual workflow (session close, state sync)
- Make it a manual/guidance prompt rather than automated

**Option B: Remove entirely**
- Delete the prompt
- Update any references to it

**Action:** Implement Option A — rewrite to be self-contained

**Verification:** Read through prompt, confirm no `file '...'` references to non-existent files

---

### Task 1.5: Fix Broken Links in prefs.md

**Problem:** `N5/prefs/prefs.md` has broken relative links.

**Fixes:**
- [ ] `(../README.md)` → `(../../README.md)`
- [ ] `(../docs/ARCHITECTURE.md)` → Remove or create stub
- [ ] `(../docs/CONTRIBUTING.md)` → Remove or create stub

**Recommendation:** Create minimal `N5/docs/ARCHITECTURE.md` and `N5/docs/CONTRIBUTING.md` stubs.

**Verification:** All markdown links in `N5/prefs/prefs.md` resolve to existing files

---

## Priority 2: Important Improvements

### Task 2.1: Add LICENSE File

**Problem:** No explicit license for open-source distribution.

**Action:** Create `LICENSE` file with MIT License text (or your preferred license).

**Template:**
```
MIT License

Copyright (c) 2026 Vrijen Attawar

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

### Task 2.2: Document PyYAML Dependency

**Problem:** `docs/DEPENDENCIES.md` says "no external packages required" but `n5_load_context.py` requires PyYAML.

**Options:**
1. Add PyYAML to documented dependencies
2. Add graceful fallback in `n5_load_context.py` when PyYAML missing

**Recommendation:** Option 1 — update `docs/DEPENDENCIES.md`:
```markdown
## Python Dependencies

- **PyYAML** — Required for context loading (`pip install pyyaml`)
```

---

### Task 2.3: Fix Journal Prompt Script Paths

**Problem:** `Prompts/Journal.prompt.md` references `scripts/journal.py` (relative) instead of `N5/scripts/journal.py`.

**Action:** Update all script references in the prompt to use full path `N5/scripts/journal.py`

---

## Priority 3: Polish

### Task 3.1: Create N5/docs/ Directory with Stubs

**Action:** Create:
- `N5/docs/ARCHITECTURE.md` — High-level system architecture
- `N5/docs/CONTRIBUTING.md` — How to contribute/extend

These can be brief (100-200 words each).

---

### Task 3.2: Add N5/README.md

**Problem:** `N5/prefs/prefs.md` links to `../README.md` expecting an N5-specific README.

**Action:** Create `N5/README.md` with:
- What the N5 directory contains
- Quick reference to scripts
- Link to main README

---

### Task 3.3: Validate All Prompts

**Action:** Run through each prompt file and verify:
- [ ] No references to non-existent files
- [ ] Script paths are correct (`N5/scripts/` not `scripts/`)
- [ ] YAML frontmatter is valid

**Prompts to check:**
- `Prompts/Build Capability.prompt.md`
- `Prompts/Close Conversation.prompt.md`
- `Prompts/Journal.prompt.md`
- `Prompts/Blocks/*.prompt.md` (6 files)
- `Prompts/reflections/*.prompt.md` (4 files)

---

## Verification Checklist

Run these commands after all fixes:

```bash
# 1. No placeholder URLs
rg "PROJECT_REPO" . && echo "FAIL: Placeholders remain" || echo "PASS"

# 2. All Python files compile
python3 -m py_compile N5/scripts/*.py && echo "PASS" || echo "FAIL"

# 3. Context loading works
python3 N5/scripts/n5_load_context.py build && echo "PASS" || echo "FAIL"

# 4. Init build works
python3 N5/scripts/init_build.py verify-test --title "Verification Test" && echo "PASS" || echo "FAIL"

# 5. No broken internal links (run link checker)
# Manual review of markdown links

# 6. LICENSE exists
test -f LICENSE && echo "PASS" || echo "FAIL"
```

---

## File Creation Summary

**New files to create:**
1. `N5/scripts/init_build.py`
2. `N5/prefs/operations/planning_prompt.md`
3. `N5/prefs/operations/scheduled-task-protocol.md`
4. `N5/prefs/communication/style-guide.md`
5. `N5/scripts/n5_safety.py`
6. `N5/schemas/index.schema.json`
7. `Knowledge/architectural/principles.md`
8. `Lists/POLICY.md`
9. `N5/docs/ARCHITECTURE.md`
10. `N5/docs/CONTRIBUTING.md`
11. `N5/README.md`
12. `LICENSE`

**Files to edit:**
1. `N5/scripts/n5_load_context.py` — fix URL
2. `N5/scripts/content_ingest.py` — fix URL
3. `N5/scripts/debug_logger.py` — fix URL
4. `N5/scripts/journal.py` — fix URL
5. `N5/scripts/n5_protect.py` — fix URL
6. `N5/scripts/session_state_manager.py` — fix URL
7. `N5/prefs/prefs.md` — fix broken links
8. `Prompts/Close Conversation.prompt.md` — simplify/rewrite
9. `Prompts/Journal.prompt.md` — fix script paths
10. `Prompts/Build Capability.prompt.md` — fix script paths
11. `docs/DEPENDENCIES.md` — add PyYAML

---

## Commit Strategy

Suggested commits:
1. `fix: replace PROJECT_REPO placeholders with actual repo URL`
2. `feat: add init_build.py script for build capability workflow`
3. `feat: add missing context files referenced in manifest`
4. `fix: simplify Close Conversation prompt to remove dead references`
5. `fix: correct relative links in prefs.md and prompt files`
6. `docs: add LICENSE, ARCHITECTURE, CONTRIBUTING`
7. `docs: update DEPENDENCIES to include PyYAML requirement`

---

## Success Criteria

The release is ready when:
- [ ] A fresh Zo user can run BOOTLOADER without errors
- [ ] `@Build Capability` workflow completes successfully  
- [ ] `@Journal` commands work as documented
- [ ] `n5_load_context.py` loads all context groups without errors
- [ ] No broken file references in any prompt
- [ ] LICENSE file present
- [ ] All verification checks pass

