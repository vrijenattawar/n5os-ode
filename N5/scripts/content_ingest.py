#!/usr/bin/env python3
"""
Content Library Ingest Script
Ingests content files into the N5 Content Library database.

Usage:
    python3 content_ingest.py /path/to/article.md --type article
    python3 content_ingest.py /path/to/file.md --dry-run
    python3 content_ingest.py /path/to/file.md --move

Part of n5OS-Ode: https://github.com/PROJECT_REPO/n5os-ode
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path("/home/workspace")
DB_PATH = WORKSPACE_ROOT / "N5/data/content_library.db"
CANONICAL_ROOT = WORKSPACE_ROOT / "Knowledge/content-library"
LOG_ROOT = WORKSPACE_ROOT / "N5/runtime/runs/content-ingest"

# Content type mappings
TYPE_DIRECTORIES = {
    "article": "articles",
    "deck": "decks",
    "paper": "papers",
    "book": "books",
    "framework": "frameworks",
    "social-post": "social-posts",
    "inspiration": "inspiration",
}

# Path patterns for auto-detection
PATH_TYPE_PATTERNS = [
    (r"/articles/", "article"),
    (r"/decks/", "deck"),
    (r"/papers/", "paper"),
    (r"/books/", "book"),
    (r"/frameworks/", "framework"),
    (r"/social-posts/", "social-post"),
    (r"/inspiration/", "inspiration"),
]


def setup_logging(dry_run: bool = False) -> Path:
    """Create log directory and return log file path."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_ROOT / today
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H%M%S")
    suffix = "_dry-run" if dry_run else ""
    log_file = log_dir / f"ingest_{timestamp}{suffix}.json"
    return log_file


def log_result(log_file: Path, result: dict):
    """Append result to log file."""
    with open(log_file, "a") as f:
        f.write(json.dumps(result) + "\n")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    body = content
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_block = parts[1].strip()
            body = parts[2].strip()
            
            # Simple YAML parsing (key: value)
            for line in yaml_block.split("\n"):
                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if value:
                        frontmatter[key] = value
    
    return frontmatter, body


def extract_title_from_filename(filepath: Path) -> str:
    """Generate title from filename."""
    name = filepath.stem
    # Remove common suffixes like " :: domain.com"
    if " :: " in name:
        name = name.split(" :: ")[0]
    # Clean up
    name = name.replace("-", " ").replace("_", " ")
    return name.strip()


def count_words(content: str) -> int:
    """Count words in text content."""
    # Remove markdown formatting
    text = re.sub(r"[#*`\[\]()>]", " ", content)
    words = text.split()
    return len(words)


def detect_content_type(filepath: Path) -> str:
    """Auto-detect content type from file path."""
    path_str = str(filepath)
    
    for pattern, content_type in PATH_TYPE_PATTERNS:
        if re.search(pattern, path_str, re.IGNORECASE):
            return content_type
    
    # Extension-based fallback
    ext = filepath.suffix.lower()
    if ext == ".pdf":
        return "deck"
    
    return "article"  # Default


def get_relative_path(filepath: Path) -> str:
    """Get path relative to workspace root."""
    try:
        return str(filepath.relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(filepath)


def get_canonical_path(content_type: str, filename: str) -> Path:
    """Get canonical storage path for content type."""
    subdir = TYPE_DIRECTORIES.get(content_type, "articles")
    return CANONICAL_ROOT / subdir / filename


def init_db():
    """Initialize the database schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content_type TEXT NOT NULL,
            source_path TEXT,
            canonical_path TEXT,
            url TEXT,
            author TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            word_count INTEGER DEFAULT 0,
            tags TEXT,
            status TEXT DEFAULT 'active',
            content_hash TEXT
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_type ON content_items(content_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_hash ON content_items(content_hash)
    """)
    
    conn.commit()
    conn.close()


def record_exists(conn: sqlite3.Connection, content_hash: str) -> bool:
    """Check if content with this hash already exists."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM content_items WHERE content_hash = ?", (content_hash,))
    return cursor.fetchone() is not None


def ingest_file(filepath: Path, content_type: str = None, move: bool = False, 
                dry_run: bool = False) -> dict:
    """Ingest a single file into the content library."""
    filepath = filepath.resolve()
    
    if not filepath.exists():
        return {"success": False, "error": f"File not found: {filepath}"}
    
    # Read content
    try:
        content = filepath.read_text()
    except Exception as e:
        return {"success": False, "error": f"Failed to read file: {e}"}
    
    # Parse frontmatter
    frontmatter, body = parse_frontmatter(content)
    
    # Determine content type
    if not content_type:
        content_type = frontmatter.get("type") or detect_content_type(filepath)
    
    # Extract metadata
    title = frontmatter.get("title") or extract_title_from_filename(filepath)
    author = frontmatter.get("author")
    url = frontmatter.get("url") or frontmatter.get("source_url")
    tags = frontmatter.get("tags")
    
    # Calculate hash for deduplication
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    # Word count
    word_count = count_words(body)
    
    # Generate record ID
    record_id = str(uuid.uuid4())[:8]
    
    # Calculate target path
    target_path = get_canonical_path(content_type, filepath.name)
    
    result = {
        "success": True,
        "record_id": record_id,
        "title": title,
        "content_type": content_type,
        "source_path": str(filepath),
        "target_path": str(target_path),
        "word_count": word_count,
        "content_hash": content_hash,
        "dry_run": dry_run,
    }
    
    if dry_run:
        return result
    
    # Initialize DB and check for duplicates
    init_db()
    conn = sqlite3.connect(DB_PATH)
    
    if record_exists(conn, content_hash):
        conn.close()
        result["success"] = False
        result["error"] = "Content already exists (duplicate hash)"
        return result
    
    # Move file if requested
    moved_to = None
    if move:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if not target_path.exists():
            shutil.move(str(filepath), str(target_path))
            moved_to = str(target_path)
            result["moved_to"] = moved_to
    
    # Insert record
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO content_items (id, title, content_type, source_path, canonical_path, 
                                  url, author, word_count, tags, content_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (record_id, title, content_type, str(filepath), 
          moved_to or str(target_path), url, author, word_count, tags, content_hash))
    
    conn.commit()
    conn.close()
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Content Library Ingest")
    parser.add_argument("filepath", type=Path, help="File to ingest")
    parser.add_argument("--type", dest="content_type", 
                        choices=list(TYPE_DIRECTORIES.keys()),
                        help="Content type (auto-detected if not specified)")
    parser.add_argument("--move", action="store_true", 
                        help="Move file to canonical location")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen without making changes")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Minimal output (JSON only)")
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = setup_logging(args.dry_run)
    
    # Ingest file
    result = ingest_file(
        filepath=args.filepath,
        content_type=args.content_type,
        move=args.move,
        dry_run=args.dry_run
    )
    
    # Log result
    log_result(log_file, result)
    
    # Output
    if not args.quiet:
        if not result["success"]:
            print(f"❌ Failed: {result.get('error')}")
        elif args.dry_run:
            print(f"🔍 Would ingest: '{result['title']}'")
            print(f"   Type: {result['content_type']}")
            print(f"   Words: {result['word_count']}")
            print(f"   Would move to: {result['target_path']}")
        else:
            print(f"✅ Ingested: '{result['title']}'")
            print(f"   ID: {result['record_id']}")
            print(f"   Type: {result['content_type']}")
            if result.get("moved_to"):
                print(f"   Moved to: {result['moved_to']}")
    
    # Return result as JSON for programmatic use
    if args.quiet:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
