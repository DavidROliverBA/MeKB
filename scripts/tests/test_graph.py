#!/usr/bin/env python3
"""Tests for build-graph.py."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import _import_script, create_note, VaultFixture, SCRIPTS_DIR

_bg = _import_script("build_graph", "build-graph.py")
build_graph = _bg.build_graph
find_orphans = _bg.find_orphans
find_hubs = _bg.find_hubs
bfs_traverse = _bg.bfs_traverse
shortest_path = _bg.shortest_path
build_adjacency = _bg.build_adjacency
extract_relationships = _bg.extract_relationships
resolve_link = _bg.resolve_link
WIKILINK_PATTERN = _bg.WIKILINK_PATTERN


class TestWikiLinkExtraction(unittest.TestCase):
    """Test wiki-link pattern matching."""

    def test_basic_link(self):
        matches = WIKILINK_PATTERN.findall("See [[Note - Test]] for details.")
        self.assertEqual(matches, ["Note - Test"])

    def test_aliased_link(self):
        matches = WIKILINK_PATTERN.findall("[[Person - Jane Smith|Jane]]")
        self.assertEqual(matches, ["Person - Jane Smith"])

    def test_multiple_links(self):
        text = "[[Note - A]] and [[Note - B]] and [[Note - C]]"
        matches = WIKILINK_PATTERN.findall(text)
        self.assertEqual(len(matches), 3)

    def test_no_links(self):
        matches = WIKILINK_PATTERN.findall("No links here.")
        self.assertEqual(len(matches), 0)


class TestRelationshipExtraction(unittest.TestCase):
    """Test typed relationship parsing from frontmatter."""

    def test_inline_format(self):
        # Indentation must match what build-graph.py expects (2 spaces for nested keys)
        yaml = "relationships:\n  depends-on: [\"[[Decision - Cloud Provider]]\"]\n  references: [\"[[Concept - Event Sourcing]]\"]"
        rels = extract_relationships(yaml)
        types = [r["type"] for r in rels]
        self.assertIn("depends-on", types)
        self.assertIn("references", types)

    def test_no_relationships(self):
        yaml = "type: Note\ntitle: Test\n"
        rels = extract_relationships(yaml)
        self.assertEqual(len(rels), 0)


class TestLinkResolution(unittest.TestCase):
    """Test wiki-link to file path resolution."""

    def test_direct_match(self):
        paths = {"Note - Test": "Note - Test.md"}
        self.assertEqual(resolve_link("Note - Test", paths), "Note - Test.md")

    def test_not_found(self):
        paths = {"Note - Test": "Note - Test.md"}
        self.assertIsNone(resolve_link("Note - Missing", paths))


class TestGraphBuilding(unittest.TestCase):
    """Test graph construction."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.vault_dir = Path(self.tmpdir)

        # Create test notes
        (self.vault_dir / "CLAUDE.md").write_text("# MeKB\n")
        (self.vault_dir / ".mekb").mkdir()

        (self.vault_dir / "Note - A.md").write_text("""---
type: Note
title: Note A
---

Links to [[Note - B]] and [[Concept - C]].
""")
        (self.vault_dir / "Note - B.md").write_text("""---
type: Note
title: Note B
---

Links to [[Note - A]].
""")
        (self.vault_dir / "Concept - C.md").write_text("""---
type: Concept
title: Concept C
---

# Concept C

Standalone concept.
""")
        (self.vault_dir / "Orphan.md").write_text("""---
type: Note
title: Orphan
---

No links here.
""")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_build_graph(self):
        graph = build_graph(self.vault_dir)
        self.assertGreater(len(graph["nodes"]), 0)
        self.assertIn("stats", graph)

    def test_nodes_have_required_fields(self):
        graph = build_graph(self.vault_dir)
        for path, node in graph["nodes"].items():
            self.assertIn("title", node)
            self.assertIn("type", node)
            self.assertIn("degree", node)
            self.assertIn("in_degree", node)
            self.assertIn("out_degree", node)

    def test_edges_created(self):
        graph = build_graph(self.vault_dir)
        self.assertGreater(len(graph["edges"]), 0)

    def test_find_orphans(self):
        graph = build_graph(self.vault_dir)
        orphans = find_orphans(graph)
        orphan_paths = [o["path"] for o in orphans]
        self.assertIn("Orphan.md", orphan_paths)

    def test_find_hubs(self):
        graph = build_graph(self.vault_dir)
        hubs = find_hubs(graph, limit=5)
        self.assertGreater(len(hubs), 0)
        # First hub should have highest degree
        if len(hubs) > 1:
            self.assertGreaterEqual(hubs[0]["degree"], hubs[1]["degree"])

    def test_bfs_traverse(self):
        graph = build_graph(self.vault_dir)
        result = bfs_traverse(graph, "Note - A.md", depth=2)
        self.assertNotIn("error", result)
        self.assertIn("layers", result)
        self.assertGreater(result["total_reachable"], 0)

    def test_shortest_path(self):
        graph = build_graph(self.vault_dir)
        result = shortest_path(graph, "Note - A.md", "Note - B.md")
        self.assertIsNotNone(result.get("path"))
        self.assertEqual(result["length"], 1)

    def test_shortest_path_no_connection(self):
        graph = build_graph(self.vault_dir)
        result = shortest_path(graph, "Note - A.md", "Orphan.md")
        self.assertIsNone(result.get("path"))

    def test_traverse_nonexistent_node(self):
        graph = build_graph(self.vault_dir)
        result = bfs_traverse(graph, "Nonexistent.md", depth=2)
        self.assertIn("error", result)


