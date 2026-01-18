---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: worker_010_debug_logging
---

# Debug System

The debug system provides structured logging and circular pattern detection for troubleshooting and debugging conversations.

## Philosophy: Log While Working, Not After

**The Problem:** Building the tool isn't enough — you must USE it reflexively during debugging.

**The Solution:** Explicit triggers for logging attempts in real-time, creating a visible trail of problem-solving attempts.

---

## Components

1. **debug_logger.py** — CLI tool for logging and pattern detection
2. **debug-logging-auto-behavior.md** — Behavioral guidelines for when/how to log
3. **DEBUG_LOG.jsonl** — Log file created per conversation (in workspace)

---

## When to Log (Explicit Triggers)

### Trigger 1: After Attempting a Fix

Log when you try to fix something, run a command, or make a change and are about to check if it worked.

```bash
python3 N5/scripts/debug_logger.py append \
  --convo-id <current> \
  --component "<what you're fixing>" \
  --problem "<what's wrong>" \
  --hypothesis "<what you think will fix it>" \
  --actions "<what you just did>" \
  --outcome <success|failure|partial> \
  --notes "<any insights>"
```

### Trigger 2: Before 3rd Attempt on Same Problem

Log the current attempt, then check for circular patterns:

```bash
# Log the attempt
python3 N5/scripts/debug_logger.py append \
  --convo-id <current> \
  --component "api.py" \
  --problem "Rate limit 429" \
  --hypothesis "Add backoff" \
  --actions "Added exponential backoff" \
  --outcome partial \
  --notes "Testing 5s, 15s, 45s delays"

# Check for circular patterns
python3 N5/scripts/debug_logger.py patterns \
  --convo-id <current> --window 10 --threshold 2
```

If pattern detected → Stop and analyze OR switch to Debugger persona with planning.

### Trigger 3: When Stuck/Confused

Log what you know so far, then review recent attempts:

```bash
# Log current state
python3 N5/scripts/debug_logger.py append \
  --convo-id <current> \
  --component "build_process" \
  --problem "Build fails at test stage" \
  --hypothesis "Missing dependency" \
  --actions "Ran tests, checked requirements.txt" \
  --outcome partial \
  --notes "Unable to identify missing dep"

# Review recent attempts
python3 N5/scripts/debug_logger.py recent \
  --convo-id <current> --n 5 --format display
```

### Trigger 4: Prompt Execution Attempts

Log when executing workflow prompts that encounter errors or unexpected behavior.

```bash
python3 N5/scripts/debug_logger.py append \
  --convo-id <current> \
  --component "prompt:drive_meeting_ingestion" \
  --problem "Tool call did not complete when reading prompt file" \
  --hypothesis "Prompt file should be readable but tool errored" \
  --actions "Called read_file on Prompts/drive_meeting_ingestion.md" \
  --outcome failure \
  --notes "Switched to manual tool calls instead of prompt orchestration"
```

---

## CLI Usage

### Append Entry

```bash
python3 N5/scripts/debug_logger.py append \
  --convo-id con_xyz123 \
  --component "api.py" \
  --problem "Rate limit 429" \
  --hypothesis "Add backoff" \
  --actions "Added exponential backoff" \
  --outcome success \
  --notes "5s, 15s, 45s worked"
```

### Show Recent Entries

```bash
# Display format (human-readable)
python3 N5/scripts/debug_logger.py recent \
  --convo-id con_xyz123 --n 5 --format display

# JSON format (for scripts)
python3 N5/scripts/debug_logger.py recent \
  --convo-id con_xyz123 --n 10 --format json
```

### Detect Circular Patterns

```bash
python3 N5/scripts/debug_logger.py patterns \
  --convo-id con_xyz123 --window 10 --threshold 2
```

- `--window`: Number of recent entries to analyze (default: 10)
- `--threshold`: Minimum count to consider a pattern (default: 3)

**Output:**
- Warning message if circular patterns detected
- List of patterns with count and entry IDs

---

## Log File Structure

Entries are stored in `DEBUG_LOG.jsonl` in the conversation workspace:

```json
{
  "ts": "2026-01-18T23:00:00Z",
  "entry_id": "abc12345",
  "component": "api.py",
  "problem": "Rate limit 429",
  "hypothesis": "Add backoff",
  "actions": ["Added exponential backoff", "Tested delays"],
  "outcome": "success",
  "notes": "5s, 15s, 45s worked",
  "conv_id": "con_xyz123"
}
```

---

## Circular Pattern Detection

The `patterns` command detects when you're stuck in a loop:

**Detection Criteria:**
- Same component
- High text similarity in problem descriptions (> 70%)
- OR high keyword overlap (> 60%)

**When to Check:**
- After 2nd failure on same component
- Before 3rd attempt on same problem

**Response if Pattern Detected:**
```
⚠️  CIRCULAR PATTERN DETECTED

Problem: "Rate limit 429"
Component: "api.py"
Count: 3 attempts
Entry IDs: [abc123, def456, ghi789]

Recommendation: Stop and analyze approach before continuing.
```

---

## Behavioral Pattern

**OLD (Wrong):**
```
Think → Try fix → Check result → Think again → Try another fix
[No logging, patterns invisible, circular debugging undetected]
```

**NEW (Correct):**
```
Think → Log hypothesis → Try fix → Log outcome → Check patterns → Next attempt
[Logged trail, patterns visible, circular detection active]
```

---

## Integration with Vibe Operator

The Vibe Operator persona should:

1. **Detect build/debug context** — Check if `DEBUG_LOG.jsonl` exists in the workspace
2. **Log significant attempts** — After fix attempts (not trivial reads)
3. **Check patterns proactively** — After 2nd failure on same component
4. **Surface warnings to V** — When circular pattern is detected
5. **Consider Debugger persona** — If 3+ similar failures

---

## Quick Command Templates

### Success
```bash
python3 N5/scripts/debug_logger.py append \
  --convo-id $CONVO_ID --component "$COMPONENT" \
  --problem "$PROBLEM" --hypothesis "$HYPOTHESIS" \
  --actions "$ACTIONS" --outcome success --notes "$NOTES"
```

### Failure
```bash
python3 N5/scripts/debug_logger.py append \
  --convo-id $CONVO_ID --component "$COMPONENT" \
  --problem "$PROBLEM" --hypothesis "$HYPOTHESIS" \
  --actions "$ACTIONS" --outcome failure --notes "$NOTES"
```

### Check Recent + Patterns (After 2nd Failure)
```bash
python3 N5/scripts/debug_logger.py recent \
  --convo-id $CONVO_ID --n 5 --format display

python3 N5/scripts/debug_logger.py patterns \
  --convo-id $CONVO_ID --window 10 --threshold 2
```

---

## Reinforcement Checklist

Before claiming "done" on any debugging session:

- [ ] Significant attempts logged to `DEBUG_LOG.jsonl`
- [ ] Pattern check run (if 3+ attempts made)
- [ ] Root cause identified and logged
- [ ] Success entry logged with resolution notes

---

## Files

- **N5/scripts/debug_logger.py** — CLI tool
- **N5/prefs/operations/debug-logging-auto-behavior.md** — Behavioral guidelines
- **DEBUG_LOG.jsonl** — Per-conversation log file (created in workspace)

---

## Version

**Debug System v1.0**  
Updated: 2026-01-18