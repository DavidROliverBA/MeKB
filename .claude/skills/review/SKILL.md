---
name: review
---

# /review

Spaced repetition review - surfaces random old notes for reflection.

## When to Use

- Daily practice to compound knowledge
- When you want to reconnect with past ideas
- User says "review notes", "what did I write before", "resurface old notes"

## Instructions

### Step 1: Find Old Notes

Search for notes older than 7 days:
- Use Glob to find all `*.md` files in root and Daily/
- Filter to notes with `type:` in frontmatter (exclude README, CLAUDE.md, etc.)
- Exclude notes modified in last 7 days
- Randomly select 3-5 notes

### Step 2: Present Notes for Review

For each selected note, show:
- Title and type
- Created date and "X days ago"
- First 2-3 lines of content (after frontmatter)
- Link to the full note

### Step 3: Prompt Reflection

Ask the user:
- "Does this still hold true?"
- "Should this be updated, linked to something, or archived?"
- "Any new insights since you wrote this?"

### Step 4: Offer Actions

Provide options:
1. **Mark as verified** - Update `verified: YYYY-MM-DD` in frontmatter
2. **Add to today's daily** - Link the note in today's daily note
3. **Archive** - Move to Archive/ if no longer relevant
4. **Skip** - Move to next note

### Example Output

```
## Daily Review - 3 Notes to Revisit

### 1. Note - API Design Principles (47 days ago)
> REST APIs should be resource-oriented. Use nouns, not verbs...

**Still relevant?** [Verify] [Link to Daily] [Archive] [Skip]

### 2. Concept - Event Sourcing (23 days ago)  
> Store state changes as events rather than current state...

**Still relevant?** [Verify] [Link to Daily] [Archive] [Skip]

### 3. Meeting - 2026-01-15 Architecture Review (20 days ago)
> Discussed migration timeline. Decision: Q2 start...

**Still relevant?** [Verify] [Link to Daily] [Archive] [Skip]
```

## Tips

- Run `/review` daily for best results
- Notes marked as verified won't appear again for 30 days
- The more you review, the better your knowledge compounds
