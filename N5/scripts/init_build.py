#!/usr/bin/env python3
"""
init_build.py - Initialize a new build workspace with v2 orchestration support.

Usage:
    python3 N5/scripts/init_build.py <slug> [options]

Examples:
    python3 N5/scripts/init_build.py my-feature --title "My Feature Build"
    python3 N5/scripts/init_build.py calendar-v2 --title "Calendar V2" --type code_build --workers 5

Creates:
    N5/builds/<slug>/
    ├── BUILD.md          (orchestrator document)
    ├── PLAN.md           (architect's plan)
    ├── STATUS.md         (progress tracking)
    ├── meta.json         (machine-readable state)
    ├── workers/          (worker briefs folder)
    ├── completions/      (worker completion reports)
    └── .n5protected      (prevents accidental deletion)

The build is FOR AI execution. Architect fills the plan; workers execute it.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
TEMPLATES_DIR = WORKSPACE / "N5" / "templates" / "build"

# Valid build types (from meta_schema.json)
VALID_TYPES = ["code_build", "content", "research", "general"]

# Schema version for meta.json
META_SCHEMA_VERSION = "1.0"


def validate_slug(slug: str) -> bool:
    """Validate slug: lowercase, hyphens, no spaces, no special chars."""
    pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def get_incomplete_builds() -> list[dict]:
    """
    Scan for incomplete builds (status != 'complete' and != 'abandoned').
    
    Returns:
        List of dicts with slug, title, status, workers info
    """
    incomplete = []
    
    if not BUILDS_DIR.exists():
        return incomplete
    
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue
            
        meta_file = build_dir / "meta.json"
        if not meta_file.exists():
            # Old-style build without meta.json - check STATUS.md
            status_file = build_dir / "STATUS.md"
            if status_file.exists():
                # Assume old builds without meta.json are potentially incomplete
                incomplete.append({
                    "slug": build_dir.name,
                    "title": build_dir.name.replace("-", " ").title(),
                    "status": "unknown (no meta.json)",
                    "workers_complete": None,
                    "workers_total": None,
                    "created": None
                })
            continue
        
        try:
            with open(meta_file) as f:
                meta = json.load(f)
            
            status = meta.get("status", "unknown")
            if status not in ("complete", "abandoned"):
                workers = meta.get("workers", {})
                incomplete.append({
                    "slug": build_dir.name,
                    "title": meta.get("title", build_dir.name),
                    "status": status,
                    "workers_complete": workers.get("complete", 0),
                    "workers_total": workers.get("total", 0),
                    "created": meta.get("created")
                })
        except (json.JSONDecodeError, IOError):
            # Malformed meta.json - treat as potentially incomplete
            incomplete.append({
                "slug": build_dir.name,
                "title": build_dir.name.replace("-", " ").title(),
                "status": "unknown (invalid meta.json)",
                "workers_complete": None,
                "workers_total": None,
                "created": None
            })
    
    return incomplete


def prescreen_builds(slug: str, title: str, skip: bool = False, strict: bool = False) -> bool:
    """
    Check for incomplete builds and warn user.
    
    Args:
        slug: The new build slug
        title: The new build title
        skip: Skip the pre-screen entirely
        strict: Fail instead of warning in non-interactive mode
        
    Returns:
        True if should proceed, False if should abort
    """
    if skip:
        return True
    
    incomplete = get_incomplete_builds()
    
    if not incomplete:
        return True
    
    # Filter for similar slugs or titles (fuzzy match)
    similar = []
    slug_words = set(slug.lower().replace("-", " ").split())
    title_words = set(title.lower().split()) if title else set()
    
    for build in incomplete:
        build_slug_words = set(build["slug"].lower().replace("-", " ").split())
        build_title_words = set(build["title"].lower().split()) if build["title"] else set()
        
        # Check for word overlap
        if (slug_words & build_slug_words) or (title_words & build_title_words):
            similar.append(build)
    
    # Show warning
    print(f"\n⚠️  Found {len(incomplete)} incomplete build(s):")
    
    for build in incomplete:
        workers_str = ""
        if build["workers_total"] is not None and build["workers_complete"] is not None:
            workers_str = f" ({build['workers_complete']}/{build['workers_total']} workers complete)"
        elif build["created"]:
            workers_str = f" (active since {build['created']})"
        
        marker = " ← similar" if build in similar else ""
        print(f"   - {build['slug']}: {build['status']}{workers_str}{marker}")
    
    print()
    
    if strict:
        print("❌ Strict mode: aborting due to incomplete builds.")
        print("   Use --skip-prescreen to bypass this check.")
        return False
    
    # Check if running interactively
    if sys.stdin.isatty():
        try:
            response = input("Continue anyway? [y/N] ").strip().lower()
            return response in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            print()
            return False
    else:
        # Non-interactive: warn but continue
        print("   (Non-interactive mode: proceeding anyway)")
        return True


def create_meta_json(slug: str, title: str, build_type: str, today: str) -> dict:
    """
    Create initial meta.json content.
    
    Args:
        slug: Build slug
        title: Build title
        build_type: One of VALID_TYPES
        today: ISO date string (YYYY-MM-DD)
        
    Returns:
        Dict representing meta.json content
    """
    return {
        "schema_version": META_SCHEMA_VERSION,
        "slug": slug,
        "title": title,
        "objective": None,
        "created": today,
        "status": "draft",
        "completed_at": None,
        "type": build_type,
        "orchestrator_convo_id": None,
        "workers": {
            "total": 0,
            "complete": 0,
            "in_progress": 0,
            "blocked": 0,
            "pending": 0
        },
        "waves": [],
        "worker_details": []
    }


def generate_worker_stubs(build_dir: Path, slug: str, num_workers: int) -> list[Path]:
    """
    Generate worker brief stub files.
    
    Args:
        build_dir: Path to build directory
        slug: Build slug
        num_workers: Number of worker stubs to generate
        
    Returns:
        List of created file paths
    """
    workers_dir = build_dir / "workers"
    template_file = TEMPLATES_DIR / "worker_brief_template.md"
    
    if template_file.exists():
        template_content = template_file.read_text()
    else:
        # Minimal fallback template
        template_content = """---
