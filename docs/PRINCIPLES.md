---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_TU8sAIUts3Mzvqq6
---

# Principles Library

## What Are Principles?

Principles are accumulated architectural wisdom captured in parseable YAML format. Each principle represents a tested guideline for making decisions about code quality, system design, error handling, and workflow orchestration.

These principles are **universally applicable**—they work across different projects, technologies, and contexts. They're not opinions; they're battle-tested patterns that emerge from real-world experience.

## Why Principles Matter

- **Prevent costly mistakes**: Principles like P15 (Complete Before Claiming) and P23 (Identify Trap Doors) catch errors before they cascade
- **Reduce technical debt**: Following P28 (Plans As Code DNA) means cleaner implementations that require less refactoring
- **Enable consistency**: A shared language for discussing design trade-offs and architectural decisions
- **AI-friendly**: YAML format enables automated loading, querying, and application by AI systems

## Principle File Format

Each principle is a standalone YAML file with this structure:

```yaml
---
id: P1
name: Human-Readable First
category: code_patterns
priority: high
version: "1.0.0"
created: "2025-11-02"

purpose: |
  One-sentence summary of what this principle achieves

when_to_apply:
  - Situation where principle applies
  - Another situation

pattern:
  core_behavior: |
    The actual behavior/guideline

examples:
  - description: Example scenario
    good: "What correct application looks like"
    bad: "What incorrect application looks like"

anti_patterns:
  - symptom: "Common mistake"
    fix: "How to avoid it"

related_principles:
  - P2: Another principle
```

### Key Fields

| Field | Description |
|-------|-------------|
| `id` | Short identifier (P1, P2, etc.) |
| `name` | Human-readable name |
| `category` | Grouping: `code_patterns`, `quality`, `communication`, `safety`, `design`, `strategy`, `workflow` |
| `priority` | `critical`, `high`, `medium`, `low` |
| `purpose` | What the principle achieves |
| `when_to_apply` | Situations where the principle is relevant |
| `pattern` | Core behavior guideline |
| `examples` | Concrete good/bad examples |
| `anti_patterns` | Common mistakes and fixes |
| `related_principles` | Cross-references to related principles |

## Using Principles

### Loading a Principle

```python
import yaml

def load_principle(principle_id):
    """Load a principle by ID"""
    path = f"N5/prefs/principles/P{principle_id}_*.yaml"
    # Find and parse the file
    with open(path) as f:
        return yaml.safe_load(f)
```

### Querying the Index

```python
import yaml

with open("N5/prefs/principles/principles_index.yaml") as f:
    index = yaml.safe_load(f)

# Get all critical principles
critical = [p for p in index['principles'].values()
            if p['priority'] == 'critical']

# Get principles by category
design_principles = [p for p in index['principles'].values()
                     if p['category'] == 'design']
```

### Applying a Principle at Build Time

When creating a build plan, check for relevant principles:

```python
def check_relevant_principles(plan_context):
    """Return principles relevant to the current context"""
    # plan_context contains: file_changes, new_systems, destructive_ops
    relevant = []

    if plan_context['destructive_operations']:
        relevant.extend([
            'P05',  # Safety, Determinism, and Anti-Overwrite
            'P19',  # Error Handling is Not Optional
        ])

    if plan_context['trap_doors']:
        relevant.append('P23')  # Identify Trap Doors

    return relevant
```

## Adding Custom Principles

When you discover a new pattern worth codifying:

1. **Check if it's already covered**: Review `principles_index.yaml` first
2. **Follow the format**: Use the same YAML structure as existing principles
3. **Use the next available ID**: Find the highest P-number and increment
4. **Update the index**: Add the new principle to `principles_index.yaml`
5. **Test parsing**: Ensure the YAML file is valid

### Naming Convention

```
P<two_digit_number>_<snake_case_name>.yaml
```

Example: `P45_api_design_first.yaml`

## Principle Categories

### Critical Priority (Must Apply)
- **P15**: Complete Before Claiming Complete — Progress reporting discipline
- **P19**: Error Handling is Not Optional — Recovery paths for all systems
- **P23**: Identify Trap Doors — Spot irreversible decisions early
- **P28**: Plans As Code DNA — Plan quality determines code quality
- **P32**: Simple Over Easy — Choose fewer concepts over familiarity

### High Priority (Strongly Recommended)
- Code Patterns: P01, P02, P07, P08, P13
- Quality: P05, P11, P16, P18, P20, P21
- Design: P32
- Strategy: P23, P27, P28
- Communication: P08
- Safety: P19
- Workflow: P36

## Quick Reference

| ID | Name | Category | Priority |
|----|------|----------|----------|
| P01 | Human-Readable First | code_patterns | high |
| P02 | Single Source of Truth | quality | high |
| P05 | Safety, Determinism, and Anti-Overwrite | quality | high |
| P07 | Idempotence and Dry-Run by Default | code_patterns | high |
| P08 | Minimal Context, Maximal Clarity | communication | high |
| P11 | Failure Modes and Recovery | quality | high |
| P13 | Naming and Placement | code_patterns | medium |
| P15 | Complete Before Claiming Complete | quality | critical |
| P16 | Accuracy Over Sophistication | quality | high |
| P18 | State Verification is Mandatory | quality | high |
| P19 | Error Handling is Not Optional | safety | critical |
| P20 | Modular Design for Context Efficiency | design | high |
| P21 | Document All Assumptions, Placeholders, and Stubs | quality | high |
| P23 | Identify Trap Doors | strategy | critical |
| P27 | Nemawashi Mode | strategy | high |
| P28 | Plans As Code DNA | strategy | critical |
| P32 | Simple Over Easy | design | critical |
| P36 | Orchestration Pattern | workflow | high |

## See Also

- `N5/prefs/principles/principles_index.yaml` — Complete index of all principles
- `N5/prefs/principles/*.yaml` — Individual principle files with full details