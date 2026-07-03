# Digest Creation Protocol

**Purpose:** Standard workflow for creating new daily digest types in N5  
**Version:** 1.0  
**Updated:** 2025-10-13

---

## Overview

This protocol defines the standard process for creating new daily digest systems. Follow this workflow to ensure consistency, reliability, and maintainability across all digest implementations.

**Existing Digests:**
- Meeting Prep Digest → `file 'N5/digests/daily-meeting-prep-YYYY-MM-DD.md'`
- Newsletter Digest → `file 'N5/knowledge/digests/YYYY-MM-DD.md'`

---

## Pre-Flight Checklist

Before starting, gather:

1. **Clear Purpose** — What does this digest do? Who is it for?
2. **Data Sources** — Gmail, Calendar, web, local files, APIs?
3. **Output Format** — Sections, tables, BLUF, citations?
4. **Frequency** — Daily, weekday-only, weekly?
5. **Delivery** — Email, file only, SMS?
6. **Success Criteria** — How do we know it's working?

**Load Required Principles:**
- `file 'Knowledge/architectural/principles/core.md'` (SSOT)
- `file 'Knowledge/architectural/principles/safety.md'` (dry-run, error handling)
- `file 'Knowledge/architectural/principles/quality.md'` (Complete, Verify state)

---

## Phase 1: Design & Planning

### 1.1 Define Digest Structure

Create planning document in conversation workspace:

```markdown
# [Digest Name] Design

## Purpose
One-sentence description of what this digest accomplishes.

## Data Sources
- Gmail: specific queries or filters
- Calendar: event types, tags
- Web: specific sites or searches
- Files: local knowledge base areas
- APIs: external services

## Output Format
### Section 1: [Name]
- Bullet format? Table? Prose?
- What data appears here?

### Section 2: [Name]
...

## Exclusions
What should NOT appear in this digest?

## Output Location
Where does the file get saved?
Pattern: YYYY-MM-DD.md or daily-[name]-YYYY-MM-DD.md

## Delivery Method
- File only
- Email (subject line format)
- SMS
- Multiple channels

## Success Metrics
How do we verify this is working correctly?
```

### 1.2 Check for Existing Components

**Search before building:**

```bash
# Check if similar digest exists
grep -ri "keyword" /home/workspace/N5/commands/
grep -ri "keyword" /home/workspace/N5/scripts/

# Check existing digest scripts for reusable code
ls -la /home/workspace/N5/scripts/*digest*.py

# Check if output location conflicts
ls -la /home/workspace/N5/digests/
ls -la /home/workspace/N5/knowledge/digests/
```

### 1.3 Define Complete

**Before writing any code, explicitly define "complete":**

```markdown
## Definition of Complete

Script must:
- [ ] Accept --date parameter (default: today)
- [ ] Accept --dry-run flag
- [ ] Fetch data from [sources]
- [ ] Filter/process data per exclusions
- [ ] Generate markdown output
- [ ] Save to correct location
- [ ] Log timestamp and summary
- [ ] Return exit code 0 on success

Output must include:
- [ ] [Section 1]
- [ ] [Section 2]
- [ ] Timestamp footer
- [ ] Source citations (if web content)

Testing complete when:
- [ ] Dry-run works without errors
- [ ] Production run creates valid file
- [ ] File appears in correct location
- [ ] Content matches design spec
- [ ] Fresh thread test passes
```

---

## Phase 2: Implementation

### 2.1 Create Script

**Location:** `file 'N5/scripts/[digest_name].py'`

**Template Structure:**

