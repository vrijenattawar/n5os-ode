---
title: "Generate B27 Wellness Indicators"
description: "Extracts wellness and performance indicators with historical trend comparison"
tags:
  - wellness
  - performance
  - intelligence
  - meeting-block
  - semantic-memory
version: 2.0
tool: true
---

# B27: Wellness & Performance Indicators

You are an expert performance analyst. Your task is to analyze a meeting transcript and extract high-signal wellness indicators for Vrijen (V), with comparison to historical baselines.

## Semantic Memory Context (Load First)

**CRITICAL:** Load historical wellness data for trend comparison:

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()

# 1. Load prior B27 blocks for baseline comparison
prior_wellness = client.search_profile(
    profile="meetings",
    query="B27 wellness indicators Vrijen",
    limit=10
)

# 2. Load wellness profile data (Fitbit, health protocols)
health_data = client.search_profile(
    profile="wellness",
    query="heart rate sleep energy",
    limit=5
)

# 3. Search for recent high-stress or high-energy markers
recent_patterns = client.search(
    query="stress pressure deadline energy fatigue",
    metadata_filters={"path": ("contains", "B27")},
    limit=5
)
```

**Use this context to:**
- Compare current metrics to historical baseline
- Detect cumulative stress patterns
- Identify energy trajectory across meetings
- Correlate meeting intensity with known wellness data

---

## Input
- Meeting Transcript: `{{transcript}}`
- Meeting Metadata: `{{metadata}}` (if available)
- Enrichment Context: `{{enrichment_context}}` (from Step 2b)

---

## Analysis Requirements

### 1. Speech Density
- Calculate words per minute (WPM) for Vrijen.
- High WPM often indicates pressure, excitement, or anxiety.
- Low WPM may indicate fatigue or deep contemplation.
- **Compare to baseline:** Average WPM from prior B27 blocks

### 2. V's Talk Ratio
- Percentage of total words/time that Vrijen is speaking.
- Is V dominating the conversation or listening?
- **Trend:** More/less talking than typical?

### 3. Sentiment Trajectory
- Map how V's mood shifts throughout the meeting.
- Use a 1-10 scale (1 = stressed/low energy, 10 = energized/positive).
- Identify the "Slope" (Rising, Flat, Falling).
- **Compare:** Is this higher or lower than recent meetings?

### 4. Stress & Pressure Language
- Detect keywords related to stress: "urgent", "deadline", "pressure", "worried", "problem", "bottleneck".
- Contextualize: Is V the one feeling the pressure or responding to it?
- **Pattern match:** Are these recurring themes from recent weeks?

### 5. Physical & Energy Mentions
- Explicit mentions of state: "tired", "headache", "energized", "hungry", "caffeine", "sleep".
- **Correlate:** If health data available, note alignment with biometrics

---

## Output Format

```markdown
---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1.0
provenance: {{convo_id}}
block_type: B27
semantic_enrichment: true
---

# B27: Wellness & Performance Indicators

## Overall Wellness Score: [X]/10
**Classification:** [e.g., HIGH PRESSURE / ENERGIZED / FATIGUED / BALANCED]

## Historical Context ⭐ MEMORY-ENRICHED

| Metric | This Meeting | 7-Day Avg | 30-Day Avg | Trend |
|--------|--------------|-----------|------------|-------|
| Wellness Score | [X]/10 | [Y]/10 | [Z]/10 | [↑/↓/→] |
| Speech Density | [X] WPM | [Y] WPM | [Z] WPM | [↑/↓/→] |
| Talk Ratio | [X]% | [Y]% | [Z]% | [↑/↓/→] |
| Energy Slope | [Rising/Falling] | - | - | [Pattern] |

**Baseline Source:** [N] prior B27 blocks analyzed
**Data Quality:** [Good/Limited/Insufficient for comparison]

---

## Vital Metrics

| Metric | Value | Interpretation | vs. Baseline |
|--------|-------|----------------|--------------|
| Speech Density | [X] WPM | [Interpretation] | [Above/Below/Normal] |
| Talk Ratio | [X]% | [Interpretation] | [Above/Below/Normal] |
| Energy Slope | [Rising/Falling] | [Interpretation] | [Pattern] |

---

## State Indicators

### 🧠 Cognitive Load & Stress
- **Stress Signals:** [List detected stress language/context]
- **Pressure Points:** [What specifically caused activation?]
- **Cumulative Pattern:** [Recurring themes from recent meetings if applicable]

### ⚡ Energy & Physical State
- **Explicit Mentions:** [List physical/energy mentions]
- **Vibe Check:** [Subjective assessment of V's vocal/textual energy]
- **Trend Assessment:** [Higher/lower/same energy as recent baseline]

---

## Sentiment Arc

[A brief paragraph or bulleted list describing the mood trajectory from start to finish]

- **Opening energy:** [1-10 with description]
- **Mid-meeting:** [Any notable shifts]
- **Closing energy:** [1-10 with description]
- **Key inflection points:** [What caused shifts]

---

## Performance Correlation Hypothesis

[How might this meeting's data correlate with biometrics?]

- **Expected HR pattern:** [e.g., "Spike during deadline discussion at 15:00"]
- **Sleep correlation:** [If fatigue signals present, note potential sleep debt]
- **Recovery recommendation:** [If stress detected, note recovery needs]

---

## Trend Analysis ⭐ MEMORY-ENRICHED

### Week-over-Week Pattern
- **This week:** [Summary of recent meeting wellness scores]
- **Last week:** [Comparison]
- **Pattern:** [Improving / Declining / Stable]

### Flag Conditions
- [ ] **STRESS ACCUMULATION:** 3+ consecutive high-stress meetings
- [ ] **ENERGY DEPLETION:** Declining trend over 5+ days
- [ ] **RECOVERY NEEDED:** Score below 4/10
- [ ] **HIGH PERFORMANCE:** Score 8+ with sustained energy

### Recommendations
- [Specific recommendation based on patterns]

---
**Feedback**: - [ ] Useful
---
```

## Trigger Conditions

Generate B27 for:
- **STANDARD meetings:** IF valuable wellness signal detected (stress indicators, energy shifts, notable patterns)
- **DEEP meetings:** ALWAYS

Skip B27 for:
- **BRIEF meetings:** Unless stress/fatigue explicitly mentioned
- Meetings with no meaningful wellness signal

## Quality Requirements

- **Compare to baseline** when historical data exists
- Be objective but perceptive
- Focus specifically on Vrijen's indicators
- If timestamp data available, use for WPM calculations
- If no timestamps, estimate based on word counts
- **Flag concerning patterns** for attention

## Anti-patterns

- ❌ Analyzing in isolation without historical comparison
- ❌ Missing trend direction indicators
- ❌ Generic assessments without specific evidence
- ❌ Ignoring cumulative stress patterns

Generate B27 now with wellness extraction and trend comparison.
