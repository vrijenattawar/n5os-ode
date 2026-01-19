---
description: Generate R09 Content Idea block from reflection input
tags: [reflection, block, r09, content, publishing]
tool: true
version: 2.0
---

# R09: Content Idea — Deep Analytical Framework

**Block ID:** R09
**Block Name:** Content Idea
**Purpose:** Extract content thesis, audience, format fit, and publishing opportunities.

---

## 1. Domain Definition

### What This Lens Sees
R09 captures **content and publishing opportunities**:

- **Blog post ideas:** Long-form written content
- **Social media angles:** Twitter threads, LinkedIn posts
- **Newsletter topics:** Email content ideas
- **Speaking opportunities:** Talk or podcast material
- **"People need to hear this":** Insights demanding audience
- **Teaching opportunities:** Educational content
- **Thought leadership angles:** Position-establishing content

### What This Lens Ignores
- **The actual learning** → R02 (Learning Note)
- **Market analysis being discussed** → R04 (Market Signal)
- **Synthesis/framework** → R06 (Synthesis)

### Boundary Cases
- If learning could be content: The learning in R02; publishing angle here
- If synthesis is publishable: Framework in R06; content format/audience here

---

## 2. Extraction Framework

### Trigger Patterns
```
Content words: blog, post, write about, article, newsletter, tweet,
               thread, LinkedIn, publish, share

Audience words: people need to know, founders should hear, most don't
                realize, common mistake, underrated, contrarian

Format words: could be a talk, podcast topic, course idea, guide,
              how-to, explainer

Signal words: I should write about, note to self to share, would make
              a good post
```

### Counter-Indicators
- Content is the insight itself (not the publishing angle)
- No audience or format consideration

---

## 3. Analysis Dimensions

### Dimension 1: Content Type
| Type | Best For |
|------|----------|
| **Long-form** | Deep dives, nuanced takes |
| **Short-form** | Quick insights, hot takes |
| **Interactive** | Stories, conversations |
| **Educational** | How-to, skill transfer |

### Dimension 2: Target Audience
| Audience | Platforms |
|----------|-----------|
| **Founders/entrepreneurs** | Twitter, Substack |
| **Career professionals** | LinkedIn, newsletters |
| **Recruiters/HR** | LinkedIn, industry pubs |
| **Tech community** | Twitter, dev blogs |

### Dimension 3: Uniqueness
| Angle | Strength |
|-------|----------|
| **Novel take** | High — if credible |
| **Contrarian view** | High — if defensible |
| **Personal experience** | High — if relatable |
| **Synthesis** | Medium — if well-executed |

### Dimension 4: Timeliness
| Timing | Action |
|--------|--------|
| **Time-sensitive** | Publish soon |
| **Evergreen** | Publish anytime |
| **Seasonal** | Plan for timing |

### Dimension 5: Effort to Produce
| Level | Time |
|-------|------|
| **Quick** | < 1 hour |
| **Medium** | Hours |
| **Substantial** | Days |

---

## 4. Memory Integration

```python
from N5.cognition.n5_memory_client import N5MemoryClient

profiles_to_query = ["knowledge", "positions"]

def enrich_content_idea(transcript_key_concepts: list[str]) -> dict:
    client = N5MemoryClient()

    prior_content = client.search_profile(
        profile="knowledge",
        query=f"content published blog post {' '.join(transcript_key_concepts)}",
        limit=5
    )

    supporting_positions = client.search_profile(
        profile="positions",
        query=f"{' '.join(transcript_key_concepts)}",
        limit=5
    )

    return {"prior_content": prior_content, "supporting_positions": supporting_positions}
```

---

## 5. Output Schema

```markdown
## R09: Content Idea

**Generated:** {timestamp}
**Provenance:** {conversation_id}
**Source:** {reflection_file}

### Content Summary
**Title/Hook:** [Working title]
**Type:** [Long-form | Short-form | Interactive | Educational]
**Audience:** [Target audience]
**Timeliness:** [Time-sensitive | Evergreen | Seasonal]

### The Idea

#### The Core Thesis
[1-2 sentences: what's the main point]

#### Why This Matters to the Audience
[Why they should care]


### Edge Candidates
[Entities/concepts from this analysis that RIX should check for connections]
- `{concept_1}` — {potential_connection_domain}
- `{concept_2}` — {potential_connection_domain}

### Evidence
> [Direct quote showing content spark]

### Uniqueness Angle
**What makes this worth reading:**
[Novel take | Contrarian view | Personal experience | Synthesis]

### Format Recommendation
**Best format:** [Specific format]
**Why:** [Format rationale]

### Effort Estimate
**Production time:** [Quick | Medium | Substantial]
**Key components:** [What needs to be created]

### Distribution Plan
**Primary platform:** [Where to publish]
**Secondary distribution:** [Where to share/repurpose]

### Memory Connections
- **Related content:** [Prior posts]
- **Supporting positions:** [Positions that inform this]
```

---

## 6. Connection Hooks

### Upstream
- "Following up on my post about..."
- References to prior published content

### Downstream
- Tag the topic/theme
- Tag the audience

---

## 7. Worked Example

### Sample Input
```
I keep telling founders the same thing: stop optimizing your resume pitch
and start understanding why investors say no. Most founders pitch what
they're building, not why it matters. This would make a good thread —
"Why investors really say no: a decoder ring."
```

### Final Output
```markdown
## R09: Content Idea

**Generated:** 2026-01-09T12:00:00Z
**Source:** 2026-01-09_founder-advice/transcript.md

### Content Summary
**Title/Hook:** "Why investors really say no: a decoder ring"
**Type:** Short-form (Twitter thread)
**Audience:** Founders/entrepreneurs
**Timeliness:** Evergreen

### The Idea

#### The Core Thesis
Most founders pitch what they're building instead of why it matters. "Interesting but not for us" usually means "I don't understand."

#### Why This Matters to the Audience
Founders waste hours misinterpreting investor feedback.

### Evidence
> "stop optimizing your resume pitch and start understanding why investors say no"

### Uniqueness Angle
**What makes this worth reading:** Insider decoding + contrarian take

### Format Recommendation
**Best format:** Twitter thread (7-10 tweets)
**Why:** Snackable, shareable, the list format works

### Effort Estimate
**Production time:** Quick (< 1 hour)
**Key components:** List of 5-7 rejections with "real" meanings

### Distribution Plan
**Primary platform:** Twitter
**Secondary distribution:** Cross-post to LinkedIn
```

---

## Quality Checklist

- [ ] Title/hook is compelling
- [ ] Audience is specific
- [ ] Uniqueness angle is genuine
- [ ] Format choice has rationale

## Not Applicable Criteria

```markdown
## R09: Content Idea

**Status:** Not applicable

**Reason:** Reflection does not contain content ideas or publishing angles.

**Alternative blocks that may apply:** [R02, R06, R01, etc.]
```

---

*Template Version: 2.0 | R-Block Framework | 2026-01-09*
