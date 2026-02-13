# /suggest

Get AI-powered suggestions for linking the current note to related content.

## When to Use

- After creating a new note
- When a note feels isolated
- User says "what should I link to", "find related notes", "suggest connections"

## Instructions

### Step 1: Analyse Current Note

Read the current note (or specified note) and extract:
- Main topics and concepts
- People mentioned
- Projects referenced
- Key terms and phrases
- Existing links

### Step 2: Find Related Notes

Search vault for notes that:
- Share similar topics
- Mention same people
- Are part of same project
- Have semantic similarity
- Could provide context

### Step 3: Rank Suggestions

Order by relevance:
1. **Direct relevance** - Same topic, should definitely link
2. **Contextual** - Related concept, adds depth
3. **Tangential** - Loosely related, optional link
4. **People connections** - Same person mentioned

### Step 4: Present Suggestions

```markdown
## Link Suggestions for [[Note - API Design Principles]]

### Strong Matches (you should link these)
- [[Decision - REST vs GraphQL]] - directly related decision
- [[Concept - API Versioning]] - complementary concept
- [[Meeting - 2026-01-20 API Review]] - discussed these principles

### Contextual (consider linking)
- [[Note - Microservices Architecture]] - broader context
- [[Person - Jane Smith]] - mentioned as API lead
- [[Project - Platform Modernisation]] - where these apply

### This note could link FROM:
These notes might benefit from linking to this one:
- [[Note - Backend Development Standards]]
- [[Meeting - 2026-01-15 Tech Debt Review]]

### Suggested tags to add:
- api
- architecture
- design-patterns
```

### Step 5: Offer Actions

- **Add link** - Insert `[[Note Title]]` at cursor or end
- **Add backlink** - Add link from suggested note TO current note
- **Add all strong matches** - Bulk add the top suggestions
- **Skip** - No changes

### Options

```
/suggest                    # Suggest links for current note
/suggest "Note - Title"     # Suggest for specific note
/suggest --orphans          # Find orphan notes and suggest links
/suggest --batch            # Run on all recent notes
```

### Auto-Suggest Mode

Can be enabled to run automatically:
- After creating a new note
- When opening a note with no links
- During weekly review

### Suggestion Logic

Notes are considered related if they:
1. Share 2+ tags
2. Mention same `[[Person]]` or `[[Project]]`
3. Have overlapping key terms (>30% overlap)
4. Are in same folder/type
5. Were created around same time
6. Have semantic similarity >70%

### Tips

- Accept strong matches without overthinking
- Contextual links add depth but aren't required
- Review suggestions weekly for new connections
- Use `/orphans` first, then `/suggest` for each
- The more links, the more valuable your graph
