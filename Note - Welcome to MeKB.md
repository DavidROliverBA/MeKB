---
type: Note
title: Welcome to MeKB
created: 2026-02-04
tags:
  - getting-started
---

# Welcome to MeKB

Your personal knowledge base starts here. This note will guide you through your first steps.

## Using Claude Code?

Run `/start` for a guided setup that creates personalised notes based on your interests.

```
/start
```

---

## Manual Setup (Any Editor)

If you're using Obsidian, VS Code, or any other editor, follow this checklist:

### Step 1: Your First Daily Note

- [ ] Create folder `Daily/2026/` (use current year)
- [ ] Copy `Templates/Daily.md` to `Daily/2026/2026-02-04.md` (use today's date)
- [ ] Open it and write something - anything! This is your capture surface.

### Step 2: Your First Knowledge Note

- [ ] Think of a topic you're interested in
- [ ] Copy `Templates/Note.md` to root folder
- [ ] Rename to `Note - [Your Topic].md`
- [ ] Fill in the frontmatter and add some initial thoughts

### Step 3: Connect with Links

- [ ] Go back to your daily note
- [ ] Add a link: `[[Note - Your Topic]]`
- [ ] Click the link (in Obsidian) to see the connection

### Step 4: Add a Person

- [ ] Copy `Templates/Person.md` to root
- [ ] Rename to `Person - [Someone You Know].md`
- [ ] Fill in what you know about them
- [ ] Link to them from your daily note: `Met with [[Person - Name]] today`

### Step 5: Explore

- [ ] Try the graph view (Obsidian: click the graph icon)
- [ ] Check backlinks (see what links TO the current note)
- [ ] Search your vault (Ctrl/Cmd+Shift+F)

---

## The Core Idea

**Capture → Connect → Compound**

1. **Capture** everything in daily notes - don't organise yet
2. **Connect** by adding `[[links]]` between related notes
3. **Compound** as connections reveal patterns and insights

## Tips for Success

- **Start messy** - Capture first, organise later
- **Link liberally** - Every `[[link]]` adds value
- **Review weekly** - 15 minutes to link orphan notes
- **One concept = one note** - If you keep writing about X, give it a note

## Quick Reference

| I want to...       | Do this                        |
| ------------------ | ------------------------------ |
| Capture a thought  | Add to today's daily note      |
| Remember a concept | Create a `Note - Title.md`     |
| Track a task       | Create a `Task - Title.md`     |
| Note a meeting     | Create a `Meeting - Title.md`  |
| Remember a person  | Create a `Person - Name.md`    |
| Save a link        | Create a `Resource - Title.md` |
| Find something     | Search (Ctrl/Cmd+Shift+F)      |

## What's in This Vault?

```
MeKB/
├── Daily/           # Your daily journal notes
├── Templates/       # Copy these to create new notes
├── Archive/         # Old/completed content
├── CLAUDE.md        # AI assistant instructions
├── README.md        # Full documentation
└── *.md             # Your notes live in root
```

## Next Steps

1. Complete the checklist above
2. Create daily notes for 3 days in a row
3. Add 5 notes on topics that interest you
4. Delete this note when you're comfortable (or keep it as reference)

---

**Remember:** Your notes are plain markdown. They work in any editor, sync anywhere, and will outlive any tool.

_Happy knowledge building!_
