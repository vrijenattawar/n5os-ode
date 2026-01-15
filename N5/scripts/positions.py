#!/usr/bin/env python3
"""
Positions database manager (minimal implementation for n5OS-Ode).

Commands:
  python3 N5/scripts/positions.py list           - List all positions
  python3 N5/scripts/positions.py audit          - Audit position consistency
  python3 N5/scripts/positions.py check-overlap <text> [--threshold 0.4]
"""
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Positions database manager")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    subparsers.add_parser("list", help="List all positions")
    subparsers.add_parser("audit", help="Audit positions")
    
    check_sub = subparsers.add_parser("check-overlap", help="Check text overlap with positions")
    check_sub.add_argument("text", help="Text to check")
    check_sub.add_argument("--threshold", type=float, default=0.4, help="Similarity threshold")
    
    args = parser.parse_args()
    
    root = Path(__file__).parent.parent.parent
    positions_file = root / "Knowledge" / "positions.md"
    
    if args.command == "list":
        if positions_file.exists():
            print(f"📋 Positions stored in: {positions_file}")
            print(positions_file.read_text())
        else:
            print("ℹ️  No positions file yet. Create one at: Knowledge/positions.md")
        return 0
    
    elif args.command == "audit":
        if positions_file.exists():
            print(f"✅ Positions audit: {positions_file}")
            lines = positions_file.read_text().split('\n')
            print(f"   Lines: {len(lines)}")
        else:
            print("⚠️  No positions file found at: Knowledge/positions.md")
        return 0
    
    elif args.command == "check-overlap":
        # Minimal overlap check — in a full system, this would use semantic similarity
        print(f"🔍 Checking overlap for text (threshold={args.threshold}):")
        print(f"   '{args.text[:60]}...'")
        print()
        
        if positions_file.exists():
            content = positions_file.read_text()
            # Very basic: just check if text substring exists
            if args.text in content:
                print("⚠️  Potential match found in existing positions")
                print("   Recommendation: EXTEND existing position")
                return 0
        
        print("✅ No overlap detected")
        print("   Recommendation: CREATE new position")
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())

