# /people

Manage relationships and track interactions with people in your network.

## When to Use

- Reviewing your professional network
- Finding someone to help with a topic
- Checking who you haven't contacted recently
- User says "who do I know", "relationship management", "reconnect"

## Commands

```
/people                    # Dashboard overview
/people list               # All people in vault
/people search <topic>     # Find people by expertise
/people reconnect          # People you should reach out to
/people met <name>         # Log an interaction
/people add <name>         # Create new person note
```

## Instructions

### /people (Dashboard)

Show relationship overview:

```markdown
## Your Network

**Total contacts:** 47
**Strong relationships:** 12
**Need reconnection:** 8

### Recent Interactions
- [[Person - Jane Smith]] - Meeting yesterday
- [[Person - Bob Jones]] - Email 3 days ago
- [[Person - Sarah Wilson]] - Call last week

### Reconnect Soon (no contact in 30+ days)
- [[Person - Mike Chen]] - Last: 45 days ago (monthly frequency)
- [[Person - Lisa Park]] - Last: 62 days ago (monthly frequency)

### Upcoming Follow-ups
- [[Person - Tom Brown]] - Follow up due tomorrow
- [[Person - Amy Lee]] - Follow up due in 3 days

### By Relationship Type
- Colleagues: 23
- Clients: 8
- Vendors: 6
- Mentors: 3
- Friends: 7
```

### /people search <topic>

Find people who can help with a topic:

```
User: /people search kubernetes

Claude: People who might help with kubernetes:

### Has Expertise
- [[Person - Jane Smith]] - expertise: [kubernetes, aws, devops]
- [[Person - Bob Jones]] - expertise: [kubernetes, docker]

### Worked Together On
- [[Person - Mike Chen]] - projects: [[Project - Platform Migration]]

### Mentioned In Notes About
- [[Person - Sarah Wilson]] - mentioned in [[Note - K8s Best Practices]]
```

### /people reconnect

Show people you should reach out to based on:
- `contact_frequency` vs `last_contact`
- `relationship_strength` degradation
- Overdue `next_followup`

```markdown
## Time to Reconnect

### Overdue (past their preferred frequency)
- [[Person - Mike Chen]] 
  - Frequency: monthly, Last: 45 days ago
  - Expertise: cloud architecture
  - Suggestion: "Ask about their AWS migration"

### Relationship Cooling
- [[Person - Tom Brown]]
  - Was: strong, Now: medium (no contact 60 days)
  - Shared: [[Project - API Redesign]]
  - Suggestion: "Share the API article you read"

### Follow-up Due
- [[Person - Amy Lee]]
  - Due: 2026-02-05
  - Context: "Send architecture doc"
```

### /people met <name>

Quick log of an interaction:

```
User: /people met Jane Smith

Claude: Logging interaction with Jane Smith...

What type of interaction?
1. Meeting
2. Call  
3. Email
4. Message
5. Coffee/Lunch

User: Meeting

Claude: Brief summary of the meeting?

User: Discussed Q2 roadmap, she's interested in the AI project

Claude: Updated [[Person - Jane Smith]]:
- last_contact: 2026-02-04
- Added to Interaction Log

Also created: [[Interaction - 2026-02-04 Jane Smith Meeting]]

Any follow-up needed?

User: Send her the AI proposal

Claude: Added follow-up:
- next_followup: 2026-02-11
- Task: "Send AI proposal to Jane"
```

### /people add <name>

Create new Person note with prompts:

```
User: /people add Sarah Connor

Claude: Creating Person note for Sarah Connor...

How do you know Sarah?
1. Colleague (same company)
2. Client
3. Vendor/Partner
4. Friend
5. Met at event
6. Other

User: Colleague

Claude: What's their role?

User: Engineering Manager

Claude: Created: [[Person - Sarah Connor]]
- role: Engineering Manager
- relationship_type: colleague
- met_date: 2026-02-04

Would you like to add:
- Email/contact info?
- Their expertise areas?
- Shared projects?
```

## Relationship Strength Calculation

Automatically calculated based on:
- Interaction frequency
- Recency of contact
- Number of shared projects
- Depth of notes about them

| Factor | Strong | Medium | Weak | Dormant |
|--------|--------|--------|------|---------|
| Last contact | <14 days | <30 days | <90 days | >90 days |
| Interactions/year | >12 | >4 | >1 | 0 |
| Shared projects | >2 | 1 | 0 | 0 |

## Tips

- Update `last_contact` after every meaningful interaction
- Set realistic `contact_frequency` based on relationship
- Use expertise tags to find help later
- Link people to projects they're involved in
- Run `/people reconnect` weekly
