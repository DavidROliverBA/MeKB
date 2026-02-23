# Quality Patterns

Patterns for maintaining note quality and relationships in MeKB.

## Quality Indicators

Add to Concepts, Decisions, Projects, and Resources for content quality tracking:

```yaml
confidence: high | medium | low
freshness: current | recent | stale
source: primary | secondary | synthesis
verified: true | false
reviewed: YYYY-MM-DD
keywords: []
summary: <one-line summary>
```

### Confidence Levels

| Level    | When to Use                                |
| -------- | ------------------------------------------ |
| `high`   | Authoritative, well-researched, definitive |
| `medium` | Good information but some uncertainty      |
| `low`    | Preliminary, needs verification            |

### Freshness Levels

| Level     | Timeframe                  |
| --------- | -------------------------- |
| `current` | Reviewed within 3 months   |
| `recent`  | Reviewed 3-12 months ago   |
| `stale`   | Not reviewed in >12 months |

### Source Types

| Type        | Meaning                              |
| ----------- | ------------------------------------ |
| `primary`   | Created by you, first-hand knowledge |
| `secondary` | Based on documentation, meetings     |
| `synthesis` | Compiled from multiple sources       |

## Relationship Fields

Track connections between notes:

```yaml
relatedTo: ["[[Related Note]]"]
supersedes: ["[[Old Decision]]"]
dependsOn: ["[[Foundation Decision]]"]
```

### Guidelines

- **relatedTo** — General related content (projects, decisions, context)
- **supersedes** — Decisions this one replaces
- **dependsOn** — Required foundation decisions

## Review Workflow

1. **Quarterly review** — Check `freshness` on important notes
2. **Update `reviewed` date** — When verifying content is current
3. **Downgrade `confidence`** — If information becomes uncertain
4. **Check relationships** — Ensure links are still valid