worker_id: W{{WAVE}}.{{SEQ}}
title: "[{{SLUG}}] W{{WAVE}}.{{SEQ}}: {{TASK_NAME}}"
build_slug: {{SLUG}}
wave: {{WAVE}}
depends_on: []
thread_title: "[{{SLUG}}] W{{WAVE}}.{{SEQ}}: {{TASK_NAME}}"
---

# Worker Brief: {{TASK_NAME}}

**Your Mission:** [TO BE FILLED]

**Output(s):**
- `{{OUTPUT_PATH}}` (CREATE/UPDATE)

---

## Context

[TO BE FILLED]

---

## Success Criteria

- [ ] [TO BE FILLED]

---

## Report Back

**DO NOT COMMIT.** Write completion to `N5/builds/{{SLUG}}/completions/W{{WAVE}}.{{SEQ}}.json`
"""
    
    created_files = []
    
    # Generate stubs in wave 1 by default
    for seq in range(1, num_workers + 1):
        worker_id = f"W1.{seq}"
        task_name = f"Task {seq}"
        filename = f"W1.{seq}-task-{seq}.md"
        
        content = template_content
        content = content.replace("{{SLUG}}", slug)
        content = content.replace("{{WAVE}}", "1")
        content = content.replace("{{SEQ}}", str(seq))
        content = content.replace("{{TASK_NAME}}", task_name)
        content = content.replace("{{ONE_SENTENCE_MISSION}}", "[TO BE FILLED]")
        content = content.replace("{{OUTPUT_PATH_1}}", "[TO BE FILLED]")
        content = content.replace("{{OUTPUT_PATH_2}}", "[TO BE FILLED]")
        content = content.replace("{{CONTEXT_DESCRIPTION}}", "[TO BE FILLED]")
        content = content.replace("{{REQUIREMENT_SECTION_1}}", "Requirement 1")
        content = content.replace("{{REQUIREMENT_SECTION_2}}", "Requirement 2")
        content = content.replace("{{REQUIREMENT_DETAILS}}", "[TO BE FILLED]")
        content = content.replace("{{CRITERION_1}}", "[TO BE FILLED]")
        content = content.replace("{{CRITERION_2}}", "[TO BE FILLED]")
        content = content.replace("{{CRITERION_3}}", "[TO BE FILLED]")
        content = content.replace("{{CRITERION_4}}", "[TO BE FILLED]")
        content = content.replace("{{ISO_TIMESTAMP}}", "[COMPLETION TIMESTAMP]")
        
        worker_file = workers_dir / filename
        worker_file.write_text(content)
        created_files.append(worker_file)
    
    return created_files


def init_build(
    slug: str,
    title: str | None = None,
    build_type: str = "general",
    num_workers: int = 0,
    force: bool = False,
    skip_prescreen: bool = False,
    strict: bool = False
) -> Path:
    """
    Initialize a new build workspace with v2 structure.
    
    Args:
        slug: Build identifier (lowercase-hyphenated)
        title: Optional human-readable title
        build_type: Build type (code_build, content, research, general)
        num_workers: Number of worker stub files to generate (0 = none)
        force: Overwrite existing build
        skip_prescreen: Skip incomplete builds check
        strict: Fail if incomplete builds found
        
    Returns:
        Path to the created build directory
    """
    # Validate slug
    if not validate_slug(slug):
        print(f"❌ Invalid slug: '{slug}'")
        print("   Slug must be lowercase with hyphens (e.g., 'my-new-feature')")
        sys.exit(1)
    
    # Validate build type
    if build_type not in VALID_TYPES:
        print(f"❌ Invalid type: '{build_type}'")
        print(f"   Valid types: {', '.join(VALID_TYPES)}")
        sys.exit(1)
    
    # Check if build already exists
    build_dir = BUILDS_DIR / slug
    if build_dir.exists():
        if force:
            print(f"⚠️  Overwriting existing build: {build_dir}")
            import shutil
            shutil.rmtree(build_dir)
        else:
            print(f"❌ Build already exists: {build_dir}")
            print("   Use --force to overwrite, or choose a different slug.")
            sys.exit(1)
    
    # Title defaults to slug titlecased
    if title is None:
        title = slug.replace("-", " ").title()
    
    # Pre-screen for incomplete builds
    if not prescreen_builds(slug, title, skip_prescreen, strict):
        sys.exit(1)
    
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create build directory structure
    build_dir.mkdir(parents=True, exist_ok=True)
    workers_dir = build_dir / "workers"
    workers_dir.mkdir(exist_ok=True)
    completions_dir = build_dir / "completions"
    completions_dir.mkdir(exist_ok=True)
    
    # Create meta.json
    meta_content = create_meta_json(slug, title, build_type, today)
    if num_workers > 0:
        # Pre-populate worker stats if generating stubs
        meta_content["workers"]["total"] = num_workers
        meta_content["workers"]["pending"] = num_workers
        meta_content["waves"] = [{
            "wave": 1,
            "workers": [f"W1.{i}" for i in range(1, num_workers + 1)],
            "status": "pending"
        }]
        meta_content["worker_details"] = [
            {
                "id": f"W1.{i}",
                "title": f"Task {i}",
                "status": "pending",
                "thread_id": None,
                "completed_at": None,
                "depends_on": []
            }
            for i in range(1, num_workers + 1)
        ]
    
    meta_file = build_dir / "meta.json"
    with open(meta_file, "w") as f:
        json.dump(meta_content, f, indent=2)
    
    # Read and populate BUILD template
    build_template = TEMPLATES_DIR / "BUILD_template.md"
    if build_template.exists():
        build_content = build_template.read_text()
        build_content = build_content.replace("{{DATE}}", today)
        build_content = build_content.replace("{{TITLE}}", title)
        build_content = build_content.replace("{{SLUG}}", slug)
        build_content = build_content.replace("{{TYPE}}", build_type)
        build_content = build_content.replace("{{OBJECTIVE}}", "[TO BE FILLED BY ARCHITECT]")
        build_content = build_content.replace("{{CONVO_ID}}", "[ORCHESTRATOR CONVERSATION ID]")
        build_content = build_content.replace("{{CURRENT_PHASE}}", "Planning")
        build_content = build_content.replace("{{LAST_UPDATE}}", today)
        build_content = build_content.replace("{{STATUS_SUMMARY}}", "Build initialized. Awaiting Architect plan.")
        build_content = build_content.replace("{{WAVE_1_NOTES}}", "Awaiting plan")
        # Clear placeholder worker rows for now
        build_content = build_content.replace("{{W1.1_TITLE}}", "[TBD]")
        build_content = build_content.replace("{{W1.2_TITLE}}", "[TBD]")
        build_content = build_content.replace("{{W2.1_TITLE}}", "[TBD]")
    else:
        # Minimal fallback if template missing
        build_content = f"""---
