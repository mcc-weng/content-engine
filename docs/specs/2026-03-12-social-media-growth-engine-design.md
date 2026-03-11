# Social Media Growth Engine — Design Spec

**Date:** 2026-03-12
**Status:** Approved
**Goal:** AI-assisted content creation workflow for Threads (Chinese), maximizing human touch while automating research, writing, and posting.

---

## Overview

A suite of 6 Claude Code skills (`/cc-*`) that form a content creation pipeline. Phase 1 is fully human-triggered — no background automation. The engine helps Mike research, draft, and post Threads content in his authentic voice, targeting non-technical Chinese-speaking professionals interested in AI.

### Core Principle

Post → Listen → Package → Sell. The engine accelerates the "Post" step. Human touch stays in the loop — every post is reviewed before publishing.

---

## Target Platform

- **Phase 1:** Threads (Chinese) — primary and only
- **Phase 2:** Add self-improving feedback loop
- **Phase 3:** Expand to X (English), LinkedIn (English)
- **Phase 4:** Full autonomy (auto-drafting, scheduling, growth planning)

## Target Audience

Non-technical Chinese-speaking professionals, 35-50, curious about AI but intimidated. They want outcomes, not process. Proof, not promises.

## Voice

朋友 + 實驗者 (friend + experimenter). Casual Taiwanese Mandarin. Extracted from real LINE conversations — see Voice Profile reference doc.

---

## Architecture

### Skill Suite (6 skills, Phase 1)

```
~/.claude/skills/
├── cc-capture/
│   ├── SKILL.md
│   └── references/
│       └── ideas-vault-format.md
├── cc-research/
│   ├── SKILL.md
│   └── scripts/
│       └── scan-threads.py          (Phase 2 — cron-based)
├── cc-draft/
│   ├── SKILL.md
│   ├── references/
│   │   ├── anti-ai-patterns.md
│   │   └── post-examples.md
│   └── assets/
│       └── post-templates.md
│   # NOTE: voice-profile.md lives in Obsidian vault (content-voice.md)
│   # cc-draft reads it directly — no copy to avoid drift
├── cc-review/
│   ├── SKILL.md
│   └── references/
│       └── content-calendar.md
├── cc-post/
│   ├── SKILL.md
│   └── scripts/
│       └── post-to-threads.py       (new — borrows auth from threads-poster)
└── cc-recap/
    └── SKILL.md
```

