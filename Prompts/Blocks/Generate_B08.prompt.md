---
description: Generate B08 Stakeholder Intelligence block with semantic memory enrichment
tags:
  - meeting-intelligence
  - block-generation
  - b08
  - stakeholder
  - semantic-memory
  - crm
  - nyne
version: 2.1
tool: true
---
# Generate Block B08: Stakeholder Intelligence

Deep stakeholder profile for CRM with historical context enrichment.

## Semantic Memory Context (Load First)

**CRITICAL:** Before generating B08, load prior relationship context:

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()

# 1. Check for existing CRM profile
crm_results = client.search_profile(
    profile="crm",
    query=f"{stakeholder_name} {organization}",
    limit=3
)

# 2. Find prior meetings with this stakeholder
meeting_history = client.search_profile(
    profile="meetings",
    query=f"{stakeholder_name}",
    limit=5
)

# 3. If prior meetings exist, note for comparison
prior_b08_exists = len(meeting_history) > 0
```

**Use this context to:**
- Detect relationship trajectory (first meeting vs. recurring contact)
- Compare current resonance to prior conversations
- Update credibility/domain authority from prior B08s
- Track CRM profile evolution

---

## Nyne Social Intelligence (Load for Section 5)

**When to fetch:** If stakeholder has LinkedIn URL in CRM profile or enrichment data.

```python
import asyncio
from N5.scripts.enrichment.nyne_enricher import get_recent_social_activity

# Check for LinkedIn URL in enrichment context or CRM profile
linkedin_url = enrichment_context.get('linkedin_url') or crm_profile.get('linkedin_url')

if linkedin_url:
    # Fetch recent social activity (cached for 7 days)
    nyne_result = asyncio.run(get_recent_social_activity(
        linkedin_url=linkedin_url,
        max_age_days=7
    ))
    
    if nyne_result['success'] and nyne_result['data']:
        nyne_intelligence = nyne_result['data']
        # Use this to populate Section 5: Social Presence
```

**Credit Cost:** 6 credits per newsfeed fetch. Cache results for 7 days.

**Skip Section 5 if:**
- No LinkedIn URL available
- Nyne data already fetched within 7 days (check `nyne_newsfeed_last_fetched` in CRM)
- Internal stakeholder (no need for social intel)

---

## Input

- **Meeting Transcript:** `{{transcript}}`
- **Meeting Metadata:** `{{metadata}}`
- **Enrichment Context:** `{{enrichment_context}}` (from Step 2b of Meeting Process)

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B08
semantic_enrichment: true
---

# B08: Stakeholder Intelligence

## Section 1: Foundational Profile

| Field | Value |
|-------|-------|
| **Name** | [Full name] |
| **Title** | [Role/Position] |
| **Organization** | [Company/Org] |
| **Product/Service** | [What they do - 1-2 sentences] |
| **Motivation** | [Why they're doing this, what drives them] |
| **Funding Status** | [If discussed, else: Unknown - needs enrichment] |
| **Key Challenges** | [Main pain points mentioned] |
| **Standout Quote** | "[Something memorable that captures their approach/values]" |

## Section 2: What Resonated

Identify 3-5 moments of genuine enthusiasm, energy, or strong reaction.

### [Topic/Concept 1]
- **Quote:** "[Verbatim or near-verbatim]"
- **Why it resonated:** [Explanation]
- **Signal/Implication:** [What this reveals about priorities/fit]

### [Topic/Concept 2]
...

## Section 3: Relationship Context ⭐ MEMORY-ENRICHED

### Prior Relationship
- **Meeting History:** [First meeting / Nth meeting (count)]
- **Last Contact:** [Date if known, else: First contact]
- **Existing CRM Profile:** [Yes - path / No - will create]

### Trajectory Assessment
- **Relationship Direction:** [Warming / Stable / Cooling / New]
- **Evidence:** [What signals this trajectory]
- **Compared to Prior:** [How this meeting compares to previous interactions]

### Evolution Notes
- **Topics that consistently resonate:** [From meeting history]
- **Concerns that persist:** [Recurring issues across meetings]
- **New developments:** [What changed since last contact]

## Section 4: Domain Authority & Source Credibility

Track what topics this stakeholder is credible on:

### Primary Source Domains (Firsthand Experience)

#### [Domain 1 - e.g., "Enterprise Sales"]
- **Authority level:** ● ● ● ● ○ (4/5)
- **Based on:** [Specific experience that makes them credible]
- **Insights provided:** [Count] insights (B31 refs if applicable)

### Secondary Source Domains (Informed Perspective)
- [Domain]: ● ● ○ ○ ○ - [Why secondary not primary]

## Section 5: Social Presence (Nyne Intelligence)

**Source:** Nyne enrichment data (fetch if LinkedIn URL available)

### Social Profiles
| Platform | Handle | Followers | Link |
|----------|--------|-----------|------|
| Twitter/X | [@handle] | [count] | [url] |
| LinkedIn | [profile] | — | [url] |
| Instagram | [@handle] | [count] | [url] |
| YouTube | [channel] | [subscribers] | [url] |

### Recent Activity (Last 7 days)
Surface recent posts/activity that provide conversation context:

- **[Platform]** [Date]: "[Post excerpt or topic summary]"
  - *Engagement: [likes/comments/shares if notable]*
- **[Platform]** [Date]: "[Post excerpt or topic summary]"
  - *Engagement: [likes/comments/shares if notable]*
- **[Platform]** [Date]: "[Post excerpt or topic summary]"

*Note: Only include if Nyne newsfeed data available. Skip if no recent activity.*

### Interests & Topics
Based on social activity and follows, this stakeholder engages with:
- **[Category]:** [Interest 1], [Interest 2]
- **[Category]:** [Interest 3], [Interest 4]

### Conversation Starters (Nyne-Derived)
Based on recent posts and interests, consider opening with:
1. "[Topic from recent post — specific and timely]"
2. "[Shared interest or reaction to their content]"
3. "[Question about something they recently discussed]"

*Skip this section if no Nyne data available. Note: "Social presence data not available — LinkedIn URL required for Nyne enrichment."*

## Section 6: CRM Integration

- **Auto-create profile:** [Yes/No - based on stakeholder type]
- **Profile path:** `Knowledge/crm/individuals/[firstname-lastname].md`
- **Enrichment Priority:** [HIGH / MEDIUM / LOW] - [Rationale]
- **Mutual Acquaintances:** [List if identified, else: None identified - needs enrichment]
- **Next Actions:**
  - [ ] [Enrichment task 1]
  - [ ] [Enrichment task 2]

## Section 7: Howie Integration (V-OS Tags)

**Recommended Tags:** `[LD-XXX] [GPT-X] [A-X]`

| Tag | Value | Rationale |
|-----|-------|-----------|
| LD (Lead Type) | [INV/NET/COM/CUS/FND] | [Why] |
| GPT (Goal/Phase) | [E/M/C] | [Why] |
| A (Accommodation) | [1-4] | [Why] |

**Priority:** [Critical / Important / Non-critical]

---
**Feedback**: - [ ] Useful
---
```

## Quality Requirements

- **Use enrichment context** to provide historical grounding
- If first meeting: Note "First contact - baseline established"
- If recurring: Compare signals to prior meetings
- **Minimum 800 bytes** for substantive profile
- **CRM tags with rationale** - not just tags, explain why

## Anti-patterns

- ❌ Generating B08 without checking for prior relationship
- ❌ Treating every meeting as first contact
- ❌ Copy-pasting placeholder text
- ❌ Generic resonance without specific quotes

Generate B08 now with deep insight extraction and historical context.



