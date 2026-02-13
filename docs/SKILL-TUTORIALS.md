# Skill Tutorials

Hands-on tutorials for MeKB's newest skills. Each tutorial walks through a real use case with example input and output.

**Skills covered:** `/de-ai-ify`, `/inbox`, `/spotlight`

---

## Table of Contents

1. [/de-ai-ify — Clean Up AI-Generated Text](#de-ai-ify--clean-up-ai-generated-text)
2. [/inbox — Find and Triage Unprocessed Files](#inbox--find-and-triage-unprocessed-files)
3. [/spotlight — Search Inside PDFs and Images](#spotlight--search-inside-pdfs-and-images)

---

## /de-ai-ify — Clean Up AI-Generated Text

AI-generated text often has a recognisable flavour: hedge words, filler phrases, excessive enthusiasm, and formulaic structure. `/de-ai-ify` identifies these patterns and rewrites them to sound natural.

### When to Use

- After using `/note`, `/concept`, or `/ask` to generate content
- When reviewing notes with `> [!ai-suggestion]` callouts
- Before sharing AI-assisted writing with others
- To clean up pasted ChatGPT/Claude output in your vault

### Tutorial: Cleaning a Concept Note

**1. You have a concept note that reads like AI wrote it:**

```markdown
# Concept - Event Sourcing

## Overview

Let's dive into event sourcing! It's worth noting that this is a
fantastic pattern that has gained incredible traction in today's
rapidly evolving software landscape.

Event sourcing could potentially offer significant advantages. It's
possible that by storing events rather than current state, you might
arguably achieve better auditability. Perhaps this approach might
somewhat reduce data loss scenarios.

In conclusion, event sourcing is an amazing pattern that can help you
leverage your data to drive value and synergise your architecture.
```

**2. Run the skill:**

```
/de-ai-ify "Concept - Event Sourcing.md"
```

**3. Claude identifies the problems and shows a diff:**

```
Filler: "Let's dive into", "It's worth noting"
Hedging: "could potentially", "It's possible that", "might arguably"
Tone: "fantastic", "incredible", "amazing", "leverage", "synergise"
Structure: "In conclusion" wrap-up
```

**4. The rewritten version:**

```markdown
# Concept - Event Sourcing

## Overview

Event sourcing stores every change as an immutable event rather than
overwriting current state.

Storing events gives you a complete audit trail. Because nothing is
overwritten, data loss from accidental updates is eliminated.

Event sourcing suits systems where you need to reconstruct past states
or replay changes — audit-heavy domains, financial systems, and
collaborative editing.
```

**5. You review and confirm the changes.**

### What It Catches

| Pattern | Example | Fix |
|---------|---------|-----|
| Filler phrases | "Let's dive into..." | Cut entirely |
| Stacked hedging | "could potentially perhaps" | State directly |
| Enthusiasm | "fantastic", "incredible" | Remove or replace |
| Corporate-speak | "leverage", "drive value" | Use plain language |
| Formulaic endings | "In conclusion..." | Cut or rephrase |
| Question restating | "Great question! So..." | Answer directly |

### Tips

- Use `--section "Overview"` to target just one section instead of the whole note
- The skill never changes frontmatter, wiki-links, or Dataview queries
- It rephrases rather than removes — your ideas stay, the AI flavour goes

---

## /inbox — Find and Triage Unprocessed Files

Over time, files accumulate at the vault root without proper frontmatter or naming. Maybe you dropped in a quick `.md` file, pasted something from elsewhere, or an import left behind untyped notes. `/inbox` finds these and suggests what to do with each one.

### When to Use

- At the start of a session — quick hygiene check
- After importing notes from another tool (Notion, Roam, Apple Notes)
- When you notice loose files at the vault root
- As part of a weekly maintenance routine

### Tutorial: Triaging Loose Files

**1. You have some files sitting at the vault root without structure:**

```
MeKB/
├── meeting with sarah.md       # No frontmatter, no type prefix
├── API ideas.md                # No frontmatter
├── Quick thought on caching.md # No type prefix
└── ...
```

**2. Run the skill:**

```
/inbox
```

**3. Claude scans and produces a report:**

```markdown
## Inbox Report — 2026-02-13

### Unprocessed Files (3 found)

| # | File | Issue | Suggested Action |
|---|------|-------|-----------------|
| 1 | meeting with sarah.md | Missing type, no frontmatter | `/meeting` — create proper meeting note |
| 2 | API ideas.md | Missing type, no frontmatter | `/note` — add frontmatter and rename |
| 3 | Quick thought on caching.md | Missing type prefix | `/concept` — convert to concept note |

### Quick Actions
- Process all: `/inbox --process`
- Process one: Run the suggested skill command
```

**4. Process individually or in batch:**

```
# Process one at a time
/meeting "Meeting with Sarah"

# Or let Claude process them all with confirmation
/inbox --process
```

When using `--process`, Claude runs each suggested skill one by one, asking you to confirm before each.

### What It Skips

The skill ignores these automatically:
- `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `TOOLS.md`, `SOUL.md`, `SECURITY.md`
- Files in `Archive/`, `Templates/`, `.claude/`, `.mekb/`
- Files that already have valid `type` frontmatter and naming

### Tips

- Run `/inbox` at the start of each session — takes seconds and keeps the vault tidy
- Pair with `/health` for a complete vault checkup
- The skill is read-only by default — nothing changes until you say so

---

## /spotlight — Search Inside PDFs and Images

`/q` searches your markdown notes. But what about the PDFs, presentations, and images you've saved? `/spotlight` uses macOS Spotlight (`mdfind`) to search inside binary files — no custom indexing needed.

### When to Use

- Searching for text inside a saved PDF
- Finding which presentation mentions a specific topic
- Locating images that have been OCR-indexed
- When `/q` returns nothing but you know the content is somewhere in the vault

### Prerequisites

- **macOS only** — Spotlight is a macOS feature
- Files must be Spotlight-indexed (most are by default)
- For cross-platform search, use `/q` instead

### Tutorial: Finding Content in PDFs

**1. You have several PDFs in your vault and want to find one about "authentication":**

```
/spotlight authentication
```

**2. Claude runs `mdfind` and presents results:**

```markdown
## Spotlight Search: authentication

Found **3** matching files

| # | File | Type | Size |
|---|------|------|------|
| 1 | Security Architecture Review.pdf | PDF | 2.4 MB |
| 2 | API Gateway Design.pdf | PDF | 1.1 MB |
| 3 | OAuth2 Diagram.png | Image | 340 KB |

### Quick Actions
- Full vault search: `/q authentication`
- Semantic search: `/search authentication`
```

### Filtering by File Type

```
/spotlight --type pdf "data migration"     # PDFs only
/spotlight --type image "architecture"      # Images only (OCR-indexed)
```

### How It Works

Spotlight indexes file content in the background. When you search:

1. `mdfind` queries the Spotlight index (instant, no scanning)
2. Results include any file where the content matches — PDFs, PPTX, images with OCR text
3. Claude formats the results with file sizes and quick action links

### Tips

- Spotlight works best with text-based PDFs; scanned documents need OCR indexing first
- `/spotlight` searches all files in the vault directory, not just `Attachments/`
- Combine with `/q` — search notes with `/q`, search files with `/spotlight`
- If Spotlight hasn't indexed a file yet, wait a few minutes or run `mdimport <file>` manually

---

## Further Reading

- [CLAUDE.md](../CLAUDE.md) — Full skills reference table
- [TOOLS.md](../TOOLS.md) — All 40 skills listed by category
- [CONTRIBUTING.md](../CONTRIBUTING.md) — How to create your own skills
