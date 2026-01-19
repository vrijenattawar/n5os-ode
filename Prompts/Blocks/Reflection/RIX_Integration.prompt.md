---
description: Generate RIX Integration block for every reflection (always runs)
tags: [reflection, block, rix, integration, edges, memory]
tool: true
version: 2.0
---

# RIX: Integration — Deep Analytical Framework

**Block ID:** RIX
**Block Name:** Integration
**Purpose:** Connect every reflection to the broader knowledge base, create edges, track patterns.

---

## 1. Domain Definition

### What This Lens Sees
RIX is UNIQUE — it sees **everything** because it **always runs**:

- **Every reflection processed** — not conditional like R01-R09
- **Memory connections** — links to prior positions, knowledge, meetings
- **Edge relationships** — formal graph connections
- **Pattern accumulation** — tracks recurring themes over time
- **Integration context** — how this fits V's broader thinking

### RIX's Unique Role
Unlike R01-R09 which selectively extract specific content types:

| R01-R09 | RIX |
|---------|-----|
| Conditional (may not apply) | **Always runs** |
| Extracts content | **Creates connections** |
| Looks within reflection | **Looks across reflections** |
| Produces standalone blocks | **Produces graph edges** |

### What RIX Does NOT Do
- Duplicate R01-R09 extraction (those blocks handle content)
- Create edges without evidence (same standards as other blocks)
- Force connections that don't exist

---

## 2. Extraction Framework

### Trigger Patterns
**RIX always triggers** — there is no conditional logic.

Every reflection gets:
1. Key concept extraction
2. Memory profile queries
3. Connection assessment
4. Edge creation (if warranted)
5. Pattern tracking

### Process Flow
```
Transcript → Extract Concepts → Query Memory → Assess Connections → Write Edges → Detect Patterns
```

### Counter-Indicators
None — RIX always runs. However, it may produce:
- Zero edges (if no genuine connections exist)
- Minimal output (for trivial reflections)

---

## 3. Analysis Dimensions

### Dimension 1: Key Concept Extraction
Extract from transcript:

| Concept Type | Examples |
|--------------|----------|
| **Named entities** | People, companies, products |
| **Abstract concepts** | Themes, principles, patterns |
| **YOUR_COMPANY terms** | Product features, strategic elements |
| **Emotional markers** | Frustrations, excitements, concerns |

### Dimension 2: Memory Profile Queries
Query three profiles with extracted concepts:

```python
from N5.cognition.n5_memory_client import N5MemoryClient

profiles_to_query = ["positions", "knowledge", "meetings"]

def query_memory_profiles(key_concepts: list[str]) -> dict:
    client = N5MemoryClient()

    # Query positions (V's stated beliefs and stances)
    position_hits = client.search_profile(
        profile="positions",
        query=" ".join(key_concepts),
        limit=5
    )

    # Query knowledge (facts, articles, learnings)
    knowledge_hits = client.search_profile(
        profile="knowledge",
        query=" ".join(key_concepts),
        limit=5
    )

    # Query meetings (prior conversations)
    meeting_hits = client.search_profile(
        profile="meetings",
        query=" ".join(key_concepts),
        limit=3
    )

    return {
        "positions": position_hits,
        "knowledge": knowledge_hits,
        "meetings": meeting_hits
    }
```

### Dimension 3: Connection Assessment
For each memory hit, evaluate:

| Question | Purpose |
|----------|---------|
| **Is this real?** | Surface similarity vs genuine connection |
| **What type?** | Which edge type fits |
| **What's the evidence?** | Specific quote from transcript |
| **How confident?** | High, medium, or low |

### Dimension 4: Edge Type Selection

| Edge Type | Meaning | Use When |
|-----------|---------|----------|
| **EXTENDS** | Builds upon | New reflection develops prior idea |
| **CONTRADICTS** | Challenges | New reflection conflicts with prior |
| **SUPPORTS** | Provides evidence | New data backs prior position |
| **REFINES** | Adds nuance | Clarifies or narrows prior idea |
| **ENABLES** | Unlocks | New insight makes prior actionable |

### Dimension 5: Pattern Detection
Track across reflections:

| Pattern | Threshold | Action |
|---------|-----------|--------|
| **Super-connector** | 5+ inbound edges | Flag for attention |
| **Promotion candidate** | 3+ occurrences | Consider elevating to position |
| **Contradiction cluster** | 2+ CONTRADICTS | Flag for resolution |

