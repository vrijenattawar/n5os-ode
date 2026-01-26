#!/usr/bin/env python3
"""
Meeting Manifest Generator - Enhanced with External/Internal Detection

Changes from original:
- Added detect_meeting_type() to classify meetings as external/internal/partnership
- Made B08_STAKEHOLDER_INTELLIGENCE mandatory for external meetings
- Kept canonical_blocks.yaml as documentation
- Minimal touch refactor
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional

def load_blocks_config(config_path: Path) -> Dict:
    """Load canonical blocks config (for documentation purposes)"""
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

def detect_meeting_type(meeting_dir: str) -> str:
    """
    Detect if meeting is external, internal, or partnership based on directory name.
    
    Rules:
    - Contains '_internal' or '_[M]' suffix → internal
    - Contains '_external', '_partnership', '_discovery', '_sales' → external
    - Contains '_coaching', '_advisory' → external
    - Default → external (conservative: generate stakeholder intel unless explicitly internal)
    
    Returns: 'external', 'internal', or 'partnership'
    """
    meeting_dir_lower = meeting_dir.lower()
    
    # Internal markers
    if '_internal' in meeting_dir_lower or meeting_dir_lower.endswith('_[m]'):
        return 'internal'
    
    # External/Partnership markers
    external_markers = [
        '_external', '_partnership', '_discovery', '_sales',
        '_coaching', '_advisory', '_demo', '_networking'
    ]
    
    for marker in external_markers:
        if marker in meeting_dir_lower:
            if marker == '_partnership':
                return 'partnership'
            return 'external'
    
    # Default to external (conservative approach)
    return 'external'

def generate_manifest(transcript_path: Path, meeting_dir: Optional[Path] = None) -> List[str]:
    """
    Generate meeting intelligence manifest based on transcript content and meeting type.
    
    Core blocks (always included):
    - B01_DETAILED_RECAP
    - B02_COMMITMENTS
    - B03_DECISIONS
    - B05_ACTION_ITEMS
    - B08_STAKEHOLDER_INTELLIGENCE (external meetings only)
    - B25_DELIVERABLES
    - B26_MEETING_METADATA
    
    Conditional blocks based on transcript analysis.
    """
    # Read transcript
    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")
    
    transcript = transcript_path.read_text()
    
    # Detect meeting type
    meeting_type = 'external'  # default
    if meeting_dir:
        meeting_type = detect_meeting_type(meeting_dir.name)
    
    # === CORE BLOCKS (always included) ===
    core_blocks = [
        "B01_DETAILED_RECAP",
        "B02_COMMITMENTS", 
        "B03_DECISIONS",
        "B05_ACTION_ITEMS",
        "B25_DELIVERABLES",
        "B26_MEETING_METADATA"
    ]
    
    # Add B08_STAKEHOLDER_INTELLIGENCE for external meetings
    if meeting_type in ['external', 'partnership']:
        core_blocks.insert(4, "B08_STAKEHOLDER_INTELLIGENCE")  # Insert after B05
    
    manifest = core_blocks.copy()
    
    # === CONDITIONAL BLOCKS (pattern matching on transcript) ===
    
    # B04_OPEN_QUESTIONS - if questions are raised
    question_patterns = [
        r'\?',
        r'\bwondering\b',
        r'\bunsure\b',
        r'\bneed to figure out\b',
        r'\bnot clear\b'
    ]
    if any(re.search(pattern, transcript, re.IGNORECASE) for pattern in question_patterns):
        if "B04_OPEN_QUESTIONS" not in manifest:
            manifest.append("B04_OPEN_QUESTIONS")
    
    # B06_BUSINESS_CONTEXT - if business/commercial discussion
    business_patterns = [
        r'\bpricing\b',
        r'\brevenue\b',
        r'\bcustomer\b',
        r'\bmarket\b',
        r'\bcompetitor\b',
        r'\bbusiness model\b'
    ]
    if any(re.search(pattern, transcript, re.IGNORECASE) for pattern in business_patterns):
        if "B06_BUSINESS_CONTEXT" not in manifest:
            manifest.append("B06_BUSINESS_CONTEXT")
    
    # B07_TONE_AND_CONTEXT - if emotional/interpersonal content
    tone_patterns = [
        r'\bexcited\b',
        r'\bconcerned\b',
        r'\bfrustrated\b',
        r'\bworried\b',
        r'\boptimistic\b',
        r'\bpessimistic\b'
    ]
    if any(re.search(pattern, transcript, re.IGNORECASE) for pattern in tone_patterns):
        if "B07_TONE_AND_CONTEXT" not in manifest:
            manifest.append("B07_TONE_AND_CONTEXT")
    
    # B10_RISKS_AND_FLAGS - if risks/concerns mentioned
    risk_patterns = [
        r'\brisk\b',
        r'\bconcern\b',
        r'\bwarning\b',
        r'\bproblem\b',
        r'\bissue\b',
        r'\bchallenge\b'
    ]
    if any(re.search(pattern, transcript, re.IGNORECASE) for pattern in risk_patterns):
        if "B10_RISKS_AND_FLAGS" not in manifest:
            manifest.append("B10_RISKS_AND_FLAGS")
    
    # B13_PLAN_OF_ACTION - if multiple stakeholders and action-oriented
    speaker_count = len(set(re.findall(r'^(\w+):', transcript, re.MULTILINE)))
    action_patterns = [
        r'\baction item\b',
        r'\bnext step\b',
        r'\bfollow up\b',
        r'\bwe should\b',
        r'\bwe need to\b'
    ]
    if speaker_count >= 2 and any(re.search(pattern, transcript, re.IGNORECASE) for pattern in action_patterns):
        if "B13_PLAN_OF_ACTION" not in manifest:
            manifest.append("B13_PLAN_OF_ACTION")
    
    # B21_KEY_MOMENTS - if significant moments/quotes
    moment_patterns = [
        r'\bbreakthrough\b',
        r'\bkey insight\b',
        r'\bimportant\b',
        r'\bcrucial\b',
        r'\bturning point\b'
    ]
    if any(re.search(pattern, transcript, re.IGNORECASE) for pattern in moment_patterns):
        if "B21_KEY_MOMENTS" not in manifest:
            manifest.append("B21_KEY_MOMENTS")
    
    # B28_STRATEGIC_INTELLIGENCE - if strategic discussion
    strategic_patterns = [
        r'\bstrategy\b',
        r'\blong.term\b',
        r'\bvision\b',
        r'\bdirection\b',
        r'\bpriorities\b'
    ]
    if any(re.search(pattern, transcript, re.IGNORECASE) for pattern in strategic_patterns):
        if "B28_STRATEGIC_INTELLIGENCE" not in manifest:
            manifest.append("B28_STRATEGIC_INTELLIGENCE")
    
    return manifest

def main():
    """Test the manifest generator"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python meeting_manifest_generator.py <transcript_path> [meeting_dir]")
        sys.exit(1)
    
    transcript_path = Path(sys.argv[1])
    meeting_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    try:
        manifest = generate_manifest(transcript_path, meeting_dir)
        print("Generated Manifest:")
        for block in manifest:
            print(f"  - {block}")
        
        if meeting_dir:
            meeting_type = detect_meeting_type(meeting_dir.name)
            print(f"\nMeeting Type: {meeting_type}")
            print(f"B08 Generated: {'Yes' if 'B08_STAKEHOLDER_INTELLIGENCE' in manifest else 'No'}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

