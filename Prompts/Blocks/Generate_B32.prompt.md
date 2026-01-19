---
description: Generate B32 Thought Provoking Ideas block
tags: [meeting-intelligence, block-generation, b32, thought-provoker, wisdom-capture]
tool: true
created: 2025-12-22
updated: 2026-01-03
version: 2.0
provenance: con_hrrnHOCuFRK8x2KS
---

# Generate Block B32: Thought Provoking Ideas

Extract 1-3 genuinely provocative worldview positions or strategic insights that emerged during the meeting.

## Core Purpose

Capture **wisdom-level insights** that:
- Represent falsifiable beliefs or principles V endorses (or is actively questioning)
- Have lasting relevance beyond this specific meeting
- Could inform future decisions, strategy, or worldview

## Classification

For each potential idea, classify as:
- **V_POSITION**: A belief V endorses as true → Extract
- **V_HYPOTHESIS**: Speculation V is testing → Extract with questioning stance
- **EXTERNAL_WISDOM**: Someone else's insight worth tracking → Extract with speaker attribution
- **QUESTION/TACTICAL/META**: Open questions, operational tasks, or meeting mechanics → SKIP

## Guidelines

- **FORBIDDEN**: Actionable tasks, tactical follow-ups, or standard meeting recaps. If it can be a task, it belongs in B05 or B02.
- **THRESHOLD**: If no truly provocative or original ideas exist, DO NOT generate any output. An empty response is a success signal.
- **CRINGE FILTER**: Avoid shallow AI-platitudes. If the idea isn't truly novel or surprising in V's worldview, skip it.
- **PRINCIPLE-GROUNDED**: Reasoning must explain WHY something is true IN GENERAL, not just restate the specific anecdote.
- **DOMAIN EXPANSION**: The listed domains are V's known intellectual territories, but **do not constrain capture to them**. If a genuinely provocative, counterintuitive, or original idea emerges in ANY domain — even one not listed — capture it and mark as `emerging`. New domains reveal themselves through what gets captured. Cast a wide net; categorization comes after capture.

## Output Format

For each provocation, use this EXACT structure:

```
### [Provocation/Idea Title]

**Speaker**: V | [Person's name]
**Classification**: V_POSITION | V_HYPOTHESIS | EXTERNAL_WISDOM
**Domain**: hiring-market | careerspan | ai-automation | founder | worldview | epistemology | emerging

**The Spark**:
What was said or implied that triggered this thought? (Direct quote or paraphrase from transcript)

**The Insight**:
2-3 sentence core observation. What do you see that others don't? The belief in enough detail to be meaningful and falsifiable.

**The Principle**:
Why this is true IN GENERAL—not grounded in the specific anecdote, but in underlying mechanisms, human psychology, market dynamics, or structural forces that apply across contexts. Reference analogies or parallel domains where the same principle applies.

**The Stakes**:
What follows from this? Why it matters. Implications for action, belief, or strategy. If this is true, what should change?

**Boundary Conditions**:
When does this apply? Where does the principle break down or not hold? Edge cases and limitations.
```

---

## Example

### Story Minimum for Human Portability

**Speaker**: V
**Classification**: V_POSITION
**Domain**: careerspan

**The Spark**:
"If your whole professional identity can be captured in 6 stories... what does that mean for how we think about career ownership?"

**The Insight**:
Professional identity can be compressed into a small set of carefully chosen career stories without losing essential meaning. The traditional resume's verbosity is not thoroughness—it's noise that obscures signal. Competitive advantage shifts from having experience to precision of mapping stories to opportunities.

**The Principle**:
Information compression follows a power law: the first few data points capture most of the variance. In narrative identity, 6 well-chosen stories can represent the "eigenvalues" of a person's professional capability. This mirrors how investors evaluate founders (a few key stories) rather than exhaustive CVs. The pattern exists because humans are narrative creatures who make decisions through pattern-matching on stories, not data integration.

**The Stakes**:
Career infrastructure should optimize for story elicitation and precision mapping rather than exhaustive documentation. Coaching becomes about surfacing the right 6 stories, not adding more content. Hiring processes could be radically shortened if candidates came with pre-validated, high-signal story portfolios.

**Boundary Conditions**:
Applies when the evaluator is human and decision-making is intuition-driven. Breaks down in highly technical screening (where specific skills verification matters) or regulated industries requiring documented credentials. Less relevant for entry-level candidates who lack sufficient story material.

---

## Requirements

- Minimum 1 provocation, maximum 3
- Must be rooted in the meeting transcript
- Strictly conceptual/strategic, never tactical
- All fields must be filled (no empty sections)
- Reasoning must be PRINCIPLE-GROUNDED, not ANECDOTE-GROUNDED

### Principle-Grounded vs. Anecdote-Grounded

**WRONG (anecdote-grounded):**
> "When Victor mentioned treating YOUR_COMPANY as a portfolio company, he showed that investors think modularly."

**RIGHT (principle-grounded):**
> "Portfolio construction logic increasingly treats investments as modular ecosystem components rather than standalone bets. This reflects a shift from 'best company wins' to 'best network wins'—the same pattern driving platform economics, where value accrues to orchestrators more than individual nodes."

---

Generate B32 now.

