#!/usr/bin/env python3
"""
Spawn Worker v3.0 - Pure Plumbing

The LLM writes all worker assignment content.
This script handles ONLY:
1. Generate unique worker ID and timestamp
2. Save the LLM-written markdown file
3. Update parent SESSION_STATE with worker reference
4. Create worker_updates/ directory for communication

Usage:
    # LLM writes assignment, script saves it
    python3 spawn_worker.py --parent con_XXX --content-file /path/to/assignment.md
    
    # Generate IDs only (LLM will save file manually)
    python3 spawn_worker.py --parent con_XXX --generate-ids

IMPORTANT: This script does NOT generate content. The LLM must:
1. Read context (SESSION_STATE, immediate request)
2. Deliberately scope the work
3. Write a complete worker assignment
4. Call this script to save it
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

WORKSPACE = Path("/home/workspace")
WORKSPACES_ROOT = Path("/home/.z/workspaces")
OUTPUT_DIR = WORKSPACE / "Records" / "Temporary"
VERSION = "3.0"


def generate_ids(parent_id: str) -> dict:
    """Generate worker ID and timestamp."""
    now = datetime.now(timezone.utc)
    suffix = parent_id[-4:] if len(parent_id) >= 4 else parent_id
    worker_id = f"WORKER_{suffix}_{now.strftime('%Y%m%d_%H%M%S')}"
    timestamp = now.isoformat()
    filename = f"WORKER_ASSIGNMENT_{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond:06d}_{suffix}.md"
    
    return {
        "worker_id": worker_id,
        "timestamp": timestamp,
        "filename": filename,
        "output_path": str(OUTPUT_DIR / filename),
    }


def update_parent_session_state(parent_id: str, worker_filename: str, timestamp: str) -> bool:
    """Add worker reference to parent's SESSION_STATE.md"""
    session_path = WORKSPACES_ROOT / parent_id / "SESSION_STATE.md"
    
    if not session_path.exists():
        logging.warning("No parent SESSION_STATE.md found")
        return False
    
    content = session_path.read_text()
    worker_entry = f"- {worker_filename} (spawned {timestamp[:16].replace('T', ' ')} UTC)"
    
    if "## Spawned Workers" in content:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("## Spawned Workers"):
                lines.insert(i + 2, worker_entry)
                break
        content = "\n".join(lines)
    else:
        content += f"\n\n## Spawned Workers\n\n{worker_entry}\n"
    
    session_path.write_text(content)
    logging.info(f"✓ Updated parent SESSION_STATE: {worker_entry}")
    return True


def create_worker_updates_dir(parent_id: str) -> Path:
    """Create worker_updates directory in parent workspace."""
    updates_dir = WORKSPACES_ROOT / parent_id / "worker_updates"
    updates_dir.mkdir(exist_ok=True)
    return updates_dir


def main():
    parser = argparse.ArgumentParser(
        description="Save LLM-written worker assignment and link to parent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
IMPORTANT: The LLM writes the worker assignment content.
This script only handles:
  1. Generate unique IDs
  2. Save the markdown file
  3. Update parent SESSION_STATE with worker reference

Example workflow:
  1. LLM reads context and writes assignment to temp file
  2. LLM calls: python3 spawn_worker.py --parent con_XXX --content-file /path/to/assignment.md
  3. Script saves to Records/Temporary/ and links to parent

ID-only mode (for LLM to write file manually):
  python3 spawn_worker.py --parent con_XXX --generate-ids
"""
    )
    parser.add_argument("--parent", required=True, help="Parent conversation ID")
    parser.add_argument("--content-file", help="Path to markdown file with worker assignment content")
    parser.add_argument("--generate-ids", action="store_true", help="Only generate IDs, output JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    
    args = parser.parse_args()
    
    # Handle --generate-ids mode
    if args.generate_ids:
        ids = generate_ids(args.parent)
        ids["parent_workspace"] = str(Path(f"/home/.z/workspaces/{args.parent}"))
        ids["worker_updates_dir"] = str(Path(f"/home/.z/workspaces/{args.parent}/worker_updates"))
        ids["parent_id"] = args.parent
        print(json.dumps(ids, indent=2))
        return 0
    
    # Require --content-file for actual spawning
    if not args.content_file:
        logging.error("--content-file is required (unless using --generate-ids)")
        logging.error("")
        logging.error("The LLM must write the worker assignment content.")
        logging.error("This script only saves the file and links to parent.")
        logging.error("")
        logging.error("Workflow:")
        logging.error("  1. LLM reads context (SESSION_STATE, immediate request)")
        logging.error("  2. LLM writes complete worker assignment to a temp file")
        logging.error("  3. LLM calls: python3 spawn_worker.py --parent con_XXX --content-file /path/to/file.md")
        return 1
    
    # Read content
    content_path = Path(args.content_file)
    if not content_path.exists():
        logging.error(f"Content file not found: {content_path}")
        return 1
    
    content = content_path.read_text()
    if len(content.strip()) < 50:
        logging.error(f"Content file seems too short ({len(content)} chars). Worker assignments need substance.")
        return 1
    
    # Generate IDs
    ids = generate_ids(args.parent)
    
    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Would save to: {ids['output_path']}")
        print(f"Content length: {len(content)} chars")
        print(f"First 500 chars:\n{content[:500]}")
        return 0
    
    # Write file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(ids['output_path'])
    output_path.write_text(content)
    logging.info(f"✓ Worker assignment saved: {output_path}")
    
    # Update parent SESSION_STATE
    update_parent_session_state(args.parent, ids['filename'], ids['timestamp'])
    
    # Create worker_updates directory
    worker_updates_path = create_worker_updates_dir(args.parent)
    
    # Output for LLM
    result = {
        "success": True,
        "worker_id": ids['worker_id'],
        "output_path": str(output_path),
        "relative_path": f"Records/Temporary/{ids['filename']}",
        "worker_updates_dir": str(worker_updates_path),
    }
    print(json.dumps(result, indent=2))
    
    logging.info(f"\n✓ Worker saved!")
    logging.info(f"📄 Open this file in a new conversation: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

