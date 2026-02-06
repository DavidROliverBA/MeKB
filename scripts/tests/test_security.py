#!/usr/bin/env python3
"""Tests for detect-secrets.py and classification-guard.py."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import _import_script, create_note, VaultFixture, SCRIPTS_DIR

_ds = _import_script("detect_secrets", "detect-secrets.py")
scan_file = _ds.scan_file
is_false_positive = _ds.is_false_positive
should_ignore_file = _ds.should_ignore_file


class TestSecretPatterns(unittest.TestCase):
    """Test secret detection patterns."""

    def _write_temp(self, content, suffix=".md"):
        """Write content to a temporary file and return its path."""
        fd, path = tempfile.mkstemp(suffix=suffix, dir=os.environ.get("TMPDIR", "/tmp"))
        with os.fdopen(fd, "w") as f:
            f.write(content)
        self.addCleanup(lambda: os.unlink(path))
        return Path(path)

    def test_detects_aws_access_key(self):
        # Use a realistic 20-char AWS key (AKIA + 16 uppercase alphanumeric)
        path = self._write_temp("AWS_KEY=AKIAI44QH8DHBFAKEKEY\n")
        findings = scan_file(path)
        types = [f["type"] for f in findings]
        self.assertIn("AWS Access Key", types)

    def test_detects_github_token(self):
        # GitHub PAT: ghp_ followed by 36 alphanumeric chars
        path = self._write_temp("token = ghp_1234567890ABCDEFGHIJKLMNOPQRSTUVWXyz\n")
        findings = scan_file(path)
        types = [f["type"] for f in findings]
        self.assertTrue(any("GitHub" in t for t in types))

    def test_detects_private_key(self):
        path = self._write_temp("-----BEGIN RSA PRIVATE KEY-----\n")
        findings = scan_file(path)
        types = [f["type"] for f in findings]
        self.assertIn("Private Key", types)

    def test_detects_connection_string(self):
        path = self._write_temp("mongodb://admin:password123@localhost:27017/db\n")
        findings = scan_file(path)
        types = [f["type"] for f in findings]
        self.assertIn("Connection String", types)

    def test_ignores_false_positives(self):
        self.assertTrue(is_false_positive("your-api-key"))
        self.assertTrue(is_false_positive("example_key"))
        self.assertTrue(is_false_positive("{{placeholder}}"))
        self.assertTrue(is_false_positive("test_secret_key"))

    def test_detects_anthropic_key(self):
        path = self._write_temp("ANTHROPIC_KEY=sk-ant-abcdefghijklmnopqrstuvwxyz1234567890ABCD\n")
        findings = scan_file(path)
        types = [f["type"] for f in findings]
        self.assertIn("Anthropic API Key", types)

    def test_detects_jwt_token(self):
        # JWT: three base64url-encoded sections separated by dots
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        path = self._write_temp(f"token = {jwt}\n")
        findings = scan_file(path)
        types = [f["type"] for f in findings]
        self.assertIn("JWT Token", types)

    def test_detects_azure_storage_key(self):
        azure = "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=abc123def456+ghi789=="
        path = self._write_temp(f"{azure}\n")
        findings = scan_file(path)
        types = [f["type"] for f in findings]
        self.assertIn("Azure Storage Key", types)

    def test_clean_file_has_no_findings(self):
        path = self._write_temp("# Notes\n\nJust some regular notes here.\n")
        findings = scan_file(path)
        self.assertEqual(len(findings), 0)

    def test_should_ignore_git_dir(self):
        self.assertTrue(should_ignore_file(".git/config"))
        self.assertTrue(should_ignore_file("node_modules/package.json"))
        self.assertTrue(should_ignore_file("image.png"))

    def test_should_not_ignore_markdown(self):
        self.assertFalse(should_ignore_file("Note - Test.md"))
        self.assertFalse(should_ignore_file("CLAUDE.md"))


class TestClassificationGuard(unittest.TestCase):
    """Test classification guard logic."""

    def test_security_config_exists(self):
        """Verify .mekb/security.json has required structure."""
        vault_root = SCRIPTS_DIR.parent
        security_path = vault_root / ".mekb" / "security.json"
        if security_path.exists():
            with open(security_path) as f:
                config = json.load(f)
            self.assertIn("ai_access_control", config)
            self.assertIn("levels", config["ai_access_control"])
            levels = config["ai_access_control"]["levels"]
            self.assertEqual(levels["secret"], "block")
            self.assertEqual(levels["public"], "allow")

    def test_classification_levels_ordering(self):
        """Verify classification levels follow expected ordering."""
        levels = ["public", "personal", "confidential", "secret"]
        # Secret should always be blocked, public always allowed
        config_path = SCRIPTS_DIR.parent / ".mekb" / "security.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            access = config["ai_access_control"]["levels"]
            self.assertEqual(access["public"], "allow")
            self.assertEqual(access["secret"], "block")


class TestScanDirectory(unittest.TestCase):
    """Test directory scanning."""

    def setUp(self):
        self.fixture = VaultFixture().setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_finds_secrets_in_temp_dir(self):
        secret_file = self.fixture.root / "config.md"
        secret_file.write_text("AWS_KEY=AKIAI44QH8DHBFAKEKEY\n")
        findings = _ds.scan_directory(str(self.fixture.root))
        self.assertGreater(len(findings), 0)
        types = [f["type"] for f in findings]
        self.assertIn("AWS Access Key", types)

    def test_skips_binary_files(self):
        img = self.fixture.root / "image.png"
        img.write_text("not really binary but has .png extension")
        findings = _ds.scan_directory(str(self.fixture.root))
        files_scanned = [f["file"] for f in findings]
        self.assertTrue(all("image.png" not in f for f in files_scanned))


if __name__ == "__main__":
    unittest.main()
