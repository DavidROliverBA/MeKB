# Memory & Persistence Guide

MeKB uses a two-layer persistence system so your AI assistant learns between sessions instead of starting from scratch every time.

## The Problem

Every Claude Code session starts with no memory of previous sessions. It re-discovers the same bugs, re-learns the same conventions, and trips over the same failure patterns you already fixed. CLAUDE.md provides static instructions but it is flat — a document you maintain by hand. Session Memory captures summaries but they are chronological and grow noisy fast. Neither connects ideas to other ideas.

## The Architecture

Two layers, two jobs. Each layer owns unique data.

### Layer 1: MCP Memory Graph

Cross-session learning stored in `Memory/memory.jsonl` via the [MCP memory server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory).

**What it stores:**
- Lessons from failures (things that broke and how to fix them)
- Conventions the assistant keeps violating
- Runbooks for known error patterns (symptom-cause-fix procedures)
- Knowledge gaps that need future attention
- Session summaries (what happened, auto-created at session end)

**What it does NOT store:**
- Vault content (notes, people, projects — that is the graph's job)
- Raw conversation transcripts
- Temporary working state

**Configuration** (`.mcp.json` in project root):

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "${PROJECT_DIR}/Memory/memory.jsonl"
      }
    }
  }
}
```

**Available tools:** `create_entities`, `search_nodes`, `read_graph`, `add_observations`, `delete_entities`

### Layer 2: Knowledge Graph Index

Structured lookups across all your notes, built from YAML frontmatter and wiki-links by `scripts/build-graph.py`.

**What it stores:**
- Note metadata (type, title, tags, status, relationships)
- Wiki-link edges between notes
- Aggregated statistics (note counts, orphans, health scores)

**When to use it:**
- "Find all decisions about API strategy"
- "Who did I meet with last week?"
- "What tasks are overdue?"
- "Show me orphaned notes with no backlinks"

```bash
python3 scripts/build-graph.py          # Build/rebuild the graph
python3 scripts/build-graph.py --stats  # Show graph statistics
```

## Entity Types

Memory uses five entity types. Keep the total count under fifty.

| Type | Purpose | Example |
|------|---------|---------|
| **LessonLearned** | Patterns from failures | "Wiki-links in YAML must be quoted with double quotes" |
| **Convention** | Rules the assistant keeps violating | "Tags use hierarchical slash notation, all lowercase" |
| **Runbook** | Symptom-cause-fix procedures | "git commit fails after hook fixes → git add -u then commit" |
| **KnowledgeGap** | Known problems for future attention | "No pruning mechanism for memory entities" |
| **SessionSummary** | What happened in each session (auto-created) | "Session focused on meeting notes and project updates" |

## How Entities Work

Entities live in `Memory/memory.jsonl`, one JSON object per line.

**Entity format:**

```json
{"type":"entity","name":"Lesson-QuoteWikiLinks","entityType":"LessonLearned","observations":["Wiki-links in YAML frontmatter must be quoted","Unquoted brackets break YAML parsers silently"]}
```

**Relation format:**

```json
{"type":"relation","from":"Lesson-QuoteWikiLinks","to":"Convention-FrontmatterSchema","relationType":"reinforces"}
```

**Naming conventions:**
- `Lesson-` prefix for LessonLearned
- `Convention-` prefix for Convention
- `Runbook-` prefix for Runbook
- `Gap-` prefix for KnowledgeGap
- `Session-YYYY-MM-DD-HHMM` for SessionSummary

**Observation rules:**
- One fact per observation string
- Front-load keywords (search uses contiguous substring matching)
- Keep observations short and specific
- Include discovery context ("Discovered 2026-02-20 during meeting note creation")

## Search Limitations

The MCP memory server's `search_nodes` uses contiguous substring matching, not full-text search.

| Query | Result |
|-------|--------|
| `pre-commit` | Finds runbooks mentioning pre-commit |
| `pre-commit hook whitespace` | Returns nothing (words not adjacent) |
| `wiki` | Finds lessons about wiki-links |
| `wiki YAML quotes` | Returns nothing |

**Best practice:** Search with single keywords, not phrases. Use the most distinctive term.

## Known Constraints

1. **No pagination** — `read_graph` returns everything in one call. Keep entities under fifty.
2. **No type filtering on search** — `search_nodes` searches all entity types.
3. **No file locking** — never issue parallel memory writes (corruption risk, GitHub issue #1819).
4. **Contiguous substring matching** — not semantic search, not word-level matching.
5. **No server-side pruning** — old entities must be deleted manually or via script.

## Security

Two hooks protect your vault during Claude Code sessions:

### Secret Scanner (`.claude/hooks/secret-scanner.py`)

Fires before every Edit and Write operation. Scans the content being written against eighteen credential patterns covering:
- Cloud provider keys (AWS, Google, Azure)
- API tokens (GitHub, Slack, Stripe, OpenAI, Anthropic)
- Generic patterns (passwords, bearer tokens, connection strings, private keys, JWTs)

If a pattern matches, the operation is blocked before anything is written to disk. Documentation files (SECURITY.md, CLAUDE.md, docs/) are whitelisted to avoid false positives.

### Classification Guard (`.claude/hooks/classification-guard.py`)

Blocks Claude from reading notes classified as `confidential` or `secret`. Uses the `classification` field in YAML frontmatter.

| Classification | AI Access |
|---------------|-----------|
| `public` | Full access |
| `personal` | Full access |
| `confidential` | Blocked (requires approval) |
| `secret` | Always blocked |

## Daily Usage

You do not need to manage memory manually. It works in the background:

1. **Session start** — Claude reads `.mcp.json`, connects to the memory server, and can search for relevant lessons and conventions.
2. **During the session** — When Claude encounters a problem it has seen before, it searches memory and finds the runbook or lesson.
3. **When you learn something new** — Ask Claude to record it: "Save this as a lesson learned" or "Create a runbook for this error pattern."
4. **Session end** — Session summaries can be recorded automatically with a session-learner hook.

## Maintenance

### Backup

The memory file is gitignored (it contains local learning data). Back it up periodically:

```bash
cp Memory/memory.jsonl Memory/memory.jsonl.bak
```

### Check entity count

```bash
wc -l Memory/memory.jsonl
# Keep under 50 entities + their relations (roughly 100 lines)
```

### Prune old sessions

If SessionSummary entities accumulate, delete the oldest ones:

```bash
# Count session summaries
grep -c '"SessionSummary"' Memory/memory.jsonl

# To prune, ask Claude: "Delete session summaries older than 30 days"
```

### Rebuild the graph

```bash
python3 scripts/build-graph.py          # Full rebuild
python3 scripts/build-graph.py --stats  # Check health
```

## What Should NOT Be in Memory

- **Vault content** — Notes, people, projects belong in the graph index, not memory
- **Credentials** — Never store keys, tokens, or passwords anywhere in the vault
- **Temporary state** — Session working context belongs in `.claude/AGENDA.md`
- **Duplicates of CLAUDE.md** — If it is already in CLAUDE.md, memory adds noise not signal

## Further Reading

- [Architecture article](https://medium.com/@DavidROliverBA) — Full design rationale for the two-layer system
- [MCP memory server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) — Official repository and documentation
- [SECURITY.md](../SECURITY.md) — Classification, access control, and secret detection
- [docs/ENCRYPTION.md](ENCRYPTION.md) — Encrypting classified notes at rest
