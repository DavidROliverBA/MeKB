# /stale

Find notes that haven't been verified recently and may need review.

## When to Use

- Periodic knowledge maintenance
- User says "find old notes", "stale content", "what needs updating"
- Part of monthly/quarterly vault maintenance

## Instructions

### Step 1: Define Staleness

Notes are considered stale if:
- `verified` field is older than 90 days (or missing)
- `freshness: stale` is set
- Note hasn't been modified in 180+ days

### Step 2: Find Stale Notes

Search all notes for:
- Missing `verified` field
- `verified` date > 90 days ago
- Exclude Daily notes (they're inherently time-bound)
- Exclude archived notes

### Step 3: Categorise by Priority

Group stale notes by:
1. **Critical** - Decisions, important concepts (>180 days)
2. **High** - Notes with many backlinks (>120 days)
3. **Medium** - Regular notes (>90 days)
4. **Low** - Resource links, references

### Step 4: Present Results

```markdown
## Stale Notes Report

### Critical (6+ months, high-impact)
- [[Decision - API Strategy]] - verified 203 days ago, 8 backlinks
- [[Concept - Authentication Flow]] - never verified, 5 backlinks

### High Priority (4+ months)
- [[Note - Cloud Architecture]] - verified 145 days ago
- [[Person - Key Contact]] - verified 130 days ago

### Medium Priority (3+ months)  
- [[Note - Meeting Templates]] - verified 95 days ago
- [[Resource - AWS Docs]] - verified 92 days ago

### Summary
- 4 critical notes need immediate review
- 12 notes total need verification
- Run `/review` daily to prevent staleness
```

### Step 5: Offer Bulk Actions

- **Verify all** - Update `verified` date on all shown notes
- **Review one by one** - Step through each note
- **Archive old** - Move truly obsolete notes to Archive/

## Freshness Fields

Notes can use these fields:
```yaml
verified: 2026-02-04      # Last time content was checked
freshness: current        # current | recent | stale
confidence: high          # high | medium | low
```

## Tips

- Run `/stale` monthly as part of maintenance
- High-backlink notes are more important to keep current
- Decisions and Concepts decay faster than Resources
