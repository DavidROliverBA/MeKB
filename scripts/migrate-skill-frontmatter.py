#!/usr/bin/env python3
"""
Migrate skill files to include kepano-compatible YAML frontmatter.

Adds a `name` field in YAML frontmatter to each SKILL.md that lacks it.
This is the format used by Anthropic's kepano skills convention.

Usage:
    python3 scripts/migrate-skill-frontmatter.py             # Run migration
    python3 scripts/migrate-skill-frontmatter.py --dry-run    # Preview changes
    python3 scripts/migrate-skill-frontmatter.py --validate   # Check all have frontmatter

Dependencies: Python 3.9+ (stdlib only)
"""

import argparse
import sys
from pathlib import Path


def find_vault_root():
    """Find the vault root."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def has_frontmatter(content):
    """Check if content starts with YAML frontmatter."""
    return content.strip().startswith("---")


def add_frontmatter(content, skill_name):
    """Prepend YAML frontmatter with name field."""
    return f"---\nname: {skill_name}\n---\n\n{content}"


def migrate(vault_root, dry_run=False):
    """Add frontmatter to all skills that lack it."""
    skills_dir = vault_root / ".claude" / "skills"
    skills = sorted(skills_dir.glob("*/SKILL.md"))

    migrated = 0
    skipped = 0

    for path in skills:
        content = path.read_text()
        skill_name = path.parent.name

        if has_frontmatter(content):
            skipped += 1
            if not dry_run:
                continue
            print(f"  SKIP: {skill_name}/SKILL.md (already has frontmatter)")
            continue

        new_content = add_frontmatter(content, skill_name)

        if dry_run:
            print(f"  WOULD ADD: {skill_name}/SKILL.md")
        else:
            path.write_text(new_content)
            print(f"  ADDED: {skill_name}/SKILL.md")

        migrated += 1

    print(f"\n{'Would migrate' if dry_run else 'Migrated'}: {migrated}")
    print(f"Skipped (already have frontmatter): {skipped}")
    print(f"Total: {migrated + skipped}")

    return migrated


def validate(vault_root):
    """Check all skills have frontmatter."""
    skills_dir = vault_root / ".claude" / "skills"
    skills = sorted(skills_dir.glob("*/SKILL.md"))

    missing = []
    for path in skills:
        content = path.read_text()
        if not has_frontmatter(content):
            missing.append(path.parent.name)

    if missing:
        print(f"\n{len(missing)} skill(s) missing frontmatter:")
        for name in missing:
            print(f"  - {name}/SKILL.md")
        return len(missing)
    else:
        print(f"\nAll {len(skills)} skills have frontmatter.")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate skill files to include YAML frontmatter"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing")
    parser.add_argument("--validate", action="store_true",
                        help="Check all skills have frontmatter")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()

    if args.validate:
        issues = validate(vault_root)
        sys.exit(1 if issues > 0 else 0)
    else:
        migrate(vault_root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
