# /session

Track and recall what happened during this working session.

## When to Use

- User says "what did I work on", "session summary", "what happened"
- At start of session to resume context from last time
- Before `/wipe` or context compaction to preserve state

## Usage

```
/session                # Show current session summary
/session save           # Save session state to disk
/session last           # Show last saved session
```

## Instructions

### Session Tracking

Throughout the conversation, mentally track:
- **Notes created** - any new files created
- **Notes read** - files the user asked about or you read
- **Notes modified** - files that were edited
- **Queries** - search terms used
- **Topics** - main themes discussed
- **Decisions** - any decisions made

### /session (Show Current)

Summarise the current session:

```markdown
## Current Session

**Started:** ~[estimate based on first message]
**Duration:** ~[estimate]

### Notes Created (3)
- [[Note - API Patterns]] - new knowledge note
- [[Task - Review Auth]] - new task
- [[Meeting - 2026-02-06 Sprint]] - meeting notes

### Notes Read (5)
- [[Concept - Event Sourcing]] - reviewed via /review
- [[Person - Sarah Chen]] - checked contact info
- ...

### Notes Modified (1)
- [[Daily/2026/2026-02-06.md]] - added links

### Queries
- "event sourcing" (found 8 results)
- "API design" (found 3 results)

### Topics
- Architecture patterns
- API design principles
- Sprint planning

### Decisions
- Chose AWS over Azure for event streaming
```

### /session save

Save session state to `.mekb/sessions/` as a YAML file:

```yaml
# .mekb/sessions/2026-02-06T19-30.yaml
date: 2026-02-06
started: "19:30"
notes_created:
  - path: "Note - API Patterns.md"
    type: Note
  - path: "Task - Review Auth.md"
    type: Task
notes_read:
  - "Concept - Event Sourcing.md"
  - "Person - Sarah Chen.md"
notes_modified:
  - "Daily/2026/2026-02-06.md"
queries:
  - term: "event sourcing"
    results: 8
  - term: "API design"
    results: 3
topics:
  - architecture patterns
  - API design
  - sprint planning
decisions:
  - "Chose AWS for event streaming"
```

1. Create `.mekb/sessions/` directory if it doesn't exist
2. Write YAML file with timestamp filename
3. Confirm save location

### /session last

1. Find most recent file in `.mekb/sessions/`
2. Read and display it as a summary
3. Offer to continue where you left off

## Storage

- **Location:** `.mekb/sessions/` (gitignored)
- **Format:** YAML files with ISO timestamp names
- **Retention:** Keep last 30 sessions, auto-clean older ones

## Notes

- Session files are gitignored - they're local working state
- This is a lightweight alternative to full conversation logging
- Useful for context recovery after `/wipe` or new sessions
- The AI tracks session state in memory; `/session save` persists it
