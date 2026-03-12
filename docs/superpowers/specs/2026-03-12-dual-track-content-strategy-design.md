# Dual-Track Content Strategy: Building My Way to America

## Overview

A content strategy redesign that shifts from single-platform Chinese content to a dual-track English + Chinese approach, built around a central narrative: going from $0 in Taiwan/Melbourne to $20k/month in internet income to relocate to the US.

This spec covers positioning, platform strategy, content pillars, monetization path, and the required updates to the existing content engine.

## Context

### Current State
- Existing social media growth engine: 6 Claude Code skills (`cc-capture`, `cc-draft`, `cc-post`, `cc-review`, `cc-recap`, `cc-research`)
- Chinese voice profile extracted from real LINE conversations
- Threads posting script (Python, Threads Graph API)
- Content data files in Obsidian vault
- Content extraction cron job feeding insights from Claude conversations
- Target audience: non-technical Chinese-speaking professionals, 35-50, curious about AI

### What's Changing
- Adding English content track on X (Twitter)
- Shifting from "AI experimenter" positioning to "building my way to America" narrative
- Monetization becomes central to the content (freelance AI automation → productized service → SaaS)
- Audience expands to English-speaking indie hackers, entrepreneurs, AI builders

## Identity & Positioning

**Brand narrative:** "Building my way from Taiwan to America — one AI automation at a time"

**Who Mike is to the audience:** A Taiwanese/Melbourne-based developer building AI automation businesses from scratch, documenting the entire journey transparently, with the goal of hitting $20k/month and relocating to the US to be around the entrepreneurs he admires.

**What makes this followable:**
- Real stakes — not a side project, it's a life trajectory
- Bilingual Asian founder in the AI space — underrepresented voice
- Zero to something, documented live — people follow transformation, not perfection
- The emotional pull of the immigrant dream + the practical pull of AI expertise

**English voice:**
- Direct, honest, slightly raw
- No corporate polish, no guru energy
- Smart friend texting you what he learned today
- OK to mix in occasional Chinese/Taiwanese expressions — part of identity

**Chinese voice:** Existing 朋友 + 實驗者 (friend + experimenter) positioning remains. The US dream adds a new emotional layer to this existing voice.

## Platform Strategy

### X (Twitter) — English Track (Primary for growth)
- Build-in-public community lives here
- Algorithmic reach rewards consistency and engagement
- Quote-tweet and reply culture enables engagement with bigger accounts
- 280 character limit per post (threads for longer content)

### Threads — Chinese Track (Maintained)
- Growing platform, generous algorithm for new creators
- Existing infrastructure (posting script, voice profile, skills)
- 500 character limit
- 台灣人追美國夢 angle resonates differently here — more personal/emotional

### Cadence
- X: 1-2 posts per day
- Threads: 1 post per day
- Same core story, adapted per audience — not translated

### LinkedIn (Deferred to Month 2-3)
- Repurpose best X posts for consulting/freelance funnel
- "AI automation consultant" positioning for client acquisition

## Content Pillars

### Shared Pillars (Both Platforms, Adapted Per Language)

**1. Build Logs (40%)**
What you shipped, what you're working on, demos.

- X example: "Shipped an AI automation for a client that saves them 5hrs/week. Here's how it works:"
- Threads example: "幫客戶做了一個 AI 自動化，省了他們每週5小時。做法是這樣："

**2. Revenue/Progress Transparency (20%)**
Monthly income, client wins, failures, expenses.

- X example: "March: $0 → $850. Two clients. One ghosted. Here's what I learned."
- Threads example: "三月收入報告：從0到$850。兩個客戶，一個消失了。學到的事："

**3. Dream Posts (15%)**
Why the US, what entrepreneurship means, the emotional journey.

- X: immigrant founder narrative, the loneliness, the motivation
- Threads: 台灣人追美國夢, more personal/emotional for Chinese audience

### X-Only Pillar

**4. AI Expertise Drops (25%)**
Tutorials, tool breakdowns, vibe coding demos, hot takes on AI tools.

- Authority builder for the English indie hacker crowd
- Attracts freelance clients directly
- Demonstrates competence without selling

### Threads-Only Pillar

**4. Curated AI Insights (25%)**
Translating English AI world developments for Chinese audience with personal take.

- Existing content engine strength
- Maintains 朋友 + 實驗者 positioning
- Bridge between English AI world and Chinese-speaking audience

