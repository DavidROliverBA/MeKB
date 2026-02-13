---
name: q
---

# /q

Fast full-text search across all notes.

## Usage

```
/q <search term>
/q <term> --type Concept
/q "exact phrase"
/q --similar "Note - My Idea"
```

## Instructions

### Preferred: SQLite FTS5 (fast, ranked)

If `.mekb/search.db` exists, use the search engine:

```bash
python3 scripts/search.py "<search term>"
python3 scripts/search.py "<search term>" --type <Type>
python3 scripts/search.py "<search term>" --limit 20
python3 scripts/search.py "<search term>" --explain
```

This returns BM25-ranked results with snippets and is ~1000x faster than grep.

**Rebuild the index** if results seem stale:
```bash
python3 scripts/build-index.py
```

### Similar Notes (--similar flag)

If `--similar "Note - Title"` is passed and `.mekb/embeddings.json` exists, find semantically similar notes:

```bash
python3 scripts/search.py --similar "Note - Title" --limit 10
```

This uses vector embeddings to find notes with related meaning, even if they don't share keywords. For full semantic search with more options, use `/search`.

### Fallback: Grep Search

If no search index exists, fall back to grep:

1. Search all `.md` files in the vault for the term
2. Return results showing:
   - Filename
   - Matching line with context
   - Match count per file
3. Sort by relevance (match count)
4. Limit to top 20 results

## Example

```
/q authentication
```

Returns notes mentioning "authentication" with context, ranked by relevance.

## Notes

- Search is case-insensitive
- Searches both filename and content
- Use quotes for exact phrases: `/q "exact phrase"`
- FTS5 search excludes `secret`-classified notes automatically
- Run `python3 scripts/build-index.py` to build/rebuild the index
