# Content Engine v2: Multi-Platform Redesign

## Overview

Redesign the content creator engine (cc-* skills) from a 2-platform system (Threads + X) to a 5-platform system (RED, Instagram, Threads, X, LinkedIn) with new voice profiles, integrated humanizer, and cross-platform adaptation.

## Context

### Current State
- 7 skills: cc-capture, cc-brainstorm, cc-draft, cc-post, cc-review, cc-recap, cc-research
- 2 platforms: Threads (Traditional Chinese) + X (English)
- Voice profiles: `voice.md` (Chinese, LINE chat-derived) + `voice-en.md` (English, inline guidelines)
- Posting scripts: `post-to-threads.py`, `post-to-x.py`
- Scaffolds: 6 types (Demo, Curated Insight, Hot Take, Personal Journey, Rant/Reaction, Question)
- Hooks: 8 types (Bold Claim, Pain Point, Curiosity Gap, Numbers First, Reverse Contrast, Age+Result, Mid-Action Story, Raw Rant)

### Problems
1. Voice profiles are derived from LINE chat history — too casual and private-chat for public content
2. Only 2 platforms supported; new strategy requires 5
3. No humanizer pass — drafts can sound AI-generated
4. No cross-platform adaptation flow
5. Scaffolds, hooks, scoring, and anti-AI patterns are Threads-specific

### What This Spec Covers
- Platform module architecture for 5 platforms
- New voice profiles (full rewrite, not LINE-derived)
- Bilingual humanizer integrated into drafting
- New `/cc-adapt` skill for cross-platform native rewrites
- Updates to all existing cc-* skills for platform awareness
- New `post-to-instagram.py` posting script

---

## Architecture

### Approach: B+ (Platform Modules with Phase 2 Data Model Upgrades)

Workflow-based skills stay (brainstorm → draft → post). Platform-specific rules live in modular reference files loaded by the draft skill. Phase 2 extends data model (streaks, calendar, dashboards) after real posting data exists.

### File Structure Changes

```
cc-draft/
  references/
    platforms/
      red.md              ← NEW: format, tone, strategy, anti-patterns, examples
      instagram.md        ← NEW
      threads.md          ← NEW (extracted from current inline rules)
      x.md                ← NEW (extracted from current inline rules)
      linkedin.md         ← NEW
    humanizer-en.md       ← NEW: English AI-tell patterns + banned words
    humanizer-zh.md       ← NEW: Chinese AI-tell patterns + banned words
    anti-ai-patterns.md   ← REMOVE (replaced by humanizer-zh.md)
    anti-ai-patterns-en.md ← REMOVE (replaced by humanizer-en.md)
    hook-types.md         ← UPDATE: platform-aware hooks
    cta-bank.md           ← UPDATE: platform-aware CTAs
    scoring-rubric.md     ← UPDATE: per-platform scoring
    post-examples.md      ← UPDATE: examples per platform
  assets/
    post-templates.md     ← UPDATE: scaffolds per platform

Obsidian vault (content/):
  voice-zh.md             ← REWRITE: Traditional Chinese voice (RED + Threads)
  voice-en.md             ← REWRITE: English voice (Instagram + X + LinkedIn)

scripts/
  post-to-instagram.py    ← NEW: Instagram carousel API
  post-to-threads.py      ← EXISTS
  post-to-x.py            ← EXISTS

New skill:
  cc-adapt/SKILL.md       ← NEW: cross-platform adaptation
```

### Loading Pattern

When `/cc-draft --platform <platform>` runs:

```
platform = red
  → load platforms/red.md        (format rules, strategy, anti-patterns)
  → load voice-zh.md             (voice)
  → load humanizer-zh.md         (AI-tell filter)
  → load post-templates.md       (scaffolds — red section)
  → load hook-types.md           (hooks — red section)
  → generate draft
  → humanizer self-check (scan + rewrite flagged lines)
  → scoring pass (per platform rubric)
  → present to user
```

Language routing:
- Chinese platforms (RED, Threads) → `voice-zh.md` + `humanizer-zh.md`
- English platforms (Instagram, X, LinkedIn) → `voice-en.md` + `humanizer-en.md`

---

## Platform Modules

Each file in `references/platforms/` follows this structure:

