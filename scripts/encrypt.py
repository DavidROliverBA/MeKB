#!/usr/bin/env python3
"""
Encryption/Decryption Script for MeKB
Encrypt and decrypt note bodies using age, preserving plaintext frontmatter.

Usage:
    python3 scripts/encrypt.py encrypt <file> [--recipients KEY...]
    python3 scripts/encrypt.py decrypt <file> [--identity PATH]
    python3 scripts/encrypt.py status <file>
    python3 scripts/encrypt.py audit [--vault PATH]

File format (split):
    Plaintext YAML frontmatter (always readable) + age-encrypted body.
    Frontmatter gains: encrypted: true, encryption_method: age, encryption_recipients: N

Dependencies: Python 3.9+ (stdlib only), age CLI (brew install age)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Frontmatter regex: captures YAML between --- markers
FM_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# age ASCII armour markers
AGE_BEGIN = "-----BEGIN AGE ENCRYPTED FILE-----"
AGE_END = "-----END AGE ENCRYPTED FILE-----"


def find_vault_root(start=None):
    """Find the vault root by looking for .mekb/ or CLAUDE.md."""
    path = Path(start) if start else Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def load_config(vault_root):
    """Load encryption config from .mekb/security.json."""
    config_path = vault_root / ".mekb" / "security.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path) as f:
            return json.load(f).get("encryption", {})
    except (json.JSONDecodeError, IOError):
        return {}


def check_age_installed():
    """Check if age CLI is available."""
    return shutil.which("age") is not None


def split_frontmatter(content):
    """Split markdown content into YAML frontmatter and body.

    Returns:
        tuple: (frontmatter_text, body_text, has_frontmatter)
            - frontmatter_text includes the --- delimiters
            - body_text is everything after the closing ---
            - has_frontmatter is True if frontmatter was found
    """
    match = FM_PATTERN.match(content)
    if not match:
        return "", content, False

    # Include the full frontmatter block with delimiters
    frontmatter_end = match.end()
    frontmatter_text = content[:frontmatter_end]
    body_text = content[frontmatter_end:]

    return frontmatter_text, body_text, True


def parse_frontmatter_fields(frontmatter_text):
    """Extract key fields from frontmatter text (simple YAML parsing)."""
    match = FM_PATTERN.match(frontmatter_text)
    if not match:
        return {}

    yaml_text = match.group(1)
    fields = {}

    for field in ("encrypted", "encryption_method", "encryption_recipients",
                  "classification", "title", "type"):
        line_match = re.search(rf"^{field}\s*:\s*(.+)$", yaml_text, re.MULTILINE)
        if line_match:
            value = line_match.group(1).strip()
            if value in ("true", "True"):
                value = True
            elif value in ("false", "False"):
                value = False
            elif value in ("null", "~", ""):
                value = None
            elif value.isdigit():
                value = int(value)
            else:
                # Strip quotes
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
            fields[field] = value

    return fields


def add_encryption_fields(frontmatter_text, recipient_count=1):
    """Add encryption metadata fields to frontmatter.

    Inserts encrypted: true, encryption_method: age, and
    encryption_recipients: N before the closing --- delimiter.

    Args:
        frontmatter_text: The full frontmatter block including --- delimiters.
        recipient_count: Number of encryption recipients.

    Returns:
        Updated frontmatter text with encryption fields.
    """
    if not frontmatter_text.strip():
        return frontmatter_text

    # Check if encryption fields already exist
    fields = parse_frontmatter_fields(frontmatter_text)
    if fields.get("encrypted") is True:
        # Update recipient count if changed
        frontmatter_text = re.sub(
            r"^encryption_recipients\s*:\s*\d+",
            f"encryption_recipients: {recipient_count}",
            frontmatter_text,
            flags=re.MULTILINE,
        )
        return frontmatter_text

    # Find the closing --- and insert before it
    lines = frontmatter_text.rstrip("\n").split("\n")

    # Find the last --- line
    close_idx = None
    for i in range(len(lines) - 1, 0, -1):
        if lines[i].strip() == "---":
            close_idx = i
            break

    if close_idx is None:
        return frontmatter_text

    # Insert encryption fields before closing ---
    encryption_lines = [
        "encrypted: true",
        "encryption_method: age",
        f"encryption_recipients: {recipient_count}",
    ]

    lines = lines[:close_idx] + encryption_lines + lines[close_idx:]
    return "\n".join(lines) + "\n"


def remove_encryption_fields(frontmatter_text):
    """Remove encryption metadata fields from frontmatter.

    Removes encrypted, encryption_method, and encryption_recipients lines.

    Args:
        frontmatter_text: The full frontmatter block including --- delimiters.

    Returns:
        Updated frontmatter text without encryption fields.
    """
    lines = frontmatter_text.split("\n")
    filtered = [
        line for line in lines
        if not re.match(r"^(encrypted|encryption_method|encryption_recipients)\s*:", line)
    ]
    return "\n".join(filtered)


def reassemble(frontmatter_text, body_text):
    """Reassemble frontmatter and body into a complete markdown file.

    Args:
        frontmatter_text: YAML frontmatter block (with --- delimiters).
        body_text: Markdown body (may be encrypted).

    Returns:
        Complete file content.
    """
    return frontmatter_text + body_text


def is_encrypted(content):
    """Check if file content contains an age-encrypted body."""
    return AGE_BEGIN in content


def encrypt_body(body, recipients):
    """Encrypt markdown body text using age.

    Args:
        body: Plaintext markdown body.
        recipients: List of age recipient public keys.

    Returns:
        ASCII-armoured age ciphertext.

    Raises:
        RuntimeError: If age encryption fails.
    """
    if not recipients:
        raise ValueError("At least one recipient key is required")

    if not check_age_installed():
        raise RuntimeError(
            "age is not installed. Install with: brew install age"
        )

    cmd = ["age", "--armor"]
    for r in recipients:
        cmd.extend(["-r", r])

    result = subprocess.run(
        cmd,
        input=body.encode("utf-8"),
        capture_output=True,
    )

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"age encryption failed: {stderr}")

    return result.stdout.decode("utf-8")


def decrypt_body(encrypted_body, identity_path):
    """Decrypt age-encrypted body text.

    Args:
        encrypted_body: ASCII-armoured age ciphertext.
        identity_path: Path to age identity file (private key).

    Returns:
        Decrypted plaintext.

    Raises:
        RuntimeError: If age decryption fails.
    """
    if not check_age_installed():
        raise RuntimeError(
            "age is not installed. Install with: brew install age"
        )

    identity = Path(identity_path).expanduser()
    if not identity.exists():
        raise FileNotFoundError(f"Identity file not found: {identity}")

    cmd = ["age", "-d", "-i", str(identity)]

    result = subprocess.run(
        cmd,
        input=encrypted_body.encode("utf-8"),
        capture_output=True,
    )

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"age decryption failed: {stderr}")

    return result.stdout.decode("utf-8")


def encrypt_file(file_path, recipients, dry_run=False):
    """Encrypt a markdown file in-place using split format.

    Preserves plaintext frontmatter, encrypts the body.

    Args:
        file_path: Path to the markdown file.
        recipients: List of age recipient public keys.
        dry_run: If True, print what would happen without modifying files.

    Returns:
        True if file was encrypted, False if already encrypted or skipped.
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    frontmatter_text, body_text, has_fm = split_frontmatter(content)

    # Already encrypted?
    if is_encrypted(content):
        return False

    # Nothing to encrypt?
    if not body_text.strip():
        return False

    if dry_run:
        print(f"Would encrypt: {path}")
        return True

    # Encrypt the body
    encrypted_body = encrypt_body(body_text, recipients)

    # Add encryption fields to frontmatter
    if has_fm:
        frontmatter_text = add_encryption_fields(frontmatter_text, len(recipients))
    else:
        # Create minimal frontmatter if none exists
        frontmatter_text = (
            "---\n"
            "encrypted: true\n"
            "encryption_method: age\n"
            f"encryption_recipients: {len(recipients)}\n"
            "---\n"
        )

    # Write back
    result = reassemble(frontmatter_text, encrypted_body)
    path.write_text(result, encoding="utf-8")
    return True


