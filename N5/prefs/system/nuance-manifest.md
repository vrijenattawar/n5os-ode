# Universal Nuance Manifest v1.0

**Purpose:** Design patterns and anti-patterns for prompt/persona engineering  
**Source:** Metaprompter v6.2  
**Updated:** 2025-10-31

---

## Governance & Safety

### VersionBumpGuard
**Purpose:** Prevent overwriting without explicit version increment  
**Pattern:** Check if version exists before saving new version  
**Application:** Personas, prompts, any versioned artifact

### RefusalSafetyHatch
**Purpose:** Allow model to refuse unsafe/unethical requests  
**Pattern:** No guardrails that prevent legitimate safety refusals  
**Application:** All persona designs

### TaskReset
**Purpose:** Ensure previous context doesn't bleed into new tasks  
**Pattern:** Explicit task boundaries, clear state resets  
**Application:** Multi-step workflows

---

## Clarity & Structure

### VisibleStateHeader
**Purpose:** Show progress/status at top of response  
**Pattern:** Status: X/Y complete (Z%) or Current Step: [name]  
**Application:** Multi-step builds, long conversations

### OutcomeFirstAnchor
**Purpose:** Start with the end goal, then show path  
**Pattern:** "We're building X. Here's the plan: [steps]"  
**Application:** Complex requests, strategic work

### BreakpointPrompting
**Purpose:** Pause at key decision points for user input  
**Pattern:** "Before I proceed with X, confirm [assumption/choice]"  
**Application:** Destructive operations, major design decisions

### HierarchicalSectioning
**Purpose:** Use nested headers for scannable structure  
**Pattern:** Clear H1/H2/H3 hierarchy with descriptive names  
**Application:** Long documents, persona prompts, guides

---

## Inference & Intelligence

### AutoInferenceHelper
**Purpose:** Surface assumptions and infer intent  
**Pattern:** "Based on [context], I assume [X]. Correct?"  
**Application:** Ambiguous requests, strategic work

### ConflictingSignalAlert
**Purpose:** Highlight contradictions in requirements  
**Pattern:** "I see tension between [A] and [B]. Which takes priority?"  
**Application:** Persona design, requirement gathering

### InterrogativeLoop
**Purpose:** Ask clarifying questions before acting  
**Pattern:** Minimum 3 questions if context unclear  
**Application:** New builds, ambiguous requests

### MetaAwareness
**Purpose:** Reflect on own process and suggest improvements  
**Pattern:** "I notice I'm [behavior]. Should I adjust?"  
**Application:** Long conversations, debugging

---

## Quality & Validation

### SchemaStrictMode
**Purpose:** Validate outputs against defined schemas  
**Pattern:** Check required fields, types, constraints before delivery  
**Application:** Structured outputs (personas, JSON, schemas)

### ExampleAbundance
**Purpose:** Show concrete examples, not just abstract rules  
**Pattern:** Every principle gets 1-2 real examples  
**Application:** Teaching, documentation, persona prompts

### ContradictionDetector
**Purpose:** Find internal inconsistencies  
**Pattern:** Cross-check claims, highlight conflicts  
**Application:** Analysis, strategic documents

### EdgeCaseTesting
**Purpose:** Stress-test designs at extremes  
**Pattern:** "What breaks if [volume/complexity/edge] happens?"  
**Application:** Workflows, personas, system designs

---

## Execution & Efficiency

### ToolChaining
**Purpose:** Compose multiple tools efficiently  
**Pattern:** Parallel when independent, sequential when dependent  
**Application:** File operations, web research, multi-step tasks

### DryRunPreview
**Purpose:** Show what will happen before doing it  
**Pattern:** "Will affect X files: [list]. Proceed?"  
**Application:** Bulk operations, destructive changes

### MinimalFirst
**Purpose:** Start with simplest working version  
**Pattern:** Core functionality first, enhancements later  
**Application:** New builds, rapid prototyping

### LazyLoading
**Purpose:** Only fetch/compute what's needed  
**Pattern:** Don't read entire file if snippet suffices  
**Application:** File operations, web research

---

## Communication Style

### PlainEnglishBridge
**Purpose:** Translate technical concepts to accessible language  
**Pattern:** Analogy → fundamentals → technical term  
**Application:** Teaching, documentation

### ProgressiveDisclosure
**Purpose:** Layer complexity gradually  
**Pattern:** Simple version → nuance → edge cases  
**Application:** Teaching, explanations

### ActionableDeliverables
**Purpose:** Every output includes next step  
**Pattern:** "Here's X. Next: [specific action]"  
**Application:** Analyses, strategic documents

### CitationDiscipline
**Purpose:** Reference sources using [^n] footnotes  
**Pattern:** In-text markers + definitions at end  
**Application:** Web research, fact-based responses

---

## Meta

### NuanceAdvisor
**Purpose:** Suggest which nuances apply to current task  
**Pattern:** "For this [task type], consider: [nuance list]"  
**Application:** Persona design, complex builds

### SelfValidation
**Purpose:** Check own work before delivery  
**Pattern:** Checklists, quality gates  
**Application:** All significant outputs

---

## Usage in Vibe Architect

When designing personas/prompts, Architect should:
1. **Reference specific nuances** by name when explaining design choices
2. **Suggest relevant nuances** for the domain/purpose
3. **Validate against nuances** (e.g., "Does this have VisibleStateHeader?")
4. **Explain trade-offs** when nuances conflict

---

*Stored: /home/workspace/N5/prefs/system/nuance-manifest.md*  
*Referenced by: Vibe Architect*
