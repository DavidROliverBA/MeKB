#!/usr/bin/env python3
"""
Skill Management Tools for MeKB
List, validate, export, and import skills.

Usage:
    python3 scripts/skill-tools.py list                 # List all skills
    python3 scripts/skill-tools.py validate              # Validate all skills
    python3 scripts/skill-tools.py validate /q           # Validate specific skill
    python3 scripts/skill-tools.py export /q             # Export skill as .mekb-skill
    python3 scripts/skill-tools.py import path.mekb-skill # Import a skill package

Dependencies: Python 3.9+ (stdlib only)
"""

import argparse
import json
import os
import re
import shutil
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


def get_skills_dir(vault_root):
    """Get the skills directory."""
    return vault_root / ".claude" / "skills"


def parse_skill(path):
    """Parse a skill file and extract metadata."""
    content = path.read_text()
    lines = content.strip().split("\n")

    # Skip YAML frontmatter block if present
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break

    # Extract command name from first non-frontmatter, non-blank line
    command = None
    for line in lines[start:]:
        if line.strip():
            match = re.match(r"# /(\w[\w-]*)", line)
            if match:
                command = match.group(1)
            break

    # Check for key sections
    has_usage = "## Usage" in content or "## When to Use" in content
    has_instructions = ("## Instructions" in content or
                       "## How It Works" in content or
                       "## Step" in content)

    # Find script references
    script_refs = re.findall(r"(?:python3|node)\s+scripts/(\S+)", content)
    script_refs = [s.rstrip("`'\")}") for s in script_refs]

    # Count sections
    sections = re.findall(r"^## .+$", content, re.MULTILINE)

    # Derive skill name from parent directory (subdirectory layout)
    skill_name = path.parent.name if path.name == "SKILL.md" else path.stem

    return {
        "filename": path.name,
        "skill_name": skill_name,
        "command": command,
        "has_usage": has_usage,
        "has_instructions": has_instructions,
        "script_refs": script_refs,
        "sections": len(sections),
        "lines": len(lines),
        "size": path.stat().st_size,
    }


def list_skills(vault_root):
    """List all skills with metadata."""
    skills_dir = get_skills_dir(vault_root)
    skills = sorted(skills_dir.glob("*/SKILL.md"))

    print(f"\nMeKB Skills ({len(skills)} total)\n")
    print(f"  {'Command':<18} {'Skill':<22} {'Lines':>5}  {'Sections':>8}  Scripts")
    print(f"  {'-'*18} {'-'*22} {'-'*5}  {'-'*8}  {'-'*20}")

    for path in skills:
        info = parse_skill(path)
        cmd = f"/{info['command']}" if info['command'] else "?"
        scripts = ", ".join(info["script_refs"]) if info["script_refs"] else "-"
        print(f"  {cmd:<18} {info['skill_name']:<22} {info['lines']:>5}  {info['sections']:>8}  {scripts}")


def validate_skill(path, vault_root, verbose=False):
    """Validate a single skill file. Returns list of issues."""
    info = parse_skill(path)
    issues = []

    if not info["command"]:
        issues.append("Missing command header (expected '# /name')")

    expected_name = path.parent.name if path.name == "SKILL.md" else path.stem
    if info["command"] and info["command"] != expected_name:
        issues.append(f"Command '/{info['command']}' doesn't match skill directory '{expected_name}'")

    if not info["has_usage"]:
        issues.append("Missing '## Usage' or '## When to Use' section")

    if not info["has_instructions"]:
        issues.append("Missing '## Instructions' or '## How It Works' section")

    # Check script references exist
    for ref in info["script_refs"]:
        script_path = vault_root / "scripts" / ref
        if not script_path.exists():
            issues.append(f"Referenced script not found: scripts/{ref}")

    if verbose and not issues:
        print(f"  OK: {path.name}")

    return issues


def validate_all(vault_root, verbose=False):
    """Validate all skills."""
    skills_dir = get_skills_dir(vault_root)
    skills = sorted(skills_dir.glob("*/SKILL.md"))

    total_issues = 0
    print(f"\nValidating {len(skills)} skills...\n")

    for path in skills:
        issues = validate_skill(path, vault_root, verbose)
        if issues:
            skill_name = path.parent.name
            print(f"  {skill_name}/SKILL.md:")
            for issue in issues:
                print(f"    - {issue}")
            total_issues += len(issues)

    if total_issues == 0:
        print("  All skills pass validation.")
    else:
        print(f"\n{total_issues} issue(s) found.")

    return total_issues


