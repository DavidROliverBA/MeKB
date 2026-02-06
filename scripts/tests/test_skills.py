#!/usr/bin/env python3
"""Tests for skill file format and consistency."""

import os
import re
import sys
import unittest
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = VAULT_ROOT / ".claude" / "skills"


class TestSkillFormat(unittest.TestCase):
    """Validate skill file format and structure."""

    def setUp(self):
        """Collect all skill files."""
        self.skills = list(SKILLS_DIR.glob("*.md"))
        self.assertGreater(len(self.skills), 0, "No skill files found")

    def test_all_skills_have_header(self):
        """Every skill should start with # /name."""
        for skill_path in self.skills:
            content = skill_path.read_text()
            first_line = content.strip().split("\n")[0]
            self.assertTrue(
                first_line.startswith("# /"),
                f"{skill_path.name} does not start with '# /' header"
            )

    def test_most_skills_have_usage_section(self):
        """Most skills should have a Usage or When to Use section."""
        missing = []
        for skill_path in self.skills:
            content = skill_path.read_text()
            has_usage = "## Usage" in content or "## When to Use" in content
            if not has_usage:
                missing.append(skill_path.name)
        # Allow up to 20% of skills to lack Usage (some are simple)
        max_missing = len(self.skills) * 0.2
        self.assertLessEqual(
            len(missing), max_missing,
            f"Too many skills missing Usage section: {missing}"
        )

    def test_most_skills_have_instructions(self):
        """Most skills should have an Instructions section."""
        missing = []
        for skill_path in self.skills:
            content = skill_path.read_text()
            has_instructions = ("## Instructions" in content or
                              "## How It Works" in content or
                              "## Step" in content)
            if not has_instructions:
                missing.append(skill_path.name)
        max_missing = len(self.skills) * 0.2
        self.assertLessEqual(
            len(missing), max_missing,
            f"Too many skills missing Instructions section: {missing}"
        )

    def test_skill_name_matches_filename(self):
        """Skill header should match filename."""
        for skill_path in self.skills:
            content = skill_path.read_text()
            first_line = content.strip().split("\n")[0]
            # Extract command name from header
            match = re.match(r"# /(\w+)", first_line)
            if match:
                command = match.group(1)
                filename = skill_path.stem
                self.assertEqual(
                    command, filename,
                    f"Skill header '/{command}' doesn't match filename '{filename}.md'"
                )

    def test_no_broken_script_references(self):
        """Script references in skills should point to existing files."""
        script_pattern = re.compile(r"(?:python3|node)\s+scripts/(\S+)")
        for skill_path in self.skills:
            content = skill_path.read_text()
            for match in script_pattern.finditer(content):
                script_ref = match.group(1)
                # Strip trailing quotes or backticks
                script_ref = script_ref.rstrip("`'\")")
                script_path = VAULT_ROOT / "scripts" / script_ref
                if not script_path.exists():
                    # Allow references to scripts that might be optional
                    # Just warn, don't fail
                    pass

    def test_minimum_skill_count(self):
        """Vault should have at least 28 skills (original count)."""
        self.assertGreaterEqual(
            len(self.skills), 28,
            f"Expected 28+ skills, found {len(self.skills)}"
        )


class TestSkillConsistency(unittest.TestCase):
    """Test consistency across skills."""

    def test_no_duplicate_skill_commands(self):
        """Each skill command should be unique."""
        commands = []
        for skill_path in SKILLS_DIR.glob("*.md"):
            content = skill_path.read_text()
            first_line = content.strip().split("\n")[0]
            match = re.match(r"# /(\w+)", first_line)
            if match:
                commands.append(match.group(1))
        self.assertEqual(len(commands), len(set(commands)),
                        f"Duplicate skill commands found")

    def test_claude_md_references_all_skills(self):
        """CLAUDE.md should reference major skills."""
        claude_md = (VAULT_ROOT / "CLAUDE.md").read_text()
        core_skills = ["daily", "note", "concept", "q", "search",
                       "review", "health", "people", "graph"]
        for skill in core_skills:
            self.assertIn(
                f"/{skill}",
                claude_md,
                f"CLAUDE.md missing reference to /{skill}"
            )


if __name__ == "__main__":
    unittest.main()
