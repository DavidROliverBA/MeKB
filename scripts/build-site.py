#!/usr/bin/env python3
"""
Static site generator for MeKB.
Convert markdown notes to a browsable HTML site.

Usage:
    python3 scripts/build-site.py                     # Build to _site/
    python3 scripts/build-site.py --output /tmp/site   # Custom output dir
    python3 scripts/build-site.py --serve              # Build and serve locally
    python3 scripts/build-site.py --public-only        # Only public notes
    python3 scripts/build-site.py --stats              # Show build statistics
    python3 scripts/build-site.py --dry-run            # Preview without writing

Dependencies: Python 3.9+ (stdlib only)
"""

import argparse
import html
import http.server
import os
import re
import shutil
import sys
import threading
from datetime import datetime
from pathlib import Path


def find_vault_root():
    """Find the vault root."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(content):
    """Extract YAML frontmatter as dict."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end < 0:
        return {}, content
    yaml_block = content[3:end].strip()
    body = content[end + 3:].strip()

    meta = {}
    for line in yaml_block.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip("\"'")
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            elif val.lower() in ("null", "~", ""):
                val = None
            elif val.startswith("["):
                # Simple list parse
                val = [v.strip().strip("\"'") for v in val.strip("[]").split(",") if v.strip()]
            meta[key.strip()] = val
    return meta, body


# ---------------------------------------------------------------------------
# Markdown to HTML conversion (basic, no dependencies)
# ---------------------------------------------------------------------------

