---
name: spotlight
---

# /spotlight

Search inside PDFs, images, and other non-markdown files using macOS Spotlight (`mdfind`). This leverages the OS-level content index — no custom indexing needed.

> **Note:** macOS only. For cross-platform vault search, use `/q` instead.

## Usage

```
/spotlight <search query>           # Search all files in the vault
/spotlight --type pdf <query>       # Search only PDFs
/spotlight --type image <query>     # Search only images (OCR-indexed)
```

## Instructions

### 1. Run mdfind

Execute the appropriate search based on flags:

#### Default (all files)

```bash
mdfind -onlyin . "<search_query>" 2>/dev/null
```

#### Filter by PDF

```bash
mdfind -onlyin . "kMDItemContentType == 'com.adobe.pdf' && kMDItemTextContent == '*<query>*'" 2>/dev/null
```

If the above returns nothing, fall back to the simpler form:

```bash
mdfind -onlyin . -name ".pdf" "<search_query>" 2>/dev/null
```

#### Filter by Images

```bash
mdfind -onlyin . "kMDItemContentType == 'public.image'" "<search_query>" 2>/dev/null
```

### 2. Present Results

Format results clearly:

```markdown
## Spotlight Search: <query>

Found **N** matching files

| # | File | Type | Size |
|---|------|------|------|
| 1 | [filename](path) | PDF | 2.4 MB |
| 2 | ... | ... | ... |

### Quick Actions

- Full vault search: `/q <query>`
- Semantic search: `/search <query>`
```

### 3. Get File Details (Optional)

For each result, get file size and type:

```bash
ls -lh "<file_path>" 2>/dev/null
```

## Notes

- `mdfind` uses macOS Spotlight — files must be indexed (most are by default)
- Works best with text-based PDFs; scanned PDFs need OCR indexing
- For vault note content search, use `/q` instead
- Results are file paths relative to the vault root
