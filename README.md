# MeKB

**Me Knowledge Base** - A personal knowledge management system for everyone.

MeKB helps you capture, connect, and compound your knowledge over time using plain markdown files. No special tools required - just a text editor.

## Philosophy

### Knowledge Outlives Tools

Your markdown files are the permanent asset. Today you might use Obsidian, tomorrow a different editor. Today Claude Code, tomorrow a different AI assistant. What persists? **Plain text files.**

MeKB is designed so:

- Every note is a standalone `.md` file
- Frontmatter uses standard YAML
- Wiki-links (`[[Note Title]]`) are widely supported
- No proprietary formats, no lock-in

### Collaboration is Humanity's Superpower

Knowledge flows between people:

- **Easy to share** - It's just markdown. Email it, paste it, post it.
- **Easy to receive** - Drop a `.md` file in, it works.
- **Git-native** - Fork, branch, merge, pull request.
- **No walled garden** - Export anything, import anything.

### Your Data Deserves Protection

Not all notes are equal:

- Classify sensitive info: `public`, `personal`, `confidential`, `secret`
- Never store passwords in notes - use a password manager
- Understand what AI assistants can see
- Encrypt if needed (git-crypt, Cryptomator)

## Prerequisites

**Required:** Any text editor (Notepad, TextEdit, VS Code, anything)

**Recommended:**

