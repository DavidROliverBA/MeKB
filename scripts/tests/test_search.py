#!/usr/bin/env python3
"""Tests for build-index.py and search.py."""

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import _import_script, create_note, VaultFixture, SCRIPTS_DIR

_bi = _import_script("build_index", "build-index.py")
parse_frontmatter = _bi.parse_frontmatter
extract_field = _bi.extract_field
extract_list = _bi.extract_list
create_schema = _bi.create_schema
index_note = _bi.index_note
collect_notes = _bi.collect_notes


class TestFrontmatterParsing(unittest.TestCase):
    """Test YAML frontmatter extraction."""

    def test_parse_basic_frontmatter(self):
        content = """---
type: Concept
title: Test Note
created: 2026-01-15
tags: [topic/testing, activity/research]
---

# Test Note

Some content here.
"""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["type"], "Concept")
        self.assertEqual(fm["title"], "Test Note")
        self.assertEqual(fm["created"], "2026-01-15")
        self.assertEqual(fm["tags"], ["topic/testing", "activity/research"])
        self.assertIn("Some content here", body)

    def test_parse_no_frontmatter(self):
        content = "# Just a note\n\nNo frontmatter here.\n"
        fm, body = parse_frontmatter(content)
        self.assertIsNone(fm.get("type"))
        self.assertIn("Just a note", body)

    def test_parse_null_fields(self):
        content = """---
type: Note
title: null
created: 2026-01-15
tags: []
---
"""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["type"], "Note")
        self.assertIsNone(fm["title"])

    def test_parse_quoted_strings(self):
        content = """---
type: Decision
title: "Cloud Provider: AWS vs Azure"
created: 2026-01-15
tags: []
---
"""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["title"], "Cloud Provider: AWS vs Azure")


class TestExtractField(unittest.TestCase):
    """Test individual field extraction."""

    def test_extract_simple_field(self):
        self.assertEqual(extract_field("type: Concept", "type"), "Concept")

    def test_extract_missing_field(self):
        self.assertIsNone(extract_field("type: Concept", "title"))

    def test_extract_null_field(self):
        self.assertIsNone(extract_field("title: null", "title"))

    def test_extract_quoted_field(self):
        self.assertEqual(extract_field('title: "Hello World"', "title"), "Hello World")


class TestExtractList(unittest.TestCase):
    """Test list field extraction."""

    def test_inline_list(self):
        result = extract_list("tags: [a, b, c]", "tags")
        self.assertEqual(result, ["a", "b", "c"])

    def test_empty_list(self):
        result = extract_list("tags: []", "tags")
        self.assertEqual(result, [])

    def test_quoted_items(self):
        result = extract_list('tags: ["topic/test", "activity/research"]', "tags")
        self.assertEqual(result, ["topic/test", "activity/research"])


class TestIndexBuilding(unittest.TestCase):
    """Test SQLite index creation and querying."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test.db"
        self.vault_dir = Path(self.tmpdir) / "vault"
        self.vault_dir.mkdir()

        # Create test notes
        (self.vault_dir / "Note - Test.md").write_text("""---
type: Note
title: Test Note
created: 2026-01-15
tags: [topic/testing]
---

# Test Note

This is a test note about testing things.
""")
        (self.vault_dir / "Concept - Foo.md").write_text("""---
type: Concept
title: Foo
created: 2026-01-15
tags: []
---

# Foo

