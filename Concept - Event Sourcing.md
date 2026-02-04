---
type: Concept
title: Event Sourcing
created: 2025-11-28
tags: [topic/architecture, topic/patterns]
verified: 2025-11-28
---

# Event Sourcing

A pattern where state changes are stored as a sequence of events rather than just the current state.

## Definition

Instead of storing: `balance: 100`

Store the events:
- `AccountOpened { initial: 0 }`
- `Deposited { amount: 150 }`
- `Withdrew { amount: 50 }`

Current state is derived by replaying events.

## Benefits

- Complete audit trail
- Can reconstruct state at any point in time
- Natural fit for event-driven systems
- Enables temporal queries

## Drawbacks

- More complex to implement
- Eventual consistency challenges
- Storage can grow large
- Querying current state requires projection

## When to Use

- Financial systems (audit requirements)
- Collaborative editing
- Systems needing full history
- CQRS architectures

## Related

- [[Decision - Cloud Provider Selection]]
