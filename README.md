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

**Without Claude Code?** Open `Note - Welcome to MeKB.md` and follow the checklist.

## What You Get

```
MeKB/
├── Daily/           # Daily journal notes
├── Templates/       # 11 note templates
├── Archive/         # Completed/old content
├── .claude/skills/  # 24 AI-powered skills
├── CLAUDE.md        # AI assistant instructions
└── *.md             # Your notes (root directory)
```

**11 Note Types:** Daily, Note, Concept, Task, Project, Meeting, Person, Resource, Decision, ActionItem, Interaction

**28 Skills:** Capture, discover, review, and maintain your knowledge

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

### Review & Reflect

| Skill     | Purpose                              |
| --------- | ------------------------------------ |
| `/review` | Spaced repetition - resurface notes  |
| `/weekly` | Generate weekly summary              |
| `/stale`  | Find notes needing verification      |

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

### Maintenance

| Skill       | Purpose                     |
| ----------- | --------------------------- |
| `/health`   | Vault health check          |
| `/orphans`  | Find unlinked notes         |
| `/classify` | Manage security levels      |
| `/start`    | Guided onboarding           |

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
- **Terminal:** `grep -r "search term" *.md`

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

## License

MIT - Do whatever you want with it.

---

**Start simple. Link liberally. Let knowledge compound.**
