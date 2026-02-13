---
name: concept
---

# /concept

Create a concept definition note.

## Usage

```
/concept <title>
```

## Instructions

1. Parse title from command
2. Get today's date
3. Create `Concept - <title>.md` from `Templates/Concept.md`:
   - Replace `{{title}}` with provided title
   - Replace `{{date}}` with today's date
4. Confirm: "Created [[Concept - <title>]]"

## Example

```
/concept Personal Knowledge Management
```

Creates `Concept - Personal Knowledge Management.md`
