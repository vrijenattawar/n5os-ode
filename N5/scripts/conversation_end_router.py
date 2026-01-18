#!/usr/bin/env python3
"""
Conversation End Router v3.0

Determines which tier of conversation-end workflow to execute based on:
- SESSION_STATE.md content (if present)
- Build workspace presence
- DEBUG_LOG.jsonl presence  
- Artifact count in conversation workspace
- Git changes in user workspace

Tier Logic:
- Tier 1 (Quick): Default for simple discussions, Q&A
- Tier 2 (Standard): ≥3 artifacts OR research/substantial discussion
- Tier 3 (Full Build): Build/orchestrator work, debug sessions, capability changes

Usage:
    python3 conversation_end_router.py --convo-id <id> [--force-tier N]
    
Returns JSON with tier recommendation and reasoning.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
CONVERSATION_WORKSPACE_BASE = Path("/home/.z/workspaces")
USER_WORKSPACE = Path("/home/workspace")
BUILD_WORKSPACE = USER_WORKSPACE / "N5" / "builds"
ARTIFACT_THRESHOLD_TIER2 = 3

# Build/orchestrator markers in conversation content
BUILD_MARKERS = [
    "build", "implement", "create system", "new feature",
    "orchestrator", "pipeline", "migration", "refactor",
    "architecture", "schema change"
]

DEBUG_MARKERS = [
    "debug", "fix", "broken", "error", "failed",
    "troubleshoot", "repair", "diagnose"
]


def get_conversation_workspace(convo_id: str) -> Path:
    """Get path to conversation workspace."""
    # Handle both formats: con_XXX and just XXX
    if not convo_id.startswith("con_"):
        convo_id = f"con_{convo_id}"
    return CONVERSATION_WORKSPACE_BASE / convo_id


def parse_session_state(convo_path: Path) -> dict:
    """Parse SESSION_STATE.md if it exists."""
    session_file = convo_path / "SESSION_STATE.md"
    
    if not session_file.exists():
        logger.info("No SESSION_STATE.md found")
        return {"exists": False}
    
    content = session_file.read_text()
    
    # Extract key fields from YAML frontmatter or markdown
    result = {
        "exists": True,
        "type": None,
        "focus": None,
        "has_artifacts": False,
        "progress_items": 0
    }
    
    # Look for Type field
    for line in content.split("\n"):
        line_lower = line.lower().strip()
        if line_lower.startswith("type:"):
            result["type"] = line.split(":", 1)[1].strip().lower()
        elif line_lower.startswith("focus:"):
            result["focus"] = line.split(":", 1)[1].strip()
        elif "artifacts:" in line_lower:
            result["has_artifacts"] = True
        elif line.startswith("- ") and ("☑" in line or "[x]" in line.lower()):
            result["progress_items"] += 1
    
    logger.info(f"SESSION_STATE parsed: type={result['type']}, progress_items={result['progress_items']}")
    return result


def count_artifacts(convo_path: Path) -> int:
    """Count files in conversation workspace (excluding system files)."""
    if not convo_path.exists():
        return 0
    
    count = 0
    exclude_patterns = ["SESSION_STATE.md", "DEBUG_LOG.jsonl", ".log", "__pycache__"]
    
    for f in convo_path.rglob("*"):
        if f.is_file():
            # Skip system/log files
            if any(pattern in str(f) for pattern in exclude_patterns):
                continue
            count += 1
    
    logger.info(f"Artifact count: {count}")
    return count


def check_build_workspace(convo_id: str) -> dict:
    """Check if a build workspace exists for this conversation."""
    result = {"exists": False, "slug": None, "path": None}
    
    if not BUILD_WORKSPACE.exists():
        return result
    
    # Check each build directory for a reference to this convo
    for build_dir in BUILD_WORKSPACE.iterdir():
        if not build_dir.is_dir():
            continue
        
        plan_file = build_dir / "PLAN.md"
        status_file = build_dir / "STATUS.md"
        
        for check_file in [plan_file, status_file]:
            if check_file.exists():
                content = check_file.read_text()
                if convo_id in content:
                    result = {
                        "exists": True,
                        "slug": build_dir.name,
                        "path": str(build_dir)
                    }
                    logger.info(f"Build workspace found: {build_dir.name}")
                    return result
    
    return result


def check_debug_log(convo_path: Path) -> bool:
    """Check if DEBUG_LOG.jsonl exists (indicates troubleshooting session)."""
    debug_log = convo_path / "DEBUG_LOG.jsonl"
    exists = debug_log.exists()
    if exists:
        logger.info("DEBUG_LOG.jsonl found - troubleshooting session")
    return exists


def check_git_changes() -> dict:
    """Check for uncommitted git changes in user workspace."""
    result = {"has_changes": False, "file_count": 0, "summary": ""}
    
    try:
        # Check if workspace is a git repo
        git_dir = USER_WORKSPACE / ".git"
        if not git_dir.exists():
            return result
        
        # Get status
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=USER_WORKSPACE,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if proc.returncode == 0 and proc.stdout.strip():
            lines = [l for l in proc.stdout.strip().split("\n") if l]
            result = {
                "has_changes": True,
                "file_count": len(lines),
                "summary": f"{len(lines)} uncommitted changes"
            }
            logger.info(f"Git changes detected: {result['file_count']} files")
    except Exception as e:
        logger.warning(f"Git check failed: {e}")
    
    return result


def scan_for_markers(convo_path: Path) -> dict:
    """Scan conversation files for build/debug markers."""
    result = {
        "build_markers_found": [],
        "debug_markers_found": [],
        "is_likely_build": False,
        "is_likely_debug": False
    }
    
    if not convo_path.exists():
        return result
    
    # Read text files in conversation workspace
    text_content = ""
    for f in convo_path.glob("*.md"):
        try:
            text_content += f.read_text().lower() + "\n"
        except:
            continue
    
    # Check for markers
    for marker in BUILD_MARKERS:
        if marker in text_content:
            result["build_markers_found"].append(marker)
    
    for marker in DEBUG_MARKERS:
        if marker in text_content:
            result["debug_markers_found"].append(marker)
    
    result["is_likely_build"] = len(result["build_markers_found"]) >= 2
    result["is_likely_debug"] = len(result["debug_markers_found"]) >= 2
    
    if result["is_likely_build"]:
        logger.info(f"Build markers found: {result['build_markers_found'][:3]}")
    if result["is_likely_debug"]:
        logger.info(f"Debug markers found: {result['debug_markers_found'][:3]}")
    
    return result


def determine_tier(
    session_state: dict,
    artifact_count: int,
    build_workspace: dict,
    has_debug_log: bool,
    git_changes: dict,
    markers: dict,
    force_tier: int = None
) -> dict:
    """Determine which tier to use based on all signals."""
    
    # Handle manual override
    if force_tier is not None:
        if force_tier in [1, 2, 3]:
            return {
                "tier": force_tier,
                "reason": f"Manual override: --force-tier={force_tier}",
                "confidence": "high",
                "signals": ["manual_override"]
            }
        else:
            logger.warning(f"Invalid force_tier {force_tier}, ignoring")
    
    signals = []
    tier = 1  # Default
    reasons = []
    
    # Tier 3 signals (highest priority)
    tier3_signals = []
    
    if build_workspace["exists"]:
        tier3_signals.append(f"build_workspace:{build_workspace['slug']}")
        reasons.append(f"Build workspace exists: {build_workspace['slug']}")
    
    if has_debug_log:
        tier3_signals.append("debug_log_present")
        reasons.append("DEBUG_LOG.jsonl present (troubleshooting session)")
    
    if session_state.get("type") in ["build", "orchestrator"]:
        tier3_signals.append(f"session_type:{session_state['type']}")
        reasons.append(f"SESSION_STATE type is '{session_state['type']}'")
    
    if markers["is_likely_build"]:
        tier3_signals.append("build_markers")
        reasons.append(f"Build markers detected: {markers['build_markers_found'][:2]}")
    
    # Tier 2 signals
    tier2_signals = []
    
    if artifact_count >= ARTIFACT_THRESHOLD_TIER2:
        tier2_signals.append(f"artifacts:{artifact_count}")
        reasons.append(f"≥{ARTIFACT_THRESHOLD_TIER2} artifacts created ({artifact_count})")
    
    if session_state.get("type") in ["research", "discussion"] and session_state.get("progress_items", 0) > 3:
        tier2_signals.append("substantial_progress")
        reasons.append("Substantial progress in research/discussion")
    
    # Git changes alone don't escalate - they're workspace-wide, not convo-specific
    # But they DO contribute if other signals present
    has_other_tier2_signals = len(tier2_signals) > 0
    
    if git_changes["has_changes"] and (has_other_tier2_signals or artifact_count > 0):
        tier2_signals.append(f"git_changes:{git_changes['file_count']}")
        reasons.append(f"Git changes detected ({git_changes['file_count']} files)")
    
    if markers["is_likely_debug"] and not has_debug_log:
        tier2_signals.append("debug_markers")
        reasons.append("Debug/fix activity detected")
    
    # Determine final tier
    if tier3_signals:
        tier = 3
        signals = tier3_signals
        confidence = "high" if len(tier3_signals) >= 2 else "medium"
    elif tier2_signals:
        tier = 2
        signals = tier2_signals
        confidence = "high" if len(tier2_signals) >= 2 else "medium"
    else:
        tier = 1
        signals = ["default"]
        reasons = ["No escalation signals detected - using quick close"]
        confidence = "high"
    
    return {
        "tier": tier,
        "reason": "; ".join(reasons) if reasons else "Default tier",
        "confidence": confidence,
        "signals": signals
    }


def route_conversation(convo_id: str, force_tier: int = None) -> dict:
    """Main routing function - analyzes conversation and returns tier recommendation."""
    
    logger.info(f"Routing conversation: {convo_id}")
    
    convo_path = get_conversation_workspace(convo_id)
    
    # Gather all signals
    session_state = parse_session_state(convo_path)
    artifact_count = count_artifacts(convo_path)
    build_workspace = check_build_workspace(convo_id)
    has_debug_log = check_debug_log(convo_path)
    git_changes = check_git_changes()
    markers = scan_for_markers(convo_path)
    
    # Determine tier
    tier_result = determine_tier(
        session_state=session_state,
        artifact_count=artifact_count,
        build_workspace=build_workspace,
        has_debug_log=has_debug_log,
        git_changes=git_changes,
        markers=markers,
        force_tier=force_tier
    )
    
    # Build full result
    result = {
        "convo_id": convo_id,
        "convo_path": str(convo_path),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "recommendation": tier_result,
        "analysis": {
            "session_state": session_state,
            "artifact_count": artifact_count,
            "build_workspace": build_workspace,
            "has_debug_log": has_debug_log,
            "git_changes": git_changes,
            "markers": {
                "build": markers["build_markers_found"][:5],
                "debug": markers["debug_markers_found"][:5],
                "is_likely_build": markers["is_likely_build"],
                "is_likely_debug": markers["is_likely_debug"]
            }
        }
    }
    
    logger.info(f"Routing complete: Tier {tier_result['tier']} ({tier_result['confidence']})")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Route conversation to appropriate close tier"
    )
    parser.add_argument(
        "--convo-id",
        required=True,
        help="Conversation ID (with or without con_ prefix)"
    )
    parser.add_argument(
        "--force-tier",
        type=int,
        choices=[1, 2, 3],
        help="Force specific tier (overrides auto-detection)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress logging, output JSON only"
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.disable(logging.CRITICAL)
    
    result = route_conversation(args.convo_id, args.force_tier)
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        Path(args.output).write_text(output_json)
        if not args.quiet:
            print(f"Result written to: {args.output}")
    else:
        print(output_json)
    
    # Return tier as exit code for easy scripting
    sys.exit(0)


if __name__ == "__main__":
    main()