```markdown
# [Platform] Module

## Format Spec
## Algorithm Signals
## Tone Rules
## Content Strategy
## Hashtag Strategy
## Anti-Patterns
## Example Posts
```

### Platform Summary (from research)

| | RED | Instagram | Threads | X | LinkedIn |
|---|---|---|---|---|---|
| **Format** | 300-800 char note + images (600+ ideal) | 8-10 slide carousel | 100-300 char text | 280 char text | 1,300-1,900 char text |
| **#1 Signal** | Saves | Dwell time + swipes | Replies | Conversation depth | Saves |
| **Hashtags** | 4-7 (1-2 precise + 3-5 long-tail) | 3-5 relevant | Topic tags | 0-2 max | 3-5 relevant |
| **Language** | Traditional Chinese | English | Traditional Chinese | English | English |
| **Posting** | Manual (no API) | Automated (script) | Automated (script) | Automated (script) | Manual (Month 2) |
| **Cadence** | 5-7/week | 3-5/week | 3-5/week | 3-5/week | 2-5/week (Month 2) |
| **Best time** | 7-10 PM | Wed 11AM-1PM | Wed 7AM | Wed 12-1PM | Tue-Thu 8-10AM |

### RED (Xiaohongshu)

**Format:** Long-form image-text notes. Target 600-800 characters (hard minimum 300 for shorter topics). 60%+ originality required. Cover image in 3:4 vertical ratio with bold text overlay. Subject occupies 70% of frame. Resolution 1080P+.

**Algorithm:** CES scoring — click-through rate, completion rate, interaction value. Saves are the strongest signal (saves > shares > comments > likes). Posts get 200-500 initial test impressions; engagement in first 2 hours determines broader distribution. Search traffic is ~50% of total — title front 10 characters carry 60%+ weight for search ranking. Accounts active 180+ days get bonus exposure.

**Tone:** KOC (Key Opinion Consumer) style — authentic, personal, detailed honest reviews. Practical and actionable. Relatable, down-to-earth. Avoid corporate or overly polished tone.

**Content strategy:** Research drops (25%), Build logs (30%), Buyer guides (25%), Case studies + offers (20%). 70% buyer-facing, 30% agent-facing.

