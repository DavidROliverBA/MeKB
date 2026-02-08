# /classify

Manage and audit note classifications.

## Usage

```
/classify                      # Show classification summary
/classify check                # Find files that might need classification
/classify list <level>         # List files at classification level
/classify set <file> <level>   # Set classification for a file
/classify audit                # Full security audit
/classify config               # Show current security config
```

## Commands

### `/classify` - Summary

Show count of notes by classification level.

**Instructions:**
1. Scan all `.md` files in vault (excluding Templates/, .obsidian/, .claude/)
2. Extract `classification` from frontmatter
3. Check folder inheritance rules from `.mekb/security.json`
4. Count by level: public, personal, confidential, secret
5. Show notes without explicit classification

**Output:**
```
Classification Summary
======================
public:       12 notes
personal:     45 notes (default)
confidential:  8 notes
secret:        2 notes
unclassified: 23 notes (treated as personal)

Total: 90 notes
```

---

### `/classify check` - Find files needing classification

Scan for files that might need higher classification.

**Instructions:**
1. Scan all `.md` files without explicit classification
2. Check content for sensitive patterns:
   - password, secret, key, token, credential
   - email addresses, phone numbers
   - financial terms: salary, account, bank
   - personal terms: health, medical, ssn
3. Check if file links to classified files
4. Score each file by risk indicators
5. Show top 20 files needing review

**Output:**
```
Files Potentially Needing Classification
========================================

HIGH RISK (contains sensitive terms):
- Note - API credentials.md (contains: password, key)
- Note - Client contact info.md (contains: email, phone)

MEDIUM RISK (links to classified files):
- Note - Project overview.md (links to 2 confidential files)

Recommendation: Review these files and add classification field.
```

---

### `/classify list <level>` - List files at level

List all files with specific classification.

**Instructions:**
1. Parse level from command (public/personal/confidential/secret)
2. Scan all `.md` files
3. Include files where:
   - Frontmatter `classification` matches level
   - Folder inheritance assigns this level
4. Show file path and title

**Example:**
```
/classify list confidential
```

**Output:**
```
Confidential Files (8)
======================
- Note - Client passwords.md
- Note - Salary information.md
- Meeting - HR review.md
- confidential/Budget 2026.md (folder inheritance)
...
```

---

### `/classify set <file> <level>` - Set classification

Add or update classification for a file.

**Instructions:**
1. Parse file path and level from command
2. Validate level is: public, personal, confidential, secret
3. Read file content
4. If frontmatter exists:
   - Add/update `classification: <level>` field
5. If no frontmatter:
   - Add frontmatter with classification
6. Write file
7. **Encryption integration** (when encryption is enabled in `.mekb/security.json`):
   - If raising to `confidential` or `secret` AND file is not encrypted:
     - Auto-encrypt: `python3 scripts/encrypt.py encrypt "<file>"`
     - Confirm encryption to user
   - If lowering FROM `confidential`/`secret` to `personal`/`public` AND file IS encrypted:
     - Auto-decrypt: `python3 scripts/encrypt.py decrypt "<file>" --identity <identity_path>`
     - Confirm decryption to user
8. Confirm change

**Example:**
```
/classify set "Note - Client info.md" confidential
```

**Output:**
```
✅ Updated classification for "Note - Client info.md"
   Level: confidential
   AI access: Will prompt before access (interactive mode)
   Encryption: Encrypted with 2 recipients
```

---

### `/classify audit` - Full security audit

Comprehensive security review.

**Instructions:**
1. Run classification summary
2. Run sensitive content check
3. Check for files in classified folders without explicit classification
4. Check access log for denied attempts
5. Verify security config is valid
6. Check for secrets in content (run detect-secrets patterns)
7. **Encryption audit** (when encryption is enabled):
   - Run: `python3 scripts/encrypt.py audit --vault .`
   - Report any classified files missing encryption
   - Report any encrypted files without proper classification

**Output:**
```
MeKB Security Audit
===================
Date: 2026-02-04

CLASSIFICATION STATUS
- 67 notes classified
- 23 notes unclassified (treated as personal)

ENCRYPTION STATUS
- 5 notes correctly encrypted
- 2 classified notes NOT encrypted (need /encrypt)
- 0 encrypted notes without classification

POTENTIAL ISSUES
⚠️  3 files contain sensitive patterns without classification
⚠️  2 files in confidential/ folder lack explicit classification
⚠️  1 file may contain hardcoded credentials
⚠️  2 confidential files are NOT encrypted

ACCESS LOG (last 7 days)
- 12 access attempts
- 3 blocked (confidential files)
- 2 prompted (user denied)

RECOMMENDATIONS
1. Review files flagged above
2. Add classification to unclassified files in secure folders
3. Check Note - API setup.md for potential secrets
4. Run /encrypt on unencrypted classified files

Config: .mekb/security.json
Mode: interactive
Write protection: enabled
Encryption: enabled (age, split-format)
```

---

### `/classify config` - Show security config

Display current security configuration.

**Instructions:**
1. Read `.mekb/security.json`
2. Display formatted config
3. Explain current settings

**Output:**
```
MeKB Security Configuration
===========================

AI Access Control: ENABLED
Mode: interactive

Classification Rules:
  public:       allow (AI can freely access)
  personal:     allow (AI can freely access)
  confidential: ask   (AI will prompt before access)
  secret:       block (AI access denied)

Write Protection: ENABLED
  AI cannot write to confidential/secret files

Trusted AI Providers: ENABLED
  bedrock: trusted up to confidential
  local:   trusted up to secret

Folder Inheritance: ENABLED
  confidential/ → confidential
  secret/       → secret
  private/      → confidential

Config file: .mekb/security.json
```

---

## Classification Levels Reference

| Level | AI Access | Use For |
|-------|-----------|---------|
| `public` | Always allowed | Blog drafts, public notes |
| `personal` | Always allowed | Private but not sensitive |
| `confidential` | Ask/Block | Work secrets, client info |
| `secret` | Always blocked | Passwords, keys, highly sensitive |

## Setting Classification

Add to any note's frontmatter:

```yaml
---
type: Note
title: My Secret Note
classification: confidential
---
```

Or use folder inheritance by placing files in `confidential/` or `secret/` folders.