- [Obsidian](https://obsidian.md) - Graph view, backlinks, plugins
- [Claude Code](https://claude.ai/code) - AI assistance, automation

**Optional:**

- Git - For version control and backup
- Node.js - For advanced automation

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/MeKB.git my-knowledge-base
cd my-knowledge-base
```

Or just download and unzip. That's it - no build step, no dependencies.

## First 5 Minutes

### 1. Create Your First Note

Copy `Templates/Note.md` to the root:

```bash
cp Templates/Note.md "Note - My first note.md"
```

Edit the file:

```yaml
---
type: Note
title: My first note
created: 2026-02-04
tags: []
---
# My first note

This is my first note in MeKB!
```

### 2. Link to Another Note

Create a second note and link them:

```markdown
This relates to [[Note - My first note]].
```

### 3. Find What You Captured

- **Obsidian**: Ctrl/Cmd+O or Ctrl/Cmd+Shift+F
- **VS Code**: Ctrl/Cmd+P or Ctrl/Cmd+Shift+F
- **Terminal**: `grep -r "search term" *.md`

**With Claude Code:**

```
/q search term
```

## Tool Enhancements

MeKB works with any text editor. These tools add superpowers:

### Obsidian (Recommended)

Open the folder as a vault. You get:

- **Graph view** - Visualize connections
- **Backlinks** - See what links to current note
- **Templates** - Quick note creation
- **Daily notes** - Automatic daily journal

### Claude Code

Run `claude` in the MeKB folder. You get:

- `/daily` - Create today's note
- `/note <title>` - Quick capture
- `/q <search>` - Fast search
- `/meeting <title>` - Meeting notes
- See `CLAUDE.md` for all skills

### VS Code

Install extensions:

- **Foam** - Wiki-links and graph
- **Markdown All-in-One** - Enhanced editing

### Any Editor

Just works. Edit `.md` files, use `[[brackets]]` for links.

## Note Types

| Type         | Purpose           | Example                         |
| ------------ | ----------------- | ------------------------------- |
| **Daily**    | Daily journal     | `Daily/2026/2026-02-04.md`      |
| **Note**     | General knowledge | `Note - How to learn.md`        |
| **Concept**  | Definitions       | `Concept - What is PKM.md`      |
| **Task**     | Things to do      | `Task - Review proposal.md`     |
| **Project**  | Multi-task work   | `Project - Website redesign.md` |
| **Meeting**  | Meeting notes     | `Meeting - Team standup.md`     |
| **Person**   | People you know   | `Person - Jane Smith.md`        |
| **Resource** | External links    | `Resource - Great article.md`   |

## Sharing & Collaboration

### Share a Note

1. It's already markdown - just send the file
2. Recipient opens in any text editor
3. They can add it to their own vault

### Work in Teams

1. Create a shared Git repo
2. Each person clones
3. Standard Git workflow: branch, edit, commit, merge
4. Or use Dropbox/iCloud/Google Drive for simpler sync

### Track Sources

Add attribution in frontmatter:

```yaml
source: "Conversation with [[Person - Jane Smith]]"
author: "Jane Smith"
via: "meeting"
```

## Security & Privacy

MeKB includes built-in security features to protect sensitive information.

### Quick Setup

```bash
./scripts/setup-security.sh
```

This enables:
- Secret detection (pre-commit hook)
- AI access control
- Classified folders

### Classification Levels

Add to any note's frontmatter:

```yaml
classification: confidential
```

| Level | AI Access | Use For |
|-------|-----------|---------|
| `public` | ✅ Allowed | Blog drafts, public notes |
| `personal` | ✅ Allowed | Private but not sensitive (default) |
| `confidential` | ⚠️ Prompts | Work secrets, client info |
| `secret` | 🚫 Blocked | Passwords, keys, highly sensitive |

### AI Access Control

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

### Trusted AI Providers

Different trust levels for different AI setups:

| Provider | Trust Level | Notes |
|----------|-------------|-------|
| **Bedrock** | Up to confidential | Zero data retention |
| **Local** | Up to secret | Data never leaves machine |
| **API** | Up to personal | 30-day retention |
| **Consumer** | Up to personal | May train on data |

### Folder Inheritance

Files in classified folders auto-inherit classification:

```
confidential/   → classification: confidential
secret/         → classification: secret
private/        → classification: confidential
```

The `secret/` folder is gitignored - never committed.

### Secret Detection

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

### /classify Skill

Manage classifications with Claude Code:

```
/classify              # Summary of all classifications
/classify check        # Find files needing classification
/classify list secret  # List all secret files
/classify audit        # Full security audit
/classify set FILE confidential
```

### Never Store

- Passwords, API keys, tokens
- Full credit card numbers
- Government ID numbers
- Unencrypted sensitive data

Use a password manager instead.

### Encryption Options

For sensitive vaults:

- **git-crypt** - Encrypt specific files in Git
- **Cryptomator** - Encrypted vault container
- **Encrypted drive** - BitLocker, FileVault, LUKS

### Backup: 3-2-1 Rule

- **3** copies of your data
- **2** different media types (local + cloud)
- **1** offsite backup

Git + cloud sync = easy 3-2-1.

## Portability

### From Notion

1. Export workspace as Markdown
2. Move `.md` files here
3. Add frontmatter to each
4. Replace Notion links with `[[wiki-links]]`

### From Roam

1. Export as Markdown
2. Move files here
3. Add frontmatter (links already compatible)

### From Apple Notes

1. Export notes
2. Add frontmatter
3. Convert formatting

### To Anywhere

Just copy the folder. It's portable markdown.

## Growing Your Vault

### Week 1: Capture

- Create daily notes
- Dump thoughts, don't organise
- Link when obvious

### Week 2: Connect

- Review daily notes
- Create dedicated notes for recurring topics
- Add links between related notes

### Week 3: Compound

- Notice patterns
- Create Concept notes for important ideas
- Build your personal knowledge graph

### Ongoing

- 15 min weekly review
- Prune what's not useful
- Link orphan notes
- Let structure emerge naturally

## Directory Structure

```
MeKB/
├── .claude/
│   ├── skills/        # Claude Code skills
│   └── hooks/         # Security hooks
├── .mekb/
│   └── security.json  # Security configuration
├── .obsidian/         # Obsidian config
├── Daily/
│   └── 2026/          # Daily notes by year
├── Templates/         # Note templates
├── Archive/           # Old/completed content
├── confidential/      # Auto-classified as confidential
├── secret/            # Auto-classified as secret (gitignored)
├── scripts/           # Utility scripts
├── CLAUDE.md          # AI assistant instructions
├── README.md          # This file
└── *.md               # Your notes
```

## Contributing

MeKB is a template. Fork it, make it yours. Share improvements via pull request.

## License

MIT - Do whatever you want with it.

---

**Start simple. Link liberally. Let knowledge compound.**
