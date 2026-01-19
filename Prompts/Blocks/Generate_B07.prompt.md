---
description: Generate B07 Warm Introductions block with CRM deduplication
tags:
  - meeting-intelligence
  - block-generation
  - b07
  - intros
  - semantic-memory
  - crm
version: 2.0
tool: true
---
# Generate Block B07: Warm Introductions Promised

Track promised introductions and networking commitments with CRM verification.

## Semantic Memory Context (Load First)

**CRITICAL:** Before generating intro requests, check if target already exists in CRM:

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()

# For each intro target mentioned:
for target_name in intro_targets:
    # 1. Check CRM for existing profile
    existing = client.search_profile(
        profile="crm",
        query=f"{target_name}",
        limit=3
    )

    # 2. Check meeting history for prior contact
    prior_meetings = client.search_profile(
        profile="meetings",
        query=f"{target_name}",
        limit=5
    )

    # Flag if target already in network
    if existing or prior_meetings:
        # Note: "Already in network" or "Prior contact exists"
```

**Use this context to:**
- Flag if intro target already exists in CRM (avoid duplicate intros)
- Note prior relationship with target if exists
- Identify if this is a re-introduction vs. new introduction
- Check for warm paths through existing network

---

## Input

- **Meeting Transcript:** `{{transcript}}`
- **Meeting Metadata:** `{{metadata}}`
- **Enrichment Context:** `{{enrichment_context}}` (from Step 2b)

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B07
semantic_enrichment: true
---

# B07: Warm Introductions Promised

## Summary

| Direction | Count | Priority |
|-----------|-------|----------|
| V introduces them to → | [N] | [High/Med/Low] |
| They introduce V to → | [N] | [High/Med/Low] |

---

## Section 1: Introductions V Will Make

### 1. [Person Name] ⭐ PRIORITY

| Field | Value |
|-------|-------|
| **Target** | [Full name] |
| **Organization** | [Company/Role] |
| **Introducing to** | [Who will receive the intro] |
| **Strategic Value** | [Why this intro matters] |
| **Context/Quote** | "[What was said that led to this]" |
| **Timeline** | [When intro will happen] |

**CRM Check:** ⭐ MEMORY-ENRICHED
- **Target in CRM?** [Yes - path / No]
- **Prior contact?** [Yes - last meeting date / No - new contact]
- **Existing relationship?** [Warm/Cold/None]
- **Deduplication note:** [If already connected, note here]

### 2. [Person Name]
...

---

## Section 2: Introductions They Will Make (to V)

### 1. [Person Name]

| Field | Value |
|-------|-------|
| **Target** | [Who V will be introduced to] |
| **Organization** | [Company/Role] |
| **Introducer** | [Who is making the intro] |
| **Strategic Value** | [Why this intro matters to V/YOUR_COMPANY] |
| **Context/Quote** | "[What was said]" |
| **Timeline** | [When to expect] |

**CRM Check:**
- **Target in CRM?** [Yes - path / No - will create after intro]
- **Prior awareness?** [Yes - how V knows of them / No]

---

## Section 3: Blurb Requirements

For intros V is making, note if blurb is needed:

| Intro | Blurb Needed? | Type | Status |
|-------|---------------|------|--------|
| [Name] → [Recipient] | Yes/No | [Type 1/2/3] | [Have/Need] |

**Link to B14** if blurb requests detected.

---

## Section 4: Follow-up Actions

- [ ] [Specific action 1 with timeline]
- [ ] [Specific action 2 with timeline]

---
**Feedback**: - [ ] Useful
---
```

## Detection Phrases

Listen for:
- "I'll introduce you to..."
- "Let me connect you with..."
- "You should meet..."
- "I'll put you in touch with..."
- "I know someone who..."
- "Maybe I could connect you..." (tentative - still capture)

## Requirements

- **Extract names, roles, companies accurately**
- **Explain strategic value** of each intro (not just who)
- **Include relevant quotes** that led to intro promise
- **Flag priority intros** that are time-sensitive
- **CRM verification** - check if target already in network
- **Minimum 500 bytes** for substantive content

## Anti-patterns

- ❌ Missing CRM deduplication check
- ❌ Generic "networking" without specific value
- ❌ No timeline for intro execution
- ❌ Ignoring tentative intro mentions

## Special Cases

**If no intros discussed:**
```markdown
# B07: Warm Introductions Promised

No explicit warm introductions were discussed in this meeting.

**Potential opportunities identified:**
- [If any networking opportunities were implicitly mentioned]
```

Generate B07 now with intro extraction and CRM verification.
