---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
provenance: worker_006_documentation
---

# N5OS Ode

**A cognitive operating system for Zo Computer**

N5OS Ode transforms Zo from a general-purpose AI assistant into a structured thinking partner. It gives your AI memory, specialized modes of operation, and workflows that evolve with you.

---

## What Is This?

Think of N5OS Ode as firmware for your AI. Out of the box, Zo is a powerful but generic assistant. N5OS Ode adds:

- **Specialist Personas** — 6 focused modes (Builder, Researcher, Writer, Strategist, Debugger, Operator) that excel at different work types
- **Behavioral Rules** — Persistent instructions that shape AI behavior across all conversations
- **Conversation State** — Memory that persists across long sessions
- **Structured Outputs** — Block generators that transform transcripts into actionable intelligence
- **Journaling System** — Guided reflection workflows for personal insights
- **Safety Rails** — Protection mechanisms that prevent data loss

---

## Quick Start

### 1. Run the Bootloader

Open a new Zo conversation and invoke:

```
@BOOTLOADER.prompt.md
```

The bootloader will:
- Install 6 specialist personas
- Create 6 core behavioral rules  
- Set up the folder structure (N5/, Knowledge/, Records/, Prompts/)
- Initialize configuration files

Takes about 2-3 minutes.

### 2. Personalize

After installation, run:

```
@PERSONALIZE.prompt.md
```

This wizard collects:
- Your name and timezone
- Work context (what you do)
- Communication preferences

Your AI will adapt its behavior to match.

### 3. Start Using

You're ready. Some things to try:

**Journal Entry**
```
@Journal
```
Start a guided reflection session.

**Build Something**
```
@Build Capability
I want to create a script that backs up my files daily
```
Activates structured planning and execution.

**Use Personas**
```
Switch to Researcher and find recent papers on AI safety
```
Routes to the research specialist.

---

## Features Overview

### Specialist Personas

| Persona | Best For |
|---------|----------|
| **Operator** | Navigation, routing, state tracking (default) |
| **Builder** | Scripts, automations, implementations |
| **Researcher** | Web search, documentation, synthesis |
| **Writer** | Emails, docs, polished content |
| **Strategist** | Decisions, frameworks, planning |
| **Debugger** | Troubleshooting, QA, root cause analysis |

→ See [docs/PERSONAS.md](docs/PERSONAS.md) for full details

→ See [docs/ROUTING.md](docs/ROUTING.md) for persona choreography

### Behavioral Rules

6 core rules that shape AI behavior:

1. **Session State** — Tracks conversation context automatically
2. **Frontmatter** — Adds provenance to all markdown files
3. **P15 (Progress)** — Prevents false "done" claims
4. **File Protection** — Guards critical directories
5. **Debug Logging** — Breaks failure loops
6. **Clarifying Questions** — Reduces mistakes from ambiguity

→ See [docs/RULES.md](docs/RULES.md) for full details

### Principles Library

18 codified architectural principles that shape how N5OS thinks:

