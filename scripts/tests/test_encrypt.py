#!/usr/bin/env python3
"""Tests for encrypt.py - MeKB note encryption/decryption."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from helpers import _import_script, create_note, VaultFixture

_enc = _import_script("encrypt", "encrypt.py")
split_frontmatter = _enc.split_frontmatter
parse_frontmatter_fields = _enc.parse_frontmatter_fields
add_encryption_fields = _enc.add_encryption_fields
remove_encryption_fields = _enc.remove_encryption_fields
reassemble = _enc.reassemble
is_encrypted = _enc.is_encrypted
encrypt_body = _enc.encrypt_body
decrypt_body = _enc.decrypt_body
encrypt_file = _enc.encrypt_file
decrypt_file = _enc.decrypt_file
file_status = _enc.file_status
audit_vault = _enc.audit_vault
AGE_BEGIN = _enc.AGE_BEGIN
AGE_END = _enc.AGE_END


# Whether age CLI is available for integration tests
HAS_AGE = shutil.which("age") is not None


class TestSplitFrontmatter(unittest.TestCase):
    """Test frontmatter splitting."""

    def test_standard_frontmatter(self):
        content = "---\ntitle: Test Note\ntype: Note\n---\n# Hello\n\nBody here.\n"
        fm, body, has_fm = split_frontmatter(content)
        self.assertTrue(has_fm)
        self.assertIn("title: Test Note", fm)
        self.assertIn("---", fm)
        self.assertIn("# Hello", body)
        self.assertIn("Body here.", body)

    def test_no_frontmatter(self):
        content = "# Just a heading\n\nSome text.\n"
        fm, body, has_fm = split_frontmatter(content)
        self.assertFalse(has_fm)
        self.assertEqual(fm, "")
        self.assertEqual(body, content)

    def test_empty_content(self):
        fm, body, has_fm = split_frontmatter("")
        self.assertFalse(has_fm)
        self.assertEqual(fm, "")
        self.assertEqual(body, "")

    def test_frontmatter_only(self):
        content = "---\ntitle: Just FM\ntype: Note\n---\n"
        fm, body, has_fm = split_frontmatter(content)
        self.assertTrue(has_fm)
        self.assertIn("title: Just FM", fm)
        self.assertEqual(body, "")

    def test_preserves_multiline_yaml(self):
        content = (
            "---\ntitle: Complex Note\n"
            "tags:\n  - domain/security\n  - activity/research\n"
            "classification: confidential\n---\n"
            "# Body\n"
        )
        fm, body, has_fm = split_frontmatter(content)
        self.assertTrue(has_fm)
        self.assertIn("tags:", fm)
        self.assertIn("  - domain/security", fm)
        self.assertEqual(body.strip(), "# Body")

    def test_roundtrip_preserves_content(self):
        content = "---\ntitle: Round Trip\ntype: Note\n---\n# Body\n\nParagraph.\n"
        fm, body, has_fm = split_frontmatter(content)
        result = reassemble(fm, body)
        self.assertEqual(result, content)

    def test_frontmatter_with_special_chars(self):
        content = '---\ntitle: "Note: Special (chars) & more"\ntype: Note\n---\n# Body\n'
        fm, body, has_fm = split_frontmatter(content)
        self.assertTrue(has_fm)
        self.assertIn('title: "Note: Special (chars) & more"', fm)


class TestParseFrontmatterFields(unittest.TestCase):
    """Test frontmatter field extraction."""

    def test_extract_basic_fields(self):
        fm = "---\ntitle: Test\ntype: Note\nclassification: confidential\n---\n"
        fields = parse_frontmatter_fields(fm)
        self.assertEqual(fields["title"], "Test")
        self.assertEqual(fields["type"], "Note")
        self.assertEqual(fields["classification"], "confidential")

    def test_extract_boolean_true(self):
        fm = "---\nencrypted: true\n---\n"
        fields = parse_frontmatter_fields(fm)
        self.assertTrue(fields["encrypted"])

    def test_extract_boolean_false(self):
        fm = "---\nencrypted: false\n---\n"
        fields = parse_frontmatter_fields(fm)
        self.assertFalse(fields["encrypted"])

    def test_extract_integer(self):
        fm = "---\nencryption_recipients: 2\n---\n"
        fields = parse_frontmatter_fields(fm)
        self.assertEqual(fields["encryption_recipients"], 2)

    def test_extract_quoted_string(self):
        fm = '---\ntitle: "My Note Title"\n---\n'
        fields = parse_frontmatter_fields(fm)
        self.assertEqual(fields["title"], "My Note Title")

    def test_no_frontmatter(self):
        fields = parse_frontmatter_fields("# Just text\n")
        self.assertEqual(fields, {})


class TestAddEncryptionFields(unittest.TestCase):
    """Test adding encryption metadata to frontmatter."""

    def test_adds_fields(self):
        fm = "---\ntitle: Test\ntype: Note\n---\n"
        result = add_encryption_fields(fm, recipient_count=2)
        self.assertIn("encrypted: true", result)
        self.assertIn("encryption_method: age", result)
        self.assertIn("encryption_recipients: 2", result)
        # Should still have the closing ---
        self.assertTrue(result.rstrip().endswith("---"))

    def test_idempotent(self):
        fm = "---\ntitle: Test\nencrypted: true\nencryption_method: age\nencryption_recipients: 2\n---\n"
        result = add_encryption_fields(fm, recipient_count=2)
        # Should not duplicate fields
        self.assertEqual(result.count("encrypted: true"), 1)
        self.assertEqual(result.count("encryption_method: age"), 1)

    def test_updates_recipient_count(self):
        fm = "---\ntitle: Test\nencrypted: true\nencryption_method: age\nencryption_recipients: 1\n---\n"
        result = add_encryption_fields(fm, recipient_count=3)
        self.assertIn("encryption_recipients: 3", result)
        self.assertNotIn("encryption_recipients: 1", result)

    def test_empty_frontmatter(self):
        result = add_encryption_fields("")
        self.assertEqual(result, "")

    def test_preserves_existing_fields(self):
        fm = "---\ntitle: My Note\nclassification: confidential\ntags: [domain/security]\n---\n"
        result = add_encryption_fields(fm, recipient_count=1)
        self.assertIn("title: My Note", result)
        self.assertIn("classification: confidential", result)
        self.assertIn("tags: [domain/security]", result)
        self.assertIn("encrypted: true", result)


class TestRemoveEncryptionFields(unittest.TestCase):
    """Test removing encryption metadata from frontmatter."""

    def test_removes_fields(self):
        fm = "---\ntitle: Test\nencrypted: true\nencryption_method: age\nencryption_recipients: 2\n---\n"
        result = remove_encryption_fields(fm)
        self.assertNotIn("encrypted:", result)
        self.assertNotIn("encryption_method:", result)
        self.assertNotIn("encryption_recipients:", result)
        self.assertIn("title: Test", result)

    def test_no_encryption_fields(self):
        fm = "---\ntitle: Test\ntype: Note\n---\n"
        result = remove_encryption_fields(fm)
        self.assertIn("title: Test", result)
        self.assertIn("type: Note", result)


class TestReassemble(unittest.TestCase):
    """Test reassembling frontmatter and body."""

    def test_basic_reassembly(self):
        fm = "---\ntitle: Test\n---\n"
        body = "# Heading\n\nBody text.\n"
        result = reassemble(fm, body)
        self.assertEqual(result, fm + body)

    def test_empty_body(self):
        fm = "---\ntitle: Test\n---\n"
        result = reassemble(fm, "")
        self.assertEqual(result, fm)

    def test_no_frontmatter(self):
        result = reassemble("", "# Just body\n")
        self.assertEqual(result, "# Just body\n")


class TestIsEncrypted(unittest.TestCase):
    """Test encrypted content detection."""

    def test_detects_encrypted(self):
        content = f"---\ntitle: Test\n---\n{AGE_BEGIN}\ndata\n{AGE_END}\n"
        self.assertTrue(is_encrypted(content))

    def test_detects_plaintext(self):
        content = "---\ntitle: Test\n---\n# Regular body\n"
        self.assertFalse(is_encrypted(content))

    def test_empty_content(self):
        self.assertFalse(is_encrypted(""))


@unittest.skipUnless(HAS_AGE, "age CLI not installed")
class TestEncryptDecryptIntegration(unittest.TestCase):
    """Integration tests requiring age CLI."""

    def setUp(self):
        """Generate a temporary age key pair for testing."""
        self.tmpdir = tempfile.mkdtemp()

        # Generate age key
        result = subprocess.run(
            ["age-keygen"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"age-keygen failed: {result.stderr}")

        # Parse output: public key is on comment line, private key follows
        self.identity_path = os.path.join(self.tmpdir, "test-key.txt")
        with open(self.identity_path, "w") as f:
            f.write(result.stdout)

        # Extract public key from the comment line
        for line in result.stderr.split("\n"):
            if line.startswith("Public key:"):
                self.public_key = line.split(": ")[1].strip()
                break
        else:
            # Try stdout for older age versions
            for line in result.stdout.split("\n"):
                if line.startswith("# public key:"):
                    self.public_key = line.split(": ")[1].strip()
                    break

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_encrypt_decrypt_roundtrip(self):
        """Body survives an encrypt/decrypt cycle unchanged."""
        body = "# Secret Notes\n\nThis is confidential information.\n\n- Item 1\n- Item 2\n"
        encrypted = encrypt_body(body, [self.public_key])

        self.assertIn(AGE_BEGIN, encrypted)
        self.assertIn(AGE_END, encrypted)
        self.assertNotIn("Secret Notes", encrypted)
        self.assertNotIn("confidential information", encrypted)

        decrypted = decrypt_body(encrypted, self.identity_path)
        self.assertEqual(decrypted, body)

    def test_encrypt_empty_body(self):
        """Encrypting an empty string still produces valid ciphertext."""
        encrypted = encrypt_body("", [self.public_key])
        self.assertIn(AGE_BEGIN, encrypted)
        decrypted = decrypt_body(encrypted, self.identity_path)
        self.assertEqual(decrypted, "")

    def test_encrypt_unicode(self):
        """Unicode content survives encryption."""
        body = "# Notes\n\nEmoji: \U0001f512 Lock, \U0001f511 Key\nAccented: cafe\u0301\nCJK: \u77e5\u8b58\n"
        encrypted = encrypt_body(body, [self.public_key])
        decrypted = decrypt_body(encrypted, self.identity_path)
        self.assertEqual(decrypted, body)

    def test_encrypt_large_body(self):
        """Performance acceptable for large notes (~100KB)."""
        body = "# Large Note\n\n" + ("Lorem ipsum dolor sit amet. " * 5000)
        encrypted = encrypt_body(body, [self.public_key])
        decrypted = decrypt_body(encrypted, self.identity_path)
        self.assertEqual(decrypted, body)

    def test_file_encrypt_decrypt_roundtrip(self):
        """Full file encrypt/decrypt preserves frontmatter and body."""
        note_path = os.path.join(self.tmpdir, "Note - Secret.md")
        original_content = (
            "---\n"
            "title: Secret Info\n"
            "type: Note\n"
            "classification: confidential\n"
            "---\n"
            "# Secret Content\n\n"
            "This should be encrypted.\n"
        )
        Path(note_path).write_text(original_content)

        # Encrypt
        result = encrypt_file(note_path, [self.public_key])
        self.assertTrue(result)

        encrypted_content = Path(note_path).read_text()
        # Frontmatter should be plaintext
        self.assertIn("title: Secret Info", encrypted_content)
        self.assertIn("classification: confidential", encrypted_content)
        self.assertIn("encrypted: true", encrypted_content)
        self.assertIn("encryption_method: age", encrypted_content)
        # Body should be encrypted
        self.assertIn(AGE_BEGIN, encrypted_content)
        self.assertNotIn("# Secret Content", encrypted_content)

        # Decrypt
        result = decrypt_file(note_path, self.identity_path)
        self.assertTrue(result)

        decrypted_content = Path(note_path).read_text()
        # Should match original (minus encryption fields)
        self.assertIn("title: Secret Info", decrypted_content)
        self.assertIn("# Secret Content", decrypted_content)
        self.assertIn("This should be encrypted.", decrypted_content)
        self.assertNotIn("encrypted: true", decrypted_content)
        self.assertNotIn(AGE_BEGIN, decrypted_content)

    def test_encrypt_already_encrypted_skips(self):
        """Encrypting an already-encrypted file returns False."""
        note_path = os.path.join(self.tmpdir, "Note - Already.md")
        content = (
            "---\ntitle: Already\nencrypted: true\n---\n"
            f"{AGE_BEGIN}\ndata\n{AGE_END}\n"
        )
        Path(note_path).write_text(content)
        result = encrypt_file(note_path, [self.public_key])
        self.assertFalse(result)

    def test_decrypt_plaintext_skips(self):
        """Decrypting a plaintext file returns False."""
        note_path = os.path.join(self.tmpdir, "Note - Plain.md")
        Path(note_path).write_text("---\ntitle: Plain\n---\n# Body\n")
        result = decrypt_file(note_path, self.identity_path)
        self.assertFalse(result)

    def test_multi_recipient_encrypt(self):
        """File encrypted for multiple recipients is decryptable by each."""
        # Generate second key
        result = subprocess.run(["age-keygen"], capture_output=True, text=True)
        second_key_path = os.path.join(self.tmpdir, "second-key.txt")
        with open(second_key_path, "w") as f:
            f.write(result.stdout)
        for line in result.stderr.split("\n"):
            if line.startswith("Public key:"):
                second_pub = line.split(": ")[1].strip()
                break

        body = "Multi-recipient test\n"
        encrypted = encrypt_body(body, [self.public_key, second_pub])

        # Both keys should decrypt
        d1 = decrypt_body(encrypted, self.identity_path)
        d2 = decrypt_body(encrypted, second_key_path)
        self.assertEqual(d1, body)
        self.assertEqual(d2, body)


class TestEncryptBodyErrors(unittest.TestCase):
    """Test error handling in encryption functions."""

    def test_no_recipients_raises(self):
        with self.assertRaises(ValueError):
            encrypt_body("test", [])

    @patch("encrypt.check_age_installed", return_value=False)
    def test_no_age_raises(self, _mock):
        with self.assertRaises(RuntimeError):
            encrypt_body("test", ["age1fake..."])

    @patch("encrypt.check_age_installed", return_value=False)
    def test_decrypt_no_age_raises(self, _mock):
        with self.assertRaises(RuntimeError):
            decrypt_body("ciphertext", "/some/identity")


class TestFileStatus(unittest.TestCase):
    """Test file status reporting."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_plaintext_status(self):
        path = os.path.join(self.tmpdir, "Note - Plain.md")
        Path(path).write_text("---\ntitle: Plain\nclassification: personal\n---\n# Body\n")
        status = file_status(path)
        self.assertFalse(status["encrypted"])
        self.assertEqual(status["classification"], "personal")

    def test_encrypted_status(self):
        path = os.path.join(self.tmpdir, "Note - Secret.md")
        content = (
            "---\ntitle: Secret\nclassification: confidential\n"
            "encrypted: true\nencryption_method: age\nencryption_recipients: 2\n---\n"
            f"{AGE_BEGIN}\ndata\n{AGE_END}\n"
        )
        Path(path).write_text(content)
        status = file_status(path)
        self.assertTrue(status["encrypted"])
        self.assertEqual(status["classification"], "confidential")
        self.assertEqual(status["encryption_method"], "age")
        self.assertEqual(status["encryption_recipients"], 2)