## Monetization Path

### Month 1-2: Freelance AI Automation
- Cold outreach + content that demonstrates capability
- Target: small businesses, solopreneurs needing AI workflows
- Price: $500-2000 per project
- Every project becomes content (build logs, case studies)

### Month 3-4: Productize
- Identify most commonly requested automations
- Package as fixed-price service (e.g., "I'll build your AI email responder for $1500, done in 3 days")
- Content shifts from "look what I built" to "here's my offer"

### Month 5-6+: Scale or SaaS
- Hire/outsource to scale service, or build self-serve SaaS from client patterns
- Audience becomes launch distribution

### Revenue Checkpoints
- Month 3: $1-3k/month (2-3 freelance clients)
- Month 6: $5-8k/month (productized service + recurring clients)
- Month 9-12: $15-20k/month (scaled service or SaaS revenue)

These targets are directional. Actual numbers shared publicly become content regardless of trajectory.

## Content Engine Updates

### Keep As-Is
- `/cc-capture` — language-agnostic idea capture
- `/cc-review` — daily dashboard (extend to show both tracks)
- `/cc-recap` — end-of-day summary (extend to cover both tracks)
- Obsidian vault as single source of truth
- Content extraction pipeline from Claude conversations
- Human-in-loop for Phase 1

### Needs Updating

**`/cc-draft` skill**
- Add English X mode alongside existing Chinese Threads mode
- Different voice profile per language
- Different length constraints (X: 280 chars, Threads: 500 chars)
- Platform parameter: `--platform x` or `--platform threads`

**`/cc-post` skill**
- Add X (Twitter) API posting capability
- Platform selection at post time

**`/cc-research` skill**
- Expand to scan English X trending topics (build-in-public, AI, indie hackers)
- Currently only scans Chinese AI content

**Content calendar**
- Update to reflect dual-track pillars
- Different pillar weights per platform

**Ideas vault (`content-ideas.md`)**
- Add `platform` field: `x` | `threads` | `both`
- Ideas can target one or both platforms

### New Things Needed

**English voice profile**
- Develop over time from Mike's real English writing
- Start with guidelines (direct, raw, no polish) and refine after 2-3 weeks of posts
- Store as `content-voice-en.md` alongside existing `content-voice.md` (Chinese)

**X API posting script**
- New Python script for X/Twitter API integration
- Same pattern as existing `post-to-threads.py`
- Env vars: X API keys

**English anti-AI patterns**
- Different tells than Chinese (e.g., "In today's rapidly evolving...", "Let's dive in", "Here's the thing:")
- Store alongside existing Chinese anti-AI patterns

## Launch Plan

### Week 1: Start Posting
- Set up X account (or activate existing one)
- Write "day 1" post on both platforms — who you are, the goal, the journey starts now
- Post daily on both. Short posts. Build the habit before optimizing
- No automation needed — copy-paste is fine

### Week 2-3: Start Outreach
- Cold DM/email potential AI automation clients while posting
- Outreach conversations become content ("got rejected by 5 prospects today")
- First client is the unlock — everything compounds from there

### Week 4+: Settle Into Rhythm
- 1-2 posts per day per platform
- Weekly revenue/progress update post
- Monthly milestone post with reflection
- Begin updating content engine skills as needed

### What's NOT Needed Before Starting
- Perfect English voice profile — develops as you write
- X posting automation — copy-paste for now
- Updated skills/engine — infrastructure catches up to content, not the other way around
- LinkedIn presence — defer to month 2-3

## Architecture Decisions

1. **Dual-track, not bilingual** — each platform gets native content, not translations
2. **Same data layer** — both tracks share Obsidian vault, ideas queue, and extraction pipeline
3. **Platform field on ideas** — ideas tagged for `x`, `threads`, or `both`
4. **English voice develops organically** — start with guidelines, formalize after real writing samples exist
5. **X integration is additive** — existing Threads infrastructure untouched, X capability layered on top
6. **Content and monetization are the same thing** — every client project is content, every post is a client magnet
7. **Start before the system is ready** — posting day 1 matters more than having perfect automation

## Success Criteria

- Posting consistently on both platforms within week 1
- First freelance client within month 1-2
- English voice profile documented by end of month 1
- Revenue tracked publicly monthly
- Content engine updated to support dual-track by end of month 1