---

## 4. Memory Integration

### Query Implementation

```python
from N5.cognition.n5_memory_client import N5MemoryClient

def run_rix_integration(reflection_slug: str, key_concepts: list[str]) -> dict:
    client = N5MemoryClient()

    # Query all three profiles
    positions = client.search_profile("positions", " ".join(key_concepts), limit=5)
    knowledge = client.search_profile("knowledge", " ".join(key_concepts), limit=5)
    meetings = client.search_profile("meetings", " ".join(key_concepts), limit=3)

    # Assess each hit for genuine connection
    edges_to_create = []

    for hit in positions + knowledge + meetings:
        connection = assess_connection(reflection_slug, hit, key_concepts)
        if connection["is_genuine"]:
            edges_to_create.append(connection)

    return {
        "memory_hits": {
            "positions": positions,
            "knowledge": knowledge,
            "meetings": meetings
        },
        "edges": edges_to_create
    }
```

### Edge Writing Integration

```bash
# Write edges using the reflection_edges.py infrastructure
python3 N5/scripts/reflection_edges.py add \
  --from "<reflection_slug>" \
  --to "<target_slug>" \
  --edge-type <TYPE> \
  --evidence "<quote from transcript>" \
  --confidence <high|medium|low>
```

---

## 5. Output Schema

```markdown
## RIX: Integration Analysis

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Integration Summary
**Reflection:** [slug/title]
**Concepts Extracted:** [comma-separated list]
**Memory Hits:** [positions: X, knowledge: Y, meetings: Z]
**Edges Created:** [count]

### Key Concepts Extracted

| Type | Concepts |
|------|----------|
| **Entities** | [people, companies, products] |
| **Themes** | [abstract concepts] |
| **YOUR_COMPANY** | [product/strategy terms] |

### Memory Hits

#### Positions
| Position | Relevance | Connection Type |
|----------|-----------|-----------------|
| [position-slug] | [brief rationale] | [EXTENDS/SUPPORTS/etc] |

#### Knowledge
| Item | Relevance | Connection Type |
|------|-----------|-----------------|
| [knowledge-slug] | [brief rationale] | [EXTENDS/SUPPORTS/etc] |

#### Meetings
| Meeting | Relevance | Connection Type |
|---------|-----------|-----------------|
| [meeting-slug] | [brief rationale] | [EXTENDS/SUPPORTS/etc] |

### Edges Created

| From | To | Type | Evidence | Confidence |
|------|----|------|----------|------------|
| {this} | [target] | [TYPE] | "[quote]" | [level] |

### Pattern Flags

**Super-connectors (5+ edges):**
- [target-slug]: [X edges]

**Promotion candidates (3+ occurrences):**
- [theme]: appeared in [list of reflections]

**Contradiction clusters:**
- [topic]: [reflection-a] vs [reflection-b]

### Integration Narrative

[2-3 paragraphs contextualizing how this reflection connects to V's broader thinking. What patterns does this reinforce? What evolution does this show? What questions does this raise?]

### CLI Commands Executed

```bash
# Edges added during this integration
python3 N5/scripts/reflection_edges.py add --from "..." --to "..." --edge-type ... --evidence "..." --confidence ...
```
```

---

## 6. Connection Hooks

### Upstream
RIX queries all memory profiles:
- `positions` — V's stated beliefs and stances
- `knowledge` — Facts, articles, learnings
- `meetings` — Prior conversations and their outcomes

### Downstream
RIX produces:
- **JSONL edges** in `N5/data/reflection_edges.jsonl`
- **Pattern flags** for attention
- **Integration narrative** for context

### Cross-Block Connections
RIX may reference other R-blocks from the same reflection:
- "This R03 Strategic Thought EXTENDS position X"
- "The R07 Prediction CONTRADICTS prior forecast Y"

---

## 7. Worked Example

### Sample Input
```
Reflection: 2026-01-09_recruiter-game-plan
Key concepts: recruiter, ownership, candidate, matching, trust

Memory query returns:
- Position: "candidate-ownership-thesis" (recruiter should own candidate relationship)
- Knowledge: "trust-building-in-recruiting" (article on trust dynamics)
- Meeting: "2025-12-meeting-with-agency-owner" (discussed candidate ownership)
```