```python
#!/usr/bin/env python3
"""
[Digest Name] Generator

Purpose: [One-line description]
Output: N5/[location]/[pattern].md
Version: 1.0.0
Updated: YYYY-MM-DD
"""

import argparse
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %Z"
)
logger = logging.getLogger(__name__)

# Constants
OUTPUT_DIR = Path("/home/workspace/N5/[location]")
WORKSPACE = Path("/home/workspace")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate [digest name] digest"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=date.today().isoformat(),
        help="Date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without saving"
    )
    return parser.parse_args()


def validate_inputs(target_date: date) -> bool:
    """Validate inputs before processing."""
    # Add validation logic
    return True


def fetch_data(target_date: date) -> dict:
    """Fetch raw data from sources."""
    try:
        data = {}
        # Fetch from Gmail
        # Fetch from Calendar
        # Fetch from files
        # Fetch from web/APIs
        return data
    except Exception as e:
        logger.error(f"Data fetch failed: {e}", exc_info=True)
        raise


def process_data(raw_data: dict, target_date: date) -> dict:
    """Filter and transform data per digest logic."""
    processed = {}
    # Apply filters
    # Transform for output format
    # Apply exclusions
    return processed


def generate_markdown(data: dict, target_date: date) -> str:
    """Generate markdown output from processed data."""
    md_lines = [
        f"# [Digest Title] — {target_date.strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
    ]
    
    # Add sections
    # Add timestamp footer
    
    # Footer
    et_tz = "America/New_York"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
    md_lines.extend([
        "",
        "---",
        "",
        f"*Generated: {timestamp}*"
    ])
    
    return "\n".join(md_lines)


def save_output(content: str, target_date: date, dry_run: bool) -> Path:
    """Save digest to file."""
    output_path = OUTPUT_DIR / f"[pattern]-{target_date.isoformat()}.md"
    
    if dry_run:
        logger.info(f"[DRY RUN] Would save to: {output_path}")
        logger.info(f"[DRY RUN] Content preview:\n{content[:500]}...")
        return output_path
    
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"✓ Saved: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save: {e}", exc_info=True)
        raise


def verify_output(output_path: Path, dry_run: bool) -> bool:
    """Verify file was created successfully."""
    if dry_run:
        return True
    
    if not output_path.exists():
        logger.error(f"Output file not found: {output_path}")
        return False
    
    if output_path.stat().st_size == 0:
        logger.error(f"Output file is empty: {output_path}")
        return False
    
    logger.info(f"✓ Verified: {output_path} ({output_path.stat().st_size} bytes)")
    return True


def main() -> int:
    """Main execution flow."""
    try:
        args = parse_args()
        target_date = date.fromisoformat(args.date)
        
        logger.info(f"Generating [digest name] for {target_date}")
        
        # Validate
        if not validate_inputs(target_date):
            logger.error("Input validation failed")
            return 1
        
        # Fetch
        raw_data = fetch_data(target_date)
        logger.info(f"Fetched data from {len(raw_data)} sources")
        
        # Process
        processed = process_data(raw_data, target_date)
        
        # Generate
        content = generate_markdown(processed, target_date)
        
        # Save
        output_path = save_output(content, target_date, args.dry_run)
        
        # Verify
        if not verify_output(output_path, args.dry_run):
            return 1
        
        logger.info(f"✓ Complete: [digest name] for {target_date}")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
```

**Requirements:**
- ✅ Logging with timestamps
- ✅ `--dry-run` flag
- ✅ `--date` parameter
- ✅ Error handling with context
- ✅ State verification
- ✅ Exit codes (0=success, 1=failure)
- ✅ Type hints
- ✅ Docstrings

### 2.2 Test Script in Isolation

```bash
# Make executable
chmod +x /home/workspace/N5/scripts/[digest_name].py

# Test dry-run
python3 /home/workspace/N5/scripts/[digest_name].py --dry-run

# Test with specific date
python3 /home/workspace/N5/scripts/[digest_name].py --date 2025-10-14 --dry-run

# Production test
python3 /home/workspace/N5/scripts/[digest_name].py --date 2025-10-14

# Verify output
ls -lah /home/workspace/N5/[location]/
cat /home/workspace/N5/[location]/[output-file].md
```

---

## Phase 3: Documentation

### 3.1 Create Command Documentation

**Location:** `file 'N5/commands/[digest-name].md'`

**Template:**

