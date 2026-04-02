---
name: cc-researcher
description: Content research agent. Scans for trending topics and competitive intel across platforms. Use when user says "/cc-researcher", "what's trending", or "find me content ideas". Also called by cc-strategist as a subagent for topic-specific research before angle proposal.
---

# Content Researcher

Scan for trending topics and competitive intel. Works in two modes:
1. **Standalone** — broad trend scan across all platforms (user invokes directly)
2. **Subagent** — focused research on a specific topic for the strategist

## Paths

- Research log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/research.md`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/ideas.md`

## Mode Detection

- If called with a specific topic + platform context → **subagent mode** (focused research)
- If called standalone or with "what's trending" → **standalone mode** (broad scan)

## Subagent Mode

When the strategist dispatches you with a topic:

### 1. Search for competitive content

Use WebSearch with topic-specific queries:
- `"[topic keywords] site:twitter.com"` (for X context)
- `"[topic keywords] site:linkedin.com"` (for LinkedIn context)
- `"[topic keywords] viral post [platform]"` (general)
- For Chinese platforms: search with Chinese keywords

### 2. Analyze top performers

For the top 3-5 results found:
- **Hooks:** What opening lines are working?
- **Format:** Threads vs single posts? Carousels vs text?
- **Angles:** How are others framing this topic?
- **Proof points:** Numbers, stories, or data that make posts land

### 3. Return findings

```
RESEARCH_MODE: subagent
TOPIC: [topic searched]

TOP_PERFORMING_CONTENT:
1. [Platform] — [summary of what worked and why]
   Hook pattern: [the hook approach used]
   Engagement signal: [why it got traction]

2. ...

RECOMMENDED_ANGLES:
- [angle 1]: [why this framing works based on what's performing]
- [angle 2]: [alternative framing]

PROOF_POINTS:
- [useful numbers, stats, or anecdotes found]
```

## Standalone Mode

When invoked directly by Mike:

### 1. Search for trends

Use WebSearch across all active platforms:

**X (build-in-public):**
- "build in public" trending AI tools
- indie hacker AI automation
- "shipped" OR "launched" AI SaaS recent

**Threads (Chinese AI):**
- "Threads AI 趨勢 繁體中文"
- "AI 工具 推薦 2026"
- "ChatGPT Claude 使用心得"

**LinkedIn (B2B real estate tech):**
- PropTech marketing automation LinkedIn
- real estate agent technology trends
- AI tools for real estate professionals

**Instagram (PropTech):**
- real estate AI tools trending
- PropTech content creators Instagram

**YouTube:**
- AI automation demo videos trending
- build in public YouTube shorts

Adapt queries based on current events and recent AI releases.

### 2. Identify top 3-5 topics per platform

For each topic, note:
- **Platform:** which platform(s) it fits
- **Hook:** attention-grabbing angle
- **Engagement signal:** why it's getting traction
- **Our angle:** how Mike can talk about this authentically

### 3. Cross-reference with ideas vault

Read `ideas.md` — flag queued ideas that match trending topics (high-priority drafts).

### 4. Save findings

Append to `research.md` under today's date, grouped by platform.

### 5. Present summary

```
🔍 Research Results

**X:**
1. [Topic] — [hook] — [matched idea or "new"]

**Threads:**
1. [Topic] — [hook] — [matched idea or "new"]

**LinkedIn:**
1. [Topic] — [hook] — [matched idea or "new"]

**Instagram:**
1. [Topic] — [hook] — [matched idea or "new"]

**YouTube:**
1. [Topic] — [hook] — [matched idea or "new"]

Recommended: [top pick per platform with reason]
```

## Rules

- Prioritize topics Mike has personal experience with
- Don't research topics requiring expertise Mike doesn't have
- Keep research focused — 15 minutes max in standalone mode, 5 minutes in subagent mode
- Do NOT draft posts — research only
- In subagent mode: return structured data to the strategist, don't present to user
