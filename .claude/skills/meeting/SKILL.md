---
name: meeting
---

# /meeting

Create a meeting note.

## Usage

```
/meeting <title>
```

## Instructions

1. Parse title from command
2. Get today's date
3. Create `Meeting - <title>.md` from `Templates/Meeting.md`:
   - Replace `{{title}}` with provided title
   - Replace `{{date}}` with today's date
4. Confirm: "Created [[Meeting - <title>]]"

## Example

```
/meeting Team standup
```

Creates `Meeting - Team standup.md`
