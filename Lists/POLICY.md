---
created: 2025-12-15
last_edited: 2026-01-15
version: 1.0
provenance: n5os-ode-bootstrap
---

# Lists Policy

Guidelines for maintaining lists in n5OS-Ode.

## List Categories

- **Active**: Current projects, work in progress
- **Backlog**: Future work, to-do items
- **Archive**: Completed, historical reference
- **Reference**: Non-actionable lists (resources, learning)

## Single Source of Truth (SSOT)

Each list lives in exactly one place:
- List files: `Lists/<name>.md`
- Database: N/A in n5OS-Ode (use markdown by default)

Don't duplicate lists across multiple files.

## Structure

```markdown
# List Name

## Active

- [ ] Item 1
- [ ] Item 2

## Backlog

- [ ] Future item

## Archive

- ✅ Completed item

```

## Conventions

- Checkbox `[ ]` = not done
- Checkbox `[x]` = done
- Emoji prefix for quick scanning (e.g., 🔴 urgent, 🟡 medium, 🟢 low)

All lists include YAML frontmatter with version and provenance.

