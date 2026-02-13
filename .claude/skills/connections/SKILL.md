---
name: connections
---

# /connections

Explore typed relationships between notes in your knowledge graph.

## Usage

```
/connections [[Note - Title]]         # Show all connections for a note
/connections types                     # List all relationship types in vault
/connections path [[A]] [[B]]         # Find shortest path between notes
/connections common [[A]] [[B]]       # Find common connections
```

## Instructions

### Prerequisites

If `.mekb/graph.json` exists, use it for fast lookups:

```bash
python3 scripts/build-graph.py        # Build/rebuild graph
```

If no graph exists, scan the vault at runtime (slower but works).

### /connections [[Note]]

Show all connections for a specific note:

```markdown
## Connections for [[Concept - Event Sourcing]]

### Typed Relationships
- **depends-on:** [[Decision - Cloud Provider Selection]] - platform choice
- **supports:** [[Note - API Design Principles]] - async pattern

### Incoming Links (6)
- [[Resource - Designing Data-Intensive Applications]] - Chapter 11
- [[Person - Sarah Chen]] - expertise area
- [[Daily/2026/2026-02-04]] - reviewed
- [[Decision - Cloud Provider Selection]] - mentioned
- [[Daily/2026/Week-06-Review]] - weekly theme
- [[Resource - Why You Should Take Notes If You Use AI]] - related

### Outgoing Links (1)
- [[Resource - Designing Data-Intensive Applications]]

### Suggested Connections
- [[Concept - CQRS]] - often paired pattern (not linked yet)
```

**Implementation:**

1. Load graph from `.mekb/graph.json` or scan vault
2. Find the note in the graph
3. Separate typed relationships from plain wiki-links
4. List incoming links (backlinks)
5. List outgoing links
6. Suggest potential connections (notes sharing 2+ common neighbours)

### /connections types

List all typed relationships in the vault:

```markdown
## Relationship Types in Vault

| Type | Count | Example |
|------|-------|---------|
| references | 12 | Event Sourcing -> DDIA |
| depends-on | 5 | Cloud Selection -> Platform |
| supersedes | 2 | New API -> Old API |
| supports | 3 | Events -> API Design |
```

**Supported types:**
- `references` - General mention/link
- `depends-on` - Requires this to exist
- `supersedes` - Replaces this
- `contradicts` - Conflicts with
- `supports` - Evidence for
- `implements` - Realises
- `extends` - Builds upon
- `inspired-by` - Creative influence

### /connections path [[A]] [[B]]

Find the shortest path between two notes:

```bash
python3 scripts/build-graph.py --path "Note A" "Note B"
```

```markdown
## Path: [[Concept - Event Sourcing]] -> [[Meeting - Sprint Planning]]

2 hops:
1. [[Concept - Event Sourcing]]
2. [[Decision - Cloud Provider Selection]]
3. [[Meeting - Sprint Planning]]
```

### /connections common [[A]] [[B]]

Find notes that link to both A and B:

```markdown
## Common Connections

[[Person - Sarah Chen]] and [[Concept - Event Sourcing]] share 3 connections:
- [[Decision - Cloud Provider Selection]]
- [[Resource - Designing Data-Intensive Applications]]
- [[Meeting - 2026-01-10 Sprint Planning]]
```

### Adding Typed Relationships

Add a `relationships` section to note frontmatter:

```yaml
relationships:
  depends-on: ["[[Decision - Cloud Provider Selection]]"]
  references: ["[[Concept - Event Sourcing]]"]
  extends: ["[[Pattern - Event-Driven Architecture]]"]
```

Then rebuild the graph: `python3 scripts/build-graph.py`

## Tips

- Run `python3 scripts/build-graph.py --hubs` to find your most connected notes
- Run `python3 scripts/build-graph.py --orphans` to find isolated notes
- Typed relationships are optional but add semantic meaning to connections
- Use `/connections` before writing a new note to find related content
