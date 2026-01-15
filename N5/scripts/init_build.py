#!/usr/bin/env python3
"""Initialize a build workspace for N5OS-Ode.

Usage:
    python3 N5/scripts/init_build.py <slug> --title "Build Title"
    
Creates:
    N5/builds/<slug>/
    ├── PLAN.md
    ├── STATUS.md
    └── artifacts/
"""
import argparse
from datetime import datetime
from pathlib import Path
import sys

# Script info
__version__ = "1.0.0"
REPO_URL = "https://github.com/vrijenattawar/n5os-ode"


def get_plan_template(title: str, date: str) -> str:
    """Generate PLAN.md content."""
    return f"""---
created: {date}
last_edited: {date}
version: 1
---
# {title}

## Objective

[Describe the build objective]

## Tasks

- [ ] Task 1
- [ ] Task 2

## Success Criteria

- [ ] Criterion 1
"""


def get_status_template(title: str, date: str) -> str:
    """Generate STATUS.md content."""
    return f"""---
created: {date}
last_edited: {date}
---
# {title} - Status

**Status:** In Progress  
**Started:** {date}

## Progress

| Task | Status | Notes |
|------|--------|-------|
| - | - | - |

## Blockers

None

## Next Steps

1. Define tasks in PLAN.md
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a build workspace for N5OS-Ode.",
        epilog=f"Repository: {REPO_URL}"
    )
    parser.add_argument(
        "slug",
        help="Build identifier (e.g., my-feature)"
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Build title (defaults to slug if not provided)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    args = parser.parse_args()
    
    # Default title to slug if not provided
    title = args.title if args.title else args.slug
    
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Determine script location to find N5/builds relative path
    script_path = Path(__file__).resolve()
    scripts_dir = script_path.parent  # N5/scripts
    n5_dir = scripts_dir.parent  # N5/
    builds_dir = n5_dir / "builds"
    
    # Create build directory path
    build_path = builds_dir / args.slug
    
    # Check if directory already exists
    if build_path.exists():
        print(f"⚠️  Warning: Build directory already exists: {build_path}", file=sys.stderr)
        print("   Use a different slug or remove the existing directory.", file=sys.stderr)
        return 1
    
    try:
        # Create directory structure
        build_path.mkdir(parents=True, exist_ok=True)
        (build_path / "artifacts").mkdir(exist_ok=True)
        
        # Create PLAN.md
        plan_content = get_plan_template(title, today)
        (build_path / "PLAN.md").write_text(plan_content)
        
        # Create STATUS.md
        status_content = get_status_template(title, today)
        (build_path / "STATUS.md").write_text(status_content)
        
        # Print confirmation
        print(f"✓ Build workspace created: {build_path}")
        print(f"  ├── PLAN.md")
        print(f"  ├── STATUS.md")
        print(f"  └── artifacts/")
        print(f"\nNext: Edit PLAN.md to define your build objective and tasks.")
        
        return 0
        
    except OSError as e:
        print(f"Error creating build workspace: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

