# CLAUDE.md

This file provides guidance to AI assistants (Claude Code, etc.) when working with this vault.

## What is MeKB?

MeKB (Me Knowledge Base) is a personal knowledge management system built on plain markdown files. It helps you capture, connect, and compound your knowledge over time. The markdown files ARE the product - tools like Obsidian or Claude Code just help you work with them.

## Philosophy

**Three Core Principles:**

1. **Knowledge Outlives Tools** - Your markdown files are the permanent asset. Tools come and go.
2. **Collaboration is Power** - Knowledge flows between people. Easy to share, easy to receive.
3. **Your Data Deserves Protection** - Classify sensitive info. Be thoughtful about what you share.

## Quick Start

**New to MeKB?** Run `/start` for guided onboarding that creates personalised first notes.

```
/start              # Guided setup for new users
/daily              # Create today's note
/note My Idea       # Capture a thought
/q search term      # Find anything
```

**Without Claude Code?** Open `Note - Welcome to MeKB.md` and follow the checklist.

## Note Types

| Type         | Purpose                     | Template                |
| ------------ | --------------------------- | ----------------------- |
| **Daily**    | Daily journal and capture   | `Templates/Daily.md`    |
| **Note**     | General knowledge (default) | `Templates/Note.md`     |
| **Concept**  | Definitions ("What is X?")  | `Templates/Concept.md`  |
| **Task**     | Things to do                | `Templates/Task.md`     |
| **Project**  | Multi-task initiatives      | `Templates/Project.md`  |
| **Meeting**  | Meeting notes               | `Templates/Meeting.md`  |
| **Person**   | People you know             | `Templates/Person.md`   |
| **Resource** | Links, books, videos        | `Templates/Resource.md` |

**Three Pillars:**

- **Things** - People, places, tools (root directory)
- **Ideas** - Notes, concepts, resources (root directory)
- **Moments** - Daily notes, meetings, tasks (Daily/ folder or root)

## Skills Reference

### Getting Started

| Skill    | Purpose                                        |
| -------- | ---------------------------------------------- |
| `/start` | Guided onboarding - creates personalised notes |

### Daily Workflow

| Skill              | Purpose                   |
| ------------------ | ------------------------- |
| `/daily`           | Create today's daily note |
| `/meeting <title>` | Create meeting note       |
| `/task <title>`    | Quick-create task         |

### Capture

| Skill              | Purpose                   |
| ------------------ | ------------------------- |
| `/note <title>`    | Create knowledge note     |
| `/concept <title>` | Create concept definition |
| `/person <name>`   | Create person note        |
| `/weblink <url>`   | Save URL with summary     |

### Find

| Skill              | Purpose                |
| ------------------ | ---------------------- |
| `/q <search>`      | Search all notes       |
| `/recent`          | Show recently modified |
| `/related <topic>` | Find connected notes   |

### Maintenance

| Skill       | Purpose                         |
| ----------- | ------------------------------- |
| `/health`   | Vault health check              |
| `/orphans`  | Find unlinked notes             |
| `/classify` | Manage security classifications |

## Frontmatter Schema

### Universal Fields (all notes)

```yaml
type: <Type>
title: <Title>
created: YYYY-MM-DD
tags: []
```

### Optional: Classification (security)

```yaml
classification: public | personal | confidential | secret
```

| Level          | Meaning                | Sharing              |
| -------------- | ---------------------- | -------------------- |
| `public`       | Safe anywhere          | Blog, social, anyone |
| `personal`     | Private, not sensitive | Friends, family      |
| `confidential` | Sensitive              | Need-to-know only    |
| `secret`       | Highly sensitive       | Never share; encrypt |

Default (no field) = `personal`.

### Optional: Attribution (collaboration)

```yaml
source: null # Where it came from
author: null # Who wrote it (if not you)
contributors: [] # Others who contributed
via: null # How you received it
```

### Type-Specific Fields

**Task:**

```yaml
completed: false
due: null
project: null
```

**Meeting:**

```yaml
date: YYYY-MM-DD
attendees: []
```

**Person:**

```yaml
role: null
organisation: null
```

**Resource:**

```yaml
url: <URL>
```

**Project:**

```yaml
status: active | paused | completed
```

## Conventions