Foo is a concept about bars.
""")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_create_schema(self):
        conn = sqlite3.connect(str(self.db_path))
        create_schema(conn)
        # Verify tables exist
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        self.assertIn("notes", table_names)
        conn.close()

    def test_index_note(self):
        conn = sqlite3.connect(str(self.db_path))
        create_schema(conn)
        path = self.vault_dir / "Note - Test.md"
        result = index_note(conn, path, self.vault_dir)
        self.assertTrue(result)
        conn.commit()

        # Verify the note was indexed
        row = conn.execute("SELECT title, type FROM notes").fetchone()
        self.assertEqual(row[0], "Test Note")
        self.assertEqual(row[1], "Note")
        conn.close()

    def test_fts5_search(self):
        conn = sqlite3.connect(str(self.db_path))
        create_schema(conn)
        for path in self.vault_dir.glob("*.md"):
            index_note(conn, path, self.vault_dir)
        conn.commit()

        # Rebuild FTS
        conn.execute("INSERT INTO fts_notes(fts_notes) VALUES('rebuild')")
        conn.commit()

        # Search
        rows = conn.execute("""
            SELECT n.title FROM fts_notes f
            JOIN notes n ON n.id = f.rowid
            WHERE fts_notes MATCH 'testing'
        """).fetchall()
        self.assertTrue(len(rows) > 0)
        self.assertEqual(rows[0][0], "Test Note")
        conn.close()

    def test_secret_notes_excluded(self):
        # Create a secret note
        (self.vault_dir / "Secret - Passwords.md").write_text("""---
type: Note
title: Passwords
classification: secret
---

