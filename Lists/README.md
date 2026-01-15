---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: worker_006_documentation
---

# Lists Directory

This directory stores single-source-of-truth (SSOT) lists — curated collections that you maintain over time.

---

## What Are SSOT Lists?

A **Single Source of Truth list** is a canonical collection where:

- **One location** — The list lives in exactly one place
- **Authoritative** — If there's a discrepancy, the list is right
- **Maintained** — You actively add, update, and remove items
- **Queryable** — Easy to search and filter

**Examples**:
- Books to read
- People to follow up with
- Ideas to explore
- Tools to evaluate
- Projects on hold

---

## List Format

Lists use markdown with YAML-structured items:

```markdown
---
created: 2026-01-15
last_edited: 2026-01-15
type: list
domain: reading
---

# Books to Read

## Active Queue

- **Deep Work** by Cal Newport
  - status: in-progress
  - added: 2026-01-10
  - priority: high
  - notes: "Recommended by Sarah"

- **Thinking, Fast and Slow** by Daniel Kahneman
  - status: queued
  - added: 2026-01-05
  - priority: medium

## Completed

- **Atomic Habits** by James Clear
  - status: completed
  - finished: 2026-01-08
  - rating: 4/5
  - notes: "Great on habit stacking"
```

---

## Creating Lists

### Basic Structure

```markdown
---
created: YYYY-MM-DD
type: list
domain: [topic]
---

# [List Name]

## [Section 1]

- **Item name**
  - key: value
  - key: value

## [Section 2]
...
```

### Recommended Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `status` | Current state | queued, active, done, on-hold |
| `added` | When added to list | 2026-01-15 |
| `priority` | How important | high, medium, low |
| `notes` | Context/details | "From podcast episode" |
| `source` | Where you found it | URL, person name |

---

## Working with Lists

### Adding Items

Ask your AI to add items:

```
Add "The Design of Everyday Things" to my reading list
- priority: high
- source: Design meetup recommendation
```

### Querying Lists

```
What's on my reading list that's high priority?
```

```
Show me everything I've added to lists this month
```

### Maintaining Lists

**Monthly review**:
1. Open each list
2. Remove items you'll never do
3. Update statuses
4. Reprioritize based on current goals

---

## Common List Types

### Reading List
```
Lists/reading.md
- Books, articles, papers to read
- Fields: author, status, priority, format
```

### Ideas List
```
Lists/ideas.md
- Things to explore, build, or write about
- Fields: category, status, potential, next-step
```

### Follow-Up List
```
Lists/follow-ups.md
- People to reach out to
- Fields: person, reason, deadline, last-contact
```

### Tools to Evaluate
```
Lists/tools.md
- Software, services, products to try
- Fields: category, status, verdict, notes
```

### Someday/Maybe
```
Lists/someday.md
- Things you might do eventually
- Fields: category, added, interest-level
```

---

## List vs. Other Locations

**Use Lists/ when**:
- You actively maintain the collection
- Items are added and removed over time
- You query it to make decisions

**Use Knowledge/ when**:
- Content is reference material
- Things don't get "completed" or removed
- It's for reading, not tracking

**Use Records/ when**:
- Content is tied to specific dates
- It's a record of what happened
- Chronological organization matters

---

## Best Practices

### 1. One List Per Domain

Don't mix books and follow-ups in the same list. Keep domains separate for clean queries.

### 2. Keep Status Current

Stale lists lose trust. Update statuses when things change.

### 3. Regular Purging

Lists that only grow become useless. Remove items you'll genuinely never pursue.

### 4. Consistent Fields

Use the same fields across items in a list. Makes querying reliable.

### 5. Archive, Don't Delete History

Move completed items to a "## Completed" section rather than deleting. History has value.

---

## Protection

Lists are valuable. Consider protecting:

```bash
echo "Curated lists - do not bulk delete" > Lists/.n5protected
```

This requires explicit confirmation before any destructive operations.

---

*A good list is a forcing function for decision-making.*

