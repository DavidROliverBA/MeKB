# /related

Find notes connected to a topic.

## Usage

```
/related <topic>
```

## Instructions

1. Parse topic from command
2. Find all notes that:
   - Contain the topic in filename
   - Contain the topic in content
   - Link to notes containing the topic
   - Are linked FROM notes containing the topic
3. Build a connection map showing:
   - Direct matches
   - Notes that link to matches
   - Notes that matches link to
4. Display as grouped list

## Example

```
/related authentication
```

**Direct matches:**

- Note - OAuth implementation.md
- Concept - API security.md

**Links to these:**

- Project - Website redesign.md

**These link to:**

- Person - Security team lead.md
