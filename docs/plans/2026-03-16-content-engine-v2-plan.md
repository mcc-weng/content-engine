# Content Engine v2: Multi-Platform Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the cc-* content creator skills from 2 platforms (Threads + X) to 5 platforms (RED, Instagram, Threads, X, LinkedIn) with new voice profiles, integrated humanizer, and cross-platform adaptation.

**Architecture:** Workflow-based skills stay (brainstorm → draft → post). Platform-specific rules live in modular reference files (`references/platforms/*.md`) loaded by cc-draft. New `/cc-adapt` skill generates native rewrites across platforms. Custom bilingual humanizer integrated into the drafting pipeline.

**Tech Stack:** Claude Code skills (markdown), Python 3 (posting scripts), Instagram Graph API, Obsidian vault (voice profiles)

**Spec:** `docs/superpowers/specs/2026-03-16-content-engine-v2-design.md`

**Git note:** Commit commands use `git add -A` for brevity. In practice, stage specific files by name to avoid committing untracked files (`.DS_Store`, `__pycache__/`, `.playwright-mcp/`). Consider updating `.gitignore` before starting if these patterns aren't already excluded.

---

## Chunk 1: Foundation — Voice Profiles + Humanizer Files

These are the base files everything else depends on. Voice profiles define how Mike sounds; humanizer files define what AI patterns to strip. All other skills load these.

### Task 1: Write new Chinese voice profile

**Files:**
- Rewrite: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/voice-zh.md` (replaces current `voice.md`)

**Context:** The current `voice.md` is derived from LINE chat history and is too casual for public content. The new file must be a complete rewrite — not a tweak. Read the spec sections "Voice Profiles > `voice-zh.md`" for requirements.

- [ ] **Step 1: Read the current `voice.md`** to understand what exists
- [ ] **Step 2: Write `voice-zh.md`** with these sections:
  - Identity statement (Taiwanese AI engineer, bilingual, overseas property buyer)
  - Tone definition (authentic content creator, not chat buddy)
  - Sentence patterns (short default, result-first, specific details)
  - Vocabulary guidelines (what to use + what to avoid — explicitly list removed LINE patterns)
  - `## RED Adjustments` subsection (more structured, informative, 600+ chars, headers)
  - `## Threads Adjustments` subsection (casual, conversational, under 300 chars)
  - 3-5 example sentences per platform showing the voice
- [ ] **Step 3: Delete old `voice.md`** (the new file replaces it with a different name)
- [ ] **Step 4: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): rewrite Chinese voice profile, remove LINE-derived voice"
  ```

### Task 2: Write new English voice profile

**Files:**
- Rewrite: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/voice-en.md`

**Context:** Current `voice-en.md` is basic inline guidelines. New version must serve 3 platforms (X, Instagram, LinkedIn) with different registers. Read spec section "Voice Profiles > `voice-en.md`".

- [ ] **Step 1: Read current `voice-en.md`** to understand what exists
- [ ] **Step 2: Write new `voice-en.md`** with these sections:
  - Identity statement (Taiwanese AI engineer, building for real estate)
  - Tone definition (direct, honest, slightly raw — smart friend energy)
  - Sentence patterns (short punchy, vary lengths, contractions always)
  - Vocabulary guidelines (use "shipped" not "completed", use "broke" not "encountered")
  - What NOT to sound like (LinkedIn thought leader, startup bro, AI guru, generic motivational)
  - Cultural identity (Taiwanese identity leaned into, bilingual angle)
  - `## X Adjustments` subsection (most raw and direct, mid-thought starts, 280 chars)
  - `## Instagram Adjustments` subsection (professional but personal, visual storytelling captions)
  - `## LinkedIn Adjustments` subsection (credibility-forward, process-driven, data-backed)
  - 3-5 example sentences per platform showing the voice
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): rewrite English voice profile with multi-platform registers"
  ```

### Task 3: Write English humanizer file

**Files:**
- Create: `~/.claude/skills/cc-draft/references/humanizer-en.md`

**Context:** This file defines English AI-tell patterns that the draft skill scans for and rewrites. Based on Sabrina Ramonov's research + expanded. Read spec section "Humanizer > `humanizer-en.md`".

- [ ] **Step 1: Create `humanizer-en.md`** with these sections:
  - `## Banned Words` — full list from spec (delve, embark, enlightening, esteemed, shed light, craft, crafting, imagine, realm, game-changer, unlock, discover, skyrocket, abyss, revolutionize, disruptive, utilize, utilizing, dive deep, tapestry, illuminate, unveil, pivotal, intricate, elucidate, hence, furthermore, moreover, however, harness, exciting, groundbreaking, cutting-edge, remarkable, remains to be seen, glimpse into, navigating, landscape, stark, testament, in summary, in conclusion, boost, skyrocketing, powerful, inquiries, ever-evolving, certainly, probably, basically, leverage, synergy, paradigm)
  - `## Banned Structures` — full list from spec
  - `## Required Patterns` — vary sentence length, contractions, direct address, specifics over generalizations
  - `## Self-Check Process` — scan → rewrite flagged lines → re-scan → max 2 passes
