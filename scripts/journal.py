#!/usr/bin/env python3
"""Wrapper for N5/scripts/journal.py — provides local CLI access"""
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent.parent
script = root / "N5/scripts/journal.py"

if not script.exists():
    print(f"ERROR: {script} not found", file=sys.stderr)
    sys.exit(1)

sys.exit(subprocess.run([sys.executable, str(script)] + sys.argv[1:]).returncode)

