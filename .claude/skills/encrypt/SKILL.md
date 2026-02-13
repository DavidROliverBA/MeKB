---
name: encrypt
---

# /encrypt

Encrypt and decrypt classified notes using age.

Notes classified as `confidential` or `secret` can be encrypted at rest using
split-format encryption: plaintext YAML frontmatter + age-encrypted body.

## Usage

```
/encrypt <file>           # Encrypt a note
/encrypt audit            # Audit vault encryption status
/encrypt status <file>    # Check encryption status of a file
/encrypt setup            # Run encryption setup wizard
/decrypt <file>           # Decrypt a note
```

## Commands

### `/encrypt <file>` - Encrypt a note

Encrypt the body of a markdown note, preserving frontmatter.

**Instructions:**
1. Read `.mekb/security.json` to get encryption config
2. Verify encryption is enabled and recipients are configured
3. Check if file is already encrypted (skip if so)
4. Run: `python3 scripts/encrypt.py encrypt "<file>"`
   - Uses recipients from config
   - Split-format: frontmatter stays plaintext, body encrypted
5. Verify the file was encrypted (check for `encrypted: true` in frontmatter)
6. Confirm to user

**Prerequisites:**
- `age` installed (`brew install age`)
- Encryption configured (run `/encrypt setup` first)

**Output:**
```
Encrypted: Note - Client Credentials.md
  Recipients: 2 (primary + backup key)
  Frontmatter: plaintext (searchable)
  Body: encrypted (age ASCII armour)
```

---

### `/decrypt <file>` - Decrypt a note

Decrypt an encrypted note, restoring the plaintext body.

**Instructions:**
1. Read `.mekb/security.json` to get identity file path
2. Check if file is actually encrypted (skip if not)
3. Run: `python3 scripts/encrypt.py decrypt "<file>" --identity <identity_path>`
   - Uses primary identity from config (triggers Touch ID if age-plugin-se)
   - Falls back to backup identity if primary fails
4. Verify decryption succeeded (body no longer contains age armour)
5. Confirm to user

**Output:**
```
Decrypted: Note - Client Credentials.md
  Classification: confidential (still set)
  Body: plaintext restored
```

---

### `/encrypt audit` - Audit encryption status

Check all classified notes for correct encryption.

**Instructions:**
1. Run: `python3 scripts/encrypt.py audit --vault .`
2. Report:
   - Correctly encrypted files (classified + encrypted)
   - MISSING encryption (classified but NOT encrypted) - these need action
   - Encrypted but not classified (unusual - investigate)
3. Suggest remediation for any mismatches

**Output:**
```
Encryption Audit (150 files checked)
==================================================

  Correctly encrypted: 5
    confidential/Budget.md (confidential)
    Note - API Keys.md (secret)
    ...

  MISSING encryption (2 files):
    Note - Client Info.md (confidential) - NOT ENCRYPTED
    Note - Passwords.md (secret) - NOT ENCRYPTED

Recommendation: Run /encrypt on the 2 files above.
```

---

### `/encrypt status <file>` - Check file status

Show encryption status of a single file.

**Instructions:**
1. Run: `python3 scripts/encrypt.py status "<file>"`
2. Display result

**Output:**
```
ENCRYPTED (age, 2 recipients)
```
or
```
PLAINTEXT (classification: confidential)
```

---

### `/encrypt setup` - Encryption setup wizard

Set up encryption keys and configuration.

**Instructions:**
1. Check if `age` is installed: `which age`
   - If not: suggest `brew install age`
2. Check if keys exist in `.mekb/`:
   - `.mekb/age-key.txt` (primary key)
   - `.mekb/backup-key.txt` (backup key)
3. If keys missing, run: `./scripts/setup-security.sh`
   - Or generate manually:
     ```bash
     age-keygen -o .mekb/age-key.txt
     age-keygen -o .mekb/backup-key.txt
     ```
4. Verify `.mekb/security.json` has encryption section with recipients
5. Verify key files are in `.gitignore`
6. Print summary and remind user to back up keys

---

## Split-Format Explained

Encrypted files look like this:

```yaml
---
title: Client Credentials
type: Note
classification: secret
encrypted: true
encryption_method: age
encryption_recipients: 2
---
-----BEGIN AGE ENCRYPTED FILE-----
YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+...
-----END AGE ENCRYPTED FILE-----
```

- **Frontmatter** stays plaintext: searchable, queryable by Dataview, readable by classification guard
- **Body** is encrypted: unreadable without the key
- **Git** sees metadata changes as text diffs, body as changed ciphertext

## Key Management

| File | Purpose | Backed up? |
|------|---------|-----------|
| `.mekb/age-key.txt` | Primary decryption key | gitignored |
| `.mekb/backup-key.txt` | Backup key for recovery | gitignored, store in password manager |

**Recovery:** If primary key is lost, decrypt with backup key:
```bash
python3 scripts/encrypt.py decrypt <file> --identity .mekb/backup-key.txt
```

## Integration with /classify

When encryption is enabled (`encrypt_on_classify: true` in config):
- `/classify set <file> confidential` or `secret` will auto-encrypt
- `/classify set <file> personal` or `public` will auto-decrypt
