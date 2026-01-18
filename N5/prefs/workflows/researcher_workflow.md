---
created: 2025-12-16
last_edited: 2025-12-16
version: 1.0
provenance: con_TU8sAIUts3Mzvqq6
---

# Researcher Workflow

## Overview

Rigorous 5-phase research methodology with adaptive modes. Load this file for substantive research tasks.

---

## Phase 1: Clarify (10% of effort)

**BEFORE ANY RESEARCH**, establish:

### 1.1 Core Questions
- What's the *real* question? (Not just what was asked - what decision depends on this?)
- What would "good" research deliver? (Success criteria)
- Scope: breadth vs. depth? How much time?
- Who is the audience? What format?

### 1.2 Document Assumptions
```
## Research Assumptions
- Assuming: [X]
- Assuming: [Y]
- Explicitly NOT covering: [Z]
```

### 1.3 Propose Strategy
Present research approach and get confirmation before proceeding:
- Which adaptive mode? (Speed/Deep/Challenge/Intel/Balanced)
- Key search angles
- Expected sources

**Soft failsafe:** If request unclear or contradictory → clarify, don't guess.

---

## Phase 2: Breadth Scan (30% of effort)

### 2.1 Parallel Searches
Run 3-5 searches with **varied queries**:
- Direct query
- Synonym/alternative framing
- Contrarian angle ("criticism of X", "problems with X")
- Adjacent domain (who else cares about this?)
- Historical angle (how has this evolved?)

### 2.2 Landscape Mapping
- Key players/authors/sources
- Core concepts and terminology
- Active debates and controversies
- Knowledge state: 🔒 SETTLED | 🔄 EVOLVING | 🆕 EMERGING
- Decay rate: ⚡ FAST | 🔸 MODERATE | 🔹 SLOW

### 2.3 Triage for Deep Dive
Flag high-value areas for Phase 3. Don't boil the ocean.

---

## Phase 3: Deep Dive (40% of effort)

### 3.1 Source Prioritization
- **Primary sources** when available (original research, not summaries)
- Credibility assessment: 🟢 High | 🟡 Medium | 🔴 Low | ❓ Unknown
- Note source vintage when relevant: "(2019, ⚡ fast decay field)"

### 3.2 Claim Validation
For each key claim:
```
Claim: [Statement]
Source: [^n]
Confidence: 🟢🟡🔴❓
Supporting evidence: [X]
Contradicting evidence: [Y]
```

### 3.3 Steel Man Opposing Views
Actively seek contrarian sources. Present the **best** version of opposing arguments, not strawmen.

### 3.4 Track What's NOT Found
Knowledge gaps are findings too:
- "Searched for X, no credible sources found"
- "Expected to find Y, but sources silent on this"

### 3.5 Watch Diminishing Returns
If you're not learning new things, stop and move to synthesis.

---

## Phase 4: Synthesize (15% of effort)

### 4.1 Structure
```
## Key Findings
1. [Finding] (Confidence: 🟢, Implications: [X]) [^n]
2. [Finding] (Confidence: 🟡, Implications: [Y]) [^n]

## Patterns
- Pattern 1: [Theme across findings]
- Pattern 2: [Another theme]

## Steel Man: [Opposing View]
The strongest argument against this is... [present fairly]

## Knowledge Gaps
- Gap 1: [What we don't know] (Impact: High/Medium/Low)
- Gap 2: [Another gap]

## Implications
- Decision: [What this means for the original question]
- Action: [Recommended next steps]
- Caution: [What could go wrong]

## Follow-Up Agenda (Prioritized)
1. [Most important open question]
2. [Second priority]
3. [Third priority]
```

### 4.2 "So What?" Test
Every section must answer: **Why does this matter for the decision at hand?**

If you can't answer that, you're data-dumping, not synthesizing.

---

## Phase 5: Validate (5% of effort)

### 5.1 Self-Audit Checklist
- [ ] Every key claim has [^n] citation
- [ ] Confidence ratings justified (not guessed)
- [ ] Contrarian sources sought and addressed
- [ ] Knowledge gaps documented honestly
- [ ] "So what?" is clear and actionable
- [ ] Follow-up agenda prioritized

### 5.2 Bias Check
- Did I seek disconfirming evidence?
- Did I present opposing views fairly?
- Did I let my assumptions drive the research?

---

## Adaptive Modes

| Mode | Use When | Approach |
|------|----------|----------|
| **Speed** | Time-constrained, need 80/20 | Breadth only, 🟡 confidence acceptable |
| **Deep** | High-stakes, need certainty | Exhaustive, PRIMARY sources, 🟢 required |
| **Challenge** | Testing assumptions | Actively seek disconfirming evidence |
| **Intel** | Competitive/market research | Cui bono analysis, stakeholder mapping |
| **Learn** | Building understanding | Explain as you go, bridge to Teacher |
| **Balanced** | Default | Breadth → selective deep-dives |

Declare mode at start: "Using **[Mode]** mode because [reason]."

---

## Anti-Patterns & Fixes

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| **Surface Skimming** | Only first 3 results | 3-5 parallel varied searches |
| **Citation Laziness** | "Studies show..." | Every claim needs [^n] |
| **Hallucination** | Fill gaps with speculation | State "no evidence found" |
| **Confirmation Bias** | Only supporting evidence | Seek contrarian sources |
| **Echo Chamber** | Fail to challenge user perspective | Present opposing views fairly |
| **Data Dump** | Facts without synthesis | Findings → Patterns → "So what?" |
| **Rabbit Hole** | Endless research | Time-box, watch diminishing returns |

---

## Citation Standards

```markdown
Claim text here [^1].

[^1]: Author, "Title", Source (Year). Credibility: 🟢. Note: [context if relevant]
```

**Language by confidence:**
- 🟢 HIGH: "Evidence shows...", "Research demonstrates..."
- 🟡 MEDIUM: "Evidence suggests...", "Research indicates..."
- 🔴 LOW: "Limited evidence suggests...", "One source claims..."
- ❓ UNKNOWN: "May...", "Possibly...", "Unclear whether..."

---

## Output Template

```markdown
# Research: [Topic]

## Parameters
- **Question**: [The real question being answered]
- **Mode**: [Speed/Deep/Challenge/Intel/Learn/Balanced]
- **Knowledge State**: 🔒 SETTLED | 🔄 EVOLVING | 🆕 EMERGING
- **Scope**: [What's included/excluded]

## Key Findings
1. [Finding with confidence and citation]

## Patterns
- [Cross-cutting themes]

## Steel Man: [Best Opposing Argument]
[Present fairly]

## Knowledge Gaps
- [What we don't know, with impact]

## Implications
- Decision: [What this means]
- Action: [Next steps]
- Caution: [Risks]

## Follow-Up Agenda
1. [Prioritized open questions]

## Citations
[^1]: [Full citation with credibility note]
```