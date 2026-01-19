"""
N5 Load Context Utility
Restores the "missing link" between intent and standards.
Loads context bundles based on task type defined in N5/prefs/prefs.md.
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Optional
# Import N5 Memory Client (Hybrid Integration)
# We assume N5 is in the path or relative.
try:
    ROOT = Path(__file__).resolve().parents[2]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from N5.cognition.n5_memory_client import N5MemoryClient
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False


# Base paths - resolve relative to script location for portability
# When installed: ROOT is /home/workspace, when in repo: ROOT is repo root
ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = Path(os.environ.get("N5_WORKSPACE", ROOT))
MANIFEST_PATH = WORKSPACE / "N5/prefs/context_manifest.yaml"

def load_manifest() -> Dict:
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
def search_memory(query: str, limit: int = 3) -> str:
    """Query the N5 Brain for semantic context."""
    if not MEMORY_AVAILABLE:
        return "<!-- Memory Client Not Available -->"
    
    try:
        client = N5MemoryClient()
        # Only search if we have a real query, not just a mode keyword
        if len(query.split()) < 2:
            return "" 
            
        results = client.search(query, limit=limit)
        if not results:
            return ""
            
        output = ["\n<memory_context>"]
        output.append(f"  <!-- Retrieved {len(results)} relevant blocks for '{query}' -->")
        for res in results:
            path = res.get('path', 'unknown')
            lines = res.get('lines')
            if isinstance(lines, (list, tuple)) and len(lines) == 2:
                start, end = lines
            else:
                start = res.get('start_line', 0)
                end = res.get('end_line', 0)

            if start and end:
                source = f"{path}:{start}-{end}"
            else:
                source = path

            score = res.get('score', res.get('similarity', 0.0))
            output.append(f"  <block source='{source}' score='{score:.2f}'>")
            output.append(res.get('content', ''))
            output.append("  </block>")
        output.append("</memory_context>\n")
        return "\n".join(output)
        
    except Exception as e:
        return f"<!-- Memory Search Error: {e} -->"


def determine_group_from_intent(intent: str, groups: Dict) -> str:
    """
    Dynamic Logic: Maps natural language intent to a context group.
    Uses keyword matching (Simple Over Easy).
    """
    intent = intent.lower()
    
    # Keyword Mappings
    keywords = {
        "build": ["code", "fix", "bug", "implement", "refactor", "script", "python", "error"],
        "strategy": ["plan", "think", "reason", "design", "approach", "why", "architect"],
        "scheduler": ["agent", "schedule", "task", "automation", "cron", "run"],
        "system": ["list", "index", "db", "database", "ops", "admin"],
        "safety": ["delete", "remove", "clean", "purge", "destroy"],
        "writer": ["email", "write", "draft", "post", "message", "content", "blog", "article"],
        "research": ["research", "find", "look up", "investigate", "search", "analyze"]
    }
    
    # Check against manifest groups
    for group_name, terms in keywords.items():
        if group_name in groups: # Only match if group exists in manifest
            for term in terms:
                if term in intent:
                    return group_name
                    
    return "general" # Default to general if no match found

def main():
    parser = argparse.ArgumentParser(description="N5 Dynamic Context Loader")
    parser.add_argument("input", nargs='?', help="Mode name (e.g., 'build') or Intent string (e.g., 'fix the script'). Use --list to see available modes.")
    parser.add_argument("--list", action="store_true", help="List all available context groups")
    args = parser.parse_args()

    manifest = load_manifest()
    groups = manifest.get("groups", {})
    
    # Handle --list option
    if args.list:
        print("\n=== Available Context Groups ===\n")
        for name, config in groups.items():
            desc = config.get("description", "No description")
            file_count = len(config.get("files", []))
            print(f"  {name:15} - {desc} ({file_count} files)")
        print()
        return
    
    # Ensure input is provided for normal operation
    if not args.input:
        parser.print_help()
        sys.exit(1)

    target_group = None
    is_fallback = False
    
    # 1. Check if input is a direct mode match
    if args.input in groups:
        target_group = args.input
        print(f"> **Context Loader:** Mode `{target_group}` detected.")
        
    # 2. Check if input is an intent (Dynamic Mode)
    else:
        target_group = determine_group_from_intent(args.input, groups)
        if target_group == "general":
             is_fallback = True
             print(f"> **Context Loader:** Novel context detected (intent: `{args.input}`).")
             print(f"> **Action:** Loading `general` context. Consider defining a new category for this workflow.")
        else:
             print(f"> **Context Loader:** Intent `{args.input}` mapped to mode `{target_group}`.")

    # 3. Load Content
    if target_group not in groups:
         print(f"Error: Target group `{target_group}` not found in manifest.")
         return

    files_to_load = groups[target_group]["files"]
    
    output = []
    output.append(f"> **N5 Context Injection**")
    output.append(f"> Target: `{target_group}`")
    output.append(f"> Injecting {len(files_to_load)} context files...")
    
    print("\n".join(output))
    
    for file_path in files_to_load:
        print(read_file(file_path))
    
    # 4. Inject Memory (Hybrid Layer)
    # We query the brain using the original input intent
    memory_block = search_memory(args.input)
    if memory_block:
        print(memory_block)
        print(f"> **Context Loader:** Injected semantic memory.")
        
    print(f"\n> **Context Loaded.** System ready for `{target_group}` operations.")

if __name__ == "__main__":
    main()





