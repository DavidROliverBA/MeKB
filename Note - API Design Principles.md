---
type: Note
title: API Design Principles
created: 2025-12-15
tags: [topic/api, topic/architecture]
verified: 2025-12-15
---

# API Design Principles

Core principles I've learned about designing good APIs.

## Key Ideas

1. **Resource-oriented** - Use nouns, not verbs. `/users/123` not `/getUser?id=123`
2. **Consistent naming** - Pick a convention and stick to it
3. **Versioning from day one** - `/v1/users` saves pain later
4. **Meaningful status codes** - 201 for created, 404 for not found, 422 for validation errors

## Questions

- When should I use GraphQL vs REST?
- How to handle pagination consistently?

## Related

- [[Decision - Cloud Provider Selection]] - APIs hosted on AWS API Gateway
- [[Meeting - 2026-01-10 Sprint Planning]] - API gateway work planned
- [[Resource - Designing Data-Intensive Applications]] - API design patterns
- [[Person - Sarah Chen]] - Discussed API patterns over coffee
