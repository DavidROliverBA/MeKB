---
name: export
---

# /export

Export notes in shareable formats.

## When to Use

- Sharing knowledge with others
- Publishing to blog or documentation
- Creating presentations
- Backing up specific notes

## Instructions

### Basic Usage

```
/export [[Note - Title]]              # Export single note
/export [[Note - Title]] --format pdf # Specific format
/export project/myproject             # Export all notes with tag
/export --recent 7                    # Export last 7 days
```

### Formats

| Format     | Use Case                    | Output                |
|------------|-----------------------------|-----------------------|
| `markdown` | Sharing, other tools        | Clean .md file        |
| `html`     | Web publishing              | Styled HTML           |
| `pdf`      | Formal sharing              | PDF document          |
| `json`     | Data export, backup         | Structured JSON       |
| `docx`     | Word documents              | .docx file            |

### Step 1: Select Notes

Options for selecting notes:
- Single note: `[[Note - Title]]`
- Multiple notes: `[[Note 1]], [[Note 2]]`
- By tag: `tag:topic/architecture`
- By type: `type:Decision`
- By date: `--recent 7` or `--from 2026-01-01`
- By project: `project:myproject`

### Step 2: Clean for Export

Before export, optionally:
- Remove frontmatter (YAML)
- Convert wiki-links to standard markdown links
- Remove internal tags
- Resolve relative links
- Strip classification metadata

### Step 3: Generate Output

**Markdown (default):**
```bash
# Copy to clipboard
pbcopy < "Note - Title.md"

# Or write to export folder
cp "Note - Title.md" export/
```

**HTML:**
```bash
# Using pandoc
pandoc "Note - Title.md" -o export/note.html --standalone

# Or marked
marked "Note - Title.md" > export/note.html
```

**PDF:**
```bash
# Using pandoc + LaTeX
pandoc "Note - Title.md" -o export/note.pdf

# Or via HTML
pandoc "Note - Title.md" -o export/note.html
# Then print to PDF from browser
```

### Step 4: Handle Links

When exporting, handle wiki-links:

| Option          | Behaviour                          |
|-----------------|-----------------------------------|
| `--keep-links`  | Keep `[[wiki-links]]` as-is       |
| `--to-markdown` | Convert to `[title](file.md)`     |
| `--to-plain`    | Convert to plain text             |
| `--remove`      | Remove links entirely             |

### Examples

**Export for blog:**
```
User: /export [[Note - How to Learn]] --format html --remove-frontmatter

Claude: Exported to: export/how-to-learn.html

- Removed frontmatter
- Converted wiki-links to plain text
- Ready to paste into blog CMS
```

**Export project notes:**
```
User: /export project:website-redesign --format pdf

Claude: Exporting 12 notes tagged with project:website-redesign...

Created: export/website-redesign-bundle.pdf

Contents:
- Project - Website Redesign
- 5 Meeting notes
- 3 Decision notes
- 3 Task notes
```

**Quick share:**
```
User: /export [[Decision - API Strategy]] --clipboard

Claude: Copied to clipboard!

Decision - API Strategy

We chose REST over GraphQL because...
[full note content]

Paste anywhere to share.
```

### Bulk Export

Export everything for backup:
```
/export --all --format json --output backup-2026-02-04.json
```

### Tips

- Export before sharing to remove internal links
- Use HTML for web publishing
- Use PDF for formal documents
- JSON export is great for backups
- Check classification before sharing!
