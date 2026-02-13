---
name: orphans
---

# /orphans

Find notes with no links.

## Usage

```
/orphans
```

## Instructions

1. Scan all `.md` files for wiki-links `[[...]]`
2. Build a map of:
   - Outgoing links (links in the note)
   - Incoming links (links to the note)
3. Find notes with zero incoming AND zero outgoing links
4. Exclude:
   - Templates
   - CLAUDE.md, README.md
   - Daily notes (these are often standalone)
5. Display list of orphan notes

## Example Output

```
Orphan Notes (no links in or out)
=================================

- Note - Random thought.md
- Person - Old contact.md
- Task - Forgotten task.md

Consider:
- Linking these to related notes
- Archiving if no longer relevant
- Deleting if not useful
```
