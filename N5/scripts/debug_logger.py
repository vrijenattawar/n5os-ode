#!/usr/bin/env python3
"""
Debug Logger - Track debugging attempts and detect circular patterns

Usage:
    debug_logger.py append --component X --problem "Y" --hypothesis "Z" --actions "A,B" --outcome success|failure
    debug_logger.py recent [--limit N]
    debug_logger.py patterns [--window N] [--threshold N]

Commands:
    append    - Add a new debug log entry
    recent    - Show recent debug attempts
    patterns  - Detect circular debugging patterns

Part of n5OS-Ode: https://github.com/vrijenattawar/n5os-ode
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


class DebugLogger:
    """Track debugging attempts and detect circular patterns."""
    
    def __init__(self, log_path: Optional[Path] = None):
        """Initialize with optional custom log path."""
        if log_path:
            self.log_path = Path(log_path)
        else:
            # Default to conversation workspace if available
            convo_workspace = os.environ.get("CONVERSATION_WORKSPACE")
            if convo_workspace:
                self.log_path = Path(convo_workspace) / "DEBUG_LOG.jsonl"
            else:
                # Fallback to N5 runtime
                self.log_path = Path("/home/workspace/N5/runtime/DEBUG_LOG.jsonl")
        
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def append(self, component: str, problem: str, hypothesis: str,
               actions: List[str], outcome: str, notes: str = None) -> Dict:
        """
        Log a debug attempt.
        
        Args:
            component: System/file/area being debugged
            problem: Description of the issue
            hypothesis: What we thought was wrong
            actions: List of actions taken
            outcome: "success", "failure", or "partial"
            notes: Optional additional notes
        
        Returns:
            The logged entry
        """
        entry = {
            "entry_id": self._generate_id(),
            "ts": datetime.now(timezone.utc).isoformat(),
            "component": component,
            "problem": problem,
            "hypothesis": hypothesis,
            "actions": actions if isinstance(actions, list) else [actions],
            "outcome": outcome,
        }
        
        if notes:
            entry["notes"] = notes
        
        # Append to log
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        logger.info(f"Logged debug attempt: {component} [{outcome}]")
        return entry
    
    def read_all(self) -> List[Dict]:
        """Read all log entries."""
        if not self.log_path.exists():
            return []
        
        entries = []
        with open(self.log_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        return entries
    
    def recent(self, limit: int = 10) -> List[Dict]:
        """Get recent entries."""
        entries = self.read_all()
        return entries[-limit:] if len(entries) > limit else entries
    
    def _generate_id(self) -> str:
        """Generate a unique entry ID."""
        import hashlib
        ts = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(ts.encode()).hexdigest()[:8]
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate text similarity using simple Jaccard coefficient."""
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _shared_keywords(self, s1: str, s2: str, min_length: int = 4) -> float:
        """Calculate percentage of shared meaningful keywords."""
        words1 = set(w.lower() for w in s1.split() if len(w) >= min_length)
        words2 = set(w.lower() for w in s2.split() if len(w) >= min_length)
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def detect_patterns(self, window: int = 10, threshold: int = 3) -> Dict:
        """
        Detect circular debugging patterns.
        
        Returns: {
            "circular_detected": bool,
            "patterns": [{"problem": str, "count": int, "entries": [entry_ids]}],
            "warning": str
        }
        """
        try:
            entries = self.read_all()
            if len(entries) < threshold:
                return {
                    "circular_detected": False,
                    "patterns": [],
                    "warning": None
                }
            
            # Only check recent window
            recent = entries[-window:] if len(entries) > window else entries
            
            # Group similar problems
            clusters = []
            for i, entry in enumerate(recent):
                # Skip successes for pattern detection
                if entry["outcome"] == "success":
                    continue
                
                # Find matching cluster
                matched = False
                for cluster in clusters:
                    ref = cluster["entries"][0]
                    
                    # Check similarity
                    problem_sim = self._similarity(entry["problem"], ref["problem"])
                    component_match = entry["component"] == ref["component"]
                    keyword_sim = self._shared_keywords(entry["problem"], ref["problem"])
                    
                    # Match criteria: same component + (high text similarity OR high keyword overlap)
                    if component_match and (problem_sim > 0.7 or keyword_sim > 0.6):
                        cluster["entries"].append(entry)
                        matched = True
                        break
                
                if not matched:
                    clusters.append({
                        "problem": entry["problem"],
                        "component": entry["component"],
                        "entries": [entry]
                    })
            
            # Find clusters meeting threshold
            significant_patterns = [
                {
                    "problem": c["problem"],
                    "component": c["component"],
                    "count": len(c["entries"]),
                    "entry_ids": [e["entry_id"] for e in c["entries"]]
                }
                for c in clusters
                if len(c["entries"]) >= threshold
            ]
            
            circular = len(significant_patterns) > 0
            
            warning = None
            if circular:
                p = significant_patterns[0]
                warning = (
                    f"⚠️ CIRCULAR DEBUGGING DETECTED\n"
                    f"Component: {p['component']}\n"
                    f"Problem: {p['problem'][:80]}...\n"
                    f"Attempts: {p['count']} similar failures\n"
                    f"→ Consider: Different approach or stepping back to reassess"
                )
            
            return {
                "circular_detected": circular,
                "patterns": significant_patterns,
                "warning": warning
            }
            
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}", exc_info=True)
            return {
                "circular_detected": False,
                "patterns": [],
                "warning": None
            }
    
    def format_display(self, entries: List[Dict], max_entries: int = 10) -> str:
        """Format entries for human-readable display."""
        if not entries:
            return "No debug log entries yet."
        
        display = ["## Recent Debug Attempts\n"]
        
        for entry in entries[-max_entries:]:
            outcome_icon = {
                "success": "✅",
                "failure": "❌",
                "partial": "⚠️"
            }.get(entry["outcome"], "❓")
            
            display.append(f"**[{entry['ts'][:19]}] {outcome_icon} {entry['component']}**")
            display.append(f"- **Problem:** {entry['problem']}")
            display.append(f"- **Hypothesis:** {entry['hypothesis']}")
            
            if entry.get("actions"):
                actions_str = ", ".join(entry["actions"]) if isinstance(entry["actions"], list) else entry["actions"]
                display.append(f"- **Actions:** {actions_str}")
            
            display.append(f"- **Outcome:** {entry['outcome']}")
            
            if entry.get("notes"):
                display.append(f"- **Notes:** {entry['notes']}")
            
            display.append("")
        
        return "\n".join(display)


