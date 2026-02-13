# TOOLS.md

Reference for MeKB's tooling capabilities.

## Scripts

13 production scripts in `scripts/`. All use Python 3.9+ stdlib only (no external dependencies unless noted).

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `scripts/build-index.py` | SQLite FTS5 search index | stdlib `sqlite3` |
| `scripts/build-graph.py` | Knowledge graph (JSON) | stdlib only |
| `scripts/build-embeddings.py` | Vector embeddings | **Optional:** `sentence-transformers` |
| `scripts/search.py` | Hybrid search engine | stdlib only |
| `scripts/build-site.py` | Static HTML site generator | stdlib only |
| `scripts/browse.py` | Web content fetcher/extractor | **Optional:** `playwright` |
| `scripts/notify.py` | Multi-backend notifications | stdlib only |
| `scripts/schedule.py` | Job scheduling (launchd/cron) | stdlib only |
| `scripts/stale-check.py` | Stale note detection | stdlib only |
| `scripts/webhook-server.py` | HTTP API for remote operations | stdlib only |
| `scripts/skill-tools.py` | Skill listing, validation, export/import | stdlib only |
| `scripts/detect-secrets.py` | Pre-commit secret scanner | stdlib only |
| `scripts/migrate-skill-frontmatter.py` | Add kepano frontmatter to skills | stdlib only |
| `scripts/setup-security.sh` | Security setup wizard | bash |

See [scripts/README.md](scripts/README.md) for full documentation, usage examples, and architecture.

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
| rebuild-graph | Daily 06:15 | `python3 scripts/build-graph.py` |
| rebuild-embeddings | Weekly (Sun 03:00) | `python3 scripts/build-embeddings.py` |
| stale-check | Weekly (Fri 09:00) | `python3 scripts/stale-check.py --summary` |

Install with: `python3 scripts/schedule.py install`

## Skills

40 skills available in `.claude/skills/`. Categories:

### Capture

| Skill | Purpose |
|-------|---------|
| `/daily` | Create today's daily note |
| `/note <title>` | Create knowledge note |
| `/concept <title>` | Create concept definition |
| `/meeting <title>` | Create meeting note |
| `/task <title>` | Quick-create task |
| `/person <name>` | Create person note |
| `/weblink <url>` | Save URL with summary |
| `/clip <url>` | Web clipper (YouTube, etc.) |
| `/voice` | Voice note transcription |
| `/de-ai-ify` | Rewrite AI text to sound human |

### Discover

| Skill | Purpose |
|-------|---------|
| `/q <term>` | Keyword search (FTS5) |
| `/search <query>` | Semantic search by meaning |
| `/ask <question>` | AI-powered vault Q&A |
| `/recent` | Recently modified notes |
| `/related <topic>` | Find connected notes |
| `/suggest` | AI-powered link suggestions |
| `/graph` | Explore note connections |
| `/connections` | Deep relationship analysis |
| `/browse <url>` | Fetch and extract web content |
| `/spotlight` | Search non-markdown files (macOS) |

### Review & Reflect

| Skill | Purpose |
|-------|---------|
| `/review` | Spaced repetition - resurface notes |
| `/weekly` | Generate weekly summary |
| `/stale` | Find notes needing verification |
| `/session` | Session summary and handoff |

### Relationships (CRM)

| Skill | Purpose |
|-------|---------|
| `/people` | Network dashboard |
| `/people reconnect` | Who to reach out to |
| `/people met <name>` | Log an interaction |
| `/people search` | Find by expertise |

### Productivity

| Skill | Purpose |
|-------|---------|
| `/habits` | Track daily habits |
| `/export` | Export for sharing |
| `/calendar` | Calendar integration |
| `/readwise` | Readwise sync |

### Automation & Dev

| Skill | Purpose |
|-------|---------|
| `/automate` | Create automation workflows |
| `/dev` | Developer tools and utilities |
| `/notify` | Send notifications (Slack, Discord, etc.) |
| `/schedule` | Manage scheduled jobs |
| `/site` | Generate static HTML site |

### Maintenance

| Skill | Purpose |
|-------|---------|
| `/health` | Vault health check |
| `/orphans` | Find unlinked notes |
| `/inbox` | Find unprocessed files |
| `/classify` | Manage security levels |
| `/start` | Guided onboarding |

## Testing

236 tests across 12 test files, covering all 12 production scripts.

| Test File | Script Tested | Tests |
|-----------|--------------|-------|
| `test_search.py` | `build-index.py`, `search.py` | 29 |
| `test_graph.py` | `build-graph.py` | 22 |
| `test_security.py` | `detect-secrets.py` | 16 |
| `test_skills.py` | Skill files | 8 |
| `test_site.py` | `build-site.py` | 33 |
| `test_webhook.py` | `webhook-server.py` | 24 |
| `test_browse.py` | `browse.py` | 24 |
| `test_notify.py` | `notify.py` | 25 |
| `test_stale.py` | `stale-check.py` | 15 |
| `test_schedule.py` | `schedule.py` | 12 |
| `test_embeddings.py` | `build-embeddings.py` | 14 |
| `test_skill_tools.py` | `skill-tools.py` | 10 |

**Shared helpers** in `tests/helpers.py`: `VaultFixture` (temp vault creation), `create_note` (test note factory), `_import_script` (import hyphenated filenames).

```bash
python3 -m pytest scripts/tests/ -v          # Run all (pytest)
python3 -m unittest discover scripts/tests/  # Run all (stdlib)
```

## CI/CD

7 parallel GitHub Actions jobs on every push/PR to `main`:

| Job | What it checks |
|-----|----------------|
| Security Checks | Secret detection + security tests |
| Search Index | Index build + search tests |
| Knowledge Graph | Graph build + graph tests |
| Skill Validation | Skill format + consistency tests |
| Site Generator | Site builder tests |
| Webhook Server | Webhook handler tests |
| Utility Scripts | Browse, notify, stale, schedule, embeddings, skill-tools tests |

See `.github/workflows/ci.yml` for configuration.

## Security

- **Classification:** 4 levels (public, personal, confidential, secret)
- **AI Access Control:** Hook-based interception via `classification-guard.py`
- **Secret Detection:** Pre-commit hook via `detect-secrets.py`
- **Modes:** Interactive (ask user) or Strict (always block confidential+)