- [ ] **Step 2: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): add English humanizer reference file"
  ```

### Task 4: Write Chinese humanizer file

**Files:**
- Create: `~/.claude/skills/cc-draft/references/humanizer-zh.md`

**Context:** Same purpose as English humanizer but for Traditional Chinese AI-tell patterns. Read spec section "Humanizer > `humanizer-zh.md`".

- [ ] **Step 1: Create `humanizer-zh.md`** with these sections:
  - `## Banned Words/Phrases` — full list from spec (此外, 因此, 值得注意的是, 總而言之, 綜上所述, 不僅...還..., 在這個...的時代, 隨著...的發展, 毫無疑問, 不言而喻, 顯而易見, 與此同時, 換言之, 具體來說, 事實上, 從某種程度上來說, 至關重要, 發揮著重要作用, 提供了寶貴的, 開啟了新的篇章)
  - `## Banned Structures` — parallel sentences, neat summaries, formal transitions, balanced arguments, essay tone, repetitive list openings
  - `## Required Patterns` — mix sentence lengths, interjections, Taiwanese vocabulary, casual endings, specific details
  - `## Self-Check Process` — same scan → rewrite → re-scan → max 2 passes
- [ ] **Step 2: Remove old anti-AI pattern files:**
  - Delete: `~/.claude/skills/cc-draft/references/anti-ai-patterns.md`
  - Delete: `~/.claude/skills/cc-draft/references/anti-ai-patterns-en.md`
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): add Chinese humanizer, remove old anti-AI pattern files"
  ```

---

## Chunk 2: Platform Modules

Create the 5 platform reference files that cc-draft loads for format, tone, strategy, and anti-patterns. Each file follows the same structure but with platform-specific content drawn from the spec's platform sections.

### Task 5: Create RED platform module

**Files:**
- Create: `~/.claude/skills/cc-draft/references/platforms/red.md`

**Context:** RED (Xiaohongshu) is the primary platform — manual posting, Traditional Chinese, long-form notes. Read spec section "RED (Xiaohongshu)" for all details.

- [ ] **Step 1: Create `platforms/` directory** inside `cc-draft/references/`
- [ ] **Step 2: Write `red.md`** with these sections:
  - `## Format Spec` — 600-800 chars (min 300), cover image 3:4, bold text overlay, 1080P+
  - `## Algorithm Signals` — CES scoring, saves strongest signal, first 2 hours critical, search traffic 50%, title first 10 chars = 60% weight
  - `## Tone Rules` — KOC style, authentic, practical, relatable, load `voice-zh.md` + `## RED Adjustments`
  - `## Content Strategy` — Research drops 25%, Build logs 30%, Buyer guides 25%, Case studies 20%. 70% buyer-facing, 30% agent-facing
  - `## Hashtag Strategy` — 1-2 precise + 3-5 long-tail, region + audience + scenario combos
  - `## Anti-Patterns` — superlatives, contact info, QR codes, external URLs, platform watermarks. AI labeling awareness note.
  - `## Example Posts` — 2-3 examples of good RED posts in the real estate niche (Traditional Chinese)
  - Note: Scoring criteria for RED live in `scoring-rubric.md` (Task 12), not duplicated here
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): add RED platform module"
  ```

### Task 6: Create Instagram platform module

**Files:**
- Create: `~/.claude/skills/cc-draft/references/platforms/instagram.md`

**Context:** Instagram uses English carousels — 8-10 slides. Engine outputs slide text only; user creates visuals. Read spec section "Instagram".

- [ ] **Step 1: Write `instagram.md`** with these sections:
  - `## Format Spec` — 8-10 slides, 4:5 portrait (1080x1350px), under 20% text per slide, hook under 12 words. Caption 150-300 chars. Image creation is manual (engine outputs text only).
  - `## Algorithm Signals` — dwell time + swipe velocity, every swipe = engagement event, saves highest value, completion rate >60%
  - `## Tone Rules` — educational, value-driven, professional but personal, clean design. Load `voice-en.md` + `## Instagram Adjustments`
  - `## Content Strategy` — Research drops 25%, Build logs 35%, Personal brand 20%, Offers 20%. 70% agent-facing, 30% personal brand
  - `## Hashtag Strategy` — 3-5 relevant tags in caption, keyword-rich captions > hashtag stuffing
  - `## Anti-Patterns` — inconsistent design, cluttered slides, mixed aspect ratios, weak CTAs
  - `## Example Posts` — 2-3 carousel text examples (slide-by-slide) in real estate/PropTech niche
  - Note: Scoring criteria for Instagram live in `scoring-rubric.md` (Task 12), not duplicated here