def md_to_html(text, note_index=None):
    """Convert markdown to HTML (basic subset)."""
    lines = text.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False
    code_lang = ""

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                code_lang = line.strip()[3:].strip()
                cls = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
                html_lines.append(f"<pre><code{cls}>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(html.escape(line))
            continue

        stripped = line.strip()

        # Empty line
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("")
            continue

        # Headings
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text_content = heading_match.group(2)
            anchor = re.sub(r"[^a-z0-9-]", "", text_content.lower().replace(" ", "-"))
            html_lines.append(f'<h{level} id="{anchor}">{_inline_md(text_content, note_index)}</h{level}>')
            continue

        # Horizontal rule
        if re.match(r"^[-*_]{3,}$", stripped):
            html_lines.append("<hr>")
            continue

        # Unordered list items
        list_match = re.match(r"^[-*+]\s+(.+)$", stripped)
        if list_match:
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_inline_md(list_match.group(1), note_index)}</li>")
            continue

        # Blockquote
        if stripped.startswith(">"):
            text_content = stripped[1:].strip()
            html_lines.append(f"<blockquote>{_inline_md(text_content, note_index)}</blockquote>")
            continue

        # Close list if needed
        if in_list:
            html_lines.append("</ul>")
            in_list = False

        # Paragraph
        html_lines.append(f"<p>{_inline_md(stripped, note_index)}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_code_block:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)


def _inline_md(text, note_index=None):
    """Convert inline markdown: bold, italic, code, links, wiki-links."""
    # Escape HTML first (except what we generate)
    text = html.escape(text)

    # Code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)

    # Markdown links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    # Wiki-links: [[Title|Display]] and [[Title]]
    def _wiki_link(m):
        full = m.group(1)
        if "|" in full:
            target, display = full.split("|", 1)
        else:
            target = display = full
        target = target.strip()
        display = display.strip()

        if note_index and target in note_index:
            href = note_index[target]
            return f'<a href="{href}" class="wiki-link">{display}</a>'
        return f'<span class="wiki-link broken">{display}</span>'

    text = re.sub(r"\[\[([^\]]+)\]\]", _wiki_link, text)

    return text


# ---------------------------------------------------------------------------
# HTML templates
# ---------------------------------------------------------------------------

SITE_CSS = """
:root {
    --bg: #1a1a2e;
    --surface: #16213e;
    --text: #eee;
    --muted: #888;
    --accent: #e94560;
    --link: #6ec6ff;
    --code-bg: #0f3460;
}
@media (prefers-color-scheme: light) {
    :root {
        --bg: #fafafa;
        --surface: #fff;
        --text: #333;
        --muted: #666;
        --accent: #c62828;
        --link: #1565c0;
        --code-bg: #f5f5f5;
    }
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    max-width: 50rem;
    margin: 0 auto;
    padding: 2rem 1rem;
}
nav { margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--muted); }
nav a { color: var(--link); text-decoration: none; margin-right: 1rem; }
nav a:hover { text-decoration: underline; }
h1, h2, h3, h4 { margin: 1.5rem 0 0.5rem; }
h1 { font-size: 1.8rem; color: var(--accent); }
p { margin: 0.5rem 0; }
a { color: var(--link); }
a.wiki-link { border-bottom: 1px dashed var(--link); text-decoration: none; }
span.wiki-link.broken { color: var(--muted); border-bottom: 1px dashed var(--muted); }
pre { background: var(--code-bg); padding: 1rem; border-radius: 4px; overflow-x: auto; margin: 1rem 0; }
code { font-family: "SF Mono", "Fira Code", monospace; font-size: 0.9em; }
p code { background: var(--code-bg); padding: 0.15rem 0.3rem; border-radius: 3px; }
blockquote { border-left: 3px solid var(--accent); padding-left: 1rem; color: var(--muted); margin: 1rem 0; }
ul { padding-left: 1.5rem; margin: 0.5rem 0; }
li { margin: 0.25rem 0; }
hr { border: none; border-top: 1px solid var(--muted); margin: 2rem 0; }
.meta { color: var(--muted); font-size: 0.85rem; margin-bottom: 1.5rem; }
.meta span { margin-right: 1rem; }
.tag { background: var(--code-bg); padding: 0.1rem 0.5rem; border-radius: 3px; font-size: 0.8rem; }
.note-list { list-style: none; padding: 0; }
.note-list li { padding: 0.5rem 0; border-bottom: 1px solid var(--surface); }
.note-list .type { color: var(--muted); font-size: 0.8rem; margin-right: 0.5rem; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--muted); color: var(--muted); font-size: 0.8rem; }
"""


def page_template(title, content, nav_html="", meta_html=""):
    """Generate full HTML page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} - MeKB</title>
<style>{SITE_CSS}</style>
</head>
<body>
<nav>
<a href="/index.html">Home</a>
<a href="/notes.html">All Notes</a>
<a href="/tags.html">Tags</a>
</nav>
{meta_html}
{content}
<footer>
Generated by MeKB &middot; {datetime.now().strftime("%Y-%m-%d %H:%M")}
</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Site builder
# ---------------------------------------------------------------------------

SKIP_DIRS = {".claude", ".mekb", ".obsidian", ".git", ".github",
             "Templates", "Archive", "secret", "node_modules",
             "__pycache__", "scripts", "_site"}

SKIP_FILES = {"CLAUDE.md", "SOUL.md", "TOOLS.md", "CONTRIBUTING.md",
              "SECURITY.md", "README.md", ".gitignore"}


def collect_notes(vault_root, public_only=False):
    """Collect all publishable notes."""
    notes = []

    for md_file in sorted(vault_root.rglob("*.md")):
        # Skip directories
        rel = md_file.relative_to(vault_root)
        parts = rel.parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        if md_file.name in SKIP_FILES:
            continue

        content = md_file.read_text(errors="replace")
        meta, body = parse_frontmatter(content)

        # Classification filter
        classification = meta.get("classification", "personal")
        if classification in ("secret", "confidential"):
            continue
        if public_only and classification != "public":
            continue

        title = meta.get("title", md_file.stem)
        note_type = meta.get("type", "Note")
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        created = meta.get("created", "")

        # Generate output path
        slug = re.sub(r"[^a-z0-9-]", "", md_file.stem.lower().replace(" ", "-"))
        out_path = f"{slug}.html"

        notes.append({
            "source": md_file,
            "rel_path": str(rel),
            "title": title,
            "type": note_type,
            "tags": tags,
            "created": str(created) if created else "",
            "classification": classification,
            "body": body,
            "meta": meta,
            "slug": slug,
            "out_path": out_path,
        })

    return notes


def build_note_index(notes):
    """Build title -> path index for wiki-link resolution."""
    index = {}
    for note in notes:
        index[note["title"]] = note["out_path"]
        # Also index by filename stem
        stem = note["source"].stem
        if stem not in index:
            index[stem] = note["out_path"]
    return index


def build_site(vault_root, output_dir, public_only=False, dry_run=False):
    """Build the static site."""
    notes = collect_notes(vault_root, public_only=public_only)
    note_index = build_note_index(notes)

    if dry_run:
        print(f"\nDry run: would generate {len(notes)} pages to {output_dir}\n")
        for note in notes[:20]:
            print(f"  {note['out_path']:<50} {note['type']:<12} {note['title']}")
        if len(notes) > 20:
            print(f"  ... and {len(notes) - 20} more")
        return len(notes)

    # Clean and create output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Build individual note pages
    for note in notes:
        content_html = md_to_html(note["body"], note_index)

        meta_parts = []
        if note["type"]:
            meta_parts.append(f'<span class="type">{html.escape(str(note["type"]))}</span>')
        if note["created"]:
            meta_parts.append(f'<span>{html.escape(note["created"])}</span>')
        for tag in (note["tags"] or []):
            meta_parts.append(f'<span class="tag">{html.escape(str(tag))}</span>')

        meta_html = f'<div class="meta">{"".join(meta_parts)}</div>' if meta_parts else ""

        page_html = page_template(
            title=note["title"],
            content=f"<h1>{html.escape(note['title'])}</h1>\n{content_html}",
            meta_html=meta_html,
        )

        out_file = output_dir / note["out_path"]
        out_file.write_text(page_html)

    # Build index page
    recent = sorted(notes, key=lambda n: n["created"] or "", reverse=True)[:20]
    index_items = []
    for note in recent:
        type_badge = f'<span class="type">{html.escape(str(note["type"]))}</span>'
        link = f'<a href="{note["out_path"]}">{html.escape(note["title"])}</a>'
        date = f' <span class="meta">{note["created"]}</span>' if note["created"] else ""
        index_items.append(f"<li>{type_badge} {link}{date}</li>")

    index_html = page_template(
        title="Home",
        content=f"""<h1>MeKB</h1>
<p>Personal knowledge base &middot; {len(notes)} notes</p>
<h2>Recent Notes</h2>
<ul class="note-list">
{"".join(index_items)}
</ul>""",
    )
    (output_dir / "index.html").write_text(index_html)

    # Build all notes page
    by_type = {}
    for note in sorted(notes, key=lambda n: n["title"]):
        t = note["type"] or "Other"
        by_type.setdefault(t, []).append(note)

    all_items = []
    for note_type in sorted(by_type.keys()):
        all_items.append(f"<h2>{html.escape(str(note_type))} ({len(by_type[note_type])})</h2>")
        all_items.append('<ul class="note-list">')
        for note in by_type[note_type]:
            link = f'<a href="{note["out_path"]}">{html.escape(note["title"])}</a>'
            all_items.append(f"<li>{link}</li>")
        all_items.append("</ul>")

    notes_html = page_template(
        title="All Notes",
        content=f"<h1>All Notes ({len(notes)})</h1>\n" + "\n".join(all_items),
    )
    (output_dir / "notes.html").write_text(notes_html)

    # Build tags page
    tag_notes = {}
    for note in notes:
        for tag in (note["tags"] or []):
            tag_str = str(tag)
            tag_notes.setdefault(tag_str, []).append(note)

    tag_items = []
    for tag in sorted(tag_notes.keys()):
        tag_items.append(f"<h2>{html.escape(tag)} ({len(tag_notes[tag])})</h2>")
        tag_items.append('<ul class="note-list">')
        for note in sorted(tag_notes[tag], key=lambda n: n["title"]):
            link = f'<a href="{note["out_path"]}">{html.escape(note["title"])}</a>'
            tag_items.append(f"<li>{link}</li>")
        tag_items.append("</ul>")

    tags_html = page_template(
        title="Tags",
        content=f"<h1>Tags ({len(tag_notes)})</h1>\n" + "\n".join(tag_items),
    )
    (output_dir / "tags.html").write_text(tags_html)

    return len(notes)


def serve_site(output_dir, port=8080):
    """Serve the static site locally."""
    os.chdir(output_dir)
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.HTTPServer(("", port), handler)
    print(f"\nServing at http://localhost:{port}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MeKB static site generator")
    parser.add_argument("--output", "-o", default="_site",
                       help="Output directory (default: _site)")
    parser.add_argument("--serve", "-s", action="store_true",
                       help="Build and serve locally")
    parser.add_argument("--port", type=int, default=8080,
                       help="Port for local server (default: 8080)")
    parser.add_argument("--public-only", action="store_true",
                       help="Only include public notes")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview without writing files")
    parser.add_argument("--stats", action="store_true",
                       help="Show build statistics")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    output_dir = vault_root / args.output

    if args.stats:
        notes = collect_notes(vault_root, public_only=args.public_only)
        by_type = {}
        for note in notes:
            t = note["type"] or "Other"
            by_type.setdefault(t, []).append(note)

        tag_count = len(set(str(t) for n in notes for t in (n["tags"] or [])))

        print(f"\nSite Statistics\n")
        print(f"  Total notes:      {len(notes)}")
        print(f"  Unique tags:      {tag_count}")
        print(f"  Note types:       {len(by_type)}")
        print()
        for t in sorted(by_type.keys()):
            print(f"    {t:<15} {len(by_type[t])}")
        return

    count = build_site(vault_root, output_dir, public_only=args.public_only, dry_run=args.dry_run)
    if not args.dry_run:
        print(f"\nBuilt {count} pages to {output_dir}/")

    if args.serve and not args.dry_run:
        serve_site(output_dir, port=args.port)


if __name__ == "__main__":
    main()
