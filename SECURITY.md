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

## Encryption Options

For sensitive vaults:

- **git-crypt** - Encrypt specific files in Git
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
- [ ] Set up encrypted backup for `secret/` folder
- [ ] Review AI provider data policies

---

Security is about being thoughtful, not paranoid. Classify what matters, protect what's sensitive, and don't store what shouldn't be stored.
