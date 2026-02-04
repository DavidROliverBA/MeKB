# /health

Quick vault health check.

## Usage

```
/health
```

## Instructions

1. Count notes by type (from frontmatter)
2. Find notes missing required frontmatter (`type`, `title`)
3. Count orphan notes (no incoming or outgoing links)
4. Check for broken links (links to non-existent notes)
5. Display summary:

## Example Output

```
Vault Health Check
==================

Notes by type:
- Daily: 45
- Note: 23
- Task: 12
- Person: 8
- Meeting: 6
- Concept: 4
- Resource: 3
- Project: 2

Total: 103 notes

Issues:
- 3 notes missing frontmatter type
- 7 orphan notes (no links)
- 2 broken links

Run /orphans to see unlinked notes.
```