```markdown
# `[digest-name]`

[One-line description]

**Version:** 1.0.0  
**Updated:** YYYY-MM-DD

---

## Usage

\`\`\`bash
# Generate digest for today
[digest-name]

# Generate for specific date
[digest-name] --date 2025-10-12

# Preview without saving
[digest-name] --dry-run
\`\`\`

---

## Description

[2-3 paragraph description of what this digest does]

**What it does:**

1. **[Step 1]** — Description
2. **[Step 2]** — Description
3. **[Step 3]** — Description

**Exclusions:**
- [What gets filtered out]
- [What gets skipped]

**Output:**
- Location: `N5/[location]/[pattern]-YYYY-MM-DD.md`
- Format: Markdown with [sections]
- Includes: [key elements]

---

## Data Sources

### [Source 1]
- **Query:** [specific query or filter]
- **Lookback:** [time range]
- **Fields:** [what data is extracted]

### [Source 2]
...

---

## Output Format

### Section 1: [Name]
[Description of content and format]

### Section 2: [Name]
...

---

## Examples

### Example Output

\`\`\`markdown
# [Digest Title] — 2025-10-13

## [Section 1]
...

## [Section 2]
...
\`\`\`

---

## Scheduling

**Recommended Schedule:**
- **Frequency:** Daily at [time] ET
- **Delivery:** [Email/File/SMS]
- **RRULE:** `FREQ=DAILY;BYHOUR=[H];BYMINUTE=[M]`

**Create Scheduled Task:**

\`\`\`bash
# Generation task
create_scheduled_task(
    rrule="FREQ=DAILY;BYHOUR=[H];BYMINUTE=[M]",
    instruction="Execute [digest-name] command",
    delivery_method=None  # or "email"
)

# Optional: Email delivery task (if separate)
create_scheduled_task(
    rrule="FREQ=DAILY;BYHOUR=[H+0:30];BYMINUTE=[M]",
    instruction="Email digest to user",
    delivery_method="email"
)
\`\`\`

---

## Troubleshooting

### Issue: No output generated

**Check:**
1. Data sources accessible (API credentials, file permissions)
2. Date format valid (YYYY-MM-DD)
3. Output directory exists and writable
4. Run with `--dry-run` to see preview

### Issue: Missing expected content

**Check:**
1. Filters/exclusions too restrictive
2. Date range includes expected data
3. Source queries correct
4. Run script with logging to see fetch results

### Issue: Scheduled task failed

**Check:**
1. Task logs in scheduled task output
2. Script runs manually without errors
3. Production config tested (Principle 17)
4. Fresh thread test completed (Principle 12)

---

## Implementation

**Script:** `file 'N5/scripts/[digest_name].py'`  
**Protocol:** `file 'N5/prefs/operations/digest-creation-protocol.md'`  
**Principles:** `file 'Knowledge/architectural/architectural_principles.md'`

---

## Related Components

**Related Commands:** 
- `meeting-prep-digest` - Meeting intelligence digest
- `digest-runs` - Analyze digest execution history

**Related Scripts:**
- `file 'N5/scripts/[digest_name].py'` - Main generator

---

## Change Log

### 1.0.0 (YYYY-MM-DD)
- Initial implementation
- [Feature 1]
- [Feature 2]
```

---

## Phase 4: Integration

### 4.1 Register Command (Optional)

If creating a formal command (not just a script):

1. Add entry to `'Prompts/' (see recipe-execution-guide.md)`
2. Run `docgen` to update catalog
3. Test command invocation

### 4.2 Create Scheduled Tasks

```python
# Task 1: Generate digest
create_scheduled_task(
    rrule="FREQ=DAILY;BYHOUR=[H];BYMINUTE=[M]",
    instruction="Execute command '[digest-name]' or run script at /home/workspace/N5/scripts/[digest_name].py",
    delivery_method=None
)

# Task 2: Deliver digest (if separate)
create_scheduled_task(
    rrule="FREQ=DAILY;BYHOUR=[H+0:30];BYMINUTE=[M]",
    instruction="Read digest at file 'N5/[location]/[pattern]-{today}.md' and email with subject '[Subject Line]'",
    delivery_method="email"
)
```

