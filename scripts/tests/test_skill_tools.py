#!/usr/bin/env python3
"""Tests for skill-tools.py."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import _import_script, VaultFixture, SCRIPTS_DIR

_st = _import_script("skill_tools", "skill-tools.py")
parse_skill = _st.parse_skill
validate_skill = _st.validate_skill


class TestParseSkill(unittest.TestCase):
    """Test skill file parsing."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _write_skill(self, name, content):
        """Create a skill in subdirectory layout: <name>/SKILL.md."""
        skill_dir = Path(self.tmpdir) / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        path = skill_dir / "SKILL.md"
        path.write_text(content)
        return path

    def test_command_extraction(self):
        path = self._write_skill("search", "# /search\n\nSearch the vault.\n")
        info = parse_skill(path)
        self.assertEqual(info["command"], "search")

    def test_usage_detection(self):
        path = self._write_skill("q", "# /q\n\n## Usage\n\nRun /q term\n")
        info = parse_skill(path)
        self.assertTrue(info["has_usage"])

    def test_instructions_detection(self):
        path = self._write_skill("daily",
                                 "# /daily\n\n## Instructions\n\nCreate a daily note.\n")
        info = parse_skill(path)
        self.assertTrue(info["has_instructions"])

    def test_script_references(self):
        path = self._write_skill("index",
                                 "# /index\n\nRun `python3 scripts/build-index.py --stats`\n")
        info = parse_skill(path)
        self.assertIn("build-index.py", info["script_refs"])

    def test_section_and_line_counts(self):
        path = self._write_skill("test",
                                 "# /test\n\n## Usage\n\nUsage text.\n\n## Instructions\n\nSteps.\n")
        info = parse_skill(path)
        self.assertEqual(info["sections"], 2)
        self.assertGreater(info["lines"], 5)

    def test_frontmatter_skipping(self):
        """parse_skill should skip YAML frontmatter before extracting command."""
        path = self._write_skill("myskill",
                                 "---\nname: myskill\n---\n\n# /myskill\n\n## Usage\n\nDo things.\n")
        info = parse_skill(path)
        self.assertEqual(info["command"], "myskill")
        self.assertEqual(info["skill_name"], "myskill")

    def test_skill_name_from_directory(self):
        """skill_name should come from parent directory, not file stem."""
        path = self._write_skill("search", "# /search\n\nSearch.\n")
        info = parse_skill(path)
        self.assertEqual(info["skill_name"], "search")


class TestValidateSkill(unittest.TestCase):
    """Test skill validation."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.skills_dir = self.fixture.root / ".claude" / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir = self.fixture.root / "scripts"
        self.scripts_dir.mkdir(exist_ok=True)

    def tearDown(self):
        self.fixture.teardown()

    def _write_skill(self, name, content):
        """Create a skill in subdirectory layout: <name>/SKILL.md."""
        skill_dir = self.skills_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        path = skill_dir / "SKILL.md"
        path.write_text(content)
        return path

    def test_valid_skill(self):
        (self.scripts_dir / "search.py").write_text("# stub")
        path = self._write_skill("search",
                                 "# /search\n\n## Usage\n\nSearch.\n\n"
                                 "## Instructions\n\nRun `python3 scripts/search.py`\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertEqual(issues, [])

    def test_missing_header(self):
        path = self._write_skill("broken", "No header here\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("header" in i.lower() for i in issues))

    def test_command_directory_mismatch(self):
        path = self._write_skill("wrong", "# /different\n\n## Usage\n\n## Instructions\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("doesn't match" in i.lower() or "match" in i.lower() for i in issues))

    def test_missing_usage(self):
        path = self._write_skill("nousage",
                                 "# /nousage\n\n## Instructions\n\nDo things.\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("usage" in i.lower() for i in issues))

    def test_broken_script_reference(self):
        path = self._write_skill("reftest",
                                 "# /reftest\n\n## Usage\n\nUse it.\n\n"
                                 "## Instructions\n\nRun `python3 scripts/nonexistent.py`\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("not found" in i.lower() for i in issues))


if __name__ == "__main__":
    unittest.main()
