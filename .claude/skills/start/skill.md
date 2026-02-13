# /start

Guided onboarding for new MeKB users. Creates personalised first notes based on user preferences.

## When to Use

- First time opening MeKB with Claude Code
- User says "get started", "set up", "help me begin"
- User seems new and unsure where to start

## Instructions

### Step 1: Welcome and Gather Information

Use the AskUserQuestion tool to ask the user:

**Question 1: Name**

- "What should I call you?"
- Header: "Your name"
- Options: Let them type freely (use Other)

**Question 2: Primary use case**

- "What will you mainly use MeKB for?"
- Header: "Use case"
- Options:
  - "Work" - Professional notes, projects, meetings
  - "Personal" - Life admin, journals, memories
  - "Learning" - Study notes, courses, research
  - "Creative" - Writing, ideas, projects

**Question 3: First topic**

- "What's one topic you'd like to start capturing notes about?"
- Header: "First topic"
- Options: Let them type freely (use Other)

**Question 4: Example content**

- "Should I keep the example Welcome note or start fresh?"
- Header: "Examples"
- Options:
  - "Keep examples" - Useful reference while learning
  - "Clean slate" - Remove examples, start empty

### Step 2: Generate Personalised Content

Based on their answers, create:

#### 2a. Today's Daily Note

Create `Daily/YYYY/YYYY-MM-DD.md` with personalised welcome:

```markdown
---
type: Daily
title: {{date}}
created: {{date}}
tags: []
---

# {{date}}

## Welcome, {{name}}!

This is your first daily note. It's your capture surface - dump anything here.

### Getting Started Checklist

- [ ] Create a note about {{topic}} using `/note`
- [ ] Add a person you know with `/person`
- [ ] Link something to this note with `[[brackets]]`
- [ ] Try `/q` to search your vault

### Capture

_What's on your mind today?_

### Tasks

- [ ] Complete getting started checklist

### Links

- [[Note - Welcome to MeKB]]
```

#### 2b. Seed Note on Their Topic

Create `Note - {{Topic}}.md`:

```markdown
---
type: Note
title: {{Topic}}
created: {{date}}
tags: [topic/{{topic-slug}}]
---

# {{Topic}}

_Your notes on {{topic}} go here. This is just a starting point._

## Key Ideas

## Questions

- What do I want to learn about {{topic}}?
- What do I already know?

## Resources

_Links, books, videos about {{topic}}_

## Related

- [[Daily/YYYY/YYYY-MM-DD|Today's note]]
```

#### 2c. First Task

Create `Task - Complete MeKB setup.md`:

```markdown
---
type: Task
title: Complete MeKB setup
created: {{date}}
completed: false
due: null
project: null
tags: [getting-started]
---

# Complete MeKB setup

## Checklist

- [ ] Create 3 daily notes this week
- [ ] Add 5 notes on topics that interest you
- [ ] Add at least 2 people you interact with
- [ ] Review and link orphan notes (use `/orphans`)
- [ ] Delete this task when comfortable

## Tips

- Don't overthink it - capture first, organise later
- Link liberally - every `[[link]]` adds value
- Check backlinks to see what references a note

## Related

- [[Note - Welcome to MeKB]]
```

#### 2d. Update Welcome Note (if keeping)

If user chose "Keep examples", personalise the Welcome note:

- Add their name to the greeting
- Reference their first topic
- Add link to their first daily note

If user chose "Clean slate":

- Archive `Note - Welcome to MeKB.md` to `Archive/`

### Step 3: Summary

Tell the user what was created:

```
All set, {{name}}! I've created:

1. **Today's daily note** - Your capture surface
2. **Note - {{Topic}}** - Your first knowledge note
3. **Task - Complete MeKB setup** - Guided checklist

**Next steps:**
- Open your daily note and start capturing
- Use `/note <title>` to create more notes
- Use `/q <search>` to find anything
- Use `/health` to check vault status

Happy knowledge building!
```

## Non-Claude-Code Users

Users without Claude Code can follow the manual checklist in `Note - Welcome to MeKB.md`. The Welcome note includes an interactive getting started section with checkboxes.

## Example Conversation

```
User: /start

Claude: Welcome to MeKB! Let me help you get set up.

[Asks questions via AskUserQuestion]

User: [Answers: "Alex", "Learning", "Machine Learning", "Keep examples"]

Claude: All set, Alex! I've created:

1. **Today's daily note** - Your capture surface
2. **Note - Machine Learning** - Your first knowledge note
3. **Task - Complete MeKB setup** - Guided checklist

Next steps:
- Open your daily note and start capturing
- Use `/note <title>` to create more notes
- Use `/q <search>` to find anything

Happy knowledge building!
```
