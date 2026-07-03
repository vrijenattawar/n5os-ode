# Conversation Initialization Protocol

**Version:** 1.0  
**Created:** 2025-10-29  
**Purpose:** Ensure EVERY conversation gets proper initialization

> **⚠️ Superseded — read this first.** This v1.0 doc predates `N5/SESSION_STATE_POLICY.md`, which is now authoritative. Session state is now **OFF by default** — it is opt-in per lane (multi-phase build/orchestration, Pulse/drop/build-close, or work that must resume or produce structured closeout). Do **not** auto-create `SESSION_STATE.md` for ordinary conversations, quick Q&A, lookups, or small edits. Treat the "before ANYTHING / non-negotiable" language below as historical context only. Follow `N5/SESSION_STATE_POLICY.md` for the current decision procedure. The hourly `auto_init_conversation.py` fallback and `conversations.db` audit trail referenced below are optional live-system infrastructure and do **not** ship with the base distribution.

---

## Critical Rule

**BEFORE DOING ANYTHING in a conversation, check if SESSION_STATE.md exists.**

If it doesn't exist:

```bash
python3 /home/workspace/N5/scripts/session_state_manager.py init \
  --convo-id <current_conversation_id> \
  --load-system
```

**This MUST happen before:**
- Responding to user
- Creating any files
- Running any commands
- Loading any context

---

## Why This Matters

Without initialization:
- ❌ Conversation not tracked in database
- ❌ No SESSION_STATE to track progress
- ❌ Conversation-end will completely fail
- ❌ Title generation has nothing to work with
- ❌ Thread export fails
- ❌ No audit trail

With initialization:
- ✅ Database entry created
- ✅ SESSION_STATE.md file with templates
- ✅ Proper type classification (build/research/discussion/planning)
- ✅ Conversation-end will work
- ✅ Title generation has data
- ✅ Full tracking and auditability

---

## Auto-Classification

The init system will auto-detect conversation type from the first message:
- Keywords "build", "implement", "code", "script", "create" → build
- Keywords "research", "analyze", "learn", "study" → research  
- Keywords "discuss", "think", "explore", "brainstorm" → discussion
- Keywords "plan", "strategy", "decide", "organize" → planning
- Default: discussion

---

## Automatic Fallback

**Scheduled task runs every hour:**
```bash
python3 /home/workspace/N5/scripts/auto_init_conversation.py
```

This catches any conversations that slip through without manual initialization.

---

## Implementation

### For AI (Me)
1. Check for SESSION_STATE.md at conversation start
2. If missing, run init IMMEDIATELY
3. Wait for init to complete before proceeding
4. Report to user that initialization happened

### For System
1. Auto-init script runs hourly via scheduled task
2. Scans all conversation workspaces
3. Initializes any without SESSION_STATE
4. Logs initialization activity

---

## Validation

To check if a conversation is initialized:
```bash
# Check for SESSION_STATE
ls /home/.z/workspaces/<convo_id>/SESSION_STATE.md

# Check database
sqlite3 /home/workspace/N5/data/conversations.db \
  "SELECT id, title, type, status FROM conversations WHERE id='<convo_id>';"
```

---

**Status:** Superseded by `N5/SESSION_STATE_POLICY.md` — session state is opt-in / off by default. Historical reference only.
