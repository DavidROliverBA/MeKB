# /readwise

Sync highlights from Readwise into MeKB Resource notes.

## When to Use

- User has Readwise account with highlights
- Syncing reading highlights into vault
- User says "sync readwise", "import highlights", "sync books"

## Instructions

### Prerequisites

1. **Readwise Account** - https://readwise.io
2. **API Token** - Get from https://readwise.io/access_token
3. **Environment Variable**:
   ```bash
   export READWISE_TOKEN="your-token-here"
   ```

### Skill Flow

```
User: /readwise

Claude: Connecting to Readwise...

## Readwise Sync

**Last sync:** 2026-02-01
**New highlights since last sync:** 23

### New Content

**Books:**
- "Thinking in Systems" by Donella Meadows (12 highlights)
- "Staff Engineer" by Will Larson (5 highlights)

**Articles:**
- "How to Build a Second Brain" (4 highlights)
- "Event-Driven Architecture Guide" (2 highlights)

Would you like to:
1. Sync all new highlights
2. Select specific sources
3. Review highlights first
```

### API Integration

```bash
# Fetch highlights since last sync
curl "https://readwise.io/api/v2/highlights/?updated__gt=2026-02-01" \
  -H "Authorization: Token $READWISE_TOKEN"

# Fetch books list
curl "https://readwise.io/api/v2/books/" \
  -H "Authorization: Token $READWISE_TOKEN"
```

### Create Resource Notes

For each book/article, create or update `Resource - {{title}}.md`:

```yaml
---
type: Resource
title: {{book_title}}
created: {{first_highlight_date}}
modified: {{date}}
tags: [readwise, book]
author: {{author}}
source: readwise
readwise_id: {{book_id}}
category: {{category}}  # book, article, podcast, tweet
highlights_count: {{count}}
last_synced: {{date}}
---

# {{book_title}}

**Author:** {{author}}
**Category:** {{category}}
**Highlights:** {{count}}

## Highlights

### {{highlight_text}}
- **Location:** {{location}}
- **Note:** {{my_note}}
- **Highlighted:** {{date}}

---

### {{highlight_text_2}}
...

## My Summary

_Add your synthesis of the key ideas_

## Key Takeaways

1. 
2. 
3. 

## Related

_Link to notes where you've applied these ideas_
```

### Options

```
/readwise                  # Sync new highlights
/readwise full             # Full re-sync
/readwise books            # List synced books
/readwise search <term>    # Search highlights
/readwise status           # Show sync status
```

### Sync Tracking

Store sync state in `.mekb/readwise-sync.json`:
```json
{
  "last_sync": "2026-02-04T10:30:00Z",
  "synced_books": ["id1", "id2"],
  "highlight_count": 456
}
```

### Highlight Processing

For each highlight:
1. Check if Resource note exists for the source
2. If not, create new Resource note
3. Append highlight to the note
4. Preserve any notes/tags added by user

### Tags from Readwise

Map Readwise tags to MeKB tags:
- `.h1` → key idea, prominent display
- User tags → add to frontmatter tags

### Tips

- Sync weekly to keep highlights current
- Add your own notes to synthesise ideas
- Link highlights to projects where they apply
- Use `/search` to find highlights by concept
- Review new highlights in weekly review

### Without Readwise

If user doesn't have Readwise, suggest:
1. Manual highlight entry
2. Kindle export + copy/paste
3. PDF annotation tools
4. Browser extensions like Hypothesis
