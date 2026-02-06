#!/usr/bin/env python3
"""
Vector Embeddings Builder for MeKB
Generates vector embeddings for semantic search.

Usage:
    python3 scripts/build-embeddings.py              # Build/update embeddings
    python3 scripts/build-embeddings.py --stats       # Show embedding statistics
    python3 scripts/build-embeddings.py --rebuild     # Force full rebuild
    python3 scripts/build-embeddings.py --model <name> # Use specific model

Dependencies: Python 3.9+
Required: sentence-transformers (pip install sentence-transformers)

This script is OPTIONAL. FTS5 search works without it.
If sentence-transformers is not installed, the script exits with a helpful message.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Check for required dependency upfront
try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Folders to skip
SKIP_DIRS = {
    ".git", ".obsidian", ".claude", ".mekb", ".graph",
    "node_modules", "__pycache__", ".venv", "venv",
    "secret",
}

SKIP_FILES = {".DS_Store", "Thumbs.db"}

# Default embedding model (small, fast, good quality)
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Frontmatter regex
FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_field(yaml_text, field):
    """Extract a simple scalar field from YAML text."""
    match = re.search(rf"^{field}\s*:\s*(.+)$", yaml_text, re.MULTILINE)
    if match:
        value = match.group(1).strip().strip("'\"")
        if value in ("null", "~", ""):
            return None
        return value
    return None


def extract_list(yaml_text, field):
    """Extract a YAML list field."""
    match = re.search(rf"^{field}\s*:\s*\[([^\]]*)\]", yaml_text, re.MULTILINE)
    if match:
        items = [item.strip().strip("'\"") for item in match.group(1).split(",")]
        return [i for i in items if i and i not in ("null", "~")]
    return []


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content."""
    match = FM_PATTERN.match(content)
    if not match:
        return {}, content

    yaml_text = match.group(1)
    body = content[match.end():]

    return {
        "title": extract_field(yaml_text, "title"),
        "type": extract_field(yaml_text, "type"),
        "classification": extract_field(yaml_text, "classification"),
        "tags": extract_list(yaml_text, "tags"),
    }, body


