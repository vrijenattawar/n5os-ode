#!/usr/bin/env python3
"""
Content Library - Unified Implementation
=========================================
Canonical location for content library functionality.
DB: /home/workspace/N5/data/content_library.db

Provides search/add/get/mark_used for links and snippets used by:
- email_composer.py (signature lookup)
- b_block_parser.py (resource matching)
- auto_populate_content.py (adding new items)
- exa_research.py (storing research results)
- email_corrections.py (term lookups)

Schema:
- items: id, type (link|snippet), title, content, url, notes, deprecated, timestamps
- tags: item_id, tag_key, tag_value (e.g., purpose:signature, channel:email)

Usage:
    from content_library import ContentLibrary
    lib = ContentLibrary()
    
    # CLI commands:
    # python3 N5/scripts/content_library.py list-types
    # python3 N5/scripts/content_library.py search --query "X" --type article
    # python3 N5/scripts/content_library.py ingest /path/to/file.md --type article
    # python3 N5/scripts/content_library.py sync
    # python3 N5/scripts/content_library.py stats
    
    # Search with dict tags (key-value matching)
    sigs = lib.search(tags={"purpose": "signature", "channel": "email"})
"""

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

DB_PATH = Path("/home/workspace/N5/data/content_library.db")


@dataclass
class ContentItem:
    """A content library item (link or snippet)."""
    id: str
    type: str  # 'link' or 'snippet' - legacy, use content_type
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)  # {key: value}
    notes: Optional[str] = None
    deprecated: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_used_at: Optional[str] = None
    # v5 fields
    subtype: Optional[str] = None
    summary: Optional[str] = None
    managed_fields: Optional[str] = None  # JSON string of AI-managed field names
    external_id: Optional[str] = None
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access for backward compatibility."""
        return getattr(self, key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Allow dict.get() style access for backward compatibility."""
        return getattr(self, key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ContentLibrary:
    """Unified content library for links and snippets."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._ensure_db()
    
    def _ensure_db(self):
        """Ensure database and tables exist."""
        if not self.db_path.exists():
            self._create_schema()
    
    def _create_schema(self):
        """Create database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL CHECK(type IN ('link', 'snippet')),
                title TEXT NOT NULL,
                content TEXT,
                url TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                deprecated INTEGER NOT NULL DEFAULT 0,
                expires_at TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                last_used_at TEXT,
                notes TEXT,
                source TEXT
            );
            CREATE TABLE IF NOT EXISTS tags (
                item_id TEXT NOT NULL,
                tag_key TEXT NOT NULL,
                tag_value TEXT NOT NULL,
                PRIMARY KEY (item_id, tag_key, tag_value),
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_items_type ON items(type);
            CREATE INDEX IF NOT EXISTS idx_items_deprecated ON items(deprecated);
            CREATE INDEX IF NOT EXISTS idx_items_title ON items(title COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_tags_key_value ON tags(tag_key, tag_value);
            CREATE INDEX IF NOT EXISTS idx_items_updated ON items(updated_at DESC);
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
        conn.close()
    
    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _row_to_item(self, row: sqlite3.Row, tags: Dict[str, str] = None) -> ContentItem:
        # Handle both old 'type' and new 'content_type' column names
        item_type = row["content_type"] if "content_type" in row.keys() else row.get("type", "unknown")
        return ContentItem(
            id=row["id"],
            type=item_type,
            title=row["title"],
            content=row["content"],
            url=row["url"],
            tags=tags or {},
            notes=row["notes"],
            deprecated=bool(row["deprecated"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_used_at=row["last_used_at"],
            # v5 fields
            subtype=row["subtype"] if "subtype" in row.keys() else None,
            summary=row["summary"] if "summary" in row.keys() else None,
            managed_fields=row["managed_fields"] if "managed_fields" in row.keys() else None,
            external_id=row["external_id"] if "external_id" in row.keys() else None,
        )
    
    def _get_tags(self, conn: sqlite3.Connection, item_id: str) -> Dict[str, str]:
        """Get tags as {key: value} dict."""
        rows = conn.execute(
            "SELECT tag_key, tag_value FROM tags WHERE item_id = ?", (item_id,)
        ).fetchall()
        return {r["tag_key"]: r["tag_value"] for r in rows}
    
    def _parse_tag_filter(self, tags: Union[List[str], Dict[str, str], None]) -> Dict[str, str]:
        """Parse tags from list or dict format into dict format."""
        if tags is None:
            return {}
        if isinstance(tags, dict):
            return tags
        # List format: ["key:value", "key2:value2"]
        result = {}
        for tag in tags:
            if ":" in tag:
                key, value = tag.split(":", 1)
                result[key] = value
            else:
                result["category"] = tag
        return result
    
    def search(
        self,
        query: Optional[str] = None,
        item_type: Optional[str] = None,
        content_type: Optional[str] = None,
        subtype: Optional[str] = None,
        tags: Union[List[str], Dict[str, str], None] = None,
        include_deprecated: bool = False,
        limit: int = 50,
    ) -> List[ContentItem]:
        """Search content library items.
        
        Args:
            query: Text search in title, content, notes
            item_type: 'link' or 'snippet' (legacy type field)
            content_type: Filter by content_type (article, deck, paper, etc.)
            subtype: Filter by subtype (e.g., 'scheduling-link' within 'link')
            tags: Filter by tags. Can be:
                - Dict: {"purpose": "signature", "channel": "email"} - all must match
                - List: ["purpose:signature", "channel:email"] - same as dict
            include_deprecated: Include deprecated items
            limit: Max results
        
        Returns:
            List of ContentItem matching criteria
        """
        conn = self._get_conn()
        
        conditions = []
        params = []
        
        if not include_deprecated:
            conditions.append("i.deprecated = 0")
        
        if item_type:
            conditions.append("i.content_type = ?")
            params.append(item_type)
        
        if content_type:
            conditions.append("i.content_type = ?")
            params.append(content_type)
        
        if subtype:
            conditions.append("i.subtype = ?")
            params.append(subtype)
        
        if query:
            conditions.append("(i.title LIKE ? OR i.content LIKE ? OR i.notes LIKE ?)")
            like_query = f"%{query}%"
            params.extend([like_query, like_query, like_query])
        
        # Parse tag filter and build SQL conditions
        tag_filter = self._parse_tag_filter(tags)
        tag_join = ""
        if tag_filter:
            # For each tag requirement, we need to join to ensure ALL tags match
            for i, (key, value) in enumerate(tag_filter.items()):
                alias = f"t{i}"
                tag_join += f" JOIN tags {alias} ON i.id = {alias}.item_id AND {alias}.tag_key = ? AND {alias}.tag_value = ?"
                params.insert(len(params), key)
                params.insert(len(params), value)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
            SELECT DISTINCT i.* FROM items i
            {tag_join}
            WHERE {where_clause}
            ORDER BY i.updated_at DESC
            LIMIT ?
        """
        params.append(limit)
        
        rows = conn.execute(sql, params).fetchall()
        
        # Get tags for each result
        results = []
        for row in rows:
            item_tags = self._get_tags(conn, row["id"])
            results.append(self._row_to_item(row, item_tags))
        
        conn.close()
        return results
    
    def get(self, item_id: str) -> Optional[ContentItem]:
        """Get a specific item by ID."""
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            conn.close()
            return None
        tags = self._get_tags(conn, item_id)
        conn.close()
        return self._row_to_item(row, tags)
    
    def add(
        self,
        item_id: str,
        item_type: str,
        title: str,
        content: Optional[str] = None,
        url: Optional[str] = None,
        tags: Union[List[str], Dict[str, str], None] = None,
        notes: Optional[str] = None,
        source: str = "manual",
        subtype: Optional[str] = None,
        summary: Optional[str] = None,
        managed_fields: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> ContentItem:
        """Add or update an item.
        
        Tags can be:
        - Dict: {"purpose": "signature", "channel": "email"}
        - List: ["purpose:signature", "channel:email"] or ["category"] (defaults to category key)
        """
        conn = self._get_conn()
        now = datetime.now().isoformat()
        
        conn.execute("""
            INSERT INTO items (id, content_type, title, content, url, notes, source, created_at, updated_at, subtype, summary, managed_fields, external_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                content = excluded.content,
                url = excluded.url,
                notes = excluded.notes,
                updated_at = excluded.updated_at,
                subtype = excluded.subtype,
                summary = excluded.summary,
                managed_fields = excluded.managed_fields,
                external_id = excluded.external_id
        """, (item_id, item_type, title, content, url, notes, source, now, now, subtype, summary, managed_fields, external_id))
        
        if tags:
            conn.execute("DELETE FROM tags WHERE item_id = ?", (item_id,))
            tag_dict = self._parse_tag_filter(tags) if isinstance(tags, list) else tags
            for key, value in tag_dict.items():
                conn.execute(
                    "INSERT OR IGNORE INTO tags (item_id, tag_key, tag_value) VALUES (?, ?, ?)",
                    (item_id, key, value)
                )
        
        conn.commit()
        item = self.get(item_id)
        conn.close()
        return item
    
    def mark_used(self, item_id: str) -> bool:
        """Mark an item as used (updates last_used_at timestamp)."""
        conn = self._get_conn()
        now = datetime.now().isoformat()
        cursor = conn.execute(
            "UPDATE items SET last_used_at = ? WHERE id = ?",
            (now, item_id)
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def deprecate(self, item_id: str) -> bool:
        """Mark an item as deprecated."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE items SET deprecated = 1, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), item_id)
        )
        conn.commit()
        conn.close()
        return True
    
    def list_tags(self) -> List[str]:
        """List all unique tag key:value combinations."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT DISTINCT tag_key || ':' || tag_value as tag FROM tags ORDER BY tag"
        ).fetchall()
        conn.close()
        return [r["tag"] for r in rows]
    
    def list_content_types(self) -> Dict[str, int]:
        """List all content types with counts."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT content_type, COUNT(*) as count FROM items WHERE deprecated = 0 AND content_type IS NOT NULL GROUP BY content_type ORDER BY count DESC"
        ).fetchall()
        conn.close()
        return {r["content_type"]: r["count"] for r in rows}
    
    def stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        conn = self._get_conn()
        total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM items WHERE deprecated = 0").fetchone()[0]
        by_content_type = dict(conn.execute(
            "SELECT content_type, COUNT(*) FROM items WHERE deprecated = 0 AND content_type IS NOT NULL GROUP BY content_type"
        ).fetchall())
        conn.close()
        return {"total": total, "active": active, "by_content_type": by_content_type}


# Backward compatibility alias
ContentLibraryV3 = ContentLibrary


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(description="Content Library CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Search
    search_p = subparsers.add_parser("search", help="Search items")
    search_p.add_argument("--query", "-q", help="Search query")
    search_p.add_argument("--type", "-t", dest="item_type", choices=["link", "snippet", "article", "deck", "paper", "book", "framework", "social-post", "podcast", "video", "quote"], help="Filter by content type (legacy alias for --content-type)")
    search_p.add_argument("--content-type", "-c", help="Content type filter (article, deck, paper, etc.)")
    search_p.add_argument("--tags", nargs="+", help="Filter by tags (key:value format)")
    search_p.add_argument("--limit", "-n", type=int, default=20, help="Max results")
    search_p.add_argument("--json", action="store_true", help="JSON output")
    
    # Get
    get_p = subparsers.add_parser("get", help="Get item by ID")
    get_p.add_argument("id", help="Item ID")
    get_p.add_argument("--json", action="store_true", help="JSON output")
    
    # Stats
    subparsers.add_parser("stats", help="Show statistics")
    
    # Tags
    subparsers.add_parser("tags", help="List all tags")
    
    # List content types (NEW)
    subparsers.add_parser("list-types", help="List content types with counts")
    
    # Ingest (NEW)
    ingest_p = subparsers.add_parser("ingest", help="Ingest a content file")
    ingest_p.add_argument("file", help="Path to file to ingest")
    ingest_p.add_argument("--type", dest="content_type", help="Content type (article, deck, paper, etc.)")
    ingest_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    ingest_p.add_argument("--move", action="store_true", help="Move file to canonical location")
    
    # Sync (NEW)
    sync_p = subparsers.add_parser("sync", help="Run backfill to sync all content files")
    sync_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    args = parser.parse_args()
    lib = ContentLibrary()
    
    if args.command == "search":
        items = lib.search(
            query=args.query,
            item_type=args.item_type,
            content_type=getattr(args, 'content_type', None),
            tags=args.tags,
            limit=args.limit,
        )
        if args.json:
            print(json.dumps([i.to_dict() for i in items], indent=2))
        else:
            for item in items:
                ct = getattr(item, 'content_type', None) or item.type
                print(f"{item.id}: {item.title} ({ct})")
                if item.url:
                    print(f"  URL: {item.url}")
                if item.tags:
                    tag_str = ", ".join(f"{k}:{v}" for k, v in item.tags.items())
                    print(f"  Tags: {tag_str}")
    
    elif args.command == "get":
        item = lib.get(args.id)
        if not item:
            print(f"Not found: {args.id}", file=sys.stderr)
            sys.exit(1)
        if args.json:
            print(json.dumps(item.to_dict(), indent=2))
        else:
            print(f"ID: {item.id}")
            print(f"Title: {item.title}")
            print(f"Type: {item.type}")
            if item.url:
                print(f"URL: {item.url}")
            if item.content:
                preview = item.content[:200] + "..." if len(item.content) > 200 else item.content
                print(f"Content: {preview}")
            if item.tags:
                tag_str = ", ".join(f"{k}:{v}" for k, v in item.tags.items())
                print(f"Tags: {tag_str}")
    
    elif args.command == "stats":
        stats = lib.stats()
        print(f"Total items: {stats['total']}")
        print(f"Active items: {stats['active']}")
        if stats.get("by_type"):
            print("By legacy type:")
            for t, c in stats["by_type"].items():
                print(f"  {t}: {c}")
        if stats.get("by_content_type"):
            print("By content type:")
            for t, c in stats["by_content_type"].items():
                print(f"  {t}: {c}")
    
    elif args.command == "tags":
        for tag in lib.list_tags():
            print(tag)
    
    elif args.command == "list-types":
        types = lib.list_content_types()
        if not types:
            print("No content types found.")
        else:
            print("Content types:")
            for ct, count in types.items():
                print(f"  {ct}: {count}")
    
    elif args.command == "ingest":
        import subprocess
        cmd = ["python3", "N5/scripts/content_ingest.py", args.file]
        if args.content_type:
            cmd.extend(["--type", args.content_type])
        if args.dry_run:
            cmd.append("--dry-run")
        if args.move:
            cmd.append("--move")
        result = subprocess.run(cmd, cwd="/home/workspace")
        sys.exit(result.returncode)
    
    elif args.command == "sync":
        import subprocess
        cmd = ["python3", "N5/scripts/content_backfill.py"]
        if args.dry_run:
            cmd.append("--dry-run")
        result = subprocess.run(cmd, cwd="/home/workspace")
        sys.exit(result.returncode)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()







