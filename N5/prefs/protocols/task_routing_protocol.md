---
name: Task Routing Protocol
version: 1.0
status: active
created: 2025-10-22
---
# Task Routing Protocol

## Purpose
Automatically detect when the user is requesting tasks and route them through the appropriate automation system (n8n → Akiflow) instead of handling manually.

## Recognition Patterns

### Priority 1: Explicit Command Prefix (ALWAYS route)
```
aki: <description>
aki-add <description>
@aki <description>
```
**Action:** Route immediately to Akiflow, no confirmation needed.

### Priority 2: HIGH Confidence Patterns (auto-route)
Phrases that indicate task creation intent:
- "I need to..." / "Tomorrow I need to..."
- "Draft [X] by [time]"
- "Review [X]" / "Send [X]" / "Follow up with [X]"
- "Schedule [X]"
- "Warm intro: [Person A] → [Person B]"
- "Action items from [meeting]"
- Meeting notes with implicit tasks
- "Add this to my tasks" / "Put this on my list"

### Priority 3: MEDIUM Confidence (ask confirmation)
- General planning: "I should probably..."
- Vague timing: "Sometime next week..."
- Discussion without clear deadline

### Priority 4: LOW Confidence (respond in chat)
- Questions: "What should I do about X?"
- Brainstorming: "Ideas for X?"
- Research: "Look into X"

## Routing Decision Tree

```
the user's message
  ↓
Contains task indicators? (action verb + object + optional timing)
  ↓ YES → HIGH/MEDIUM confidence
  |
  ├─ Has specific deadline/time? 
  |    ↓ YES → AUTO-ROUTE to n8n
  |    ↓ NO  → Ask: "Should I add this to Akiflow?"
  |
  ↓ NO → LOW confidence
  └─ Respond in chat (no task creation)
```

## Workflow Mapping

### Warm Intro Pattern
**Trigger:** "Connect [Person A] with [Person B]" OR "Intro: [A] → [B]"

**Action:** Route to n8n webhook
**Data structure:**
```json
{
  "text": "<full context>",
  "context": {
    "type": "warm_intro",
    "person_a": "Name (Role)",
    "person_b": "Name (Role)",
    "reason": "context",
    "deadline": "parsed from 'by [time]'"
  }
}
```

**Expected output:** 3 tasks in Akiflow
1. Draft intro (15m, High)
2. Send intro (5m, High, 1 hour later)
3. Follow-up (10m, Normal, +7 days)

### Meeting Notes Pattern
**Trigger:** "Meeting notes:" OR "Action items from [meeting]:"

**Action:** Route to n8n webhook
**Data structure:**
```json
{
  "text": "<full meeting notes>",
  "context": {
    "type": "meeting_recap",
    "meeting": "Meeting name",
    "date": "YYYY-MM-DD"
  }
}
```

**Expected output:** N tasks extracted, each with duration/priority/project

### Ad-hoc Task Pattern
**Trigger:** "[Action verb] [object] [by time]"

**Action:** Route to n8n webhook
**Data structure:**
```json
{
  "text": "Task description with timing",
  "context": {
    "type": "adhoc_task"
  }
}
```

**Expected output:** 1-3 tasks in Akiflow

## Execution Steps

### 1. Detect Pattern
Parse the user's message for task indicators (action verbs, timing, people, deliverables)

### 2. Classify Confidence
HIGH/MEDIUM/LOW based on specificity

### 3. Route Appropriately
**If HIGH confidence:**
```python
# POST to n8n webhook
curl -X POST https://<your-n8n-host>/webhook/akiflow/tasks \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "context": {...}}'
```

**If MEDIUM confidence:**
Ask: "Should I add this to Akiflow? (Default: Yes in 5 sec)"

**If LOW confidence:**
Respond in chat

### 4. Confirm to the user
After routing:
- "✓ Routed to Akiflow via n8n. You should see [N] tasks in ~30 seconds."
- List what was extracted (title, time, project)
- Offer to adjust if needed

### 5. Monitor for Feedback
If the user says "That's not what I meant" or corrects:
- Learn from the pattern
- Offer to delete/modify via Aki
- Update this protocol

## Response Templates

### After successful route:
```
✓ Routed to Akiflow:
- [Task 1 title] @ [time] ([duration], [priority], [project])
- [Task 2 title] @ [time] ([duration], [priority], [project])

Should appear in ~30 seconds. Need adjustments?
```

### When asking for confirmation:
```
Detected task: "[summary]"
Add to Akiflow? (I'll route it via n8n → Aki)
```

### When uncertain:
```
I'm not sure if this is a task request or discussion. 
Want me to add it to Akiflow?
```

## Error Handling

**If n8n webhook fails:**
1. Log error to conversation workspace
2. Fall back to direct `akiflow-push` script
3. Notify the user: "n8n had an issue, used direct push instead"

**If Aki doesn't create tasks:**
1. Wait 60 seconds
2. Offer to resend or check Aki email
3. CC the user's personal email if still failing

## Learning Loop

Track these metrics in session:
- Detection accuracy (did I correctly identify a task?)
- False positives (routed when the user didn't want a task)
- False negatives (missed a task the user wanted)
- Adjust patterns based on the user's corrections

## Integration Points

**Files:**
- This protocol: file 'N5/prefs/protocols/task_routing_protocol.md'
- Zo profile: file '<your builder profile doc>'
- Akiflow integration: file '<your task-integration status doc>'

**Services:**
- n8n workflow: https://<your-n8n-host>
- Zo API: http://localhost:8770
- Webhook: https://<your-n8n-host>/webhook/akiflow/tasks

## Change Log
- 2025-10-22: Created v1.0 - Pattern recognition, routing rules, error handling
