# /graph

Explore and understand your knowledge graph connections.

## When to Use

- Understanding how notes connect
- Finding central/important notes
- Discovering isolated notes
- User says "show connections", "graph", "how are notes connected"

## Instructions

### Basic Usage

```
/graph                     # Overview of vault connections
/graph [[Note - Title]]    # Show connections for specific note
/graph clusters            # Find note clusters
/graph central             # Find most connected notes
```

### Step 1: Build Connection Map

Scan all notes for:
- Outgoing links: `[[wiki-links]]` in the note
- Incoming links: Other notes that link to this one (backlinks)
- Tags: Shared tags between notes

### Step 2: Calculate Metrics

For each note, calculate:
- **Degree**: Total connections (in + out)
- **In-degree**: Number of backlinks
- **Out-degree**: Number of outgoing links
- **Centrality**: How central to the network

### Step 3: Generate Report

**Vault Overview:**
```markdown
## Knowledge Graph Overview

**Stats:**
- Total notes: 47
- Total connections: 156
- Average connections per note: 3.3
- Orphan notes: 5

### Most Connected Notes (Hubs)
| Note | Connections | Type |
|------|-------------|------|
| [[Person - Sarah Chen]] | 12 | Person |
| [[Project - Website]] | 10 | Project |
| [[Concept - API Design]] | 8 | Concept |

### Isolated Notes (Need Links)
- [[Note - Random Thought]] - 0 connections
- [[Task - Old Task]] - 0 connections

### Clusters
1. **Cloud Architecture** (8 notes)
   - [[Decision - AWS]], [[Note - Lambda]], ...
2. **Team Knowledge** (6 notes)
   - [[Person - Sarah Chen]], [[Meeting - Sprint]]...
```

**Single Note View:**
```markdown
## Connections for [[Concept - Event Sourcing]]

**Incoming Links (3):**
- [[Decision - Cloud Provider]] - "mentioned event sourcing"
- [[Meeting - Architecture Review]] - "discussed pattern"
- [[Resource - DDIA Book]] - "chapter 11 covers this"

**Outgoing Links (2):**
- [[Person - Sarah Chen]] - "recommended by"
- [[Decision - Cloud Provider]] - "relates to"

**Suggested Connections:**
- [[Concept - CQRS]] - often paired (not linked yet)
- [[Project - Data Platform]] - relevant topic
```

### Examples

**Vault overview:**
```
User: /graph

Claude: ## Your Knowledge Graph

📊 **47 notes** with **156 connections**

### Hubs (Most Connected)
1. [[Person - Sarah Chen]] - 12 links (key contact!)
2. [[Project - Website Redesign]] - 10 links
3. [[Concept - API Design]] - 8 links

### Orphans (No Connections)
5 notes have no links:
- [[Note - Quick Thought]]
- [[Task - Review Docs]]

Run `/orphans` to fix these.

### Health Score: 78/100
- Good: Most notes are connected
- Improve: Link orphan notes
- Improve: Add backlinks to key concepts
```

**Specific note:**
```
User: /graph [[Person - Sarah Chen]]

Claude: ## [[Person - Sarah Chen]] - Connection Map

**12 total connections**

← Incoming (8):
- [[Meeting - Sprint Planning]] - attendee
- [[Meeting - Architecture Review]] - attendee
- [[Decision - Cloud Provider]] - decider
- ... 5 more

→ Outgoing (4):
- [[Resource - DDIA Book]] - recommended
- [[Concept - Kubernetes]] - expert in
- [[Organisation - TechCorp]] - works at
- [[Project - API Gateway]] - involved

💡 **Suggestions:**
- Link to [[Concept - Distributed Systems]] (her expertise)
- Add recent interaction note
```

### Visual Options

For Obsidian users:
```
/graph visual [[Note - Title]]
```
Opens the local graph view in Obsidian filtered to that note.

### Tips

- Highly connected notes are your knowledge hubs
- Orphan notes lose value - link them!
- Review `/graph` monthly to find isolated knowledge
- Person notes should link to their projects and expertise
- Concepts should link to decisions that use them
