# Thread Closure Command Triggers

**Module:** Operations\
**Version:** 1.0.0\
**Date:** 2025-10-16\
**Purpose:** Define explicit mappings from user phrases to the correct thread closure command

---

## The Two Commands

### `conversation-end`

**Purpose:** File organization, workspace cleanup, git check\
**Use when:** Closing conversation naturally, organizing workspace

### `thread-export`

**Purpose:** AAR generation, documentation, archiving for continuation\
**Use when:** Exporting for reference, continuing work in new thread

---

## User Phrase Mapping

### Triggers for `conversation-end`

**ALWAYS use** `conversation-end` **when user says:**

- "End conversation"
- "End this conversation"
- "Wrap up"
- "Close thread"
- "Close this thread"
- "Let's wrap this up"
- "conversation-end" (explicit command)
- "Done for now"
- "That's all for today"

**Purpose:** User wants to cleanly close the conversation and organize files

---

### Triggers for `thread-export`

**ALWAYS use** `thread-export` **when user says:**

- "Export this thread"
- "Create an AAR"
- "Generate AAR"
- "Export conversation"
- "thread-export" (explicit command)
- "I want to continue this in a new thread"
- "Document this work"
- "Archive this"

**Purpose:** User wants comprehensive documentation and plans to continue

---

## Default Behavior

**When user says "end conversation" or similar:**\
→ Run `conversation-end` (NOT `thread-export`)

**Only run** `thread-export` **if:**

- User explicitly requests export/AAR
- User indicates they want to continue work in new thread
- User asks for documentation of the work

---

## Combined Usage

**User can request both:**\
"End conversation and export thread"\
→ Run `thread-export` first (creates AAR)\
→ Then run `conversation-end` (organizes files)

**Order matters:** thread-export first, conversation-end second

---

## Examples

| User Says | Command to Run | Why |
| --- | --- | --- |
| "End this conversation" | `conversation-end` | Standard closure |
| "Wrap up" | `conversation-end` | Standard closure |
| "Export this thread" | `thread-export` | Explicit export request |
| "End conversation and create AAR" | Both (export first, then end) | Explicit combined request |
| "Done for now" | `conversation-end` | Standard closure |
| "I want to continue this in a new thread" | `thread-export` | Continuation planned |

---

## Anti-Patterns to Avoid

❌ **Don't:** Run `thread-export` when user says "end conversation"\
✅ **Do:** Run `conversation-end` for standard closures

❌ **Don't:** Assume user wants AAR every time\
✅ **Do:** Only create AAR when explicitly requested or continuation is planned

❌ **Don't:** Ask "do you want to export?" every time\
✅ **Do:** Follow the trigger mapping and run the appropriate command

---

## Decision Tree

```markdown
User wants to close thread?
│
├─ Did they say "export", "AAR", "continue", "archive"?
│  ├─ YES → thread-export
│  └─ NO → Continue below
│
└─ Did they say "end", "wrap up", "close", "done"?
   └─ YES → conversation-end
```

---

## Integration with Existing Commands

Both commands are registered in `file 'N5/data/executables.db'` :

```json
{"command": "conversation-end", "file": "N5/commands/conversation-end.md", ...}
{"command": "thread-export", "file": "N5/commands/thread-export.md", ...}
```

Both have corresponding scripts:

- `file N5/scripts/n5_conversation_end.py` 
- `file N5/scripts/n5_thread_export.py` 

---

## Testing

**To verify correct behavior:**

1. User says "end conversation" → Should run `conversation-end`
2. User says "export this thread" → Should run `thread-export`
3. User says "wrap up" → Should run `conversation-end`
4. User says "create an AAR" → Should run `thread-export`

**If wrong command runs:**

- Check this mapping file
- Verify recipe registration
- Check for conflicting instructions in user rules

---

## Maintenance

**Update this file when:**

- New closure phrases are identified
- User reports wrong command being triggered
- New closure workflows are added

**Review:**

- After any conversation-end or thread-export confusion
- When commands are refactored
- Quarterly as part of preference review