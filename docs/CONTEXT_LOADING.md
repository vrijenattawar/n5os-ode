---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: n5os-ode-upgrade
---

# Context Loading System

## What is Context Loading?

Context loading is the mechanism that restores the "missing link" between user intent and system standards. When the AI begins work, it needs the right reference materials—architectural principles, style guides, safety protocols, etc.—that match the type of task it's performing.

Instead of manually loading relevant files or hoping the AI remembers everything, the context loader injects the appropriate bundle of context automatically based on the task category.

## Why It Matters

- **Consistency**: Ensures the AI always works with up-to-date standards
- **Efficiency**: Reduces cognitive load—no need to remember which files to reference
- **Quality**: Guards against drift by loading authoritative sources
- **Safety**: Ensures destructive operations have safety checks loaded

## Categories

The context loader supports the following categories:

| Category | Purpose | Example Use Cases |
|----------|---------|-------------------|
| `build` | Implementation, refactoring, coding, engineering | "Fix the bug," "Implement this feature," "Refactor the schema" |
| `strategy` | High-level thinking, planning, decision making | "What's the best approach?" "Plan this feature" |
| `system` | Lists, Index, System Operations, Database | "Update the index," "Organize this directory" |
| `safety` | Destructive ops, moves, deletes | "Delete these files," "Move this directory" |
| `scheduler` | Agents, Scheduled Tasks, Automation | "Create an agent," "Schedule this task" |
| `writer` | Content creation, writing, polished communication | "Draft an email," "Write this article" |
| `research` | Deep dive, analysis, web research | "Research this topic," "Analyze these findings" |
| `health` | Health planning, bio-context, energy management | "Review my supplement stack" |
| `general` | Fallback for novel or undefined tasks | Auto-loaded when no category matches |

## Usage

### Basic Usage

```bash
# Load context for a specific category
python3 N5/scripts/n5_load_context.py build

# Load context for strategy tasks
python3 N5/scripts/n5_load_context.py strategy
```

### Intent Inference

The loader can infer the category from natural language:

```bash
# Will automatically map to "build" category
python3 N5/scripts/n5_load_context.py "fix the bug in the script"

# Will automatically map to "writer" category
python3 N5/scripts/n5_load_context.py "draft an email to the team"
```

### List Available Groups

```bash
python3 N5/scripts/n5_load_context.py --list
```

## How It Works

1. **Manifest Lookup**: Reads `N5/prefs/context_manifest.yaml` for category definitions
2. **Category Detection**: Either direct match or keyword-based inference
3. **File Loading**: Reads each file defined in the category's `files` list
4. **Formatted Output**: Returns content with markdown delimiters for clear boundaries

## Customization

### Adding a New Category

Edit `N5/prefs/context_manifest.yaml`:

```yaml
groups:
  your_new_category:
    description: "What this category is for"
    files:
      - "path/to/reference/file.md"
      - "path/to/another/file.md"
```

### Modifying Existing Categories

Simply update the `files` list for any category. The loader will pick up changes immediately.

### Removing Categories

Delete the category entry from the manifest. The loader will fall back to `general` for undefined tasks.

## Integration with Rules

The context loader is typically invoked via a user rule before substantive work:

> **When**: Before substantive work requiring loaded context
> **Action**: `python3 N5/scripts/n5_load_context.py <category>`

This ensures the AI has the right context before beginning the actual task.

## File Format

Files are wrapped in XML-style comments for clear delimitation:

```html
<!-- FILE: path/to/file.md -->
... file content ...
<!-- END FILE -->
```

This makes it easy for the AI to distinguish between injected context and conversation content.