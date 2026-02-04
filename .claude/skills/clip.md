# /clip

Save web content as a Resource note with metadata and summary.

## When to Use

- Saving articles, blog posts, documentation
- User shares a URL and wants to save it
- Building a reading list or research collection

## Instructions

### Basic Usage

```
/clip https://example.com/article
```

### Step 1: Fetch Page Metadata

**For YouTube URLs:**
Use the YouTube MCP tool `mcp__MCP_DOCKER__get_video_info` to extract:
- Video title
- Channel name (author)
- Description
- Duration
- Upload date

**For other URLs:**
Use WebFetch to extract:
- Title (from `<title>` or `og:title`)
- Description (from meta description or `og:description`)
- Author (if available)
- Published date (if available)
- Domain name

### Step 2: Create Resource Note

Create `Resource - {{title}}.md`:

```yaml
---
type: Resource
title: {{title}}
created: {{date}}
tags: [web-clip]
url: {{url}}
domain: {{domain}}
author: {{author}}
published: {{published_date}}
clipped: {{date}}
read_status: unread
classification: public
---

# {{title}}

**Source:** [{{domain}}]({{url}})
**Author:** {{author}}
**Published:** {{published_date}}

## Summary

{{ai_generated_summary}}

## Key Points

- {{key_point_1}}
- {{key_point_2}}
- {{key_point_3}}

## Highlights

_Add highlights and quotes here_

## My Notes

_Your thoughts and reactions_

## Related

_Link to related notes in your vault_
```

### Step 3: Generate Summary

Use AI to:
- Summarise the article in 2-3 sentences
- Extract 3-5 key points
- Suggest relevant tags

### With Readwise Integration

If user has Readwise:
1. Article is also saved to Readwise
2. Highlights sync back to MeKB via `/readwise` skill
3. Progressive enhancement of the Resource note

### Browser Extension Alternative

For frequent clipping, recommend:
- **Obsidian Web Clipper** - Direct to vault
- **Readwise Reader** - Read later + highlights
- **MarkDownload** - Convert any page to markdown

### Options

```
/clip <url>                    # Basic clip
/clip <url> --tags tag1,tag2   # Add tags
/clip <url> --project Project  # Link to project
/clip <url> --read-later       # Mark for later reading
```

### Example

```
User: /clip https://martinfowler.com/articles/microservices.html

Claude: Clipped and created:

**Resource - Microservices by Martin Fowler.md**

Summary: Martin Fowler's comprehensive guide to microservices 
architecture, covering when to use them, how to split services, 
and common pitfalls to avoid.

Key points:
- Start with a monolith, split when needed
- Services should be independently deployable
- Distributed systems add complexity

Tags added: [architecture, microservices, web-clip]

Would you like to:
1. Add to a project?
2. Link to related notes?
3. Add to reading list?
```

### Reading List

Track unread clips with:
```
/clips unread     # Show unread resources
/clips today      # Clipped today
/clips search X   # Search clips
```

### YouTube Example

```
User: /clip https://www.youtube.com/watch?v=abc123

Claude: Clipped YouTube video:

**Resource - How to Take Smart Notes.md**

- **Channel:** Vicky Zhao [BEEAMP]
- **Duration:** 15 minutes
- **Published:** 2026-01-15

Summary: A guide to building a note-taking system for better
knowledge management and AI-assisted thinking.

Key points:
- Context engineering beats prompt engineering
- 6 categories of notes for effective AI use
- Notes capture tacit knowledge

Tags: [video, topic/note-taking, topic/ai, web-clip]
```

### Tips

- Clip generously, curate later
- Add your own notes while the content is fresh
- Link clips to projects and concepts
- Review unread clips weekly
- YouTube videos get duration and timestamps automatically