**Hashtags:** 1-2 precise keyword tags + 3-5 long-tail tags. Build keyword library using "region + audience + scenario" combinations (e.g., #澳洲買房 #海外買家 #雪梨房產).

**Anti-patterns:**
- Superlatives ("全網最好用", "行業最低價") cause direct throttling
- Personal contact info (WeChat, phone, email) = traffic diversion violation
- QR codes, external URLs, other platform watermarks = violation
- Fake personas without evidence get flagged

**Awareness:** RED policy requires AI-assisted content labeling ("AI輔助創作"). In practice, content that goes through brainstorm → draft → human edit → manual posting is sufficiently modified. Note for reference, not a hard gate.

**Scaffolds adapt as:** Long-form note with headers. Hook in title (first 18 chars = 2 core keywords). Body follows scaffold flow but expanded to 600+ chars. End with engagement question + hashtags.

### Instagram

**Format:** Carousels — 8-10 slides for maximum engagement. 4:5 portrait ratio (1080x1350px). Each slide: bold header, minimal text (under 20% text overlay), hook under 12 words. Every swipe is a distinct engagement event, so more slides = more signal to the algorithm.

**Algorithm:** Dwell time + swipe-through velocity are primary signals. Every swipe = distinct engagement event. Saves are highest-value signal. Completion rate above 60% is critical.

**Tone:** Educational, value-driven, professional but personal. Clean design with consistent brand colors (2-3 colors, 1-2 fonts). Content people want to save and reference.

**Content strategy:** Research drops (25%), Build logs (35%), Personal brand (20%), Offers (20%). 70% agent-facing, 30% personal brand.

**Hashtags:** 3-5 highly relevant tags. Keyword-rich captions generate 30% more reach and 2x more likes than hashtag-heavy posts.

**Anti-patterns:**
- Inconsistent design across slides (mixing fonts, colors, spacing)
- Cluttered slides with too much text or low-contrast text
- Mixing aspect ratios within a carousel (first slide dictates all)
- Weak/absent CTAs

**Scaffolds adapt as:** Carousel flow — Slide 1: hook/promise (bold text, answers "is this for me?"), Slides 2-9: value delivery following scaffold body, Final slide: CTA ("Save this", "DM me", "Share with someone who needs this"). Caption: 150-300 chars summarizing the post + hashtags.

**Image creation:** `/cc-draft` and `/cc-adapt` output slide text and caption only. User creates visual slides manually (e.g., Canva, Figma, or other design tool). The engine's scope is text generation, not image generation. `post-to-instagram.py` accepts publicly accessible image URLs — user uploads designed slides to an image host (e.g., Cloudinary, S3, Imgur) before posting.

### Threads

**Format:** Short text posts, 100-300 chars. 500 char platform limit is ceiling, not target. Conversation-sparking content dominates.

**Algorithm:** Replies are the strongest engagement signal. Low-quality engagement bait gets suppressed. Topic tags generate more views. Median engagement rate 6.25% (73% higher than X).

**Tone:** Conversational, witty, opinion-driven. Authenticity over polish. Questions and hot takes that invite replies.

**Content strategy:** Conversational research (35%), Build updates (35%), Hot takes (30%). 60% buyer-facing, 40% casual updates.

**Hashtags:** Topic tags on every post for discovery.

**Anti-patterns:**
- "Follow for follow" or "Like if you agree" = engagement bait suppression
- Posting identical replies across multiple threads (bot behavior)
- Scheduling tools can backfire (Meta detects automation)
- Recovery: stop posting 48 hours if shadowbanned

**Scaffolds adapt as:** Current scaffolds + hooks already optimized for Threads. Maintain existing format. Under 300 chars, mobile-first pacing, integrated CTAs.

### X (Twitter)

**Format:** Short text posts under 280 chars. Threads (2-4 posts) for longer ideas, max 1 thread/week. Text-only outperforms video by 30%.

**Algorithm:** Conversation depth is #1 signal. A reply is worth 27x a like. Premium accounts get ~10x more reach. Since March 2026: non-Premium link posts receive zero median engagement.

**Tone:** Direct, build-in-public, show-your-work. Opinionated and concise. Screenshots, code snippets, data points.

**Content strategy:** Build logs (50%), AI hot takes (30%), Progress updates (20%). 100% build-in-public / AI community.

**Hashtags:** 0-2 maximum. Never trending hashtags on unrelated content.

**Anti-patterns:**
- Follow-unfollow tactics (detected within 24-48 hours, #1 shadowban trigger)
- Generic replies ("Great post!", "100%") = looks automated
- Repetitive content patterns (same template, same link) get flagged
- Excessive hashtags trigger spam detection

**Awareness:** X Premium is essentially required for meaningful reach in 2026. Without Premium, link posts get near-zero distribution. Factor this into effort allocation — X is lowest-priority platform (AI/tech community, not core audience).

**Scaffolds adapt as:** Single tweet — compress scaffold to one core idea, punch delivery. Thread — scaffold flow maps to thread structure (hook tweet → body tweets → closing tweet). Build-in-public formula: problem → tried → worked → lesson.

### LinkedIn

**Format:** Text posts 1,300-1,900 chars. Document posts (PDF carousels) get 6.6% engagement — highest format. Under 500 chars flagged as low-effort. First 210-235 chars visible before "See more" — 60-70% of readers lost at this cutoff.

**Algorithm:** Saves are king (1 save = ~5x reach of a like). First 60-90 minutes determine 70% of total reach. Comments worth 2x likes. External links penalized ~60% less reach. Posting 2+/day drops per-post reach by 40%+.

**Tone:** Process-driven — step-by-step methods, frameworks, structured approaches. Professional but personal. Specific numbers, data points, concrete examples. Saveable reference content.

**Content strategy:** Month 2+ only. First post = sister case study. Professional credibility, B2B agent-facing.

**Hashtags:** 3-5 relevant. No hashtag stuffing.

**Anti-patterns:**
- "Post and ghost" — not engaging in first 60 minutes is the #1 killer
- External links in post body (-60% reach) — put links in first comment
- Generic AI-generated content filtered 45% of the time
- Engagement pods detected by LinkedIn
- New accounts posting aggressively immediately

**Scaffolds adapt as:** Text post — scaffold flow expanded to 1,300-1,900 chars with short paragraphs (2-3 sentences), aggressive line breaks, one idea per paragraph. Hook in first 210 chars (contrarian, narrative, or statistics opener). Document post — scaffold maps to PDF slides similar to Instagram carousel but more text-heavy and professional.

---

## Voice Profiles

### Design Principles

Both voice profiles are full rewrites. They are NOT tweaks of the existing LINE-derived files. They define how Mike sounds on public platforms — authentic, personal, but calibrated for content, not private chat.

Each profile includes:
- Identity statement
- Tone definition
- Sentence patterns
- Vocabulary guidelines (what to use, what to avoid)
- Platform-specific tone adjustments (per-platform subsections, e.g., `## RED Adjustments`, `## Threads Adjustments` — the draft skill reads the relevant subsection alongside the platform module)
- 3-5 example sentences showing the voice

### `voice-zh.md` (Traditional Chinese — RED + Threads)

Serves two platforms with different energy levels:
- RED: more structured, informative, detailed — still personal but with more depth
- Threads: casual, conversational, quick takes — closer to how you'd talk to a friend

Shared traits:
- Taiwanese identity (台灣人, not 中國人)
- Traditional Chinese throughout
- 你 not 您
- Result-first, then explanation
- Specific details always (numbers, places, dates)
- Short sentences as default, longer for storytelling
- No tutorial tone — "你一定要看這個" energy
- Occasional humor to soften

Removed from current voice:
- All LINE chat patterns (偶/迷有/真嘟假嘟/拍謝/謝拉)
- Excessive interjections (靠/三小 — use sparingly if at all on public platforms)
- Chat-specific vocabulary (好喔/恩對啊/喔喔)

### `voice-en.md` (English — Instagram + X + LinkedIn)

Serves three platforms with different registers:
- X: most raw and direct — short, punchy, mid-thought starts
- Instagram: professional but personal — visual storytelling captions
- LinkedIn: credibility-forward — process-driven, data-backed, structured

Shared traits:
- Taiwanese identity leaned into, not hidden
- Contractions always (don't, can't, I'm)
- No corporate polish, no guru energy
- Technical terms fine when talking to builders
- Occasional Chinese/Taiwanese expressions for authenticity
- Specific over vague — numbers, results, concrete examples

---

## Humanizer

### Purpose

Integrated quality gate in `/cc-draft` that strips AI-tell patterns from generated text. Runs automatically before presenting the draft to the user. Not a separate skill.

### `humanizer-en.md` (English)

**Banned words** (drawn from Sabrina Ramonov's research + expanded):
delve, embark, enlightening, esteemed, shed light, craft, crafting, imagine, realm, game-changer, unlock, discover, skyrocket, abyss, revolutionize, disruptive, utilize, utilizing, dive deep, tapestry, illuminate, unveil, pivotal, intricate, elucidate, hence, furthermore, moreover, however, harness, exciting, groundbreaking, cutting-edge, remarkable, remains to be seen, glimpse into, navigating, landscape, stark, testament, in summary, in conclusion, boost, skyrocketing, powerful, inquiries, ever-evolving, certainly, probably, basically, leverage, synergy, paradigm

**Banned structures:**
- "In today's [adjective] world/landscape..."
- "It's worth noting that..."
- "Not just X, but also Y"
- "In the realm of..."
- "Let's dive in / Let's break it down"
- Avoid excessive em dash usage (max 1 per post; prefer periods or commas)
- Overly balanced "on one hand / on the other hand"
- Neat conclusion paragraphs that summarize everything

**Required patterns:**
- Vary sentence length (5 words then 20 words then 3 words)
- Use contractions
- Direct address ("you", "your")
- Specific examples over generalizations

### `humanizer-zh.md` (Traditional Chinese)

**Banned words/phrases:**
此外, 因此, 值得注意的是, 總而言之, 綜上所述, 不僅...還..., 在這個...的時代, 隨著...的發展, 毫無疑問, 不言而喻, 顯而易見, 與此同時, 換言之, 具體來說, 事實上, 從某種程度上來說, 至關重要, 發揮著重要作用, 提供了寶貴的, 開啟了新的篇章

**Banned structures:**
- Overly parallel sentence pairs (A是B，C是D，E是F)
- Neat summary paragraphs
- Formal transitions between paragraphs
- Balanced "一方面...另一方面..."
- Academic/essay tone (論文體)
- Lists where every item starts the same way

**Required patterns:**
- Mix sentence lengths aggressively
- Start some sentences with interjections or reactions
- Use Taiwanese vocabulary where natural
- End casually — question, reaction, or just stop
- Specific details always (numbers, names, places)

### Self-Check Process

After generating a draft:
1. Scan for any banned word or structure
2. If found → rewrite only the flagged lines (not the whole draft)
3. Re-scan after rewrite
4. Max 2 rewrite passes — if still flagged after 2, present with a warning
5. This replaces the current `anti-ai-patterns.md` and `anti-ai-patterns-en.md` checks

---

## `/cc-adapt` Skill

### Purpose

Takes an approved draft from any platform and generates native rewrites for other platforms.

### Trigger

`/cc-adapt` or "adapt this to other platforms"

### Flow

1. Identify source platform and core idea from approved draft
2. Ask: "Which platforms?" — user picks from remaining platforms, or "all"
3. For each target platform:
   - Load platform module + voice profile + humanizer
   - Rewrite natively — not translate, not reformat, but write a new post that delivers the same core idea in the way that platform's audience expects
   - Apply humanizer self-check
   - Score per platform rubric
4. Present all adapted versions together:

```
Source: RED (approved)

→ Instagram (carousel):
  Slide 1: ...
  Slide 2: ...
  ...
  Caption: ...
  Score: Hook [pass/strong] | Retention [pass/strong] | CTA [pass/strong]

→ Threads:
  [post text]
  Score: Hook [pass/strong] | Retention [pass/strong] | CTA [pass/strong]

→ X:
  [post text]
  Score: Hook [pass/strong] | Retention [pass/strong] | CTA [pass/strong]

Ready to post? Pick platforms or edit inline.
```

5. User approves per platform — can edit, reject, or approve individually
6. On approve → hand off to `/cc-post` for automated platforms, show copy-paste text for manual platforms (RED, LinkedIn)

### Key Principle

Each adaptation is a native rewrite, not a translation. A RED long-form note adapted to X isn't shortened — it's reconceived as a build-in-public tweet from the same core idea.

---

## Skill Updates

### `/cc-draft` (Major Update)

Changes:
- Add `--platform` param: `red | instagram | threads | x | linkedin`
- If not specified → ask user
- Load platform module + voice + humanizer per platform selection
- Scaffolds become platform-aware: same 6 categories, platform-native format per module
- Hook types become platform-aware: current 8 hooks expanded with platform-specific examples
- Humanizer self-check replaces current anti-AI pattern check
- Scoring rubric extended per platform (current rubric is Threads-only). Each platform module defines scoring criteria for Hook, Retention, and CTA dimensions based on that platform's algorithm signals (e.g., RED: Hook = title keyword pull + first-line curiosity, Retention = structure/headers for completion rate, CTA = save-driving ending). Specific scoring criteria are defined during platform module creation.

Pipeline:
1. Determine platform
2. Load platform module + voice profile + humanizer rules
3. Get topic (same as current)
4. Gather source material (same as current)
5. Read scaffolds + hooks (platform section)
6. Draft using platform-specific format
7. Humanizer self-check (scan + rewrite flagged lines)
8. Scoring pass (per platform rubric)
9. Present to user (platform-specific format)
10. Handle feedback (same as current)

### `/cc-post` (Moderate Update)

Changes:
- Add Instagram carousel posting via `post-to-instagram.py`
- Platform routing: threads → script, x → script, instagram → script, red → copy-paste text, linkedin → copy-paste text
- Update `posts.md` tracking to include platform field for all 5 platforms. Existing entries remain as-is (backward-compatible); new entries use the updated format with explicit platform field.
- Manual platforms present structured copy-paste blocks:

  **RED output format:**
  ```
  📌 Title: [title text — first 18 chars contain 2 core keywords]

  [body text]

  [hashtags]

  ⚠️ Remember: Add cover image (3:4 vertical, bold text overlay) before posting
  ```

  **LinkedIn output format (Month 2+):**
  ```
  [post text — hook in first 210 chars]

  💬 First comment (post separately): [link or additional context]

  ⚠️ Remember: Engage in comments for first 60 minutes after posting
  ```

### `/cc-brainstorm` (Minor Update)

Changes:
- Angle proposals include platform recommendation ("this angle works best as a RED long-form note" vs "this is a natural X tweet")
- Concept card gets `Platform` recommendation field
- When surfacing candidates from ideas vault, show platform tags

### `/cc-capture` (Minor Update)

Changes:
- Platform classification expands: `red | instagram | threads | x | linkedin | all`
- Default routing: Chinese idea → `red`, English idea → `x`, works for multiple → `all`

### `/cc-research` (Minor Update)

Changes:
- Add RED/Chinese real estate trends (海外買房, 澳洲房產, AI工具)
- Add Instagram PropTech content trends
- Add LinkedIn real estate technology trends
- Research output grouped by platform, not just language

### `/cc-review` (Minor Now, Phase 2 Full)

Phase 1 changes:
- Dashboard shows all 5 platforms
- Suggestions cover all active platforms

Phase 2 changes (after real posting data):
- Per-platform streak tracking
- Redesigned content calendar for 5-platform cadence
- Cross-platform posting consistency view

### `/cc-recap` (Minor Now, Phase 2 Full)

Phase 1 changes:
- Daily summary shows all 5 platforms
- Tomorrow's plan covers all active platforms

Phase 2 changes:
- Per-platform streak metrics
- Cross-platform consistency tracking

---

## New Posting Script: `post-to-instagram.py`

### Purpose

Post carousels to Instagram via the Graph API.

### Requirements

- Instagram account must be a Business account linked to a Facebook Page
- Environment variables: `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`
- Long-lived access token from Facebook Developer portal

### Core Flow

```python
def post_carousel(image_urls: list[str], caption: str) -> dict:
    # 1. Upload each image as media object (is_carousel_item=true)
    # 2. Create carousel container (media_type=CAROUSEL, children=media_ids)
    # 3. Publish (media_publish endpoint)
    # Returns: permalink URL
```

### Pattern

Follow existing `post-to-threads.py` structure for consistency.

---

## Content Workflow: Day-to-Day Usage

### Flow A: Draft for One Platform

```
/cc-brainstorm → develops idea with platform recommendation
/cc-draft --platform red → drafts RED long-form note
  (user edits, approves)
/cc-post → copies text for manual RED posting
```

### Flow B: Draft + Adapt to All

```
/cc-draft --platform red → drafts RED long-form note
  (user edits, approves)
/cc-adapt → generates native versions for Instagram, Threads, X
  (user reviews each, edits/approves per platform)
/cc-post → posts to automated platforms, copies text for manual ones
```

### Flow C: Standalone Platform Draft

```
/cc-draft --platform x → drafts X tweet directly
  (user edits, approves)
/cc-post → posts to X
```

All three flows are supported. The engine doesn't force multi-platform — it enables it.

---

## Phase 2: Data Model Upgrades (Post-Launch)

**Trigger:** After 20+ posts across 3+ platforms, or after Week 3 — whichever comes first.

- `ideas.md`: Add platform tags to all entries
- `posts.md`: Structured per-platform tracking
- Content calendar: Redesigned for 5-platform cadence with per-platform content type rotation
- `/cc-review`: Full 5-platform dashboard with per-platform streaks
- `/cc-recap`: Cross-platform consistency metrics
- Voice profile iteration: Revisit voice files based on which posts felt most authentic and performed best

---

## Decisions Log

1. **Workflow-based skills with platform modules** — not per-platform skill bundles (avoids 25+ skills)
2. **Custom bilingual humanizer** — not off-the-shelf (needs Chinese support + Mike's voice)
3. **Humanizer baked into cc-draft** — not a separate skill or post-time pass
4. **Native rewrites in cc-adapt** — not translations or reformats
5. **Voice profiles are full rewrites** — not tweaks of LINE-derived files
6. **RED and LinkedIn posting is manual** — RED has no API; LinkedIn is Month 2
7. **Phase 2 data model upgrades** — designed for but not implemented until real posting data exists
8. **X Premium awareness** — noted in spec; reach is severely limited without it in 2026
9. **RED AI labeling** — noted as awareness item; workflow inherently produces sufficiently modified content
10. **Scaffolds/hooks preserved and expanded** — Justin Welsh content matrix concept maintained across all platforms
