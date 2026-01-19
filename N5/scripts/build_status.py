#!/usr/bin/env python3
"""
build_status.py - Global view of all builds across N5/builds/.

Commands:
    list                    List all builds with status
    list --incomplete       Show only active/in-progress builds
    list --json             Output machine-readable JSON
    list --all              Show all complete builds (not just recent)
    regenerate              Write JSON to dashboard data file

Usage:
    python3 N5/scripts/build_status.py list
    python3 N5/scripts/build_status.py list --incomplete
    python3 N5/scripts/build_status.py list --json
    python3 N5/scripts/build_status.py regenerate
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
DASHBOARD_DATA_DIR = WORKSPACE / "Sites" / "build-tracker" / "data"
DASHBOARD_DATA_FILE = DASHBOARD_DATA_DIR / "builds.json"
STALE_THRESHOLD_DAYS = 7
RECENT_COMPLETE_LIMIT = 10


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format with timezone."""
    now = datetime.now().astimezone()
    return now.isoformat(timespec='seconds')


def get_file_mtime(path: Path) -> datetime | None:
    """Get file modification time as datetime, or None if doesn't exist."""
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    return None


def parse_date_string(date_str: str | None) -> datetime | None:
    """Parse a date string (YYYY-MM-DD or ISO format) to datetime."""
    if not date_str:
        return None
    try:
        # Try ISO format first
        if 'T' in date_str:
            return datetime.fromisoformat(date_str)
        # Try simple date format
        return datetime.strptime(date_str, "%Y-%m-%d").astimezone()
    except (ValueError, TypeError):
        return None


def extract_objective(build_dir: Path) -> str | None:
    """Extract objective/description from PLAN.md if it exists."""
    plan_file = build_dir / "PLAN.md"
    if not plan_file.exists():
        return None
    
    try:
        content = plan_file.read_text()
        # Look for **Objective:** line
        for line in content.split('\n'):
            if line.strip().startswith('**Objective:**'):
                # Extract the text after **Objective:**
                obj = line.replace('**Objective:**', '').strip()
                # Truncate if too long
                if len(obj) > 200:
                    obj = obj[:197] + '...'
                return obj
        return None
    except IOError:
        return None


def is_stale(build_info: dict, completions_dir: Path) -> bool:
    """Determine if a build is stale (no activity in STALE_THRESHOLD_DAYS)."""
    if build_info.get("status") != "active":
        return False
    
    now = datetime.now().astimezone()
    threshold = now - timedelta(days=STALE_THRESHOLD_DAYS)
    
    # Check meta.json mtime
    meta_mtime = build_info.get("_meta_mtime")
    if meta_mtime and meta_mtime > threshold:
        return False
    
    # Check latest completion file
    if completions_dir.exists():
        completion_files = list(completions_dir.glob("W*.json"))
        if completion_files:
            latest_completion = max(get_file_mtime(f) for f in completion_files)
            if latest_completion and latest_completion > threshold:
                return False
    
    return True


def scan_build_v2(build_dir: Path) -> dict | None:
    """Scan a v2 build directory and extract status info."""
    meta_file = build_dir / "meta.json"
    if not meta_file.exists():
        return None
    
    try:
        meta = json.loads(meta_file.read_text())
    except (json.JSONDecodeError, IOError):
        return None
    
    completions_dir = build_dir / "completions"
    workers_data = meta.get("workers", {})
    
    # Handle two different workers schemas:
    # 1. New schema: workers: {total: X, complete: Y, ...}
    # 2. Old schema: workers: {W1.1: {...}, W1.2: {...}, ...}
    if "total" in workers_data:
        # New schema - use the provided counts directly
        total_workers = workers_data.get("total", 0)
        complete_workers = workers_data.get("complete", 0)
    else:
        # Old schema - workers is a dict of worker_id -> worker_info
        # Count worker keys that look like worker IDs (W*.*)
        worker_ids = [k for k in workers_data.keys() if k.startswith("W")]
        total_workers = len(worker_ids)
        
        # Count completion files to determine complete count
        complete_workers = 0
        if completions_dir.exists():
            completion_files = list(completions_dir.glob("W*.json"))
            complete_workers = len(completion_files)
    
    # Extract objective from PLAN.md if available
    objective = extract_objective(build_dir)
    
    build_info = {
        "slug": meta.get("slug", build_dir.name),
        "title": meta.get("title", build_dir.name),
        "status": meta.get("status", "unknown"),
        "type": meta.get("type", "unknown"),
        "created": meta.get("created"),
        "completed_at": meta.get("completed_at"),
        "objective": objective,
        "workers": {
            "complete": complete_workers,
            "total": total_workers
        },
        "progress_pct": 0,
        "path": str(build_dir.relative_to(WORKSPACE)),
        "_meta_mtime": get_file_mtime(meta_file),
        "_is_v2": True
    }
    
    # Calculate progress
    total = build_info["workers"]["total"]
    complete = build_info["workers"]["complete"]
    if total > 0:
        build_info["progress_pct"] = round((complete / total) * 100)
    
    # Check staleness
    build_info["is_stale"] = is_stale(build_info, completions_dir)
    
    return build_info


