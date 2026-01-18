---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: n5os-ode
---

# Persona Routing Guide

This guide explains how personas work together in N5OS Ode and how to get the most out of them.

---

## Home Base: Operator

Every conversation starts as **Operator**. Think of Operator as your home base — the coordinator that:

- **Navigates** your workspace and finds files
- **Runs** scripts, tools, and workflows
- **Routes** work to specialists when needed
- **Syncs** conversation state and progress

Operator is good at many things, but their strength is knowing **when to call in a specialist**.

---

## When to Route to Specialists

Use this semantic map as your guide. Route based on what you want to **accomplish**, not keywords.

### Researcher
**Route when**: You need information from outside your workspace

| Request Type | Example |
|--------------|---------|
| Web search | "Research the latest trends in AI assistants" |
| Documentation lookup | "Find how this API handles authentication" |
| Fact-finding | "What's the actual throughput limit?" |
| Synthesis | "Summarize these three sources and compare them" |

### Builder
**Route when**: You need something implemented or automated

| Request Type | Example |
|--------------|---------|
| Scripts | "Write a script to process these CSV files" |
| Integrations | "Connect this API to my workflow" |
| Tools | "Build a CLI tool for this task" |
| Implementation | "Turn this spec into working code" |

### Writer
**Route when**: You need polished, well-structured prose

| Request Type | Example |
|--------------|---------|
| Emails | "Draft a professional email to the client" |
| Documentation | "Write a README for this project" |
| Articles | "Turn these notes into a blog post" |
| Editing | "Polish this text for clarity" |

### Strategist
**Route when**: You need decisions, frameworks, or analysis

| Request Type | Example |
|--------------|---------|
| Decisions | "Which tech stack should I use for X?" |
| Frameworks | "Create a framework for evaluating vendors" |
| Planning | "How should I phase this migration?" |
| Pattern analysis | "What patterns do you see in these failures?" |

### Debugger
**Route when**: Something isn't working and you need to find out why

| Request Type | Example |
|--------------|---------|
| Bug finding | "Why is this script failing?" |
| QA | "Verify this implementation handles edge cases" |
| Root cause | "What's causing this performance issue?" |
| Testing | "Find the holes in this logic" |

---

## Return-to-Operator Rule

This is the golden rule of N5OS Ode:

> **Every specialist returns to Operator after their work is complete.**

This prevents "persona drift" where you stay in a specialist persona too long. After Builder finishes implementing something, they hand back to Operator. Operator then decides what's next.

**You don't need to request this** — it happens automatically. Specialists always return home with a summary.

---

## Routing Examples

### Good Routing

```
You: "I need to research pricing models for SaaS products."
Operator: "This is a research task. Routing to Researcher."
Researcher: [Completes research, returns to Operator]
Operator: "Research complete. Ready for next step."
```

### Bad Routing

```
You: "Move this file to Documents."
Operator: "This requires Builder's expertise." ← Unnecessary
```

Mechanical tasks like file moves are handled directly by Operator — no need to route.

### Specialist Chain

```
You: "I want to build a data pipeline, but I need to know the best tools first."
Operator: "Route to Researcher for tool evaluation."
Researcher: [Evaluates tools, returns]
Operator: "Route to Strategist for decision framework."
Strategist: [Provides analysis, returns]
Operator: "Route to Builder for implementation."
Builder: [Builds pipeline, returns]
Operator: "Pipeline complete. X/Y tasks done (100%)."
```

---

## Manual Persona Requests

You can explicitly request a persona:

- "Have Builder handle this implementation."
- "Switch to Strategist for this decision."
- "I want Writer's perspective on this draft."

Use this when you know which specialist you need, or when Operator's routing wasn't what you wanted.

---

## Tips for Effective Routing

1. **Describe the outcome, not the persona**
   - Better: "I need to understand how OAuth works"
   - Worse: "Go into Researcher mode and tell me about OAuth"

2. **Let Operator route automatically**
   - Operator is designed to detect when a specialist is needed. Trust the routing.

3. **One persona at a time**
   - Don't ask for "Builder AND Writer." Route to one, let them complete, then Operator will decide next.

4. **Be specific about outcomes**
   - "Write a draft email introducing our new product to enterprise customers"
   - Not just "Write an email"

5. **Ask for handoff when needed**
   - "Have Researcher find the sources, then Writer synthesize them into an article"

---

## Persona vs. AI Mode

N5OS Ode personas aren't "personalities" — they're **focused contexts**.

Think of them like specialized lenses:

| Aspect | Same | Different |
|--------|-------|-----------|
| AI capabilities | ✓ | |
| Knowledge base | ✓ | |
| Reasoning | ✓ | |
| **Loaded context** | | ✓ |
| **Output priorities** | | ✓ |
| **Routing awareness** | | ✓ |

The same underlying AI, but with different focus areas and standards for each type of work.

---

## Common Questions

**Q: Can I modify routing behavior?**
A: Yes. You can adjust persona prompts in Zo Settings to change how they route and respond.

**Q: What if Operator routes to the wrong specialist?**
A: Explicitly request the correct persona: "I actually need Debugger for this, not Researcher."

**Q: Do I need to know all the personas?**
A: No. Operator handles routing automatically. You just describe what you want to accomplish.

**Q: Can a specialist route to another specialist?**
A: Yes, but only for clear phase transitions (e.g., Builder → Strategist when an architecture decision is needed).

---

*See `docs/PERSONAS.md` for full persona descriptions.*