- [ ] **Step 2: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): add Instagram platform module"
  ```

### Task 7: Create Threads platform module

**Files:**
- Create: `~/.claude/skills/cc-draft/references/platforms/threads.md`

**Context:** Extract existing Threads rules from cc-draft SKILL.md inline rules into a standalone module. Traditional Chinese, short text. Read spec section "Threads".

- [ ] **Step 1: Write `threads.md`** with these sections:
  - `## Format Spec` — 100-300 chars (500 limit is ceiling), text-first, conversation-sparking
  - `## Algorithm Signals` — replies strongest signal, engagement bait suppressed, topic tags boost views, 6.25% median engagement
  - `## Tone Rules` — conversational, witty, opinion-driven, authenticity over polish. Load `voice-zh.md` + `## Threads Adjustments`
  - `## Content Strategy` — Conversational research 35%, Build updates 35%, Hot takes 30%. 60% buyer-facing, 40% casual
  - `## Hashtag Strategy` — topic tags on every post
  - `## Anti-Patterns` — engagement bait, identical replies, scheduling tool detection, bot behavior
  - `## Example Posts` — 2-3 examples (can reference existing `post-examples.md` Threads examples)
  - Note: Scoring criteria for Threads live in `scoring-rubric.md` (Task 12), not duplicated here
- [ ] **Step 2: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): add Threads platform module"
  ```

### Task 8: Create X platform module

**Files:**
- Create: `~/.claude/skills/cc-draft/references/platforms/x.md`

**Context:** Extract existing X rules from cc-draft SKILL.md into standalone module. English, short text. Read spec section "X (Twitter)".

- [ ] **Step 1: Write `x.md`** with these sections:
  - `## Format Spec` — under 280 chars single post, 2-4 post threads for longer ideas (max 1 thread/week), text outperforms video by 30%
  - `## Algorithm Signals` — conversation depth #1, reply = 27x a like, Premium = ~10x reach, non-Premium link posts = zero engagement
  - `## Tone Rules` — direct, build-in-public, show-your-work, opinionated. Load `voice-en.md` + `## X Adjustments`
  - `## Content Strategy` — Build logs 50%, AI hot takes 30%, Progress updates 20%. 100% build-in-public
  - `## Hashtag Strategy` — 0-2 max, never trending on unrelated content
  - `## Anti-Patterns` — follow-unfollow, generic replies, repetitive patterns, excessive hashtags. X Premium awareness note.
  - `## Example Posts` — 2-3 examples of build-in-public tweets in the real estate AI niche
  - Note: Scoring criteria for X live in `scoring-rubric.md` (Task 12), not duplicated here
- [ ] **Step 2: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): add X platform module"
  ```

### Task 9: Create LinkedIn platform module

**Files:**
- Create: `~/.claude/skills/cc-draft/references/platforms/linkedin.md`

**Context:** LinkedIn is Month 2 — profile only in Month 1. But the module should be ready. English, long-form professional. Read spec section "LinkedIn".

- [ ] **Step 1: Write `linkedin.md`** with these sections:
  - `## Format Spec` — text posts 1,300-1,900 chars, document posts (PDF carousels) 6.6% engagement, first 210-235 chars before "See more" is make-or-break
  - `## Algorithm Signals` — saves king (1 save = 5x like), first 60-90 min = 70% reach, comments 2x likes, external links -60% reach, 2+/day -40% per-post reach
  - `## Tone Rules` — process-driven, professional but personal, specific numbers. Load `voice-en.md` + `## LinkedIn Adjustments`
  - `## Content Strategy` — Month 2+ only, first post = sister case study, B2B agent-facing
  - `## Hashtag Strategy` — 3-5 relevant, no stuffing
  - `## Anti-Patterns` — post and ghost, links in body, generic AI content, engagement pods, aggressive new accounts
  - `## Example Posts` — 2-3 examples of PropTech/real estate AI LinkedIn posts
  - Note: Scoring criteria for LinkedIn live in `scoring-rubric.md` (Task 12), not duplicated here
