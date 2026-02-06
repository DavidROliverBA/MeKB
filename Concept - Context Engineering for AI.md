---
type: Concept
title: "Context Engineering for AI"
created: 2026-02-05
tags:
  - topic/ai
  - topic/productivity
confidence: high
---

# Context Engineering for AI

> **Intent:** Escape the median response problem inherent in RLHF-trained AI models by systematically configuring four levers—memory, instructions, tools, and style—to achieve personalised, high-quality output that compounds over time.

## Context

AI models like ChatGPT, Claude, and Gemini are trained via RLHF to satisfy the median user preference. This creates a systematic bias toward generic responses (see [[Concept - RLHF Averaging]]).

For frequent users—especially knowledge workers doing similar types of work multiple times per week—the median response problem creates ongoing friction and requires constant correction.

## The Four Levers

### Lever 1: Memory

AI retains information about you across conversations so it doesn't start fresh every time.

- **ChatGPT:** Explicit memories, project-only memory, conversation history with citations
- **Claude:** Project-scoped memory by default, RAG-style retrieval, memory summaries
- **Gemini:** Personal intelligence connecting to Google apps

**Key Tactic:** Be intentional about what you ask AI to remember. Use projects to isolate contexts.

### Lever 2: Instructions

Persistent context about who you are, what you do, and how you want AI to behave.

- **ChatGPT:** Custom instructions, project-specific workspaces, custom GPTs
- **Claude:** Profile preferences, project instructions, style profiles from writing samples
- **Claude Code:** `claude.md` files checked into Git, whole team contributes

**Anti-pattern:** Vague instructions like "be concise" don't steer the model effectively.

**Effective pattern:** "For factual questions, answer in one sentence. For analysis requests, walk through reasoning step by step."

**The Boris Churnney workflow:**

1. AI makes a mistake
2. Add a rule to your instructions so it doesn't happen again
3. File fills out within a month
4. This compounds into dramatically higher productivity

### Lever 3: Tools

Connect AI to capabilities—web search, code execution, file access, external systems.

**Model Context Protocol (MCP)** is the "USB-C for AI"—a universal interface letting any AI connect to any tool through the same protocol. Over 10,000 MCP servers exist.

**Key insight:** Tools aren't just features you add—they **steer the inputs**. Turning tools on/off changes the character of responses.

### Lever 4: Style

Control tone, personality, and communication patterns.

- **ChatGPT:** Eight personalities with granular controls
- **Claude:** Three presets plus custom styles from writing samples

**Key Tactic:** Upload writing samples rather than describing your style in words.

## The Compounding Correction Workflow

Most people:
1. AI produces something "not quite right"
2. Correct in their head, get frustrated, move on

People getting 10x results:
1. AI produces something "not quite right"
2. **Capture the correction** (what was wrong?)
3. **Identify patterns** (made this correction before?)
4. **Encode back into the system** (instructions, memory, style)

**The discipline:** Treat every "that's not quite right" moment as discovering a steering input, not just frustration.

## Consequences

### Benefits

- **Permanently better output:** A few hours of investment buys compounding improvements
- **Reduced friction:** AI "gets you" without re-explaining context every time
- **Knowledge accumulation:** Instructions and memory become organisational assets
- **Widening capability gap:** Users who configure pull ahead over time

### Trade-offs

- **Initial investment:** Requires time to configure levers and capture corrections
- **Maintenance overhead:** Instructions need periodic review and updates
- **Privacy considerations:** Memory and tools increase data exposure
- **Platform lock-in:** Heavy configuration in one system makes switching harder

## Related

- [[Concept - RLHF Averaging]] — The underlying problem this pattern solves

## Sources

- Nate B Jones, "90% of AI Users Are Getting Mediocre Output" (2026-02-05)
- Boris Churnney's Claude Code workflow (referenced in video)
