#!/usr/bin/env python3
"""
Browser automation for MeKB.
Fetch web content, extract text, take screenshots.

Uses Playwright when available, falls back to urllib.

Usage:
    python3 scripts/browse.py fetch <url>              # Fetch page content
    python3 scripts/browse.py screenshot <url> [path]  # Screenshot (Playwright only)
    python3 scripts/browse.py links <url>              # Extract links
    python3 scripts/browse.py readability <url>         # Extract main content

Dependencies: Python 3.9+ (stdlib for basic fetch)
Optional: playwright (pip install playwright && playwright install)
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


# ---------------------------------------------------------------------------
# urllib fallback
# ---------------------------------------------------------------------------

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _urllib_fetch(url, timeout=15):
    """Fetch URL content using urllib (stdlib)."""
    import ssl
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            # Fallback for macOS Python without certifi
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        raise


def _extract_title(html_content):
    """Extract <title> from HTML."""
    match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
    if match:
        return html.unescape(match.group(1).strip())
    return None


def _extract_meta(html_content, name):
    """Extract meta tag content by name or property."""
    for attr in ("name", "property"):
        pattern = rf'<meta\s+{attr}=["\']?{re.escape(name)}["\']?\s+content=["\']([^"\']*)["\']'
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            return html.unescape(match.group(1).strip())
        # Reversed attribute order
        pattern2 = rf'<meta\s+content=["\']([^"\']*)["\']?\s+{attr}=["\']?{re.escape(name)}["\']?'
        match2 = re.search(pattern2, html_content, re.IGNORECASE)
        if match2:
            return html.unescape(match2.group(1).strip())
    return None


def _extract_links(html_content, base_url=""):
    """Extract all links from HTML."""
    links = []
    for match in re.finditer(r'<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', html_content, re.IGNORECASE | re.DOTALL):
        href = match.group(1).strip()
        text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        if href and not href.startswith(("#", "javascript:", "mailto:")):
            # Resolve relative URLs
            if base_url and not href.startswith(("http://", "https://")):
                if href.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                else:
                    href = base_url.rstrip("/") + "/" + href
            links.append({"url": href, "text": text[:200]})
    return links


def _strip_html(html_content):
    """Convert HTML to plain text (basic)."""
    # Remove script and style
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html_content, flags=re.IGNORECASE | re.DOTALL)
    # Convert common block elements to newlines
    text = re.sub(r"<(br|hr|/p|/div|/h[1-6]|/li|/tr)[^>]*>", "\n", text, flags=re.IGNORECASE)
    # Remove remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode entities
    text = html.unescape(text)
    # Collapse whitespace
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def _extract_readability(html_content):
    """Extract main content using simple heuristics (no readability library)."""
    # Try to find <article> or <main> first
    for tag in ("article", "main", '[role="main"]'):
        if tag.startswith("["):
            pattern = r'<\w+\s+[^>]*role=["\']main["\'][^>]*>(.*?)</\w+>'
        else:
            pattern = rf"<{tag}[^>]*>(.*?)</{tag}>"
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            return _strip_html(match.group(1))

    # Fallback: strip everything
    return _strip_html(html_content)


# ---------------------------------------------------------------------------
# Playwright backend
# ---------------------------------------------------------------------------

def _has_playwright():
    """Check if Playwright is available."""
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def _playwright_fetch(url, timeout=30000):
    """Fetch page content using Playwright (handles JS-rendered pages)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout)
        page.wait_for_load_state("networkidle", timeout=timeout)
        content = page.content()
        browser.close()
        return content


def _playwright_screenshot(url, output_path, timeout=30000):
    """Take a screenshot using Playwright."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(url, timeout=timeout)
        page.wait_for_load_state("networkidle", timeout=timeout)
        page.screenshot(path=output_path, full_page=True)
        browser.close()
        return output_path


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_fetch(url, use_playwright=False, raw=False):
    """Fetch and process a URL."""
    if use_playwright and _has_playwright():
        html_content = _playwright_fetch(url)
        engine = "playwright"
    else:
        html_content = _urllib_fetch(url)
        engine = "urllib"

    title = _extract_title(html_content)
    description = _extract_meta(html_content, "description") or _extract_meta(html_content, "og:description")
    author = _extract_meta(html_content, "author") or _extract_meta(html_content, "og:site_name")

    if raw:
        print(html_content)
        return

    result = {
        "url": url,
        "engine": engine,
        "title": title,
        "description": description,
        "author": author,
        "content": _strip_html(html_content)[:5000],
    }
    print(json.dumps(result, indent=2))


def cmd_screenshot(url, output_path=None):
    """Take a screenshot of a URL."""
    if not _has_playwright():
        print("Error: Playwright required for screenshots.", file=sys.stderr)
        print("Install: pip install playwright && playwright install", file=sys.stderr)
        sys.exit(1)

    if not output_path:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace(".", "-")
        output_path = f"screenshot-{domain}.png"

    path = _playwright_screenshot(url, output_path)
    print(f"Screenshot saved: {path}")


def cmd_links(url, use_playwright=False):
    """Extract links from a URL."""
    if use_playwright and _has_playwright():
        html_content = _playwright_fetch(url)
    else:
        html_content = _urllib_fetch(url)

    links = _extract_links(html_content, base_url=url)
    for link in links:
        text = link["text"][:60] if link["text"] else "(no text)"
        print(f"  {text:<62} {link['url']}")
    print(f"\n{len(links)} links found.")


def cmd_readability(url, use_playwright=False):
    """Extract main content from a URL."""
    if use_playwright and _has_playwright():
        html_content = _playwright_fetch(url)
    else:
        html_content = _urllib_fetch(url)

    title = _extract_title(html_content)
    content = _extract_readability(html_content)

    if title:
        print(f"# {title}\n")
    print(content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MeKB browser automation")
    parser.add_argument("action", choices=["fetch", "screenshot", "links", "readability"],
                       help="Action to perform")
    parser.add_argument("url", help="URL to process")
    parser.add_argument("output", nargs="?", help="Output path (screenshots)")
    parser.add_argument("--playwright", action="store_true",
                       help="Use Playwright for JS-rendered pages")
    parser.add_argument("--raw", action="store_true",
                       help="Output raw HTML (fetch only)")
    args = parser.parse_args()

    try:
        if args.action == "fetch":
            cmd_fetch(args.url, use_playwright=args.playwright, raw=args.raw)
        elif args.action == "screenshot":
            cmd_screenshot(args.url, args.output)
        elif args.action == "links":
            cmd_links(args.url, use_playwright=args.playwright)
        elif args.action == "readability":
            cmd_readability(args.url, use_playwright=args.playwright)
    except urllib.error.URLError as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
