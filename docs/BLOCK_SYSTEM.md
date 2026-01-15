---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: worker_006_documentation
---

# N5OS Ode Block System

Blocks are structured generators that transform raw content (meeting transcripts, reflections, notes) into organized intelligence. This document explains what blocks are, how to use them, and how to create custom blocks.

---

## What Are Blocks?

A **block** is a focused extraction prompt that pulls specific types of information from source content.

**Example**: Feed a 60-minute meeting transcript to block B02. Get back a clean list of commitments made:

```yaml
# B02 Output
commitments:
  - owner: "Sarah"
    action: "Send revised proposal"
    deadline: "Friday EOD"
    context: "Client requested changes to scope section"
    
  - owner: "Mike" 
    action: "Schedule follow-up with legal"
    deadline: "Next week"
    context: "Contract review needed before signing"
```

No reading through the transcript. Just the commitments, structured and actionable.

---

## Included Blocks

### Meeting Blocks (B-Series)

| Block | Extracts | Use When |
|-------|----------|----------|
| **B01** | Detailed recap | You want a comprehensive summary |
| **B02** | Commitments | You need to track who promised what |
| **B03** | Decisions | You want to record what was decided |
| **B04** | Open questions | Uncertainties that need resolution |
| **B05** | Questions raised | Topics that came up for discussion |
| **B06** | Business context | Company/market info mentioned |
| **B11** | Risks & flags | Concerns that need attention |

### Reflection Blocks (R-Series)

| Block | Purpose | Best For |
|-------|---------|----------|
| **R01** | Personal insights | Self-understanding, patterns |
| **R02** | Learning notes | New knowledge, skills |
| **R06** | Synthesis | Connecting ideas across domains |

---

## Using Blocks

### Manual Invocation

Invoke any block with `@`:

```
@Generate_B02

[Paste transcript or reference file here]
```

The block generator will:
1. Analyze the content
2. Extract relevant information
3. Output structured results (usually YAML or markdown)

### Multiple Blocks

Run several blocks on the same source:

```
@Generate_B01 @Generate_B02 @Generate_B03

[Transcript]
```

Or run them sequentially for more focused output.

### With Meeting Files

If you have a meeting transcript file:

```
@Generate_B02

Source: file 'Records/meetings/2026-01-15-client-call.md'
```

---

## Block Output Formats

### YAML (Default)

Most blocks output structured YAML:

```yaml
decisions:
  - decision: "Use vendor A for infrastructure"
    rationale: "Lower cost, better support SLA"
    participants: ["Sarah", "Mike", "CEO"]
    implications: "Need to migrate by Q2"
```

### Markdown

Some blocks output formatted markdown for readability:

```markdown
## Meeting Recap

**Attendees**: Sarah (PM), Mike (Eng), Client Team

**Purpose**: Q1 planning review

### Key Points
1. Budget approved for new initiative
2. Timeline moved to March launch
3. Hiring two additional engineers
```

### Hybrid

Complex blocks may combine both:

```markdown
## Business Context

Company is expanding into European markets...

### Structured Data

​```yaml
market_intel:
  expansion_target: "Europe"
  timeline: "2026 H2"
  budget: "Undisclosed"
​```
```

---

## Creating Custom Blocks

### Block Anatomy

Every block prompt follows this structure:

```markdown
---
title: Generate_BXX
tags: [block, extraction, meeting]
description: What this block extracts
---

# BXX: [Block Name]

## Purpose
What this block extracts and why it's useful.

## Input
What kind of content to provide (transcript, notes, etc.)

## Output Format
[YAML/Markdown specification]

## Extraction Rules
- Specific guidance for what to include
- What to exclude
- Edge case handling

## Example

### Input
[Sample transcript snippet]

### Output
[Sample structured output]
```

### Design Guidelines

**Be Specific**: "Extract commitments with owner, action, deadline, and context" not "Find the important stuff"

**Define Output**: Exact YAML/Markdown structure expected

**Include Examples**: Show input → output transformation

**Handle Edge Cases**: What if no commitments? What if deadline is vague?

### Example: Custom Block

Create `Prompts/Blocks/Generate_B50.prompt.md`:

```markdown
---
title: Generate_B50
tags: [block, extraction, custom]
description: Extract mentioned tools and technologies
---

# B50: Technical Stack Mentions

## Purpose
Extract all tools, technologies, platforms, and technical concepts mentioned in a meeting or document.

## Output Format

​```yaml
technical_mentions:
  - name: "[Tool/Technology]"
    category: "[infrastructure|frontend|backend|data|other]"
    context: "[How it was discussed]"
    sentiment: "[positive|negative|neutral]"
​```

## Extraction Rules
- Include explicit mentions only (not implied)
- Category should be best-fit, not exhaustive
- Context is 1 sentence max
- Sentiment reflects how the speaker discussed it

## Example

### Input
"We've been using Kubernetes for orchestration and it's been solid. Sarah mentioned she's had issues with the Jenkins pipeline though - thinking about switching to GitHub Actions."

### Output
​```yaml
technical_mentions:
  - name: "Kubernetes"
    category: "infrastructure"
    context: "Currently used for orchestration"
    sentiment: "positive"
    
  - name: "Jenkins"
    category: "infrastructure" 
    context: "Current CI/CD pipeline"
    sentiment: "negative"
    
  - name: "GitHub Actions"
    category: "infrastructure"
    context: "Considering as Jenkins replacement"
    sentiment: "positive"
​```
```

---

## Block Best Practices

### 1. One Block, One Focus

Each block should extract one type of thing well. Don't try to extract commitments AND decisions AND risks in one block.

### 2. Structured > Prose

YAML output is easier to process, filter, and integrate. Use markdown for human-readable summaries only.

### 3. Include "None Found"

Blocks should handle empty results gracefully:

```yaml
commitments: []
# OR
commitments:
  note: "No explicit commitments identified in this transcript"
```

### 4. Context Matters

Include enough context in extractions to be useful standalone:
- BAD: `action: "Send the thing"`
- GOOD: `action: "Send revised Q1 budget proposal to finance team"`

### 5. Version Your Blocks

When modifying blocks, update the version in frontmatter. Keep old versions if you have data generated from them.

---

## Combining Blocks

### Meeting Processing Workflow

For a comprehensive meeting analysis:

1. **B01** — Detailed recap (overview)
2. **B02** — Commitments (action items)
3. **B03** — Decisions (what was decided)
4. **B04** — Open questions (unresolved)
5. **B11** — Risks (concerns flagged)

### Reflection Workflow

For journaling:

1. **R01** — Personal insights (self-understanding)
2. **R02** — Learning notes (new knowledge)
3. **R06** — Synthesis (connecting themes)

---

## Troubleshooting

**Block returns empty?**
- Check if source content actually contains the target information
- Try a more general block first (B01 for overview)
- Ensure transcript is clean and readable

**Output format wrong?**
- Explicitly request format: "Output as YAML, not prose"
- Check block prompt has clear format specification

**Missing context?**
- Add extraction rule: "Include enough context to understand standalone"
- Provide example showing desired detail level

---

*Blocks transform information overload into actionable intelligence.*

