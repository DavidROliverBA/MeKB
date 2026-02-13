# /note

Create a knowledge note.

## Usage

```
/note <title>
```

## Instructions

1. Parse title from command
2. Get today's date
3. Create `Note - <title>.md` from `Templates/Note.md`:
   - Replace `{{title}}` with provided title
   - Replace `{{date}}` with today's date
4. Confirm: "Created [[Note - <title>]]"

## Example

```
/note How to learn effectively
```

Creates `Note - How to learn effectively.md`
