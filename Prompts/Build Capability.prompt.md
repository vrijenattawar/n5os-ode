---
title: Build Capability
description: |
  Initialize a new build for a capability/feature/system. Creates workspace,
  develops a plan, then executes. Use when you want to build something new.
tags:
  - build
  - capability
  - planning
tool: true
---

# Build Capability

**Trigger:** User wants to build a new capability, feature, or system.

## Flow

1. **Parse the request** - Extract the capability name/slug from the message
2. **Initialize workspace:**
   ```bash
   python3 N5/scripts/init_build.py <slug> --title "<Capability Name>"
   ```
3. **Create plan** in `builds/<slug>/PLAN.md` following the planning template
4. **Review plan** — present for approval
5. **On approval:** Execute the build

## Slug Convention

Convert capability name to lowercase-hyphenated:
- "Calendar Sync" → `calendar-sync`
- "Email Intelligence System" → `email-intelligence-system`
- "Dashboard v2" → `dashboard-v2`

## Example

User says: "I want to build a meeting summarizer capability"

1. Slug: `meeting-summarizer`
2. Run: `python3 N5/scripts/init_build.py meeting-summarizer --title "Meeting Summarizer"`
3. Create plan in `builds/meeting-summarizer/PLAN.md`
4. Present for approval

## Reference

- **Scripts:** `file 'N5/scripts/init_build.py'` creates the build folder structure
- **Guide:** `file 'docs/PHILOSOPHY.md'` for build philosophy



