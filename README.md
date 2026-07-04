---
created: 2026-01-15
last_edited: 2026-06-11
version: 2.2
provenance: n5os-ode-v2
---

# N5OS Ode

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/thevibethinker/n5os-ode)

**A cognitive operating system for Zo Computer**

N5OS Ode transforms Zo from a general-purpose AI assistant into a structured thinking partner. It gives your AI memory, specialized modes of operation, and workflows that evolve with you.

---

## What Is This?

Think of N5OS Ode as firmware for your AI. Out of the box, Zo is a powerful but generic assistant. N5OS Ode adds:

- **Specialist Personas** — 11 focused modes (Operator, Builder, Researcher, Writer, Strategist, Debugger, Architect, Teacher, Designer, Illustrator, Level Upper) stored as a git-tracked SSOT in `N5/personas/`
- **Behavioral Rules** — 13 persistent instructions that shape AI behavior across all conversations
- **Conversation State** — Memory that persists across long sessions
- **Structured Outputs** — S-shape meeting artifacts that transform transcripts into reusable intelligence
- **Pulse Build Orchestration** — Scenario-driven planning, contract checks, worker Drops, and build finalization
- **Safety Rails** — Protection mechanisms that prevent data loss

---

## Quick Start

### 1. Install to Workspace Root

> ⚠️ **IMPORTANT:** N5OS Ode files must live at your workspace ROOT, not inside a subfolder.
> The `Prompts/`, `N5/`, `Knowledge/` folders should be directly in `./`, NOT in `./n5os-ode/`.

**One command does everything:**

```bash
git clone https://github.com/thevibethinker/n5os-ode.git && cd n5os-ode && bash install.sh
```

This clones the repo, moves all contents to your workspace root, and cleans up the `n5os-ode/` folder.

**Verify it worked:** You should see `Prompts/`, `N5/`, `BOOTLOADER.prompt.md` etc. directly in your workspace root — NOT inside an `n5os-ode/` folder.

### Existing Users: Update Path

If you already installed N5OS Ode from an older package, update from the public repo instead of reinstalling destructively:

```bash
tmp="$(mktemp -d)"
git clone https://github.com/thevibethinker/n5os-ode.git "$tmp/n5os-ode"
WORKSPACE_ROOT="$PWD" bash "$tmp/n5os-ode/install.sh" --update
python3 N5/scripts/validate_repo.py
```

Then open a new Zo conversation and re-run:

```
@BOOTLOADER.prompt.md
```

The update path refreshes root prompt/docs and merges missing packaged files without intentionally overwriting your personal state in `N5/`, `Knowledge/`, `Prompts/`, `Skills/`, or `Personal/`. After updating, verify `Knowledge/architectural/building_fundamentals.md` exists and review persona tool scopes in Settings > AI > Personas if your Zo account exposes scope metadata.

### 2. Run the Bootloader

Open a new Zo conversation and type:

```
@BOOTLOADER.prompt.md
```

The bootloader will:
- Install 11 specialist personas
- Create 13 behavioral rules  
- Set up the folder structure (N5/, Knowledge/, Records/, Prompts/)
- Initialize configuration files

Takes about 2-3 minutes.

### 3. Personalize

After installation, run:

```
@PERSONALIZE.prompt.md
```

This wizard collects:
- Your name and timezone
- Work context (what you do)
- Communication preferences

Your AI will adapt its behavior to match.

### 4. Start Using

You're ready. Some things to try:

**Build Something**
```
I want to build a script that backs up my files daily.
```
Activates the Pulse workflow: scenario extraction, Architect planning, contract validation, execution, and finalization.

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
| **Architect** | System design, build planning, technical specs |
| **Teacher** | Learning, conceptual understanding, skill building |
| **Designer** | Frontend, UI/UX, page composition, design polish |
| **Illustrator** | Image generation, editing, generative art, multimodal vision |
| **Level Upper** | Counterintuitive review for major or risky work |

→ See [docs/PERSONAS.md](docs/PERSONAS.md) for full details

→ See [docs/ROUTING.md](docs/ROUTING.md) for persona choreography

Persona prompts are managed as code:

```bash
python3 N5/scripts/persona_sync.py check
python3 N5/scripts/persona_sync.py --self-test
```

The packaged `N5/personas/registry.json` uses `PERSONA_ID_*` placeholders until installation creates live Zo personas.

### Behavioral Rules

13 core rules that shape AI behavior:

