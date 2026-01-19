# Conversation Registry System

The Conversation Registry is a SQLite database that tracks all your conversations, their state, artifacts, issues, and learnings. It's the "memory" layer that enables N5OS Ode to understand your work history.

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Zo Conversation                       │
│                   (con_XXXX workspace)                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  SESSION_STATE.md                        │
│  - Type (build/research/discussion/planning)             │
│  - Focus and Objective                                   │
│  - Progress tracking                                     │
│  - Artifacts created                                     │
│  - Decisions made                                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼ (auto-sync)
┌─────────────────────────────────────────────────────────┐
│              N5/data/conversations.db                    │
│  - conversations table                                   │
│  - artifacts table                                       │
│  - issues table                                          │
│  - learnings table                                       │
│  - decisions table                                       │
└─────────────────────────────────────────────────────────┘
```

## Components

### SESSION_STATE.md

Created at the start of every conversation in the conversation workspace (`/home/.z/workspaces/con_XXX/`). Contains:

- **Metadata**: Type, mode, focus, objective, status
- **Progress**: Overall %, current phase, next actions
- **Covered**: What's been accomplished
- **Topics**: Key themes discussed
- **Key Insights**: Important discoveries
- **Decisions Made**: Choices with rationale
- **Open Questions**: Unresolved items
- **Artifacts**: Files created during the conversation

### conversations.db

Central SQLite database at `N5/data/conversations.db` with these tables:

#### conversations
Core metadata for each conversation.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PK | Conversation ID (con_XXX) |
| title | TEXT | Generated title |
| type | TEXT | build, research, discussion, planning |
| status | TEXT | active, complete, paused |
| mode | TEXT | standalone, worker, orchestrator, scheduled |
| created_at | TEXT | ISO timestamp |
| updated_at | TEXT | ISO timestamp |
| completed_at | TEXT | ISO timestamp (if complete) |
| focus | TEXT | Main focus of conversation |
| objective | TEXT | What we're trying to achieve |
| tags | TEXT | JSON array of tags |
| parent_id | TEXT | Parent conversation (for workers) |
| progress_pct | INT | 0-100 |
| workspace_path | TEXT | Path to conversation workspace |
| state_file_path | TEXT | Path to SESSION_STATE.md |
| aar_path | TEXT | Path to After-Action Report (if generated) |

#### artifacts
Files created during conversations.

| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto-increment ID |
| conversation_id | TEXT FK | Links to conversations.id |
| filepath | TEXT | Path to the artifact |
| artifact_type | TEXT | script, doc, config, etc. |
| created_at | TEXT | ISO timestamp |
| description | TEXT | What this artifact is |

#### issues
Problems encountered and their resolutions.

| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto-increment ID |
| conversation_id | TEXT FK | Links to conversations.id |
| timestamp | TEXT | When issue was encountered |
| severity | TEXT | low, medium, high, critical |
| category | TEXT | bug, blocker, question, etc. |
| message | TEXT | Issue description |
| context | TEXT | Additional context |
| resolution | TEXT | How it was resolved |
| resolved | INT | 0 or 1 |

#### learnings
Lessons extracted for future reference.

| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto-increment ID |
| conversation_id | TEXT FK | Links to conversations.id |
| lesson_id | TEXT UNIQUE | Unique lesson identifier |
| timestamp | TEXT | When lesson was extracted |
| type | TEXT | pattern, antipattern, technique, etc. |
| title | TEXT | Short title |
| description | TEXT | Full lesson description |
| principle_refs | TEXT | Related principles |
| status | TEXT | pending, applied, rejected |

#### decisions
Key decisions made with rationale.

| Column | Type | Description |
|--------|------|-------------|
| id | INT PK | Auto-increment ID |
| conversation_id | TEXT FK | Links to conversations.id |
| timestamp | TEXT | When decision was made |
| decision | TEXT | What was decided |
| rationale | TEXT | Why this choice |
| alternatives | TEXT | Other options considered |
| outcome | TEXT | Result of the decision |

## Scripts

### session_state_manager.py

Manages SESSION_STATE.md files.

```bash
# Initialize a new session state
python3 N5/scripts/session_state_manager.py init --convo-id con_XXX --type build