def scan_build_legacy(build_dir: Path) -> dict | None:
    """Scan a legacy build (no meta.json) and extract info."""
    # Legacy builds always count as complete - we only track v2 builds as active
    slug = build_dir.name
    
    # Try to get created date from directory mtime or STATUS.md
    created = None
    status_file = build_dir / "STATUS.md"
    if status_file.exists():
        created_mtime = get_file_mtime(status_file)
        if created_mtime:
            created = created_mtime.strftime("%Y-%m-%d")
    
    if not created:
        dir_mtime = get_file_mtime(build_dir)
        if dir_mtime:
            created = dir_mtime.strftime("%Y-%m-%d")
    
    # Extract objective if PLAN.md exists
    objective = extract_objective(build_dir)
    
    return {
        "slug": slug,
        "title": slug.replace("-", " ").title(),
        "status": "complete",  # Legacy builds are always complete
        "type": "legacy",
        "created": created,
        "completed_at": created,  # Assume completed when created for legacy
        "objective": objective,
        "workers": {
            "complete": 0,
            "total": 0
        },
        "progress_pct": 100,  # Legacy builds show as 100% (done)
        "path": str(build_dir.relative_to(WORKSPACE)),
        "_is_v2": False
    }


def scan_all_builds() -> list[dict]:
    """Scan all builds in N5/builds/ and return build info list."""
    builds = []
    
    if not BUILDS_DIR.exists():
        return builds
    
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue
        
        # Try v2 format first
        build_info = scan_build_v2(build_dir)
        if build_info:
            builds.append(build_info)
            continue
        
        # Fall back to legacy format
        build_info = scan_build_legacy(build_dir)
        if build_info:
            builds.append(build_info)
    
    return builds


def sort_builds(builds: list[dict]) -> list[dict]:
    """Sort builds: active first, then by created date descending."""
    def sort_key(b):
        # Primary: active status (active=0, complete=1, unknown=2)
        status_order = {"active": 0, "in_progress": 0, "complete": 1}.get(b.get("status"), 2)
        # Secondary: created date (newer first)
        created = b.get("created") or "1970-01-01"
        return (status_order, created)
    
    # Sort by status first, then reverse sort by date (newest first)
    return sorted(builds, key=lambda b: (sort_key(b)[0], -hash(sort_key(b)[1])))


def filter_incomplete(builds: list[dict]) -> list[dict]:
    """Filter to only active/incomplete builds."""
    return [b for b in builds if b.get("status") in ("active", "in_progress")]


def cmd_list(args):
    """List all builds."""
    builds = scan_all_builds()
    builds = sort_builds(builds)
    
    if args.incomplete:
        builds = filter_incomplete(builds)
    
    if args.as_json:
        output_json(builds, args.all)
        return
    
    output_human(builds, args.all, args.incomplete)


def output_json(builds: list[dict], show_all: bool):
    """Output builds in JSON format."""
    # Clean up internal fields
    clean_builds = []
    for b in builds:
        clean = {k: v for k, v in b.items() if not k.startswith("_")}
        clean_builds.append(clean)
    
    active_builds = [b for b in clean_builds if b.get("status") in ("active", "in_progress")]
    complete_builds = [b for b in clean_builds if b.get("status") == "complete"]
    stale_builds = [b for b in clean_builds if b.get("is_stale")]
    
    # Limit complete builds unless --all
    if not show_all and len(complete_builds) > RECENT_COMPLETE_LIMIT:
        complete_builds = complete_builds[:RECENT_COMPLETE_LIMIT]
    
    output = {
        "generated_at": get_iso_timestamp(),
        "builds": active_builds + complete_builds,
        "summary": {
            "total": len(clean_builds),
            "active": len(active_builds),
            "complete": len([b for b in clean_builds if b.get("status") == "complete"]),
            "stale": len(stale_builds)
        }
    }
    
    print(json.dumps(output, indent=2))