created: {today}
last_edited: {today}
version: 1.0
type: build_orchestrator
status: draft
---

# Build: {title}

**Slug:** `{slug}`
**Type:** {build_type}
**Created:** {today}

## Current Status

Build initialized. Awaiting Architect plan.

## References

- **PLAN.md:** `N5/builds/{slug}/PLAN.md`
- **meta.json:** `N5/builds/{slug}/meta.json`
- **Workers:** `N5/builds/{slug}/workers/`
- **Completions:** `N5/builds/{slug}/completions/`
"""
    
    build_file = build_dir / "BUILD.md"
    build_file.write_text(build_content)
    
    # Read and populate PLAN template
    plan_template = TEMPLATES_DIR / "plan_template.md"
    if plan_template.exists():
        plan_content = plan_template.read_text()
        plan_content = plan_content.replace("{{DATE}}", today)
        plan_content = plan_content.replace("{{TITLE}}", title)
        plan_content = plan_content.replace("{{SLUG}}", slug)
    else:
        # Fallback minimal plan if template missing
        plan_content = f"""---
created: {today}
last_edited: {today}
version: 1.0
type: build_plan
status: draft
---

# Plan: {title}

**Objective:** [TO BE FILLED BY ARCHITECT]

---

## Open Questions

- [ ] [TO BE FILLED]

