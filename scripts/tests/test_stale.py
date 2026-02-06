#!/usr/bin/env python3
"""Tests for stale-check.py."""

import os
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from helpers import _import_script, create_note, VaultFixture, SCRIPTS_DIR

_sc = _import_script("stale_check", "stale-check.py")
parse_date = _sc.parse_date
should_skip = _sc.should_skip
check_note = _sc.check_note
THRESHOLDS = _sc.THRESHOLDS


class TestStaleDateParsing(unittest.TestCase):
    """Test date parsing for staleness checks."""

    def test_valid_date(self):
        result = parse_date("2026-01-15")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)

    def test_invalid_date(self):
        result = parse_date("not-a-date")
        self.assertIsNone(result)

    def test_empty_string(self):
        result = parse_date("")
        self.assertIsNone(result)

    def test_none_input(self):
        result = parse_date(None)
        self.assertIsNone(result)


class TestStaleSkipLogic(unittest.TestCase):
    """Test file skip logic."""

    def setUp(self):
        self.fixture = VaultFixture().setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_archive_dir_skipped(self):
        archive_dir = self.fixture.root / "Archive"
        archive_dir.mkdir()
        note = archive_dir / "Old Note.md"
        note.write_text("content")
        self.assertTrue(should_skip(note, self.fixture.root))

    def test_secret_dir_skipped(self):
        secret_dir = self.fixture.root / "secret"
        secret_dir.mkdir()
        note = secret_dir / "Creds.md"
        note.write_text("content")
        self.assertTrue(should_skip(note, self.fixture.root))

    def test_root_md_not_skipped(self):
        note = create_note(self.fixture.root, "Note - Test.md",
                           {"type": "Note", "title": "Test"}, "Content")
        self.assertFalse(should_skip(note, self.fixture.root))


class TestCheckNote(unittest.TestCase):
    """Test individual note staleness checking."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.today = datetime.now()

    def tearDown(self):
        self.fixture.teardown()

    def test_critical_staleness(self):
        """Note verified 200 days ago should be critical."""
        old_date = (self.today - timedelta(days=200)).strftime("%Y-%m-%d")
        note = create_note(self.fixture.root, "Concept - Old.md",
                           {"type": "Concept", "title": "Old", "verified": old_date},
                           "Old content")
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNotNone(result)
        self.assertEqual(result["priority"], "critical")

    def test_high_staleness(self):
        """Note verified 130 days ago should be high."""
        old_date = (self.today - timedelta(days=130)).strftime("%Y-%m-%d")
        note = create_note(self.fixture.root, "Concept - Medium.md",
                           {"type": "Concept", "title": "Medium", "verified": old_date},
                           "Content")
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNotNone(result)
        self.assertEqual(result["priority"], "high")

    def test_medium_staleness(self):
        """Note verified 100 days ago should be medium (non-high-value type)."""
        old_date = (self.today - timedelta(days=100)).strftime("%Y-%m-%d")
        note = create_note(self.fixture.root, "Weblink - Stale.md",
                           {"type": "Weblink", "title": "Stale", "verified": old_date},
                           "Content")
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNotNone(result)
        self.assertEqual(result["priority"], "medium")

    def test_not_stale(self):
        """Note verified recently should not be flagged."""
        recent_date = (self.today - timedelta(days=30)).strftime("%Y-%m-%d")
        note = create_note(self.fixture.root, "Concept - Fresh.md",
                           {"type": "Concept", "title": "Fresh", "verified": recent_date},
                           "Content")
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNone(result)

    def test_daily_skipped(self):
        """Daily notes should always be skipped."""
        note = create_note(self.fixture.root, "Daily - 2025-01-01.md",
                           {"type": "Daily", "title": "2025-01-01"}, "Content")
        # Make file old
        old_time = time.time() - (200 * 86400)
        os.utime(note, (old_time, old_time))
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNone(result)

    def test_secret_skipped(self):
        """Secret notes should always be skipped."""
        note = create_note(self.fixture.root, "Note - Secret.md",
                           {"type": "Note", "title": "Secret", "classification": "secret"},
                           "Content")
        old_time = time.time() - (200 * 86400)
        os.utime(note, (old_time, old_time))
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNone(result)

    def test_freshness_stale_override(self):
        """Note with freshness:stale should be critical regardless of age."""
        recent_date = (self.today - timedelta(days=10)).strftime("%Y-%m-%d")
        note = create_note(self.fixture.root, "Concept - MarkedStale.md",
                           {"type": "Concept", "title": "Marked Stale",
                            "verified": recent_date, "freshness": "stale"},
                           "Content")
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNotNone(result)
        self.assertEqual(result["priority"], "critical")

    def test_high_value_type_boost(self):
        """High-value types at medium staleness should be boosted to high."""
        old_date = (self.today - timedelta(days=100)).strftime("%Y-%m-%d")
        note = create_note(self.fixture.root, "Concept - Important.md",
                           {"type": "Concept", "title": "Important", "verified": old_date},
                           "Content")
        result = check_note(note, self.fixture.root, self.today)
        self.assertIsNotNone(result)
        # Concept is HIGH_VALUE_TYPES, medium becomes high
        self.assertEqual(result["priority"], "high")


if __name__ == "__main__":
    unittest.main()
