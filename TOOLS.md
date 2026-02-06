# TOOLS.md

Reference for MeKB's tooling capabilities.

## Scripts

All scripts use Python 3.9+ stdlib only (no external dependencies unless noted).

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `scripts/build-index.py` | SQLite FTS5 search index | stdlib `sqlite3` |
| `scripts/build-graph.py` | Knowledge graph (JSON) | stdlib only |
| `scripts/build-embeddings.py` | Vector embeddings | **Optional:** `sentence-transformers` |
| `scripts/search.py` | Hybrid search engine | stdlib only |
| `scripts/stale-check.py` | Stale note detection | stdlib only |
| `scripts/schedule.py` | Job scheduling (launchd/cron) | stdlib only |
| `scripts/detect-secrets.py` | Pre-commit secret scanner | stdlib only |
| `scripts/setup-security.sh` | Security setup wizard | bash |

## Search Tiers

| Tier | Tool | Speed | Quality | Required |
|------|------|-------|---------|----------|
| 1 | FTS5 BM25 (`search.db`) | ~0.01s | Good | `build-index.py` |
| 2 | Vector similarity (`embeddings.json`) | ~0.1s | Better | `build-embeddings.py` + `sentence-transformers` |
| 3 | Hybrid (70/30 fusion + graph boost) | ~0.1s | Best | Tiers 1+2 + `build-graph.py` |

## Indexes

| File | Builder | Size | Rebuild |
|------|---------|------|---------|
| `.mekb/search.db` | `build-index.py` | ~200 KB | Daily |
| `.mekb/graph.json` | `build-graph.py` | ~50 KB | Daily |
| `.mekb/embeddings.json` | `build-embeddings.py` | ~5 MB | Weekly |

## Scheduling

| Job | Schedule | Command |
|-----|----------|---------|
| rebuild-index | Daily 06:00 | `python3 scripts/build-index.py` |
| rebuild-graph | Daily 06:05 | `python3 scripts/build-graph.py` |
| rebuild-embeddings | Weekly (Sun 06:10) | `python3 scripts/build-embeddings.py` |
| stale-check | Weekly (Fri 09:00) | `python3 scripts/stale-check.py --summary` |

Install with: `python3 scripts/schedule.py install`

## Skills

30 skills available in `.claude/skills/`. Key categories:

- **Capture:** `/daily`, `/note`, `/concept`, `/meeting`, `/task`, `/person`, `/weblink`, `/clip`, `/voice`
- **Search:** `/q`, `/search`, `/ask`, `/recent`, `/related`, `/suggest`
- **Graph:** `/graph`, `/connections`, `/orphans`
- **Review:** `/review`, `/weekly`, `/stale`, `/session`
- **CRM:** `/people`, `/people reconnect`, `/people met`, `/people search`
- **Maintenance:** `/health`, `/classify`, `/schedule`
- **Integrations:** `/calendar`, `/readwise`, `/export`, `/habits`

## Security

- **Classification:** 4 levels (public, personal, confidential, secret)
- **AI Access Control:** Hook-based interception via `classification-guard.py`
- **Secret Detection:** Pre-commit hook via `detect-secrets.py`
- **Modes:** Interactive (ask user) or Strict (always block confidential+)
