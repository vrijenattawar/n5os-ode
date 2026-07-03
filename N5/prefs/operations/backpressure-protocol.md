---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_eIykmXaCiLjaN8Yf
---

# Backpressure Protocol

**Purpose:** Define when and how to run backpressure validation during builds, interpret results, and configure per-build overrides.

**Related:**
- `N5/prefs/operations/orchestrator-protocol.md` - Main orchestrator workflow
- `N5/prefs/operations/mece-worker-framework.md` - MECE validation
- `N5/scripts/backpressure.py` - The validation script
- `N5/config/backpressure_rules.yaml` - Global defaults

---

## When to Run Backpressure

### During Builds

| Trigger | Required | Notes |
|---------|----------|-------|
| After each worker completes | ✓ | Before marking worker "done" |
| Before launching Wave N+1 | ✓ | All Wave N must pass first |
| Before final merge/close | ✓ | Last quality gate |
| During extended worker execution | Optional | Spot-check if worried |

### Outside Builds

| Trigger | Recommended |
|---------|-------------|
| Before committing substantial changes | ✓ |
| After major refactors | ✓ |
| When preparing a PR | ✓ |
| Debugging test failures | ✓ |

---

## How to Run

### Basic Usage

```bash
# Validate a build by slug
python3 N5/scripts/backpressure.py <slug>

# Validate a specific path
python3 N5/scripts/backpressure.py --path N5/scripts/

# JSON output for programmatic use
python3 N5/scripts/backpressure.py <slug> --json
```

### With Custom Config

```bash
# Use per-build config
python3 N5/scripts/backpressure.py <slug> --config N5/builds/<slug>/backpressure.yaml
```

---

## Interpreting Results

### Exit Codes

| Code | Status | Meaning |
|------|--------|---------|
| 0 | **PASS** | All validators passed |
| 1 | **WARN** | Some warnings but no failures |
| 2 | **FAIL** | At least one validator failed |

### Status Actions

#### PASS (exit 0)
- ✅ Proceed with next step
- ✅ Worker can be marked complete
- ✅ Dependent workers can launch
- ✅ Merge is safe

#### WARN (exit 1)
- ⚠️ Review warnings before proceeding
- ⚠️ Decide if warnings are acceptable (style-only, known issues)
- ⚠️ Document decision if proceeding despite warnings
- ⚠️ Consider fixing warnings if low effort

#### FAIL (exit 2)
- ❌ Worker MUST address issues before proceeding
- ❌ Do NOT launch dependent workers
- ❌ Do NOT merge

### Handling Persistent FAIL

If a worker cannot resolve FAIL after 2-3 attempts:

1. **Check struggle detector:**
   ```bash
   python3 N5/scripts/struggle_detector.py --build-slug <slug>
   ```

2. **If STRUGGLING/STUCK:** Consider loop runner for fresh context
   ```bash
   python3 N5/scripts/loop_runner.py --prompt <brief.md> --build-slug <slug>
   ```

3. **If still failing:** Escalate to the user with:
   - Error details from backpressure output
   - Struggle detector findings
   - What was tried
   - Proposed solutions

---

## Validators

The backpressure script runs these validators:

### pytest
- **What:** Runs test suite
- **Pass:** All tests pass
- **Warn:** N/A
- **Fail:** Any test fails
- **Skipped when:** No `pytest.ini`, `pyproject.toml` with pytest config, or test files found

### ruff (or flake8 fallback)
- **What:** Python linting
- **Pass:** No errors
- **Warn:** Style warnings only
- **Fail:** Syntax or import errors
- **Skipped when:** Neither ruff nor flake8 installed

### mypy
- **What:** Type checking
- **Pass:** No type errors
- **Warn:** Missing stubs or minor issues
- **Fail:** Type errors in code
- **Skipped when:** No mypy configuration found

---

## Per-Build Configuration

Place a `backpressure.yaml` file in the build folder to override defaults.

### Location
```
N5/builds/<slug>/backpressure.yaml
```

### Schema

```yaml
# Which validators to run (default: all)
validators:
  pytest: true
  ruff: true
  mypy: false  # Skip type checking for this build

# Paths to check (default: build folder + N5/scripts/)
paths:
  - N5/scripts/
  - Sites/my-site/src/

# Files/patterns to exclude
exclude:
  - "*.test.py"
  - "migrations/"

# Treat warnings as errors
strict: false

# Custom pytest args
pytest_args: "--ignore=tests/integration/"
```

### Example: Minimal Config

```yaml
# Only run tests, skip linting
validators:
  pytest: true
  ruff: false
  mypy: false
```

### Example: Strict Mode

```yaml
# All validators, warnings = fail
validators:
  pytest: true
  ruff: true
  mypy: true
strict: true
```

---

## Relationship to MECE Validation

**MECE validation** and **backpressure** serve different purposes:

| Aspect | MECE Validation | Backpressure |
|--------|-----------------|--------------|
| **When** | Before launching workers | After workers complete |
| **What** | Worker scope/boundaries | Code quality/correctness |
| **Script** | `mece_validator.py` | `backpressure.py` |
| **Catches** | Overlaps, gaps, token issues | Test failures, lint errors, type errors |

**Both are required** for a healthy build process:
1. MECE ensures workers won't conflict
2. Backpressure ensures workers produce quality output

---

## Reading JSON Output

When using `--json`, the output structure is:

```json
{
  "overall_status": "PASS|WARN|FAIL",
  "validators": {
    "pytest": {
      "status": "PASS|WARN|FAIL|SKIP",
      "message": "12 passed",
      "details": { ... }
    },
    "ruff": {
      "status": "WARN",
      "message": "3 style warnings",
      "warnings": ["E501: line too long", ...]
    },
    "mypy": {
      "status": "SKIP",
      "message": "not configured"
    }
  },
  "stub": false,
  "path": "/home/workspace/N5/builds/my-build/",
  "timestamp": "2026-01-19T20:00:00Z"
}
```

**Important:** Check `"stub": true` — this indicates fallback mode when validators couldn't be found. Real validation did not occur.

---

## Dashboard Integration

The build dashboard (`N5/scripts/build_dashboard.py`) calls backpressure with `--json` and displays:

```
├── BACKPRESSURE                                        │
│  ├─ pytest    PASS (12 passed)                       │
│  ├─ ruff      WARN (3 style warnings)                │
│  └─ mypy      SKIP (not configured)                  │
│  Overall: WARN                                       │
```

Use the dashboard for at-a-glance build health.

---

## Troubleshooting

### "ruff not found"
```bash
pip install ruff
```

### "mypy not found"
```bash
pip install mypy
```

### "No tests found"
- Ensure test files follow `test_*.py` or `*_test.py` naming
- Check pytest is configured in `pyproject.toml` or `pytest.ini`
- Verify test directory is in the validated path

### Validator always SKIP
- Check that the tool is installed
- Check that config files exist (pytest.ini, pyproject.toml, mypy.ini)
- Try running the validator directly to diagnose

---

## Quick Reference

```bash
# Standard build validation
python3 N5/scripts/backpressure.py ralph-learnings

# Path validation
python3 N5/scripts/backpressure.py --path N5/scripts/

# JSON for scripting
python3 N5/scripts/backpressure.py ralph-learnings --json

# Custom config
python3 N5/scripts/backpressure.py my-build --config my-build/backpressure.yaml
```

**Exit codes:** 0=PASS, 1=WARN, 2=FAIL
