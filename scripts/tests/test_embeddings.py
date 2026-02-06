#!/usr/bin/env python3
"""Tests for build-embeddings.py."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from helpers import _import_script, create_note, VaultFixture, SCRIPTS_DIR

_be = _import_script("build_embeddings", "build-embeddings.py")
prepare_text = _be.prepare_text
load_existing = _be.load_existing
collect_notes = _be.collect_notes
should_skip = _be.should_skip


class TestEmbeddingsPrepareText(unittest.TestCase):
    """Test text preparation for embedding."""

    def test_includes_title_and_type(self):
        result = prepare_text("My Note", "Concept", [], "Body content")
        self.assertIn("Title: My Note", result)
        self.assertIn("Type: Concept", result)

    def test_includes_tags(self):
        result = prepare_text("Note", "Concept", ["domain/data", "activity/research"], "Body")
        self.assertIn("Tags: domain/data, activity/research", result)

    def test_truncates_to_3000_chars(self):
        long_body = "x" * 5000
        result = prepare_text("Note", "Concept", [], long_body)
        # Body portion should be truncated to 3000
        lines = result.split("\n")
        body_line = lines[-1]  # Last line is the body
        self.assertLessEqual(len(body_line), 3000)

    def test_removes_code_blocks(self):
        body = "Before\n```python\nprint('hello')\n```\nAfter"
        result = prepare_text("Note", None, [], body)
        self.assertNotIn("print('hello')", result)
        self.assertIn("Before", result)
        self.assertIn("After", result)

    def test_unwraps_wiki_links(self):
        body = "See [[Concept - Data Quality]] for details"
        result = prepare_text("Note", None, [], body)
        self.assertNotIn("[[", result)
        self.assertIn("Concept - Data Quality", result)


class TestEmbeddingsLoadExisting(unittest.TestCase):
    """Test loading existing embeddings file."""

    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"model": "test-model", "embeddings": {"note.md": {"vector": [1, 2, 3]}}}, f)
            f.flush()
            path = Path(f.name)
        try:
            result = load_existing(path)
            self.assertEqual(result["model"], "test-model")
            self.assertIn("note.md", result["embeddings"])
        finally:
            os.unlink(path)

    def test_missing_file(self):
        result = load_existing(Path("/nonexistent/path/embeddings.json"))
        self.assertIsNone(result["model"])
        self.assertEqual(result["embeddings"], {})

    def test_corrupt_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{not valid json")
            f.flush()
            path = Path(f.name)
        try:
            result = load_existing(path)
            self.assertIsNone(result["model"])
            self.assertEqual(result["embeddings"], {})
        finally:
            os.unlink(path)


class TestEmbeddingsCollectNotes(unittest.TestCase):
    """Test note collection for embedding."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        create_note(self.fixture.root, "Concept - Test.md",
                     {"type": "Concept", "title": "Test"}, "Content")
        create_note(self.fixture.root, "Pattern - Other.md",
                     {"type": "Pattern", "title": "Other"}, "Content")

    def tearDown(self):
        self.fixture.teardown()

    def test_finds_md_files(self):
        notes = collect_notes(self.fixture.root)
        names = [n.name for n in notes]
        self.assertIn("Concept - Test.md", names)
        self.assertIn("Pattern - Other.md", names)

    def test_skips_secret_dir(self):
        secret_dir = self.fixture.root / "secret"
        secret_dir.mkdir()
        (secret_dir / "Creds.md").write_text("password")
        notes = collect_notes(self.fixture.root)
        names = [n.name for n in notes]
        self.assertNotIn("Creds.md", names)

    def test_skips_non_md(self):
        (self.fixture.root / "image.png").write_text("binary")
        notes = collect_notes(self.fixture.root)
        names = [n.name for n in notes]
        self.assertNotIn("image.png", names)


class TestEmbeddingsShouldSkip(unittest.TestCase):
    """Test skip logic for embedding collection."""

    def setUp(self):
        self.fixture = VaultFixture().setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_skips_git_dir(self):
        git_dir = self.fixture.root / ".git"
        git_dir.mkdir()
        note = git_dir / "config.md"
        note.write_text("git config")
        self.assertTrue(should_skip(note, self.fixture.root))

    def test_skips_py_files(self):
        py = self.fixture.root / "script.py"
        py.write_text("print('hi')")
        self.assertTrue(should_skip(py, self.fixture.root))

    def test_allows_root_md(self):
        note = create_note(self.fixture.root, "Note.md",
                           {"type": "Note"}, "Content")
        self.assertFalse(should_skip(note, self.fixture.root))


if __name__ == "__main__":
    unittest.main()
