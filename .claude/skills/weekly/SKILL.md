---
name: weekly
---

# /weekly

Generate a weekly review summarising what you captured and learned.

## When to Use

- End of week reflection (Friday/Sunday)
- User says "weekly review", "what did I do this week", "summarise my week"

## Instructions

### Step 1: Gather This Week's Content

Find all notes created or modified in the last 7 days:
- Daily notes from this week
- New notes created
- Notes modified (updated content)
- Tasks completed
- Meetings held

### Step 2: Generate Statistics

Count and categorise:
- Total notes created
- By type (Note, Task, Meeting, Person, etc.)
- Tasks completed vs created
- People mentioned/created
- Topics/tags used

### Step 3: Identify Themes

Analyse the week's notes for:
- Most mentioned topics
- Frequently linked notes
- Emerging patterns
- Decisions made

### Step 4: Find Orphans

Check for notes created this week with:
- No outgoing links
- No incoming links (backlinks)
- Suggest connections

### Step 5: Generate Weekly Note

Create `Daily/YYYY/Week-WW-Review.md` with:

```markdown
---
type: Daily
title: Week {{week_number}} Review
created: {{date}}
tags: [weekly-review]
---

# Week {{week_number}} Review ({{start_date}} - {{end_date}})

## Summary

- **Notes created:** X
- **Tasks completed:** Y of Z
- **Meetings:** N
- **People added:** P

## What I Captured

### New Notes
- [[Note - Title 1]]
- [[Note - Title 2]]

### Meetings
- [[Meeting - Date Title]]

### Tasks Completed
- [x] [[Task - Completed task]]

## Themes This Week

Based on your notes, you focused on:
1. **Theme 1** - mentioned in X notes
2. **Theme 2** - mentioned in Y notes

## Orphan Notes (Need Links)

These notes have no connections:
- [[Note - Orphan 1]] - consider linking to...
- [[Note - Orphan 2]]

## Reflection Prompts

- What was the most valuable thing I learned?
- What should I explore further?
- What can I let go of?

## Next Week

- [ ] Key focus for next week
- [ ] Follow up on...
```

### Step 6: Prompt User

Ask:
- "Anything to add to your weekly reflection?"
- "Any notes to archive from this week?"

## Example

```
User: /weekly

Claude: Here's your Week 5 review...

## Summary
- 12 notes created (4 Notes, 3 Meetings, 2 Tasks, 2 People, 1 Decision)
- 5 of 7 tasks completed
- Main themes: cloud migration, API design

## Orphans Needing Links
- [[Note - Kubernetes Basics]] - no links, consider connecting to [[Note - Cloud Architecture]]

Created: Daily/2026/Week-05-Review.md
```
