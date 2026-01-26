#!/usr/bin/env python3
"""
Meeting Registry - SQLite-backed registry for meeting metadata
Canonical source of truth for all ingested meetings (registry-first architecture)
"""

import sqlite3
import json
import logging
import pytz
from datetime import datetime, UTC
from pathlib import Path
from typing import Optional, Dict, List, Any
from contextlib import contextmanager
from meeting_config import WORKSPACE, MEETINGS_DIR, STAGING_DIR, LOG_DIR, REGISTRY_DB, TIMEZONE, ENABLE_SMS

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Parse timezone from config
if TIMEZONE == 'UTC':
    TZ = UTC
else:
    TZ = pytz.timezone(TIMEZONE)


class MeetingRegistry:
    """
    Registry for meeting metadata with duplicate detection.
    Registry-first: this is source of truth, filesystem is storage.
    """
    
    def __init__(self, db_path: str = REGISTRY_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    @contextmanager
    def _get_conn(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    meeting_id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    participants_normalized TEXT NOT NULL,
                    folder_name TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    source TEXT,
                    file_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    metadata TEXT
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON meetings(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_folder ON meetings(folder_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON meetings(status)")
            conn.commit()
            logger.info(f"Initialized registry at {self.db_path}")
    
    def add_meeting(self, metadata: Dict[str, Any]) -> str:
        """
        Add new meeting to registry.
        
        Args:
            metadata: Dict with keys: meeting_id, date, participants_normalized,
                     folder_name, source, file_count (optional), metadata (optional)
        
        Returns:
            meeting_id of created record
        
        Raises:
            sqlite3.IntegrityError: If meeting_id or folder_name already exists
        """
        required = ['meeting_id', 'date', 'participants_normalized', 'folder_name']
        missing = [k for k in required if k not in metadata]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        created_at = datetime.now(TZ).isoformat().replace('+00:00', 'Z')
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO meetings 
                (meeting_id, date, participants_normalized, folder_name, 
                 created_at, source, file_count, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata['meeting_id'],
                metadata['date'],
                json.dumps(metadata['participants_normalized']),
                metadata['folder_name'],
                created_at,
                metadata.get('source', 'unknown'),
                metadata.get('file_count', 0),
                metadata.get('status', 'pending'),
                json.dumps(metadata.get('metadata', {}))
            ))
            conn.commit()
        
        logger.info(f"Added meeting {metadata['meeting_id']} to registry")
        return metadata['meeting_id']
    
    def find_duplicate(self, date: str, participants: List[str]) -> Optional[Dict[str, Any]]:
        """
        Find existing meeting with exact match on date + normalized participants.
        
        Args:
            date: YYYY-MM-DD format
            participants: List of normalized participant names (lowercase, sorted)
        
        Returns:
            Dict with meeting data if found, None otherwise
        """
        participants_json = json.dumps(sorted(participants))
        
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT * FROM meetings 
                WHERE date = ? AND participants_normalized = ?
            """, (date, participants_json))
            
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
    
    def find_fuzzy_duplicates(
        self, 
        date: str, 
        participants: List[str],
        similarity_threshold: float = 0.90
    ) -> List[Dict[str, Any]]:
        """
        Find meetings on same date with similar participants (fuzzy match).
        Uses rapidfuzz for participant name similarity.
        
        Args:
            date: YYYY-MM-DD format
            participants: List of normalized participant names
            similarity_threshold: Minimum similarity score (0.0-1.0)
        
        Returns:
            List of matching meetings with similarity scores
        """
        from rapidfuzz import fuzz
        
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT * FROM meetings WHERE date = ?
            """, (date,))
            
            matches = []
            for row in cursor:
                existing_participants = json.loads(row['participants_normalized'])
                
                similarity = self._calculate_participant_similarity(
                    participants, existing_participants
                )
                
                if similarity >= similarity_threshold:
                    match = self._row_to_dict(row)
                    match['similarity_score'] = similarity
                    matches.append(match)
            
            return sorted(matches, key=lambda x: x['similarity_score'], reverse=True)
    
    def _calculate_participant_similarity(
        self, 
        p1: List[str], 
        p2: List[str]
    ) -> float:
        """
        Calculate similarity between two participant lists.
        Uses best-match pairing and averages similarity scores.
        """
        from rapidfuzz import fuzz
        
        if not p1 or not p2:
            return 0.0
        
        set1, set2 = set(p1), set(p2)
        
        if set1 == set2:
            return 1.0
        
        total_similarity = 0.0
        matched = 0
        
        for name1 in p1:
            best_score = max(
                fuzz.ratio(name1, name2) / 100.0 
                for name2 in p2
            )
            total_similarity += best_score
            matched += 1
        
        return total_similarity / matched if matched > 0 else 0.0
    
    def update_meeting(self, meeting_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing meeting record.
        
        Args:
            meeting_id: ID of meeting to update
            updates: Dict with fields to update (file_count, status, metadata, etc)
        
        Returns:
            True if updated, False if meeting_id not found
        """
        allowed_fields = ['file_count', 'status', 'metadata', 'folder_name']
        update_parts = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                if field == 'metadata':
                    value = json.dumps(value)
                update_parts.append(f"{field} = ?")
                values.append(value)
        
        if not update_parts:
            logger.warning(f"No valid fields to update for {meeting_id}")
            return False
        
        values.append(meeting_id)
        
        with self._get_conn() as conn:
            cursor = conn.execute(
                f"UPDATE meetings SET {', '.join(update_parts)} WHERE meeting_id = ?",
                values
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Updated meeting {meeting_id}")
                return True
            else:
                logger.warning(f"Meeting {meeting_id} not found for update")
                return False
    
    def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM meetings WHERE meeting_id = ?", 
                (meeting_id,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
    
    def get_meeting_by_folder(self, folder_name: str) -> Optional[Dict[str, Any]]:
        """Get meeting by folder name"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM meetings WHERE folder_name = ?", 
                (folder_name,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
    
    def list_meetings(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        order_by: str = "date DESC"
    ) -> List[Dict[str, Any]]:
        """
        List meetings with optional filters.
        
        Args:
            filters: Dict with keys matching column names (date, status, source)
            limit: Max number of results
            order_by: SQL ORDER BY clause (default: "date DESC")
        
        Returns:
            List of meeting dicts
        """
        where_parts = []
        values = []
        
        if filters:
            for field, value in filters.items():
                where_parts.append(f"{field} = ?")
                values.append(value)
        
        query = "SELECT * FROM meetings"
        if where_parts:
            query += f" WHERE {' AND '.join(where_parts)}"
        query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        
        with self._get_conn() as conn:
            cursor = conn.execute(query, values)
            return [self._row_to_dict(row) for row in cursor]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        with self._get_conn() as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_meetings,
                    COUNT(DISTINCT date) as unique_dates,
                    SUM(file_count) as total_files,
                    COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    MIN(date) as earliest_date,
                    MAX(date) as latest_date
                FROM meetings
            """)
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dict, deserializing JSON fields"""
        d = dict(row)
        if 'participants_normalized' in d:
            d['participants_normalized'] = json.loads(d['participants_normalized'])
        if 'metadata' in d and d['metadata']:
            d['metadata'] = json.loads(d['metadata'])
        return d


def main():
    """CLI for testing registry operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeting Registry CLI")
    parser.add_argument("command", choices=['stats', 'list', 'get', 'test'])
    parser.add_argument("--meeting-id", help="Meeting ID for 'get' command")
    parser.add_argument("--limit", type=int, default=10, help="Limit for 'list'")
    
    args = parser.parse_args()
    registry = MeetingRegistry()
    
    if args.command == 'stats':
        stats = registry.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'list':
        meetings = registry.list_meetings(limit=args.limit)
        print(json.dumps(meetings, indent=2))
    
    elif args.command == 'get':
        if not args.meeting_id:
            print("Error: --meeting-id required")
            return 1
        meeting = registry.get_meeting(args.meeting_id)
        print(json.dumps(meeting, indent=2))
    
    elif args.command == 'test':
        print("Running registry tests...")
        
        test_meeting = {
            'meeting_id': 'test-2025-01-01-alice-bob',
            'date': '2025-01-01',
            'participants_normalized': ['alice', 'bob'],
            'folder_name': 'test_folder',
            'source': 'test'
        }
        
        try:
            meeting_id = registry.add_meeting(test_meeting)
            print(f"✓ Created test meeting: {meeting_id}")
            
            found = registry.find_duplicate('2025-01-01', ['alice', 'bob'])
            print(f"✓ Found exact duplicate: {found['meeting_id']}")
            
            fuzzy = registry.find_fuzzy_duplicates('2025-01-01', ['alyce', 'bobby'])
            if fuzzy:
                print(f"✓ Fuzzy match found: {fuzzy[0]['meeting_id']} (score: {fuzzy[0]['similarity_score']:.2f})")
            
            updated = registry.update_meeting(meeting_id, {'file_count': 5, 'status': 'processed'})
            print(f"✓ Updated meeting: {updated}")
            
            stats = registry.get_stats()
            print(f"✓ Stats: {stats['total_meetings']} meetings")
            
            print("\n✅ All tests passed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


