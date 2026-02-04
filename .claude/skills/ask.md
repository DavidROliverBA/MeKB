# /ask

Ask questions about your vault and get AI-powered answers.

## When to Use

- User wants to query their knowledge base
- Questions like "What do I know about X?", "Summarise my notes on Y"
- Finding insights across multiple notes

## Instructions

### Basic Usage

```
/ask What do I know about Kubernetes?
/ask Summarise my meetings from last week
/ask Who should I talk to about API design?
```

### Step 1: Understand the Question

Parse the question to determine:
- **Topic query** - "What do I know about X?"
- **Summary query** - "Summarise my notes on X"
- **People query** - "Who knows about X?"
- **Decision query** - "What decisions have I made about X?"
- **Timeline query** - "What happened with X?"

### Step 2: Search Relevant Notes

Use multiple search strategies:

1. **Keyword search** - Find notes mentioning key terms
2. **Type filter** - Filter by note type if relevant
3. **Time filter** - Filter by date if temporal
4. **People filter** - Filter by person if relational

### Step 3: Synthesise Answer

Read the relevant notes and synthesise:
- Direct answer to the question
- Supporting evidence from notes
- Links to source notes
- Gaps in knowledge (what you don't have notes on)

### Step 4: Format Response

```markdown
## Answer

[Synthesised answer based on your notes]

## Sources

- [[Note - Relevant Note 1]] - [brief context]
- [[Note - Relevant Note 2]] - [brief context]

## Related Questions

- Have you considered...?
- You might also want to know...

## Knowledge Gaps

- No notes found about [subtopic]
- Consider creating a note on [suggestion]
```

### Examples

**Topic query:**
```
User: /ask What do I know about event sourcing?

Claude: Based on your notes:

## Answer

Event sourcing is a pattern where state changes are stored as a 
sequence of events rather than just current state. You've noted 
it's useful for audit trails and temporal queries, but adds 
complexity.

## Sources
- [[Concept - Event Sourcing]] - Your definition and notes
- [[Decision - Cloud Provider Selection]] - Mentioned as option for AWS

## Related
- You might want to explore CQRS (often paired with event sourcing)
```

**People query:**
```
User: /ask Who should I talk to about Kubernetes?

Claude: Based on your People notes:

## Answer

**[[Person - Sarah Chen]]** is your best contact for Kubernetes.
- Expertise: distributed-systems, kubernetes, golang
- Relationship: colleague, monthly contact
- Last contact: 2026-02-04

## Related Notes
- [[Meeting - 2026-01-10 Sprint Planning]] - Sarah mentioned
```

### Tips

- Be specific in your questions for better answers
- Follow up with more specific questions
- Create notes for topics where you have gaps
- Use `/ask` to prepare for meetings