- [ ] **Step 2: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): add LinkedIn platform module"
  ```

---

## Chunk 3: Scaffolds, Hooks, Scoring, CTAs — Multi-Platform Expansion

Update the shared reference files to support all 5 platforms. Currently these are Threads-only.

### Task 10: Update post-templates.md (scaffolds) for multi-platform

**Files:**
- Modify: `~/.claude/skills/cc-draft/assets/post-templates.md`

**Context:** Current file has 6 scaffolds + global pacing rules, all Threads-specific. Add platform-specific scaffold adaptations for RED, Instagram, X, and LinkedIn. Read spec "Scaffolds adapt as" sections for each platform.

- [ ] **Step 1: Read current `post-templates.md`**
- [ ] **Step 2: Restructure each scaffold** to include platform adaptations:
  - Keep existing Threads flow as-is under each scaffold
  - Add `### RED Adaptation` under each scaffold — long-form note with headers, hook in title, expanded to 600+ chars
  - Add `### Instagram Adaptation` — carousel flow: Slide 1 = hook, Slides 2-9 = body, Final slide = CTA. Include slide text guidelines.
  - Add `### X Adaptation` — single tweet compression or thread structure. Build-in-public formula.
  - Add `### LinkedIn Adaptation` — expanded to 1,300-1,900 chars, short paragraphs, hook in first 210 chars
- [ ] **Step 3: Update Global Pacing Rules** to note which rules are platform-universal vs platform-specific
- [ ] **Step 4: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): expand scaffolds with multi-platform adaptations"
  ```

### Task 11: Update hook-types.md for multi-platform

**Files:**
- Modify: `~/.claude/skills/cc-draft/references/hook-types.md`

**Context:** Current 8 hooks are Chinese/Threads-only. Add English examples for X, Instagram caption hooks, LinkedIn hooks, and RED title hooks.

- [ ] **Step 1: Read current `hook-types.md`**
- [ ] **Step 2: For each of the 8 hook types, add:**
  - `**RED title example:**` (Traditional Chinese, optimized for first 18 chars + search keywords)
  - `**Instagram slide 1 example:**` (English, under 12 words, bold visual text)
  - `**X example:**` (English, under 280 chars, scroll-stopping)
  - `**LinkedIn example:**` (English, first 210 chars, contrarian/narrative/statistics)
  - Keep existing Threads examples as-is
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): expand hooks with multi-platform examples"
  ```

### Task 12: Update scoring-rubric.md for multi-platform

**Files:**
- Modify: `~/.claude/skills/cc-draft/references/scoring-rubric.md`

**Context:** Current rubric is Threads-only. Add per-platform scoring criteria. Each platform module defines what Hook/Retention/CTA mean for that platform. The rubric file should contain the universal framework + platform-specific calibration.