def decrypt_file(file_path, identity_path, dry_run=False):
    """Decrypt a markdown file in-place.

    Preserves frontmatter, decrypts the body, removes encryption fields.

    Args:
        file_path: Path to the encrypted markdown file.
        identity_path: Path to age identity file.
        dry_run: If True, print what would happen without modifying files.

    Returns:
        True if file was decrypted, False if not encrypted.
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    if not is_encrypted(content):
        return False

    frontmatter_text, encrypted_body, has_fm = split_frontmatter(content)

    if dry_run:
        print(f"Would decrypt: {path}")
        return True

    # Decrypt the body
    plaintext_body = decrypt_body(encrypted_body, identity_path)

    # Remove encryption fields from frontmatter
    if has_fm:
        frontmatter_text = remove_encryption_fields(frontmatter_text)

    # Write back
    result = reassemble(frontmatter_text, plaintext_body)
    path.write_text(result, encoding="utf-8")
    return True


def file_status(file_path):
    """Check encryption status of a file.

    Returns:
        dict with keys: path, encrypted, classification, encryption_method
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    frontmatter_text, body_text, has_fm = split_frontmatter(content)
    fields = parse_frontmatter_fields(frontmatter_text) if has_fm else {}

    return {
        "path": str(path),
        "encrypted": is_encrypted(content),
        "classification": fields.get("classification", "personal"),
        "encryption_method": fields.get("encryption_method"),
        "encryption_recipients": fields.get("encryption_recipients", 0),
        "has_frontmatter": has_fm,
        "title": fields.get("title", path.stem),
    }


