---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: worker_006_documentation
---

# Knowledge Directory

This directory stores long-term reference material — things you want to keep, retrieve, and build upon over time.

---

## What Goes Here

✅ **Good fits**:
- Saved web articles worth keeping
- Reference documentation
- Your notes and memos
- Domain-specific knowledge
- Evergreen content that ages well

❌ **Don't put here**:
- Temporary files
- Work in progress
- Meeting-specific notes (use Records/)
- Drafts and scratchwork

---

## Structure

```
Knowledge/
├── content-library/        # Ingested content
│   ├── articles/           # Web articles
│   └── notes/              # Your notes
└── [your categories]/      # Custom folders
```

### Content Library

The `content-library/` subdirectory is managed by the content ingest system:

```
# Save an article
@save_webpage https://example.com/great-article

# The article is automatically:
# 1. Downloaded as markdown
# 2. Moved to content-library/articles/
# 3. Indexed in the database
```

### Custom Folders

Create your own organization:

```
Knowledge/
├── technical/           # Programming, tools
├── business/            # Strategy, markets
├── domain/              # Your field
└── personal/            # Interests
```

---

## Using Knowledge

### Finding Content

Search by text:
```bash
grep -r "search term" Knowledge/
```

Search by filename:
```bash
find Knowledge/ -name "*keyword*"
```

### With Semantic Memory (Optional)

If semantic memory is enabled, you can search by meaning:

```
Search my knowledge for articles about "effective team communication"
```

Returns relevant results even if they don't contain those exact words.

See [SEMANTIC_MEMORY.md](../docs/SEMANTIC_MEMORY.md) for setup.

---

## Content Ingest

### From Web

When you save articles using `@save_webpage`, they're automatically:
1. Downloaded as markdown
2. Moved to `content-library/articles/`
3. Added to the database (if configured)
4. Indexed for semantic search (if enabled)

### Manual Addition

Add your own files directly:

```
Knowledge/
└── technical/
    └── my-notes-on-databases.md
```

For semantic indexing, run:
```bash
python3 N5/scripts/content_ingest.py "Knowledge/technical/my-notes.md" --type note
```

---

## Best Practices

### 1. Organize by Topic, Not Source

- GOOD: `Knowledge/engineering/database-design.md`
- BAD: `Knowledge/saved-from-web/article-12345.md`

### 2. Add Frontmatter

Include metadata for future reference:

```yaml
---
created: 2026-01-15
source: https://example.com/article
tags: [databases, architecture]
---
```

### 3. Curate Aggressively

Knowledge/ should contain things you'll actually use. Delete or archive content that:
- Became outdated
- You'll never reference again
- Duplicates other content

### 4. Link, Don't Duplicate

If the same info could live in multiple places, pick one canonical location and link to it from others.

---

## Maintenance

### Quarterly Review

1. List everything: `find Knowledge/ -type f -name "*.md"`
2. Ask: "Did I use this in the last 3 months?"
3. Archive or delete unused content
4. Reorganize if categories have grown unwieldy

### Keeping Fresh

- Date-sensitive content should be reviewed and updated
- Mark evergreen vs. time-sensitive in frontmatter if needed
- Update tags as your mental model evolves

---

*Knowledge is only useful if you can find it.*