### Final Output
```markdown
## RIX: Integration Analysis

**Generated:** 2026-01-09T14:30:00Z
**Source:** Personal/Reflections/2026/01/2026-01-09_recruiter-game-plan/transcript.md

### Integration Summary
**Reflection:** 2026-01-09_recruiter-game-plan
**Concepts Extracted:** recruiter, ownership, candidate, matching, trust
**Memory Hits:** [positions: 2, knowledge: 1, meetings: 1]
**Edges Created:** 3

### Key Concepts Extracted

| Type | Concepts |
|------|----------|
| **Entities** | recruiters, candidates |
| **Themes** | ownership, trust, matching |
| **YOUR_COMPANY** | recruiter tools, candidate flow |

### Memory Hits

#### Positions
| Position | Relevance | Connection Type |
|----------|-----------|-----------------|
| candidate-ownership-thesis | Direct exploration of ownership model | EXTENDS |
| recruiter-value-prop | Related to recruiter role definition | SUPPORTS |

#### Knowledge
| Item | Relevance | Connection Type |
|------|-----------|-----------------|
| trust-building-in-recruiting | Provides framework for trust dynamics | SUPPORTS |

#### Meetings
| Meeting | Relevance | Connection Type |
|---------|-----------|-----------------|
| 2025-12-meeting-with-agency-owner | Prior discussion of same themes | EXTENDS |

### Edges Created

| From | To | Type | Evidence | Confidence |
|------|----|------|----------|------------|
| 2026-01-09_recruiter-game-plan | candidate-ownership-thesis | EXTENDS | "the recruiter owns the relationship until placement" | high |
| 2026-01-09_recruiter-game-plan | trust-building-in-recruiting | SUPPORTS | "trust is the foundation of any good placement" | medium |
| 2026-01-09_recruiter-game-plan | 2025-12-meeting-with-agency-owner | EXTENDS | "building on what we discussed about agency dynamics" | high |

### Pattern Flags

**Super-connectors (5+ edges):**
- candidate-ownership-thesis: 7 edges (growing theme)

**Promotion candidates (3+ occurrences):**
- "recruiter-candidate trust": appeared in 4 reflections — consider formalizing as position

**Contradiction clusters:**
- None detected

### Integration Narrative

This reflection continues V's exploration of the recruiter-candidate relationship, a theme that has been building over the past several weeks. The "candidate-ownership-thesis" position is becoming a super-connector with 7 inbound edges, suggesting it's a foundational belief worth documenting more formally.

The connection to the December meeting with the agency owner shows continuity of thinking — V is building on that conversation rather than starting fresh. The trust framework from knowledge base provides theoretical grounding.

Notably, the recurring theme of "recruiter-candidate trust" has now appeared in 4 reflections. This may warrant elevation to a formal position statement.

### CLI Commands Executed

```bash
python3 N5/scripts/reflection_edges.py add --from "2026-01-09_recruiter-game-plan" --to "candidate-ownership-thesis" --edge-type EXTENDS --evidence "the recruiter owns the relationship until placement" --confidence high
python3 N5/scripts/reflection_edges.py add --from "2026-01-09_recruiter-game-plan" --to "trust-building-in-recruiting" --edge-type SUPPORTS --evidence "trust is the foundation of any good placement" --confidence medium
python3 N5/scripts/reflection_edges.py add --from "2026-01-09_recruiter-game-plan" --to "2025-12-meeting-with-agency-owner" --edge-type EXTENDS --evidence "building on what we discussed about agency dynamics" --confidence high
```
```

---

## Quality Checklist

- [ ] Key concepts comprehensively extracted
- [ ] All three memory profiles queried
- [ ] Connections assessed for genuineness (not forced)
- [ ] Edge types appropriately selected
- [ ] Evidence quotes are specific and relevant
- [ ] Pattern flags checked (super-connectors, promotions)
- [ ] Integration narrative provides genuine insight

## Edge Writing Protocol

1. **Only create edges with evidence** — no speculative connections
2. **Use appropriate confidence levels:**
   - High: Explicit reference or clear development
   - Medium: Strong thematic connection
   - Low: Possible connection, worth tracking
3. **Prefer fewer high-quality edges** over many weak ones

## Pattern Thresholds

| Pattern | Threshold | Action |
|---------|-----------|--------|
| Super-connector | 5+ edges | Add to integration narrative, consider deep-dive |
| Promotion candidate | 3+ occurrences | Flag for position formalization |
| Contradiction cluster | 2+ CONTRADICTS | Flag for resolution in future reflection |

---

*Template Version: 2.0 | R-Block Framework | 2026-01-09*
