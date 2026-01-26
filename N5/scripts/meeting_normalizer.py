#!/usr/bin/env python3
"""
Meeting Normalizer - Normalize dates, participant names, and generate canonical IDs
Handles various date formats and name variations for duplicate detection
"""

import re
from datetime import datetime
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def normalize_date(date_str: str) -> str:
    """
    Convert various date formats to canonical YYYY-MM-DD format.
    
    Handles:
    - YYYY-MM-DD (already canonical)
    - YYYYMMDD (compact)
    - MM/DD/YYYY (US format)
    - DD/MM/YYYY (EU format - ambiguous, assumes day < 13)
    - YYYY/MM/DD
    - Month DD, YYYY
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Date in YYYY-MM-DD format
    
    Raises:
        ValueError: If date format not recognized or invalid
    """
    date_str = date_str.strip()
    
    formats = [
        '%Y-%m-%d',      # 2025-11-14
        '%Y%m%d',        # 20251114
        '%m/%d/%Y',      # 11/14/2025
        '%d/%m/%Y',      # 14/11/2025
        '%Y/%m/%d',      # 2025/11/14
        '%B %d, %Y',     # November 14, 2025
        '%b %d, %Y',     # Nov 14, 2025
        '%Y.%m.%d',      # 2025.11.14
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    
    raise ValueError(f"Unrecognized date format: {date_str}")


def normalize_participant_name(name: str) -> str:
    """
    Normalize single participant name for matching.
    
    Rules:
    - Lowercase
    - Remove all separators (hyphens, underscores, spaces)
    - Remove punctuation
    - Trim whitespace
    
    Examples:
        "User-Two" -> "usertwo"
        "User_One" -> "userone"
        "John Smith" -> "johnsmith"
        "O'Brien" -> "obrien"
    
    Args:
        name: Participant name in any format
    
    Returns:
        Normalized name (lowercase, no separators)
    """
    name = name.strip().lower()
    
    name = re.sub(r'[_\-\s\'\.\,]', '', name)
    
    name = re.sub(r'[^a-z]', '', name)
    
    return name


def normalize_participants(participants: List[str]) -> List[str]:
    """
    Normalize list of participant names and sort alphabetically.
    
    Args:
        participants: List of participant names in any format
    
    Returns:
        Sorted list of normalized names
    """
    normalized = [normalize_participant_name(p) for p in participants if p.strip()]
    
    return sorted(set(normalized))


def generate_meeting_id(date: str, participants: List[str]) -> str:
    """
    Generate canonical meeting ID from date and participants.
    
    Format: YYYY-MM-DD_participant1-participant2-participant3
    
    Args:
        date: Date in YYYY-MM-DD format (should be pre-normalized)
        participants: List of normalized participant names
    
    Returns:
        Canonical meeting ID
    
    Examples:
        ('2025-11-14', ['usertwo', 'userone']) 
        -> '2025-11-14_usertwo-userone'
    """
    if not participants:
        raise ValueError("Cannot generate meeting_id without participants")
    
    sorted_participants = sorted(participants)
    participant_str = '-'.join(sorted_participants)
    
    return f"{date}_{participant_str}"


def extract_date_from_folder_name(folder_name: str) -> Optional[str]:
    """
    Extract date from meeting folder name.
    
    Handles patterns like:
    - 2025-11-14_User-Two_User-One
    - 20251114_meeting
    - 2025-11-14_notes
    
    Args:
        folder_name: Name of meeting folder
    
    Returns:
        Normalized date (YYYY-MM-DD) if found, None otherwise
    """
    patterns = [
        r'^(\d{4}-\d{2}-\d{2})',      # YYYY-MM-DD at start
        r'^(\d{8})',                   # YYYYMMDD at start
        r'(\d{4}_\d{2}_\d{2})',        # YYYY_MM_DD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, folder_name)
        if match:
            date_str = match.group(1).replace('_', '-')
            try:
                return normalize_date(date_str)
            except ValueError:
                continue
    
    return None


def extract_participants_from_folder_name(folder_name: str) -> List[str]:
    """
    Extract participant names from meeting folder name.
    
    Handles patterns like:
    - 2025-11-14_User-Two_User-One -> ['usertwo', 'userone']
    - 2025-11-14_UserTwo-UserOne -> ['usertwo', 'userone']
    
    Args:
        folder_name: Name of meeting folder
    
    Returns:
        List of normalized participant names
    """
    # Extract the part after the date
    date_match = re.match(r'^\d{4}[_-]\d{2}[_-]\d{2}[_-](.+)$', folder_name)
    if not date_match:
        return []
    
    name_part = date_match.group(1)
    
    # Split on underscores (primary separator between different people)
    potential_names = name_part.split('_')
    
    # Filter out common non-name words and normalize each full name
    participants = []
    for name in potential_names:
        normalized = normalize_participant_name(name)
        if len(normalized) > 2 and not re.match(r'^(meeting|notes|call|sync|session)$', normalized):
            participants.append(normalized)
    
    # Return sorted unique names
    return sorted(set(participants))


def parse_folder_name(folder_name: str) -> Optional[dict]:
    """
    Parse meeting folder name to extract date and participants.
    
    Args:
        folder_name: Name of meeting folder
    
    Returns:
        Dict with 'date' and 'participants' keys if parseable, None otherwise
    """
    date = extract_date_from_folder_name(folder_name)
    if not date:
        return None
    
    participants = extract_participants_from_folder_name(folder_name)
    if not participants:
        return None
    
    return {
        'date': date,
        'participants': participants
    }


def main():
    """CLI for testing normalization functions"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Meeting Normalizer CLI")
    parser.add_argument("command", choices=['date', 'participants', 'id', 'parse', 'test'])
    parser.add_argument("--date", help="Date string to normalize")
    parser.add_argument("--participants", nargs='+', help="Participant names")
    parser.add_argument("--folder", help="Folder name to parse")
    
    args = parser.parse_args()
    
    if args.command == 'date':
        if not args.date:
            print("Error: --date required")
            return 1
        try:
            normalized = normalize_date(args.date)
            print(normalized)
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    elif args.command == 'participants':
        if not args.participants:
            print("Error: --participants required")
            return 1
        normalized = normalize_participants(args.participants)
        print(json.dumps(normalized))
    
    elif args.command == 'id':
        if not args.date or not args.participants:
            print("Error: --date and --participants required")
            return 1
        try:
            date = normalize_date(args.date)
            participants = normalize_participants(args.participants)
            meeting_id = generate_meeting_id(date, participants)
            print(meeting_id)
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    elif args.command == 'parse':
        if not args.folder:
            print("Error: --folder required")
            return 1
        result = parse_folder_name(args.folder)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'test':
        print("Running normalization tests...")
        
        tests = [
            {
                'name': 'Date normalization',
                'func': lambda: normalize_date('2025-11-14'),
                'expected': '2025-11-14'
            },
            {
                'name': 'Date compact format',
                'func': lambda: normalize_date('20251114'),
                'expected': '2025-11-14'
            },
            {
                'name': 'Date US format',
                'func': lambda: normalize_date('11/14/2025'),
                'expected': '2025-11-14'
            },
            {
                'name': 'Participant normalization (hyphen)',
                'func': lambda: normalize_participant_name('User-Two'),
                'expected': 'usertwo'
            },
            {
                'name': 'Participant normalization (underscore)',
                'func': lambda: normalize_participant_name('User_One'),
                'expected': 'userone'
            },
            {
                'name': 'Participant normalization (space)',
                'func': lambda: normalize_participant_name('John Smith'),
                'expected': 'johnsmith'
            },
            {
                'name': 'Participants list (sorted)',
                'func': lambda: normalize_participants(['Bob', 'Alice', 'Charlie']),
                'expected': ['alice', 'bob', 'charlie']
            },
            {
                'name': 'Meeting ID generation',
                'func': lambda: generate_meeting_id('2025-11-14', ['usertwo', 'userone']),
                'expected': '2025-11-14_usertwo-userone'
            },
            {
                'name': 'Extract date from folder',
                'func': lambda: extract_date_from_folder_name('2025-11-14_User-Two_User-One'),
                'expected': '2025-11-14'
            },
            {
                'name': 'Parse folder name',
                'func': lambda: parse_folder_name('2025-11-14_User-Two_User-One'),
                'expected': {'date': '2025-11-14', 'participants': ['usertwo', 'userone']}
            },
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                result = test['func']()
                if result == test['expected']:
                    print(f"✓ {test['name']}")
                    passed += 1
                else:
                    print(f"✗ {test['name']}")
                    print(f"  Expected: {test['expected']}")
                    print(f"  Got: {result}")
                    failed += 1
            except Exception as e:
                print(f"✗ {test['name']}: {e}")
                failed += 1
        
        print(f"\n{passed} passed, {failed} failed")
        return 0 if failed == 0 else 1
    
    return 0


if __name__ == "__main__":
    exit(main())


