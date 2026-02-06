# MeKB

**Me Knowledge Base** - A personal knowledge system for everyone.

Capture, connect, and compound your knowledge using plain Markdown files. No special tools required.

## Philosophy

1. **Knowledge Outlives Tools** - Your markdown files are the permanent asset. Tools come and go.
2. **Collaboration is Power** - Easy to share, easy to receive. It's just text files.
3. **Your Data Deserves Protection** - Classify sensitive info. Be thoughtful about what you share.

## Quick Start

```bash
# Clone it
git clone https://github.com/DavidROliverBA/MeKB.git my-knowledge-base
cd my-knowledge-base

# Open in Obsidian (recommended) or any text editor
# That's it - no build step, no dependencies
```

**With Claude Code?** Run `/start` for guided setup.

**Without Claude Code?** Open [`Note - Welcome to MeKB.md`](Note%20-%20Welcome%20to%20MeKB.md) and follow the checklist.

## What You Get

```
MeKB/
├── Daily/              # Daily journal notes
├── Templates/          # 11 note templates
├── Archive/            # Completed/old content
├── .claude/skills/     # 36 AI-powered skills
├── scripts/            # 12 production Python scripts
│   └── tests/          # 236 tests across 12 test files
├── .github/workflows/  # CI pipeline (7 parallel jobs)
├── CLAUDE.md           # AI assistant instructions
├── CHANGELOG.md        # Version history
├── SOUL.md             # Project philosophy
└── *.md                # Your notes (root directory)
```

**11 Note Types:** Daily, Note, Concept, Task, Project, Meeting, Person, Resource, Decision, ActionItem, Interaction

**36 Skills:** Capture, discover, review, automate, and maintain your knowledge

**12 Scripts:** Search, graph, site generation, notifications, scheduling — zero external dependencies

## Tool Compatibility

Works with any text editor. Enhanced experience with:

| Tool            | Enhancement                               |
| --------------- | ----------------------------------------- |
| **Obsidian**    | Graph view, backlinks, templates, plugins |
| **Claude Code** | AI assistance, automation, skills         |
| **VS Code**     | Foam extension, wiki-links                |
| **Any editor**  | Just works - it's plain text              |

## Note Types

### Core Types (Personal)

| Type         | Purpose                      | Example                          |
| ------------ | ---------------------------- | -------------------------------- |
| **Daily**    | Daily journal and capture    | `Daily/2026/2026-02-04.md`       |
| **Note**     | General knowledge            | `Note - How to learn.md`         |
| **Concept**  | Definitions ("What is X?")   | `Concept - Event Sourcing.md`    |
| **Task**     | Things to do                 | `Task - Review docs.md`          |
| **Project**  | Multi-task initiatives       | `Project - Website Redesign.md`  |
| **Meeting**  | Meeting notes                | `Meeting - 2026-02-04 Sprint.md` |
| **Person**   | People (CRM features)        | `Person - Jane Smith.md`         |
| **Resource** | Links, books, videos         | `Resource - DDIA Book.md`        |

### Professional Types

| Type            | Purpose                       | Example                              |
| --------------- | ----------------------------- | ------------------------------------ |
| **Decision**    | Track decisions with context  | `Decision - API Strategy.md`         |
| **ActionItem**  | Meeting actions with owners   | `ActionItem - Send proposal.md`      |
| **Interaction** | Log conversations/meetings    | `Interaction - 2026-02-04 Jane.md`   |

## Skills (Claude Code)

### Capture

| Skill              | Purpose                      |
| ------------------ | ---------------------------- |
| `/daily`           | Create today's daily note    |
| `/note <title>`    | Create knowledge note        |
| `/concept <title>` | Create concept definition    |
| `/meeting <title>` | Create meeting note          |
| `/task <title>`    | Quick-create task            |
| `/person <name>`   | Create person note           |
| `/weblink <url>`   | Save URL with summary        |
| `/clip <url>`      | Web clipper (YouTube, etc.)  |
| `/voice`           | Voice note transcription     |

### Discover

| Skill              | Purpose                      |
| ------------------ | ---------------------------- |
| `/q <term>`        | Keyword search               |
| `/search <query>`  | Semantic search by meaning   |
| `/ask <question>`  | AI-powered vault Q&A         |
| `/recent`          | Recently modified notes      |
| `/related <topic>` | Find connected notes         |
| `/suggest`         | AI-powered link suggestions  |
| `/graph`           | Explore note connections     |
| `/connections`     | Deep relationship analysis   |
| `/browse <url>`    | Fetch and extract web content|

### Review & Reflect

| Skill      | Purpose                              |
| ---------- | ------------------------------------ |
| `/review`  | Spaced repetition - resurface notes  |
| `/weekly`  | Generate weekly summary              |
| `/stale`   | Find notes needing verification      |
| `/session` | Session summary and handoff          |

### Relationships (CRM)

| Skill               | Purpose                     |
| ------------------- | --------------------------- |
| `/people`           | Network dashboard           |
| `/people reconnect` | Who to reach out to         |
| `/people met <name>`| Log an interaction          |
| `/people search`    | Find by expertise           |

