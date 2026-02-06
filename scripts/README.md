# MeKB Scripts

Production scripts for the MeKB personal knowledge base. All scripts are standalone Python 3.9+ with **zero external dependencies** (stdlib only). Optional features like vector search require additional packages.

## Quick Reference

| Script | Purpose | Runtime |
|--------|---------|---------|
| `build-index.py` | SQLite FTS5 search index | ~0.03s |
| `build-graph.py` | Knowledge graph with traversal | ~0.5s |
| `build-embeddings.py` | Vector embeddings for semantic search | ~30s |
| `search.py` | Hybrid search (BM25 + vector + graph) | ~0.01s |
| `build-site.py` | Static HTML site generator | ~1s |
| `browse.py` | Web content fetcher/extractor | varies |
| `notify.py` | Multi-backend notifications | ~1s |
| `schedule.py` | Job scheduling (launchd/cron) | instant |
| `stale-check.py` | Find notes needing review | ~0.1s |
| `webhook-server.py` | HTTP API for remote operations | server |
| `skill-tools.py` | Skill management utilities | instant |
| `detect-secrets.py` | Pre-commit secret scanner | ~0.5s |

## Prerequisites

- **Python 3.9+** (all scripts)
- **No pip install required** for core functionality

Optional:
- `pip install sentence-transformers` — for vector/semantic search
- `pip install playwright && playwright install chromium` — for JS-rendered web fetching

## Getting Started

```bash
# Build the search index (do this first)
python3 scripts/build-index.py

# Search your vault
python3 scripts/search.py "your query"

# Build the knowledge graph
python3 scripts/build-graph.py

# Check vault health
python3 scripts/stale-check.py --summary
```

## Scripts in Detail

### build-index.py — Search Index

Creates a SQLite FTS5 full-text search index from all markdown files. Supports incremental updates (only re-indexes changed files).

```bash
python3 scripts/build-index.py              # Build/update index
python3 scripts/build-index.py --rebuild    # Force full rebuild
python3 scripts/build-index.py --stats      # Show index statistics
python3 scripts/build-index.py --verbose    # Show progress
python3 scripts/build-index.py --vault /path/to/vault  # Specify vault
```

**Output:** `.mekb/search.db` (gitignored — rebuild locally)

**Security:** Notes with `classification: secret` are excluded from the index. The `secret/` directory is skipped entirely.

---

### search.py — Hybrid Search Engine

Three-tier search with automatic fallback:

1. **FTS5 BM25** — always available when `search.db` exists
2. **Vector similarity** — when `embeddings.json` exists
3. **Hybrid fusion** — 70% BM25 + 30% vector with optional graph centrality boost

```bash
python3 scripts/search.py "search query"
python3 scripts/search.py "query" --type Concept    # Filter by note type
python3 scripts/search.py "query" --limit 20        # Max results
python3 scripts/search.py "query" --explain          # Show scoring details
python3 scripts/search.py "query" --json             # JSON output
python3 scripts/search.py "query" --fts-only         # Skip vector search
python3 scripts/search.py "query" --vector-only      # Skip FTS search
```

**Security:** Results with `classification: secret` are always excluded.

---

### build-graph.py — Knowledge Graph

Builds a typed knowledge graph from wiki-links and frontmatter relationships. Supports BFS traversal, shortest path, orphan detection, and hub identification.

```bash
python3 scripts/build-graph.py                           # Build/update graph
python3 scripts/build-graph.py --stats                    # Show statistics
python3 scripts/build-graph.py --orphans                  # List unlinked notes
python3 scripts/build-graph.py --hubs                     # Most connected notes
python3 scripts/build-graph.py --traverse "Note.md" --depth 2  # BFS from note
python3 scripts/build-graph.py --path "A.md" "B.md"       # Shortest path
python3 scripts/build-graph.py --json                      # JSON output
```

**Output:** `.mekb/graph.json` (gitignored — rebuild locally)

**Typed relationships** parsed from frontmatter: `depends-on`, `references`, `supersedes`, `contradicts`, `supports`, `implements`, `extends`, `inspired-by`.

---

### build-embeddings.py — Vector Embeddings

Generates vector embeddings for semantic (meaning-based) search using sentence-transformers.

```bash
pip install sentence-transformers              # One-time setup
python3 scripts/build-embeddings.py            # Build/update embeddings
python3 scripts/build-embeddings.py --rebuild  # Force full rebuild
python3 scripts/build-embeddings.py --stats    # Show statistics
python3 scripts/build-embeddings.py --model all-MiniLM-L6-v2  # Specify model
```

**Output:** `.mekb/embeddings.json` (gitignored — rebuild locally)

**Text preparation:** Titles, types, and tags are prepended to body text. Code blocks are stripped. Wiki-links are unwrapped. Body is truncated to 3,000 characters.

**Security:** Notes with `classification: secret` are excluded. The `secret/` directory is skipped.

---

### build-site.py — Static Site Generator

Generates a static HTML site from vault notes with dark/light mode, tag pages, and wiki-link resolution.