class TestAdjacencyList(unittest.TestCase):
    """Test adjacency list construction."""

    def test_build_adjacency(self):
        graph = {
            "nodes": {"A": {}, "B": {}, "C": {}},
            "edges": [
                {"source": "A", "target": "B"},
                {"source": "B", "target": "C"},
            ],
            "typed_edges": [],
        }
        adj = build_adjacency(graph)
        self.assertIn("B", adj["A"])
        self.assertIn("A", adj["B"])  # Undirected
        self.assertIn("C", adj["B"])


class TestParseNote(unittest.TestCase):
    """Test individual note parsing."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        # Build stem -> path mapping
        self.paths_by_stem = {}

    def tearDown(self):
        self.fixture.teardown()

    def _create_and_map(self, filename, content):
        path = self.fixture.root / filename
        path.write_text(content)
        stem = Path(filename).stem
        self.paths_by_stem[stem] = filename
        return path

    def test_basic_parse(self):
        path = self._create_and_map("Concept - Alpha.md", """---
type: Concept
title: Alpha
---

# Alpha

Some content about alpha.
""")
        data = _bg.parse_note(path, self.fixture.root, self.paths_by_stem)
        self.assertIsNotNone(data)
        self.assertEqual(data["title"], "Alpha")
        self.assertEqual(data["type"], "Concept")

    def test_frontmatter_links(self):
        self._create_and_map("Project - X.md", """---
type: Project
title: X
---

Content.
""")
        path = self._create_and_map("Concept - Beta.md", """---
type: Concept
title: Beta
project: "[[Project - X]]"
---

Links to [[Project - X]] in body too.
""")
        data = _bg.parse_note(path, self.fixture.root, self.paths_by_stem)
        self.assertIsNotNone(data)
        # Should find the link from both frontmatter and body
        self.assertIn("Project - X.md", data["links"])

    def test_unreadable_file(self):
        # parse_note returns None for files it can't read
        fake_path = self.fixture.root / "Missing.md"
        data = _bg.parse_note(fake_path, self.fixture.root, self.paths_by_stem)
        self.assertIsNone(data)


class TestGraphPersistence(unittest.TestCase):
    """Test graph save/load and utility functions."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        # Create minimal vault
        create_note(self.fixture.root, "Concept - One.md",
                     {"type": "Concept", "title": "One"}, "Links to [[Concept - Two]].")
        create_note(self.fixture.root, "Concept - Two.md",
                     {"type": "Concept", "title": "Two"}, "Standalone.")

    def tearDown(self):
        self.fixture.teardown()

    def test_save_load_json(self):
        graph = build_graph(self.fixture.root)
        graph_path = self.fixture.root / ".mekb" / "graph.json"
        _bg.save_graph(graph, graph_path)
        self.assertTrue(graph_path.exists())
        with open(graph_path) as f:
            loaded = json.load(f)
        self.assertEqual(loaded["stats"]["total_nodes"], graph["stats"]["total_nodes"])

    def test_stats_computed(self):
        graph = build_graph(self.fixture.root)
        stats = graph["stats"]
        self.assertGreater(stats["total_nodes"], 0)
        self.assertIn("avg_degree", stats)
        self.assertIn("total_edges", stats)
        self.assertIn("total_typed_edges", stats)

    def test_resolve_note_arg(self):
        graph = build_graph(self.fixture.root)
        # Direct path match
        result = _bg.resolve_note_arg("Concept - One.md", graph)
        self.assertEqual(result, "Concept - One.md")
        # Partial stem match
        result = _bg.resolve_note_arg("one", graph)
        self.assertIsNotNone(result)
        self.assertIn("One", result)
        # Non-existent
        result = _bg.resolve_note_arg("nonexistent-xyz", graph)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
