# /weblink

Save a URL with summary.

## Usage

```
/weblink <url>
```

## Instructions

1. Parse URL from command
2. Fetch the URL and extract:
   - Page title
   - Brief description/summary
3. Get today's date
4. Create `Resource - <title>.md` from `Templates/Resource.md`:
   - Replace `{{title}}` with page title
   - Replace `{{url}}` with the URL
   - Replace `{{date}}` with today's date
   - Add fetched summary to Summary section
5. Confirm: "Saved [[Resource - <title>]]"

## Example

```
/weblink https://example.com/great-article
```

Creates `Resource - Great Article.md` with summary
