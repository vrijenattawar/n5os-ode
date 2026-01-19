---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_wkgwgDeEtgUjiPYf
tool: true
tags:
  - meeting-intelligence
  - voice-library
  - extraction
description: |
  Generate B35 Linguistic Primitives block — extracts analogies, metaphors,
  distinctive phrases, and capture signals from meeting transcripts for
  the Voice Library.
block_id: B35
block_name: LINGUISTIC_PRIMITIVES
---

# Generate B35: Linguistic Primitives

## Purpose

Extract V's distinctive language patterns from meeting transcripts to populate the Voice Library. This block identifies:

1. **Analogies** — "X is like Y because Z" constructions
2. **Metaphors** — Conceptual framings (e.g., "talent as optionality", "career as portfolio")
3. **Distinctive Phrases** — Sentence patterns that sound characteristically like V
4. **Capture Signals** — Explicit markers like "I'm stealing that", "That's a great way to put it"
5. **Comparisons** — "The difference between X and Y is..." constructions

## Input

- Meeting transcript (full text or V's utterances only)
- Optional: Meeting metadata (topic, participants)

## Output Format

```jsonl
{"type": "analogy", "text": "...", "domains": ["career", "incentives"], "context": "...", "capture_signal": false}
{"type": "metaphor", "text": "...", "domains": ["ethics"], "context": "...", "capture_signal": false}
{"type": "phrase", "text": "...", "domains": ["optionality"], "context": "...", "capture_signal": true}
```

## Extraction Rules

### 1. ONLY extract V's utterances
Do not extract language from other participants unless V explicitly endorses it with a capture signal.

### 2. Minimum length
Each primitive should be **at least 50 characters** (for Pangram scoring reliability). Skip single-word or very short fragments.

### 3. Capture Signal Detection
Flag `capture_signal: true` if V says any of:
- "I'm stealing that"
- "That's a great way to put it"
- "I love that framing"
- "I'm going to use that"
- "That's exactly it"
- Or similar explicit endorsement of someone else's language

### 4. Domain Tagging
Tag each primitive with relevant domains from:
- `career` — job search, professional development, workplace dynamics
- `incentives` — motivation, game theory, behavioral economics
- `ethics` — morality, fairness, values
- `optionality` — choices, flexibility, strategic positioning
- `status` — reputation, perception, social dynamics
- `talent` — skill development, capability, competence
- `entrepreneurship` — startups, business building, risk
- `relationships` — networking, trust, interpersonal dynamics

Multiple domains allowed. Choose 1-3 most relevant.

### 5. Context Preservation
Include enough surrounding context (1-2 sentences) to understand the primitive's meaning, but the `text` field should be the extractable phrase itself.

---

## Prompt Template

When generating B35, use this structure:

```
You are extracting linguistic primitives from a meeting transcript for V's Voice Library.

TRANSCRIPT:
{transcript}

INSTRUCTIONS:
1. Read through V's utterances carefully
2. Identify analogies, metaphors, distinctive phrases, and capture signals
3. For each primitive:
   - Extract the exact text (minimum 50 chars)
   - Tag with 1-3 relevant domains
   - Include brief context
   - Flag if it's a capture signal (V endorsing someone else's language)
4. Output as JSONL (one JSON object per line)
5. Quality over quantity — only extract genuinely distinctive language, not generic statements

DOMAIN OPTIONS: career, incentives, ethics, optionality, status, talent, entrepreneurship, relationships

OUTPUT (JSONL):
```

---

## Example Output

```jsonl
{"type": "analogy", "text": "The talent cliff isn't about skill—it's about options. When you're good enough, doors open that make honesty cheap.", "domains": ["talent", "optionality", "ethics"], "context": "Discussing why talented people can afford to be honest while struggling people may need to play games.", "capture_signal": false}
{"type": "metaphor", "text": "Career development is portfolio construction—you're diversifying across skills, relationships, and opportunities.", "domains": ["career", "optionality"], "context": "Explaining career strategy to a client.", "capture_signal": false}
{"type": "phrase", "text": "The meritocracy requires a minimum talent threshold just to participate honestly.", "domains": ["talent", "ethics", "status"], "context": "On the prerequisites for ethical behavior in competitive environments.", "capture_signal": false}
{"type": "phrase", "text": "That's a beautiful framing—I'm absolutely stealing that.", "domains": ["relationships"], "context": "V endorsing a guest's phrasing of an idea.", "capture_signal": true}
```

---

## Integration

This block feeds into:
- `N5/scripts/extract_voice_primitives.py` — batch extraction
- `N5/data/voice_library.db` — storage after review
- `N5/review/voice/` — HITL review queue

## Success Criteria

- Extracts at least 3-10 primitives per meeting (varies by meeting type)
- All primitives are ≥50 characters
- Domain tags are accurate and relevant
- Capture signals are correctly identified
- Output is valid JSONL

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-12 | Initial creation for Voice Library V2 |

