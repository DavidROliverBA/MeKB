# Changelog

All notable changes to MeKB are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project uses date-based versioning.

## [v3.2] - 2026-02-20

Two-layer persistence system for cross-session learning.

### Added

- **MCP memory server** — `.mcp.json` configuration for `@modelcontextprotocol/server-memory`, storing cross-session learning in `Memory/memory.jsonl`
- **Secret scanner hook** — `.claude/hooks/secret-scanner.py` blocks Edit/Write operations containing credential patterns (18 regex patterns covering AWS, GitHub, Slack, Stripe, OpenAI, Anthropic, and generic formats)
- **Memory guide** — `docs/MEMORY.md` with entity types, search limitations, maintenance procedures, and daily usage
- **Memory directory** — `Memory/` for MCP memory graph data (gitignored, local learning)

### Changed

- **README.md** — expanded Memory & Persistence section with architecture table, security hooks, and link to guide
- **CLAUDE.md** — added MCP Memory section with entity types, constraints, and tool reference
- **.gitignore** — added `Memory/memory.jsonl` exclusions
- **.claude/settings.json** — wired secret-scanner hook alongside classification-guard

## [v3.1] - 2026-02-13

Community ideas adoption and skill tooling fixes.

### Added

- **3 new skills:** `/de-ai-ify` (strip AI patterns from text), `/inbox` (find unprocessed files), `/spotlight` (macOS Spotlight search for non-markdown files)
- **kepano frontmatter** on all 40 skills — `name` field in YAML frontmatter for Anthropic skills convention
- **`migrate-skill-frontmatter.py`** — migration script with `--dry-run` and `--validate` flags
- **`.claude/AGENDA.md`** — session working state template (current focus, pending decisions, session notes)
- **`completedDate: null`** field in Task template for tracking when tasks were finished
- **`> [!ai-suggestion]` callout convention** for marking AI-generated content needing review
- **Claim-based naming convention** — optional thesis-in-title pattern for Note/Concept types
- **Frontmatter-aware tests** — `test_frontmatter_skipping` and `test_skill_name_from_directory` in test_skill_tools.py

### Changed

- **Fixed `skill-tools.py`** — all glob patterns updated from `*.md` to `*/SKILL.md` for subdirectory skill layout; `parse_skill()` now skips YAML frontmatter; skill name derived from parent directory
- **Fixed `test_skills.py`** — updated to use `*/SKILL.md` glob, frontmatter-aware header extraction, directory-based name matching
- **Fixed `test_skill_tools.py`** — test helpers create subdirectory structure, compare against `path.parent.name`
- **Fixed CI workflow** — skill count uses `find -name "SKILL.md"` instead of `ls *.md`
- **Enhanced `/daily`** — carries forward yesterday's unchecked items, checks overdue tasks, adds yesterday summary
- **Enhanced `/q`** — `--similar` flag for vector-based similar note discovery
- **Enhanced `/health`** — freshness cross-reference (flags `freshness: current` with stale `verified` dates)

## [v3.0] - 2026-02-06

Production scripts, comprehensive test suite, and CI pipeline.

### Added

- **12 production Python scripts** — all stdlib-only (zero external dependencies):
  - `build-index.py` — SQLite FTS5 search index with incremental updates
  - `build-graph.py` — Knowledge graph with BFS traversal and shortest path
  - `build-embeddings.py` — Vector embeddings for semantic search
  - `search.py` — Hybrid search engine (BM25 + vector + graph boost)
  - `build-site.py` — Static HTML site generator with dark/light mode
  - `browse.py` — Web content fetcher with Playwright fallback
  - `notify.py` — Multi-backend notifications (desktop, Slack, Discord, email)
  - `schedule.py` — Job scheduling via macOS launchd or Linux crontab
  - `stale-check.py` — Freshness monitoring with priority classification
  - `webhook-server.py` — HTTP API for remote note creation and index management
  - `skill-tools.py` — Skill listing, validation, export, and import
  - `detect-secrets.py` — Regex-based secret scanner for pre-commit hooks
- **8 new skills:** `/automate`, `/browse`, `/connections`, `/dev`, `/notify`, `/schedule`, `/session`, `/site`
- **236 tests** across 12 test files (~80% coverage, ~0.28s runtime)
- **7-job GitHub Actions CI pipeline** — security, search, graph, skills, site, webhook, utilities
- **scripts/README.md** — comprehensive documentation for all 12 scripts
- **CONTRIBUTING.md** — contributor guidelines, test development, PR checklist
- **SOUL.md** — project philosophy and design principles
- **TOOLS.md** — complete tooling reference

### Changed

- Updated 5 existing skills (`/graph`, `/health`, `/q`, `/search`, `/stale`) to reference new scripts
- Updated Decision and Concept templates
- README updated with production scripts, testing, and CI sections

## [v2.1] - 2026-02-04

Documentation, polish, and graph quality improvements.

### Added

- AI knowledge concepts from research (Event Sourcing, CQRS, etc.)
- Documentation polish and new features

### Fixed

- Orphan notes — improved graph connectivity across existing notes
- Markdown capitalisation in README

## [v2.0] - 2026-02-04

Personal knowledge management features, CRM, and sample content.

### Added

- **CRM features:** `/people`, `/people reconnect`, `/people met`, `/people search`
- **Review and reflection:** `/review` (spaced repetition), `/weekly` (summaries), `/stale` (freshness), `/habits` (tracking)
- **Content capture:** `/voice` (transcription), `/clip` (web clipper), `/suggest` (AI link recommendations)
- **Integrations:** `/calendar`, `/readwise`, `/export`
- **Sample notes** demonstrating all note types and features
- Week 6 review with orphan note fixes

## [v1.1] - 2026-02-04

Security features and guided onboarding.

### Added

- **Classification system:** 4 levels (public, personal, confidential, secret)
- **AI access control:** Hook-based interception for classified content
- **Secret detection:** Pre-commit hook via `detect-secrets.py`
- **Security setup wizard:** `scripts/setup-security.sh`
- **Guided onboarding:** `/start` skill with interactive setup

## [v1.0] - 2026-02-04

Initial release of MeKB.

### Added

- **11 note templates:** Daily, Note, Concept, Task, Project, Meeting, Person, Resource, Decision, ActionItem, Interaction
- **Core capture skills:** `/daily`, `/note`, `/concept`, `/meeting`, `/task`, `/person`, `/weblink`
- **Search skills:** `/q` (keyword), `/search` (semantic), `/ask` (AI Q&A), `/recent`, `/related`
- **Graph exploration:** `/graph`, `/orphans`
- **Maintenance:** `/health`, `/classify`
- **CLAUDE.md** — AI assistant instructions and vault schema
- **README.md** — project overview and quick start

---

[v3.0]: https://github.com/DavidROliverBA/MeKB/compare/392b84a...main
[v2.1]: https://github.com/DavidROliverBA/MeKB/compare/f746b41...392b84a
[v2.0]: https://github.com/DavidROliverBA/MeKB/compare/e2dcc09...f746b41
[v1.1]: https://github.com/DavidROliverBA/MeKB/compare/aeced28...e2dcc09
[v1.0]: https://github.com/DavidROliverBA/MeKB/commit/aeced28
