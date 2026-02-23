#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml"]
# ///
"""
Validate Frontmatter Hook (Blocking)

Validates YAML frontmatter structure and required fields for a specific note type.
Used as a Stop hook to verify skill output has correct frontmatter.

Exit Codes:
  0 - Validation passed
  2 - Validation failed (blocking, feeds back to Claude)

Usage in skill frontmatter:
  hooks:
    Stop:
      - type: command
        command: >-
          python3 .claude/hooks/validators/validate_frontmatter.py
          --directory Memory/
          --type Note
          --required title,type,created
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Required fields by note type (MeKB types)
REQUIRED_FIELDS = {
    "Daily": ["type", "title", "date"],
    "Note": ["type", "title"],
    "Concept": ["type", "title"],
    "Task": ["type", "title", "completed", "priority"],
    "Project": ["type", "title", "status"],
    "Meeting": ["type", "title", "date", "attendees"],
    "Person": ["type", "title"],
    "Resource": ["type", "title"],
    "Decision": ["type", "title", "status"],
    "ActionItem": ["type", "title", "completed"],
    "Interaction": ["type", "title", "date"],
}


def find_latest_file(directory: Path, extension: str, within_minutes: int = 5) -> Path | None:
    if not directory.exists():
        return None

    cutoff = datetime.now() - timedelta(minutes=within_minutes)
    recent = []

    for file in directory.rglob(f"*{extension}"):
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if mtime > cutoff:
            recent.append((file, mtime))

    if not recent:
        return None

    return max(recent, key=lambda x: x[1])[0]


def parse_frontmatter_simple(content: str) -> dict | None:
    if not content.startswith("---"):
        return None

    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return None

    yaml_content = content[4:end_match.start() + 3]
    frontmatter = {}

    for line in yaml_content.split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip().strip('"\'')
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                value = [i.strip().strip('"\'') for i in items if i.strip()]
            frontmatter[key] = value

    return frontmatter


def parse_frontmatter(content: str) -> dict | None:
    if not content.startswith("---"):
        return None

    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return None

    yaml_content = content[4:end_match.start() + 3]

    if HAS_YAML:
        try:
            return yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            return parse_frontmatter_simple(content)
    else:
        return parse_frontmatter_simple(content)


def main():
    parser = argparse.ArgumentParser(description="Validate frontmatter structure")
    parser.add_argument("--file", help="Specific file to validate")
    parser.add_argument("--directory", help="Directory to find latest file in")
    parser.add_argument("--extension", default=".md", help="File extension")
    parser.add_argument("--type", dest="note_type", help="Expected note type")
    parser.add_argument("--required", help="Comma-separated required fields")
    parser.add_argument("--within-minutes", type=int, default=5, help="Check files modified within N minutes")
    args = parser.parse_args()

    vault_root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))

    if args.file:
        target = vault_root / args.file
        if not target.exists():
            print(f"ERROR: File not found: {args.file}")
            sys.exit(2)
    elif args.directory:
        directory = vault_root / args.directory
        target = find_latest_file(directory, args.extension, args.within_minutes)
        if not target:
            print(f"ERROR: No recent {args.extension} files found in {args.directory}")
            sys.exit(2)
    else:
        print("ERROR: Must specify either --file or --directory")
        sys.exit(2)

    print(f"Validating frontmatter: {target.relative_to(vault_root)}")

    content = target.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(content)

    if not frontmatter:
        print("ERROR: No valid frontmatter found")
        print("File should start with --- and have closing ---")
        sys.exit(2)

    print("Frontmatter parsed successfully")

    errors = []

    actual_type = frontmatter.get("type", "")
    if args.note_type and actual_type != args.note_type:
        print(f"Expected type '{args.note_type}', got '{actual_type}'")
        errors.append(f"type should be '{args.note_type}'")
    elif actual_type:
        print(f"Type: {actual_type}")

    required_fields = []
    if args.required:
        required_fields = [f.strip() for f in args.required.split(",")]
    elif args.note_type and args.note_type in REQUIRED_FIELDS:
        required_fields = REQUIRED_FIELDS[args.note_type]
    elif actual_type and actual_type in REQUIRED_FIELDS:
        required_fields = REQUIRED_FIELDS[actual_type]

    for field in required_fields:
        if field in frontmatter and frontmatter[field] not in (None, "", [], "null"):
            print(f"Has '{field}': {str(frontmatter[field])[:50]}")
        else:
            print(f"Missing or empty: '{field}'")
            errors.append(f"missing required field '{field}'")

    if errors:
        print(f"\nERROR: Frontmatter validation failed with {len(errors)} issues:")
        for e in errors:
            print(f"  - {e}")
        print("\nPlease fix these issues and try again.")
        sys.exit(2)

    print("\nAll frontmatter validations passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