def output_human(builds: list[dict], show_all: bool, incomplete_only: bool):
    """Output builds in human-readable format."""
    active_builds = [b for b in builds if b.get("status") in ("active", "in_progress")]
    complete_builds = [b for b in builds if b.get("status") == "complete"]
    
    if active_builds:
        print("Active Builds:")
        for b in active_builds:
            stale_flag = " ⚠️ stale" if b.get("is_stale") else ""
            workers = b.get("workers", {})
            complete = workers.get("complete", 0)
            total = workers.get("total", 0)
            pct = b.get("progress_pct", 0)
            
            if total > 0:
                progress = f"{complete}/{total} workers ({pct}%)"
            else:
                progress = "legacy"
            
            build_type = b.get("type", "unknown")
            created = b.get("created", "unknown")
            
            print(f"  ● {b['slug']:<20} {progress:<20} {build_type:<12} {created}{stale_flag}")
        print()
    
    if not incomplete_only and complete_builds:
        display_complete = complete_builds if show_all else complete_builds[:RECENT_COMPLETE_LIMIT]
        remaining = len(complete_builds) - len(display_complete)
        
        label = "Complete Builds:" if show_all else "Complete Builds (recent):"
        print(label)
        for b in display_complete:
            workers = b.get("workers", {})
            complete = workers.get("complete", 0)
            total = workers.get("total", 0)
            
            if total > 0:
                progress = f"{complete}/{total} workers"
            else:
                progress = "legacy"
            
            build_type = b.get("type", "unknown")
            created = b.get("created", "unknown")
            
            print(f"  ✓ {b['slug']:<20} {progress:<20} {build_type:<12} {created}")
        
        if remaining > 0:
            print(f"  ... and {remaining} more (use --all to see all)")
        print()
    
    # Summary
    total = len(builds)
    active = len(active_builds)
    complete = len(complete_builds)
    stale = len([b for b in builds if b.get("is_stale")])
    
    print(f"Total: {total} builds ({active} active, {complete} complete)", end="")
    if stale > 0:
        print(f", {stale} stale", end="")
    print()


def cmd_regenerate(args):
    """Regenerate dashboard data file."""
    builds = scan_all_builds()
    builds = sort_builds(builds)
    
    # Clean up internal fields
    clean_builds = []
    for b in builds:
        clean = {k: v for k, v in b.items() if not k.startswith("_")}
        clean_builds.append(clean)
    
    active_builds = [b for b in clean_builds if b.get("status") in ("active", "in_progress")]
    complete_builds = [b for b in clean_builds if b.get("status") == "complete"]
    stale_builds = [b for b in clean_builds if b.get("is_stale")]
    
    output = {
        "generated_at": get_iso_timestamp(),
        "builds": clean_builds,
        "summary": {
            "total": len(clean_builds),
            "active": len(active_builds),
            "complete": len(complete_builds),
            "stale": len(stale_builds)
        }
    }
    
    # Ensure directory exists
    DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    DASHBOARD_DATA_FILE.write_text(json.dumps(output, indent=2) + "\n")
    
    print(f"✓ Dashboard data regenerated")
    print(f"  File: {DASHBOARD_DATA_FILE.relative_to(WORKSPACE)}")
    print(f"  Builds: {len(clean_builds)} total ({len(active_builds)} active)")


def main():
    parser = argparse.ArgumentParser(
        description="Global view of all builds across N5/builds/.",
        epilog="Examples:\n"
               "  python3 N5/scripts/build_status.py list\n"
               "  python3 N5/scripts/build_status.py list --incomplete\n"
               "  python3 N5/scripts/build_status.py list --json\n"
               "  python3 N5/scripts/build_status.py regenerate",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="List all builds with status"
    )
    list_parser.add_argument(
        "--incomplete", "-i",
        action="store_true",
        help="Show only active/in-progress builds"
    )
    list_parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="as_json",
        help="Output as JSON"
    )
    list_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Show all complete builds (not just recent)"
    )
    
    # regenerate command
    regenerate_parser = subparsers.add_parser(
        "regenerate",
        help="Write JSON to dashboard data file"
    )
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list(args)
    elif args.command == "regenerate":
        cmd_regenerate(args)


if __name__ == "__main__":
    main()
