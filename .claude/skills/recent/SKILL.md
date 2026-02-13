---
name: recent
---

# /recent

Show recently modified notes.

## Usage

```
/recent
/recent 20
```

## Instructions

1. Parse optional count (default: 10)
2. List all `.md` files sorted by modification time (newest first)
3. Exclude:
   - Files in `.obsidian/`
   - Files in `.claude/`
   - Files in `Templates/`
4. Display as table:
   - Filename
   - Type (from frontmatter)
   - Modified date/time
5. Limit to requested count

## Example

```
/recent
```

| Note                     | Type  | Modified    |
| ------------------------ | ----- | ----------- |
| Note - My idea.md        | Note  | 2 hours ago |
| Daily/2026/2026-02-04.md | Daily | 3 hours ago |