```bash
python3 scripts/build-site.py                        # Build to _site/
python3 scripts/build-site.py --output /path/to/out  # Custom output dir
python3 scripts/build-site.py --public-only          # Only public notes
python3 scripts/build-site.py --dry-run              # Preview without writing
python3 scripts/build-site.py --serve                # Build and start HTTP server
python3 scripts/build-site.py --serve --port 8080    # Custom port
```

**Output:** `_site/` directory (gitignored)

**Generated pages:** `index.html` (overview), `notes.html` (all notes), `tags.html` (tag index), plus one page per note.

**Security:** Notes with `classification: secret` or `confidential` are always excluded. Use `--public-only` to restrict to `classification: public` notes only.

**Markdown rendering:** Built-in renderer (no external dependencies). Supports headings, bold, italic, code blocks, lists, blockquotes, horizontal rules, wiki-links, and markdown links. HTML is escaped to prevent XSS.

---

### browse.py — Web Content Fetcher

Fetches and extracts content from web pages. Uses Playwright for JavaScript-rendered pages with urllib fallback.

```bash
python3 scripts/browse.py fetch "https://example.com"        # Fetch page content
python3 scripts/browse.py links "https://example.com"         # Extract links
python3 scripts/browse.py readability "https://example.com"   # Extract main content
python3 scripts/browse.py screenshot "https://example.com"    # Take screenshot (Playwright)
```

**Playwright** (optional): Install with `pip install playwright && playwright install chromium`. Required for `screenshot` command and JavaScript-heavy sites.

---

### notify.py — Notification System

Multi-backend notification system supporting desktop (macOS), Slack, Discord, and email.

```bash
python3 scripts/notify.py send "Title" "Message"          # Auto-detect backend
python3 scripts/notify.py send "Title" "Msg" --backend slack  # Specific backend
python3 scripts/notify.py --test                            # Test all backends
python3 scripts/notify.py --list                            # List available backends
```

**Configuration:** `.mekb/notifications.yaml` (gitignored — may contain webhook URLs):

```yaml
slack:
  webhook_url: https://hooks.slack.com/services/...
discord:
  webhook_url: https://discord.com/api/webhooks/...
email:
  smtp_host: smtp.gmail.com
  smtp_port: 587
  from_address: you@example.com
  to_address: you@example.com
```

**Backends:**
- **Desktop** — macOS `osascript` (auto-detected on Darwin)
- **Slack** — Incoming webhook
- **Discord** — Webhook
- **Email** — SMTP with STARTTLS

---

### schedule.py — Job Scheduler

Cross-platform job scheduling using macOS launchd or Linux crontab.

```bash
python3 scripts/schedule.py install               # Install all jobs
python3 scripts/schedule.py install rebuild-index  # Install specific job
python3 scripts/schedule.py uninstall              # Remove all jobs
python3 scripts/schedule.py status                 # Show loaded jobs
python3 scripts/schedule.py run rebuild-index      # Run job immediately
python3 scripts/schedule.py list                   # List available jobs
```

**Predefined jobs:**

| Job | Schedule | What it does |
|-----|----------|--------------|
| `rebuild-index` | Daily 06:00 | Rebuild SQLite search index |
| `rebuild-graph` | Daily 06:15 | Rebuild knowledge graph |
| `rebuild-embeddings` | Weekly (Sunday 03:00) | Rebuild vector embeddings |
| `stale-check` | Weekly (Friday 09:00) | Check for stale notes |

**macOS:** Creates `~/Library/LaunchAgents/com.mekb.*.plist` files. Uses `launchctl` for management.

**Linux:** Adds entries to user crontab with `# mekb:job-name` markers for identification.

---

### stale-check.py — Freshness Monitor

Detects notes needing review based on their `verified` date or file modification time.

```bash
python3 scripts/stale-check.py                    # Full report
python3 scripts/stale-check.py --summary          # Summary counts only
python3 scripts/stale-check.py --json             # JSON output
python3 scripts/stale-check.py --type Concept     # Filter by type
```

**Staleness thresholds:**

| Priority | Age | Description |
|----------|-----|-------------|
| Critical | 180+ days | Urgently needs review |
| High | 120-179 days | Should be reviewed soon |
| Medium | 90-119 days | Starting to age |

**Priority boost:** High-value types (Decision, Concept, Pattern, Note) at medium staleness are boosted to high priority.

**Skipped:** Daily notes, `secret`-classified notes, archived notes, notes with `freshness: stale` override (marked critical regardless of age).

---

### webhook-server.py — HTTP API

Lightweight HTTP server for remote note creation and index management. Supports token-based authentication.

```bash
python3 scripts/webhook-server.py                              # Start on port 8765
python3 scripts/webhook-server.py --port 9000                  # Custom port
python3 scripts/webhook-server.py --token "your-secret-token"  # Enable auth
```

**Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | List available endpoints |
| `GET` | `/api/status` | Server status |
| `POST` | `/api/health` | Vault health (note/index counts) |
| `POST` | `/api/note` | Create a new note |
| `POST` | `/api/rebuild-index` | Trigger index rebuild |
| `POST` | `/api/rebuild-graph` | Trigger graph rebuild |

