---
name: daily
---

# /daily

Create today's daily note.

## Instructions

1. Get today's date in YYYY-MM-DD format
2. Check if `Daily/YYYY/YYYY-MM-DD.md` exists
3. If exists, open it and confirm
4. If not, create it from `Templates/Daily.md`:
   - Replace `{{date}}` with today's date
   - Create in `Daily/YYYY/` folder (create year folder if needed)
5. Confirm: "Created daily note for YYYY-MM-DD"
6. **Yesterday review:** Read yesterday's daily note (calculate the date). Extract any unchecked `- [ ]` items and carry them forward into today's note under a "Carried Forward" section
7. **Overdue task check:** Search for incomplete tasks with past due dates:
   ```bash
   python3 scripts/search.py "completed: false" --type Task 2>/dev/null
   ```
   Filter results by `due` date < today. List any overdue tasks in today's note
8. **Yesterday's summary:** Add a brief "Yesterday" section showing what was completed (checked `- [x]` items) vs what was carried forward

## Example

```
/daily
```

Creates `Daily/2026/2026-02-04.md`
