# Security Guide

MeKB includes built-in security features to protect sensitive information. All features are optional - enable what you need.

## Quick Setup

```bash
./scripts/setup-security.sh
```

This enables:

- Secret detection (pre-commit hook)
- AI access control
- Classified folders

## Classification Levels

Add to any note's frontmatter:

```yaml
classification: confidential
```

| Level          | AI Access  | Use For                             |
| -------------- | ---------- | ----------------------------------- |
| `public`       | Allowed    | Blog drafts, public notes           |
| `personal`     | Allowed    | Private but not sensitive (default) |
| `confidential` | Asks first | Work secrets, client info           |
| `secret`       | Blocked    | Passwords, keys, highly sensitive   |

Default (no field) = `personal`.

## AI Access Control

MeKB protects classified files from AI assistants:

**Interactive Mode** (default):

- `public`/`personal`: AI can access freely
- `confidential`: AI asks permission before accessing
- `secret`: AI access always blocked

**Strict Mode**:

- `confidential` and `secret` files are always blocked

Configure in `.mekb/security.json`:

```json
{
  "ai_access_control": {
    "mode": "interactive",
    "levels": {
      "confidential": "ask",
      "secret": "block"
    }
  }
}
```

## Trusted AI Providers

Different trust levels for different AI setups:

| Provider     | Trust Level        | Notes                     |
| ------------ | ------------------ | ------------------------- |
| **Bedrock**  | Up to confidential | Zero data retention       |
| **Local**    | Up to secret       | Data never leaves machine |
| **API**      | Up to personal     | 30-day retention          |
| **Consumer** | Up to personal     | May train on data         |

## Folder Inheritance

Files in classified folders auto-inherit classification:

```
confidential/   → classification: confidential
secret/         → classification: secret
private/        → classification: confidential
```

The `secret/` folder is gitignored - never committed.

## Secret Detection

Pre-commit hook blocks commits containing:

- API keys (AWS, GitHub, OpenAI, etc.)
- Passwords and tokens
- Private keys
- Connection strings

```bash
# Install hook
pre-commit install

# Test detection
python scripts/detect-secrets.py --directory .
```

## /classify Skill

Manage classifications with Claude Code:

```
/classify              # Summary of all classifications
/classify check        # Find files needing classification
/classify list secret  # List all secret files
/classify audit        # Full security audit
/classify set FILE confidential
```

## Never Store

- Passwords, API keys, tokens
- Full credit card numbers
- Government ID numbers
- Unencrypted sensitive data

Use a password manager instead.

## Built-in Encryption

MeKB has built-in per-note encryption using [age](https://age-encryption.org/) (actually good encryption). Notes classified as `confidential` or `secret` can be encrypted at rest with a single command.

**How it works:** Split-format encryption preserves plaintext YAML frontmatter (so search, Dataview, and classification still work) while encrypting the markdown body with age.

### Quick Start

```bash
# 1. Set up encryption (part of security setup)
./scripts/setup-security.sh

# 2. Encrypt a note
python3 scripts/encrypt.py encrypt "Note - Client Credentials.md"

# 3. Decrypt a note
python3 scripts/encrypt.py decrypt "Note - Client Credentials.md" --identity .mekb/age-key.txt

# 4. Audit encryption status
python3 scripts/encrypt.py audit
```

Or with Claude Code:

```
/encrypt "Note - Client Credentials.md"
/decrypt "Note - Client Credentials.md"
/encrypt audit
```

### Key Management

| File | Purpose | Location |
|------|---------|----------|
| `.mekb/age-key.txt` | Primary decryption key | gitignored, local only |
| `.mekb/backup-key.txt` | Backup key for recovery | gitignored, store in password manager |

Both keys are generated during setup and added to `.gitignore` automatically.

### Integration with Classification

When `encrypt_on_classify` is enabled (default):
- `/classify set <file> confidential` auto-encrypts the note
- `/classify set <file> personal` auto-decrypts the note
- `/classify audit` reports encryption mismatches

### What Gets Encrypted

Only the markdown **body** is encrypted. Frontmatter stays plaintext:

```yaml
---
title: Client Credentials          # Plaintext (searchable)
classification: secret             # Plaintext (classification guard works)
encrypted: true                    # Indicates body is encrypted
encryption_method: age
encryption_recipients: 2
---
-----BEGIN AGE ENCRYPTED FILE-----   # Body is ciphertext
YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+...
-----END AGE ENCRYPTED FILE-----
```

### Recovery

If your primary key is lost:

1. Retrieve backup key from your password manager
2. Decrypt: `python3 scripts/encrypt.py decrypt <file> --identity .mekb/backup-key.txt`
3. Generate new primary key: `age-keygen -o .mekb/age-key.txt`
4. Re-encrypt all notes with new key

See `docs/ENCRYPTION.md` for the full guide including installation, daily workflow, and upgrade/uninstall procedures.

### Alternative External Options

If you prefer external encryption instead of MeKB's built-in:

- **Cryptomator** - Encrypted vault container
- **Encrypted drive** - BitLocker, FileVault, LUKS

## Backup: 3-2-1 Rule

- **3** copies of your data
- **2** different media types (local + cloud)
- **1** offsite backup

Git + cloud sync = easy 3-2-1.

## AI Awareness

When using AI assistants, understand:

1. **What data is sent** - Your prompts and file contents
2. **Where it's processed** - Cloud servers (usually)
3. **Retention policies** - Varies by provider
4. **Training usage** - Some providers train on your data

Check your AI provider's data policy. For sensitive work, consider:

- Local AI models
- Zero-retention providers (AWS Bedrock)
- Not sharing classified content with AI

## Checklist

- [ ] Run `./scripts/setup-security.sh`
- [ ] Enable pre-commit hooks
- [ ] Review existing notes for sensitive content
- [ ] Classify sensitive notes appropriately
- [ ] Set up encryption for classified notes (optional)
- [ ] Back up encryption keys in password manager
- [ ] Review AI provider data policies

---

Security is about being thoughtful, not paranoid. Classify what matters, protect what's sensitive, and don't store what shouldn't be stored.
