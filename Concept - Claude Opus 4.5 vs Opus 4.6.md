---
type: Concept
title: Claude Opus 4.5 vs Opus 4.6
created: 2026-02-05
tags:
  - topic/ai
  - topic/machine-learning
confidence: high
---

# Claude Opus 4.5 vs Opus 4.6

Opus 4.6 was released on 5 February 2026, approximately 10 weeks after Opus 4.5 (24 November 2025). Anthropic now classifies Opus 4.5 as a **legacy model**, recommending migration to 4.6.

## At a Glance

| Specification            | Opus 4.5                   | Opus 4.6                               |
| ------------------------ | -------------------------- | -------------------------------------- |
| **Release date**         | 24 Nov 2025                | 5 Feb 2026                             |
| **Model ID**             | `claude-opus-4-5-20251101` | `claude-opus-4-6`                      |
| **Context window**       | 200K tokens                | 200K (standard) / **1M tokens** (beta) |
| **Max output**           | 64K tokens                 | **128K tokens**                        |
| **Knowledge cutoff**     | May 2025                   | May 2025                               |
| **Input pricing**        | $5 / MTok                  | $5 / MTok                              |
| **Output pricing**       | $25 / MTok                 | $25 / MTok                             |

Pricing is identical. Both represent a 67% cost reduction from Opus 4.1 ($15/$75).

## Benchmark Improvements

| Benchmark                  | Opus 4.5 | Opus 4.6    | Measures                             |
| -------------------------- | -------- | ----------- | ------------------------------------ |
| **ARC AGI 2**              | 37.6%    | **68.8%**   | Novel problem-solving                |
| **Terminal-Bench 2.0**     | ~50%     | **65.4%**   | Agentic coding in real terminals     |
| **GDPval-AA (Elo)**        | ~1,416   | **1,606**   | Economically valuable knowledge work |
| **MRCR v2 (8-needle, 1M)** | N/A      | **76%**     | Long-context fact-finding            |
| **Humanity's Last Exam**   | Strong   | **Highest** | Complex multidisciplinary reasoning  |

The ARC AGI 2 improvement is particularly striking—nearly doubling. For context, GPT-5.2 scored 54.2% and Gemini 3 Pro scored 45.1% on the same benchmark.

## New Capabilities in Opus 4.6

### 1M Token Context Window (Beta)

The first Opus-class model with 1M token context. On the MRCR v2 benchmark (8-needle, 1M tokens): Opus 4.6 scored 76% vs Sonnet 4.5's 18.5%.

### Agent Teams (Research Preview)

Multiple AI agents can work on different parts of a task in parallel, coordinating directly with each other.

### Adaptive Thinking

Exclusive to Opus 4.6. The model dynamically selects when deeper reasoning would be beneficial, optimising between thoroughness and speed.

### Effort Controls

Four configurable levels (low, medium, high, max) trading off intelligence, speed, and cost.

### Context Compaction (Beta)

Automatic summarisation of older context during long-running tasks, allowing agents to sustain longer sessions.

## Coding and Agent Performance

- **Plans more carefully** before executing complex tasks
- **Sustains agentic tasks for longer** without degradation
- **Operates more reliably in larger codebases** (aided by 1M context)
- Holds **highest score on Terminal-Bench 2.0** for agentic coding
- Uncovered approximately **500 zero-day flaws** in open-source code during testing

## Why It Matters

- **1M context** enables processing entire codebases or document corpora in a single prompt
- **128K output** doubles maximum output for long-form generation
- **Adaptive Thinking** improves quality on complex multi-step tasks without manual configuration
- **Agent Teams** enables parallel sub-agent workflows
- **Context Compaction** extends autonomous session duration

## Sources

- [Introducing Claude Opus 4.6 — Anthropic](https://www.anthropic.com/news/claude-opus-4-6)
- [Introducing Claude Opus 4.5 — Anthropic](https://www.anthropic.com/news/claude-opus-4-5)
- [Models Overview — Claude API Docs](https://platform.claude.com/docs/en/about-claude/models/overview)
