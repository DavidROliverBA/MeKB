# MeKB Encryption Guide

Per-note encryption for confidential and secret notes using [age](https://age-encryption.org/).

**Version:** 1.0
**Requires:** age 1.1+, Python 3.9+

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Day-to-Day Usage](#day-to-day-usage)
4. [How It Works](#how-it-works)
5. [Key Management](#key-management)
6. [Recovery Procedures](#recovery-procedures)
7. [Threat Model](#threat-model)
8. [Cross-Platform Notes](#cross-platform-notes)
9. [Troubleshooting](#troubleshooting)
10. [Uninstall / Upgrade to a Different Mechanism](#uninstall--upgrade-to-a-different-mechanism)

---

## Overview

MeKB encryption protects notes classified as `confidential` or `secret` by encrypting the markdown body while keeping the YAML frontmatter in plaintext. This means:

- **Search still works** - titles, tags, and metadata are indexed
- **Classification guard still works** - it reads the plaintext frontmatter
- **Git diffs are meaningful** - metadata changes show as text diffs
- **The body is unreadable** - without the decryption key, the content is ciphertext

### Design Principles

| Principle | How Encryption Respects It |
|-----------|---------------------------|
| Knowledge outlives tools | Encrypted files are standard age ciphertext. Any tool with age can decrypt them |
| Zero hard dependencies | age is an optional install. Without it, unencrypted notes work fine |
| Tool-agnostic | Works from terminal, VS Code, Obsidian, or any editor + age CLI |
| Git-friendly | ASCII-armoured ciphertext commits cleanly to git |
| Offline-first | No network required for encryption or decryption |

---

## Installation

### Prerequisites

- Python 3.9+ (for `scripts/encrypt.py`)
- A terminal (macOS, Linux, or WSL on Windows)

### Step 1: Install age

**macOS (Homebrew):**

```bash
brew install age
```

**Linux (package manager):**

```bash
# Debian/Ubuntu
sudo apt install age

# Arch
sudo pacman -S age

# Or download binary from GitHub
# https://github.com/FiloSottile/age/releases
```

**Windows (Scoop or Chocolatey):**

```bash
scoop install age
# or
choco install age.portable
```

Verify installation:

```bash
age --version
# age v1.3.1 (or later)
```

### Step 2: Run Security Setup

The setup wizard handles key generation and configuration:

```bash
./scripts/setup-security.sh
```

When prompted "Set up encryption?", answer `y`. This will:

1. Check that age is installed
2. Generate a **primary key** at `.mekb/age-key.txt`
3. Generate a **backup key** at `.mekb/backup-key.txt`
4. Save both public keys as recipients in `.mekb/security.json`
5. Add key files to `.gitignore`

### Step 3: Back Up Your Keys

**This is critical.** Store `.mekb/backup-key.txt` in your password manager (Bitwarden, 1Password, etc.). If you lose both keys, encrypted notes cannot be recovered.

### Step 4: Verify

```bash
python3 scripts/encrypt.py audit
```

This should show 0 encrypted files and 0 mismatches.

### Manual Setup (Without Wizard)

If you prefer to set up manually:

```bash
# Generate keys
age-keygen -o .mekb/age-key.txt 2>/tmp/key1.txt
age-keygen -o .mekb/backup-key.txt 2>/tmp/key2.txt

# Note the public keys from the output
PRIMARY_PUB=$(grep "public key:" /tmp/key1.txt | awk '{print $NF}')
BACKUP_PUB=$(grep "public key:" /tmp/key2.txt | awk '{print $NF}')

# Add to .gitignore
echo ".mekb/age-key.txt" >> .gitignore
echo ".mekb/backup-key.txt" >> .gitignore

# Update security.json encryption section
# Set recipients to [$PRIMARY_PUB, $BACKUP_PUB]
# Set enabled to true
```

---

## Day-to-Day Usage

### Encrypt a Note

```bash
# CLI
python3 scripts/encrypt.py encrypt "Note - Client Credentials.md"

# With Claude Code
/encrypt "Note - Client Credentials.md"
```

### Decrypt a Note

```bash
# CLI (uses primary key from config)
python3 scripts/encrypt.py decrypt "Note - Client Credentials.md" \
  --identity .mekb/age-key.txt

# With Claude Code
/decrypt "Note - Client Credentials.md"
```

### Classify and Auto-Encrypt

When encryption is enabled with `encrypt_on_classify: true` (the default):

```
/classify set "Note - Client Info.md" confidential
```

This sets the classification AND encrypts the note in one step.

Lowering classification auto-decrypts:

```
/classify set "Note - Client Info.md" personal
```

### Check Status

```bash
# Single file
python3 scripts/encrypt.py status "Note - Client Credentials.md"
# → ENCRYPTED (age, 2 recipients)

# Vault-wide audit
python3 scripts/encrypt.py audit
```

### Search Encrypted Notes

Encrypted notes appear in search results with an `[ENCRYPTED]` indicator. Their titles, tags, and metadata are searchable, but body content is not (by design).

```bash
python3 scripts/search.py "credentials"
#   1. [Note] Client Credentials [ENCRYPTED]
#      Note - Client Credentials.md
```

### Edit an Encrypted Note

1. Decrypt: `/decrypt "Note - Client Credentials.md"`
2. Edit the file in any editor
3. Re-encrypt: `/encrypt "Note - Client Credentials.md"`

Or in a single flow with Claude Code:

```
/decrypt "Note - Client Credentials.md"
# ... make your changes ...
/encrypt "Note - Client Credentials.md"
```

### Git Workflow

Encrypted notes commit normally. The frontmatter is readable in diffs, the body shows as changed ciphertext:

```bash
git add "Note - Client Credentials.md"
git commit -m "Update client credentials"
git push
```

The encrypted body will appear as base64 text in the git diff. This is expected.

---

## How It Works

### Split-Format Files

An encrypted file has two sections:

```
┌─────────────────────────────────┐
│ --- (YAML frontmatter)          │  ← Plaintext (always readable)
│ title: Client Credentials       │
│ classification: secret          │
│ encrypted: true                 │
│ encryption_method: age          │
│ encryption_recipients: 2        │
│ ---                             │
├─────────────────────────────────┤
│ -----BEGIN AGE ENCRYPTED FILE-- │  ← Ciphertext (needs key to read)
│ YWdlLWVuY3J5cHRpb24ub3JnL3Yx.. │
│ -----END AGE ENCRYPTED FILE---- │
└─────────────────────────────────┘
```

### Encryption Flow

```
1. Read file
2. Split: frontmatter | body
3. Encrypt body: echo "$body" | age --armor -r $KEY1 -r $KEY2
4. Add encryption fields to frontmatter
5. Write: frontmatter + encrypted body
```

### Decryption Flow

```
1. Read file
2. Split: frontmatter | encrypted body
3. Decrypt body: echo "$encrypted" | age -d -i identity.txt
4. Remove encryption fields from frontmatter
5. Write: frontmatter + plaintext body
```

### What age Provides

- **X25519** key agreement (Curve25519)
- **ChaCha20-Poly1305** authenticated encryption
- **scrypt** for passphrase-based keys
- **ASCII armour** output (text-safe, git-friendly)
- **Multi-recipient** encryption (one file, multiple keys can decrypt)

---

## Key Management

### Key Files

| File | Contains | Purpose |
|------|----------|---------|
| `.mekb/age-key.txt` | Private key (AGE-SECRET-KEY-...) + public key comment | Day-to-day decryption |
| `.mekb/backup-key.txt` | Private key (AGE-SECRET-KEY-...) + public key comment | Recovery if primary lost |

Both files are gitignored. They never leave your machine via git.

### Recipients

Every encrypted file is encrypted to **both** public keys. Either private key can decrypt. This means:

- **Normal use:** decrypt with `.mekb/age-key.txt`
- **Recovery:** decrypt with `.mekb/backup-key.txt` (from password manager)

### Adding a New Recipient

To add a third key (e.g. a YubiKey or new device):

1. Generate or obtain the new public key
2. Add it to `recipients` array in `.mekb/security.json`
3. Re-encrypt all encrypted files:

```bash
# Decrypt all
for f in $(grep -rl "encrypted: true" --include="*.md" .); do
  python3 scripts/encrypt.py decrypt "$f" --identity .mekb/age-key.txt
done

# Re-encrypt with new recipient list
for f in $(grep -rl "classification: confidential\|classification: secret" --include="*.md" .); do
  python3 scripts/encrypt.py encrypt "$f"
done
```

### Revoking a Key

Since age has no revocation mechanism, to revoke a compromised key:

1. Generate a new key pair
2. Decrypt all files with any remaining valid key
3. Remove the old public key from `recipients` in config
4. Re-encrypt all files with the new recipient list

---

## Recovery Procedures

### Scenario: Primary Key Lost (Device Replacement)

1. Clone your vault on the new device
2. Retrieve `.mekb/backup-key.txt` from your password manager
3. Place it at `.mekb/backup-key.txt` in the vault
4. Decrypt files: `python3 scripts/encrypt.py decrypt <file> --identity .mekb/backup-key.txt`
5. Generate a new primary key: `age-keygen -o .mekb/age-key.txt`
6. Update the public key in `.mekb/security.json` recipients
7. Re-encrypt all classified files

### Scenario: Both Keys Lost

**Encrypted content is unrecoverable.** This is by design. The frontmatter (title, tags, classification, dates) is still readable, so you know what was lost.

Prevention:
- Store backup key in a password manager
- Store backup key on a separate device or printed on paper
- Consider a third recipient key on a hardware security key (YubiKey)

### Scenario: Encrypted File Corrupted

If the age ciphertext is corrupted (truncated, modified), decryption will fail with an error. Git history may contain a valid earlier version:

```bash
git log --oneline "Note - Client Credentials.md"
git show <commit>:"Note - Client Credentials.md" > /tmp/recovered.md
python3 scripts/encrypt.py decrypt /tmp/recovered.md --identity .mekb/age-key.txt
```

---

## Threat Model

| Threat | Protected? | Notes |
|--------|-----------|-------|
| Laptop stolen while locked | Yes | Files encrypted at rest |
| Cloud sync provider breach | Yes | Only ciphertext in sync |
| Git hosting compromise | Yes | Ciphertext in git, frontmatter is metadata only |
| AI assistant data exfiltration | Yes | Classification guard + encryption = defence in depth |
| Malicious Obsidian plugin | Partial | Can't read encrypted body unless you've decrypted it |
| Shoulder surfing | No | Content visible when decrypted |
| Lost encryption key | Mitigated | Multi-recipient (primary + backup) |
| Search index theft | Partial | Index stores `[ENCRYPTED]` placeholder, not plaintext body |
| Compromised OS / keylogger | No | Out of scope (game over regardless) |

---

## Cross-Platform Notes

### macOS

Full support. Install via `brew install age`. Optional Touch ID integration available with `age-plugin-se` (Secure Enclave plugin):

```bash
brew install age-plugin-se
age-plugin-se keygen --access-control any-biometry-or-passcode
```

### Linux

Full support. Install via package manager or download binary. Uses passphrase-based keys or standard age identity files.

### Windows

Works via WSL (Windows Subsystem for Linux) or native age binary. Install via `scoop install age` or `choco install age.portable`.

### iOS / Android

Limited. age does not have mature mobile implementations. Encrypted notes will appear with ciphertext body in mobile Obsidian. Options:
- View frontmatter (title, tags) on mobile, full content on desktop
- Use a mobile-compatible age client if one becomes available

### Syncing

Encrypted files sync normally via any mechanism (git, iCloud, Dropbox, Syncthing). The ciphertext is just text in a `.md` file.

---

## Troubleshooting

### "age is not installed"

```bash
brew install age    # macOS
sudo apt install age  # Ubuntu/Debian
```

### "No recipients specified"

Run `/encrypt setup` or check `.mekb/security.json` has a non-empty `recipients` array.

### "Identity file not found"

Check that `.mekb/age-key.txt` exists. If lost, use backup key:

```bash
python3 scripts/encrypt.py decrypt <file> --identity .mekb/backup-key.txt
```

### "age decryption failed"

Possible causes:
- Wrong identity file (key doesn't match the recipients used to encrypt)
- Corrupted ciphertext (check git history for a valid version)
- File is not actually encrypted (check with `/encrypt status <file>`)

### "File already encrypted" (skipped)

The file already contains an age-encrypted body. No action needed.

### Search returns no body content for encrypted notes

By design. Encrypted notes are indexed as metadata only. The search index stores `[ENCRYPTED]` instead of the body to prevent plaintext leakage.

### Obsidian shows raw ciphertext

Expected behaviour. When a note is encrypted, Obsidian renders the frontmatter normally but shows the age ASCII armour block as the body. Decrypt the note to view/edit content.

---

## Uninstall / Upgrade to a Different Mechanism

### Step 1: Decrypt All Notes

Before removing encryption or switching tools, decrypt every encrypted note:

```bash
# Find all encrypted notes
grep -rl "encrypted: true" --include="*.md" .

# Decrypt each one
for f in $(grep -rl "encrypted: true" --include="*.md" .); do
  python3 scripts/encrypt.py decrypt "$f" --identity .mekb/age-key.txt
  echo "Decrypted: $f"
done
```

Verify no encrypted notes remain:

```bash
python3 scripts/encrypt.py audit
# Should show: 0 encrypted files
```

### Step 2: Remove Encryption Configuration

Edit `.mekb/security.json` and either:

**Option A: Disable encryption (keep config for later)**

```json
{
  "encryption": {
    "enabled": false
  }
}
```

**Option B: Remove encryption section entirely**

Delete the `"encryption": { ... }` block from `.mekb/security.json`.

### Step 3: Remove Key Files

```bash
rm .mekb/age-key.txt
rm .mekb/backup-key.txt
```

### Step 4: Remove Encryption Fields from Notes

If any notes still have `encrypted: false` or leftover fields:

```bash
# Check for any remaining encryption frontmatter
grep -rl "encryption_method:" --include="*.md" .
```

These fields are harmless but can be removed manually if desired.

### Step 5: Uninstall age (Optional)

```bash
brew uninstall age    # macOS
sudo apt remove age   # Ubuntu/Debian
```

### Step 6: Clean Up .gitignore

Remove these lines from `.gitignore`:

```
.mekb/age-key.txt
.mekb/backup-key.txt
```

### Step 7: Commit the Decrypted State

```bash
git add -A
git commit -m "Remove encryption: all notes decrypted for migration"
```

### Upgrading to a Different Encryption Mechanism

If you want to switch to a different tool (e.g. git-crypt, SOPS, Vault):

1. Complete Steps 1-7 above (decrypt everything, remove age)
2. Set up the new encryption tool following its documentation
3. The notes are now plaintext markdown - any encryption tool can wrap them
4. Update `.mekb/security.json` if the new tool integrates with MeKB
5. Update `scripts/encrypt.py` or replace it with the new tool's wrapper

**Key principle:** Your notes are always plain markdown when decrypted. The encryption layer is a wrapper, not a format. Switching tools means: decrypt with old tool, encrypt with new tool.

---

## Configuration Reference

`.mekb/security.json` encryption section:

```json
{
  "encryption": {
    "enabled": true,
    "tool": "age",
    "levels_to_encrypt": ["secret", "confidential"],
    "format": "split",
    "recipients": [
      "age1...",
      "age1..."
    ],
    "primary_identity": ".mekb/age-key.txt",
    "backup_identity": ".mekb/backup-key.txt",
    "session_timeout_minutes": 30,
    "index_encrypted_body": false,
    "encrypt_on_classify": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Master switch for encryption features |
| `tool` | string | Encryption tool (`age`) |
| `levels_to_encrypt` | array | Classification levels that trigger encryption |
| `format` | string | File format (`split` = plaintext frontmatter + encrypted body) |
| `recipients` | array | age public keys to encrypt to |
| `primary_identity` | string | Path to primary decryption key |
| `backup_identity` | string | Path to backup decryption key |
| `session_timeout_minutes` | number | Auto-relock timeout (future feature) |
| `index_encrypted_body` | boolean | Whether to decrypt body for search indexing |
| `encrypt_on_classify` | boolean | Auto-encrypt when classification raised |

---

## Script Reference

```bash
# Encrypt
python3 scripts/encrypt.py encrypt <file> [-r RECIPIENT...]
python3 scripts/encrypt.py encrypt <file> --dry-run

# Decrypt
python3 scripts/encrypt.py decrypt <file> [-i IDENTITY]
python3 scripts/encrypt.py decrypt <file> --dry-run

# Status
python3 scripts/encrypt.py status <file>

# Audit
python3 scripts/encrypt.py audit [--vault PATH] [--json]
```
