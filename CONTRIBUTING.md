# Contributing to MeKB

MeKB is a personal knowledge base template. Contributions that improve the template for all users are welcome.

## Prerequisites

- Python 3.9+
- Git
- A text editor (Obsidian recommended but not required)

## Setup

```bash
git clone https://github.com/your-username/MeKB.git
cd MeKB
./scripts/setup-security.sh    # Set up pre-commit hooks
python3 scripts/build-index.py  # Build search index
python3 scripts/build-graph.py  # Build knowledge graph
```

## Running Tests

MeKB has 236 tests across 12 test files covering all 12 production scripts. Tests run in ~0.28s.

```bash
# All tests (requires pytest)
python3 -m pytest scripts/tests/ -v

# Without pytest (stdlib unittest)
python3 -m unittest discover scripts/tests/ -v

# Individual test files
python3 -m pytest scripts/tests/test_search.py -v
python3 -m pytest scripts/tests/test_graph.py -v
python3 -m pytest scripts/tests/test_security.py -v
python3 -m pytest scripts/tests/test_skills.py -v
python3 -m pytest scripts/tests/test_site.py -v
python3 -m pytest scripts/tests/test_browse.py -v
python3 -m pytest scripts/tests/test_notify.py -v
python3 -m pytest scripts/tests/test_stale.py -v
python3 -m pytest scripts/tests/test_schedule.py -v
python3 -m pytest scripts/tests/test_embeddings.py -v
python3 -m pytest scripts/tests/test_skill_tools.py -v
python3 -m pytest scripts/tests/test_webhook.py -v
```

### Test Helpers

Shared test utilities live in `scripts/tests/helpers.py`:

- **`VaultFixture`** — Creates a temporary vault directory with `.mekb/` config for isolated testing
- **`create_note(title, type, ...)`** — Factory function for creating test notes with valid frontmatter
- **`_import_script(name)`** — Imports scripts with hyphenated filenames (e.g., `build-index`)

All test files use these helpers to avoid duplicating vault setup. Tests create their own temporary directories and clean up automatically.

## CI Pipeline

Every push and PR to `main` triggers 7 parallel GitHub Actions jobs:

| Job | What it runs |
|-----|-------------|
| Security Checks | Secret detection scan + `test_security.py` |
| Search Index | Index build + `test_search.py` |
| Knowledge Graph | Graph build + `test_graph.py` |
| Skill Validation | `test_skills.py` + skill count check |
| Site Generator | `test_site.py` |
| Webhook Server | `test_webhook.py` |
| Utility Scripts | `test_browse.py`, `test_notify.py`, `test_stale.py`, `test_schedule.py`, `test_embeddings.py`, `test_skill_tools.py` |

All 7 jobs must pass before a PR can be merged. See `.github/workflows/ci.yml` for the full configuration.

## Development Principles

### Zero Dependencies

MeKB's core must work with Python stdlib only. No `pip install` required for:
- Search index (`sqlite3`)
- Knowledge graph (`json`)
- Secret detection (`re`)
- Scheduling (`subprocess`)
- Site generation (`http.server`)
- Notifications (`urllib.request`)
- Web fetching (`urllib.request`)

Optional dependencies are allowed but must degrade gracefully:
- `sentence-transformers` for vector embeddings
- `pytest` for testing (falls back to `unittest`)
- `playwright` for browser automation (falls back to `urllib`)

### Security First

- Never store credentials in notes
- All scripts must respect the classification system
- `secret/` content is never indexed, never searched, never exposed
- Pre-commit hooks block committed secrets

### Markdown is the Product

- Notes must be readable without any tooling
- Frontmatter should follow the schema in `CLAUDE.md`
- Wiki-links (`[[Note Title]]`) for cross-references
- No proprietary formats

## Adding a Script

1. Create in `scripts/` with `.py` extension
2. Use Python 3.9+ stdlib only (document optional deps)
3. Include a docstring with usage examples
4. Add tests in `scripts/tests/test_<name>.py`
5. Add a shebang line: `#!/usr/bin/env python3`
6. Handle classification: skip `secret/` content
7. Use `helpers.py` utilities in tests (`VaultFixture`, `create_note`)

## Adding a Skill

1. Create in `.claude/skills/` with `.md` extension
2. Follow the format:
   ```markdown
   # /skill-name

   Brief description.

   ## Usage
   /skill-name <args>

   ## Instructions
   Step-by-step implementation guide.
   ```
3. Skill name must match filename
4. Reference scripts with `python3 scripts/name.py`
5. Update `CLAUDE.md` skills table
6. Run `python3 -m pytest scripts/tests/test_skills.py` to validate

## Adding a Template

1. Create in `Templates/` with `.md` extension
2. Include YAML frontmatter with `type` field
3. Use `{{placeholders}}` for dynamic values
4. Document in `CLAUDE.md` Note Types table

## Pull Request Checklist

- [ ] All tests pass: `python3 -m pytest scripts/tests/ -v`
- [ ] CI pipeline passes (7 jobs)
- [ ] No secrets: `python3 scripts/detect-secrets.py --directory .`
- [ ] No new dependencies (or documented as optional with graceful fallback)
- [ ] CLAUDE.md updated if adding skills/scripts
- [ ] TOOLS.md updated if adding scripts or skills
- [ ] Follows existing code style (no linter configured - match what's there)

## Code Style

- Python: Follow existing patterns in `scripts/`
- Markdown: Follow conventions in `CLAUDE.md`
- No tabs (spaces only)
- Line length: reasonable (no strict limit)
- UK English in documentation
