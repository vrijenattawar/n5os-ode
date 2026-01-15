---
created: 2025-12-15
last_edited: 2026-01-15
version: 1.0
provenance: n5os-ode-bootstrap
---

# Scheduled Task Protocol

How to create and manage scheduled tasks (agents) in n5OS-Ode.

## Creating a Task

Via the `create_agent` tool:

```python
create_agent(
    rrule="FREQ=DAILY;BYHOUR=9;BYMINUTE=0",  # RFC 5545
    instruction="Your task instruction here",
    delivery_method="email"  # optional
)
```

## RRULE Examples

- `FREQ=DAILY;BYHOUR=9;BYMINUTE=0` → Every day at 9 AM
- `FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=14;BYMINUTE=30` → Mon/Wed/Fri at 2:30 PM
- `FREQ=DAILY;BYMONTH=11;BYMONTHDAY=5;BYHOUR=8;BYMINUTE=0;COUNT=1` → One-time on Nov 5 at 8 AM

## Instruction Guidelines

- **Complete**: Include all context the agent needs
- **Actionable**: Don't schedule meta-tasks (e.g., "schedule a task")
- **Atomic**: One clear objective per task
- **Resilient**: Handle missing files, network errors gracefully

## Monitoring

Use `list_agents` to view all tasks and their next run times.

Use `edit_agent` to update instructions or pause/resume.

Use `delete_agent` to remove (requires explicit confirmation for cornerstone tasks marked with ⇱).

