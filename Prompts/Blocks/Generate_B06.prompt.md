---
description: Generate B06 Business Context block from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b06
  - business
  - strategy
  - market
version: 1.0
tool: true
created: 2025-11-15
last_edited: 2026-01-03
---

# Generate Block B06: Business Context & Implications

## Objective

Extract business strategy, market context, competitive landscape, and commercial implications discussed in the meeting. Focus on the "big picture" business thinking.

## What to Capture

**Business Strategy:**
- Strategic goals and priorities mentioned
- Business model discussions
- Go-to-market approaches
- Positioning and differentiation
- Partnership or alliance strategy

**Market Context:**
- Market size and opportunity
- Customer segments and needs
- Competitive landscape
- Industry trends or dynamics
- Market timing considerations

**Commercial Implications:**
- Revenue impact or potential
- Pricing strategy
- Cost considerations
- Resource allocation decisions
- ROI or business case thinking

**Risk & Opportunity:**
- Business risks identified
- Market opportunities discussed
- Competitive threats
- Strategic options evaluated

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
block_type: B06
---

# B06: Business Context & Implications

## Market Opportunity
[Description of market context discussed]
- Size, growth, key dynamics
- Customer needs identified

## Competitive Position
[How company/product fits in landscape]
- Key competitors mentioned
- Differentiation points
- Competitive advantages/disadvantages

## Strategic Direction
[High-level strategy discussed]
- Goals and priorities
- Approach being taken
- Rationale for direction

## Commercial Model
[Business model and economics]
- Revenue approach
- Pricing considerations
- Cost structure thoughts

## Implications & Next Steps
[What this means for business]
- Key takeaways
- Strategic decisions needed
- Business impact
```

## Generation Guidelines

1. Look for strategic language:
   - "Our strategy is..."
   - "The market for..."
   - "Competitively, we..."
   - "From a business perspective..."
   - "This could generate..."

2. Connect dots:
   - How does tactical discussion relate to bigger picture?
   - What are business implications of technical decisions?
   - Why does this matter commercially?

3. Distinguish from execution:
   - This block = WHY and WHAT (strategy)
   - Other blocks = HOW and WHO (tactics)

4. Capture reasoning:
   - Why is this approach being taken?
   - What assumptions underlie strategy?
   - What factors are driving decisions?

5. Note uncertainties:
   - What's validated vs. assumed?
   - Where is there disagreement or debate?

## When to Generate

Generate B06 when meeting includes:
- Strategic planning or roadmap discussions
- Sales/partnership negotiations
- Market or competitive analysis
- Business model or pricing decisions
- Investment or funding conversations
- Board-level strategic topics

Skip if meeting is purely tactical/operational with no strategic context.

Generate B06 now.

