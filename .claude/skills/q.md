# /q

Fast full-text search across all notes.

## Usage

```
/q <search term>
```

## Instructions

1. Parse search term from command
2. Search all `.md` files in the vault for the term
3. Return results showing:
   - Filename
   - Matching line with context
   - Match count per file
4. Sort by relevance (match count)
5. Limit to top 20 results

## Example

```
/q authentication
```

Returns notes mentioning "authentication" with context.

## Notes

- Search is case-insensitive
- Searches both filename and content
- Use quotes for exact phrases: `/q "exact phrase"`
