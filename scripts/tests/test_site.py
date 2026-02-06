#!/usr/bin/env python3
"""Tests for build-site.py."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import _import_script, create_note, VaultFixture, SCRIPTS_DIR

_bs = _import_script("build_site", "build-site.py")
parse_frontmatter = _bs.parse_frontmatter
md_to_html = _bs.md_to_html
_inline_md = _bs._inline_md
collect_notes = _bs.collect_notes
build_site = _bs.build_site
SKIP_DIRS = _bs.SKIP_DIRS
SKIP_FILES = _bs.SKIP_FILES


class TestSiteFrontmatter(unittest.TestCase):
    """Test frontmatter parsing for the site generator."""

    def test_basic_parsing(self):
        content = "---\ntype: Concept\ntitle: Test\n---\n\nBody text."
        meta, body = parse_frontmatter(content)
        self.assertEqual(meta["type"], "Concept")
        self.assertEqual(meta["title"], "Test")
        self.assertIn("Body text", body)

    def test_no_frontmatter(self):
        content = "# Just markdown\n\nNo frontmatter here."
        meta, body = parse_frontmatter(content)
        self.assertEqual(meta, {})
        self.assertIn("Just markdown", body)

    def test_boolean_values(self):
        content = "---\nverified: true\narchived: false\n---\n"
        meta, body = parse_frontmatter(content)
        self.assertIs(meta["verified"], True)
        self.assertIs(meta["archived"], False)

    def test_null_values(self):
        content = "---\ntitle: null\ndescription: ~\nempty:\n---\n"
        meta, body = parse_frontmatter(content)
        self.assertIsNone(meta["title"])
        self.assertIsNone(meta["description"])
        self.assertIsNone(meta.get("empty"))

    def test_list_values(self):
        content = "---\ntags: [domain/data, activity/research]\n---\n"
        meta, body = parse_frontmatter(content)
        self.assertEqual(meta["tags"], ["domain/data", "activity/research"])


class TestMarkdownToHtml(unittest.TestCase):
    """Test markdown to HTML conversion."""

    def test_heading_h1(self):
        result = md_to_html("# Heading One")
        self.assertIn("<h1", result)
        self.assertIn("Heading One", result)

    def test_heading_h3(self):
        result = md_to_html("### Heading Three")
        self.assertIn("<h3", result)

    def test_heading_h6(self):
        result = md_to_html("###### Heading Six")
        self.assertIn("<h6", result)

    def test_heading_anchors(self):
        result = md_to_html("## My Section")
        self.assertIn('id="my-section"', result)

    def test_bold(self):
        result = md_to_html("This is **bold** text")
        self.assertIn("<strong>bold</strong>", result)

    def test_italic(self):
        result = md_to_html("This is *italic* text")
        self.assertIn("<em>italic</em>", result)

    def test_inline_code(self):
        result = md_to_html("Use `code` here")
        self.assertIn("<code>code</code>", result)

    def test_code_block(self):
        result = md_to_html("```python\nprint('hello')\n```")
        self.assertIn("<pre><code", result)
        self.assertIn("language-python", result)
        self.assertIn("print(", result)

    def test_unordered_list(self):
        result = md_to_html("- Item one\n- Item two")
        self.assertIn("<ul>", result)
        self.assertIn("<li>", result)
        self.assertIn("Item one", result)

    def test_blockquote(self):
        result = md_to_html("> Quoted text")
        self.assertIn("<blockquote>", result)
        self.assertIn("Quoted text", result)

    def test_horizontal_rule(self):
        result = md_to_html("---")
        self.assertIn("<hr>", result)

    def test_paragraph(self):
        result = md_to_html("Simple paragraph text.")
        self.assertIn("<p>Simple paragraph text.</p>", result)

    def test_html_escaping(self):
        result = md_to_html("Use <script>alert('xss')</script> here")
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)

    def test_empty_input(self):
        result = md_to_html("")
        self.assertEqual(result, "")


class TestInlineMarkdown(unittest.TestCase):
    """Test inline markdown processing."""

    def test_markdown_link(self):
        result = _inline_md("[Click here](https://example.com)")
        self.assertIn('href="https://example.com"', result)
        self.assertIn("Click here", result)

    def test_wiki_link_resolved(self):
        index = {"Test Note": "test-note.html"}
        result = _inline_md("See [[Test Note]] for details", index)
        self.assertIn('href="test-note.html"', result)
        self.assertIn("wiki-link", result)

    def test_wiki_link_aliased(self):
        index = {"Person - Jane Smith": "person---jane-smith.html"}
        result = _inline_md("See [[Person - Jane Smith|Jane]]", index)
        self.assertIn("Jane", result)
        self.assertIn("wiki-link", result)

    def test_broken_wiki_link(self):
        result = _inline_md("See [[Missing Note]]", {})
        self.assertIn("broken", result)
        self.assertIn("Missing Note", result)

    def test_combined_formatting(self):
        result = _inline_md("Use **bold** and `code` together")
        self.assertIn("<strong>bold</strong>", result)
        self.assertIn("<code>code</code>", result)


class TestSiteNoteCollection(unittest.TestCase):
    """Test note collection for site building."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        create_note(self.fixture.root, "Concept - Test.md",
                     {"type": "Concept", "title": "Test"}, "# Test\n\nContent")
        create_note(self.fixture.root, "Pattern - One.md",
                     {"type": "Pattern", "title": "One"}, "# One\n\nContent")

    def tearDown(self):
        self.fixture.teardown()

    def test_collects_markdown_only(self):
        (self.fixture.root / "image.png").write_text("not markdown")
        notes = collect_notes(self.fixture.root)
        paths = [n["source"].name for n in notes]
        self.assertNotIn("image.png", paths)

    def test_excludes_secret(self):
        create_note(self.fixture.root, "Secret - Creds.md",
                     {"type": "Note", "title": "Creds", "classification": "secret"},
                     "password123")
        notes = collect_notes(self.fixture.root)
        titles = [n["title"] for n in notes]
        self.assertNotIn("Creds", titles)

    def test_excludes_confidential(self):
        create_note(self.fixture.root, "Note - Private.md",
                     {"type": "Note", "title": "Private", "classification": "confidential"},
                     "sensitive")
        notes = collect_notes(self.fixture.root)
        titles = [n["title"] for n in notes]
        self.assertNotIn("Private", titles)

    def test_public_only_mode(self):
        create_note(self.fixture.root, "Note - Personal.md",
                     {"type": "Note", "title": "Personal", "classification": "personal"},
                     "my note")
        create_note(self.fixture.root, "Note - Public.md",
                     {"type": "Note", "title": "Public", "classification": "public"},
                     "public note")
        notes = collect_notes(self.fixture.root, public_only=True)
        titles = [n["title"] for n in notes]
        self.assertNotIn("Personal", titles)
        self.assertIn("Public", titles)

    def test_skip_dirs(self):
        scripts_dir = self.fixture.root / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "helper.md").write_text("---\ntype: Note\n---\n")
        notes = collect_notes(self.fixture.root)
        sources = [str(n["source"]) for n in notes]
        self.assertFalse(any("scripts" in s for s in sources))

    def test_skip_files(self):
        notes = collect_notes(self.fixture.root)
        sources = [n["source"].name for n in notes]
        self.assertNotIn("CLAUDE.md", sources)