def main():
    parser = argparse.ArgumentParser(description="Debug Logger")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Append command
    append_parser = subparsers.add_parser("append", help="Log a debug attempt")
    append_parser.add_argument("--component", required=True, help="Component being debugged")
    append_parser.add_argument("--problem", required=True, help="Problem description")
    append_parser.add_argument("--hypothesis", required=True, help="What we thought was wrong")
    append_parser.add_argument("--actions", required=True, help="Actions taken (comma-separated)")
    append_parser.add_argument("--outcome", required=True, choices=["success", "failure", "partial"])
    append_parser.add_argument("--notes", help="Additional notes")
    append_parser.add_argument("--log-path", help="Custom log file path")
    
    # Recent command
    recent_parser = subparsers.add_parser("recent", help="Show recent entries")
    recent_parser.add_argument("--limit", type=int, default=10, help="Number of entries")
    recent_parser.add_argument("--log-path", help="Custom log file path")
    
    # Patterns command
    patterns_parser = subparsers.add_parser("patterns", help="Detect circular patterns")
    patterns_parser.add_argument("--window", type=int, default=10, help="Window size")
    patterns_parser.add_argument("--threshold", type=int, default=3, help="Pattern threshold")
    patterns_parser.add_argument("--log-path", help="Custom log file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    log_path = Path(args.log_path) if hasattr(args, 'log_path') and args.log_path else None
    debug_log = DebugLogger(log_path)
    
    if args.command == "append":
        actions = [a.strip() for a in args.actions.split(",")]
        entry = debug_log.append(
            component=args.component,
            problem=args.problem,
            hypothesis=args.hypothesis,
            actions=actions,
            outcome=args.outcome,
            notes=args.notes
        )
        print(json.dumps(entry, indent=2))
        return 0
        
    elif args.command == "recent":
        entries = debug_log.recent(args.limit)
        print(debug_log.format_display(entries))
        return 0
        
    elif args.command == "patterns":
        result = debug_log.detect_patterns(args.window, args.threshold)
        if result["warning"]:
            print(result["warning"])
        else:
            print("✓ No circular patterns detected")
        print(json.dumps(result, indent=2))
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

