---
type: Concept
title: "RLHF Averaging"
created: 2026-02-05
tags:
  - topic/ai
  - topic/machine-learning
confidence: high
---

# RLHF Averaging

> **Definition:** The systematic tendency of AI models trained via Reinforcement Learning from Human Feedback (RLHF) to produce median responses that satisfy the broadest range of users rather than being optimised for any specific individual's needs.

## Overview

RLHF Averaging describes the mechanical reason why default AI systems often feel "slightly off"—not wrong, but not quite right for your specific situation. Modern AI assistants like ChatGPT, Claude, and Gemini undergo RLHF training where human raters compare multiple responses to the same prompt and select the "better" one. Over millions of such comparisons, the model learns to produce outputs that would satisfy most people, not you specifically.

The training process encodes "what would most people want here?" as the optimisation target. This creates what's been called the "Pizza Hut problem"—like a restaurant optimising one dish for the widest possible audience, the result is competent and inoffensive but never quite matches individual preferences.

## Key Characteristics

- **Median Optimisation:** Models learn to satisfy the middle of the human preference distribution, not any individual user
- **Rater Proxy Problem:** Human raters evaluating outputs are not experts in your field, don't know your constraints, and aren't familiar with your preferences
- **Statistically Generic:** Every default response is optimised for a "hypothetical typical person" who doesn't exist
- **Competent but Off:** Output is technically correct and grammatically sound, but feels slightly misaligned with actual needs
- **Universal Trade-off:** The mechanism that prevents poor responses also prevents highly personalised ones

## Why It Matters

### For Individual Users

RLHF Averaging explains why:

- Your AI output always feels "slightly off" despite being technically correct
- Recommendations feel generic rather than personalised
- Advice applies generally but misses your constraints
- Generated content requires significant editing to match your voice

Understanding the mechanism reveals it's not that "AI is just okay"—it's that default configurations are systematically biased toward the median. This is **fixable** through deliberate configuration.

### For Knowledge Workers

Professional work demands precision, nuance, and context. RLHF Averaging undermines this:

- **Decision records:** Generic outputs miss organisational decision frameworks and risk appetite
- **System designs:** Median architecture patterns don't account for specific non-functional requirements
- **Analysis:** Generic assessments don't weight criteria according to your priorities

## Mitigations

Four distinct configuration surfaces exist to steer away from the median:

1. **Memory:** AI retains information about you across conversations
2. **Instructions:** Persistent context about who you are and how you want AI to behave
3. **Tools:** Capabilities the AI can use (web search, code execution, file access, MCP connectors)
4. **Style:** Tone, personality, and communication preferences

See [[Concept - Context Engineering for AI]] for detailed implementation of these four levers.

### The Compounding Correction Workflow

Most people correct AI in their head and move on. People getting 10x results **capture corrections and encode them back into the system:**

1. AI produces something "not quite right"
2. Identify what's wrong
3. Add a rule to instructions so it doesn't happen again
4. File becomes a living document that compounds over time

## Sources

- Nate B Jones, "90% of AI Users Are Getting Mediocre Output" (2026-02-05)
- Anthropic RLHF papers
- OpenAI RLHF papers
