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
├── Templates/       # Note templates (copy to create)
├── Archive/         # Completed/old content
├── CLAUDE.md        # AI assistant instructions
└── *.md             # Your notes (root directory)
```

**8 Note Types:** Daily, Note, Concept, Task, Project, Meeting, Person, Resource

**13 Skills:** `/daily`, `/meeting`, `/task`, `/note`, `/person`, `/weblink`, `/concept`, `/q`, `/recent`, `/related`, `/health`, `/orphans`, `/classify`

## Tool Compatibility

Works with any text editor. Enhanced experience with:

| Tool            | Enhancement                               |
| --------------- | ----------------------------------------- |
| **Obsidian**    | Graph view, backlinks, templates, plugins |
| **Claude Code** | AI assistance, automation, skills         |
| **VS Code**     | Foam extension, wiki-links                |
| **Any editor**  | Just works - it's plain text              |

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
