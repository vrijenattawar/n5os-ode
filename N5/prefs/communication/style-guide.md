---
created: 2025-12-15
last_edited: 2026-01-15
version: 1.0
provenance: n5os-ode-bootstrap
---

# Communication Style Guide

Guidelines for writing in n5OS-Ode context (emails, blurbs, documentation, prompts).

## Principles

1. **Clarity over cleverness** — Be direct. Jargon only if necessary.
2. **Structured** — Use lists, tables, headers. Scannable.
3. **Evidence-based** — Claims need sources or reasoning.
4. **Concise** — Short sentences. No filler.
5. **Actionable** — Each piece should lead somewhere.

## Tone

- Professional but warm
- Confident but not arrogant
- Respectful of reader's time
- Explicit about uncertainty ("Unknown", "Assuming X")

## Formatting

- Markdown for everything
- YAML frontmatter for documents
- File references use backticks: `` `file 'path/to/file'` ``
- Code blocks with language tags

## Examples

✅ **Good**: "Fixed broken import paths in 3 services. All tests pass."  
❌ **Bad**: "Attempted to optimize and enhance the service layer infrastructure."

✅ **Good**: "Unknown: exact rollout timeline"  
❌ **Bad**: "Probably ready in a few days"

See `Prompts/` for prompt examples that follow this guide.

