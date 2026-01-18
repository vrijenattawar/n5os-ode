---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: n5os-ode-upgrade-worker1
---

# Conversation End System

## Why Conversation Hygiene Matters

Every conversation in N5OS generates artifacts—files, decisions, insights, positions, and context. Without proper hygiene:

- **Knowledge leaks** into temporary workspaces, never captured in canonical locations
- **Learning fragments** across conversations, preventing compound growth
- **Worldview positions** remain ephemeral, unavailable for future reasoning
- **Build context** gets lost, making it impossible to understand what was decided and why

The conversation end system ensures all value from a conversation is captured before the conversation closes.

---

## The Three Tiers

### Tier 1: Quick Close
**For:** Simple discussions, Q&A, quick clarifications

- No SESSION_STATE.md or minimal content
- No artifacts created in user workspace
- No git changes
- Duration: <5 minutes

**Action:** Archive conversation workspace, close SESSION_STATE, return to Operator.

---

### Tier 2: Standard Close
**For:** Substantial discussions with artifacts

- 3+ artifacts in conversation workspace OR
- Research / exploration with findings OR
- Document creation / editing

**Action:** 
- Semantic close with Librarian persona
- Extract decisions, open items, next steps
- Generate semantic title (3-slot emoji: State | Type | Content)
- Position detection (if worldview positions emerged)
- Commit target suggestions (Content Library, Voice Library, etc.)

---

### Tier 3: Full Build Close
**For:** Build work, orchestrator threads, debug sessions, capability changes

- Build workspace active (`N5/builds/*/`)
- Orchestrator context present
- DEBUG_LOG.jsonl active
- Git changes pending

**Action:**
- All Tier 2 actions PLUS
- Worker review (if orchestrator)
- After-Action Report (AAR) generation
- Capability graduation check
- PII audit for created files
- Atomic commit across all workers

---

## Worker vs. Full Close Mode

### Worker Close Mode
**Trigger:** `build_id` + `worker_num` in SESSION_STATE frontmatter

Workers are spawned by orchestrators for parallel work. Their goal is **clean handoff**, not finalization.

**Worker responsibilities:**
- Verify deliverables exist
- Generate worker title with parent topic tag: `MMM DD | ✅ 👷🏽‍♂️ 🛠️ [Parent-Topic] Task Description`
- Write handoff summary for orchestrator
- Update SESSION_STATE to "complete"
- **Do NOT commit** — defers to orchestrator

### Full Close Mode
**Trigger:** Normal thread OR orchestrator thread

Full close includes commits and finalization. Orchestrators:
- Review all worker completions
- Consolidate worker artifacts
- Execute atomic commit across all changes
- Generate AAR

---

## Integration with SESSION_STATE

SESSION_STATE.md is the backbone of the conversation end system:

```yaml
---
convo_id: con_abc123
type: build
status: active
focus: Feature implementation
artifacts:
  - file 'path/to/code.py'
  - file 'path/to/PLAN.md'
build_id: my-project      # Worker mode trigger
worker_num: 1             # Worker number
parent_topic: My Project  # For greppable lineage
---
```

The router parses SESSION_STATE to:
- Detect worker mode
- Identify conversation type
- Count progress items
- Provide context for tier decision

---

## Router Detection Logic

The `conversation_end_router.py` script analyzes multiple signals:

1. **SESSION_STATE.md presence and content**
   - Conversation type
   - Focus area
   - Progress tracking

2. **Artifact count in conversation workspace**
   - ≥3 artifacts → Tier 2 or 3

3. **Build workspace status**
   - Active build folder → Tier 3

4. **DEBUG_LOG.jsonl presence**
   - Debug session → Tier 3

5. **Git changes**
   - Modified files → Tier 2 or 3

6. **Content markers**
   - Build markers (implement, refactor, schema change)
   - Debug markers (fix, broken, troubleshoot)

The router returns JSON with tier recommendation and confidence:

```json
{
  "tier": 3,
  "reason": "Build workspace active; debug markers found",
  "confidence": "high",
  "signals": {
    "artifact_count": 12,
    "build_workspace": {"exists": true},
    "has_debug_log": true
  }
}
```

---

## Command Reference

### Route conversation to tier
```bash
python3 N5/scripts/conversation_end_router.py --convo-id <id> [--force-tier N]
```

### Worker completion notification
```bash
python3 N5/scripts/build_worker_complete.py --convo-id <id> --build-id <slug> --worker-num <n>
```

### Position extraction
```bash
python3 N5/scripts/positions.py list
python3 N5/scripts/positions.py check-overlap "insight text"
```

### PII Audit
```bash
python3 N5/scripts/conversation_pii_audit.py --convo-id <id> --auto-mark
```

---

## See Also

- **Prompt:** `file 'Prompts/Close Conversation.prompt.md'` (v5.1)
- **Router:** `file 'N5/scripts/conversation_end_router.py'` (424 lines)
- **Spec:** `file 'N5/prefs/operations/conversation-end-v3.md'`
- **Emoji Legend:** `file 'N5/config/emoji-legend.json'`