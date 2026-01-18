---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: worker_007_nuance_manifest
---

# Nuance Manifest

**The prompt engineering patterns that make N5OS work.**

---

## What Is This?

The Nuance Manifest is a collection of design patterns and anti-patterns for AI prompt/persona engineering. It's the "how to write good prompts" wisdom that makes N5OS Ode effective.

When you create or modify personas, prompts, or behavioral rules in N5OS, this document provides the patterns to follow. It's the difference between "an AI that kind of works" and "an AI that works reliably."

**Source:** Derived from Metaprompter v6.2  
**Version:** Universal Nuance Manifest v1.0  
**Location:** `N5/prefs/system/nuance-manifest.md`

---

## When to Consult

Use this document when:

- **Designing a new persona** — What behavioral patterns should it follow?
- **Writing a complex prompt** — How should it structure its responses?
- **Debugging AI behavior** — Why is it doing (not doing) X?
- **Evaluating prompt quality** — Is this prompt well-designed?

You don't need to memorize it — treat it as a reference library.

---

## How to Apply

### For Persona Design

When creating a persona (via Settings > Your AI > Personas):

1. **Read relevant sections** — Focus on patterns that match your persona's purpose
2. **Apply specific patterns** — Incorporate them into the persona's system prompt
3. **Validate against patterns** — Ask "Does this follow [PatternName]?"
4. **Explain trade-offs** — If patterns conflict, document why you chose one over another

**Example:** A "Strategist" persona should include:
- `OutcomeFirstAnchor` — Start with the end goal
- `HierarchicalSectioning` — Clear document structure
- `PlainEnglishBridge` — Explain complex concepts accessibly

### For Prompt Writing

When writing reusable prompts (in `Prompts/` or inline):

- Use `HierarchicalSectioning` for long prompts
- Include `BreakpointPrompting` for destructive operations
- Add `VisibleStateHeader` for multi-step workflows
- Apply `SchemaStrictMode` for structured outputs

### For Troubleshooting

If AI behavior is off:

1. **Identify the failure mode** — What's happening that shouldn't?
2. **Find the relevant anti-pattern** — What pattern is being violated?
3. **Add missing pattern** — Update the persona/prompt to include it
4. **Test and iterate** — Verify the fix

---

## Key Sections Overview

### Governance & Safety
**Patterns for reliability and control**

| Pattern | Purpose | Best For |
|---------|---------|----------|
| `VersionBumpGuard` | Prevent overwriting versioned artifacts without increment | Personas, prompts, configs |
| `RefusalSafetyHatch` | Allow model to refuse unsafe requests | All personas |
| `TaskReset` | Prevent context bleed between tasks | Multi-step workflows |

**Anti-pattern to avoid:** Guardrails that block legitimate safety refusals.

---

### Clarity & Structure
**Patterns for readable, scannable outputs**

| Pattern | Purpose | Best For |
|---------|---------|----------|
| `VisibleStateHeader` | Show progress/status at top | Long builds, multi-step tasks |
| `OutcomeFirstAnchor` | Start with goal, then path | Complex requests |
| `BreakpointPrompting` | Pause for user confirmation | Destructive operations |
| `HierarchicalSectioning` | Nested headers for structure | Long documents, prompts |

**Anti-pattern to avoid:** Walls of text without clear hierarchy.

---

### Inference & Intelligence
**Patterns for understanding and reasoning**

| Pattern | Purpose | Best For |
|---------|---------|----------|
| `AutoInferenceHelper` | Surface assumptions clearly | Ambiguous requests |
| `ConflictingSignalAlert` | Highlight contradictions | Requirement gathering |
| `InterrogativeLoop` | Ask clarifying questions | New builds, vague requests |
| `MetaAwareness` | Reflect on process, suggest improvements | Debugging, long conversations |

**Anti-pattern to avoid:** Proceeding without clarifying when context is missing.

---

### Quality & Validation
**Patterns for reliable, correct outputs**

| Pattern | Purpose | Best For |
|---------|---------|----------|
| `SchemaStrictMode` | Validate outputs against schemas | Structured data (JSON, YAML) |
| `ExampleAbundance` | Show concrete examples | Teaching, documentation |
| `ContradictionDetector` | Find internal inconsistencies | Analysis, strategic docs |
| `EdgeCaseTesting` | Stress-test at extremes | Workflows, system designs |

