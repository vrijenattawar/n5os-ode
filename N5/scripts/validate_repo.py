#!/usr/bin/env python3
"""
Validate n5OS-Ode repo for completeness and consistency.

Usage:
  python3 scripts/validate_repo.py [--verbose]
"""
import sys
import re
from pathlib import Path
import py_compile
import argparse

def main():
    parser = argparse.ArgumentParser(description="Validate n5OS-Ode repository")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # Script is at N5/scripts/, repo root is 2 levels up
    root = Path(__file__).resolve().parent.parent.parent
    errors = []
    warnings = []
    
    # 1. Check Python syntax
    py_files = sorted(root.rglob("*.py"))
    for pf in py_files:
        try:
            py_compile.compile(str(pf), doraise=True)
        except Exception as e:
            errors.append(f"Python syntax: {pf}: {e}")
    
    # 2. Check for file references in markdown/prompts
    file_ref_re = re.compile(r"`file '([^']+)'`")
    # Build set of relative paths from root
    existing = {str(p.relative_to(root)).replace('\\', '/') for p in root.rglob('*') if p.is_file()}
    
    md_files = list(root.rglob("*.md")) + list(root.rglob("*.prompt.md"))
    for md_file in md_files:
        try:
            txt = md_file.read_text(errors="ignore")
        except Exception:
            continue
        
        for m in file_ref_re.finditer(txt):
            ref = m.group(1)
            if ref.startswith('/'):
                continue
            ref_norm = ref.lstrip('./')
            if ref_norm not in existing:
                warnings.append(f"Missing file ref: {md_file.relative_to(root)}: {ref}")
    
    # 3. Check markdown links
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for md_file in root.rglob("*.md"):
        try:
            txt = md_file.read_text(errors="ignore")
        except Exception:
            continue
        
        for m in link_re.finditer(txt):
            url = m.group(1).strip()
            if url.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            url = url.split('#', 1)[0]
            if not url:
                continue
            
            try:
                target = (md_file.parent / url).resolve()
                rel = str(target.relative_to(root)).replace('\\', '/')
            except ValueError:
                continue
            
            if rel not in existing:
                warnings.append(f"Missing link target: {md_file.relative_to(root)}: {url}")
    
    # 4. Check for PROJECT_REPO placeholder (skip self to avoid false positive)
    placeholder_pattern = "PROJECT" + "_REPO"  # Split to avoid self-match
    for pf in root.rglob("*.py"):
        if pf.name == "validate_repo.py":
            continue  # Skip self
        try:
            txt = pf.read_text(errors="ignore")
        except Exception:
            continue
        if placeholder_pattern in txt:
            warnings.append(f"Placeholder {placeholder_pattern} found in: {pf.relative_to(root)}")
    
    # Report
    print("=" * 70)
    print("n5OS-Ode Repository Validation")
    print("=" * 70)
    print()
    
    if errors:
        print(f"❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        print()
    
    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")
        print()
    
    if not errors and not warnings:
        print("✅ All checks passed!")
        print()
    
    py_count = len(py_files)
    md_count = len(list(root.rglob("*.md"))) + len(list(root.rglob("*.prompt.md")))
    print(f"📊 Summary:")
    print(f"  Python files: {py_count}")
    print(f"  Markdown files: {md_count}")
    print()
    
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())


