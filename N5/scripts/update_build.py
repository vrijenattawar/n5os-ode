#!/usr/bin/env python3
"""
update_build.py - Worker completion tracking and build status management.

Commands:
    complete <slug> <worker_id>    Record worker completion (creates completions/<worker_id>.json)
    status <slug>                  Show human-readable build status
    status <slug> --json           Output machine-readable JSON status
    close <slug>                   Mark build as complete

Usage:
    python3 N5/scripts/update_build.py complete my-build W2.1
    python3 N5/scripts/update_build.py status my-build
    python3 N5/scripts/update_build.py status my-build --json
    python3 N5/scripts/update_build.py close my-build
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
SESSION_STATE_PATH = Path("/home/.z/workspaces") 


def get_convo_id_from_session_state() -> str | None:
    """Try to extract convo_id from SESSION_STATE.md in current conversation workspace."""
    for workspace_dir in SESSION_STATE_PATH.iterdir():
        if workspace_dir.is_dir() and workspace_dir.name.startswith("con_"):
            session_file = workspace_dir / "SESSION_STATE.md"
            if session_file.exists():
                content = session_file.read_text()
                match = re.search(r'Conversation ID:\s*`?([^`\s\n]+)`?', content)
                if match:
                    return match.group(1)
    return None


def validate_slug(slug: str) -> bool:
    """Validate slug: lowercase, hyphens, numbers only."""
    pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def validate_worker_id(worker_id: str) -> bool:
    """Validate worker_id format: W{wave}.{seq}"""
    pattern = r'^W[0-9]+\.[0-9]+$'
    return bool(re.match(pattern, worker_id))


def get_build_dir(slug: str) -> Path:
    """Get build directory, validating it exists."""
    if not validate_slug(slug):
        print(f"❌ Invalid slug format: '{slug}'")
        print("   Slug must be lowercase with hyphens (e.g., 'my-build')")
        sys.exit(1)
    
    build_dir = BUILDS_DIR / slug
    if not build_dir.exists():
        print(f"❌ Build not found: '{slug}'")
        print(f"   Expected at: {build_dir}")
        print(f"   Available builds: {', '.join(d.name for d in BUILDS_DIR.iterdir() if d.is_dir()) or 'none'}")
        sys.exit(1)
    
    return build_dir


def load_meta(build_dir: Path) -> dict:
    """Load meta.json from build directory."""
    meta_file = build_dir / "meta.json"
    if not meta_file.exists():
        print(f"❌ meta.json not found in {build_dir}")
        print("   Build may be incomplete or corrupted.")
        sys.exit(1)
    
    return json.loads(meta_file.read_text())


def save_meta(build_dir: Path, meta: dict):
    """Save meta.json to build directory."""
    meta_file = build_dir / "meta.json"
    meta_file.write_text(json.dumps(meta, indent=2) + "\n")


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format with timezone."""
    now = datetime.now().astimezone()
    return now.isoformat(timespec='seconds')


