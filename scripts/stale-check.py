#!/usr/bin/env python3
"""
Stale Note Detection for MeKB
Finds notes that haven't been verified recently and may need review.

Usage:
    python3 scripts/stale-check.py              # Full report
    python3 scripts/stale-check.py --summary     # Summary only
    python3 scripts/stale-check.py --json        # JSON output
    python3 scripts/stale-check.py --type Concept # Filter by type

Dependencies: Python 3.9+ (stdlib only)
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Folders to skip
SKIP_DIRS = {
    ".git", ".obsidian", ".claude", ".mekb", ".graph",
    "node_modules", "__pycache__", ".venv", "venv",
    "secret", "Archive", "Templates",
}

# Staleness thresholds (days)
THRESHOLDS = {
    "critical": 180,  # 6+ months
    "high": 120,      # 4+ months
    "medium": 90,     # 3+ months
}

# Note types to prioritise
HIGH_VALUE_TYPES = {"Decision", "Concept", "Pattern", "Note"}

FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_field(yaml_text, field):
    """Extract a simple scalar field from YAML text."""
    match = re.search(rf"^{field}\s*:\s*(.+)$", yaml_text, re.MULTILINE)
    if match:
        value = match.group(1).strip().strip("'\"")
        if value in ("null", "~", ""):
            return None
        return value
    return None


def find_vault_root():
    """Find the vault root."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def should_skip(path, vault_root):
    """Check if a path should be skipped."""
    rel = path.relative_to(vault_root)
    for part in rel.parts[:-1]:
        if part in SKIP_DIRS:
            return True
    if path.suffix != ".md":
        return True
    return False


def parse_date(date_str):
    """Parse a date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def check_note(path, vault_root, today):
    """Check a single note for staleness."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError):
        return None

    fm_match = FM_PATTERN.match(content)
    if not fm_match:
        return None

    yaml_text = fm_match.group(1)
    note_type = extract_field(yaml_text, "type")
    title = extract_field(yaml_text, "title") or path.stem
    verified = extract_field(yaml_text, "verified")
    freshness = extract_field(yaml_text, "freshness")
    classification = extract_field(yaml_text, "classification")

    # Skip Daily notes (inherently time-bound)
    if note_type == "Daily":
        return None

    # Skip secret content
    if classification == "secret":
        return None

    rel_path = str(path.relative_to(vault_root))

    # Check staleness
    verified_date = parse_date(verified)
    if verified_date:
        days_since = (today - verified_date).days
    else:
        # Use file modification time as fallback
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        days_since = (today - mtime).days

    # Already marked stale in frontmatter
    if freshness == "stale":
        priority = "critical"
    elif days_since >= THRESHOLDS["critical"]:
        priority = "critical"
    elif days_since >= THRESHOLDS["high"]:
        priority = "high"
    elif days_since >= THRESHOLDS["medium"]:
        priority = "medium"
    else:
        return None  # Not stale

    # Boost priority for high-value types
    if note_type in HIGH_VALUE_TYPES and priority == "medium":
        priority = "high"

    return {
        "path": rel_path,
        "title": title,
        "type": note_type,
        "verified": verified,
        "days_since": days_since,
        "priority": priority,
        "has_verified_field": verified is not None,
    }


def main():
    parser = argparse.ArgumentParser(description="Find stale MeKB notes")
    parser.add_argument("--summary", action="store_true", help="Summary only")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--type", dest="note_type", help="Filter by note type")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    today = datetime.now()

    stale_notes = {"critical": [], "high": [], "medium": []}
    total_checked = 0

    for path in vault_root.rglob("*.md"):
        if should_skip(path, vault_root):
            continue

        total_checked += 1
        result = check_note(path, vault_root, today)
        if result:
            if args.note_type and result["type"] != args.note_type:
                continue
            stale_notes[result["priority"]].append(result)

    # Sort each priority by days_since descending
    for priority in stale_notes:
        stale_notes[priority].sort(key=lambda x: x["days_since"], reverse=True)

    total_stale = sum(len(v) for v in stale_notes.values())

    if args.json:
        output = {
            "total_checked": total_checked,
            "total_stale": total_stale,
            "by_priority": stale_notes,
        }
        print(json.dumps(output, indent=2))
        return

    if args.summary:
        print(f"\nStale Notes Summary")
        print(f"Checked: {total_checked} notes")
        print(f"Stale: {total_stale} notes")
        print(f"  Critical (6+ months): {len(stale_notes['critical'])}")
        print(f"  High (4+ months):     {len(stale_notes['high'])}")
        print(f"  Medium (3+ months):   {len(stale_notes['medium'])}")
        if total_stale > 0:
            print(f"\nRun without --summary for full report.")
        return

    # Full report
    print(f"\nStale Notes Report")
    print(f"{'=' * 60}")
    print(f"Checked: {total_checked} notes | Stale: {total_stale} notes\n")

    if total_stale == 0:
        print("All notes are up to date!")
        return

    for priority in ("critical", "high", "medium"):
        notes = stale_notes[priority]
        if not notes:
            continue

        labels = {"critical": "CRITICAL (6+ months)", "high": "HIGH (4+ months)",
                  "medium": "MEDIUM (3+ months)"}
        print(f"### {labels[priority]} ({len(notes)})\n")

        for n in notes:
            note_type = n["type"] or "unknown"
            verified_str = f"verified {n['days_since']}d ago" if n["has_verified_field"] else f"modified {n['days_since']}d ago (no verified field)"
            print(f"  [{note_type}] {n['title']}")
            print(f"    {n['path']} - {verified_str}")
        print()

    print(f"{'=' * 60}")
    print("Actions:")
    print("  /review  - Step through notes for verification")
    print("  /stale   - Interactive stale note management")


if __name__ == "__main__":
    main()
