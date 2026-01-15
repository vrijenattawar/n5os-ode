#!/usr/bin/env python3
"""
Journal CLI - Quick journaling with typed entries and SQLite storage.

Usage:
    journal.py new [TYPE]           Start a new journal entry (default: journal)
    journal.py list [--type TYPE] [--days N] [--limit N]   List recent entries
    journal.py view ID              View a specific entry
    journal.py types                List available entry types
    journal.py edit ID              Edit an existing entry
    journal.py search QUERY         Search entries by content

Entry Types:
    - journal          General journaling
    - morning_pages    Morning stream-of-consciousness
    - evening          Evening reflection
    - gratitude        Gratitude practice
    - weekly_review    Weekly reflection
    - idea             Idea capture
    - custom           Any custom type you specify

Examples:
    python3 journal.py new morning_pages
    python3 journal.py new evening
    python3 journal.py list --type morning_pages --days 7
    python3 journal.py view 42

Part of n5OS-Ode: https://github.com/vrijenattawar/n5os-ode
"""

import argparse
import sqlite3
import subprocess
import tempfile
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent

DB_PATH = Path("/home/workspace/N5/data/journal.db")
EDITOR = os.environ.get("EDITOR", "nano")

ENTRY_TYPES = {
    "journal": "General journaling",
    "morning_pages": "Morning stream-of-consciousness writing",
    "evening": "Evening reflection on the day",
    "gratitude": "Gratitude practice - what you're thankful for",
    "weekly_review": "Weekly reflection and planning",
    "idea": "Idea capture and exploration",
    "ad_hoc": "Ad hoc reflection",
}

TAG_CATEGORIES = {
    "mood": ["anxious", "calm", "energized", "tired", "focused", "distracted"],
    "trigger": ["work", "social", "fatigue", "hunger", "boredom", "stress"],
    "theme": ["relationships", "career", "health", "finance", "creativity"],
}

PROMPTS = {
    "journal": "Write freely about whatever is on your mind...\n\n",
    "morning_pages": dedent("""
        Morning Pages - Stream of consciousness writing
        ===============================================
        Write whatever comes to mind. Don't edit, don't judge.
        Just let the thoughts flow onto the page.
        
        ---
        
    """).strip() + "\n\n",
    "evening": dedent("""
        Evening Reflection
        ==================
        
        What went well today?
        
        
        What could have gone better?
        
        
        What did I learn?
        
        
        What am I grateful for?
        
    """).strip() + "\n",
    "gratitude": dedent("""
        Gratitude Practice
        ==================
        
        Three things I'm grateful for today:
        
        1. 
        
        2. 
        
        3. 
        
        Why these matter to me:
        
    """).strip() + "\n",
    "weekly_review": dedent("""
        Weekly Review
        =============
        
        ## Wins this week
        
        
        ## Challenges faced
        
        
        ## Lessons learned
        
        
        ## Focus for next week
        
        
        ## Energy/mood reflection
        
    """).strip() + "\n",
    "idea": dedent("""
        Idea Capture
        ============
        
        The idea:
        
        
        Why it matters:
        
        
        Next steps to explore:
        
    """).strip() + "\n",
}


def init_db():
    """Initialize the database schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            entry_type TEXT NOT NULL DEFAULT 'journal',
            content TEXT NOT NULL,
            mood TEXT,
            tags TEXT,
            word_count INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entry_type ON journal_entries(entry_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at ON journal_entries(created_at)
    """)
    
    conn.commit()
    conn.close()


