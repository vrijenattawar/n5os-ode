---
name: meeting-ingestion
description: Unified skill for ingesting meeting transcripts from Google Drive and orchestrating the processing pipeline (recap, blocks). Replaces legacy MG-1 through MG-6 agent sequence.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0.0"
  created: 2026-01-26
---

# Meeting Ingestion Skill

Unified meeting transcript processing: download from Google Drive, generate intelligence blocks.

## Quick Start

```bash
# Check status
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status

# Pull new transcripts (preview)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --dry-run

# Pull and download
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --batch-size 5

# Process all pending meetings
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process

# Process specific meeting
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process /path/to/meeting --blocks B01,B05,B08
```

## Commands

### `pull`
Download meeting transcripts from Google Drive to staging area.

```bash
python3 scripts/meeting_cli.py pull [--dry-run] [--batch-size N] [--json]
```

**Options:**
- `--dry-run` - Preview files without downloading
- `--batch-size N` - Max files to download (default: 5)
- `--json` - Output results as JSON

**Workflow:**
1. Reads folder ID from `N5/config/drive_locations.yaml`
2. Lists files in Drive folder
3. Filters to unprocessed transcripts
4. Downloads and converts to markdown
5. Stages to `Personal/Meetings/Inbox/`

### `process`
Generate intelligence blocks for meeting transcripts.

```bash
python3 scripts/meeting_cli.py process [meeting_path] [options]
```

**Arguments:**
- `meeting_path` - Specific meeting folder or transcript (omit to process queue)

**Options:**
- `--blocks B01,B05,B08` - Specific blocks to generate (auto-detect if omitted)
- `--batch-size N` - Max meetings from queue (default: 5)
- `--dry-run` - Preview without processing
- `--json` - Output as JSON

**Workflow:**
1. Finds transcript in meeting folder
2. Detects meeting type (external/internal)
3. Generates manifest (which blocks to create)
4. Generates each intelligence block via LLM
5. Writes blocks to meeting folder
6. Updates folder name with state suffix

### `status`
Show current ingestion queue status.

```bash
python3 scripts/meeting_cli.py status [--json]
```

**Output:**
- Registry statistics (total, processed, pending)
- Staging queue count
- Date range of processed meetings

### `archive`
Archive processed meetings to weekly folders.

```bash
python3 scripts/meeting_cli.py archive [--dry-run] [--execute]
```

**Options:**
- `--dry-run` - Preview changes without executing (default)
- `--execute` - Actually perform archival
- `--json` - Output results as JSON

**Workflow:**
1. Scans `Personal/Meetings/Inbox/` for meetings
2. Checks each meeting's `manifest.json` for completion status
3. Moves ready meetings to `Personal/Meetings/Week-of-YYYY-MM-DD/` folders
4. Week folder calculated from meeting date (Monday of that week)
5. Handles duplicate folders by merging content

**Readiness Criteria (from manifest.json status):**
- Always ready: `ready_for_followup`, `crm_synced`, `complete`, `processed`
- Ready with conditions: `intelligence_generated` (requires FOLLOW_UP_EMAIL.md or marked no follow-up)
- Not ready: `manifest_generated`, `mg2_in_progress` (still processing)
- No manifest: Awaiting MG-1

### `list`
List meetings in the registry.

```bash
python3 scripts/meeting_cli.py list [--pending|--processed] [--limit N] [-v]
```

**Options:**
- `--pending` - Show only pending meetings
- `--processed` - Show only processed meetings
- `--limit N` - Max results (default: 20)
- `-v, --verbose` - Show participant details

## Intelligence Blocks

### External Meetings (Standard Set)
| Block | Description |
|-------|-------------|
| B01_DETAILED_RECAP | Comprehensive meeting summary |
| B02_COMMITMENTS | Explicit commitments made |
| B03_DECISIONS | Key decisions with rationale |
| B05_ACTION_ITEMS | Actions with owners and deadlines |
| B08_STAKEHOLDER_INTELLIGENCE | Insights about external stakeholders |
| B25_DELIVERABLES | Artifacts to be created |
| B26_MEETING_METADATA | Meeting metadata |

### Conditional Blocks
Generated based on transcript content:
- B04_OPEN_QUESTIONS - Unresolved questions
- B06_BUSINESS_CONTEXT - Business implications
- B07_TONE_AND_CONTEXT - Emotional/relationship context
- B10_RISKS_AND_FLAGS - Risks and concerns
- B13_PLAN_OF_ACTION - Coordinated next steps
- B21_KEY_MOMENTS - Significant moments/quotes
- B28_STRATEGIC_INTELLIGENCE - Long-term implications

### Internal Meetings (B40-B48)
Used for team meetings, co-founder syncs:
- B40_INTERNAL_DECISIONS
- B41_TEAM_COORDINATION
- B47_OPEN_DEBATES
- Plus conditional B42-B46, B48

## Meeting State Machine

```
[Raw] → _[M] (Manifested) → _[B] (Blocked)
```

| State | Suffix | Meaning |
|-------|--------|---------|
| Raw | (none) | Transcript present |
| Manifested | `_[M]` | Manifest generated |
| Blocked | `_[B]` | Intelligence blocks generated |

## Directory Structure

```
Skills/meeting-ingestion/
├── SKILL.md                    # This file
├── scripts/
│   ├── meeting_cli.py          # Unified CLI entry point
│   ├── pull.py                 # Google Drive ingestion
│   ├── processor.py            # Block generation pipeline
│   └── archive.py             # Meeting archival to weekly folders
├── references/
│   └── legacy_prompts.md       # Legacy prompt documentation
└── assets/
```

## Dependencies

This skill wraps existing N5 scripts:
- `N5/scripts/meeting_registry.py` - SQLite registry
- `N5/scripts/meeting_orchestrator.py` - Duplicate prevention
- `N5/scripts/meeting_normalizer.py` - Date/name normalization
- `N5/scripts/meeting_manifest_generator.py` - Block manifest
- `N5/scripts/meeting_crm_sync.py` - CRM synchronization

Configuration:
- `N5/config/drive_locations.yaml` - Google Drive folder IDs

## Typical Workflow

### Daily Processing
```bash
# Morning: Pull new transcripts
python3 scripts/meeting_cli.py pull

# Process the queue
python3 scripts/meeting_cli.py process

# Check status
python3 scripts/meeting_cli.py status
```

### Single Meeting
```bash
# Process specific meeting with custom blocks
python3 scripts/meeting_cli.py process /path/to/meeting \
    --blocks B01,B05,B08,B28
```

### Automation (Scheduled Agent)
```bash
# Single command for automated runs
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --batch-size 3 && \
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process --batch-size 3
```

## Troubleshooting

### "ZO_CLIENT_IDENTITY_TOKEN not set"
The skill uses Zo API for Google Drive access. This token is automatically available when running within Zo.

### "No transcript found"
Ensure the meeting folder contains a `.md` or `.txt` file with transcript content.

### Block generation fails
- Check transcript length (minimum ~100 characters)
- Review `N5/logs/meeting_processing.log` for details
- Try with `--blocks B01` to isolate issues

### Duplicate detection
The registry tracks processed meetings by date + participants. If a meeting appears as duplicate:
```bash
python3 N5/scripts/meeting_registry.py list --limit 10
```

## Migration from Legacy Agents

This skill replaces:
- Agent `afda82fa` (Google Drive scanner)
- MG-1 through MG-6 agent chain
- `Prompts/drive_meeting_ingestion.prompt.md`
- `Prompts/Analyze Meeting.prompt.md`

See `references/legacy_prompts.md` for detailed migration notes.
