---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: worker_006_documentation
---

# N5OS Ode Folder Structure

This document explains the directory layout created by N5OS Ode, what each folder is for, and conventions for keeping things organized.

---

## Overview

After running the bootloader, your workspace looks like this:

```
workspace/
├── N5/                      # System intelligence (core)
│   ├── prefs/               # Configuration and preferences
│   ├── scripts/             # Utility scripts
│   └── cognition/           # Semantic memory (optional)
├── Knowledge/               # Long-term reference
│   └── content-library/     # Ingested articles
├── Records/                 # Date-organized records
│   └── journal/             # Journal entries
├── Prompts/                 # Reusable workflows
│   ├── Blocks/              # Block generators
│   └── reflections/         # Reflection templates
├── BOOTLOADER.prompt.md     # Installation prompt
└── PERSONALIZE.prompt.md    # Configuration wizard
```

---

## Core Directories

### N5/

**Purpose**: System intelligence and configuration. The "brain" of N5OS Ode.

```
N5/
├── prefs/
│   ├── prefs.md              # User preferences
│   └── context_manifest.yaml # Context loading rules
├── scripts/
│   ├── session_state_manager.py
│   ├── n5_protect.py
│   ├── n5_load_context.py
│   ├── debug_logger.py
│   ├── journal.py
│   └── content_ingest.py
└── cognition/                # Optional semantic memory
    ├── config.yaml
    ├── schema.sql
    └── n5_memory_client.py
```

**Key Files**:
- `prefs/prefs.md` — Your personalization settings (name, preferences, bio)
- `prefs/context_manifest.yaml` — Rules for what context loads when
- `scripts/` — Utility scripts used by personas and rules

**Convention**: Don't manually edit scripts unless you know what you're doing. Preferences are safe to modify.

---

### Knowledge/

**Purpose**: Long-term reference material. Things you want to keep and retrieve later.

```
Knowledge/
├── content-library/
│   ├── articles/           # Saved web articles
│   └── notes/              # Your notes and memos
└── [your categories]/      # Custom folders
```

**What goes here**:
- Saved articles from the web
- Reference documentation
- Notes and memos worth keeping
- Domain knowledge

**What doesn't belong**:
- Temporary files
- Work in progress
- Meeting-specific content

**Convention**: Create subfolders by topic or domain. Flat is fine for small collections.

---

### Records/

**Purpose**: Date-organized records. Things tied to specific times.

```
Records/
├── journal/
│   ├── 2026-01-15-morning-reflection.md
│   └── 2026-01-14-weekly-review.md
└── [other dated content]/
```

**What goes here**:
- Journal entries
- Meeting notes
- Daily logs
- Time-specific records

**Convention**: Use date prefixes (YYYY-MM-DD) for chronological sorting.

---

### Prompts/

**Purpose**: Reusable workflows that can be invoked with `@`.

```
Prompts/
├── Journal.prompt.md
├── Close Conversation.prompt.md
├── Build Capability.prompt.md
├── Blocks/
│   ├── Generate_B01.prompt.md
│   ├── Generate_B02.prompt.md
│   └── ...
└── reflections/
    ├── morning-pages.prompt.md
    ├── evening-reflection.prompt.md
    └── weekly-review.prompt.md
```

**What goes here**:
- Workflows you run repeatedly
- Block generators
- Reflection templates
- Any procedure you want to invoke by name

**Convention**: Use `.prompt.md` extension. Include frontmatter with title, tags, and description.

---

## File Naming Conventions

### General Rules

- **Lowercase with hyphens** for most files: `my-document.md`
- **Date prefix** for chronological content: `2026-01-15-meeting-notes.md`
- **Extension indicates type**: `.md` for docs, `.yaml` for config, `.py` for scripts

### Special Naming Patterns

| Pattern | Meaning |
|---------|---------|
| `*.prompt.md` | Invokable workflow |
| `SESSION_STATE.md` | Conversation state file |
| `.n5protected` | Protection marker |
| `_*.md` | Draft or partial file |

---

## Protection System

Mark directories that shouldn't be casually deleted with a `.n5protected` file:

```bash
# Create protection
echo "Core system files" > N5/.n5protected

# Check protection
python3 N5/scripts/n5_protect.py check /path/to/directory
```

Protected directories require explicit confirmation before move/delete operations.

**Pre-protected directories**:
- `N5/` — System intelligence
- `Knowledge/` — Reference material

---

## Adding Your Own Directories

The bootloader creates the essentials. Add your own as needed:

**Common additions**:
```
workspace/
├── Projects/              # Active work
├── Archive/               # Completed/inactive
├── Personal/              # Personal non-work
└── Inbox/                 # Temporary staging
```

**Guidelines**:
- Top-level directories should be broad categories
- Avoid deep nesting (3 levels max is a good rule)
- Clear names that explain themselves

---

## Migration: Existing Workspace

If you're installing N5OS Ode on an existing workspace:

1. **Audit** — List what you have now
2. **Decide** — What fits the N5 structure vs. what's fine as-is
3. **Don't force** — You don't have to reorganize everything
4. **Gradual** — Move things as you touch them, not all at once

N5OS Ode creates its directories alongside whatever you have. Nothing gets overwritten.

---

## Conventions Summary

| Thing | Convention |
|-------|------------|
| File names | `lowercase-with-hyphens.md` |
| Date files | `YYYY-MM-DD-description.md` |
| Prompts | `Name.prompt.md` with frontmatter |
| Config | YAML preferred over JSON |
| Protection | `.n5protected` file in directory |
| Depth | 3 levels max recommended |

---

## Troubleshooting

**Can't find a file?**
- Use grep: `grep -r "search term" Knowledge/`
- Use find: `find . -name "*keyword*"`

**Directory got cluttered?**
- Create subdirectories by topic
- Move old content to Archive/
- Be aggressive about deletion if truly unneeded

**Protection getting in the way?**
- Remove `.n5protected` to disable
- Or confirm explicitly when asked

---

*Structure serves workflow. If it doesn't help, change it.*

