#!/usr/bin/env python3
"""Tests for browse.py — pure function tests (no network calls)."""

import unittest

from helpers import _import_script, SCRIPTS_DIR

_br = _import_script("browse", "browse.py")
_extract_title = _br._extract_title
_extract_meta = _br._extract_meta
_extract_links = _br._extract_links
_strip_html = _br._strip_html
_extract_readability = _br._extract_readability


class TestExtractTitle(unittest.TestCase):
    """Test HTML title extraction."""

    def test_basic_title(self):
        html = "<html><head><title>My Page</title></head><body></body></html>"
        self.assertEqual(_extract_title(html), "My Page")

    def test_html_entities(self):
        html = "<title>Test &amp; More</title>"
        self.assertEqual(_extract_title(html), "Test & More")

    def test_whitespace_stripped(self):
        html = "<title>  Spacey Title  </title>"
        self.assertEqual(_extract_title(html), "Spacey Title")

    def test_no_title(self):
        html = "<html><head></head><body>No title</body></html>"
        self.assertIsNone(_extract_title(html))

    def test_title_with_attributes(self):
        html = '<title lang="en">Attributed</title>'
        self.assertEqual(_extract_title(html), "Attributed")


class TestExtractMeta(unittest.TestCase):
    """Test meta tag extraction."""

    def test_description_by_name(self):
        html = '<meta name="description" content="A great page">'
        self.assertEqual(_extract_meta(html, "description"), "A great page")

    def test_og_description(self):
        html = '<meta property="og:description" content="Open Graph desc">'
        self.assertEqual(_extract_meta(html, "og:description"), "Open Graph desc")

    def test_reversed_attribute_order(self):
        html = '<meta content="Reversed" name="description">'
        self.assertEqual(_extract_meta(html, "description"), "Reversed")

    def test_missing_meta(self):
        html = "<html><head></head></html>"
        self.assertIsNone(_extract_meta(html, "description"))

    def test_entity_decoding(self):
        html = '<meta name="description" content="Test &amp; Decode">'
        self.assertEqual(_extract_meta(html, "description"), "Test & Decode")


class TestExtractLinks(unittest.TestCase):
    """Test link extraction from HTML."""

    def test_basic_extraction(self):
        html = '<a href="https://example.com">Example</a>'
        links = _extract_links(html)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["url"], "https://example.com")
        self.assertEqual(links[0]["text"], "Example")

    def test_skip_anchors(self):
        html = '<a href="#section">Section</a>'
        links = _extract_links(html)
        self.assertEqual(len(links), 0)

    def test_skip_javascript(self):
        html = '<a href="javascript:void(0)">Click</a>'
        links = _extract_links(html)
        self.assertEqual(len(links), 0)

    def test_skip_mailto(self):
        html = '<a href="mailto:test@example.com">Email</a>'
        links = _extract_links(html)
        self.assertEqual(len(links), 0)

    def test_resolve_relative_urls(self):
        html = '<a href="page.html">Page</a>'
        links = _extract_links(html, base_url="https://example.com/dir/")
        self.assertEqual(links[0]["url"], "https://example.com/dir/page.html")

    def test_resolve_absolute_path_urls(self):
        html = '<a href="/about">About</a>'
        links = _extract_links(html, base_url="https://example.com/dir/page")
        self.assertEqual(links[0]["url"], "https://example.com/about")


class TestStripHtml(unittest.TestCase):
    """Test HTML to plain text conversion."""

    def test_tag_removal(self):
        result = _strip_html("<p>Hello <b>world</b></p>")
        self.assertIn("Hello", result)
        self.assertIn("world", result)
        self.assertNotIn("<", result)

    def test_script_removal(self):
        result = _strip_html("<script>alert('xss')</script>Real content")
        self.assertNotIn("alert", result)
        self.assertIn("Real content", result)

    def test_style_removal(self):
        result = _strip_html("<style>body{color:red}</style>Visible text")
        self.assertNotIn("color", result)
        self.assertIn("Visible text", result)

    def test_entity_decoding(self):
        result = _strip_html("Test &amp; More &lt;html&gt;")
        self.assertIn("Test & More", result)

    def test_whitespace_collapse(self):
        result = _strip_html("<p>Line one</p>  <p>  Line two  </p>")
        lines = result.strip().split("\n")
        # Blank lines removed, content preserved
        self.assertTrue(all(line.strip() for line in lines))


class TestExtractReadability(unittest.TestCase):
    """Test readability-style content extraction."""

    def test_article_tag_preferred(self):
        html = "<div>Sidebar</div><article>Main content here</article>"
        result = _extract_readability(html)
        self.assertIn("Main content", result)

    def test_main_tag_preferred(self):
        html = "<nav>Nav</nav><main>The main body of the page</main>"
        result = _extract_readability(html)
        self.assertIn("main body", result)

    def test_fallback_to_full_strip(self):
        html = "<div>Just some <b>content</b> without article/main tags</div>"
        result = _extract_readability(html)
        self.assertIn("Just some", result)
        self.assertIn("content", result)


if __name__ == "__main__":
    unittest.main()
