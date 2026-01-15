#!/usr/bin/env python3
"""
Safety checks for destructive operations.

Usage:
  python3 N5/scripts/n5_safety.py check <path>
  python3 N5/scripts/n5_safety.py scan
"""
import sys
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description="Safety checks for operations")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    check_sub = subparsers.add_parser("check", help="Check a path for safety")
    check_sub.add_argument("path", help="Path to check")
    
    subparsers.add_parser("scan", help="Scan workspace for safety issues")
    
    args = parser.parse_args()
    
    if args.command == "check":
        path = Path(args.path)
        
        # Check for .n5protected
        protected_file = path / ".n5protected" if path.is_dir() else path.parent / ".n5protected"
        
        if protected_file.exists():
            reason = protected_file.read_text().strip() if protected_file.read_text().strip() else "Protected"
            print(f"⚠️  PROTECTED: {path}")
            print(f"   Reason: {reason}")
            return 1
        
        print(f"✅ Not protected: {path}")
        return 0
    
    elif args.command == "scan":
        print("🔍 Scanning for safety issues...")
        print("   (In a full system, this would check for unintended deletions)")
        return 0
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())

