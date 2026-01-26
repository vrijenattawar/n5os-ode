#!/usr/bin/env python3
"""
Meeting Ingestion - Pull Script

Downloads transcripts from Google Drive to the meeting staging area.
Uses Zo API for Google Drive access to leverage authenticated connections.

Usage:
    python3 pull.py [--dry-run] [--batch-size N]
"""

import os
import sys
import json
import yaml
import argparse
import logging
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, UTC

# Add N5/scripts to path for imports
import os
WORKSPACE = Path(os.environ.get("ZO_WORKSPACE", "/home/workspace"))
sys.path.insert(0, str(WORKSPACE / "N5/scripts"))

from meeting_registry import MeetingRegistry
from meeting_normalizer import normalize_date, normalize_participants, generate_meeting_id
from meeting_config import STAGING_PATH, LOG_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
CONFIG_PATH = WORKSPACE / "N5/config/drive_locations.yaml"
STAGING_DIR = Path(STAGING_PATH)
LOG_DIR = Path(LOG_PATH)


def load_drive_config() -> dict:
    """Load Google Drive folder configuration."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Drive config not found: {CONFIG_PATH}")
    
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    
    return config


def call_zo_api(prompt: str) -> dict:
    """
    Call Zo API to execute a task.
    Returns parsed JSON response.
    """
    import requests
    
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json"
        },
        json={
            "input": prompt,
            "output_format": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "mimeType": {"type": "string"},
                                "createdTime": {"type": "string"}
                            }
                        }
                    },
                    "error": {"type": "string"}
                },
                "required": ["success"]
            }
        },
        timeout=120
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Zo API error: {response.status_code} - {response.text}")
    
    return response.json().get("output", {})


def list_drive_files(folder_id: str) -> list:
    """
    List files in Google Drive folder via Zo API.
    Returns list of file metadata dicts.
    """
    prompt = f"""List all files in Google Drive folder with ID: {folder_id}

Use use_app_google_drive with list-files-in-folder tool.

Return a JSON response with:
- success: true/false
- files: array of file objects with id, name, mimeType, createdTime
- error: error message if failed

IMPORTANT: Return ONLY the JSON object, no additional text."""

    result = call_zo_api(prompt)
    
    if not result.get("success"):
        error = result.get("error", "Unknown error")
        raise RuntimeError(f"Failed to list Drive files: {error}")
    
    return result.get("files", [])


def download_drive_file(file_id: str, file_name: str, dest_path: Path) -> Path:
    """
    Download a file from Google Drive via Zo API.
    Returns path to downloaded file.
    """
    prompt = f"""Download file from Google Drive:
- File ID: {file_id}
- File name: {file_name}
- Save to: {dest_path}

Use use_app_google_drive with download-file tool.

If the file is a Google Doc, export it as text/plain or application/vnd.openxmlformats-officedocument.wordprocessingml.document.

After download, confirm the file exists at the destination path.