class TestAuditVault(unittest.TestCase):
    """Test vault encryption audit."""

    def setUp(self):
        self.fixture = VaultFixture().setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_detects_unencrypted_confidential(self):
        create_note(
            self.fixture.root, "Note - Unenc.md",
            frontmatter={"title": "Unencrypted", "type": "Note", "classification": "confidential"},
            body="# Sensitive info here",
        )
        results = audit_vault(self.fixture.root)
        self.assertEqual(len(results["unencrypted_classified"]), 1)
        self.assertEqual(results["unencrypted_classified"][0]["classification"], "confidential")

    def test_detects_correctly_encrypted(self):
        path = self.fixture.root / "Note - Enc.md"
        content = (
            "---\ntitle: Encrypted\ntype: Note\nclassification: confidential\n"
            "encrypted: true\nencryption_method: age\nencryption_recipients: 2\n---\n"
            f"{AGE_BEGIN}\ndata\n{AGE_END}\n"
        )
        path.write_text(content)
        results = audit_vault(self.fixture.root)
        self.assertEqual(len(results["encrypted_correct"]), 1)

    def test_ignores_public_unencrypted(self):
        create_note(
            self.fixture.root, "Note - Public.md",
            frontmatter={"title": "Public", "type": "Note", "classification": "public"},
            body="# Public info",
        )
        results = audit_vault(self.fixture.root)
        self.assertEqual(len(results["unencrypted_classified"]), 0)
        self.assertEqual(len(results["encrypted_correct"]), 0)

    def test_detects_unencrypted_secret(self):
        create_note(
            self.fixture.root, "Note - Secret.md",
            frontmatter={"title": "Top Secret", "type": "Note", "classification": "secret"},
            body="# Super secret",
        )
        results = audit_vault(self.fixture.root)
        self.assertEqual(len(results["unencrypted_classified"]), 1)
        self.assertEqual(results["unencrypted_classified"][0]["classification"], "secret")

    def test_skips_hidden_dirs(self):
        hidden_dir = self.fixture.root / ".claude"
        hidden_dir.mkdir()
        create_note(
            hidden_dir, "config.md",
            frontmatter={"title": "Config", "classification": "confidential"},
            body="# Config",
        )
        results = audit_vault(self.fixture.root)
        self.assertEqual(len(results["unencrypted_classified"]), 0)