**Authentication:** When started with `--token`, all requests must include either:
- `Authorization: Bearer <token>` header, or
- `X-Webhook-Token: <token>` header

**Security:**
- Notes with `classification: secret` or `confidential` cannot be created via the API (returns 403)
- Title characters are sanitised to prevent path traversal
- Duplicate note titles return 409

**Example — create a note:**

```bash
curl -X POST http://localhost:8765/api/note \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"title": "My Note", "type": "Concept", "content": "Note body", "tags": ["domain/data"]}'
```

---

### skill-tools.py — Skill Management

Utilities for listing, validating, exporting, and importing MeKB skills.

```bash
python3 scripts/skill-tools.py list                     # List all skills
python3 scripts/skill-tools.py validate                  # Validate all skills
python3 scripts/skill-tools.py validate search.md        # Validate one skill
python3 scripts/skill-tools.py export search.md          # Export as .mekb-skill
python3 scripts/skill-tools.py import skill.mekb-skill   # Import a skill
```

**Validation checks:** Missing header, command/filename mismatch, missing Usage/Instructions sections, broken script references.

---

### detect-secrets.py — Secret Scanner

Regex-based secret detection for pre-commit hooks. Scans files for API keys, tokens, private keys, connection strings, and high-entropy strings.

```bash
python3 scripts/detect-secrets.py --directory .          # Scan current directory
python3 scripts/detect-secrets.py file1.md file2.md      # Scan specific files
python3 scripts/detect-secrets.py --json                  # JSON output
python3 scripts/detect-secrets.py --baseline .secrets.baseline  # Exclude known entries
echo "file.md" | python3 scripts/detect-secrets.py       # Read file list from stdin
```

**Detected patterns:** AWS keys, GitHub tokens, API keys, passwords, bearer tokens, private keys, SSH keys, connection strings, Slack/Stripe/Azure/Google/Anthropic/OpenAI tokens, JWT tokens, high-entropy strings.

**Severity levels:** critical, high, medium, low.

**False positive handling:** Patterns like `example`, `placeholder`, `test`, `dummy`, `sample`, and template variables (`{{...}}`) are automatically excluded.

**Ignored files:** `.git/`, `node_modules/`, images (`.png`, `.jpg`, `.gif`, `.pdf`), `package-lock.json`.

---

## Testing

The test suite covers all 12 scripts with 236 tests across 13 files.

```bash
# Run all tests
python3 -m pytest scripts/tests/ -v

# Run tests for a specific script
python3 -m pytest scripts/tests/test_search.py -v

# Run without pytest (stdlib only)
python3 -m unittest discover scripts/tests/ -v
```

**Test structure:**

| Test File | Script | Tests |
|-----------|--------|-------|
| `test_search.py` | `build-index.py`, `search.py` | 29 |
| `test_graph.py` | `build-graph.py` | 22 |
| `test_security.py` | `detect-secrets.py` | 16 |
| `test_skills.py` | Skill files | 8 |
| `test_webhook.py` | `webhook-server.py` | 24 |
| `test_site.py` | `build-site.py` | 33 |
| `test_browse.py` | `browse.py` | 24 |
| `test_notify.py` | `notify.py` | 25 |
| `test_stale.py` | `stale-check.py` | 15 |
| `test_schedule.py` | `schedule.py` | 12 |
| `test_embeddings.py` | `build-embeddings.py` | 14 |
| `test_skill_tools.py` | `skill-tools.py` | 10 |

**Shared utilities** in `tests/helpers.py`: `VaultFixture` (temp vault creation), `create_note` (test note factory), `_import_script` (import hyphenated filenames).

---

## Architecture

```
scripts/
  build-index.py          # Index layer — SQLite FTS5
  build-graph.py          # Index layer — knowledge graph
  build-embeddings.py     # Index layer — vector embeddings
  search.py               # Query layer — hybrid search
  build-site.py           # Output layer — static site
  browse.py               # Input layer — web fetching
  notify.py               # Output layer — notifications
  schedule.py             # Automation — job scheduling
  stale-check.py          # Quality — freshness monitoring
  webhook-server.py       # API layer — HTTP endpoints
  skill-tools.py          # Tooling — skill management
  detect-secrets.py       # Security — secret scanning
  tests/
    helpers.py            # Shared test utilities
    conftest.py           # Pytest configuration
    test_*.py             # Test files (13 total)
```

**Key principles:**
- **Zero external dependencies** for core functionality (Python stdlib only)
- **Security-first** — secret/confidential content excluded from all indexes and outputs
- **Vault discovery** — scripts find the vault root by looking for `.mekb/` or `CLAUDE.md`
- **Incremental updates** — index and graph builders only process changed files
- **Cross-platform** — macOS and Linux support for scheduling; all other scripts work anywhere

## CI/CD

GitHub Actions runs 7 parallel jobs on every push/PR to `main`:

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