def export_skill(skill_name, vault_root):
    """Export a skill as a .mekb-skill directory."""
    skills_dir = get_skills_dir(vault_root)
    # Strip leading /
    skill_name = skill_name.lstrip("/")
    skill_path = skills_dir / skill_name / "SKILL.md"

    if not skill_path.exists():
        print(f"Skill not found: {skill_name}")
        available = ', '.join(p.parent.name for p in skills_dir.glob("*/SKILL.md"))
        print(f"Available: {available}")
        sys.exit(1)

    info = parse_skill(skill_path)
    export_dir = vault_root / f"{skill_name}.mekb-skill"
    export_dir.mkdir(exist_ok=True)

    # Copy skill file
    shutil.copy2(skill_path, export_dir / "SKILL.md")

    # Copy referenced scripts
    for ref in info["script_refs"]:
        src = vault_root / "scripts" / ref
        if src.exists():
            (export_dir / "scripts").mkdir(exist_ok=True)
            shutil.copy2(src, export_dir / "scripts" / ref)

    # Create manifest
    manifest = {
        "name": skill_name,
        "command": f"/{info['command']}",
        "version": "1.0",
        "description": f"MeKB skill: /{skill_name}",
        "files": ["SKILL.md"],
        "scripts": info["script_refs"],
    }

    with open(export_dir / "manifest.yaml", "w") as f:
        # Simple YAML output without pyyaml
        for key, value in manifest.items():
            if isinstance(value, list):
                f.write(f"{key}:\n")
                for item in value:
                    f.write(f"  - {item}\n")
            else:
                f.write(f"{key}: {value}\n")

    print(f"Exported: {export_dir}")
    print(f"  Skill: {skill_name}.md")
    if info["script_refs"]:
        print(f"  Scripts: {', '.join(info['script_refs'])}")


def import_skill(package_path, vault_root):
    """Import a skill from a .mekb-skill directory."""
    pkg = Path(package_path)
    if not pkg.is_dir():
        print(f"Not a directory: {package_path}")
        sys.exit(1)

    # Find skill file (SKILL.md or fallback to *.md)
    skill_file = pkg / "SKILL.md"
    if not skill_file.exists():
        skill_files = list(pkg.glob("*.md"))
        if not skill_files:
            print(f"No .md file found in {package_path}")
            sys.exit(1)
        skill_file = skill_files[0]

    # Derive skill name from package directory
    skill_name = pkg.stem.replace(".mekb-skill", "")
    skills_dir = get_skills_dir(vault_root)
    scripts_dir = vault_root / "scripts"

    # Create subdirectory and copy skill file
    dest_dir = skills_dir / skill_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "SKILL.md"
    shutil.copy2(skill_file, dest)
    print(f"  Installed: {dest}")

    # Copy scripts
    pkg_scripts = pkg / "scripts"
    if pkg_scripts.is_dir():
        for script in pkg_scripts.glob("*"):
            dest = scripts_dir / script.name
            shutil.copy2(script, dest)
            print(f"  Installed: {dest}")

    print(f"\nSkill imported. Update CLAUDE.md to reference the new skill.")


def main():
    parser = argparse.ArgumentParser(description="MeKB skill management")
    parser.add_argument("action", choices=["list", "validate", "export", "import"],
                       help="Action to perform")
    parser.add_argument("target", nargs="?", help="Skill name or path")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()

    if args.action == "list":
        list_skills(vault_root)
    elif args.action == "validate":
        if args.target:
            skill_name = args.target.lstrip("/")
            skill_path = get_skills_dir(vault_root) / skill_name / "SKILL.md"
            if not skill_path.exists():
                print(f"Skill not found: {skill_name}")
                sys.exit(1)
            issues = validate_skill(skill_path, vault_root, verbose=True)
            if issues:
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)
            else:
                print(f"  {skill_name}/SKILL.md: OK")
        else:
            issues = validate_all(vault_root, verbose=args.verbose)
            sys.exit(1 if issues > 0 else 0)
    elif args.action == "export":
        if not args.target:
            print("Specify a skill to export: python3 scripts/skill-tools.py export /q")
            sys.exit(1)
        export_skill(args.target, vault_root)
    elif args.action == "import":
        if not args.target:
            print("Specify a .mekb-skill directory to import")
            sys.exit(1)
        import_skill(args.target, vault_root)


if __name__ == "__main__":
    main()