- [ ] **Step 1: Read current `scoring-rubric.md`**
- [ ] **Step 2: Restructure as:**
  - `## Universal Framework` — the 3-pillar model (Hook, Retention, CTA) with Fail/Pass/Strong scale
  - `## Threads Scoring` — migrate existing criteria as-is
  - `## RED Scoring` — Hook: title keyword pull + first-line curiosity. Retention: headers/structure for completion rate. CTA: save-driving ending + engagement question.
  - `## Instagram Scoring` — Hook: slide 1 answers "is this for me?" under 12 words. Retention: swipe-worthy progression. CTA: final slide drives save/DM/share.
  - `## X Scoring` — Hook: first line stops scroll. Retention: N/A for single tweets (thread pacing for threads). CTA: drives reply or quote-tweet.
  - `## LinkedIn Scoring` — Hook: first 210 chars. Retention: short paragraphs, line breaks. CTA: question driving comments.
  - Keep Rewrite Rules section, make platform-aware
  - Update fail calibration examples — add one example per platform
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): expand scoring rubric for multi-platform"
  ```

### Task 13: Update cta-bank.md for multi-platform

**Files:**
- Modify: `~/.claude/skills/cc-draft/references/cta-bank.md`

**Context:** Current CTA bank is Chinese/Threads-only. Add English CTAs for X, Instagram, and LinkedIn.

- [ ] **Step 1: Read current `cta-bank.md`**
- [ ] **Step 2: Add platform sections:**
  - Keep existing Threads CTAs under `## Threads (Traditional Chinese)`
  - Add `## RED (Traditional Chinese)` — similar to Threads but calibrated for save-driving (RED's #1 signal is saves, not replies)
  - Add `## Instagram (English)` — carousel-specific CTAs ("Save this for later", "DM me [keyword]", "Share with someone who needs this")
  - Add `## X (English)` — reply-driving CTAs, quote-tweet invitations, build-in-public engagement
  - Add `## LinkedIn (English)` — professional comment-driving CTAs, question-based, expertise-sharing
- [ ] **Step 3: Update selection rules** to be platform-aware
- [ ] **Step 4: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): expand CTA bank for multi-platform"
  ```

### Task 14: Update post-examples.md for multi-platform

**Files:**
- Modify: `~/.claude/skills/cc-draft/references/post-examples.md`

**Context:** Add example posts for each platform in the real estate AI niche.

- [ ] **Step 1: Read current `post-examples.md`**
- [ ] **Step 2: Add examples per platform:**
  - `## RED Examples` — 2-3 Traditional Chinese long-form notes about overseas buying, AI tools for agents
  - `## Instagram Examples` — 2-3 carousel text examples (slide-by-slide format) in English
  - `## Threads Examples` — keep existing + add real estate niche examples
  - `## X Examples` — 2-3 build-in-public tweets about real estate AI
  - `## LinkedIn Examples` — 2-3 professional PropTech posts
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): expand post examples for multi-platform"
  ```

---

## Chunk 4: cc-draft Major Rewrite

The core skill update — make cc-draft platform-aware with the new loading pattern.

### Task 15: Rewrite cc-draft SKILL.md

**Files:**
- Rewrite: `~/.claude/skills/cc-draft/SKILL.md`

**Context:** This is the most complex change. The current skill is hardcoded for Threads (Chinese) and X (English). The new version loads platform modules dynamically. Read the full current SKILL.md and the spec section "Skill Updates > `/cc-draft`" for the new pipeline.

- [ ] **Step 1: Read current `cc-draft/SKILL.md`** carefully — note all paths, steps, rules
- [ ] **Step 2: Rewrite SKILL.md** with this structure:

  **Frontmatter:** Update description to mention all 5 platforms

  **## Paths** — update to include:
  - Platform modules: `references/platforms/{red,instagram,threads,x,linkedin}.md`
  - Voice profiles: `voice-zh.md` (RED, Threads) and `voice-en.md` (Instagram, X, LinkedIn)
  - Humanizer: `references/humanizer-zh.md` (RED, Threads) and `references/humanizer-en.md` (Instagram, X, LinkedIn)
  - Scaffolds, hooks, CTA bank, scoring rubric, post examples (existing paths)
  - Ideas vault, content log (existing paths)

  **## Steps** — new 10-step pipeline:
  1. Determine platform (`--platform` param or ask user). Valid: `red | instagram | threads | x | linkedin`
  2. Load platform module + voice profile + humanizer based on platform:
     - `red` → `platforms/red.md` + `voice-zh.md` (## RED Adjustments) + `humanizer-zh.md`
     - `instagram` → `platforms/instagram.md` + `voice-en.md` (## Instagram Adjustments) + `humanizer-en.md`
     - `threads` → `platforms/threads.md` + `voice-zh.md` (## Threads Adjustments) + `humanizer-zh.md`
     - `x` → `platforms/x.md` + `voice-en.md` (## X Adjustments) + `humanizer-en.md`
     - `linkedin` → `platforms/linkedin.md` + `voice-en.md` (## LinkedIn Adjustments) + `humanizer-en.md`
  3. Get topic (same as current — user provides, or from queue, or from research)
  4. Gather source material (ideas.md, log.md)
  5. Read scaffolds + hooks (platform-specific sections from post-templates.md and hook-types.md)
  6. Draft using platform-specific format (follow scaffold adaptation for the selected platform)
  7. Humanizer self-check (load humanizer file, scan for banned words/structures, rewrite flagged lines, max 2 passes)
  8. Scoring pass (load scoring rubric, score per platform section)
  9. Present to user (platform-specific format — see below)
  10. Handle feedback (edit inline, reject, approve → update ideas vault)

  **## Platform-Specific Presentation Formats:**
  - RED: title + body + hashtags + char count / 800
  - Instagram: slide-by-slide text + caption + char count per slide
  - Threads: post text + scores + char count / 300
  - X: tweet text + char count / 280 (or thread format)
  - LinkedIn: post text + first-comment text + char count / 1900

  **## Character Count** — per-platform limits

  **## Rules** — merge current both-platform rules + add platform-specific rules

- [ ] **Step 3: Verify** — read the completed SKILL.md and confirm each of the 5 platforms has a complete loading path by checking that all referenced files exist on disk (platform module, voice profile, humanizer). Run `ls` on the referenced paths.
- [ ] **Step 4: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): rewrite cc-draft for multi-platform support"
  ```