class TestSiteBuilder(unittest.TestCase):
    """Test full site build."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        create_note(self.fixture.root, "Concept - Alpha.md",
                     {"type": "Concept", "title": "Alpha", "created": "2026-01-01",
                      "tags": ["domain/data"]}, "# Alpha\n\nContent about Alpha.")
        create_note(self.fixture.root, "Pattern - Beta.md",
                     {"type": "Pattern", "title": "Beta", "created": "2026-01-02"},
                     "# Beta\n\nContent about Beta.")
        self.output_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        self.fixture.teardown()
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

    def test_creates_index_html(self):
        build_site(self.fixture.root, self.output_dir)
        self.assertTrue((self.output_dir / "index.html").exists())

    def test_creates_notes_html(self):
        build_site(self.fixture.root, self.output_dir)
        self.assertTrue((self.output_dir / "notes.html").exists())

    def test_creates_tags_html(self):
        build_site(self.fixture.root, self.output_dir)
        self.assertTrue((self.output_dir / "tags.html").exists())

    def test_creates_per_note_pages(self):
        count = build_site(self.fixture.root, self.output_dir)
        self.assertGreaterEqual(count, 2)
        html_files = list(self.output_dir.glob("*.html"))
        # At least index + notes + tags + 2 note pages
        self.assertGreaterEqual(len(html_files), 5)

    def test_dry_run_creates_nothing(self):
        clean_dir = Path(tempfile.mkdtemp())
        try:
            count = build_site(self.fixture.root, clean_dir, dry_run=True)
            self.assertGreater(count, 0)
            # Dry run should not create the output directory contents
            html_files = list(clean_dir.glob("*.html"))
            self.assertEqual(len(html_files), 0)
        finally:
            shutil.rmtree(clean_dir)


if __name__ == "__main__":
    unittest.main()
