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

    def _write_skill(self, filename, content):
        path = Path(self.tmpdir) / filename
        path.write_text(content)
        return path

    def test_command_extraction(self):
        path = self._write_skill("search.md", "# /search\n\nSearch the vault.\n")
        info = parse_skill(path)
        self.assertEqual(info["command"], "search")

    def test_usage_detection(self):
        path = self._write_skill("q.md", "# /q\n\n## Usage\n\nRun /q term\n")
        info = parse_skill(path)
        self.assertTrue(info["has_usage"])

    def test_instructions_detection(self):
        path = self._write_skill("daily.md",
                                 "# /daily\n\n## Instructions\n\nCreate a daily note.\n")
        info = parse_skill(path)
        self.assertTrue(info["has_instructions"])

    def test_script_references(self):
        path = self._write_skill("index.md",
                                 "# /index\n\nRun `python3 scripts/build-index.py --stats`\n")
        info = parse_skill(path)
        self.assertIn("build-index.py", info["script_refs"])

    def test_section_and_line_counts(self):
        path = self._write_skill("test.md",
                                 "# /test\n\n## Usage\n\nUsage text.\n\n## Instructions\n\nSteps.\n")
        info = parse_skill(path)
        self.assertEqual(info["sections"], 2)
        self.assertGreater(info["lines"], 5)


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

    def _write_skill(self, filename, content):
        path = self.skills_dir / filename
        path.write_text(content)
        return path

    def test_valid_skill(self):
        (self.scripts_dir / "search.py").write_text("# stub")
        path = self._write_skill("search.md",
                                 "# /search\n\n## Usage\n\nSearch.\n\n"
                                 "## Instructions\n\nRun `python3 scripts/search.py`\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertEqual(issues, [])

    def test_missing_header(self):
        path = self._write_skill("broken.md", "No header here\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("header" in i.lower() for i in issues))

    def test_command_filename_mismatch(self):
        path = self._write_skill("wrong.md", "# /different\n\n## Usage\n\n## Instructions\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("doesn't match" in i.lower() or "match" in i.lower() for i in issues))

    def test_missing_usage(self):
        path = self._write_skill("nousage.md",
                                 "# /nousage\n\n## Instructions\n\nDo things.\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("usage" in i.lower() for i in issues))

    def test_broken_script_reference(self):
        path = self._write_skill("reftest.md",
                                 "# /reftest\n\n## Usage\n\nUse it.\n\n"
                                 "## Instructions\n\nRun `python3 scripts/nonexistent.py`\n")
        issues = validate_skill(path, self.fixture.root)
        self.assertTrue(any("not found" in i.lower() for i in issues))


if __name__ == "__main__":
    unittest.main()
