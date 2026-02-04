# MeKB Security Features Prompt

**Purpose:** Add secret detection and AI access control to MeKB.

---

## Feature 1: Secret Detection (Pre-commit Hook)

### Goal
Prevent accidental commits of sensitive data (API keys, passwords, tokens, credentials).

### Implementation

Create a pre-commit hook that scans staged files for:
- API keys (AWS, Azure, GCP, GitHub, etc.)
- Passwords in plaintext
- Private keys (SSH, PGP)
- Connection strings
- Bearer tokens
- High-entropy strings that look like secrets

### Files to Create

1. **`.pre-commit-config.yaml`** - Pre-commit configuration
2. **`scripts/detect-secrets.py`** - Custom secret scanner (or use detect-secrets library)
3. **Documentation in README**

### Behaviour
- Runs automatically on `git commit`
- Blocks commit if secrets detected
- Shows which file(s) and line(s) contain potential secrets
- Provides guidance on how to proceed (remove secret, use .env, add to allowlist)

### User Control
- `.secrets.baseline` - Allowlist for false positives
- `--no-verify` flag to bypass (with warning)

---

## Feature 2: AI Classification Checker

### Goal
Control what AI assistants (Claude Code, etc.) can access based on note classification.

### Classification Levels
```yaml
classification: public       # AI can freely access
classification: personal     # AI can access (default if not specified)
classification: confidential # AI access controlled
classification: secret       # AI access blocked
```

### Two Operating Modes

#### Mode 1: Interactive (Ask Before Access)
When AI tries to read a `confidential` file:
1. Hook intercepts the Read/Edit request
2. Prompts user: "This file is marked CONFIDENTIAL. Allow AI access? [y/N]"
3. User confirms or denies
4. If denied, AI receives: "Access denied: File is classified as confidential"
5. Decision can be remembered for session or always-ask

#### Mode 2: Strict (Always Block)
When AI tries to read a `confidential` or `secret` file:
1. Hook intercepts the Read/Edit request
2. Automatically blocks access
3. AI receives: "Access denied: File is classified as [level]. AI access is disabled for this classification."
4. No prompt, no override (except manual reclassification)

### Configuration

**`.claude/settings.json`** or **`.mekb/security.json`**:
```json
{
  "ai_access_control": {
    "enabled": true,
    "mode": "interactive",  // "interactive" | "strict"
    "levels": {
      "public": "allow",
      "personal": "allow",
      "confidential": "ask",      // "allow" | "ask" | "block"
      "secret": "block"
    },
    "remember_session": true,     // Remember decisions for session
    "log_access_attempts": true   // Audit log of access attempts
  }
}
```

### Implementation

**Hook: `.claude/hooks/classification-guard.py`**

```
PreToolUse hook for: Read, Edit, Write, Grep, Glob

1. Extract file_path from tool_input
2. If file exists, read first 50 lines looking for frontmatter
3. Parse classification from frontmatter (default: "personal")
4. Check against config:
   - "allow" → exit 0 (permit)
   - "block" → print message, exit 2 (deny)
   - "ask" → prompt user, act on response
5. Log access attempt if logging enabled
```

### User Experience

**Interactive mode example:**
```
$ claude
> Read the file "Note - Client passwords.md"

⚠️  CLASSIFICATION CHECK
File: Note - Client passwords.md
Level: confidential

This file is marked CONFIDENTIAL.
Allow AI to read this file? [y/N/always/never]: n

Access denied. The AI cannot see this file's contents.
```

**Strict mode example:**
```
$ claude
> Read the file "Note - Client passwords.md"

🚫 ACCESS DENIED
File: Note - Client passwords.md
Level: confidential

AI access is blocked for confidential files.
To allow access, change the file's classification or update security settings.
```

### Audit Log

**`.mekb/access-log.jsonl`** (optional):
```jsonl
{"timestamp": "2026-02-04T10:30:00Z", "file": "Note - Client passwords.md", "classification": "confidential", "action": "blocked", "mode": "strict"}
{"timestamp": "2026-02-04T10:31:00Z", "file": "Note - Meeting notes.md", "classification": "personal", "action": "allowed", "mode": "interactive"}
```

---

## Feature 3: Classification Skill

### `/classify` Skill

Audit and manage classifications across the vault.

```
/classify                    # Show classification summary
/classify check              # Find files that might need classification
/classify list confidential  # List all confidential files
/classify list secret        # List all secret files
/classify set <file> <level> # Set classification for a file
/classify audit              # Full audit report
```

### Classification Checker Logic

Scan for files that might need higher classification:
- Contains words: password, secret, key, token, credential, api_key
- Contains patterns: email addresses, phone numbers, IP addresses
- Has no classification but links to classified files
- Is in certain folders (if configured)

---

## Installation & Setup

### Quick Setup (Recommended defaults)
```bash
cd ~/your-mekb-vault
./scripts/setup-security.sh
```

Sets up:
- Pre-commit hook for secret detection
- Interactive mode for confidential, block for secret
- Audit logging enabled

### Manual Setup

1. Install pre-commit: `pip install pre-commit`
2. Run: `pre-commit install`
3. Copy hook to `.claude/hooks/`
4. Add to `.claude/settings.json`

---

## Design Decisions

### Why block at AI level, not filesystem?
- Filesystem permissions would break Obsidian/editor access
- AI-level blocking is surgical: you can still see the file, AI can't
- Allows progressive trust: start interactive, go strict if needed

### Why YAML frontmatter for classification?
- Already part of MeKB's note structure
- Human-readable, no separate database
- Works with any tool (grep, Obsidian, scripts)
- Portable with the file

### Why two modes?
- **Interactive**: For users who want AI help but with oversight
- **Strict**: For users with compliance requirements or high-security needs

### What about files without classification?
- Default to `personal` (AI can access)
- `/classify check` helps identify files needing classification
- Encourages explicit classification over time

---

## Security Considerations

1. **Hook bypass**: User can always use `--dangerously-skip-permissions` but that's explicit
2. **Frontmatter tampering**: AI could theoretically edit classification - but that would show in git diff
3. **Log sensitivity**: Access log doesn't contain file contents, only metadata
4. **Performance**: Frontmatter parsing is fast (first 50 lines only)

---

## Success Criteria

1. **Secret Detection**: No secrets committed to git (verified by CI)
2. **Classification Guard**: AI cannot read secret files in strict mode
3. **User Control**: Easy to switch between modes
4. **Audit Trail**: Can review what AI accessed
5. **No Friction for Public/Personal**: Normal workflow unchanged

---

## Questions Before Implementation

1. Should the hook also protect against AI *writing* to classified files?
2. Should there be a "trusted AI" mode for local/Bedrock setups?
3. Should classification be inheritable (folder-level defaults)?
4. Should we integrate with the security-guidance plugin patterns?

---

## Related

- [[Pattern - Vault Security Hardening]]
- [[Concept - Secure Claude Code Implementation via AWS Bedrock]]
- MeKB README security section
