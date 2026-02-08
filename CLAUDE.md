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

### Search Index

Build the SQLite FTS5 search index for fast, ranked full-text search:

```bash
python3 scripts/build-index.py        # Build/update index (~0.03s)
python3 scripts/build-index.py --stats # Show index statistics
python3 scripts/search.py "query"      # Search from command line
```

**Optional:** For semantic (meaning-based) search, install `sentence-transformers` and build vector embeddings:

```bash
pip install sentence-transformers
python3 scripts/build-embeddings.py    # Build vector index
```

When both indexes exist, search automatically uses hybrid fusion (70% BM25 + 30% vector).

## Note Types

### Core Types

| Type         | Purpose                     | Template                |
| ------------ | --------------------------- | ----------------------- |
| **Daily**    | Daily journal and capture   | `Templates/Daily.md`    |
| **Note**     | General knowledge (default) | `Templates/Note.md`     |
| **Concept**  | Definitions ("What is X?")  | `Templates/Concept.md`  |
| **Task**     | Things to do                | `Templates/Task.md`     |
| **Project**  | Multi-task initiatives      | `Templates/Project.md`  |
| **Meeting**  | Meeting notes               | `Templates/Meeting.md`  |
| **Person**   | People you know (CRM)       | `Templates/Person.md`   |
| **Resource** | Links, books, videos        | `Templates/Resource.md` |

### Professional Types

| Type           | Purpose                      | Template                   |
| -------------- | ---------------------------- | -------------------------- |
| **Decision**   | Track decisions with context | `Templates/Decision.md`    |
| **ActionItem** | Meeting actions with owners  | `Templates/ActionItem.md`  |
| **Interaction**| Log conversations/meetings   | `Templates/Interaction.md` |

**Three Pillars:**

- **Things** - People, places, tools (root directory)
- **Ideas** - Notes, concepts, decisions, resources (root directory)
- **Moments** - Daily notes, meetings, tasks, interactions (Daily/ folder or root)

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
| `/clip <url>`      | Web clipper with summary  |
| `/voice`           | Voice note transcription  |

### Find & Discover

| Skill              | Purpose                          |
| ------------------ | -------------------------------- |
| `/q <search>`      | Keyword search all notes         |
| `/search <query>`  | Semantic search by meaning       |
| `/ask <question>`  | AI-powered vault Q&A             |
| `/recent`          | Show recently modified           |
| `/related <topic>` | Find connected notes             |
| `/suggest`         | AI-powered link suggestions      |
| `/graph`           | Explore knowledge connections    |
| `/connections`     | Typed relationship exploration   |

### Review & Reflect

| Skill      | Purpose                              |
| ---------- | ------------------------------------ |
| `/review`  | Spaced repetition - resurface old notes |
| `/weekly`  | Generate weekly summary              |
| `/stale`   | Find notes needing verification      |

### Relationships (CRM)

| Skill               | Purpose                        |
| ------------------- | ------------------------------ |
| `/people`           | Network dashboard              |
| `/people reconnect` | Who to reach out to            |
| `/people met <name>`| Log an interaction             |
| `/people search`    | Find people by expertise       |

### Integrations

| Skill       | Purpose                         |
| ----------- | ------------------------------- |
| `/calendar` | Sync calendar, create meeting notes |
| `/readwise` | Sync highlights from Readwise   |
| `/browse`   | Fetch web content, screenshots  |
| `/notify`   | Send desktop/Slack/Discord/email notifications |

### Productivity

| Skill       | Purpose                         |
| ----------- | ------------------------------- |
| `/habits`   | Track daily habits              |
| `/export`   | Export notes in shareable formats |

### Publishing

| Skill       | Purpose                         |
| ----------- | ------------------------------- |
| `/site`     | Build static HTML site from notes |

### Session & Maintenance

| Skill       | Purpose                         |
| ----------- | ------------------------------- |
| `/session`  | View/save current session state |
| `/schedule` | Manage scheduled jobs           |
| `/automate` | Custom recurring tasks          |
| `/health`   | Vault health check              |
| `/orphans`  | Find unlinked notes             |
| `/classify` | Manage security classifications |
| `/encrypt`  | Encrypt/decrypt classified notes |

## Frontmatter Schema

### Universal Fields (all notes)

```yaml
type: <Type>
title: <Title>
created: YYYY-MM-DD
tags: []
```

### Quality Tracking (optional)

```yaml
verified: YYYY-MM-DD    # Last time content was checked
freshness: current      # current | recent | stale
confidence: high        # high | medium | low
```

### Relationships (optional)

Typed relationships for knowledge graph edges:

```yaml
relationships:
  depends-on: ["[[Decision - Cloud Provider Selection]]"]
  references: ["[[Concept - Event Sourcing]]"]
  supersedes: []
```

