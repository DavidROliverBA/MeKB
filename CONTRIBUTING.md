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
```

## Development Principles

### Zero Dependencies

MeKB's core must work with Python stdlib only. No `pip install` required for:
- Search index (`sqlite3`)
- Knowledge graph (`json`)
- Secret detection (`re`)
- Scheduling (`subprocess`)

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

- [ ] Tests pass: `python3 -m pytest scripts/tests/ -v`
- [ ] No secrets: `python3 scripts/detect-secrets.py --directory .`
- [ ] No new dependencies (or documented as optional)
- [ ] CLAUDE.md updated if adding skills/scripts
- [ ] Follows existing code style (no linter configured - match what's there)

## Code Style

- Python: Follow existing patterns in `scripts/`
- Markdown: Follow conventions in `CLAUDE.md`
- No tabs (spaces only)
- Line length: reasonable (no strict limit)
- UK English in documentation