class TestEncryptedOutputFormat(unittest.TestCase):
    """Test the split-format output spec."""

    @unittest.skipUnless(HAS_AGE, "age CLI not installed")
    def test_output_matches_spec(self):
        """Encrypted file matches the documented split format."""
        tmpdir = tempfile.mkdtemp()
        try:
            # Generate key
            result = subprocess.run(["age-keygen"], capture_output=True, text=True)
            key_path = os.path.join(tmpdir, "key.txt")
            with open(key_path, "w") as f:
                f.write(result.stdout)
            for line in result.stderr.split("\n"):
                if line.startswith("Public key:"):
                    pub_key = line.split(": ")[1].strip()
                    break

            # Create and encrypt note
            note_path = os.path.join(tmpdir, "Note - Test.md")
            Path(note_path).write_text(
                "---\ntitle: Format Test\ntype: Note\nclassification: confidential\n---\n"
                "# Secret body\n\nWith content.\n"
            )
            encrypt_file(note_path, [pub_key])

            content = Path(note_path).read_text()
            lines = content.split("\n")

            # First line must be ---
            self.assertEqual(lines[0], "---")

            # Must have closing --- before encrypted content
            found_close = False
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---" and not found_close:
                    found_close = True
                    close_idx = i
                    break
            self.assertTrue(found_close, "Missing closing --- delimiter")

            # After closing ---, must have age header
            after_fm = "\n".join(lines[close_idx + 1:])
            self.assertIn(AGE_BEGIN, after_fm)
            self.assertIn(AGE_END, after_fm)

            # Frontmatter must contain encryption fields
            fm_section = "\n".join(lines[:close_idx + 1])
            self.assertIn("encrypted: true", fm_section)
            self.assertIn("encryption_method: age", fm_section)
            self.assertIn("encryption_recipients: 1", fm_section)

            # Frontmatter must NOT contain body content
            self.assertNotIn("Secret body", fm_section)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
