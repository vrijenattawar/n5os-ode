#!/usr/bin/env python3
"""
N5 Conversation Registry
Central SQLite database tracking all conversations, artifacts, issues, learnings.

Usage:
    python3 conversation_registry.py init
    python3 conversation_registry.py query --type build --status active
    python3 conversation_registry.py stats
"""

import sqlite3
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


# Default database path
DEFAULT_DB_PATH = Path("/home/workspace/N5/data/conversations.db")


class ConversationRegistry:
    """Manages the conversations database."""
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY,
        type TEXT,
        status TEXT DEFAULT 'active',
        focus TEXT,
        objective TEXT,
        progress TEXT,
        mode TEXT,
        parent_id TEXT,
        created_at TEXT,
        updated_at TEXT,
        closed_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        path TEXT NOT NULL,
        description TEXT,
        artifact_type TEXT,
        created_at TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
    );
    
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        description TEXT NOT NULL,
        resolution TEXT,
        severity TEXT,
        created_at TEXT,
        resolved_at TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
    );
    
    CREATE TABLE IF NOT EXISTS learnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        created_at TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
    );
    
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        decision TEXT NOT NULL,
        rationale TEXT,
        created_at TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_conv_type ON conversations(type);
    CREATE INDEX IF NOT EXISTS idx_conv_status ON conversations(status);
    CREATE INDEX IF NOT EXISTS idx_artifacts_conv ON artifacts(conversation_id);
    CREATE INDEX IF NOT EXISTS idx_issues_conv ON issues(conversation_id);
    CREATE INDEX IF NOT EXISTS idx_learnings_conv ON learnings(conversation_id);
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._conn = None
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def init_db(self) -> bool:
        """Initialize the database schema."""
        try:
            conn = self._get_conn()
            conn.executescript(self.SCHEMA)
            conn.commit()
            print(f"✓ Conversation registry initialized at {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize database: {e}", file=sys.stderr)
            return False
    
    def upsert_conversation(self, convo_id: str, **kwargs) -> bool:
        """Insert or update a conversation record."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("SELECT 1 FROM conversations WHERE conversation_id = ?", (convo_id,))
            exists = cursor.fetchone() is not None
            
            now = datetime.now(timezone.utc).isoformat()
            
            if exists:
                # Update
                set_parts = []
                values = []
                for key, val in kwargs.items():
                    if val is not None:
                        set_parts.append(f"{key} = ?")
                        values.append(val)
                set_parts.append("updated_at = ?")
                values.append(now)
                values.append(convo_id)
                
                sql = f"UPDATE conversations SET {', '.join(set_parts)} WHERE conversation_id = ?"
                cursor.execute(sql, values)
            else:
                # Insert
                kwargs['conversation_id'] = convo_id
                kwargs['created_at'] = now
                kwargs['updated_at'] = now
                
                cols = ', '.join(kwargs.keys())
                placeholders = ', '.join(['?' for _ in kwargs])
                sql = f"INSERT INTO conversations ({cols}) VALUES ({placeholders})"
                cursor.execute(sql, list(kwargs.values()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"✗ Failed to upsert conversation: {e}", file=sys.stderr)
            return False
    
    def add_artifact(self, convo_id: str, path: str, description: str = None, 
                     artifact_type: str = None) -> bool:
        """Add an artifact record."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO artifacts (conversation_id, path, description, artifact_type, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (convo_id, path, description, artifact_type, now))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"✗ Failed to add artifact: {e}", file=sys.stderr)
            return False
    
    def add_issue(self, convo_id: str, description: str, severity: str = "medium") -> int:
        """Add an issue record. Returns issue ID."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO issues (conversation_id, description, severity, created_at)
                VALUES (?, ?, ?, ?)
            """, (convo_id, description, severity, now))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"✗ Failed to add issue: {e}", file=sys.stderr)
            return -1
    
    def resolve_issue(self, issue_id: int, resolution: str) -> bool:
        """Mark an issue as resolved."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                UPDATE issues SET resolution = ?, resolved_at = ? WHERE id = ?
            """, (resolution, now, issue_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"✗ Failed to resolve issue: {e}", file=sys.stderr)
            return False
    
    def add_learning(self, convo_id: str, content: str, category: str = None) -> bool:
        """Add a learning record."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO learnings (conversation_id, content, category, created_at)
                VALUES (?, ?, ?, ?)
            """, (convo_id, content, category, now))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"✗ Failed to add learning: {e}", file=sys.stderr)
            return False
    
    def add_decision(self, convo_id: str, decision: str, rationale: str = None) -> bool:
        """Add a decision record."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO decisions (conversation_id, decision, rationale, created_at)
                VALUES (?, ?, ?, ?)
            """, (convo_id, decision, rationale, now))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"✗ Failed to add decision: {e}", file=sys.stderr)
            return False
    
    def query_conversations(self, conv_type: str = None, status: str = None,
                           limit: int = 50) -> List[Dict]:
        """Query conversations with optional filters."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            sql = "SELECT * FROM conversations WHERE 1=1"
            params = []
            
            if conv_type:
                sql += " AND type = ?"
                params.append(conv_type)
            if status:
                sql += " AND status = ?"
                params.append(status)
            
            sql += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"✗ Query failed: {e}", file=sys.stderr)
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            stats = {}
            
            # Total conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            stats['total_conversations'] = cursor.fetchone()[0]
            
            # By type
            cursor.execute("SELECT type, COUNT(*) FROM conversations GROUP BY type")
            stats['by_type'] = {row[0] or 'unknown': row[1] for row in cursor.fetchall()}
            
            # By status
            cursor.execute("SELECT status, COUNT(*) FROM conversations GROUP BY status")
            stats['by_status'] = {row[0] or 'unknown': row[1] for row in cursor.fetchall()}
            
            # Artifacts
            cursor.execute("SELECT COUNT(*) FROM artifacts")
            stats['total_artifacts'] = cursor.fetchone()[0]
            
            # Issues
            cursor.execute("SELECT COUNT(*) FROM issues WHERE resolved_at IS NULL")
            stats['open_issues'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM issues WHERE resolved_at IS NOT NULL")
            stats['resolved_issues'] = cursor.fetchone()[0]
            
            # Learnings
            cursor.execute("SELECT COUNT(*) FROM learnings")
            stats['total_learnings'] = cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            print(f"✗ Stats failed: {e}", file=sys.stderr)
            return {}


def main():
    parser = argparse.ArgumentParser(description="N5 Conversation Registry")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    subparsers.add_parser("init", help="Initialize the database")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query conversations")
    query_parser.add_argument("--type", help="Filter by type")
    query_parser.add_argument("--status", help="Filter by status")
    query_parser.add_argument("--limit", type=int, default=50, help="Max results")
    
    # Stats command
    subparsers.add_parser("stats", help="Show database statistics")
    
    args = parser.parse_args()
    
    registry = ConversationRegistry()
    
    try:
        if args.command == "init":
            success = registry.init_db()
            sys.exit(0 if success else 1)
        
        elif args.command == "query":
            results = registry.query_conversations(
                conv_type=args.type,
                status=args.status,
                limit=args.limit
            )
            print(json.dumps(results, indent=2))
        
        elif args.command == "stats":
            stats = registry.get_stats()
            print(json.dumps(stats, indent=2))
        
        else:
            parser.print_help()
    finally:
        registry.close()


if __name__ == "__main__":
    main()
