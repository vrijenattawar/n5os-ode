---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_T0QGg2ryaDjCTxVj
---

# Escalation Protocol

Pulse escalates via SMS when human attention is required.

## Escalation Events

| Event | Severity | Message Format |
|-------|----------|----------------|
| Build started | INFO | `[PULSE] Build {slug} STARTED. {n} Drops queued.` |
| Build complete | INFO | `[PULSE] Build {slug} COMPLETE. {n}/{n} Drops. Ready for review.` |
| Drop failed Filter | HIGH | `[PULSE] {slug} D{x.y} FAILED: {reason}. Review needed.` |
| Drop dead (15min) | HIGH | `[PULSE] {slug} D{x.y} DEAD. No response in 15min. Forensics spawned.` |
| All Drops in Stream dead | CRITICAL | `[PULSE] {slug} Stream {n} DEAD. Build halted. Intervention required.` |
| Build blocked | CRITICAL | `[PULSE] {slug} BLOCKED. No Drops can advance. Human needed.` |

## Message Guidelines

1. **Be terse.** SMS has character limits.
2. **Include slug and drop_id.** V needs to know what to look at.
3. **Include actionable info.** What does V need to do?
4. **No spam.** Batch multiple events if they occur within 60 seconds.

## Batching Rules

If multiple events occur within 60 seconds:
```
[PULSE] {slug} BATCH:
- D1.1 FAILED: reason
- D1.2 DEAD
- D1.3 COMPLETE
Review needed.
```

## Do Not Escalate

- Drop completed successfully (logged, not SMS'd)
- Drop spawned (logged, not SMS'd)
- Routine tick with no state change

## Implementation

```python
async def send_sms(message: str):
    """Send SMS via Zo's send_sms_to_user"""
    # Uses /zo/ask to invoke SMS capability
    prompt = f'''
    Send this SMS to V immediately:
    
    {message}
    
    Use send_sms_to_user tool. No other action needed.
    '''
    # ... API call
```

## V's Response Options

When V receives an escalation, they can:

1. **Check STATUS.md** — Refresh `N5/builds/{slug}/STATUS.md` in Zo
2. **Manual intervention** — Open new conversation, paste failed Drop brief, debug
3. **Stop build** — `python3 Skills/pulse/scripts/pulse.py stop {slug}`
4. **Resume** — `python3 Skills/pulse/scripts/pulse.py resume {slug}`
5. **Ignore** — If non-critical, let Pulse continue

## Forensics on Dead Drop

When a Drop is marked dead (15min timeout):
1. Forensics worker spawns automatically
2. Forensics checks the Drop's conversation workspace
3. Forensics writes report to `deposits/{drop_id}_forensics.json`
4. Report includes: last known state, any partial artifacts, likely cause
