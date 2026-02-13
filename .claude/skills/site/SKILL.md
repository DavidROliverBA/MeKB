---
name: site
---

# /site

Build a static HTML site from your notes.

## Usage

```
/site                    # Build to _site/
/site --serve            # Build and serve locally
/site --public-only      # Only include public notes
/site --stats            # Show build statistics
/site --dry-run          # Preview without writing
```

## Instructions

### Build Site

```bash
python3 scripts/build-site.py
```

Generates a browsable HTML site in `_site/` with:
- **index.html** - Home page with recent notes
- **notes.html** - All notes grouped by type
- **tags.html** - Notes grouped by tags
- Individual pages for each note

### Serve Locally

```bash
python3 scripts/build-site.py --serve
```

Builds and starts a local server at http://localhost:8080.

### Public Export

```bash
python3 scripts/build-site.py --public-only
```

Only includes notes with `classification: public`.

### Custom Output

```bash
python3 scripts/build-site.py --output ~/my-site
```

### Features

- Dark/light mode (follows system preference)
- Wiki-links converted to HTML links
- Secret and confidential notes excluded automatically
- Basic markdown rendering (headings, lists, code, links)
- No dependencies - pure Python stdlib

## Notes

- Output directory is cleaned before each build
- `_site/` is gitignored by default
- For production hosting, copy `_site/` to any static host (Netlify, GitHub Pages, etc.)