1. **Session State** — Tracks conversation context automatically
2. **Frontmatter** — Adds provenance to all markdown files
3. **P15 (Progress)** — Prevents false "done" claims
4. **File Protection** — Guards critical directories
5. **Debug Logging** — Breaks failure loops
6. **Clarifying Questions** — Reduces mistakes from ambiguity
7. **Persona Routing** — Master routing table for specialist handoffs
8. **Session State Updates** — Periodic state sync during work
9. **Honest Workflow Reporting** — Quantitative progress tracking
10. **Agent Conflict Gate** — Prevents agent sprawl
11. **Pulse Orchestration** — Build orchestration discipline
12. **Anti-Hallucination** — Penalizes fabrication over admitting uncertainty
13. **Debug Logging Discipline** — Structured debug logging during problem-solving

→ See [docs/RULES.md](docs/RULES.md) for full details

### Principles Library

37 codified architectural principles that shape how N5OS thinks:

- **P15** — Complete Before Claiming (prevents false "done")
- **P28** — Plans as Code DNA (quality happens in planning)
- **P32** — Simple Over Easy (Rich Hickey's wisdom)
- **P23** — Identify Trap Doors (flag irreversible decisions)
- **P36** — Orchestration Pattern (multi-persona workflows)

Plus 13 more principles covering safety, modularity, error handling, and more.

→ See [docs/PRINCIPLES.md](docs/PRINCIPLES.md) for full details

### Meeting Shapes

Transform meeting transcripts into canonical structured artifacts:

- **S01** — Meeting metadata and participants
- **S02** — Decisions, commitments, and next actions
- **S03** — Strategic implications and unresolved questions
- **S04** — Stakeholder and relationship intelligence
- **S05** — Durable ideas, frameworks, and market insights
- **S06** — Narrative recap for human review

→ See [Skills/meeting-ingestion/SKILL.md](Skills/meeting-ingestion/SKILL.md) for current meeting-ingestion details


### Skills

N5OS ships a self-contained skill suite. Skills fall into three practical groups:

1. **Executable workflow skills** — include scripts/tests and can run locally after install.
2. **Instruction skills** — reusable playbooks that guide the agent without requiring code.
3. **Compatibility shims** — small alias packages that keep legacy prompt references resolvable while pointing to the canonical skill.

Core executable workflows:

| Skill | Description |
| --- | --- |
| **meeting-ingestion** | Pull transcripts from Google Drive, generate intelligence blocks, and track processing state |
| **pulse** | Build orchestration: planning, contract checks, worker Drops, snapshots, validation, learning capture |
| **codebase-graph** | Static dependency graph for blast-radius review across N5, Skills, Prompts, and integrations |
| **sentience-sync** | Source-only Sentience API sync package with PII scrubbing, idempotency, local state, and tests |
| **close / thread-close / build-close / drop-close** | Conversation, worker, build, and drop close workflows |
| **visual-design-review** | Multi-viewport screenshot and DOM telemetry capture for UI review |
| **recommend-skill-chain** | Recommends ordered design-skill chains from a visual spec |
| **pulse-visual-elevation** | Orchestrates visual elevation passes around design-skill chains and review checkpoints |

Design and generation skills:

| Skill | Description |
| --- | --- |
| **frontend-design** | Production-grade UI patterns with anti-slop guardrails |
| **teach-impeccable** | Captures project design context before frontend/design work |
| **arrange, bolder, distill, delight, colorize, animate, adapt, polish, critique** | Atomic visual transformation and review playbooks |
| **remotion** | Specialized video-generation workflow |
| **spec-writing / pulse-interview** | Scenario extraction and pre-build decomposition used inside Pulse planning |
| **systematic-debugging** | Root cause analysis methodology with structured phases |
| **debono-thinking-hats** | Multi-lens thinking workflow |

Compatibility shims included intentionally:

| Shim | Canonical replacement |
| --- | --- |
| **frontend-visual-director** | `Skills/frontend-design/`, `Skills/teach-impeccable/`, `Skills/visual-design-review/`, `Skills/pulse-visual-elevation/` |

**Meeting Ingestion Quick Start:**
```bash
# Check status
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status

# Pull new transcripts
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --dry-run

# Process meetings
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process
```

**Pulse Quick Start:**
```bash
# Initialize and validate a build
python3 N5/scripts/init_build.py my-build
python3 N5/scripts/build_contract_check.py my-build
python3 Skills/pulse/scripts/pulse.py validate my-build
python3 Skills/pulse/scripts/pulse.py grill my-build

# Start build
python3 Skills/pulse/scripts/pulse.py start my-build

# Check status
python3 Skills/pulse/scripts/pulse.py status my-build
```

→ See [Skills/meeting-ingestion/SKILL.md](Skills/meeting-ingestion/SKILL.md) and [Skills/pulse/SKILL.md](Skills/pulse/SKILL.md) for full documentation
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
Use `@Close Conversation` when you are ending a meaningful thread, packaging a worker handoff, or finalizing an orchestrated build.

→ See [docs/CONVERSATION_END.md](docs/CONVERSATION_END.md) for details

### Context Loading

Dynamic context injection by task category:

- `build` — Coding, implementations
- `strategy` — Planning, decisions
- `research` — Deep analysis, synthesis
- `safety` — Destructive operations
- Plus `system`, `scheduler`, `writer`, `health`

→ See [docs/CONTEXT_LOADING.md](docs/CONTEXT_LOADING.md) for details

### Safety System

Comprehensive protection layer preventing catastrophic file operations:

- **.n5protected markers** — Directory-level protection against moves/deletes
- **Folder-specific POLICY.md** — Override global preferences at folder level
- **Protected paths and file types** — Auto-review for databases, secrets, system files
- **PII tracking** — Mark directories containing personally identifiable information
- **Blast radius control** — Logged, reversible operations with audit trails

→ See [docs/SAFETY.md](docs/SAFETY.md) for protection mechanisms and usage

### Sites Protocol

Structured deployment workflow for web applications:

- Staging vs production separation
- Service naming and port conventions
- Promotion workflow (staging → prod)
- Site protection rules

→ See [docs/SITES.md](docs/SITES.md) for deployment patterns

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
│   ├── personas/            # Git-tracked persona prompt SSOT
│   ├── scripts/             # Utility scripts
│   └── cognition/           # Semantic memory (optional)
├── Knowledge/               # Long-term reference
│   └── content-library/     # Ingested articles and notes
├── Records/                 # Date-organized records
│   └── meetings/            # Meeting records and dated operational notes
├── Prompts/                 # Reusable workflows
│   └── Blocks/              # Reflection prompts and non-B legacy prompt shells
├── Skills/                  # Packaged workflows
│   ├── codebase-graph/      # Dependency graph and blast-radius review
│   ├── frontend-design/     # Flagship frontend/design guidance
│   ├── meeting-ingestion/   # Meeting transcript processing
│   ├── pulse/               # Build orchestration
│   ├── sentience-sync/      # Sentience API sync package
│   └── ...                  # Additional generation, design, close, and compatibility skills
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
| [NUANCE_MANIFEST.md](docs/NUANCE_MANIFEST.md) | Prompt engineering patterns for AI quality |
| [PERSONAS.md](docs/PERSONAS.md) | Specialist personas, routing |
| [ROUTING.md](docs/ROUTING.md) | Persona choreography, handoffs |
| [RULES.md](docs/RULES.md) | Behavioral rules, customization |
| [PRINCIPLES.md](docs/PRINCIPLES.md) | 37 architectural principles |
| [FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) | Directory layout, conventions |
| [meeting-ingestion/SKILL.md](Skills/meeting-ingestion/SKILL.md) | Canonical meeting-ingestion pipeline and S-shape artifacts |
| [BUILD_PLANNING.md](docs/BUILD_PLANNING.md) | Build planning system, templates, and execution flow |
| [SEMANTIC_MEMORY.md](docs/SEMANTIC_MEMORY.md) | Optional memory layer setup |
| [CONVERSATION_END.md](docs/CONVERSATION_END.md) | Tiered conversation close |
| [CONTEXT_LOADING.md](docs/CONTEXT_LOADING.md) | Dynamic context injection |
| [DEBUG_SYSTEM.md](docs/DEBUG_SYSTEM.md) | Debug logging, pattern detection, troubleshooting reflexes |
| [SAFETY.md](docs/SAFETY.md) | Protection mechanisms and usage |
| [SITES.md](docs/SITES.md) | Sites protocol, staging/prod patterns, service conventions |

---

## Customization

N5OS Ode is a starting point, not a cage:

- **Add personas** — Create specialists for your domains
- **Modify rules** — Adapt to your preferences
- **Create prompts** — Build workflows for recurring tasks
- **Extend meeting shapes** — Generate custom structured intelligence from transcripts

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

**N5OS Ode v2.2**
Released: June 2026

---

*Structured thinking for structured doing.*
