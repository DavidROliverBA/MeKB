"""Shared test helpers for MeKB test suite."""

import importlib.util
import os
import shutil
import tempfile
from pathlib import Path

# Common constants
SCRIPTS_DIR = Path(__file__).parent.parent
VAULT_ROOT = SCRIPTS_DIR.parent


def _import_script(name, filename):
    """Import a Python script with hyphens in its filename."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def create_note(directory, filename, frontmatter=None, body=""):
    """Create a test note with optional frontmatter and body.

    Args:
        directory: Path to write the file in.
        filename: Name of the markdown file.
        frontmatter: Dict of YAML fields (or None for no frontmatter).
        body: Markdown body content.

    Returns:
        Path to the created file.
    """
    parts = []
    if frontmatter:
        parts.append("---")
        for key, value in frontmatter.items():
            if isinstance(value, list):
                items = ", ".join(str(v) for v in value)
                parts.append(f"{key}: [{items}]")
            elif isinstance(value, bool):
                parts.append(f"{key}: {'true' if value else 'false'}")
            elif value is None:
                parts.append(f"{key}: null")
            else:
                parts.append(f"{key}: {value}")
        parts.append("---")
        parts.append("")
    parts.append(body)

    path = Path(directory) / filename
    path.write_text("\n".join(parts))
    return path


class VaultFixture:
    """Create a temporary vault directory for testing.

    Usage:
        fixture = VaultFixture()
        fixture.setup()
        # ... run tests against fixture.root ...
        fixture.teardown()

    Or as a context manager:
        with VaultFixture() as vault:
            create_note(vault.root, "Note - Test.md", ...)
    """

    def __init__(self):
        self.root = None
        self._tmpdir = None

    def setup(self):
        """Create temp vault with .mekb/ directory."""
        self._tmpdir = tempfile.mkdtemp()
        self.root = Path(self._tmpdir)
        (self.root / ".mekb").mkdir()
        (self.root / "CLAUDE.md").write_text("# MeKB\n")
        return self

    def teardown(self):
        """Remove temp vault directory."""
        if self._tmpdir and os.path.exists(self._tmpdir):
            shutil.rmtree(self._tmpdir)

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, *args):
        self.teardown()
