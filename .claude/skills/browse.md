# /browse

Fetch and extract web content. Uses Playwright for JS-rendered pages, falls back to urllib.

## Usage

```
/browse <url>                    # Fetch page content
/browse <url> --screenshot       # Take screenshot (Playwright required)
/browse <url> --links            # Extract all links
/browse <url> --readability      # Extract main content only
```

## Instructions

### Fetch Page Content

```bash
python3 scripts/browse.py fetch <url>
```

Returns JSON with title, description, author, and stripped text content.

For JavaScript-rendered pages (SPAs, dynamic content):

```bash
python3 scripts/browse.py fetch <url> --playwright
```

### Take Screenshot

```bash
python3 scripts/browse.py screenshot <url> [output_path]
```

Requires Playwright. Install: `pip install playwright && playwright install`

### Extract Links

```bash
python3 scripts/browse.py links <url>
```

Lists all links on the page with their text and URLs.

### Extract Main Content

```bash
python3 scripts/browse.py readability <url>
```

Attempts to extract the main article content, stripping navigation and ads.

## Notes

- urllib (stdlib) handles most pages without any dependencies
- Playwright needed only for JS-rendered content and screenshots
- Install Playwright: `pip install playwright && playwright install`
- Respects standard HTTP timeouts (15s urllib, 30s Playwright)
