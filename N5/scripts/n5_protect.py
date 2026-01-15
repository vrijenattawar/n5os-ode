#!/usr/bin/env python3
"""
N5 File Protection System - Lightweight directory protection via marker files

Usage:
    n5_protect.py protect <path> --reason "description" [--pii] [--pii-categories email,phone]
    n5_protect.py unprotect <path>
    n5_protect.py list
    n5_protect.py list-pii
    n5_protect.py check <path>
    n5_protect.py mark-pii <path> --categories email,phone [--note "description"]

Part of n5OS-Ode: https://github.com/vrijenattawar/n5os-ode
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

MARKER_FILENAME = ".n5protected"
WORKSPACE = Path("/home/workspace")
VALID_PII_CATEGORIES = {"email", "phone", "name", "health", "financial", "ssn", "address", "dob"}


def create_marker(directory: Path, reason: str, metadata: Optional[dict] = None,
                  contains_pii: bool = False, pii_categories: Optional[list] = None,
                  pii_note: Optional[str] = None) -> bool:
    """Create .n5protected marker file in directory"""
    try:
        directory = directory.resolve()
        if not directory.is_dir():
            logger.error(f"Not a directory: {directory}")
            return False
        
        marker_path = directory / MARKER_FILENAME
        
        if marker_path.exists():
            logger.warning(f"Already protected: {directory}")
            return True
        
        marker_data = {
            "protected": True,
            "reason": reason,
            "created": datetime.now(timezone.utc).isoformat(),
            "created_by": metadata.get("created_by", "user") if metadata else "user"
        }
        
        # Add PII tracking fields
        if contains_pii:
            marker_data["contains_pii"] = True
            marker_data["pii_categories"] = pii_categories or []
            if pii_note:
                marker_data["pii_note"] = pii_note
        
        # Add optional metadata
        if metadata:
            for key, value in metadata.items():
                if key not in marker_data:
                    marker_data[key] = value
        
        marker_path.write_text(json.dumps(marker_data, indent=2) + "\n")
        pii_msg = f" [PII: {', '.join(pii_categories or [])}]" if contains_pii else ""
        logger.info(f"✓ Protected: {directory} (reason: {reason}){pii_msg}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to protect {directory}: {e}", exc_info=True)
        return False


def remove_marker(directory: Path) -> bool:
    """Remove .n5protected marker file from directory"""
    try:
        directory = directory.resolve()
        marker_path = directory / MARKER_FILENAME
        
        if not marker_path.exists():
            logger.warning(f"Not protected: {directory}")
            return False
        
        marker_path.unlink()
        logger.info(f"✓ Unprotected: {directory}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to unprotect {directory}: {e}", exc_info=True)
        return False


def check_protected(path: Path) -> Optional[dict]:
    """
    Check if path or any parent directory is protected.
    Returns marker data if protected, None otherwise.
    """
    try:
        path = path.resolve()
        
        # Check path itself if directory
        if path.is_dir():
            marker = path / MARKER_FILENAME
            if marker.exists():
                return json.loads(marker.read_text())
        
        # Check all parent directories
        for parent in path.parents:
            marker = parent / MARKER_FILENAME
            if marker.exists():
                return json.loads(marker.read_text())
            
            # Stop at workspace root
            if parent == WORKSPACE:
                break
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to check protection for {path}: {e}", exc_info=True)
        return None


def list_protected() -> list[tuple[Path, dict]]:
    """Find all protected directories in workspace"""
    protected_dirs = []
    
    try:
        for marker_path in WORKSPACE.rglob(MARKER_FILENAME):
            directory = marker_path.parent
            try:
                marker_data = json.loads(marker_path.read_text())
                protected_dirs.append((directory, marker_data))
            except Exception as e:
                logger.warning(f"Invalid marker at {marker_path}: {e}")
        
        return protected_dirs
        
    except Exception as e:
        logger.error(f"Failed to list protected directories: {e}", exc_info=True)
        return []


def list_pii_paths() -> list[tuple[Path, dict]]:
    """Find all directories marked as containing PII"""
    pii_dirs = []
    
    try:
        for marker_path in WORKSPACE.rglob(MARKER_FILENAME):
            directory = marker_path.parent
            try:
                marker_data = json.loads(marker_path.read_text())
                if marker_data.get("contains_pii"):
                    pii_dirs.append((directory, marker_data))
            except Exception as e:
                logger.warning(f"Invalid marker at {marker_path}: {e}")
        
        return pii_dirs
        
    except Exception as e:
        logger.error(f"Failed to list PII directories: {e}", exc_info=True)
        return []


def mark_pii(directory: Path, categories: list[str], note: Optional[str] = None) -> bool:
    """Add PII flags to an existing .n5protected marker"""
    try:
        directory = directory.resolve()
        marker_path = directory / MARKER_FILENAME
        
        if not marker_path.exists():
            logger.error(f"Not protected: {directory}. Use 'protect' first.")
            return False
        
        # Validate categories
        invalid = set(categories) - VALID_PII_CATEGORIES
        if invalid:
            logger.error(f"Invalid PII categories: {invalid}. Valid: {VALID_PII_CATEGORIES}")
            return False
        
        marker_data = json.loads(marker_path.read_text())
        marker_data["contains_pii"] = True
        marker_data["pii_categories"] = categories
        marker_data["pii_marked_at"] = datetime.now(timezone.utc).isoformat()
        if note:
            marker_data["pii_note"] = note
        
        marker_path.write_text(json.dumps(marker_data, indent=2) + "\n")
        logger.info(f"✓ Marked PII: {directory} [{', '.join(categories)}]")
        return True
        
    except Exception as e:
        logger.error(f"Failed to mark PII for {directory}: {e}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="N5 File Protection System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Protect command
    protect_parser = subparsers.add_parser("protect", help="Protect a directory")
    protect_parser.add_argument("path", type=Path, help="Directory to protect")
    protect_parser.add_argument("--reason", required=True, help="Reason for protection")
    protect_parser.add_argument("--pii", action="store_true", help="Mark as containing PII")
    protect_parser.add_argument("--pii-categories", help="Comma-separated PII categories")
    
    # Unprotect command
    unprotect_parser = subparsers.add_parser("unprotect", help="Remove protection")
    unprotect_parser.add_argument("path", type=Path, help="Directory to unprotect")
    
    # List command
    subparsers.add_parser("list", help="List protected directories")
    
    # List PII command
    subparsers.add_parser("list-pii", help="List directories with PII")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if path is protected")
    check_parser.add_argument("path", type=Path, help="Path to check")
    
    # Mark PII command
    pii_parser = subparsers.add_parser("mark-pii", help="Add PII flags to protected directory")
    pii_parser.add_argument("path", type=Path, help="Protected directory")
    pii_parser.add_argument("--categories", required=True, help="Comma-separated categories")
    pii_parser.add_argument("--note", help="Additional note about PII")
    
    args = parser.parse_args()
    
    try:
        if args.command == "protect":
            pii_cats = args.pii_categories.split(",") if args.pii_categories else None
            return 0 if create_marker(args.path, args.reason, 
                                     contains_pii=args.pii, pii_categories=pii_cats) else 1
            
        elif args.command == "unprotect":
            return 0 if remove_marker(args.path) else 1
            
        elif args.command == "list":
            protected = list_protected()
            if not protected:
                print("No protected directories found.")
                return 0
            
            print(f"\n{'='*60}")
            print("PROTECTED DIRECTORIES")
            print(f"{'='*60}")
            for directory, marker_data in sorted(protected, key=lambda x: str(x[0])):
                rel_path = directory.relative_to(WORKSPACE) if directory.is_relative_to(WORKSPACE) else directory
                pii_flag = " [PII]" if marker_data.get("contains_pii") else ""
                print(f"\n📁 {rel_path}{pii_flag}")
                print(f"   Reason: {marker_data.get('reason', 'N/A')}")
                print(f"   Created: {marker_data.get('created', 'N/A')[:10]}")
            print(f"\nTotal: {len(protected)} protected directories")
            return 0
            
        elif args.command == "list-pii":
            pii_dirs = list_pii_paths()
            if not pii_dirs:
                print("No PII directories found.")
                return 0
            
            print(f"\n{'='*60}")
            print("DIRECTORIES CONTAINING PII")
            print(f"{'='*60}")
            for directory, marker_data in sorted(pii_dirs, key=lambda x: str(x[0])):
                rel_path = directory.relative_to(WORKSPACE) if directory.is_relative_to(WORKSPACE) else directory
                cats = ", ".join(marker_data.get("pii_categories", []))
                print(f"\n⚠️  {rel_path}")
                print(f"   Categories: {cats}")
                if marker_data.get("pii_note"):
                    print(f"   Note: {marker_data['pii_note']}")
            print(f"\nTotal: {len(pii_dirs)} PII directories")
            return 0
            
        elif args.command == "check":
            result = check_protected(args.path)
            if result:
                pii_msg = " [CONTAINS PII]" if result.get("contains_pii") else ""
                print(f"⚠️  This path is protected{pii_msg}")
                print(f"   Reason: {result.get('reason', 'N/A')}")
                return 0
            else:
                print("✓ Path is not protected")
                return 0
            
        elif args.command == "mark-pii":
            categories = args.categories.split(",")
            return 0 if mark_pii(args.path, categories, args.note) else 1
            
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

