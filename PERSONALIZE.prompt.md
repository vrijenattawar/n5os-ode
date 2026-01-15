---
title: N5OS Ode Personalize
description: Configure N5OS Ode with your personal settings and preferences
version: 1.0.0
tool: true
tags: [n5os, setup, personalization, configuration]
created: 2026-01-15
---

# N5OS Ode Personalization

This prompt configures N5OS Ode with your personal settings. Run this after @BOOTLOADER.

I'll ask you a few questions to personalize your setup, then update the configuration files.

---

## Step 1: Basic Information

First, let me learn about you:

1. **What should I call you?** (name or nickname you prefer)

2. **What's your Zo handle?** (the part before .zo.computer)

3. **What's your timezone?** (e.g., America/New_York, Europe/London)

4. **What do you do?** (1-2 sentences about your work/role - this helps me tailor responses)

---

## Step 2: Connected Services

Which of these have you connected to Zo? (I'll check automatically, but confirm):

- [ ] Gmail
- [ ] Google Calendar
- [ ] Google Drive
- [ ] Notion
- [ ] Other: ___

---

## Step 3: Preferences

A few quick preferences:

1. **Communication style**: Do you prefer responses that are:
   - Concise and direct
   - Detailed and thorough
   - Balanced (default)

2. **Technical level**: How technical should explanations be?
   - Non-technical (analogies, plain language)
   - Somewhat technical (I know basics)
   - Very technical (developer-level detail)

3. **Proactivity**: Should I:
   - Wait for explicit instructions
   - Suggest improvements when I see them
   - Proactively organize and optimize (default)

---

## What Gets Updated

Based on your answers, I'll update:

### 1. Your Zo Bio
Updates your user bio in Settings so I remember who you are across conversations.

### 2. N5/prefs/prefs.md
Your local preferences file with:
- Name and handle
- Timezone
- Integration status
- Communication preferences

### 3. Custom Rules (if needed)
If you have specific requirements, I'll create rules for them:
- Company name spellings
- Preferred file locations
- Domain-specific terminology

### 4. Greeting Prompt (optional)
Customize what I say when you start a new conversation.

---

## After Personalization

Your N5OS Ode is configured! Here's what you can do:

### Test Your Setup

1. **Ask a strategic question** → Should route to Ode Strategist
2. **Request research** → Should route to Ode Researcher  
3. **Ask to build something** → Should route to Ode Builder

### Explore the System

- `N5/` — Core system files and configuration
- `Knowledge/` — Your knowledge base
- `Records/` — Meeting notes, project records
- `Prompts/` — Your prompt library

### Get Help

- Ask "How does N5OS work?" for an overview
- Ask "What can [Persona] do?" for persona capabilities
- Check `docs/` for reference documentation

---

## Re-Personalization

Run this prompt again anytime to update your settings. Changes take effect immediately for most settings, on next conversation for rules.

---

*N5OS Ode v1.0 — Personalized for you*

