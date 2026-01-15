---
created: 2025-12-10
last_edited: 2025-12-10
version: 2.0
title: Journal
description: Start a guided reflection session or manage journal entries
tags: [journal, reflection, writing, personal]
tool: true
---

# Journal System

Quick journaling and guided reflection system with SQLite storage.

## Guided Reflections (Conversational)

Start an adaptive, conversational reflection session:

| Invoke | Description | Duration |
|--------|-------------|----------|
| `@Morning Pages` | Stream-of-consciousness morning clearing | 5-10 min |
| `@Evening Reflection` | Process the day and prepare for rest | 5-10 min |
| `@Weekly Review` | Zoom out, recognize patterns, set direction | 10 min |
| `@Gratitude` | Deep appreciation practice | 5 min |

Each reflection is a guided conversation—the AI asks adaptive questions, you respond, and at the end it compiles and saves the entry to your journal database.

## Quick CLI Commands

For manual/non-conversational journaling:

```bash
# Start a new entry
python3 scripts/journal.py new morning_pages
python3 scripts/journal.py new evening
python3 scripts/journal.py new gratitude
python3 scripts/journal.py new weekly_review
python3 scripts/journal.py new journal  # general

# List recent entries
python3 scripts/journal.py list
python3 scripts/journal.py list --type evening --days 7

# View specific entry
python3 scripts/journal.py view 42

# Search entries
python3 scripts/journal.py search "gratitude"

# See all types and stats
python3 scripts/journal.py types
```

## Entry Types

| Type | Description |
|------|-------------|
| `morning_pages` | Morning stream-of-consciousness |
| `evening` | Evening reflection on the day |
| `gratitude` | Gratitude practice |
| `weekly_review` | Weekly reflection and planning |
| `journal` | General journaling |
| `idea` | Idea capture |

## Database

Entries stored in: `data/journal.db`

Schema:
- `id` - Entry ID
- `created_at` - Timestamp
- `entry_type` - Type of reflection
- `content` - Full entry content
- `mood` - Optional mood tag
- `tags` - Optional comma-separated tags
- `word_count` - Word count

## Reflection Prompts Location

`Prompts/reflections/` contains the guided interview rubrics for each reflection type.