### File Naming

```
[Type] - [Title].md
```

Examples:

- `Note - How to learn effectively.md`
- `Person - Jane Smith.md`
- `Task - Review proposal.md`
- `Daily/2026/2026-02-04.md`

### Wiki-Links

Link notes with double brackets:

```markdown
See [[Note - My other note]] for details.
Met with [[Person - Jane Smith]] today.
```

### Tags

Keep it simple. Suggested prefixes:

- `project/` - Project grouping
- `area/` - Life areas (work, personal, health)
- `topic/` - Subject areas

Flat tags like `important`, `idea`, `review` are fine too.

## Tips

1. **Start with daily notes** - They're your capture surface. Review and link later.

2. **Link liberally** - Every `[[link]]` is a connection. More links = more value.

3. **Don't over-organise** - Start messy, structure emerges. Premature organisation kills flow.

4. **Use search** - `/q` finds anything. Don't worry about perfect filing.

5. **Review weekly** - Spend 15 minutes linking orphan notes and tidying.

6. **Capture first, process later** - Get it out of your head. Polish is optional.

7. **One note per concept** - If you keep writing about X, it deserves its own note.

8. **Backlinks are magic** - Click "Backlinks" to see what references the current note.

9. **Classification is optional** - Only mark sensitive stuff. Most notes are fine as-is.

10. **Git is your friend** - Commit often. History = free backup + audit trail.

## Security Best Practices

1. **Never store credentials** - Use a password manager, not your vault.

2. **Classify sensitive notes** - Add `classification: confidential` or `secret`.

3. **Check before sharing** - Search `classification: confidential` before publishing.

4. **Encrypt if needed** - Use git-crypt, Cryptomator, or encrypted drives for sensitive vaults.

5. **Understand AI implications** - When using AI assistants, your notes may be sent to external servers. Check your provider's data policy.

6. **Backup with 3-2-1** - 3 copies, 2 media types, 1 offsite.

## Tool Compatibility

MeKB works with any text editor. Enhanced experience with:

| Tool            | Enhancement                               |
| --------------- | ----------------------------------------- |
| **Obsidian**    | Graph view, backlinks, templates, plugins |
| **Claude Code** | AI assistance, automation, skills         |
| **VS Code**     | Foam extension, Markdown All-in-One       |
| **Typora**      | Clean writing experience                  |
| **Logseq**      | Outline-based alternative                 |
| **Any editor**  | Just works - it's plain text              |

## Directory Structure

```
MeKB/
├── .claude/
│   └── skills/        # Claude Code skills
├── .obsidian/         # Obsidian config (optional)
├── Daily/
│   └── YYYY/          # Daily notes by year
├── Templates/         # Note templates
├── Archive/           # Completed/old content
├── CLAUDE.md          # This file
├── README.md          # Getting started
└── *.md               # Your notes (root)
```

## Creating Notes

### With Claude Code

```
/daily                    # Today's note
/note My brilliant idea   # Knowledge note
/task Buy groceries       # Task
/meeting Team standup     # Meeting note
```

### Manually

1. Copy template from `Templates/`
2. Rename: `[Type] - [Title].md`
3. Fill in frontmatter
4. Write content
5. Add `[[links]]` to related notes

## Finding Notes

### With Claude Code

```
/q kafka                  # Full-text search
/recent                   # Recently modified
/related authentication   # Notes about a topic
```

### Manually

- **Obsidian**: Ctrl/Cmd+O to quick-open, Ctrl/Cmd+Shift+F to search
- **VS Code**: Ctrl/Cmd+P to open, Ctrl/Cmd+Shift+F to search
- **Terminal**: `grep -r "search term" *.md`

## Migrating

### From Notion

1. Export workspace as Markdown
2. Move `.md` files to MeKB root
3. Add frontmatter to each file
4. Convert Notion links to `[[wiki-links]]`

### From Roam

1. Export as Markdown
2. Move files to MeKB root
3. Add frontmatter (Roam uses `[[links]]` already)

### From Apple Notes

1. Export notes (File > Export)
2. Add frontmatter
3. Convert formatting to Markdown

### To Anywhere

Your notes are already portable markdown. Just copy the folder.

---

**Version:** 1.0
**Lines:** ~280 (target: <500)