- **P15** — Complete Before Claiming (prevents false "done")
- **P28** — Plans as Code DNA (quality happens in planning)
- **P32** — Simple Over Easy (Rich Hickey's wisdom)
- **P23** — Identify Trap Doors (flag irreversible decisions)
- **P36** — Orchestration Pattern (multi-persona workflows)

Plus 13 more principles covering safety, modularity, error handling, and more.

→ See [docs/PRINCIPLES.md](docs/PRINCIPLES.md) for full details

### Block System

Transform meeting transcripts into structured intelligence:

- **B01** — Detailed recap
- **B02** — Commitments extracted
- **B03** — Decisions made
- **B04** — Open questions
- **B05** — Questions raised
- **B06** — Business context

Plus reflection blocks (R01, R02, R06) for journaling.

→ See [docs/BLOCK_SYSTEM.md](docs/BLOCK_SYSTEM.md) for full details

### Semantic Memory (Optional)

If you have an OpenAI API key, N5OS Ode can build a semantic memory layer:

- Auto-indexes Knowledge/ content
- Enables similarity search across your notes
- Provides context-aware retrieval

→ See [docs/SEMANTIC_MEMORY.md](docs/SEMANTIC_MEMORY.md) for setup

### Conversation End System

Tiered conversation hygiene based on conversation complexity:

- **Tier 1 (Quick)** — Simple Q&A, no commits needed
- **Tier 2 (Standard)** — Research/discussion with artifacts
- **Tier 3 (Full Build)** — Major changes, full documentation

Supports Worker vs Full mode for orchestrated multi-conversation builds.

→ See [docs/CONVERSATION_END.md](docs/CONVERSATION_END.md) for details

### Context Loading

Dynamic context injection by task category:

- `build` — Coding, implementations
- `strategy` — Planning, decisions
- `research` — Deep analysis, synthesis
- `safety` — Destructive operations
- Plus `system`, `scheduler`, `writer`, `health`

→ See [docs/CONTEXT_LOADING.md](docs/CONTEXT_LOADING.md) for details

---

## Requirements

- **Zo Computer account** — [zo.computer](https://zo.computer)
- **Fresh workspace** — Works best on new or clean workspaces
- **OpenAI API key** — Optional, for semantic memory features

---

## File Structure

After installation:

```
workspace/
├── N5/                      # System intelligence
│   ├── prefs/               # Preferences and config
│   ├── scripts/             # Utility scripts
│   └── cognition/           # Semantic memory (optional)
├── Knowledge/               # Long-term reference
│   └── content-library/     # Ingested articles and notes
├── Records/                 # Date-organized records
│   └── journal/             # Journal entries
├── Prompts/                 # Reusable workflows
│   ├── Blocks/              # Block generators
│   └── reflections/         # Reflection templates
├── BOOTLOADER.prompt.md     # Installation script
└── PERSONALIZE.prompt.md    # Configuration wizard
```

→ See [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) for details

---

## Philosophy

N5OS Ode is built on these beliefs:

1. **Structure Enables Creativity** — Frameworks free you to focus on what matters
2. **Specialists Beat Generalists** — Focused context produces better results
3. **Memory Makes Intelligence** — Without continuity, each conversation starts from zero
4. **Safety First** — Better to ask than accidentally destroy
5. **Progressive Enhancement** — Start simple, add complexity as needed

→ See [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) for the full story

---

## Documentation

| Doc | Description |
|-----|-------------|
| [PHILOSOPHY.md](docs/PHILOSOPHY.md) | Why N5OS exists, core concepts |
| [PERSONAS.md](docs/PERSONAS.md) | Specialist personas, routing |
| [ROUTING.md](docs/ROUTING.md) | Persona choreography, handoffs |
| [RULES.md](docs/RULES.md) | Behavioral rules, customization |
| [PRINCIPLES.md](docs/PRINCIPLES.md) | 18 architectural principles |
| [FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) | Directory layout, conventions |
| [BLOCK_SYSTEM.md](docs/BLOCK_SYSTEM.md) | Block generators for transcripts |
| [SEMANTIC_MEMORY.md](docs/SEMANTIC_MEMORY.md) | Optional memory layer setup |
| [CONVERSATION_END.md](docs/CONVERSATION_END.md) | Tiered conversation close |
| [CONTEXT_LOADING.md](docs/CONTEXT_LOADING.md) | Dynamic context injection |

---

## Customization

N5OS Ode is a starting point, not a cage:

- **Add personas** — Create specialists for your domains
- **Modify rules** — Adapt to your preferences
- **Create prompts** — Build workflows for recurring tasks
- **Extend blocks** — Generate custom intelligence from transcripts

Everything can be edited in Zo Settings or the workspace.

---

## Getting Help

**Something not working?**
Check if the persona/rule is installed: Settings > Your AI

**Want to modify behavior?**
Edit personas and rules in Settings, or modify the prompts directly

**Need to start over?**
Re-run @BOOTLOADER — it's idempotent (safe to run multiple times)

---

## Acknowledgments

The semantic memory architecture in N5OS Ode is based on foundational work by **[The Fork Project](https://github.com/theforkproject-dev)**. Their [zo-local-memory](https://github.com/theforkproject-dev/zo-local-memory) project established the core patterns for local semantic memory on Zo Computer, including the embedding pipeline, vector storage structure, and retrieval approach.

We gratefully acknowledge their contribution to the Zo ecosystem.

---

## Version

**N5OS Ode v1.0**  
Released: January 2026

---

*Structured thinking for structured doing.*

