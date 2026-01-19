---
description: Generate B25 Deliverable Content Map from meeting transcript
tags:
  - meeting-intelligence
  - block-generation
  - b25
  - deliverables
  - commitments
tool: true
---
# Generate Block B25: Deliverable Content Map

**Purpose:** Track all content deliverables, resources, and materials promised during the meeting. This block is a critical input for the Follow-Up Email Generator workflow.

**Input:** Meeting transcript + B02_COMMITMENTS block provided in conversation context

## Output Format

---

# B25: Deliverable Content Map

## Committed Deliverables

| Item | Promised By | Promised When | Status | Link/File | Notes |
|------|-------------|---------------|--------|-----------|-------|
| [Specific deliverable name] | [Us/Them/Both] | [Timeline or date] | [READY/IN_PROGRESS/BLOCKED] | [Path or URL if available] | [Any dependencies or context] |

**Example:**
| Item | Promised By | Promised When | Status | Link/File | Notes |
|------|-------------|---------------|--------|-----------|-------|
| Product demo recording | Us | Within 48 hours | READY | /Videos/demo_2025-11-15.mp4 | Edited version with Q&A |
| Case study deck | Us | End of week | IN_PROGRESS | - | Waiting on legal review |
| API documentation | Them | Next week | PENDING | - | Engineering team creating |

## Resources Mentioned

**Shared during meeting:**
- [Resource name]: [Brief description] - [URL or location]
- [Resource name]: [Brief description] - [URL or location]

**Requested for follow-up:**
- [Resource name]: [Who needs it] - [Why/context]
- [Resource name]: [Who needs it] - [Why/context]

## Links & References

**URLs shared:**
- [URL]: [Description of what it is]

**Documents referenced:**
- [Document name]: [Context/relevance]

## Follow-Up Content Needs

**Items to prepare before follow-up:**
- [ ] [Deliverable to create]
- [ ] [Deliverable to create]

**Items to request from them:**
- [ ] [What to ask for]
- [ ] [What to ask for]

---

## Quality Standards

**Completeness (P15):**
- ✓ ALL deliverables from both parties captured
- ✓ Accurate status (don't claim READY unless truly available)
- ✓ Specific file paths/URLs for READY items
- ✓ Clear timeline for IN_PROGRESS items

**Accuracy:**
- ✓ Cross-reference with B02_COMMITMENTS to ensure alignment
- ✓ Verify deliverable names match what was actually promised
- ✓ Status reflects reality (not aspirational)
- ✓ Dependencies and blockers noted

**Utility:**
- ✓ Information organized for easy action
- ✓ Clear what needs to happen before sending follow-up email
- ✓ Ready for Follow-Up Email Generator to reference
- ✓ Min 300 words

**Sources:**
- ✓ All deliverables sourced from transcript or B02
- ✓ No invented or assumed deliverables
- ✓ Quotes or timestamps for ambiguous items

## Integration Notes

This block is used by:
- **Follow-Up Email Generator** - References deliverables when drafting email
- **Commitment tracking** - Cross-checks against B02 for completeness
- **Content preparation workflow** - Identifies what needs to be created

**Key Principle:** This is ONLY the deliverables map. The actual follow-up email is generated separately by the Follow-Up Email Generator prompt, which loads this block as input.

**Generate the B25 block now using the transcript and B02_COMMITMENTS provided in this conversation.**

