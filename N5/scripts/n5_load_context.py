#!/usr/bin/env python3
"""
N5 Load Context Utility
Restores the "missing link" between intent and standards.
Loads context bundles based on task type defined in N5/prefs/context_manifest.yaml

Usage:
    python3 n5_load_context.py build
    python3 n5_load_context.py strategy
    python3 n5_load_context.py "custom task description"

Part of n5OS-Ode: https://github.com/vrijenattawar/n5os-ode
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Optional

# Base paths
WORKSPACE = Path("/home/workspace")
MANIFEST_PATH = WORKSPACE / "N5/prefs/context_manifest.yaml"


def load_manifest() -> Dict:
    """Load context manifest configuration."""
    if not MANIFEST_PATH.exists():
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)
    
    with open(MANIFEST_PATH, 'r') as f:
        return yaml.safe_load(f)


def read_file(path_str: str) -> str:
    """Safely reads a file and returns formatted markdown block."""
    path = WORKSPACE / path_str
    if not path.exists():
        return f"<!-- MISSING FILE: {path} -->"
    
    try:
        with open(path, 'r') as f:
            content = f.read()
            return f"\n\n<!-- FILE: {path_str} -->\n{content}\n<!-- END FILE -->\n"
    except Exception as e:
        return f"<!-- ERROR READING {path}: {e} -->"


def determine_group_from_intent(intent: str, groups: Dict) -> str:
    """
    Dynamic Logic: Maps natural language intent to a context group.
    Uses keyword matching.
    """
    intent = intent.lower()
    
    # Keyword Mappings
    keywords = {
        "build": ["code", "fix", "bug", "implement", "refactor", "script", "python", "error"],
        "strategy": ["plan", "think", "reason", "design", "approach", "why", "architect"],
        "system": ["database", "list", "index", "schema", "ops", "organize"],
        "safety": ["delete", "move", "remove", "dangerous", "destroy"],
        "scheduler": ["schedule", "agent", "automate", "cron", "recurring", "timer"],
        "writer": ["write", "draft", "email", "communicate", "content", "letter", "message"],
        "research": ["research", "deep dive", "analyze", "investigate", "study"],
    }
    
    # Score each group
    scores = {group: 0 for group in keywords}
    for group, kws in keywords.items():
        for kw in kws:
            if kw in intent:
                scores[group] += 1
    
    # Find best match
    best_group = max(scores, key=scores.get)
    if scores[best_group] == 0:
        return "build"  # Default fallback
    
    return best_group


def load_context(category: str, manifest: Dict = None) -> str:
    """Load context files for a given category."""
    if manifest is None:
        manifest = load_manifest()
    
    groups = manifest.get("groups", {})
    
    # Check if category is a known group
    if category in groups:
        group = groups[category]
    else:
        # Try to infer from intent
        inferred = determine_group_from_intent(category, groups)
        if inferred in groups:
            print(f"Inferred context group: {inferred}")
            group = groups[inferred]
        else:
            print(f"Warning: Unknown category '{category}', using minimal context")
            return ""
    
    # Load files
    files = group.get("files", [])
    output_parts = []
    
    output_parts.append(f"## Context: {category}")
    if group.get("description"):
        output_parts.append(f"*{group['description']}*\n")
    
    loaded_count = 0
    for file_path in files:
        content = read_file(file_path)
        if "MISSING FILE" not in content and "ERROR READING" not in content:
            output_parts.append(content)
            loaded_count += 1
        else:
            output_parts.append(content)  # Include error message
    
    output_parts.append(f"\n<!-- Loaded {loaded_count}/{len(files)} context files -->")
    
    return "\n".join(output_parts)


def list_groups(manifest: Dict = None) -> None:
    """List all available context groups."""
    if manifest is None:
        manifest = load_manifest()
    
    groups = manifest.get("groups", {})
    
    print("\nAvailable Context Groups:")
    print("=" * 50)
    for name, group in sorted(groups.items()):
        desc = group.get("description", "No description")
        files = group.get("files", [])
        print(f"\n  {name}")
        print(f"    {desc}")
        print(f"    Files: {len(files)}")


def main():
    parser = argparse.ArgumentParser(
        description="Load context files for specific task types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 n5_load_context.py build          # Load build context
    python3 n5_load_context.py strategy       # Load strategy context
    python3 n5_load_context.py --list         # List available groups
    python3 n5_load_context.py "fix this bug" # Infer from description
        """
    )
    
    parser.add_argument("category", nargs="?", help="Context category or task description")
    parser.add_argument("--list", "-l", action="store_true", help="List available context groups")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress info messages")
    
    args = parser.parse_args()
    
    manifest = load_manifest()
    
    if args.list:
        list_groups(manifest)
        return 0
    
    if not args.category:
        parser.print_help()
        return 1
    
    context = load_context(args.category, manifest)
    print(context)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