---

## Checklist

### Phase 1: [NAME]
- ☐ [TASK]

---

## Phase 1: [NAME]

### Affected Files
- [TO BE FILLED]

### Changes
[TO BE FILLED]

### Unit Tests
- [TO BE FILLED]
"""
    
    plan_file = build_dir / "PLAN.md"
    plan_file.write_text(plan_content)
    
    # Read and populate STATUS template
    status_template = TEMPLATES_DIR / "status_template.md"
    if status_template.exists():
        status_content = status_template.read_text()
        status_content = status_content.replace("{{DATE}}", today)
        status_content = status_content.replace("{{TITLE}}", title)
        status_content = status_content.replace("{{SLUG}}", slug)
    else:
        # Fallback minimal status if template missing
        status_content = f"""---
created: {today}
build_slug: {slug}
---

# Build Status: {title}

## Quick Status
- **Progress:** 0%
- **Current Phase:** Not started
- **Plan:** `N5/builds/{slug}/PLAN.md`
"""
    
    status_file = build_dir / "STATUS.md"
    status_file.write_text(status_content)
    
    # Create .n5protected marker
    protected_file = build_dir / ".n5protected"
    protected_file.write_text(f"Protected build workspace created {today}\nBuild type: {build_type}\n")
    
    # Generate worker stubs if requested
    if num_workers > 0:
        generate_worker_stubs(build_dir, slug, num_workers)
    
    return build_dir


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new build workspace with v2 orchestration support.",
        epilog="""
Examples:
  python3 N5/scripts/init_build.py my-feature --title 'My Feature Build'
  python3 N5/scripts/init_build.py calendar-v2 --type code_build --workers 5
  python3 N5/scripts/init_build.py quick-fix --skip-prescreen
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "slug",
        help="Build identifier (lowercase-hyphenated, e.g., 'my-new-feature')"
    )
    parser.add_argument(
        "--title", "-t",
        help="Human-readable build title (defaults to slug titlecased)"
    )
    parser.add_argument(
        "--type",
        choices=VALID_TYPES,
        default="general",
        help=f"Build type (default: general). Options: {', '.join(VALID_TYPES)}"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=0,
        metavar="N",
        help="Number of worker brief stubs to generate (default: 0)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing build directory"
    )
    parser.add_argument(
        "--skip-prescreen",
        action="store_true",
        help="Skip check for incomplete builds"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if incomplete builds are found (non-interactive mode)"
    )
    
    args = parser.parse_args()
    
    build_dir = init_build(
        slug=args.slug,
        title=args.title,
        build_type=args.type,
        num_workers=args.workers,
        force=args.force,
        skip_prescreen=args.skip_prescreen,
        strict=args.strict
    )
    
    print(f"\n✓ Build workspace created: {build_dir}/")
    print(f"  ├── BUILD.md      (orchestrator document)")
    print(f"  ├── PLAN.md       (fill with Architect)")
    print(f"  ├── STATUS.md     (progress tracking)")
    print(f"  ├── meta.json     (build state)")
    print(f"  ├── workers/      (worker briefs go here)")
    if args.workers > 0:
        print(f"  │   └── {args.workers} stub(s) generated")
    print(f"  ├── completions/  (worker reports go here)")
    print(f"  └── .n5protected  (deletion protection)")
    print()
    print(f"Build type: {args.type}")
    print(f"Pre-decided orchestrator title: [{args.slug}] ORCH: Orchestrator")
    print()
    print(f"Next: Route to Architect to create plan and worker briefs.")


if __name__ == "__main__":
    main()
