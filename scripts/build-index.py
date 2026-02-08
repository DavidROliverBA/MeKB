#!/usr/bin/env python3
"""
SQLite FTS5 Search Index Builder for MeKB
Builds a full-text search index from vault markdown files.

Usage:
    python3 scripts/build-index.py              # Build/rebuild index
    python3 scripts/build-index.py --stats       # Show index statistics
    python3 scripts/build-index.py --rebuild     # Force full rebuild
    python3 scripts/build-index.py --verbose     # Show progress

Dependencies: Python 3.9+ (stdlib only - sqlite3 includes FTS5)
"""

import argparse
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

# Folders to skip entirely
SKIP_DIRS = {
    ".git", ".obsidian", ".claude", ".mekb", ".graph",
    "node_modules", "__pycache__", ".venv", "venv",
    "secret",  # Never index secret-classified content
}

# Files to skip
SKIP_FILES = {".DS_Store", "Thumbs.db"}

# Frontmatter regex: captures YAML between --- markers
FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Simple YAML field extractors (avoids pyyaml dependency)
def extract_field(yaml_text, field):
    """Extract a simple scalar field from YAML text."""
    match = re.search(rf"^{field}\s*:\s*(.+)$", yaml_text, re.MULTILINE)
    if match:
        value = match.group(1).strip()
        # Strip quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        if value in ("null", "~", ""):
            return None
        return value
    return None


def extract_list(yaml_text, field):
    """Extract a YAML list field (inline [a, b] or block - a format)."""
    # Inline format: tags: [a, b, c]
    match = re.search(rf"^{field}\s*:\s*\[([^\]]*)\]", yaml_text, re.MULTILINE)
    if match:
        items = [item.strip().strip("'\"") for item in match.group(1).split(",")]
        return [i for i in items if i and i not in ("null", "~")]

    # Block format: tags:\n  - a\n  - b
    match = re.search(rf"^{field}\s*:\s*$", yaml_text, re.MULTILINE)
    if match:
        pos = match.end()
        items = []
        for line in yaml_text[pos:].split("\n"):
            stripped = line.strip()
            if stripped.startswith("- "):
                items.append(stripped[2:].strip().strip("'\""))
            elif stripped and not stripped.startswith("#"):
                break
        return items

    return []


def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content."""
    match = FM_PATTERN.match(content)
    if not match:
        return {}, content

    yaml_text = match.group(1)
    body = content[match.end():]

    fm = {
        "title": extract_field(yaml_text, "title"),
        "type": extract_field(yaml_text, "type"),
        "created": extract_field(yaml_text, "created"),
        "classification": extract_field(yaml_text, "classification"),
        "tags": extract_list(yaml_text, "tags"),
        "verified": extract_field(yaml_text, "verified"),
        "status": extract_field(yaml_text, "status"),
        "encrypted": extract_field(yaml_text, "encrypted"),
    }

    return fm, body


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
    parts = rel.parts

    # Skip directories
    for part in parts[:-1]:
        if part in SKIP_DIRS:
            return True

    # Skip non-markdown files
    if path.suffix != ".md":
        return True

    # Skip specific files
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


def create_schema(conn):
    """Create the database schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            title TEXT,
            type TEXT,
            created TEXT,
            tags TEXT,
            classification TEXT DEFAULT 'personal',
            encrypted INTEGER DEFAULT 0,
            status TEXT,
            verified TEXT,
            content TEXT,
            mtime REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)

    # Create FTS5 virtual table (drop and recreate to ensure sync)
    conn.execute("DROP TABLE IF EXISTS fts_notes")
    conn.execute("""
        CREATE VIRTUAL TABLE fts_notes USING fts5(
            title, type, tags, content,
            content=notes, content_rowid=id
        )
    """)

    # Triggers to keep FTS in sync
    conn.executescript("""
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO fts_notes(rowid, title, type, tags, content)
            VALUES (new.id, new.title, new.type, new.tags, new.content);
        END;

        CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
            INSERT INTO fts_notes(fts_notes, rowid, title, type, tags, content)
            VALUES ('delete', old.id, old.title, old.type, old.tags, old.content);
        END;

        CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
            INSERT INTO fts_notes(fts_notes, rowid, title, type, tags, content)
            VALUES ('delete', old.id, old.title, old.type, old.tags, old.content);
            INSERT INTO fts_notes(rowid, title, type, tags, content)
            VALUES (new.id, new.title, new.type, new.tags, new.content);
        END;
    """)

    conn.commit()