### Productivity

| Skill       | Purpose                     |
| ----------- | --------------------------- |
| `/habits`   | Track daily habits          |
| `/export`   | Export for sharing          |
| `/calendar` | Calendar integration        |
| `/readwise`  | Readwise sync              |

### Automation & Dev

| Skill        | Purpose                            |
| ------------ | ---------------------------------- |
| `/automate`  | Create automation workflows        |
| `/dev`       | Developer tools and utilities      |
| `/notify`    | Send notifications (Slack, etc.)   |
| `/schedule`  | Manage scheduled jobs              |
| `/site`      | Generate static HTML site          |

### Maintenance

| Skill       | Purpose                     |
| ----------- | --------------------------- |
| `/health`   | Vault health check          |
| `/orphans`  | Find unlinked notes         |
| `/classify` | Manage security levels      |
| `/start`    | Guided onboarding           |

## Production Scripts

12 Python scripts power search, automation, and maintenance. All use Python 3.9+ stdlib only — no `pip install` required for core functionality.

| Script | Purpose |
|--------|---------|
| `build-index.py` | SQLite FTS5 search index |
| `build-graph.py` | Knowledge graph with traversal |
| `build-embeddings.py` | Vector embeddings for semantic search |
| `search.py` | Hybrid search (BM25 + vector + graph) |
| `build-site.py` | Static HTML site generator |
| `browse.py` | Web content fetcher/extractor |
| `notify.py` | Multi-backend notifications |
| `schedule.py` | Job scheduling (launchd/cron) |
| `stale-check.py` | Find notes needing review |
| `webhook-server.py` | HTTP API for remote operations |
| `skill-tools.py` | Skill management utilities |
| `detect-secrets.py` | Pre-commit secret scanner |

See [scripts/README.md](scripts/README.md) for full documentation.

## The Basics

### Create a Note

```bash
# Copy a template
cp Templates/Note.md "Note - My idea.md"

# Edit the frontmatter and content
```

### Link Notes Together

```markdown
This relates to [[Note - My other note]].
Met with [[Person - Jane Smith]] about [[Project - Website]].
```

### Find Anything

- **Obsidian:** Ctrl/Cmd+O (quick open) or Ctrl/Cmd+Shift+F (search)
- **Claude Code:** `/q search term`
- **Terminal:** `python3 scripts/search.py "search term"`

## Key Features

### Knowledge Compounding

MeKB helps your knowledge grow over time:

- **Spaced repetition** (`/review`) - Resurface old notes for reflection
- **Weekly summaries** (`/weekly`) - See what you captured and themes that emerged
- **Link suggestions** (`/suggest`) - AI finds connections you missed
- **Freshness tracking** - Know when notes need updating

### Relationship Management (CRM)

Track your professional network:

- **Contact frequency** - Set how often to reach out
- **Follow-up reminders** - Never forget to reconnect
- **Expertise tagging** - Find the right person for help
- **Interaction logging** - Record meetings, calls, emails

### Quality Tracking

Optional fields to track knowledge health:

```yaml
verified: 2026-02-04    # Last reviewed
freshness: current      # current | recent | stale
confidence: high        # high | medium | low
```

Run `/stale` to find notes needing attention.

## Testing & CI

MeKB includes a comprehensive test suite and CI pipeline:

- **236 tests** across 12 test files (~80% coverage)
- **7 parallel CI jobs** via GitHub Actions on every push/PR
- **~0.28s** total test runtime — fast feedback
- **Dual runner support** — pytest (preferred) with unittest fallback

```bash
python3 -m pytest scripts/tests/ -v          # Run all tests
python3 -m unittest discover scripts/tests/  # Without pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for test development guidelines.

## Security

MeKB includes optional security features:

- **Classification:** Mark notes as `public`, `personal`, `confidential`, or `secret`
- **AI access control:** Protect sensitive files from AI assistants
- **Secret detection:** Pre-commit hook blocks accidental credential commits

Run `./scripts/setup-security.sh` to enable. See [SECURITY.md](SECURITY.md) for details.

**Golden rule:** Never store passwords in notes. Use a password manager.

## Portability

### Import From

- **Notion:** Export as Markdown, add frontmatter, convert links
- **Roam:** Export as Markdown, add frontmatter (links already work)
- **Apple Notes:** Export, add frontmatter, convert formatting

### Export To

Just copy the folder. It's portable markdown.

## Contributing

MeKB is a template. Fork it, make it yours. Share improvements via pull request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and [TOOLS.md](TOOLS.md) for the full tooling reference.

## Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | AI assistant instructions — note types, frontmatter schema, skills reference |
| [TOOLS.md](TOOLS.md) | Complete tooling reference — all scripts, skills, search tiers, CI |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development guidelines — tests, PR checklist, adding scripts/skills |
| [SECURITY.md](SECURITY.md) | Security features — classification, access control, secret detection |
| [SOUL.md](SOUL.md) | Project philosophy and design principles |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [scripts/README.md](scripts/README.md) | Detailed documentation for all 12 production scripts |

## License

MIT - Do whatever you want with it.

---

**Start simple. Link liberally. Let knowledge compound.**
