# /search

Semantic search - find notes by meaning, not just keywords.

## When to Use

- Finding notes when you don't remember exact words
- Exploring related concepts
- User asks "find notes about X" where X is a concept

## How It Works

Traditional search (`/q`): Finds exact keyword matches
Semantic search (`/search`): Finds conceptually similar content

Example:
- `/q authentication` → Notes containing "authentication"
- `/search how do users log in` → Notes about auth, login, SSO, sessions, etc.

## Instructions

### Prerequisites

Semantic search requires embeddings. Options:

1. **Claude API** (Recommended)
   - Uses Claude to understand query meaning
   - No separate embedding index needed
   - Set `ANTHROPIC_API_KEY`

2. **OpenAI Embeddings**
   - Requires pre-built embedding index
   - Set `OPENAI_API_KEY`
   - Run `scripts/build-embeddings.js` first

3. **Local Embeddings**
   - Use Ollama with embedding model
   - Privacy-focused, no data sent externally

### Option 1: Claude-Powered Search (No Index)

Use Claude to:
1. Understand the user's query intent
2. Generate likely keywords and synonyms
3. Search vault with expanded terms
4. Rank results by relevance
5. Explain why each result matches

### Option 2: Embedding Index Search

Pre-compute embeddings:
```bash
node scripts/build-embeddings.js
```

This creates `.mekb/embeddings.json` with vector for each note.

Search flow:
1. Embed the query
2. Find notes with highest cosine similarity
3. Return top 10 results with similarity scores

### Skill Flow

```
User: /search how do we handle distributed events

Claude: Searching by meaning...

## Results (5 matches)

### 1. Note - Event-Driven Architecture (92% match)
> Systems communicate through events rather than direct calls...
Why: Directly discusses event handling patterns

### 2. Decision - Kafka vs RabbitMQ (87% match)
> We chose Kafka for high-throughput event streaming...
Why: Covers distributed event technology choice

### 3. Meeting - 2026-01-15 Integration Review (78% match)
> Discussed async messaging between services...
Why: Contains discussion of event-based integration

### 4. Concept - CQRS Pattern (71% match)
> Command Query Responsibility Segregation separates...
Why: Related pattern often used with events

### 5. Resource - Designing Event-Driven Systems (68% match)
> O'Reilly book on event-driven architecture...
Why: External resource on the topic

Would you like to:
1. Open a specific note?
2. Find more results?
3. Create a new note linking these?
```

### Search Options

```
/search <query>              # Semantic search
/search <query> --type Note  # Filter by type
/search <query> --limit 20   # More results
/search <query> --explain    # Detailed match reasoning
```

### Building the Index

```bash
# Build embedding index (run periodically)
node scripts/build-embeddings.js

# Index stats
node scripts/build-embeddings.js --stats

# Rebuild specific notes
node scripts/build-embeddings.js --rebuild "Note - Topic.md"
```

### Comparison: /q vs /search

| Feature | /q (keyword) | /search (semantic) |
|---------|--------------|-------------------|
| Speed | Fast | Slower |
| Precision | Exact match | Fuzzy match |
| Recall | Low | High |
| Use case | Known terms | Exploration |

### Tips

- Use `/q` when you know the exact term
- Use `/search` when exploring or can't remember words
- Combine: `/search` to explore, `/q` to narrow down
- Rebuild embeddings weekly for new notes