**Anti-pattern to avoid:** Delivering outputs without checking constraints.

---

### Execution & Efficiency
**Patterns for doing things well**

| Pattern | Purpose | Best For |
|---------|---------|----------|
| `ToolChaining` | Compose tools efficiently | Multi-step operations |
| `DryRunPreview` | Show what will happen first | Bulk operations, deletions |
| `MinimalFirst` | Start with simplest version | Rapid prototyping |
| `LazyLoading` | Only fetch what's needed | File operations, research |

**Anti-pattern to avoid:** Doing more work than necessary.

---

### Communication Style
**Patterns for clear, helpful interactions**

| Pattern | Purpose | Best For |
|---------|---------|----------|
| `PlainEnglishBridge` | Translate technical to accessible | Teaching, explanations |
| `ProgressiveDisclosure` | Layer complexity gradually | Long explanations |
| `ActionableDeliverables` | Include next steps | Analyses, strategic docs |
| `CitationDiscipline` | Reference sources properly | Web research, facts |

**Anti-pattern to avoid:** Technical jargon without context.

---

### Meta Patterns
**Patterns about patterns**

| Pattern | Purpose | Best For |
|---------|---------|----------|
| `NuanceAdvisor` | Suggest relevant nuances for tasks | Persona design |
| `SelfValidation` | Check own work before delivery | All significant outputs |

---

## Usage in Vibe Architect

The Vibe Architect persona (when active) is trained to:

1. **Reference specific nuances by name** when explaining design choices
2. **Suggest relevant nuances** for the domain/purpose you're building
3. **Validate against nuances** — e.g., "Does this persona have VisibleStateHeader?"
4. **Explain trade-offs** when patterns conflict

This makes the Architect an expert persona designer.

---

## Common Patterns in N5OS

Several N5OS components already follow these patterns:

**Persona System (`N5/prefs/system/persona_routing_contract.md`)**
- Uses `HierarchicalSectioning` for clear structure
- Applies `InterrogativeLoop` for routing decisions
- Includes `MetaAwareness` for self-correction

**Behavioral Rules (`N5/prefs/rules/`)**
- Apply `SchemaStrictMode` for structured outputs
- Use `BreakpointPrompting` for destructive operations
- Follow `TaskReset` between sessions

**Block System (`Prompts/Blocks/`)**
- Use `VisibleStateHeader` for progress tracking
- Apply `ExampleAbundance` for clarity
- Include `ActionableDeliverables` for next steps

---

## Learning the Patterns

You don't need to memorize every pattern. Start with these fundamentals:

### Essential Patterns (Start Here)
1. `VisibleStateHeader` — Show progress
2. `HierarchicalSectioning` — Structure clearly
3. `BreakpointPrompting` — Confirm before breaking
4. `InterrogativeLoop` — Ask when unclear
5. `SchemaStrictMode` — Validate outputs

### Advanced Patterns (Later)
- `AutoInferenceHelper` for better reasoning
- `ConflictingSignalAlert` for requirement clarity
- `NuanceAdvisor` for persona design
- `MetaAwareness` for self-improvement

---

## See Also

- [docs/PERSONAS.md](docs/PERSONAS.md) — Specialist personas in N5OS
- [docs/RULES.md](docs/RULES.md) — Behavioral rules system
- [docs/ROUTING.md](docs/ROUTING.md) — Persona choreography patterns
- [N5/prefs/system/nuance-manifest.md](../N5/prefs/system/nuance-manifest.md) — Full canonical reference

---

## Philosophy

> **"The quality of AI output is determined by the quality of the prompt. The Nuance Manifest codifies what makes a prompt good."**

Good prompts aren't about being verbose — they're about being precise, structured, and thoughtful. Each pattern in this document represents a lesson learned from real-world AI interactions.

When you apply these patterns consistently, you get AI that:
- **Communicates clearly** — No walls of text, no ambiguity
- **Thinks before acting** — Breakpoints, previews, clarifications
- **Validates its work** — Schema checks, edge case testing
- **Explains itself** — Progressive disclosure, plain English

This is the foundation of N5OS Ode's effectiveness.

---

*For the full technical reference, see [`N5/prefs/system/nuance-manifest.md`](../N5/prefs/system/nuance-manifest.md)*