def index_note(conn, path, vault_root):
    """Index a single note into the database."""
    rel_path = str(path.relative_to(vault_root))
    mtime = path.stat().st_mtime

    # Check if already indexed and up to date
    row = conn.execute(
        "SELECT mtime FROM notes WHERE path = ?", (rel_path,)
    ).fetchone()
    if row and row[0] >= mtime:
        return False  # Already up to date

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError):
        return False

    fm, body = parse_frontmatter(content)

    # Skip secret-classified notes
    classification = fm.get("classification") or "personal"
    if classification == "secret":
        # Remove from index if previously indexed
        conn.execute("DELETE FROM notes WHERE path = ?", (rel_path,))
        return False

    title = fm.get("title") or path.stem
    note_type = fm.get("type")
    created = fm.get("created")
    tags = ", ".join(fm.get("tags") or [])
    status = fm.get("status")
    verified = fm.get("verified")
    is_encrypted = fm.get("encrypted") in ("true", "True", True)

    # For encrypted notes, index metadata only (no plaintext body in index)
    indexed_body = "[ENCRYPTED]" if is_encrypted else body

    # Upsert
    conn.execute("""
        INSERT INTO notes (path, title, type, created, tags, classification, encrypted, status, verified, content, mtime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            title=excluded.title, type=excluded.type, created=excluded.created,
            tags=excluded.tags, classification=excluded.classification,
            encrypted=excluded.encrypted,
            status=excluded.status, verified=excluded.verified,
            content=excluded.content, mtime=excluded.mtime
    """, (rel_path, title, note_type, created, tags, classification, int(is_encrypted), status, verified, indexed_body, mtime))

    return True


def remove_deleted(conn, vault_root, current_paths):
    """Remove notes from index that no longer exist on disk."""
    current_set = {str(p.relative_to(vault_root)) for p in current_paths}
    indexed = {row[0] for row in conn.execute("SELECT path FROM notes").fetchall()}
    deleted = indexed - current_set

    for path in deleted:
        conn.execute("DELETE FROM notes WHERE path = ?", (path,))

    return len(deleted)


def rebuild_fts(conn):
    """Rebuild the FTS index from the notes table."""
    conn.execute("INSERT INTO fts_notes(fts_notes) VALUES('rebuild')")
    conn.commit()


def show_stats(db_path):
    """Show index statistics."""
    if not db_path.exists():
        print("No search index found. Run: python3 scripts/build-index.py")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    print(f"\nSearch Index: {db_path}")
    print(f"Total notes indexed: {total}\n")

    # By type
    rows = conn.execute(
        "SELECT COALESCE(type, 'unknown'), COUNT(*) FROM notes GROUP BY type ORDER BY COUNT(*) DESC"
    ).fetchall()
    if rows:
        print("By type:")
        for note_type, count in rows:
            print(f"  {note_type:<20} {count:>4}")

    # By classification
    rows = conn.execute(
        "SELECT COALESCE(classification, 'personal'), COUNT(*) FROM notes GROUP BY classification ORDER BY COUNT(*) DESC"
    ).fetchall()
    if rows:
        print("\nBy classification:")
        for cls, count in rows:
            print(f"  {cls:<20} {count:>4}")

    # Encrypted notes
    try:
        enc_count = conn.execute("SELECT COUNT(*) FROM notes WHERE encrypted = 1").fetchone()[0]
        if enc_count > 0:
            print(f"\nEncrypted notes: {enc_count} (metadata-only in index)")
    except sqlite3.OperationalError:
        pass  # Column may not exist in older indexes

    # Index freshness
    meta = conn.execute("SELECT value FROM meta WHERE key = 'last_built'").fetchone()
    if meta:
        print(f"\nLast built: {meta[0]}")

    db_size = db_path.stat().st_size
    print(f"Database size: {db_size / 1024:.1f} KB")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Build MeKB search index")
    parser.add_argument("--stats", action="store_true", help="Show index statistics")
    parser.add_argument("--rebuild", action="store_true", help="Force full rebuild")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    db_dir = vault_root / ".mekb"
    db_path = db_dir / "search.db"

    if args.stats:
        show_stats(db_path)
        return

    # Ensure .mekb directory exists
    db_dir.mkdir(exist_ok=True)

    # Force rebuild: delete existing database
    if args.rebuild and db_path.exists():
        db_path.unlink()
        if args.verbose:
            print("Removed existing index for full rebuild")

    start = time.time()

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    create_schema(conn)

    # Collect and index notes
    notes = collect_notes(vault_root)
    indexed = 0
    skipped = 0

    for path in notes:
        updated = index_note(conn, path, vault_root)
        if updated:
            indexed += 1
            if args.verbose:
                print(f"  Indexed: {path.relative_to(vault_root)}")
        else:
            skipped += 1

    # Remove deleted notes from index
    removed = remove_deleted(conn, vault_root, notes)

    # Rebuild FTS if any changes
    if indexed > 0 or removed > 0:
        rebuild_fts(conn)

    # Update metadata
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('last_built', ?)",
        (time.strftime("%Y-%m-%d %H:%M:%S"),)
    )
    conn.commit()

    elapsed = time.time() - start
    total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    conn.close()

    print(f"Index built in {elapsed:.2f}s")
    print(f"  Total: {total} notes ({indexed} updated, {skipped} unchanged, {removed} removed)")

    if args.verbose:
        show_stats(db_path)


if __name__ == "__main__":
    main()
