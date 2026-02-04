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

## Example

```
/daily
```

Creates `Daily/2026/2026-02-04.md`