**Verify scheduling:**
```python
list_scheduled_tasks()
```

---

## Phase 5: Testing & Verification

### 5.1 Testing Checklist

- [ ] **Dry-run:** Script runs with `--dry-run` without errors
- [ ] **Date parameter:** Works with past, present, future dates
- [ ] **Production run:** Creates file in correct location
- [ ] **Content validation:** Output matches design spec
- [ ] **File verification:** File exists, non-zero size, valid markdown
- [ ] **Error handling:** Graceful failure with clear error messages
- [ ] **Fresh thread test:** Works in clean conversation (Principle 12)
- [ ] **Production config:** Tested with real API credentials (Principle 17)
- [ ] **Scheduled execution:** Task runs at specified time
- [ ] **Email delivery:** Arrives with correct subject and formatting (if applicable)

### 5.2 Fresh Thread Test

**Critical for reliability:**

1. Start new conversation
2. Load minimal context (this protocol + command doc)
3. Execute: `[digest-name] --dry-run`
4. Execute: `[digest-name] --date 2025-10-14`
5. Verify output matches expectations

### 5.3 Production Test

**Run with real data:**

```bash
# Test today
python3 /home/workspace/N5/scripts/[digest_name].py

# Test past date (should have data)
python3 /home/workspace/N5/scripts/[digest_name].py --date 2025-10-10

# Test future date (should handle gracefully)
python3 /home/workspace/N5/scripts/[digest_name].py --date 2025-10-20
```

---

## Phase 6: Documentation & Handoff

### 6.1 Update System Documentation

Add to relevant docs:
- `file 'Documents/N5.md'` - Add to system status if major feature
- This protocol - Add to "Existing Digests" list
- `file 'N5/prefs/prefs.md'` - If introduces new preferences

### 6.2 Create Summary Document

Save to conversation workspace:

```markdown
# [Digest Name] Implementation Summary

## Created Files
- Script: `N5/scripts/[digest_name].py`
- Command Doc: `N5/commands/[digest-name].md`
- Output Location: `N5/[location]/`

## Scheduled Tasks
- Task ID: [id]
- Schedule: [description]
- Next Run: [timestamp]

## Testing Results
- [x] Dry-run passed
- [x] Production test passed
- [x] Fresh thread test passed
- [x] Scheduled task verified

## Usage
\`\`\`bash
[digest-name]
[digest-name] --date 2025-10-14
[digest-name] --dry-run
\`\`\`

## Next Steps
- Monitor first few scheduled runs
- Adjust filters if needed
- Gather user feedback
```

---

## Anti-Patterns

**❌ Skip dry-run implementation** → Always include `--dry-run` flag  
**❌ No error handling** → Wrap all I/O in try-catch with logging  
**❌ Claim complete prematurely** → Verify file writes, test in fresh thread  
**❌ Skip fresh thread test** → Critical for validating independence  
**❌ No state verification** → Always check file exists and is non-zero  
**❌ Hardcode credentials** → Use environment variables or secure storage  
**❌ Duplicate existing digest** → Check for similar functionality first  
**❌ Unclear success criteria** → Define "complete" before implementation  

---

## Maintenance

### Regular Checks
- Monitor scheduled task outputs
- Review generated digests for quality
- Update filters as data sources evolve
- Archive old digests per retention policy

### Updates
- Document all changes in command doc change log
- Test after any modifications
- Update version number
- Notify user of significant changes

---

## References

- **Architectural Principles:** `file 'Knowledge/architectural/architectural_principles.md'`
- **Script Template:** See Phase 2.1 in this document
- **Example Implementation:** `file 'N5/commands/meeting-prep-digest.md'`
- **Scheduling Guide:** `file 'N5/prefs/operations/scheduling.md'` (if exists)

---

**Version:** 1.0  
**Last Updated:** 2025-10-13  
**Next Review:** 2025-11-13