def find_vault_root():
    """Find the vault root by looking for .mekb/ or CLAUDE.md."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def should_skip(path, vault_root):
    """Check if a path should be skipped."""
    rel = path.relative_to(vault_root)
    for part in rel.parts[:-1]:
        if part in SKIP_DIRS:
            return True
    if path.suffix != ".md":
        return True
    if path.name in SKIP_FILES:
        return True
    return False


def collect_notes(vault_root):
    """Collect all indexable markdown files."""
    notes = []
    for path in vault_root.rglob("*.md"):
        if not should_skip(path, vault_root):
            notes.append(path)
    return sorted(notes)


def prepare_text(title, note_type, tags, body):
    """Prepare text for embedding - combine metadata and content."""
    parts = []
    if title:
        parts.append(f"Title: {title}")
    if note_type:
        parts.append(f"Type: {note_type}")
    if tags:
        parts.append(f"Tags: {', '.join(tags)}")
    # Truncate body to avoid excessive embedding time
    body_clean = re.sub(r'\n{3,}', '\n\n', body)
    body_clean = re.sub(r'```.*?```', '', body_clean, flags=re.DOTALL)  # Remove code blocks
    body_clean = re.sub(r'\[\[([^\]]+)\]\]', r'\1', body_clean)  # Unwrap wiki-links
    body_clean = body_clean[:3000]  # Limit content length
    parts.append(body_clean)
    return "\n".join(parts)


def load_existing(embeddings_path):
    """Load existing embeddings file."""
    if not embeddings_path.exists():
        return {"model": None, "embeddings": {}}
    try:
        with open(embeddings_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"model": None, "embeddings": {}}


def build_embeddings(vault_root, model_name=None, rebuild=False, verbose=False):
    """Build or update vector embeddings for all notes."""
    model_name = model_name or DEFAULT_MODEL
    embeddings_path = vault_root / ".mekb" / "embeddings.json"

    # Load existing
    data = {} if rebuild else load_existing(embeddings_path)
    existing = data.get("embeddings", {})

    # If model changed, force rebuild
    if data.get("model") and data["model"] != model_name:
        print(f"Model changed from {data['model']} to {model_name}, rebuilding all")
        existing = {}

    # Collect notes
    notes = collect_notes(vault_root)
    to_embed = []

    for path in notes:
        rel_path = str(path.relative_to(vault_root))
        mtime = path.stat().st_mtime

        # Skip if already embedded and file hasn't changed
        if rel_path in existing and existing[rel_path].get("mtime", 0) >= mtime:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except (IOError, OSError):
            continue

        fm, body = parse_frontmatter(content)

        # Skip secret-classified content
        classification = fm.get("classification") or "personal"
        if classification == "secret":
            existing.pop(rel_path, None)
            continue

        title = fm.get("title") or path.stem
        text = prepare_text(title, fm.get("type"), fm.get("tags", []), body)
        to_embed.append((rel_path, title, fm.get("type"), mtime, text))

    if not to_embed:
        print("All embeddings up to date.")
        return

    # Load model
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)

    # Batch encode
    texts = [item[4] for item in to_embed]
    print(f"Embedding {len(texts)} note(s)...")
    start = time.time()
    vectors = model.encode(texts, show_progress_bar=verbose, batch_size=32)
    elapsed = time.time() - start

    # Update embeddings
    for i, (rel_path, title, note_type, mtime, _) in enumerate(to_embed):
        existing[rel_path] = {
            "title": title,
            "type": note_type,
            "mtime": mtime,
            "vector": vectors[i].tolist(),
        }
        if verbose:
            print(f"  Embedded: {rel_path}")

    # Remove deleted notes
    current_paths = {str(p.relative_to(vault_root)) for p in notes}
    for path in list(existing.keys()):
        if path not in current_paths:
            del existing[path]
            if verbose:
                print(f"  Removed: {path}")

    # Save
    output = {
        "model": model_name,
        "dimension": len(vectors[0]) if len(vectors) > 0 else 0,
        "count": len(existing),
        "built": time.strftime("%Y-%m-%d %H:%M:%S"),
        "embeddings": existing,
    }

    embeddings_path.parent.mkdir(exist_ok=True)
    with open(embeddings_path, "w") as f:
        json.dump(output, f)

    print(f"Embedded {len(texts)} notes in {elapsed:.2f}s")
    print(f"Total: {len(existing)} embeddings ({embeddings_path.stat().st_size / 1024:.1f} KB)")


def show_stats(embeddings_path):
    """Show embedding statistics."""
    if not embeddings_path.exists():
        print("No embeddings found. Run: python3 scripts/build-embeddings.py")
        print("(Requires: pip install sentence-transformers)")
        sys.exit(1)

    with open(embeddings_path, "r") as f:
        data = json.load(f)

    embeddings = data.get("embeddings", {})
    print(f"\nEmbeddings: {embeddings_path}")
    print(f"Model: {data.get('model', 'unknown')}")
    print(f"Dimension: {data.get('dimension', 'unknown')}")
    print(f"Total notes: {data.get('count', len(embeddings))}")
    print(f"Built: {data.get('built', 'unknown')}")
    print(f"File size: {embeddings_path.stat().st_size / 1024:.1f} KB")

    # By type
    by_type = {}
    for entry in embeddings.values():
        t = entry.get("type") or "unknown"
        by_type[t] = by_type.get(t, 0) + 1

    if by_type:
        print("\nBy type:")
        for note_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
            print(f"  {note_type:<20} {count:>4}")


def main():
    parser = argparse.ArgumentParser(description="Build MeKB vector embeddings")
    parser.add_argument("--stats", action="store_true", help="Show embedding statistics")
    parser.add_argument("--rebuild", action="store_true", help="Force full rebuild")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Embedding model (default: {DEFAULT_MODEL})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    embeddings_path = vault_root / ".mekb" / "embeddings.json"

    if args.stats:
        show_stats(embeddings_path)
        return

    if not HAS_TRANSFORMERS:
        print("Vector embeddings require sentence-transformers.")
        print("Install with: pip install sentence-transformers")
        print()
        print("This is OPTIONAL - FTS5 search works without embeddings.")
        print("Run: python3 scripts/search.py \"query\" for keyword search.")
        sys.exit(1)

    build_embeddings(vault_root, model_name=args.model, rebuild=args.rebuild, verbose=args.verbose)


if __name__ == "__main__":
    main()