---

## Chunk 5: cc-adapt + cc-post + Instagram Script

New adaptation skill, updated posting skill, and new Instagram posting script.

### Task 16: Create cc-adapt skill

**Files:**
- Create: `~/.claude/skills/cc-adapt/SKILL.md`

**Context:** Brand new skill for cross-platform content adaptation. Read spec section "`/cc-adapt` Skill" for the full flow.

- [ ] **Step 1: Create `~/.claude/skills/cc-adapt/` directory**
- [ ] **Step 2: Write `SKILL.md`** with:

  **Frontmatter:**
  ```yaml
  ---
  name: cc-adapt
  description: Adapt approved content to other platforms with native rewrites. Use when user says "/cc-adapt", "adapt this to other platforms", or approves a draft and wants it on multiple platforms. Does NOT trigger on drafting or posting tasks.
  ---
  ```

  **## Paths** — same platform modules, voice profiles, and humanizer files as cc-draft

  **## Steps:**
  1. Identify source platform and core idea from the approved draft in current conversation
  2. Ask: "Which platforms?" — user picks from remaining platforms, or "all"
  3. For each target platform:
     - Load platform module + voice profile + humanizer (same loading pattern as cc-draft)
     - Rewrite natively — extract the core idea and write a NEW post for the target platform's format, tone, and audience
     - Apply humanizer self-check
     - Score per platform rubric
  4. Present all adapted versions together (format from spec)
  5. User approves per platform — can edit, reject, or approve individually
  6. On approve → tell user to run `/cc-post` for each approved platform

  **## Key Principle:** Each adaptation is a native rewrite, not a translation.

  **## Rules:**
  - Never copy-paste between platforms — always rewrite
  - Respect each platform's character limits and format
  - Load the target platform's voice adjustments, not the source platform's
  - If a platform doesn't make sense for this content (e.g., LinkedIn Month 2), say so

- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): create cc-adapt skill for cross-platform adaptation"
  ```

### Task 17: Write post-to-instagram.py

**Files:**
- Create: `~/Desktop/Projects/content/scripts/post-to-instagram.py`

**Context:** Instagram Graph API carousel posting. Follow `post-to-threads.py` pattern (same error handling, dry-run support, env var pattern). Read spec section "New Posting Script".

- [ ] **Step 1: Read `post-to-threads.py`** to understand the pattern
- [ ] **Step 2: Write `post-to-instagram.py`** with:
  - Same docstring pattern, usage examples
  - Env vars: `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`
  - `--dry-run` support
  - Core flow:
    1. Accept image URLs (comma-separated) + caption as args
    2. Upload each image as media object (`is_carousel_item=true`)
    3. Create carousel container (`media_type=CAROUSEL`, `children=media_ids`)
    4. Poll for container status (Instagram needs processing time — poll `STATUS_CODE` field every 3 seconds, timeout after 30 seconds, expected final status: `FINISHED`)
    5. Publish (`media_publish` endpoint)
    6. Return permalink URL
  - Same `_handle_error` and `_retry_on_5xx` helpers
  - Usage: `python3 post-to-instagram.py --images "url1,url2,url3" --caption "Caption text"`
- [ ] **Step 3: Test with `--dry-run`**
  ```bash
  python3 scripts/post-to-instagram.py --dry-run --images "https://example.com/1.jpg,https://example.com/2.jpg" --caption "Test caption"
  ```
  Expected: dry-run output showing image count and caption
- [ ] **Step 4: Commit**
  ```bash
  git add scripts/post-to-instagram.py
  git commit -m "feat: add Instagram carousel posting script"
  ```

### Task 18: Update cc-post skill

**Files:**
- Modify: `~/.claude/skills/cc-post/SKILL.md`

**Context:** Add Instagram routing, manual platform output formats for RED/LinkedIn, and 5-platform awareness. Read spec section "Skill Updates > `/cc-post`".

- [ ] **Step 1: Read current `cc-post/SKILL.md`**
- [ ] **Step 2: Update SKILL.md:**
  - **Frontmatter:** Update description to include all 5 platforms
  - **## Paths:** Add `post-to-instagram.py` path
  - **## Steps:**
    - Step 1: Determine platform — expand to `red | instagram | threads | x | linkedin`
    - Step 4 (Publish): Add platform routing:
      - `threads` → `post-to-threads.py` (existing)
      - `x` → `post-to-x.py` (existing)
      - `instagram` → `post-to-instagram.py` (new) — requires image URLs + caption
      - `red` → present structured copy-paste block (title + body + hashtags + cover image reminder)
      - `linkedin` → present structured copy-paste block (post text + first comment text + engagement reminder)
    - Step 5 (On success): Update `posts.md` with explicit platform field. Backward-compatible with existing entries.
  - **## Manual Platform Output Formats:** Add RED and LinkedIn copy-paste block templates from spec
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): update cc-post for 5-platform routing"
  ```

