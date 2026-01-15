---
description: "Generate B11 Risks & Flags block from meeting transcript"
tags:
  - meeting-intelligence
  - block-generation
  - b11
  - risks
  - flags
tool: true
---
# Generate Block B11: Risks & Flags

**Input:** Meeting transcript provided in conversation context

**Your task:** Generate a B11 Risks & Flags block identifying warning signals and risk factors discussed in the meeting.

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
---

# B11: Risks & Flags

## Critical Flags
[High-priority warning signals requiring immediate attention]

## Risk Factors
[Specific risks identified with context]

## Mitigation Considerations
[Potential approaches to address risks, if discussed]
```

## Quality Standards
- Real, specific risks only (no generic/placeholder risks per P29)
- Extract actual concerns raised in conversation
- Distinguish between flags (immediate warnings) and risks (future concerns)
- Include context for each risk
- Min 300 words

**Generate the B11 block now using the transcript provided in this conversation.**