def get_db():
    """Get database connection."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def new_entry(entry_type: str, mood: str = None, tags: str = None):
    """Create a new journal entry using the default editor."""
    if entry_type not in ENTRY_TYPES and entry_type != "custom":
        print(f"Unknown entry type: {entry_type}")
        print(f"Available types: {', '.join(ENTRY_TYPES.keys())}")
        print("Or use any custom type name.")
    
    # Get the prompt template
    prompt = PROMPTS.get(entry_type, f"# {entry_type.replace('_', ' ').title()}\n\n")
    
    # Show tag suggestions if creating new entry
    if not tags:
        print("\nSuggested Tags:")
        for category, suggestions in TAG_CATEGORIES.items():
            print(f"  {category}: {', '.join(suggestions)}")
        print("")

    # Create temp file with prompt
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prompt)
        temp_path = f.name
    
    # Open editor
    try:
        subprocess.run([EDITOR, temp_path], check=True)
    except subprocess.CalledProcessError:
        print("Editor exited with error.")
        os.unlink(temp_path)
        return None
    except FileNotFoundError:
        print(f"Editor not found: {EDITOR}")
        print("Set EDITOR environment variable or install nano.")
        os.unlink(temp_path)
        return None
    
    # Read content
    with open(temp_path, 'r') as f:
        content = f.read()
    
    os.unlink(temp_path)
    
    # Check if content was actually written (beyond the prompt)
    if content.strip() == prompt.strip():
        print("No content added. Entry not saved.")
        return None
    
    # Save to database
    word_count = len(content.split())
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO journal_entries (entry_type, content, mood, tags, word_count)
        VALUES (?, ?, ?, ?, ?)
    """, (entry_type, content, mood, tags, word_count))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✓ Entry #{entry_id} saved ({word_count} words)")
    return entry_id


def list_entries(entry_type: str = None, days: int = None, limit: int = 20):
    """List recent journal entries."""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT id, created_at, entry_type, word_count, mood FROM journal_entries WHERE 1=1"
    params = []
    
    if entry_type:
        query += " AND entry_type = ?"
        params.append(entry_type)
    
    if days:
        cutoff = datetime.now() - timedelta(days=days)
        query += " AND created_at >= ?"
        params.append(cutoff.isoformat())
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No entries found.")
        return
    
    print(f"\n{'ID':>5} {'Date':<12} {'Type':<15} {'Words':>6} {'Mood':<10}")
    print("-" * 55)
    
    for row in rows:
        date_str = row['created_at'][:10] if row['created_at'] else "N/A"
        mood_str = row['mood'] or ""
        print(f"{row['id']:>5} {date_str:<12} {row['entry_type']:<15} {row['word_count']:>6} {mood_str:<10}")


def view_entry(entry_id: int):
    """View a specific journal entry."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"Entry #{entry_id} not found.")
        return
    
    print(f"\n{'='*60}")
    print(f"Entry #{row['id']} - {row['entry_type']}")
    print(f"Created: {row['created_at']}")
    if row['mood']:
        print(f"Mood: {row['mood']}")
    if row['tags']:
        print(f"Tags: {row['tags']}")
    print(f"{'='*60}\n")
    print(row['content'])


def search_entries(query: str, limit: int = 20):
    """Search entries by content."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, created_at, entry_type, word_count 
        FROM journal_entries 
        WHERE content LIKE ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (f"%{query}%", limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No entries matching '{query}'")
        return
    
    print(f"\nEntries matching '{query}':")
    print(f"\n{'ID':>5} {'Date':<12} {'Type':<15} {'Words':>6}")
    print("-" * 45)
    
    for row in rows:
        date_str = row['created_at'][:10] if row['created_at'] else "N/A"
        print(f"{row['id']:>5} {date_str:<12} {row['entry_type']:<15} {row['word_count']:>6}")


def list_types():
    """List available entry types."""
    print("\nAvailable Entry Types:")
    print("=" * 50)
    for name, desc in ENTRY_TYPES.items():
        print(f"  {name:<15} - {desc}")


def main():
    parser = argparse.ArgumentParser(description="Journal CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # New entry
    new_parser = subparsers.add_parser("new", help="Create new entry")
    new_parser.add_argument("type", nargs="?", default="journal", help="Entry type")
    new_parser.add_argument("--mood", help="Current mood")
    new_parser.add_argument("--tags", help="Tags (comma-separated)")
    
    # List entries
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("--type", help="Filter by type")
    list_parser.add_argument("--days", type=int, help="Last N days")
    list_parser.add_argument("--limit", type=int, default=20, help="Max entries")
    
    # View entry
    view_parser = subparsers.add_parser("view", help="View entry")
    view_parser.add_argument("id", type=int, help="Entry ID")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search entries")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=20, help="Max results")
    
    # Types
    subparsers.add_parser("types", help="List entry types")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "new":
        new_entry(args.type, args.mood, args.tags)
    elif args.command == "list":
        list_entries(args.type, args.days, args.limit)
    elif args.command == "view":
        view_entry(args.id)
    elif args.command == "search":
        search_entries(args.query, args.limit)
    elif args.command == "types":
        list_types()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

