#!/usr/bin/env python3
"""
Meeting Ingestion Skill - Unified CLI

Single entry point for all meeting ingestion operations.

Usage:
    python3 meeting_cli.py pull [--dry-run] [--batch-size N]
    python3 meeting_cli.py process [meeting_path] [--blocks B01,B05]
    python3 meeting_cli.py status [--json]
    python3 meeting_cli.py list [--pending|--processed|--all]
"""

import sys
import json
import argparse
from pathlib import Path

# Add skill scripts to path
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

# Add N5/scripts to path
import os
WORKSPACE = Path(os.environ.get("ZO_WORKSPACE", "/home/workspace"))
sys.path.insert(0, str(WORKSPACE / "N5/scripts"))


def cmd_pull(args):
    """Handle pull command."""
    from pull import pull_transcripts
    
    results = pull_transcripts(
        dry_run=args.dry_run,
        batch_size=args.batch_size
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Pull Results:")
        print(f"  Ingested: {len(results['ingested'])}")
        print(f"  Skipped:  {len(results['skipped'])}")
        print(f"  Errors:   {len(results['errors'])}")
        
        if results['ingested']:
            print("\nIngested files:")
            for item in results['ingested']:
                print(f"  - {item['file']}")
        
        if results['errors']:
            print("\nErrors:")
            for item in results['errors']:
                print(f"  - {item['file']}: {item['error']}")
    
    return 0 if not results['errors'] else 1


def cmd_process(args):
    """Handle process command."""
    from processor import process_meeting, process_queue
    
    blocks = None
    if args.blocks:
        blocks = [b.strip().upper() for b in args.blocks.split(",")]
    
    if args.meeting_path:
        meeting_path = Path(args.meeting_path)
        if not meeting_path.exists():
            print(f"Error: Path not found: {meeting_path}")
            return 1
        
        results = process_meeting(
            meeting_path,
            blocks=blocks,
            dry_run=args.dry_run
        )
    else:
        results = process_queue(
            batch_size=args.batch_size,
            blocks=blocks,
            dry_run=args.dry_run
        )
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if "meetings" in results:
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Queue Processing:")
            print(f"  Processed: {results['processed']}")
            print(f"  Succeeded: {results['succeeded']}")
            print(f"  Failed:    {results['failed']}")
        else:
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Meeting Processed:")
            print(f"  Path: {results.get('meeting_path')}")
            print(f"  Type: {results.get('meeting_type')}")
            print(f"  Blocks generated: {len(results.get('blocks_generated', []))}")
            if results.get('blocks_generated'):
                for block in results['blocks_generated']:
                    print(f"    - {block}")
    
    return 0


def cmd_status(args):
    """Handle status command."""
    from meeting_registry import MeetingRegistry
    
    registry = MeetingRegistry()
    stats = registry.get_stats()
    
    # Count meetings in staging
    staging_dir = WORKSPACE / "Personal/Meetings/Inbox"
    pending_count = 0
    if staging_dir.exists():
        for item in staging_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                pending_count += 1
            elif item.is_dir() and not item.name.startswith("."):
                pending_count += 1
    
    status = {
        "registry": {
            "total_meetings": stats.get("total_meetings", 0),
            "unique_dates": stats.get("unique_dates", 0),
            "total_files": stats.get("total_files", 0),
            "processed": stats.get("processed", 0),
            "pending": stats.get("pending", 0),
            "earliest_date": stats.get("earliest_date"),
            "latest_date": stats.get("latest_date")
        },
        "staging": {
            "pending_items": pending_count,
            "path": str(staging_dir)
        }
    }
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("\nMeeting Ingestion Status")
        print("=" * 40)
        print("\nRegistry:")
        print(f"  Total meetings:  {status['registry']['total_meetings']}")
        print(f"  Processed:       {status['registry']['processed']}")
        print(f"  Pending:         {status['registry']['pending']}")
        if status['registry']['earliest_date']:
            print(f"  Date range:      {status['registry']['earliest_date']} to {status['registry']['latest_date']}")
        print("\nStaging Queue:")
        print(f"  Pending items:   {status['staging']['pending_items']}")
        print(f"  Location:        {status['staging']['path']}")
    
    return 0


def cmd_list(args):
    """Handle list command."""
    from meeting_registry import MeetingRegistry
    
    registry = MeetingRegistry()
    
    filters = {}
    if args.pending:
        filters['status'] = 'pending'
    elif args.processed:
        filters['status'] = 'processed'
    # else: no filter (all)
    
    meetings = registry.list_meetings(
        filters=filters if filters else None,
        limit=args.limit
    )
    
    if args.json:
        print(json.dumps(meetings, indent=2))
    else:
        status_label = "Pending" if args.pending else "Processed" if args.processed else "All"
        print(f"\n{status_label} Meetings (showing {len(meetings)}):")
        print("-" * 60)
        
        for meeting in meetings:
            status = meeting.get('status', 'unknown')
            status_icon = "✓" if status == 'processed' else "○"
            print(f"  {status_icon} {meeting.get('date', 'N/A')} - {meeting.get('folder_name', 'N/A')}")
            if args.verbose:
                participants = meeting.get('participants_normalized', [])
                print(f"      Participants: {', '.join(participants)}")
                print(f"      Files: {meeting.get('file_count', 0)}")
    
    return 0


def cmd_archive(args):
    """Handle archive command."""
    from archive import main as archive_main
    
    dry_run = not args.execute
    results = archive_main(dry_run=dry_run)
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Meeting Ingestion Skill CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    meeting_cli.py pull --dry-run          # Preview files to download
    meeting_cli.py pull --batch-size 10    # Download up to 10 transcripts
    meeting_cli.py process                 # Process all pending meetings
    meeting_cli.py process /path/to/meeting --blocks B01,B05,B08
    meeting_cli.py status                  # Show queue status
    meeting_cli.py list --pending          # List pending meetings
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Download transcripts from Google Drive')
    pull_parser.add_argument('--dry-run', action='store_true', help='Preview without downloading')
    pull_parser.add_argument('--batch-size', type=int, default=5, help='Max files to download')
    pull_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process meeting transcripts')
    process_parser.add_argument('meeting_path', nargs='?', help='Specific meeting to process')
    process_parser.add_argument('--blocks', type=str, help='Comma-separated block codes (e.g., B01,B05,B08)')
    process_parser.add_argument('--batch-size', type=int, default=5, help='Max meetings to process from queue')
    process_parser.add_argument('--dry-run', action='store_true', help='Preview without processing')
    process_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show ingestion status')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List meetings in registry')
    list_parser.add_argument('--pending', action='store_true', help='Show only pending')
    list_parser.add_argument('--processed', action='store_true', help='Show only processed')
    list_parser.add_argument('--all', action='store_true', help='Show all (default)')
    list_parser.add_argument('--limit', type=int, default=20, help='Max results')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Show details')
    list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive processed meetings to weekly folders')
    archive_parser.add_argument('--dry-run', action='store_true', default=True, help='Preview without executing (default)')
    archive_parser.add_argument('--execute', action='store_true', help='Actually perform archival')
    archive_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handler
    handlers = {
        'pull': cmd_pull,
        'process': cmd_process,
        'status': cmd_status,
        'list': cmd_list,
        'archive': cmd_archive
    }
    
    handler = handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
