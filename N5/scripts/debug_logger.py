#!/usr/bin/env python3
"""
Debug Logger - Track problem-solving attempts in build/debug conversations

Principles: P2 (SSOT), P19 (Error Handling), P28 (Fast Feedback)

Usage:
    # Append entry
    python3 debug_logger.py append --component "api.py" --problem "Rate limit 429" \\
        --hypothesis "Add backoff" --actions "Added exponential backoff" \\
        --outcome "success" --notes "5s, 15s, 45s worked"
    
    # Check recent
    python3 debug_logger.py recent --n 5
    
    # Detect patterns
    python3 debug_logger.py patterns --window 10
"""

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, UTC
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


class DebugLogger:
    def __init__(self, convo_id: str):
        self.convo_id = convo_id
        self.workspace = Path(f"/home/.z/workspaces/{convo_id}")
        self.log_file = self.workspace / "DEBUG_LOG.jsonl"
        
        self.workspace.mkdir(parents=True, exist_ok=True)
    
    def append(
        self,
        component: str,
        problem: str,
        hypothesis: str,
        actions: List[str],
        outcome: str,
        notes: str = ""
    ) -> Dict:
        """Append debug entry to log."""
        try:
            if outcome not in ["success", "failure", "partial"]:
                raise ValueError(f"Invalid outcome: {outcome}. Must be success|failure|partial")
            
            entry = {
                "ts": datetime.now(UTC).isoformat(),
                "entry_id": str(uuid.uuid4())[:8],
                "component": component,
                "problem": problem,
                "hypothesis": hypothesis,
                "actions": actions if isinstance(actions, list) else [actions],
                "outcome": outcome,
                "notes": notes,
                "conv_id": self.convo_id
            }
            
            with self.log_file.open("a") as f:
                f.write(json.dumps(entry) + "\n")
            
            logger.info(f"✓ Logged {outcome} for {component}: {problem[:50]}...")
            return entry
            
        except Exception as e:
            logger.error(f"Failed to append debug entry: {e}", exc_info=True)
            raise
    
    def read_all(self) -> List[Dict]:
        """Read all entries from log."""
        try:
            if not self.log_file.exists():
                return []
            
            entries = []
            with self.log_file.open() as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to read debug log: {e}", exc_info=True)
            return []
    
    def recent(self, n: int = 5) -> List[Dict]:
        """Get last N entries."""
        entries = self.read_all()
        return entries[-n:] if entries else []
    
    @staticmethod
    def _similarity(s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings."""
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    
    @staticmethod
    def _shared_keywords(s1: str, s2: str, min_length: int = 4) -> float:
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
                    f"→ Consider: Different approach, load Debugger mode, or ask V for guidance"
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
    parser = argparse.ArgumentParser(description="Debug Logger for build/debug conversations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Append command
    append_parser = subparsers.add_parser("append", help="Add debug entry")
    append_parser.add_argument("--convo-id", required=True, help="Conversation ID")
    append_parser.add_argument("--component", required=True, help="Component/file being worked on")
    append_parser.add_argument("--problem", required=True, help="Problem description")
    append_parser.add_argument("--hypothesis", required=True, help="Hypothesis for fix")
    append_parser.add_argument("--actions", required=True, nargs="+", help="Actions taken")
    append_parser.add_argument("--outcome", required=True, choices=["success", "failure", "partial"])
    append_parser.add_argument("--notes", default="", help="Additional notes")
    
    # Recent command
    recent_parser = subparsers.add_parser("recent", help="Show recent entries")
    recent_parser.add_argument("--convo-id", required=True)
    recent_parser.add_argument("--n", type=int, default=5, help="Number of entries")
    recent_parser.add_argument("--format", choices=["json", "display"], default="display")
    
    # Patterns command
    patterns_parser = subparsers.add_parser("patterns", help="Detect circular patterns")
    patterns_parser.add_argument("--convo-id", required=True)
    patterns_parser.add_argument("--window", type=int, default=10, help="Window size")
    patterns_parser.add_argument("--threshold", type=int, default=3, help="Pattern threshold")
    
    args = parser.parse_args()
    
    logger = DebugLogger(args.convo_id)
    
    if args.command == "append":
        logger.append(
            component=args.component,
            problem=args.problem,
            hypothesis=args.hypothesis,
            actions=args.actions,
            outcome=args.outcome,
            notes=args.notes
        )
    
    elif args.command == "recent":
        entries = logger.recent(args.n)
        if args.format == "json":
            print(json.dumps(entries, indent=2))
        else:
            print(logger.format_display(entries))
    
    elif args.command == "patterns":
        result = logger.detect_patterns(window=args.window, threshold=args.threshold)
        if result["warning"]:
            print(result["warning"])
        else:
            print("✓ No circular patterns detected")
        print(f"\nPatterns found: {len(result['patterns'])}")
        if result["patterns"]:
            print(json.dumps(result["patterns"], indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
