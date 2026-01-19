---
description: Generate B21 Key Moments block from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b21
  - quotes
  - insights
  - moments
version: 1.0
tool: true
created: 2025-11-15
last_edited: 2026-01-03
---

# Generate Block B21: Key Quotes & Strategic Questions

## Objective

Capture memorable quotes, powerful statements, and important questions that represent pivotal or insightful moments in the conversation.

## What to Capture

**Memorable Quotes:**
- Insights or wisdom shared
- Strong positions stated
- Commitments declared
- Concerns expressed powerfully
- Turning points in discussion
- Revealing statements about priorities/values

**Strategic Questions:**
- Questions that reframed the conversation
- Probing questions that surfaced key issues
- Questions left hanging that matter
- Questions that challenged assumptions
- Questions that drove toward clarity

**Why These Matter:**
- They crystallize key thinking
- They're reusable in presentations, proposals, follow-up
- They capture tone and emphasis
- They reveal what really matters to participants

## Input Variables

- **Meeting Transcript:** `{{transcript}}`
- **Meeting Metadata:** `{{metadata}}`

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B21
---

# B21: Key Quotes & Strategic Questions

## Key Quotes

**"[Direct quote]"**  
— [Speaker Name]  
*Context:* [What was being discussed, why this mattered]

**"[Direct quote]"**  
— [Speaker Name]  
*Context:* [Situation and significance]

## Strategic Questions Raised

**"[Question]"**  
— [Who asked]  
*Significance:* [Why this question mattered, what it revealed]
```

## Generation Guidelines

1. Listen for impact:
   - Statements that land with weight
   - Questions that shift discussion
   - Moments of clarity or insight
   - Expressions of strong feeling

2. Be selective:
   - Quality over quantity (5-10 items max)
   - Choose what's truly memorable
   - Pick quotes that are reusable

3. Capture exactly:
   - Use direct quotes (don't paraphrase)
   - Include speaker attribution
   - Preserve tone and emphasis

4. Provide context:
   - Why does this quote matter?
   - What was happening when this was said?
   - How did it land with others?

5. Strategic value:
   - Can this be used in follow-up?
   - Does this reveal priorities?
   - Does this crystallize key thinking?

## Examples

### Good Quote Capture:

**"We're not just buying technology, we're buying a partnership with someone who understands our mission."**  
— Nicole Holubar (Emory Career Services)  
*Context:* Explaining what matters most in vendor selection beyond features. Signals that relationship and shared values are decision factors, not just capability.

**"The question isn't whether we can build this ourselves — it's whether we should, given opportunity cost."**  
— Vrijen Attawar  
*Context:* Reframing build vs. buy discussion from capability to strategy. Shifted conversation from technical to business priorities.

### Avoid:

- Mundane operational statements
- Generic pleasantries
- Repetitive points already covered elsewhere
- Out-of-context quotes that don't stand alone

## When to Generate

Generate B21 for meetings with:
- Strategic importance
- Key stakeholders whose words carry weight
- Moments of clarity or breakthrough
- Strong statements about values/priorities

Every meeting has SOME memorable moments, but be selective.

Generate B21 now.