def cmd_complete(slug: str, worker_id: str):
    """Record worker completion - creates completion JSON and updates meta.json."""
    if not validate_worker_id(worker_id):
        print(f"❌ Invalid worker_id format: '{worker_id}'")
        print("   Expected format: W<wave>.<seq> (e.g., W1.1, W2.3)")
        sys.exit(1)
    
    build_dir = get_build_dir(slug)
    meta = load_meta(build_dir)
    
    # Create completions directory if missing
    completions_dir = build_dir / "completions"
    completions_dir.mkdir(exist_ok=True)
    
    # Check if already completed
    completion_file = completions_dir / f"{worker_id}.json"
    if completion_file.exists():
        print(f"⚠️  Worker {worker_id} already has a completion file.")
        response = input("   Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("   Aborted.")
            sys.exit(0)
    
    # Try to get convo_id from SESSION_STATE.md
    convo_id = get_convo_id_from_session_state()
    
    # Create completion record
    completion = {
        "worker_id": worker_id,
        "status": "complete",
        "completed_at": get_iso_timestamp(),
        "convo_id": convo_id,
        "files_created": [],
        "files_modified": [],
        "decisions": [],
        "recommendations": [],
        "blockers": []
    }
    
    completion_file.write_text(json.dumps(completion, indent=2) + "\n")
    
    # Update meta.json worker counts
    workers = meta.get("workers", {"total": 0, "complete": 0, "in_progress": 0, "blocked": 0, "pending": 0})
    workers["complete"] = workers.get("complete", 0) + 1
    if workers.get("pending", 0) > 0:
        workers["pending"] = workers["pending"] - 1
    meta["workers"] = workers
    
    # Update wave status if applicable
    wave_num = int(worker_id.split(".")[0][1:])  # Extract wave number from W2.1 -> 2
    for wave in meta.get("waves", []):
        if wave.get("wave") == wave_num:
            wave_workers = wave.get("workers", [])
            # Check if all workers in wave are complete
            all_complete = all(
                (completions_dir / f"{w}.json").exists() 
                for w in wave_workers
            )
            if all_complete:
                wave["status"] = "complete"
            elif wave["status"] == "pending":
                wave["status"] = "in_progress"
    
    save_meta(build_dir, meta)
    
    print(f"✓ Worker {worker_id} marked complete")
    print(f"  Completion file: {completion_file.relative_to(WORKSPACE)}")
    print(f"  Progress: {workers['complete']}/{workers['total']} workers")
    print()
    print(f"📝 Edit completion details: `file '{completion_file.relative_to(WORKSPACE)}'`")


def cmd_status(slug: str, as_json: bool = False):
    """Show build status - human-readable or JSON."""
    build_dir = get_build_dir(slug)
    meta = load_meta(build_dir)
    
    completions_dir = build_dir / "completions"
    
    # Gather completion data
    completed_workers = []
    if completions_dir.exists():
        for f in completions_dir.glob("W*.json"):
            try:
                data = json.loads(f.read_text())
                completed_workers.append({
                    "worker_id": data.get("worker_id", f.stem),
                    "completed_at": data.get("completed_at"),
                    "status": data.get("status", "complete")
                })
            except json.JSONDecodeError:
                completed_workers.append({"worker_id": f.stem, "status": "error"})
    
    workers = meta.get("workers", {})
    total = workers.get("total", 0)
    complete = workers.get("complete", 0)
    percentage = round(complete / total * 100) if total > 0 else 0
    
    if as_json:
        output = {
            "slug": slug,
            "title": meta.get("title", slug),
            "status": meta.get("status", "unknown"),
            "type": meta.get("type", "unknown"),
            "created": meta.get("created"),
            "completed_at": meta.get("completed_at"),
            "workers": {
                "total": total,
                "complete": complete,
                "percentage": percentage
            },
            "waves": meta.get("waves", []),
            "completed_workers": completed_workers
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"Build: {meta.get('title', slug)}")
        print(f"Status: {meta.get('status', 'unknown')}")
        print(f"Type: {meta.get('type', 'unknown')}")
        print(f"Created: {meta.get('created', 'unknown')}")
        if meta.get("completed_at"):
            print(f"Completed: {meta['completed_at']}")
        print()
        print(f"Workers: {complete}/{total} complete ({percentage}%)")
        
        # Show by wave
        for wave in meta.get("waves", []):
            wave_num = wave.get("wave", "?")
            wave_status = wave.get("status", "unknown")
            wave_workers = wave.get("workers", [])
            
            status_icon = {"complete": "✓", "in_progress": "▶", "pending": "○", "blocked": "✗"}.get(wave_status, "?")
            print(f"  Wave {wave_num} [{status_icon}]:")
            
            for w in wave_workers:
                completion_file = completions_dir / f"{w}.json" if completions_dir.exists() else None
                if completion_file and completion_file.exists():
                    print(f"    ✓ {w}")
                else:
                    print(f"    ○ {w}")
        
        print()
        print(f"Build dir: N5/builds/{slug}/")


def cmd_close(slug: str):
    """Mark build as complete."""
    build_dir = get_build_dir(slug)
    meta = load_meta(build_dir)
    
    workers = meta.get("workers", {})
    total = workers.get("total", 0)
    complete = workers.get("complete", 0)
    
    if complete < total:
        print(f"⚠️  Build has incomplete workers: {complete}/{total}")
        response = input("   Close anyway? [y/N]: ").strip().lower()
        if response != 'y':
            print("   Aborted.")
            sys.exit(0)
    
    meta["status"] = "complete"
    meta["completed_at"] = get_iso_timestamp()
    
    # Mark all waves as complete
    for wave in meta.get("waves", []):
        if wave.get("status") != "complete":
            wave["status"] = "complete"
    
    save_meta(build_dir, meta)
    
    print(f"✓ Build '{slug}' marked complete")
    print(f"  Completed at: {meta['completed_at']}")
    print(f"  Workers: {complete}/{total}")


def main():
    parser = argparse.ArgumentParser(
        description="Worker completion tracking and build status management.",
        epilog="Examples:\n"
               "  python3 N5/scripts/update_build.py complete my-build W2.1\n"
               "  python3 N5/scripts/update_build.py status my-build\n"
               "  python3 N5/scripts/update_build.py status my-build --json\n"
               "  python3 N5/scripts/update_build.py close my-build",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # complete command
    complete_parser = subparsers.add_parser(
        "complete", 
        help="Record worker completion"
    )
    complete_parser.add_argument("slug", help="Build slug")
    complete_parser.add_argument("worker_id", help="Worker ID (e.g., W2.1)")
    
    # status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show build status"
    )
    status_parser.add_argument("slug", help="Build slug")
    status_parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="as_json",
        help="Output as JSON"
    )
    
    # close command
    close_parser = subparsers.add_parser(
        "close",
        help="Mark build as complete"
    )
    close_parser.add_argument("slug", help="Build slug")
    
    args = parser.parse_args()
    
    if args.command == "complete":
        cmd_complete(args.slug, args.worker_id)
    elif args.command == "status":
        cmd_status(args.slug, args.as_json)
    elif args.command == "close":
        cmd_close(args.slug)


if __name__ == "__main__":
    main()