---

## Chunk 6: Minor Skill Updates + Cleanup

Update remaining skills for platform awareness. These are small changes.

### Task 19: Update cc-brainstorm

**Files:**
- Modify: `~/.claude/skills/cc-brainstorm/SKILL.md`

**Context:** Add platform recommendation to angle proposals and concept cards. Read spec section "Skill Updates > `/cc-brainstorm`".

- [ ] **Step 1: Read current `cc-brainstorm/SKILL.md`**
- [ ] **Step 2: Update:**
  - In Step 3 (Propose 2-3 Angles): Add `**Best platform:**` field to each angle (e.g., "this works best as a RED long-form note")
  - In Step 5 (Present Concept Card): Expand the `Platform` field from `Threads (Chinese) or X (English)` to `red | instagram | threads | x | linkedin | all`
  - In Step 1 (Detect Entry Mode): When surfacing candidates from ideas vault, show platform tags
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): update cc-brainstorm with platform recommendations"
  ```

### Task 20: Update cc-capture

**Files:**
- Modify: `~/.claude/skills/cc-capture/SKILL.md`

**Context:** Expand platform classification. Read spec section "Skill Updates > `/cc-capture`".

- [ ] **Step 1: Read current `cc-capture/SKILL.md`**
- [ ] **Step 2: Update Step 4 (Classify platform):**
  - Expand options: `red | instagram | threads | x | linkedin | all`
  - New default routing: Chinese idea → `red`, English idea → `x`, works for multiple → `all`
  - Keep user override (if user specifies a platform, use it)
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): update cc-capture with expanded platform classification"
  ```

### Task 21: Update cc-research

**Files:**
- Modify: `~/.claude/skills/cc-research/SKILL.md`

**Context:** Add RED/Chinese real estate trends, Instagram PropTech, LinkedIn PropTech. Read spec section "Skill Updates > `/cc-research`".

- [ ] **Step 1: Read current `cc-research/SKILL.md`**
- [ ] **Step 2: Update:**
  - Step 1 (Search for trends): Add search tracks:
    - **RED (Chinese real estate):** 海外買房, 澳洲房產, AI工具, 房仲科技
    - **Instagram (PropTech):** real estate AI tools, PropTech trends, overseas buyer content
    - **LinkedIn (B2B real estate tech):** PropTech marketing, real estate automation, agent technology
  - Step 2 (Identify topics): Expand platform options to include all 5
  - Step 5 (Save findings): Group by platform, not just language
  - Step 6 (Present): Show all 5 platforms in summary
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): update cc-research with multi-platform trend scanning"
  ```

### Task 22: Update cc-review

**Files:**
- Modify: `~/.claude/skills/cc-review/SKILL.md`

**Context:** Phase 1 — minimal changes. Show all 5 platforms in dashboard. Read spec section "Skill Updates > `/cc-review`".

- [ ] **Step 1: Read current `cc-review/SKILL.md`**
- [ ] **Step 2: Update:**
  - Step 2 (Calculate streaks): Expand from X + Threads to all 5 platforms. Posts without platform field still count as Threads (backward compat).
  - Step 3 (Check calendar): Suggest content types for all active platforms
  - Step 5 (Present): Dashboard shows all 5 platforms in Queue, Recent Posts, Streaks, and Today sections
  - Add note: "Phase 2 (after 20+ posts across 3+ platforms): per-platform streak tracking, redesigned content calendar"
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): update cc-review dashboard for 5 platforms"
  ```

