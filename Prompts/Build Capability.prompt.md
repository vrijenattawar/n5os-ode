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
3. **Activate Architect** (`set_active_persona("74e0a70d-398a-4337-bcab-3e5a3a9d805c")`)
4. **Architect creates plan** in `N5/builds/<slug>/PLAN.md` following template
5. **Invoke Level Upper** for counterintuitive review (experimental)
6. **Present plan** for approval
7. **On approval:** Hand off to Builder for execution

## Slug Convention

Convert capability name to lowercase-hyphenated:
- "Calendar Sync" → `calendar-sync`
- "Email Intelligence System" → `email-intelligence-system`
- "Dashboard v2" → `dashboard-v2`

## Example

User says: "I want to build a meeting summarizer capability"

1. Slug: `meeting-summarizer`
2. Run: `python3 N5/scripts/init_build.py meeting-summarizer --title "Meeting Summarizer"`
3. Activate Architect
4. Create plan in `N5/builds/meeting-summarizer/PLAN.md`
5. Present for approval

## Reference

- **Scripts:** `N5/scripts/init_build.py` creates the build folder structure
- **Templates:** `templates/build/` for plan and status templates
- **Guide:** `docs/BUILD_PLANNING.md` for full build planning system
- **Routing:** See persona routing contract in `N5/prefs/system/`



