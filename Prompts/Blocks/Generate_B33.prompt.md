---
created: 2026-01-04
last_edited: 2026-01-09
version: 1.2
provenance: con_JAADiniaFXpKQUTN
tool: true
description: "Generate B33 Decision Edges - extract context graph relationships from meeting intelligence"
tags: [meetings, intelligence, blocks, context-graph, edges, positions, resonance]
mg_stage: MG-2+
status: canonical
---

# Generate B33 Decision Edges

Extract context graph edges from meeting intelligence blocks.

## When to Use

Run after MG-2 completes (B01-B32 blocks exist). Can be run:
- Manually on individual meetings
- As part of the [M] → [P] state transition
- In batch mode for backfill

## Usage

```bash
# Dry run - see what would be extracted
python3 N5/scripts/generate_b33_edges.py --meeting /path/to/meeting_[P] --dry-run

# Generate B33 file (edges go to review queue)
python3 N5/scripts/generate_b33_edges.py --meeting /path/to/meeting_[P]

# Generate and auto-commit to edges.db (trusted meetings)
python3 N5/scripts/generate_b33_edges.py --meeting /path/to/meeting_[P] --auto-commit
```

## Edge Types

The B33 block extracts these relationship types:

| Relation | Category | Description |
|----------|----------|-------------|
| `originated_by` | Provenance | Who first voiced this idea/decision |
| `supported_by` | Stance | Who endorsed after hearing |
| `challenged_by` | Stance | Who pushed back or raised concerns |
| `hoped_for` | Expectation | Expected positive outcome |
| `concerned_about` | Expectation | Feared risk or downside |
| `influenced_by` | Provenance | Who shaped thinking on topic |
| `depends_on` | Chain | Logical dependency between ideas/decisions |
| `supports_position` | Stance | Edge evidence validates V's documented position (Phase 4.5) |
| `challenges_position` | Stance | Edge evidence contradicts V's documented position (Phase 4.5) |
| `crystallized_from` | Chain | Position emerged from this evidence (Phase 4.5) |
| `evolves` | Evolution | Idea has evolved from previous version (use with `evolution_type`) |

<!-- INJECT_CONTEXT -->

## Resonance-Aware Extraction

This system uses a "Resonance Reservoir" to distinguish V's established mental models from genuinely novel ideas. The contextual primer (injected above when available) tells you what V already knows.

### The Resonance Hierarchy

| Level | Name | Frequency | Extraction Rule |
|-------|------|-----------|-----------------|
| **L0** | Cornerstone | 10+ meetings | Only extract if **EVOLUTION** detected (pivot, challenge, new domain) |
| **L1** | Active Thesis | 4-9 meetings | Extract evolution only. Include `evolution_type` field. |
| **L2** | Recurring Tool | 2-3 meetings | Extract if applied to **new domain**. Skip same-domain repetition. |
| **L3** | Spark | 1 meeting | Extract fully! These are the valuable novel ideas. |

### Evolution Types

When extracting an evolved idea, include the `evolution_type` field:

| Type | When to Use |
|------|-------------|
| `domain_expansion` | Same idea applied to new context/domain |
| `refinement` | Idea sharpened, nuanced, or made more specific |
| `challenge` | Idea questioned, contradicted, or tested |
| `abandonment` | Idea explicitly dropped or superseded |

### Example: Resonance-Aware Edge

```json
{
  "source_type": "idea",
  "source_id": "meaning-level-intelligence",
  "relation": "evolves",
  "target_type": "idea",
  "target_id": "meaning-level-intelligence",
  "evolution_type": "domain_expansion",
  "evidence": "V applied meaning-level intelligence to personal productivity, not just hiring",
  "context_meeting_id": "mtg_2026-01-09_xyz"
}
```

### Key Question

Before extracting any idea, ask: **"Is this genuinely new thinking, or V restating what he already believes?"**

- If restating → Skip (unless there's evolution)
- If new domain → Extract with `domain_expansion`
- If truly novel → Extract fully as Spark

## Output

Creates `B33_DECISION_EDGES.jsonl` in the meeting folder:

```jsonl
{"_meta": true, "meeting_id": "mtg_2025-12-26_Demo", "generated_at": "2026-01-04T..."}
{"source_type": "idea", "source_id": "semantic-matching", "relation": "originated_by", "target_type": "person", "target_id": "vrijen", ...}
{"source_type": "decision", "source_id": "pilot-program", "relation": "depends_on", "target_type": "decision", "target_id": "budget-approval", ...}
```

## Quality Guidelines

- **Selectivity**: 3-8 high-quality edges per meeting is ideal
- **Evidence**: Every edge must have a quote or paraphrase
- **Attribution**: Carefully distinguish originator vs supporter
- **V Identity**: Vrijen Attawar is always `vrijen` as person ID
- **Position edges**: Only create when alignment/contradiction is CLEAR (don't force it)
- **Resonance awareness**: Prioritize novel ideas over repetition of known patterns

## Pipeline Integration

Updates `manifest.json`:
```json
{
  "blocks_generated": {
    "b33_decision_edges": true
  },
  "b33_edge_count": 8,
  "b33_generated_at": "2026-01-04T18:50:02.838343"
}
```

Logs to `PROCESSING_LOG.jsonl` when run as part of MG pipeline.

## Review Flow

Generated edges flow to the review queue (`N5/review/edges/`) unless `--auto-commit` is used. Use `edge_reviewer.py` to approve/reject before committing to `edges.db`.