# Update a field
python3 N5/scripts/session_state_manager.py update --convo-id con_XXX --field status --value complete

# Bulk update sections
python3 N5/scripts/session_state_manager.py sync --convo-id con_XXX --json '{"Progress": {"Overall": "50%"}}'

# Check current state
python3 N5/scripts/session_state_manager.py check --convo-id con_XXX

# Audit for completeness
python3 N5/scripts/session_state_manager.py audit --convo-id con_XXX
```

### conversation_sync.py

Syncs SESSION_STATE.md to conversations.db.

```bash
# Initialize the database (creates tables if missing)
python3 N5/scripts/conversation_sync.py init

# Sync a single conversation
python3 N5/scripts/conversation_sync.py sync --convo-id con_XXX

# Sync all conversations with SESSION_STATE.md files
python3 N5/scripts/conversation_sync.py sync-all

# Query conversations
python3 N5/scripts/conversation_sync.py query --type build --status active --limit 20
```

## How It Works

### Conversation Lifecycle

1. **Start**: When a conversation begins, `session_state_manager.py init` creates SESSION_STATE.md
2. **Progress**: Throughout the conversation, the AI updates SESSION_STATE.md via the `update` and `sync` commands
3. **Sync**: Changes are automatically synced to conversations.db
4. **Close**: At conversation end, final state is synced and status updated to "complete"

### Auto-Classification

The system auto-classifies conversations based on keywords in the initial message:

| Type | Keywords |
|------|----------|
| build | implement, code, script, create, develop, fix, refactor |
| research | research, analyze, learn, study, investigate, explore |
| discussion | discuss, think, brainstorm, consider, talk |
| planning | plan, strategy, decide, organize, roadmap, design |

### Mode Detection

Conversations are assigned a mode:

| Mode | Description |
|------|-------------|
| standalone | Normal conversation |
| worker | Spawned by an orchestrator |
| orchestrator | Managing multiple workers |
| scheduled | Running on a schedule |

## Example Queries

```sql
-- Find all active build conversations
SELECT id, title, focus, progress_pct
FROM conversations
WHERE type = 'build' AND status = 'active'
ORDER BY updated_at DESC;

-- Find conversations with unresolved issues
SELECT c.id, c.title, i.message, i.severity
FROM conversations c
JOIN issues i ON c.id = i.conversation_id
WHERE i.resolved = 0
ORDER BY i.severity DESC;

-- Find recent learnings
SELECT l.title, l.description, c.title as conversation
FROM learnings l
JOIN conversations c ON l.conversation_id = c.id
WHERE l.status = 'pending'
ORDER BY l.timestamp DESC
LIMIT 10;

-- Find all artifacts created in the last week
SELECT a.filepath, a.artifact_type, c.title
FROM artifacts a
JOIN conversations c ON a.conversation_id = c.id
WHERE a.created_at > datetime('now', '-7 days')
ORDER BY a.created_at DESC;
```

## Integration with Rules

The "Session State Initialization" rule ensures every conversation gets a SESSION_STATE.md:

```
At the start of every conversation, check if SESSION_STATE.md exists.
If missing: create it with type, focus, and initial objective.
```

## Best Practices

1. **Let the system auto-classify** — Only override the type if the auto-classification is wrong
2. **Update progress regularly** — Every 3-5 exchanges, update the Progress section
3. **Log artifacts** — When creating files, add them to the Artifacts section
4. **Capture decisions** — When making important choices, log them with rationale
5. **Extract learnings** — At conversation close, identify reusable insights

## Troubleshooting

### "conversations.db not found"

Run initialization:
```bash
python3 N5/scripts/conversation_sync.py init
```

### "SESSION_STATE.md not found"

Initialize it manually:
```bash
python3 N5/scripts/session_state_manager.py init --convo-id con_XXX --type discussion
```

### Sync not working

Check database permissions:
```bash
ls -la N5/data/conversations.db
```

Manually trigger sync:
```bash
python3 N5/scripts/conversation_sync.py sync --convo-id con_XXX
```
