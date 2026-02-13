---
name: person
---

# /person

Create a person note.

## Usage

```
/person <name>
```

## Instructions

1. Parse name from command
2. Get today's date
3. Create `Person - <name>.md` from `Templates/Person.md`:
   - Replace `{{name}}` with provided name
   - Replace `{{date}}` with today's date
4. Confirm: "Created [[Person - <name>]]"

## Example

```
/person Jane Smith
```

Creates `Person - Jane Smith.md`