def audit_vault(vault_root):
    """Audit encryption status of all classified files.

    Returns:
        dict with summary and lists of files needing attention.
    """
    vault = Path(vault_root)
    results = {
        "encrypted_correct": [],      # encrypted + classified
        "unencrypted_classified": [],  # classified but NOT encrypted
        "encrypted_unclassified": [],  # encrypted but NOT classified
        "total_checked": 0,
    }

    levels_to_encrypt = {"confidential", "secret"}

    for md_file in vault.rglob("*.md"):
        # Skip hidden dirs and templates
        rel = md_file.relative_to(vault)
        parts = rel.parts
        if any(p.startswith(".") for p in parts[:-1]):
            continue
        if "Templates" in parts or "Archive" in parts:
            continue

        try:
            status = file_status(md_file)
        except (IOError, OSError):
            continue

        results["total_checked"] += 1
        cls = status["classification"]

        if cls in levels_to_encrypt and status["encrypted"]:
            results["encrypted_correct"].append(status)
        elif cls in levels_to_encrypt and not status["encrypted"]:
            results["unencrypted_classified"].append(status)
        elif cls not in levels_to_encrypt and status["encrypted"]:
            results["encrypted_unclassified"].append(status)

    return results


def format_audit(results):
    """Format audit results for display."""
    lines = []
    lines.append(f"Encryption Audit ({results['total_checked']} files checked)")
    lines.append("=" * 50)

    correct = results["encrypted_correct"]
    unenc = results["unencrypted_classified"]
    extra = results["encrypted_unclassified"]

    if correct:
        lines.append(f"\n  Correctly encrypted: {len(correct)}")
        for s in correct:
            lines.append(f"    {s['path']} ({s['classification']})")

    if unenc:
        lines.append(f"\n  MISSING encryption ({len(unenc)} files):")
        for s in unenc:
            lines.append(f"    {s['path']} ({s['classification']}) - NOT ENCRYPTED")
    else:
        lines.append("\n  No missing encryption.")

    if extra:
        lines.append(f"\n  Encrypted but not classified ({len(extra)} files):")
        for s in extra:
            lines.append(f"    {s['path']} ({s['classification']})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="MeKB note encryption")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # encrypt
    enc = subparsers.add_parser("encrypt", help="Encrypt a note")
    enc.add_argument("file", help="Path to markdown file")
    enc.add_argument("--recipient", "-r", action="append", dest="recipients",
                     help="age recipient public key (repeatable)")
    enc.add_argument("--dry-run", action="store_true", help="Show what would happen")

    # decrypt
    dec = subparsers.add_parser("decrypt", help="Decrypt a note")
    dec.add_argument("file", help="Path to encrypted markdown file")
    dec.add_argument("--identity", "-i", help="Path to age identity file")
    dec.add_argument("--dry-run", action="store_true", help="Show what would happen")

    # status
    st = subparsers.add_parser("status", help="Check encryption status")
    st.add_argument("file", help="Path to markdown file")

    # audit
    au = subparsers.add_parser("audit", help="Audit vault encryption")
    au.add_argument("--vault", help="Vault root directory")
    au.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "encrypt":
        vault_root = find_vault_root()
        config = load_config(vault_root)

        recipients = args.recipients or config.get("recipients", [])
        if not recipients:
            print("Error: No recipients specified. Use -r KEY or configure in .mekb/security.json",
                  file=sys.stderr)
            sys.exit(1)

        if not check_age_installed():
            print("Error: age is not installed. Install with: brew install age",
                  file=sys.stderr)
            sys.exit(1)

        encrypted = encrypt_file(args.file, recipients, dry_run=args.dry_run)
        if encrypted:
            action = "Would encrypt" if args.dry_run else "Encrypted"
            print(f"{action}: {args.file}")
        else:
            print(f"Skipped (already encrypted or empty body): {args.file}")

    elif args.command == "decrypt":
        vault_root = find_vault_root()
        config = load_config(vault_root)

        identity = args.identity or config.get("se_identity") or config.get("backup_identity")
        if not identity:
            print("Error: No identity file specified. Use -i PATH or configure in .mekb/security.json",
                  file=sys.stderr)
            sys.exit(1)

        if not check_age_installed():
            print("Error: age is not installed. Install with: brew install age",
                  file=sys.stderr)
            sys.exit(1)

        decrypted = decrypt_file(args.file, identity, dry_run=args.dry_run)
        if decrypted:
            action = "Would decrypt" if args.dry_run else "Decrypted"
            print(f"{action}: {args.file}")
        else:
            print(f"Skipped (not encrypted): {args.file}")

    elif args.command == "status":
        status = file_status(args.file)
        if status["encrypted"]:
            print(f"ENCRYPTED ({status['encryption_method']}, "
                  f"{status['encryption_recipients']} recipients)")
        else:
            print(f"PLAINTEXT (classification: {status['classification']})")

    elif args.command == "audit":
        vault_root = Path(args.vault) if args.vault else find_vault_root()
        results = audit_vault(vault_root)

        if args.json:
            # Simplify for JSON output
            output = {
                "total_checked": results["total_checked"],
                "encrypted_correct": len(results["encrypted_correct"]),
                "unencrypted_classified": [
                    {"path": s["path"], "classification": s["classification"]}
                    for s in results["unencrypted_classified"]
                ],
                "encrypted_unclassified": [
                    {"path": s["path"], "classification": s["classification"]}
                    for s in results["encrypted_unclassified"]
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_audit(results))


if __name__ == "__main__":
    main()
