#!/usr/bin/env python3
"""
Content Library Query Script
Query and search the Content Library including media files.

Part of Content Library Media Extension build (Worker 3)

Usage:
    python3 content_query.py [--type TYPE] [--tag TAG] [--search TERM] [--limit N]
"""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/home/workspace/N5/data/content_library.db")


def format_duration(seconds: int | None) -> str:
    """Format duration in human-readable form."""
    if seconds is None:
        return "-"
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def query_items(
    content_type: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    limit: int = 20,
    include_deprecated: bool = False,
    output_format: str = "table"
) -> list[dict]:
    """
    Query items from the Content Library.
    
    Args:
        content_type: Filter by content_type (article, audio, video, image, etc.)
        tag: Filter by tag (needs-transcription, transcribed, etc.)
        search: Search in title and content
        limit: Max results
        include_deprecated: Include deprecated items
        output_format: 'table', 'json', or 'brief'
    
    Returns:
        List of matching items
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    conditions = []
    params = []
    
    if not include_deprecated:
        conditions.append("deprecated = 0")
    
    if content_type:
        conditions.append("content_type = ?")
        params.append(content_type)
    
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f'%"{tag}"%')
    
    if search:
        conditions.append("(title LIKE ? OR content LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT id, title, content_type, tags, created_at, updated_at,
               file_path, mime_type, duration_seconds, dimensions,
               transcript_path, source_file_path, url
        FROM items
        WHERE {where_clause}
        ORDER BY updated_at DESC
        LIMIT ?
    """
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for row in rows:
        item = dict(row)
        # Parse tags JSON
        if item.get("tags"):
            try:
                item["tags"] = json.loads(item["tags"])
            except:
                item["tags"] = []
        items.append(item)
    
    return items


def print_table(items: list[dict]):
    """Print items as a formatted table."""
    if not items:
        print("No items found.")
        return
    
    # Header
    print(f"{'Title':<40} {'Type':<8} {'Duration':<10} {'Tags':<25}")
    print("-" * 90)
    
    for item in items:
        title = item["title"][:38] + ".." if len(item["title"]) > 40 else item["title"]
        content_type = item["content_type"]
        duration = format_duration(item.get("duration_seconds"))
        tags = ", ".join(item.get("tags", []))[:23]
        
        print(f"{title:<40} {content_type:<8} {duration:<10} {tags:<25}")
    
    print("-" * 90)
    print(f"Total: {len(items)} items")


def print_brief(items: list[dict]):
    """Print items in brief format (one line each)."""
    if not items:
        print("No items found.")
        return
    
    for item in items:
        duration = format_duration(item.get("duration_seconds"))
        loc = item.get("file_path") or item.get("url") or "-"
        print(f"[{item['content_type']}] {item['title']} ({duration}) - {loc}")


def main():
    parser = argparse.ArgumentParser(
        description="Query the Content Library"
    )
    parser.add_argument(
        "--type", "-t",
        dest="content_type",
        help="Filter by content type (article, audio, video, image, book, etc.)"
    )
    parser.add_argument(
        "--tag",
        help="Filter by tag (needs-transcription, transcribed, etc.)"
    )
    parser.add_argument(
        "--search", "-s",
        help="Search in title and content"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=20,
        help="Max results (default: 20)"
    )
    parser.add_argument(
        "--include-deprecated",
        action="store_true",
        help="Include deprecated items"
    )
    parser.add_argument(
        "--format", "-f",
        dest="output_format",
        choices=["table", "json", "brief"],
        default="table",
        help="Output format (default: table)"
    )
    
    args = parser.parse_args()
    
    items = query_items(
        content_type=args.content_type,
        tag=args.tag,
        search=args.search,
        limit=args.limit,
        include_deprecated=args.include_deprecated,
        output_format=args.output_format
    )
    
    if args.output_format == "json":
        print(json.dumps(items, indent=2, default=str))
    elif args.output_format == "brief":
        print_brief(items)
    else:
        print_table(items)


if __name__ == "__main__":
    main()