### Data Files (Obsidian Vault)

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/
├── content-log.md          (existing — auto-extracted conversation insights)
├── content-ideas.md        (NEW — ideas vault, raw inputs + queue)
├── content-voice.md        (NEW — voice profile, single source of truth)
├── content-research.md     (NEW — created when /cc-research is built)
└── content-posts.md        (NEW — log of published posts, archive after 30 entries)
```

### Data Flow

```
[Mike's brain] ──→ /cc-capture ──→ content-ideas.md
[Claude convos] ──→ cron extraction ──→ content-log.md
[Web] ──→ /cc-research ──→ content-research.md
                                ↓
    content-ideas.md + content-log.md + content-research.md
                                ↓
                    /cc-draft ──→ voice-profile.md + anti-ai-patterns.md
                                ↓
                    /cc-review ──→ content-calendar.md
                                ↓
                    /cc-post ──→ post-to-threads.py ──→ Threads
                                ↓
                    /cc-recap ──→ content-posts.md ──→ streak + suggestions
```

---

## Skill Specifications

### 1. /cc-capture — Raw Idea Intake

**Frontmatter:**
```yaml
---
name: cc-capture
description: Capture raw content ideas into the ideas vault. Use when user says "/cc-capture", "capture this for content", "idea for a post", or "save this for threads". Does NOT trigger on general URL sharing or non-content tasks.
---
```

**Workflow:**
1. Accept any input — text, URL, screenshot, half-formed thought
2. If URL: fetch and summarize the content
3. Classify type: `thought` | `link` | `demo` | `reference` | `hot-take`
4. Append structured entry to content-ideas.md (format in references/ideas-vault-format.md)
5. Suggest angle if obvious, otherwise just store
6. One-line confirmation

**Ideas Vault Format:**
```markdown
## Queue
- **[YYYY-MM-DD]** [type] Short description
  - Raw: (original input verbatim)
  - Angle: (suggested angle, or "none yet")
  - Source: (URL if applicable)
  - Status: raw | drafted | posted

## Used
- **[YYYY-MM-DD]** [type] Short description
  - Posted: YYYY-MM-DD
  - Link: (threads URL)
```

### 2. /cc-research — Trend & Topic Scanner

**Frontmatter:**
```yaml
---
name: cc-research
description: Research trending topics and content opportunities for Threads. Use when user says "/cc-research", "what's trending on threads", or "find me content ideas". Does NOT trigger on general web research or non-content questions.
---
```

**Workflow:**
1. Use WebSearch as primary tool to find trending Chinese AI content on Threads/X
2. Identify top 3-5 topics getting engagement in target niche
3. For each: note hook, engagement level, why it's working
4. Cross-reference with ideas vault — flag matching queued ideas
5. Cross-reference with content-log.md — flag matching extracted insights
6. Deposit findings to content-research.md with date header
7. Present: trending topics, recommended angles, matched ideas

**Tools used:** WebSearch (primary — Google results for trending Threads/AI topics), Playwright (fallback — direct page scraping, but unreliable due to Meta's anti-scraping. Aspirational for Phase 2.)

### 3. /cc-draft — Post Writer

**Frontmatter:**
```yaml
---
name: cc-draft
description: Draft Threads posts in Mike's authentic voice. Use when user says "/cc-draft", "write a threads post", or "draft something for threads". Does NOT trigger on general writing tasks like docs, emails, or code comments.
---
```

**Workflow:**
1. **Always first:** Read content-voice.md from Obsidian vault and references/anti-ai-patterns.md
2. Accept input: specific idea, idea from queue, or from research findings
3. Read source material: content-ideas.md, content-log.md, research findings
4. Read references/post-examples.md for style reference
5. Draft post following voice profile:
   - 朋友 + 實驗者 tone
   - Taiwanese Mandarin casual vocabulary
   - Under 300 characters unless story post
   - Hook first, engagement close
6. **Self-check gate:** Review against anti-AI patterns. If detected, rewrite.
7. Present: post text, source idea, character count, "does this sound like you?"
8. Accept inline edits or "reject and try again from scratch"
9. On approval, update ideas vault status to `drafted`

**Character count:** 300 is a style guideline, not an API limit. Count Unicode characters (each Chinese char = 1). Threads API limit is 500 chars — stay well under for readability.

### 4. /cc-review — Daily Dashboard

**Frontmatter:**
```yaml
---
name: cc-review
description: Show daily content dashboard with queued drafts, recent posts, and posting streak. Use when user says "/cc-review", "content status", or "what should I post today". Does NOT trigger on code reviews or PR reviews.
---
```

**Workflow:**
1. Read content-ideas.md — count by status
2. Read content-posts.md — last 3-5 posts with dates
3. Calculate posting streak (consecutive days)
4. Check content-calendar.md for today's planned topic
5. Cross-reference queue with recent research
6. Present dashboard:
   ```
   Content Status
   Queue: X raw | Y drafted | Z ready
   Recent: [last 3 posts with dates]
   Streak: N days
   Suggested for today: [topic] — [reason]
   ```
7. User picks → suggest next command (e.g. "Run `/cc-draft` with idea #3"). Handoff is manual — user invokes the next skill.

**Content Calendar:**
```
Weekly rhythm:
- Mon: Demo post (show something you built)
- Tue: Curated insight (translate English AI news)
- Wed: Hot take or personal journey
- Thu: Demo post or audience response
- Fri: Curated insight or trending topic
- Sat: Personal journey / week reflection
- Sun: Audience question / engagement post

Flexible — trends override calendar.
```

### 5. /cc-post — Publish to Threads

**Frontmatter:**
```yaml
---
name: cc-post
description: Publish approved content to Threads. Use when user says "/cc-post", "publish to threads", or approves a draft for posting. Does NOT trigger on general publishing or deploy tasks.
---
```

**Workflow:**
1. Accept post text (direct or from approved draft)
2. Final confirmation: show post, ask "Post this? (y/n)"
3. Execute scripts/post-to-threads.py
4. On success:
   - Update content-ideas.md: move to Used, add post date
   - Append to content-posts.md: date, text, threads URL
   - Confirm with link
5. On failure: show error, suggest retry

**Posting script:** New module at `~/Desktop/Projects/content/scripts/post-to-threads.py`.
- **Sync** (not async) — runs from shell via Claude Code, uses `requests` not `httpx`
- Borrows auth/API patterns from `~/Desktop/Projects/threads-poster/app/services/threads.py`
- Step 1: Create container (POST to graph.threads.net)
- Step 2: Publish (POST with creation_id)
- Step 3: Get permalink
- **Token management:** Threads long-lived tokens expire ~60 days. Stored in env var `THREADS_ACCESS_TOKEN`. On 401 error, skill should tell user to regenerate token and update env var. Auto-refresh is Phase 2.
- **Error handling:** Retry once on 5xx. On 4xx, show error message and suggest fix. On network error, show and abort.

### 6. /cc-recap — End of Day Summary

**Frontmatter:**
```yaml
---
name: cc-recap
description: End-of-day content summary with streak tracking and tomorrow's suggestions. Use when user says "/cc-recap", "content recap", or "how's my posting streak".
---
```

**Workflow:**
1. Read content-posts.md — what was posted today
2. Read content-ideas.md — what's queued
3. Calculate streak
4. Check content calendar for tomorrow
5. Check content-log.md for new insights captured today
6. Present:
   ```
   Today: [what you posted, or "nothing yet"]
   Streak: N days
   Queue: X ideas ready
   New insights: Y captured today
   Tomorrow: [suggestion from calendar + best queued idea]
   ```

---

## Voice Profile

### Tone: 朋友 + 實驗者

Casual friend who experiments with AI and shows receipts. Not a teacher, not a guru.

### Voice DNA (from real LINE conversations)

**Vocabulary palette:**
- Surprise: 靠、傻眼、真假、蝦米、三小
- Approval: 水喔、讚喔、確實、挺好的
- Casual: 好喔、恩對啊、喔喔、對啊
- Dismissal: 別鬧、別吵、少來、你想太多了
- Humor: 哈哈哈哈 (signature softener, use liberally)
- Playful (sparingly): 偶 for 我, 迷有 for 沒有, 真嘟假嘟

**Sentence patterns:**
- Start with interjections: 誒、欸、喔對、啊呀
- Under 20 characters per sentence when possible
- Break into 2-3 short lines, not one block
- End casual, not neat — question, reaction, or just... stop
- Use 拍謝 not 抱歉, 謝拉 not 謝謝

**How to explain technical things:**
- Result first, then shortest explanation
- Never more than 2-3 lines before checking in
- Specific details always ("3間房子", "凌晨2點")

**Rules:**
- Hook first — result, surprise, contradiction
- End with engagement — question, CTA, or "你覺得呢？"
- 你 not 您, under 300 chars, no jargon without inline explanation
- Never sound like a tutorial. Sound like "你一定要看這個"

### Anti-AI Patterns

**Never:**
- Perfect parallel structure
- Exactly 3 of anything
- "在這個...的時代" / "讓我們來看看" / "不得不說"
- Neat conclusions / moral of the story
- Balanced takes / hedging
- Same sentence lengths
- Transitions between paragraphs
- 您 anywhere

**Always:**
- Vary sentence length wildly
- Start mid-thought sometimes
- Incomplete sentences
- Strong opinions without hedging
- 口語 not 書面語
- Specific numbers/details
- Emotional reactions ("我嚇到" not "這非常有趣")
- Some posts just 2-3 sentences

**Self-check:**
1. Could any AI account have written this? → rewrite
2. Is there a detail only Mike would know? → add one
3. Friend texting or teacher lecturing? → must be friend
4. Would Mike say this out loud? → read it aloud

---

## Integration Points

**Existing systems (unchanged):**
- content-log.md auto-extraction cron — keeps running, feeds into /cc-draft as source
- threads-poster project — untouched, but auth patterns borrowed for new posting script

**New posting module:**
- `~/Desktop/Projects/content/scripts/post-to-threads.py`
- Uses Threads Graph API v1.0 (same as threads-poster)
- Env vars: THREADS_ACCESS_TOKEN, THREADS_USER_ID

**Available tools for /cc-research:**
- WebSearch — primary, quick trend scanning via Google
- Playwright — fallback/aspirational, direct Threads scraping (unreliable due to Meta anti-scraping)

**Content calendar:** Static template embedded in cc-review/references/content-calendar.md. Not a dynamic file in Phase 1. Dynamic generation is Phase 2+.

**Concurrent writes:** Low risk in Phase 1 (manual triggers, low frequency). The cron writes to content-log.md while skills write to content-ideas.md and content-posts.md — different files. No mitigation needed for Phase 1.

**Ideas vault archival:** When the "Used" section of content-ideas.md exceeds 30 entries, move older entries to content-ideas-archive.md. Can be manual or added to /cc-recap in Phase 2.

---

## Testing Plan

### Level 1: Trigger Testing
- 10 prompts that SHOULD trigger each skill — verify 90%+ rate
- 10 prompts that should NOT trigger — verify 0% false positives
- False positive examples: "draft this PR", "review my code", "post to github"

### Level 2: Voice Fidelity
- Generate 5 drafts with /cc-draft
- Lineup with 5 real LINE messages (adapted to post format)
- Blind test: can you tell which is AI?
- Ask a friend to blind test

### Level 3: A/B Against Sprint Calendar
- Take planned 7-day sprint posts
- Write manually, then generate with /cc-draft
- Compare side by side — AI version should feel like natural alternative

### Level 4: Iterative Scoring
- Score each draft 1-5: "sounds like me" / "would post this"
- Under 4 → identify what's off → update voice profile
- Track scores over time

### Level 5: End-to-End Flow
- Full pipeline: /cc-capture → /cc-draft → /cc-post (test account)
- Verify data files update correctly at each step
- Time the flow — target under 10 minutes idea to published

### Level 6: Anti-AI Detection
- Run generated posts through GPTZero, ZeroGPT
- Flagged as AI → analyse triggers → update anti-AI patterns
- Goal: consistently pass as human-written

---

## Build Order

1. `/cc-capture` — simplest, immediate value, validates ideas vault format
2. `/cc-draft` — core skill, most complex, battle-tests voice profile
3. `/cc-post` — wraps new posting script, closes capture→draft→post loop
4. `/cc-review` + `/cc-recap` — dashboard and tracking layer
5. `/cc-research` — depends on web search tooling, least urgent

---

## Phases

### Phase 1: Manual Content Machine (now)
- 6 skills, all human-triggered
- No background automation, no analytics scraping
- Engagement data is manual
- Solves: writing friction, research friction, consistency friction

### Phase 2: Feedback Loop (~2-4 weeks)
- `/cc-analyse` skill — reviews performance, updates voice profile + calendar + examples
- Engagement tracking (scrape or manual log)
- Research cron (scan-threads.py runs daily)
- /cc-recap upgrade with engagement summary
- Voice profile evolution from winning posts

### Phase 3: Multi-platform (~1-2 months)
- Platform adapters: /cc-draft --platform x, --platform linkedin
- Cross-posting support in /cc-post
- Platform-specific voice profiles
- Content repurposing: one idea → multiple platform-adapted posts

### Phase 4: Full Autonomy (when overwhelmed)
- Auto-drafting from queue + research
- Scheduling at optimal times
- Weekly growth strategy recommendations
- Auto-generated content calendars

---

## Dependencies

- Threads API access (borrow auth from threads-poster)
- WebSearch + Playwright (already available in Claude Code)
- No new infrastructure, databases, or servers
- Skills live in ~/.claude/skills/ (global, available across all projects)

## Non-Goals (Phase 1)

- No dashboard UI
- No analytics scraping
- No multi-platform
- No auto-posting without approval
- No new projects to build from scratch (content comes from existing 5 projects)