### Task 23: Update cc-recap

**Files:**
- Modify: `~/.claude/skills/cc-recap/SKILL.md`

**Context:** Phase 1 — show all 5 platforms in daily summary. Read spec section "Skill Updates > `/cc-recap`".

- [ ] **Step 1: Read current `cc-recap/SKILL.md`**
- [ ] **Step 2: Update:**
  - Step 1 (Today's activity): List all 5 platforms
  - Step 3 (Streak): Calculate for all 5 platforms. Posts without platform field count as Threads.
  - Step 5 (Tomorrow's plan): Cover all active platforms
  - Step 6 (Present): Show all 5 platforms in Today, Streaks, and Tomorrow sections
  - Add note: "Phase 2: per-platform streak metrics, cross-platform consistency tracking"
- [ ] **Step 3: Commit**
  ```bash
  git add -A
  git commit -m "feat(cc): update cc-recap for 5-platform daily summary"
  ```

### Task 24: Final cleanup + verification

**Files:**
- Verify all files are in place
- Remove any stale references

- [ ] **Step 1: Verify file structure** — list all cc-* skill files and confirm:
  - 5 platform modules exist in `cc-draft/references/platforms/`
  - 2 humanizer files exist in `cc-draft/references/`
  - Old `anti-ai-patterns.md` and `anti-ai-patterns-en.md` are deleted
  - `cc-adapt/SKILL.md` exists
  - `post-to-instagram.py` exists
  - Both voice profile files exist in Obsidian vault
- [ ] **Step 2: Verify cc-draft loading pattern** — read SKILL.md and trace each platform path:
  - `--platform red` → loads red.md + voice-zh.md + humanizer-zh.md ✓
  - `--platform instagram` → loads instagram.md + voice-en.md + humanizer-en.md ✓
  - `--platform threads` → loads threads.md + voice-zh.md + humanizer-zh.md ✓
  - `--platform x` → loads x.md + voice-en.md + humanizer-en.md ✓
  - `--platform linkedin` → loads linkedin.md + voice-en.md + humanizer-en.md ✓
- [ ] **Step 3: Smoke test** — invoke `/cc-draft --platform red` with a test topic and verify:
  - It loads the RED platform module
  - It uses the Chinese voice profile (RED adjustments)
  - It runs the Chinese humanizer self-check
  - It scores using RED criteria
  - Output is in the correct RED format (title + body + hashtags)
- [ ] **Step 4: Copy updated spec to Obsidian** (if any spec changes were made during implementation)
- [ ] **Step 5: Final commit**
  ```bash
  git add -A
  git commit -m "feat(cc): content engine v2 complete — verify all platform paths"
  ```

---

## Execution Order + Dependencies

```
Chunk 1 (Tasks 1-4): Foundation
  ↓
Chunk 2 (Tasks 5-9): Platform Modules (depends on Chunk 1 for voice/humanizer paths)
  ↓
Chunk 3 (Tasks 10-14): Scaffolds/Hooks/Scoring/CTAs (independent of Chunk 2, but logical order)
  ↓
Chunk 4 (Task 15): cc-draft Rewrite (depends on Chunks 1-3 — all reference files must exist)
  ↓
Chunk 5 (Tasks 16-18): cc-adapt + cc-post + Instagram (depends on Chunk 4 for loading pattern)
  ↓
Chunk 6 (Tasks 19-24): Minor Updates + Cleanup (depends on Chunk 4 for platform param convention)
```

Tasks within each chunk can be parallelized (e.g., Tasks 5-9 are independent of each other).

---

## What's NOT in This Plan (Phase 2)

After 20+ posts across 3+ platforms, or after Week 3:

- `ideas.md` platform tags
- `posts.md` structured per-platform tracking
- Content calendar redesign for 5-platform cadence
- `/cc-review` full 5-platform streak dashboard
- `/cc-recap` cross-platform consistency metrics
- Voice profile iteration based on real posting data