**Available types:** `references`, `depends-on`, `supersedes`, `contradicts`, `supports`, `implements`, `extends`, `inspired-by`

### Classification (security)

```yaml
classification: public | personal | confidential | secret
```

| Level          | Meaning                | Sharing              |
| -------------- | ---------------------- | -------------------- |
| `public`       | Safe anywhere          | Blog, social, anyone |
| `personal`     | Private, not sensitive | Friends, family      |
| `confidential` | Sensitive              | Need-to-know only    |
| `secret`       | Highly sensitive       | Never share; encrypt |

### Type-Specific Fields

**Task:**
```yaml
completed: false
due: null
project: null
priority: medium
```

**Meeting:**
```yaml
date: YYYY-MM-DD
attendees: []
```

**Person (CRM):**
```yaml
role: null
organisation: null
relationship_type: colleague | client | vendor | friend | mentor
last_contact: null
contact_frequency: monthly
next_followup: null
expertise: []
```

**Decision:**
```yaml
status: proposed | approved | rejected
context: null
alternatives: []
decision: null
reasoning: null
deciders: []
date_decided: null
```

**ActionItem:**
```yaml
assigned_to: null
due: null
source_meeting: null
status: pending | in_progress | completed
```

**Interaction:**
```yaml
person: null
date: YYYY-MM-DD
interaction_type: meeting | call | email | message
summary: null
next_steps: []
```

**Resource:**
```yaml
url: <URL>
read_status: unread | reading | read
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
- `Decision - API Strategy.md`
- `Daily/2026/2026-02-04.md`

### Wiki-Links

Link notes with double brackets:

```markdown
See [[Note - My other note]] for details.
Met with [[Person - Jane Smith]] today.
Decision: [[Decision - API Strategy]]
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

4. **Use search** - `/q` for exact terms, `/search` for concepts.

5. **Review regularly** - Use `/review` daily and `/weekly` on Fridays.

6. **Capture first, process later** - Get it out of your head. Polish is optional.

7. **Track decisions** - Use Decision notes for choices you'll want to remember.

8. **Maintain relationships** - Use `/people reconnect` weekly to stay connected.

9. **Verify old notes** - Use `/stale` monthly to keep knowledge current.

10. **Git is your friend** - Commit often. History = free backup + audit trail.

## Security Best Practices

1. **Never store credentials** - Use a password manager, not your vault.

2. **Classify sensitive notes** - Add `classification: confidential` or `secret`.

3. **Check before sharing** - Search `classification: confidential` before publishing.

4. **Encrypt classified notes** - Use `/encrypt` for confidential/secret notes. Encrypted body is not readable without the key, even by AI assistants.

5. **Understand AI implications** - Notes may be sent to external servers.

6. **Backup with 3-2-1** - 3 copies, 2 media types, 1 offsite.

## Tool Compatibility

MeKB works with any text editor. Enhanced experience with:

| Tool            | Enhancement                               |
| --------------- | ----------------------------------------- |
| **Obsidian**    | Graph view, backlinks, templates, plugins |
| **Claude Code** | AI assistance, automation, skills         |
| **VS Code**     | Foam extension, Markdown All-in-One       |
| **Any editor**  | Just works - it's plain text              |

## Directory Structure

```
MeKB/
├── .claude/
│   └── skills/        # Claude Code skills (36 skills)
├── .mekb/             # MeKB configuration
├── .obsidian/         # Obsidian config (optional)
├── Daily/
│   └── YYYY/          # Daily notes by year
├── Templates/         # Note templates (11 types)
├── Archive/           # Completed/old content
├── scripts/           # Utility scripts
├── CLAUDE.md          # This file
├── README.md          # Getting started
├── SECURITY.md        # Security documentation
└── *.md               # Your notes (root)
```

## Webhook Server

Receive webhooks to create notes, trigger rebuilds, and check health:

```bash
python3 scripts/webhook-server.py --token my-secret  # Start with auth
```

Endpoints: `POST /api/note`, `POST /api/rebuild-index`, `POST /api/rebuild-graph`, `POST /api/health`, `GET /api/status`. Listens on `127.0.0.1:9876` by default.

## Environment Variables

For integrations, set these environment variables:

```bash
# Voice transcription
export OPENAI_API_KEY="your-key"

# Readwise sync
export READWISE_TOKEN="your-token"

# Calendar (Google)
export GOOGLE_CALENDAR_CREDENTIALS="path/to/credentials.json"

# Webhook server auth
export MEKB_WEBHOOK_TOKEN="your-token"
```

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

### To Anywhere
Your notes are already portable markdown. Just copy the folder.

---

**Version:** 2.5
**Skills:** 36
**Note Types:** 11
