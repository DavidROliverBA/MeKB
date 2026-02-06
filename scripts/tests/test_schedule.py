#!/usr/bin/env python3
"""Tests for schedule.py."""

import unittest
from pathlib import Path
from unittest.mock import patch

from helpers import _import_script, VaultFixture, SCRIPTS_DIR

_sch = _import_script("schedule", "schedule.py")
generate_plist = _sch.generate_plist
generate_crontab_entry = _sch.generate_crontab_entry
JOBS = _sch.JOBS
DAY_MAP = _sch.DAY_MAP


class TestGeneratePlist(unittest.TestCase):
    """Test macOS launchd plist generation."""

    def setUp(self):
        self.vault_root = Path("/tmp/test-vault")

    def test_daily_job_structure(self):
        job = JOBS["rebuild-index"]
        plist = generate_plist("rebuild-index", job, self.vault_root)
        self.assertIn("<plist version", plist)
        self.assertIn("com.mekb.rebuild-index", plist)
        self.assertIn("<key>Hour</key>", plist)
        self.assertIn("<key>Minute</key>", plist)

    def test_weekly_job_has_weekday(self):
        job = JOBS["rebuild-embeddings"]
        plist = generate_plist("rebuild-embeddings", job, self.vault_root)
        self.assertIn("<key>Weekday</key>", plist)

    def test_working_directory(self):
        job = JOBS["rebuild-index"]
        plist = generate_plist("rebuild-index", job, self.vault_root)
        self.assertIn("<key>WorkingDirectory</key>", plist)
        self.assertIn(str(self.vault_root), plist)

    def test_log_paths(self):
        job = JOBS["rebuild-index"]
        plist = generate_plist("rebuild-index", job, self.vault_root)
        self.assertIn("rebuild-index.log", plist)
        self.assertIn("rebuild-index.error.log", plist)

    def test_run_at_load_false(self):
        job = JOBS["rebuild-index"]
        plist = generate_plist("rebuild-index", job, self.vault_root)
        self.assertIn("<key>RunAtLoad</key>", plist)
        self.assertIn("<false/>", plist)


class TestGenerateCrontab(unittest.TestCase):
    """Test crontab entry generation."""

    def setUp(self):
        self.vault_root = Path("/tmp/test-vault")

    def test_daily_format(self):
        job = JOBS["rebuild-index"]
        entry = generate_crontab_entry("rebuild-index", job, self.vault_root)
        # Should be: minute hour * * * (format depends on time field)
        self.assertRegex(entry, r"^\d+ \d+ \* \* \*")
        self.assertIn("# mekb:rebuild-index", entry)

    def test_weekly_format(self):
        job = JOBS["stale-check"]
        entry = generate_crontab_entry("stale-check", job, self.vault_root)
        # Friday = 5 in DAY_MAP, 5 % 7 = 5 in crontab
        self.assertIn("* * 5", entry)
        self.assertIn("# mekb:stale-check", entry)

    def test_mekb_comment_marker(self):
        for name, job in JOBS.items():
            entry = generate_crontab_entry(name, job, self.vault_root)
            if entry:
                self.assertIn(f"# mekb:{name}", entry)

    def test_sunday_maps_to_0(self):
        job = JOBS["rebuild-embeddings"]
        entry = generate_crontab_entry("rebuild-embeddings", job, self.vault_root)
        # Sunday = 7 in DAY_MAP, 7 % 7 = 0 in crontab
        self.assertIn("* * 0", entry)


class TestJobDefinitions(unittest.TestCase):
    """Test job definition structure."""

    def test_required_fields_present(self):
        for name, job in JOBS.items():
            self.assertIn("description", job, f"{name} missing description")
            self.assertIn("command", job, f"{name} missing command")
            self.assertIn("schedule", job, f"{name} missing schedule")
            self.assertIn("time", job, f"{name} missing time")
            self.assertIn("day", job, f"{name} missing day")

    def test_script_paths_valid(self):
        for name, job in JOBS.items():
            parts = job["command"].split()
            self.assertTrue(parts[0] in ("python3", "node"),
                            f"{name} command should start with python3 or node")
            # Script should be in scripts/ directory
            self.assertTrue(parts[1].startswith("scripts/"),
                            f"{name} script path should start with scripts/")

    def test_day_map_complete(self):
        expected = {"Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"}
        self.assertEqual(set(DAY_MAP.keys()), expected)


if __name__ == "__main__":
    unittest.main()