Return JSON:
- success: true/false
- downloaded_path: actual path where file was saved
- error: error message if failed"""

    result = call_zo_api(prompt)
    
    if not result.get("success"):
        error = result.get("error", "Unknown error")
        raise RuntimeError(f"Failed to download {file_name}: {error}")
    
    downloaded = Path(result.get("downloaded_path", dest_path))
    if not downloaded.exists():
        raise FileNotFoundError(f"Download claimed success but file not found: {downloaded}")
    
    return downloaded


def convert_to_markdown(source_path: Path) -> Path:
    """
    Convert document to markdown using pandoc.
    Returns path to converted file.
    """
    output_path = source_path.with_suffix(".md")
    
    cmd = [
        "pandoc",
        "-f", "docx",
        "-t", "markdown",
        "-o", str(output_path),
        str(source_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc conversion failed: {result.stderr}")
    
    # Validate output
    if not output_path.exists():
        raise FileNotFoundError(f"Conversion output not found: {output_path}")
    
    if output_path.stat().st_size == 0:
        raise ValueError(f"Conversion produced empty file: {output_path}")
    
    return output_path


def extract_meeting_metadata(file_name: str) -> dict:
    """
    Extract date and participants from filename.
    
    Expected formats:
    - "2025-01-15 Meeting with John Smith.docx"
    - "UserOne_UserTwo_2025-01-15.docx"
    - "Meeting_2025-01-15_Participants.docx"
    """
    import re
    
    # Try to extract date
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',  # 2025-01-15
        r'(\d{4}\d{2}\d{2})',     # 20250115
        r'(\d{2}/\d{2}/\d{4})',   # 01/15/2025
    ]
    
    date = None
    for pattern in date_patterns:
        match = re.search(pattern, file_name)
        if match:
            try:
                date = normalize_date(match.group(1))
                break
            except ValueError:
                continue
    
    # Extract potential participant names
    # Remove date, extension, common prefixes
    name_part = file_name
    name_part = re.sub(r'\d{4}[-/]?\d{2}[-/]?\d{2}', '', name_part)
    name_part = re.sub(r'\.(docx|txt|md|doc)$', '', name_part, flags=re.IGNORECASE)
    name_part = re.sub(r'^(Meeting|Call|Sync|Notes?)[\s_-]*', '', name_part, flags=re.IGNORECASE)
    name_part = re.sub(r'[\s_-]*(Meeting|Call|Sync|Notes?)$', '', name_part, flags=re.IGNORECASE)
    
    # Split on common separators and filter
    potential_names = re.split(r'[_\-\s]+', name_part)
    participants = [n.strip() for n in potential_names if len(n.strip()) > 2]
    
    return {
        "date": date,
        "participants": participants,
        "original_filename": file_name
    }


def pull_transcripts(
    dry_run: bool = False,
    batch_size: int = 5
) -> dict:
    """
    Main pull function.
    
    Returns:
        dict with keys: ingested, skipped, errors
    """
    logger.info(f"Starting transcript pull (dry_run={dry_run}, batch_size={batch_size})")
    
    # Load config
    config = load_drive_config()
    folder_id = config.get("meetings", {}).get("transcripts_inbox")
    
    if not folder_id:
        raise ValueError("meetings.transcripts_inbox not configured in drive_locations.yaml")
    
    logger.info(f"Drive folder ID: {folder_id}")
    
    # Initialize registry
    registry = MeetingRegistry()
    
    # List files in Drive
    logger.info("Listing files in Drive folder...")
    files = list_drive_files(folder_id)
    logger.info(f"Found {len(files)} files in Drive")
    
    # Filter to supported types
    supported_types = [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.google-apps.document",  # Google Doc
        "text/plain",  # .txt
        "text/markdown"  # .md
    ]
    
    files = [f for f in files if f.get("mimeType") in supported_types]
    logger.info(f"{len(files)} files are supported transcript formats")
    
    # Ensure staging dir exists
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {
        "ingested": [],
        "skipped": [],
        "errors": []
    }
    
    processed = 0
    for file_info in files:
        if processed >= batch_size:
            logger.info(f"Reached batch size limit ({batch_size})")
            break
        
        file_id = file_info.get("id")
        file_name = file_info.get("name")
        
        logger.info(f"Processing: {file_name}")
        
        try:
            # Check if already in registry
            existing = registry.get_meeting_by_gdrive_id(file_id) if hasattr(registry, 'get_meeting_by_gdrive_id') else None
            if existing:
                logger.info(f"  Skipped: already in registry")
                results["skipped"].append({
                    "file": file_name,
                    "reason": "already_processed"
                })
                continue
            
            # Extract metadata
            metadata = extract_meeting_metadata(file_name)
            
            if dry_run:
                logger.info(f"  Would ingest: {file_name}")
                logger.info(f"    Date: {metadata.get('date', 'unknown')}")
                logger.info(f"    Participants: {metadata.get('participants', [])}")
                results["ingested"].append({
                    "file": file_name,
                    "metadata": metadata,
                    "dry_run": True
                })
                processed += 1
                continue
            
            # Download file
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir) / file_name
                logger.info(f"  Downloading to: {tmp_path}")
                downloaded = download_drive_file(file_id, file_name, tmp_path)
                
                # Convert to markdown if needed
                if downloaded.suffix.lower() in [".docx", ".doc"]:
                    logger.info("  Converting to markdown...")
                    markdown_path = convert_to_markdown(downloaded)
                else:
                    markdown_path = downloaded
                
                # Generate destination filename
                date = metadata.get("date") or datetime.now(UTC).strftime("%Y-%m-%d")
                safe_name = file_name.replace(" ", "_")
                dest_name = f"{date}_{safe_name}"
                if not dest_name.endswith(".md"):
                    dest_name = Path(dest_name).stem + ".md"
                
                dest_path = STAGING_DIR / dest_name
                
                # Copy to staging
                import shutil
                shutil.copy2(markdown_path, dest_path)
                logger.info(f"  Staged: {dest_path}")
            
            results["ingested"].append({
                "file": file_name,
                "dest": str(dest_path),
                "metadata": metadata
            })
            processed += 1
            
        except Exception as e:
            logger.error(f"  Error: {e}")
            results["errors"].append({
                "file": file_name,
                "error": str(e)
            })
    
    # Summary
    logger.info(f"Pull complete: {len(results['ingested'])} ingested, {len(results['skipped'])} skipped, {len(results['errors'])} errors")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Pull meeting transcripts from Google Drive"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files without downloading"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Maximum files to process (default: 5)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        results = pull_transcripts(
            dry_run=args.dry_run,
            batch_size=args.batch_size
        )
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nResults:")
            print(f"  Ingested: {len(results['ingested'])}")
            print(f"  Skipped:  {len(results['skipped'])}")
            print(f"  Errors:   {len(results['errors'])}")
            
            if results['errors']:
                print("\nErrors:")
                for err in results['errors']:
                    print(f"  - {err['file']}: {err['error']}")
        
        return 0 if not results['errors'] else 1
        
    except Exception as e:
        logger.error(f"Pull failed: {e}")
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