Very secret content.
""")
        conn = sqlite3.connect(str(self.db_path))
        create_schema(conn)
        path = self.vault_dir / "Secret - Passwords.md"
        result = index_note(conn, path, self.vault_dir)
        self.assertFalse(result)  # Should not be indexed
        conn.close()

    def test_incremental_update(self):
        conn = sqlite3.connect(str(self.db_path))
        create_schema(conn)
        path = self.vault_dir / "Note - Test.md"

        # First index
        result1 = index_note(conn, path, self.vault_dir)
        conn.commit()
        self.assertTrue(result1)

        # Second index (no changes)
        result2 = index_note(conn, path, self.vault_dir)
        self.assertFalse(result2)  # Should skip
        conn.close()


class TestSearchEngine(unittest.TestCase):
    """Test search.py functions."""

    def test_sanitise_fts_query(self):
        _s = _import_script("search", "search.py")
        # Simple term
        self.assertEqual(_s.sanitise_fts_query("hello"), "hello")
        # Multiple terms
        self.assertEqual(_s.sanitise_fts_query("hello world"), "hello world")
        # Quoted phrase
        self.assertEqual(_s.sanitise_fts_query('"exact match"'), '"exact match"')
        # Special characters removed
        result = _s.sanitise_fts_query("hello{world}")
        self.assertNotIn("{", result)

    def test_clean_snippet(self):
        _s = _import_script("search", "search.py")
        result = _s.clean_snippet("This is >>>highlighted<<< text")
        self.assertEqual(result, "This is **highlighted** text")

    def test_cosine_similarity(self):
        _s = _import_script("search", "search.py")
        # Identical vectors
        self.assertAlmostEqual(_s.cosine_similarity([1, 0, 0], [1, 0, 0]), 1.0)
        # Orthogonal vectors
        self.assertAlmostEqual(_s.cosine_similarity([1, 0], [0, 1]), 0.0)
        # Empty vectors
        self.assertEqual(_s.cosine_similarity([], []), 0.0)


class TestSearchHybrid(unittest.TestCase):
    """Test hybrid search fusion."""

    def setUp(self):
        _s = _import_script("search", "search.py")
        self.hybrid_search = _s.hybrid_search
        self.fts_results = [
            {"path": "Concept - A.md", "title": "A", "bm25_score": 5.0, "snippet": "..."},
            {"path": "Concept - B.md", "title": "B", "bm25_score": 3.0, "snippet": "..."},
        ]
        self.vec_results = [
            {"path": "Concept - B.md", "title": "B", "vector_score": 0.95},
            {"path": "Concept - C.md", "title": "C", "vector_score": 0.80},
        ]

    def test_hybrid_merge(self):
        results = self.hybrid_search(self.fts_results, self.vec_results)
        paths = [r["path"] for r in results]
        # B appears in both lists so should rank highly
        self.assertIn("Concept - B.md", paths)
        # All three notes should appear
        self.assertEqual(len(paths), 3)
        # All should be tagged as hybrid source
        for r in results:
            self.assertEqual(r["source"], "hybrid")

    def test_fts_only_fallback(self):
        results = self.hybrid_search(self.fts_results, [])
        paths = [r["path"] for r in results]
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0], "Concept - A.md")

    def test_graph_boost(self):
        degrees = {"Concept - B.md": 1.0, "Concept - A.md": 0.1, "Concept - C.md": 0.5}
        results_with = self.hybrid_search(self.fts_results, self.vec_results, graph_degrees=degrees)
        # B should still be present and boosted
        paths_with = [r["path"] for r in results_with]
        self.assertIn("Concept - B.md", paths_with)
        # Graph score should be populated
        b_result = [r for r in results_with if r["path"] == "Concept - B.md"][0]
        self.assertGreater(b_result["graph_score"], 0)

    def test_weight_renormalisation(self):
        degrees = {"Concept - A.md": 0.5}
        results = self.hybrid_search(self.fts_results, self.vec_results, graph_degrees=degrees)
        # Should still produce valid results (weights renormalised)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertGreater(r["fusion_score"], 0)


class TestSearchFiltering(unittest.TestCase):
    """Test search filtering and output."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.db_path = self.fixture.root / ".mekb" / "search.db"
        conn = sqlite3.connect(str(self.db_path))
        create_schema(conn)
        # Index test notes
        create_note(self.fixture.root, "Concept - Alpha.md",
                     {"type": "Concept", "title": "Alpha", "classification": "personal"},
                     "Alpha is about testing search.")
        create_note(self.fixture.root, "Pattern - Beta.md",
                     {"type": "Pattern", "title": "Beta"},
                     "Beta describes a pattern for testing.")
        create_note(self.fixture.root, "Note - Secret.md",
                     {"type": "Note", "title": "Secret Stuff", "classification": "secret"},
                     "This should be excluded from indexing.")
        for path in self.fixture.root.glob("*.md"):
            index_note(conn, path, self.fixture.root)
        conn.commit()
        conn.execute("INSERT INTO fts_notes(fts_notes) VALUES('rebuild')")
        conn.commit()
        conn.close()
        self._search = _import_script("search", "search.py")

    def tearDown(self):
        self.fixture.teardown()

    def test_type_filter(self):
        results = self._search.fts5_search(self.db_path, "testing", note_type="Concept")
        types = [r["type"] for r in results]
        self.assertTrue(all(t == "Concept" for t in types))

    def test_secret_exclusion(self):
        results = self._search.fts5_search(
            self.db_path, "secret", exclude_classifications=["secret"])
        paths = [r["path"] for r in results]
        self.assertNotIn("Note - Secret.md", paths)

    def test_special_chars_in_query(self):
        result = self._search.sanitise_fts_query("test{brackets}")
        self.assertNotIn("{", result)
        self.assertNotIn("}", result)

    def test_json_output_format(self):
        results = self._search.fts5_search(self.db_path, "testing")
        # format_json writes to stdout; just verify result structure
        for r in results:
            self.assertIn("path", r)
            self.assertIn("title", r)
            self.assertIn("bm25_score", r)


class TestBuildIndexCollect(unittest.TestCase):
    """Test build-index.py note collection."""

    def setUp(self):
        self.fixture = VaultFixture().setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_collect_finds_root_md(self):
        create_note(self.fixture.root, "Concept - Test.md",
                     {"type": "Concept"}, "Content")
        notes = collect_notes(self.fixture.root)
        names = [n.name for n in notes]
        self.assertIn("Concept - Test.md", names)

    def test_should_skip_secret_dir(self):
        secret_dir = self.fixture.root / "secret"
        secret_dir.mkdir()
        note = secret_dir / "Creds.md"
        note.write_text("password")
        from helpers import _import_script
        _bi_local = _import_script("build_index", "build-index.py")
        self.assertTrue(_bi_local.should_skip(note, self.fixture.root))

    def test_should_skip_non_md(self):
        py_file = self.fixture.root / "script.py"
        py_file.write_text("print('hi')")
        from helpers import _import_script
        _bi_local = _import_script("build_index", "build-index.py")
        self.assertTrue(_bi_local.should_skip(py_file, self.fixture.root))


if __name__ == "__main__":
    unittest.main()
