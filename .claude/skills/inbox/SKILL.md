---
name: inbox
---

# /inbox

Monitor for unprocessed files in the vault and suggest the appropriate skill to handle each.

## Usage

```
/inbox              # Check and classify all unprocessed files
/inbox --process    # Check and auto-process with suggested skills
```

## Instructions

### 1. Check for Untyped Root Files

Find markdown files at vault root that lack a `[Type] - ` naming convention or are missing `type` in frontmatter:

Use Grep to search for files missing `type:` in frontmatter:

```
Grep: pattern="^type:" in root *.md files
```

Cross-reference with Glob to find root `.md` files that don't follow `[Type] - ` naming:

```
Glob: "*.md" at vault root
```

Filter out known non-note files (`CLAUDE.md`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `TOOLS.md`, `SOUL.md`, `SECURITY.md`, `LICENSE`).

### 2. Check for Common Drop Patterns

Look for files that may have been dropped in without processing:

- Root `.md` files without frontmatter
- Files in `Daily/` without proper date format
- Files with no wiki-links (potential unprocessed imports)

### 3. Classify and Recommend

For each unprocessed file, suggest the appropriate skill:

| File Pattern | Suggested Skill | Rationale |
|-------------|----------------|-----------|
| Untitled or generic `.md` at root | `/note` or `/concept` | Needs classification and frontmatter |
| Looks like meeting notes | `/meeting` | Has attendees, agenda, or date patterns |
| Looks like a task/todo | `/task` | Has checklist items or action language |
| Looks like a person profile | `/person` | Has contact info or name-focused |
| Has URL as primary content | `/weblink` | URL capture needing summary |
| Untyped `.md` at root | Manual triage | Loose notes need classification |

### 4. Present Report

```markdown
## Inbox Report — YYYY-MM-DD

### Unprocessed Files (N found)

| # | File | Issue | Suggested Action |
|---|------|-------|-----------------|
| 1 | My random note.md | Missing type prefix | `/note` — add frontmatter and rename |
| 2 | TODO list.md | No frontmatter | `/task` — convert to task note |

### Quick Actions
- Process all: `/inbox --process`
- Process one: Run the suggested skill command
```

### 5. Auto-Process (--process flag)

If `--process` flag is set, invoke the suggested skill for each file sequentially, confirming with the user before each.

## Guidelines

- Read-only by default — only process files when `--process` is explicitly requested
- Always confirm before processing — show what will happen first
- Skip files in `Archive/`, `Templates/`, `.claude/`, and `.mekb/`
- Present results sorted by likely importance (missing frontmatter first)
