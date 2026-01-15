#!/usr/bin/env python3
"""
Initialize a new build capability.

Usage:
  python3 scripts/init_build.py <slug> --title "Capability Name"

Example:
  python3 scripts/init_build.py meeting-summarizer --title "Meeting Summarizer"
"""
import sys
from pathlib import Path
from datetime import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description="Initialize a new build capability")
    parser.add_argument("slug", help="Lowercase-hyphenated slug (e.g., meeting-summarizer)")
    parser.add_argument("--title", required=True, help="Human-readable capability name")
    args = parser.parse_args()
    
    root = Path(__file__).parent.parent
    build_dir = root / "builds" / args.slug
    
    if build_dir.exists():
        print(f"ERROR: Build '{args.slug}' already exists at {build_dir}", file=sys.stderr)
        sys.exit(1)
    
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create PLAN.md
    plan_file = build_dir / "PLAN.md"
    plan_content = f"""---
created: {datetime.now().isoformat()}
last_edited: {datetime.now().isoformat()}
version: 1.0
provenance: n5os-ode-init
---

# Build Plan: {args.title}

**Slug:** `{args.slug}`

## Overview

[Describe the capability at a high level]

## Objectives

- [ ] [Objective 1]
- [ ] [Objective 2]
- [ ] [Objective 3]

## Architecture

[Describe design, components, dependencies]

## Implementation Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Testing Strategy

[Describe testing approach]

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Timeline

[Estimate time/effort]

## Open Questions

- [Question 1?]
- [Question 2?]
"""
    plan_file.write_text(plan_content)
    
    # Create output directory
    output_dir = build_dir / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / ".gitkeep").touch()
    
    print(f"✅ Build initialized: {build_dir}")
    print(f"   Plan: {plan_file}")
    print(f"   Output: {output_dir}")
    print()
    print("Next: Review PLAN.md and when ready, execute the build.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

