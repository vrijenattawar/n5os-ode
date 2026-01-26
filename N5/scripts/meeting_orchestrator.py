#!/usr/bin/env python3
"""
Meeting Orchestrator - Central coordination for meeting ingestion
Single entry point preventing duplicates through pre-creation checks
"""

import sys
import logging
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from meeting_registry import MeetingRegistry
from meeting_normalizer import (
    normalize_date,
    normalize_participants,
    generate_meeting_id,
    parse_folder_name
)
from meeting_config import WORKSPACE, MEETINGS_DIR, STAGING_DIR, LOG_DIR, REGISTRY_DB, TIMEZONE, ENABLE_SMS

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path(MEETINGS_DIR)
LOG_FILE = Path(LOG_DIR) / "meeting_orchestrator.log"


class MeetingOrchestrator:
    """
    Orchestrates meeting ingestion with duplicate prevention.
    
    Decision logic:
    - Exact match (date + participants): SKIP
    - Fuzzy match >90% similarity: MERGE (add files to existing)
    - No match: CREATE new meeting folder
    """
    
    def __init__(
        self, 
        registry: Optional[MeetingRegistry] = None,
        meetings_dir: Optional[Path] = None,
        fuzzy_threshold: float = 0.90
    ):
        self.registry = registry or MeetingRegistry()
        self.meetings_dir = Path(meetings_dir or MEETINGS_DIR)
        self.fuzzy_threshold = fuzzy_threshold
        
        self.meetings_dir.mkdir(parents=True, exist_ok=True)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(logging.Formatter("%(asctime)sZ %(levelname)s %(message)s"))
        logger.addHandler(file_handler)
    
    def ingest_meeting(
        self,
        transcript_path: Optional[str] = None,
        date: Optional[str] = None,
        participants: Optional[List[str]] = None,
        source: str = "unknown",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point for meeting ingestion.
        
        Args:
            transcript_path: Path to transcript file (optional if just checking)
            date: Meeting date (any format, will be normalized)
            participants: List of participant names (any format)
            source: Source of meeting (google_drive, gmail, manual, etc)
            dry_run: If True, only check for duplicates, don't create
        
        Returns:
            Dict with:
                action: "created" | "skipped" | "merged" | "checked"
                meeting_id: Canonical meeting ID
                folder_path: Path to meeting folder (if created/merged)
                reason: Human-readable reason for action
                similarity_score: If fuzzy match (optional)
        """
        try:
            if not date or not participants:
                raise ValueError("date and participants are required")
            
            normalized_date = normalize_date(date)
            normalized_participants = normalize_participants(participants)
            meeting_id = generate_meeting_id(normalized_date, normalized_participants)
            
            logger.info(f"Processing meeting: {meeting_id} (source: {source})")
            
            exact_match = self._check_exact_duplicate(normalized_date, normalized_participants)
            if exact_match:
                result = {
                    'action': 'skipped',
                    'meeting_id': exact_match['meeting_id'],
                    'folder_path': str(self.meetings_dir / exact_match['folder_name']),
                    'reason': f"Exact duplicate found: {exact_match['folder_name']}"
                }
                logger.warning(f"SKIP: {result['reason']}")
                return result
            
            fuzzy_matches = self._check_fuzzy_duplicates(
                normalized_date, 
                normalized_participants
            )
            
            if fuzzy_matches:
                best_match = fuzzy_matches[0]
                
                if dry_run:
                    result = {
                        'action': 'checked',
                        'meeting_id': meeting_id,
                        'reason': f"Would merge with {best_match['folder_name']} (similarity: {best_match['similarity_score']:.2%})",
                        'similarity_score': best_match['similarity_score']
                    }
                    logger.info(f"CHECK: {result['reason']}")
                    return result
                
                result = self._merge_meeting(
                    best_match['meeting_id'],
                    transcript_path,
                    similarity_score=best_match['similarity_score']
                )
                logger.info(f"MERGE: {result['reason']}")
                return result
            
            if dry_run:
                result = {
                    'action': 'checked',
                    'meeting_id': meeting_id,
                    'reason': f"No duplicates found, would create {meeting_id}"
                }
                logger.info(f"CHECK: {result['reason']}")
                return result
            
            result = self._create_meeting(
                meeting_id,
                normalized_date,
                normalized_participants,
                transcript_path,
                source
            )
            logger.info(f"CREATE: {result['reason']}")
            return result
            
        except Exception as e:
            logger.error(f"Error ingesting meeting: {e}", exc_info=True)
            return {
                'action': 'error',
                'meeting_id': None,
                'reason': str(e)
            }
    
    def _check_exact_duplicate(
        self, 
        date: str, 
        participants: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Check registry for exact match"""
        return self.registry.find_duplicate(date, participants)
    
    def _check_fuzzy_duplicates(
        self,
        date: str,
        participants: List[str]
    ) -> List[Dict[str, Any]]:
        """Check registry for fuzzy matches above threshold"""
        return self.registry.find_fuzzy_duplicates(
            date, 
            participants, 
            self.fuzzy_threshold
        )
    
    def _create_meeting(
        self,
        meeting_id: str,
        date: str,
        participants: List[str],
        transcript_path: Optional[str],
        source: str
    ) -> Dict[str, Any]:
        """Create new meeting folder and add to registry"""
        folder_name = self._generate_folder_name(date, participants)
        folder_path = self.meetings_dir / folder_name
        
        folder_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created folder: {folder_path}")
        
        file_count = 0
        if transcript_path:
            file_count = self._copy_transcript(transcript_path, folder_path)
        
        metadata = {
            'meeting_id': meeting_id,
            'date': date,
            'participants_normalized': participants,
            'folder_name': folder_name,
            'source': source,
            'file_count': file_count,
            'status': 'processed'
        }
        
        self.registry.add_meeting(metadata)
        
        return {
            'action': 'created',
            'meeting_id': meeting_id,
            'folder_path': str(folder_path),
            'reason': f"Created new meeting folder: {folder_name}"
        }
    
    def _merge_meeting(
        self,
        existing_meeting_id: str,
        transcript_path: Optional[str],
        similarity_score: float
    ) -> Dict[str, Any]:
        """Add transcript to existing meeting folder"""
        existing = self.registry.get_meeting(existing_meeting_id)
        if not existing:
            raise ValueError(f"Meeting {existing_meeting_id} not found in registry")
        
        folder_path = self.meetings_dir / existing['folder_name']
        
        file_count = existing.get('file_count', 0)
        if transcript_path:
            added = self._copy_transcript(transcript_path, folder_path)
            file_count += added
        
        self.registry.update_meeting(existing_meeting_id, {
            'file_count': file_count,
            'status': 'processed'
        })
        
        return {
            'action': 'merged',
            'meeting_id': existing_meeting_id,
            'folder_path': str(folder_path),
            'reason': f"Merged with existing: {existing['folder_name']} (similarity: {similarity_score:.2%})",
            'similarity_score': similarity_score
        }
    
    def _copy_transcript(self, source_path: str, dest_folder: Path) -> int:
        """
        Copy transcript file(s) to meeting folder.
        Returns number of files copied.
        """
        import shutil
        
        source = Path(source_path)
        if not source.exists():
            logger.warning(f"Transcript not found: {source}")
            return 0
        
        if source.is_file():
            dest = dest_folder / source.name
            shutil.copy2(source, dest)
            logger.info(f"Copied: {source.name} -> {dest}")
            return 1
        
        elif source.is_dir():
            count = 0
            for file in source.rglob('*'):
                if file.is_file():
                    rel_path = file.relative_to(source)
                    dest = dest_folder / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest)
                    count += 1
            logger.info(f"Copied {count} files from {source} -> {dest_folder}")
            return count
        
        return 0
    
    def _generate_folder_name(self, date: str, participants: List[str]) -> str:
        """
        Generate human-readable folder name.
        Format: YYYY-MM-DD_FirstLast_FirstLast
        """
        participant_parts = '_'.join(
            ''.join(word.capitalize() for word in p.split())
            for p in sorted(participants)
        )
        return f"{date}_{participant_parts}"
    
    def backfill_from_filesystem(
        self,
        limit: Optional[int] = None,
        lifo: bool = True
    ) -> Dict[str, Any]:
        """
        Scan filesystem and add existing meetings to registry.
        Gradual sync with LIFO prioritization (newest first).
        
        Args:
            limit: Maximum number of meetings to process (None = all)
            lifo: If True, process newest meetings first
        
        Returns:
            Dict with stats: processed, added, skipped, errors
        """
        logger.info(f"Starting backfill from {self.meetings_dir}")
        
        folders = [f for f in self.meetings_dir.iterdir() if f.is_dir()]
        
        if lifo:
            folders = sorted(folders, key=lambda f: f.stat().st_mtime, reverse=True)
        
        if limit:
            folders = folders[:limit]
        
        stats = {
            'processed': 0,
            'added': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for folder in folders:
            try:
                existing = self.registry.get_meeting_by_folder(folder.name)
                if existing:
                    logger.debug(f"Skip (already in registry): {folder.name}")
                    stats['skipped'] += 1
                    continue
                
                parsed = parse_folder_name(folder.name)
                if not parsed:
                    logger.warning(f"Cannot parse folder name: {folder.name}")
                    stats['errors'] += 1
                    continue
                
                meeting_id = generate_meeting_id(parsed['date'], parsed['participants'])
                
                file_count = len(list(folder.rglob('*')))
                
                metadata = {
                    'meeting_id': meeting_id,
                    'date': parsed['date'],
                    'participants_normalized': parsed['participants'],
                    'folder_name': folder.name,
                    'source': 'backfill',
                    'file_count': file_count,
                    'status': 'processed'
                }
                
                self.registry.add_meeting(metadata)
                logger.info(f"Added to registry: {folder.name}")
                stats['added'] += 1
                
            except Exception as e:
                logger.error(f"Error processing {folder.name}: {e}")
                stats['errors'] += 1
            
            stats['processed'] += 1
        
        logger.info(f"Backfill complete: {stats}")
        return stats


def main():
    """CLI for meeting orchestrator"""
    parser = argparse.ArgumentParser(description="Meeting Orchestrator CLI")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    ingest_parser = subparsers.add_parser('ingest', help='Ingest new meeting')
    ingest_parser.add_argument('--transcript', help='Path to transcript file/folder')
    ingest_parser.add_argument('--date', required=True, help='Meeting date')
    ingest_parser.add_argument('--participants', required=True, nargs='+', help='Participant names')
    ingest_parser.add_argument('--source', default='manual', help='Source (google_drive, gmail, manual)')
    ingest_parser.add_argument('--dry-run', action='store_true', help='Check only, don\'t create')
    
    check_parser = subparsers.add_parser('check', help='Check for duplicates')
    check_parser.add_argument('--date', required=True, help='Meeting date')
    check_parser.add_argument('--participants', required=True, nargs='+', help='Participant names')
    
    backfill_parser = subparsers.add_parser('backfill', help='Backfill registry from filesystem')
    backfill_parser.add_argument('--limit', type=int, help='Max meetings to process')
    backfill_parser.add_argument('--fifo', action='store_true', help='Process oldest first (default: newest)')
    
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    orchestrator = MeetingOrchestrator()
    
    if args.command == 'ingest':
        result = orchestrator.ingest_meeting(
            transcript_path=args.transcript,
            date=args.date,
            participants=args.participants,
            source=args.source,
            dry_run=args.dry_run
        )
        print(json.dumps(result, indent=2))
        return 0 if result['action'] != 'error' else 1
    
    elif args.command == 'check':
        result = orchestrator.ingest_meeting(
            date=args.date,
            participants=args.participants,
            dry_run=True
        )
        print(json.dumps(result, indent=2))
        return 0
    
    elif args.command == 'backfill':
        result = orchestrator.backfill_from_filesystem(
            limit=args.limit,
            lifo=not args.fifo
        )
        print(json.dumps(result, indent=2))
        return 0
    
    elif args.command == 'stats':
        stats = orchestrator.registry.get_stats()
        print(json.dumps(stats, indent=2))
        return 0
    
    return 0


if __name__ == "__main__":
    exit(main())

