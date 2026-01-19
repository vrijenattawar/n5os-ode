#!/usr/bin/env python3
"""
Conversation DB Sync - Sync SESSION_STATE.md to conversations.db

Synchronizes conversation state from SESSION_STATE.md files into
conversations.db for querying, analytics, and intelligence extraction.

Usage:
  python3 conversation_sync.py sync --convo-id con_XXX
  python3 conversation_sync.py sync-all
  python3 conversation_sync.py query --type build --status active
"""

import argparse
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import re


class ConversationSync:
    """Sync SESSION_STATE.md to conversations.db."""
    
    WORKSPACE_BASE = Path("/home/.z/workspaces")
    DB_PATH = Path("/home/workspace/N5/data/conversations.db")
    
    def __init__(self):
        self.conn = None
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Ensure conversations.db exists with proper schema."""
        # Ensure directory exists
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.DB_PATH))
        self.conn.row_factory = sqlite3.Row
        
        # Check if conversations table exists
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
        )
        if not cursor.fetchone():
            print("Creating conversations.db schema...", file=sys.stderr)
            self._create_schema()
    
    def _create_schema(self):
        """Create conversations table schema."""
        self.conn.executescript("""
            -- Core conversations table
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                mode TEXT,
                
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                
                focus TEXT,
                objective TEXT,
                tags TEXT,
                
                parent_id TEXT,
                related_ids TEXT,
                
                starred INTEGER DEFAULT 0,
                progress_pct INTEGER DEFAULT 0,
                
                workspace_path TEXT,
                state_file_path TEXT,
                aar_path TEXT,
                
                FOREIGN KEY (parent_id) REFERENCES conversations(id)
            );

            -- Artifacts created during conversations
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                filepath TEXT NOT NULL,
                artifact_type TEXT,
                created_at TEXT NOT NULL,
                description TEXT,
                
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            );

            -- Issues encountered during conversations
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT,
                message TEXT NOT NULL,
                context TEXT,
                resolution TEXT,
                resolved INTEGER DEFAULT 0,
                
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            );

            -- Learnings extracted from conversations
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                lesson_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                principle_refs TEXT,
                status TEXT DEFAULT 'pending',
                
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            );

            -- Decisions made during conversations
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                decision TEXT NOT NULL,
                rationale TEXT,
                alternatives TEXT,
                outcome TEXT,
                
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            );

            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_conversations_type ON conversations(type);
            CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
            CREATE INDEX IF NOT EXISTS idx_conversations_starred ON conversations(starred);
            CREATE INDEX IF NOT EXISTS idx_conversations_parent ON conversations(parent_id);
            CREATE INDEX IF NOT EXISTS idx_artifacts_convo ON artifacts(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_issues_convo ON issues(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_issues_severity ON issues(severity, resolved);
            CREATE INDEX IF NOT EXISTS idx_learnings_convo ON learnings(conversation_id);
            CREATE INDEX IF NOT EXISTS idx_learnings_status ON learnings(status);
        """)
        self.conn.commit()
        print("✓ conversations.db schema created")
    
    def parse_session_state(self, convo_id: str) -> Optional[Dict]:
        """Parse SESSION_STATE.md for a conversation."""
        session_state_path = self.WORKSPACE_BASE / convo_id / "SESSION_STATE.md"
        
        if not session_state_path.exists():
            return None
        
        content = session_state_path.read_text()
        
        # Extract YAML frontmatter
        frontmatter = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                for line in yaml_content.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        frontmatter[key.strip()] = value.strip()
        
        # Extract markdown sections
        data = {
            "id": convo_id,
            "type": frontmatter.get("type", "discussion"),
            "status": frontmatter.get("status", "active"),
            "mode": frontmatter.get("mode"),
            "created_at": frontmatter.get("created") or datetime.now(timezone.utc).isoformat(),
            "updated_at": frontmatter.get("last_updated") or datetime.now(timezone.utc).isoformat(),
            "workspace_path": str(self.WORKSPACE_BASE / convo_id),
            "state_file_path": str(session_state_path),
        }
        
        # Extract focus, objective, progress from markdown content
        if "**Focus:**" in content:
            match = re.search(r'\*\*Focus:\*\*\s*(.+?)(?:\n|$)', content)
            if match:
                data["focus"] = match.group(1).strip()
        
        if "**Objective:**" in content:
            match = re.search(r'\*\*Objective:\*\*\s*(.+?)(?:\n|$)', content)
            if match:
                data["objective"] = match.group(1).strip()
        
        if "**Overall:**" in content:
            match = re.search(r'\*\*Overall:\*\*\s*(\d+)%', content)
            if match:
                data["progress_pct"] = int(match.group(1))
        
        # Extract tags
        tags = []
        for line in content.split("\n"):
            if line.startswith("#") and not line.startswith("# ") and not line.startswith("##"):
                tags.extend([tag.strip() for tag in line.split() if tag.startswith("#")])
        if tags:
            data["tags"] = json.dumps(tags)
        
        # Generate title from focus or objective
        data["title"] = data.get("focus") or data.get("objective") or f"Conversation {convo_id}"
        
        return data
    
    def sync_conversation(self, convo_id: str) -> bool:
        """Sync a single conversation to the database."""
        data = self.parse_session_state(convo_id)
        
        if not data:
            print(f"⚠️  No SESSION_STATE.md found for {convo_id}", file=sys.stderr)
            return False
        
        # Upsert into database
        cursor = self.conn.execute("SELECT id FROM conversations WHERE id = ?", (convo_id,))
        exists = cursor.fetchone() is not None
        
        if exists:
            self.conn.execute("""
                UPDATE conversations SET
                    title = ?,
                    type = ?,
                    status = ?,
                    mode = ?,
                    updated_at = ?,
                    focus = ?,
                    objective = ?,
                    tags = ?,
                    progress_pct = ?,
                    workspace_path = ?,
                    state_file_path = ?
                WHERE id = ?
            """, (
                data.get("title"),
                data["type"],
                data["status"],
                data.get("mode"),
                data["updated_at"],
                data.get("focus"),
                data.get("objective"),
                data.get("tags"),
                data.get("progress_pct", 0),
                data["workspace_path"],
                data["state_file_path"],
                convo_id
            ))
            action = "Updated"
        else:
            self.conn.execute("""
                INSERT INTO conversations (
                    id, title, type, status, mode,
                    created_at, updated_at, focus, objective, tags,
                    progress_pct, workspace_path, state_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                convo_id,
                data.get("title"),
                data["type"],
                data["status"],
                data.get("mode"),
                data["created_at"],
                data["updated_at"],
                data.get("focus"),
                data.get("objective"),
                data.get("tags"),
                data.get("progress_pct", 0),
                data["workspace_path"],
                data["state_file_path"]
            ))
            action = "Inserted"
        
        self.conn.commit()
        print(f"✓ {action} {convo_id} → conversations.db")
        return True
    
    def sync_all(self) -> int:
        """Sync all conversations with SESSION_STATE.md files."""
        count = 0
        
        if not self.WORKSPACE_BASE.exists():
            print(f"⚠️  Workspace base not found: {self.WORKSPACE_BASE}", file=sys.stderr)
            return 0
        
        for convo_dir in self.WORKSPACE_BASE.iterdir():
            if convo_dir.is_dir() and convo_dir.name.startswith("con_"):
                if (convo_dir / "SESSION_STATE.md").exists():
                    if self.sync_conversation(convo_dir.name):
                        count += 1
        
        print(f"\n✓ Synced {count} conversations to conversations.db")
        return count
    
    def query(self, conv_type: str = None, status: str = None, limit: int = 20) -> List[Dict]:
        """Query conversations from the database."""
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
        
        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="Sync SESSION_STATE.md to conversations.db")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync a single conversation")
    sync_parser.add_argument("--convo-id", required=True, help="Conversation ID")
    
    # sync-all command
    subparsers.add_parser("sync-all", help="Sync all conversations")
    
    # query command
    query_parser = subparsers.add_parser("query", help="Query conversations")
    query_parser.add_argument("--type", help="Filter by type (build, research, discussion, planning)")
    query_parser.add_parser("--status", help="Filter by status (active, complete)")
    query_parser.add_argument("--limit", type=int, default=20, help="Max results")
    
    # init command - just initialize the database
    subparsers.add_parser("init", help="Initialize conversations.db (create if missing)")
    
    args = parser.parse_args()
    
    syncer = ConversationSync()
    
    try:
        if args.command == "sync":
            syncer.sync_conversation(args.convo_id)
        elif args.command == "sync-all":
            syncer.sync_all()
        elif args.command == "query":
            results = syncer.query(
                conv_type=getattr(args, 'type', None),
                status=getattr(args, 'status', None),
                limit=args.limit
            )
            for r in results:
                print(f"{r['id']}: {r['title']} [{r['type']}/{r['status']}]")
        elif args.command == "init":
            print("✓ conversations.db initialized")
        else:
            parser.print_help()
    finally:
        syncer.close()


if __name__ == "__main__":
    main()
