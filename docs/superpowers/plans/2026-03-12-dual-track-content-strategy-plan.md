# Dual-Track Content Strategy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the existing content engine (6 skills, data files, posting scripts) to support dual-track content: English on X + Chinese on Threads.

**Architecture:** The existing Chinese/Threads infrastructure stays intact. We add an English track by: (1) updating skills to accept a `--platform` parameter, (2) creating English voice and anti-AI reference docs, (3) updating data file formats with a platform field, (4) creating an X posting script, and (5) updating the content calendar for dual-track pillars.

**Tech Stack:** Claude Code skills (Markdown SKILL.md files), Python scripts, Obsidian vault (Markdown data files)

**Spec:** `docs/superpowers/specs/2026-03-12-dual-track-content-strategy-design.md`

---

## Chunk 1: Data Layer Updates

Update the shared data files and reference docs that all skills depend on.

### Task 1: Update Ideas Vault Format

Add `platform` field to the ideas vault format reference.

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-capture/references/ideas-vault-format.md`

- [ ] **Step 1: Update the entry format to include platform field**

Add `Platform:` field after `Source:` in the entry format:

```markdown
## Entry Format (append under `## Queue`)

    - **[YYYY-MM-DD]** [type] Short description
      - Raw: (original input verbatim)
      - Angle: (suggested angle, or "none yet")
      - Source: (URL if applicable)
      - Platform: x | threads | both
      - Status: raw | drafted | posted
```

And update the "Moving to Used" section to include platform:

```markdown
## Moving to Used (when posted)

Move the entry from `## Queue` to `## Used` and add:

    - **[YYYY-MM-DD]** [type] Short description
      - Posted: YYYY-MM-DD
      - Platform: [x | threads | both]
      - Link: (post URL)
```

Add a note at the bottom:

```markdown
## Backward Compatibility

Existing entries without a `Platform:` field default to `threads`.
```

- [ ] **Step 2: Verify the file reads correctly**

Read the file back and confirm formatting is correct.

- [ ] **Step 3: Commit**

```bash
git add ~/.claude/skills/cc-capture/references/ideas-vault-format.md
git commit -m "feat(cc-capture): add platform field to ideas vault format"
```

### Task 2: Create English Voice Profile

Create the initial English voice guidelines document in the Obsidian vault.

**Files:**
- Create: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/voice-en.md`

- [ ] **Step 1: Create the English voice profile**

```markdown
# English Voice Profile

## Identity

Mike — Taiwanese/Melbourne-based developer building AI automation businesses, documenting the journey from $0 to $20k/month to move to the US.

## Tone

- Direct, honest, slightly raw
- No corporate polish, no guru energy
- Smart friend texting you what he learned today
- OK to mix in occasional Chinese/Taiwanese expressions — it's part of your identity

## Sentence Patterns

- Short sentences. Punchy.
- Start mid-thought sometimes — no preamble
- Vary sentence length (5 words then 20 words then 3 words)
- End casual — question, reaction, or just stop
- Under 280 characters for X posts (can thread for longer content)

## Vocabulary

- Use "shipped" not "completed development of"
- Use "broke" not "encountered an error"
- Use "wild" not "remarkable"
- Use contractions (don't, can't, I'm)
- Swearing is fine occasionally (damn, hell) — not forced
- Technical terms are fine when talking to builders — don't dumb down

## What NOT to Sound Like

- LinkedIn thought leader ("I'm humbled to announce...")
- Startup bro ("crushing it", "10x", "leverage")
- AI guru ("unlock the power of AI")
- Generic motivational ("if I can do it, you can too!")

## Cultural Identity

- You're Taiwanese. Don't hide it — lean into it.
- The bilingual angle is a superpower, not a limitation
- Occasional Chinese words/phrases add authenticity
- The immigrant entrepreneur perspective is your differentiator

## This Document Evolves

This is a starting point. After 2-3 weeks of real posting, revisit and refine based on which posts felt most authentic and performed best.
```

- [ ] **Step 2: Verify the file exists and reads correctly**

```bash
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/content/voice-en.md
```

Read the file back to confirm formatting.

Note: This file lives in the Obsidian vault (iCloud), not the git repo. No git commit needed.

### Task 3: Create English Anti-AI Patterns

Create the initial English anti-AI patterns reference for the draft skill.

**Files:**
- Create: `/Users/mikeweng/.claude/skills/cc-draft/references/anti-ai-patterns-en.md`

- [ ] **Step 1: Create the English anti-AI patterns file**

```markdown
# Anti-AI Patterns — English Self-Check Guide

Read this BEFORE writing and AFTER writing. If any "Never" pattern appears in your draft, rewrite.

## Never

- "In today's rapidly evolving..." / "In the world of..." / "As we all know..."
- "Let's dive in" / "Let's break it down" / "Here's the thing"
- "Game-changer" / "revolutionary" / "groundbreaking"
- Numbered lists with exactly 3 or 5 items
- Perfect parallel structure
- "I'm excited to share..." / "I'm thrilled to announce..."
- Starting with a question you immediately answer ("Ever wondered...? Well,")
- Neat conclusions that wrap everything up with a bow
- Balanced hedging ("While X, it's important to note Y")
- Em dashes used for dramatic effect more than twice per post
- "At the end of the day..."

## Always

- Vary sentence length wildly
- Start mid-thought sometimes
- Incomplete sentences are fine
- Strong opinions — pick a side
- Specific numbers and details ("took me 3 hours", "client #2", "$47 in API costs")
- Real emotions ("honestly scared", "this pissed me off", "holy shit it worked")
- Some posts can be just 1-2 sentences

## Self-Check (run after every draft)

1. Could any AI-bro Twitter account have written this? → rewrite
2. Is there a specific detail only Mike would know? → if not, add one
3. Would you send this as a text to a friend? → must pass this test
4. Read it out loud — does it sound like a person or a press release?

## This Document Evolves

Starting set of patterns. Refine after 2-3 weeks of real English posting — add patterns you catch yourself falling into.
```

- [ ] **Step 2: Verify the file reads correctly**

Read the file back and confirm formatting.

- [ ] **Step 3: Commit**

```bash
git add ~/.claude/skills/cc-draft/references/anti-ai-patterns-en.md
git commit -m "feat(cc-draft): add English anti-AI patterns reference"
```

### Task 4: Update Content Calendar for Dual-Track

Replace the single-track calendar with a dual-track version.

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-review/references/content-calendar.md`

- [ ] **Step 1: Update the content calendar**

Replace the entire file content with:

```markdown
# Content Calendar — Dual-Track Weekly Rhythm

## X (English) — Build-in-Public + AI Expertise

- **Mon:** Build log (what you shipped this week / are working on)
- **Tue:** AI expertise drop (tutorial, tool breakdown, or demo)
- **Wed:** Revenue/progress update or hot take
- **Thu:** Build log or client case study
- **Fri:** AI expertise drop or trending topic
- **Sat:** Dream post (the US journey, personal reflection)
- **Sun:** Engagement post (question, poll, or reply to others)

### Pillar Weights (X)
- Build logs: 40%
- AI expertise drops: 25%
- Revenue/progress transparency: 20%
- Dream posts: 15%

## Threads (Chinese) — 朋友 + 實驗者

- **Mon:** Demo post (show something you built)
- **Tue:** Curated insight (translate English AI news)
- **Wed:** Hot take or personal journey
- **Thu:** Demo post or audience response
- **Fri:** Curated insight or trending topic
- **Sat:** Personal journey / week reflection (台灣人追美國夢 angle)
- **Sun:** Audience question / engagement post

### Pillar Weights (Threads)
- Build logs: 40%
- Curated AI insights: 25%
- Revenue/progress transparency: 20%
- Dream posts: 15%

## Rules

- Flexible — trends override calendar on both platforms
- If a major AI announcement drops, post about it regardless of day
- Weekend posts can be lighter / more personal
- Don't force a category if nothing fits — skip and post what feels right
- Same core story on both platforms, but adapted per audience — not translated
```

- [ ] **Step 2: Verify the file reads correctly**

Read the file back and confirm.

- [ ] **Step 3: Commit**

```bash
git add ~/.claude/skills/cc-review/references/content-calendar.md
git commit -m "feat(cc-review): update content calendar for dual-track strategy"
```

---

## Chunk 2: Skill Updates

Update each skill to support dual-track (English X + Chinese Threads).

### Task 5: Update `/cc-capture` Skill

Add platform selection to the capture flow. (Note: The spec lists cc-capture under "Keep As-Is" but also requires a platform field on ideas. We follow the "Needs Updating" interpretation — cc-capture needs a platform classification step.)

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-capture/SKILL.md`

- [ ] **Step 1: Update the skill description**

Change the YAML frontmatter description to:
```yaml
description: Capture raw content ideas into the ideas vault. Use when user says "/cc-capture", "capture this for content", "idea for a post", or "save this for content". Does NOT trigger on general URL sharing or non-content tasks.
```

(Changed "save this for threads" → "save this for content")

- [ ] **Step 2: Replace the entire Steps section**

Replace everything between `## Steps` and `## Rules` with:

```markdown
## Steps

1. **Accept input** — text, URL, screenshot, or half-formed thought. Whatever the user gives you.

2. **If URL:** Use WebFetch to retrieve and summarize the content in 1-2 sentences.

3. **Classify type:** Pick one: `thought` | `link` | `demo` | `reference` | `hot-take`

4. **Classify platform:** Pick one: `x` | `threads` | `both`
   - If user specifies a platform → use it
   - If idea is in English → default to `x`
   - If idea is in Chinese → default to `threads`
   - If idea works for both audiences → use `both`
   - When in doubt → use `both`

5. **Append to ideas vault:** Read `content-ideas.md`, then append a new entry under `## Queue` using the format in `references/ideas-vault-format.md`. Use today's date. Preserve the user's original input verbatim in the `Raw:` field.

6. **Suggest angle** if one is obvious from the input. Otherwise set to "none yet".

7. **Confirm** with one line: what was captured, what type, which platform, and the angle (if any).
```

- [ ] **Step 4: Verify the file reads correctly**

Read the file back and confirm all steps are correctly numbered and complete.

- [ ] **Step 5: Commit**

```bash
git add ~/.claude/skills/cc-capture/SKILL.md
git commit -m "feat(cc-capture): add platform field to capture flow"
```

### Task 6: Update `/cc-draft` Skill

Add English X drafting mode with platform parameter and voice profile routing.

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-draft/SKILL.md`

- [ ] **Step 1: Update YAML frontmatter**

```yaml
---
name: cc-draft
description: Draft posts for X (English) or Threads (Chinese) in Mike's authentic voice. Use when user says "/cc-draft", "write a post", "draft something for threads", or "draft something for X". Does NOT trigger on general writing tasks like docs, emails, or code comments.
---
```

- [ ] **Step 2: Update the title and intro**

```markdown
# Draft Post

Write a post for X (English) or Threads (Chinese) in Mike's authentic voice.
```

- [ ] **Step 3: Update the Paths section**

Replace the Paths section with:

```markdown
## Paths

### Chinese (Threads)
- Voice profile (MUST read first): `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/voice.md`
- Anti-AI patterns (MUST read first): `references/anti-ai-patterns.md`

### English (X)
- Voice profile (MUST read first): `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/voice-en.md`
- Anti-AI patterns (MUST read first): `references/anti-ai-patterns-en.md`
- If `voice-en.md` does not exist yet, use these inline guidelines: direct, raw, no polish, smart friend energy, short sentences, strong opinions

### Shared
- Post examples: `references/post-examples.md`
- Post templates: `assets/post-templates.md`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/ideas.md`
- Content log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/log.md`
```

- [ ] **Step 4: Update the Steps section**

Replace the entire Steps section with:

```markdown
## Steps

1. **Determine platform:**
   - If user says "for X", "for twitter", "in English" → platform = `x`
   - If user says "for threads", "in Chinese" → platform = `threads`
   - If not specified → ask: "For X (English) or Threads (Chinese)?"

2. **Load voice and anti-AI patterns for the platform:**
   - Platform `threads`: Read `content-voice.md` AND `references/anti-ai-patterns.md`
   - Platform `x`: Read `content-voice-en.md` AND `references/anti-ai-patterns-en.md`
   - If `content-voice-en.md` doesn't exist, use inline fallback (see Paths section)
   - Do not skip this step.

3. **Get the topic:**
   - If user provides a specific idea → use it
   - If user says "from queue" or "pick one" → read `content-ideas.md`, suggest top 3 from Queue with `raw` status that match the platform
   - If user says "from research" → read `content-research.md` (if it exists)

4. **Gather source material:** Read `content-ideas.md` and `content-log.md` for relevant context, examples, or data points that could strengthen the post.

5. **Read** `references/post-examples.md` and `assets/post-templates.md` for style reference.

6. **Draft the post:**

   **If platform = `threads` (Chinese):**
   - 朋友 + 實驗者 tone from voice profile
   - Taiwanese Mandarin casual vocabulary (靠、哈哈哈哈、蝦米、欸)
   - Under 300 characters (each Chinese char = 1 character)
   - Hook in first line
   - Engagement close (question, CTA, or "你覺得呢？")
   - Break into 2-3 short lines, not one paragraph

   **If platform = `x` (English):**
   - Direct, raw, personal tone from English voice profile
   - Under 280 characters for a single post
   - If the idea needs more space, draft as a thread (2-4 posts max)
   - Hook in first line — must stop the scroll
   - End with engagement driver (question, hot take, or call to action)
   - Short lines. Punchy.

7. **Self-check gate:** Review the draft against the platform's anti-AI patterns:
   - Any "Never" pattern detected? → rewrite that part
   - All self-check questions pass? → proceed
   - If rewritten, re-check again

8. **Present to user:**

   ---
   **[Platform: X/Threads]**
   [post text]
   ---
   Source: [where the idea came from]
   Characters: [count] / [limit]

   Does this sound like you? Edit inline, or say "reject" to start fresh.

9. **Handle feedback:**
   - User edits inline → apply edits, re-count characters
   - User says "reject" or "try again" → draft from scratch with different angle
   - User approves → update ideas vault status to `drafted` (if idea came from queue)
```

- [ ] **Step 5: Update the Character Count section**

Replace with:

```markdown
## Character Count

### Threads (Chinese)
- 300 is a style guideline for readability
- Threads API limit is 500 — stay well under
- Count Unicode characters (each Chinese character = 1)
- Emoji = 1 character

### X (English)
- 280 character limit per post
- If drafting a thread, each post under 280
- Emoji = variable (usually 2 characters in Twitter's counting)
```

- [ ] **Step 6: Update the Rules section**

Replace with:

```markdown
## Rules

### Both Platforms
- NEVER hedge or give balanced takes
- Short > long. 2 sentences > 5 sentences.

### Threads (Chinese)
- NEVER sound like a tutorial or educational content
- NEVER use 您 — always 你
- If you catch yourself writing "在這個...的時代" — stop and rewrite everything

### X (English)
- NEVER sound like a LinkedIn thought leader
- NEVER use "game-changer", "revolutionary", or "let's dive in"
- If you catch yourself writing "In today's rapidly evolving..." — stop and rewrite everything
```

- [ ] **Step 7: Verify the complete file reads correctly**

Read the entire file back and confirm all sections are complete and consistent.

- [ ] **Step 8: Commit**

```bash
git add ~/.claude/skills/cc-draft/SKILL.md
git commit -m "feat(cc-draft): add dual-track support with platform parameter and voice routing"
```

### Task 7: Update `/cc-post` Skill

Add X posting capability alongside Threads.

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-post/SKILL.md`

- [ ] **Step 1: Update YAML frontmatter**

```yaml
---
name: cc-post
description: Publish approved content to Threads or X. Use when user says "/cc-post", "publish to threads", "post to X", or approves a draft for posting. Does NOT trigger on general publishing or deploy tasks.
---
```

- [ ] **Step 2: Update the title and intro**

```markdown
# Post to Threads or X

Publish approved content to the target platform and update tracking files.
```

- [ ] **Step 3: Update the Paths section**

```markdown
## Paths

- Threads posting script: `~/Desktop/Projects/content/scripts/post-to-threads.py`
- X posting script: `~/Desktop/Projects/content/scripts/post-to-x.py`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/ideas.md`
- Posts log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/posts.md`
```

- [ ] **Step 4: Update the Steps section**

Replace the entire Steps section:

```markdown
## Steps

1. **Get the post text and platform:**
   - If provided directly → use it
   - If user says "post the last draft" → use the most recent draft from this conversation
   - Platform should be clear from the draft context (X or Threads)
   - If platform is ambiguous → ask: "Post to X or Threads?"

2. **Final confirmation:** Show the full post text and ask:

   Ready to post to **[X/Threads]**?

   ---
   [post text]
   ---

   Post this? (y/n)

3. **Wait for explicit "y" or "yes"** before proceeding. Never auto-post.

4. **Publish:**

   **Threads:**
   Write the post text to a temp file, then run the posting script:

   ```bash
   cat > /tmp/cc-post-text.txt << 'POSTEOF'
   [post text here]
   POSTEOF
   python3 ~/Desktop/Projects/content/scripts/post-to-threads.py "$(cat /tmp/cc-post-text.txt)"
   ```

   **X (Twitter):**

   If `post-to-x.py` exists:
   ```bash
   cat > /tmp/cc-post-text.txt << 'POSTEOF'
   [post text here]
   POSTEOF
   python3 ~/Desktop/Projects/content/scripts/post-to-x.py "$(cat /tmp/cc-post-text.txt)"
   ```

   If `post-to-x.py` does NOT exist yet:
   ```
   X posting script not set up yet. Copy this text and post manually:

   ---
   [post text]
   ---

   Then tell me the post URL so I can update the tracking files.
   ```

5. **On success:**
   - Read `content-ideas.md` — if this post came from a queued idea, move it from `## Queue` to `## Used` with today's date, the platform, and the permalink
   - Append to `content-posts.md`:
     ```
     - **[YYYY-MM-DD]** [platform] [first 30 chars of post text]...
       - Text: [full post text]
       - Platform: [x | threads]
       - Link: [permalink URL]
     ```
   - Confirm: "Posted to [Platform]! [permalink URL]"

6. **On failure:**
   - If 401 (Threads): "Token expired. Regenerate at Meta Developer Portal and run: `export THREADS_ACCESS_TOKEN=<new_token>`"
   - If 401 (X): "Token expired or invalid. Check your X API credentials."
   - If 4xx: Show the error message and suggest a fix
   - If 5xx: "[Platform] server error. Try again in a minute."
   - If network error: "Can't reach [Platform]. Check your connection."
```

- [ ] **Step 5: Update the Rules section**

```markdown
## Rules

- NEVER post without explicit user confirmation
- NEVER modify the post text — post exactly what was approved
- If the script fails, do NOT retry automatically — show the error and let user decide
- For X without the posting script: facilitate manual posting by showing copyable text
```

- [ ] **Step 6: Verify the complete file reads correctly**

Read the entire file back and confirm.

- [ ] **Step 7: Commit**

```bash
git add ~/.claude/skills/cc-post/SKILL.md
git commit -m "feat(cc-post): add X posting support with manual fallback"
```

### Task 8: Update `/cc-research` Skill

Add English/X trend scanning alongside Chinese.

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-research/SKILL.md`

- [ ] **Step 1: Update YAML frontmatter**

```yaml
---
name: cc-research
description: Research trending topics and content opportunities for Threads and X. Use when user says "/cc-research", "what's trending", or "find me content ideas". Does NOT trigger on general web research or non-content questions.
---
```

- [ ] **Step 2: Update the title and intro**

```markdown
# Research Trending Topics

Scan for trending topics across both the English build-in-public/AI space (X) and the Chinese AI content space (Threads).
```

- [ ] **Step 3: Update the Search step**

Replace step 1 with:

```markdown
1. **Search for trends:** Use WebSearch for both tracks:

   **English (X / build-in-public):**
   - "build in public" trending AI tools
   - indie hacker AI automation
   - "shipped" OR "launched" AI SaaS recent
   - Adapt queries based on current events and recent AI releases

   **Chinese (Threads):**
   - "Threads AI 趨勢 繁體中文" (Threads AI trends, Traditional Chinese)
   - "AI 工具 推薦 2026" (AI tool recommendations)
   - "ChatGPT Claude 使用心得" (usage experiences)
   - Adapt queries based on current events and recent AI releases
```

- [ ] **Step 4: Update the topic identification step**

Replace step 2 with:

```markdown
2. **Identify top 3-5 topics per track:**
   For each topic, note:
   - **Platform:** X, Threads, or both
   - **Hook:** What's the attention-grabbing angle?
   - **Engagement signal:** Why is this getting traction?
   - **Our angle:** How can Mike talk about this authentically (from experience, not theory)?
```

- [ ] **Step 5: Update the research output format**

Replace step 5 with:

```markdown
5. **Save findings:** Append to `content-research.md` under today's date:

   ## YYYY-MM-DD

   ### X (English)

   #### [Topic 1]
   - Hook: ...
   - Engagement: ...
   - Our angle: ...
   - Matched ideas: [idea from queue, if any]

   ### Threads (Chinese)

   #### [Topic 1]
   - Hook: ...
   - Engagement: ...
   - Our angle: ...
   - Matched ideas: [idea from queue, if any]
```

- [ ] **Step 6: Update the presentation format**

Replace step 6 with:

```markdown
6. **Present summary:**

   🔍 Research Results

   **X (English):**
   1. [Topic] — [hook] — [matched idea or "new"]
   2. [Topic] — [hook] — [matched idea or "new"]

   **Threads (Chinese):**
   1. [Topic] — [hook] — [matched idea or "new"]
   2. [Topic] — [hook] — [matched idea or "new"]

   Recommended: [top pick per platform with reason]

   Next: `/cc-draft --platform x` with [topic] or `/cc-draft --platform threads` with [topic]
```

- [ ] **Step 7: Update the Rules section**

Replace the Rules section:

```markdown
## Rules

- Cover both English and Chinese content spaces
- Prioritize topics Mike has personal experience with (can tell a real story)
- Don't research topics that require expertise Mike doesn't have
- Keep research focused — 15 minutes max, not a deep dive
- For X: focus on build-in-public, AI tools, indie hacker narratives
- For Threads: focus on Chinese-speaking AI content space
```

- [ ] **Step 8: Verify the complete file reads correctly**

Read the entire file back and confirm.

- [ ] **Step 9: Commit**

```bash
git add ~/.claude/skills/cc-research/SKILL.md
git commit -m "feat(cc-research): add English X trend scanning for dual-track"
```

### Task 9: Update `/cc-review` Skill

Update dashboard to show both platform tracks.

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-review/SKILL.md`

- [ ] **Step 1: Update YAML frontmatter**

```yaml
---
name: cc-review
description: Show daily content dashboard with queued drafts, recent posts, and posting streak across X and Threads. Use when user says "/cc-review", "content status", or "what should I post today". Does NOT trigger on code reviews or PR reviews.
---
```

- [ ] **Step 2: Update the dashboard presentation format**

Replace step 5 with:

```markdown
5. **Present dashboard:**

   📊 Content Status

   **Queue:** X raw | Y drafted
   - For X: [count] | For Threads: [count] | Both: [count]

   **Recent Posts:**
   - [date] [platform] [first 30 chars]...
   - [date] [platform] [first 30 chars]...
   - [date] [platform] [first 30 chars]...

   **Streaks:**
   - X: N days [🔥 if 3+, ⚠️ if at risk]
   - Threads: N days [🔥 if 3+, ⚠️ if at risk]

   **Today ([day]):**
   - X suggestion: [type from calendar]
   - Threads suggestion: [type from calendar]
   - Best match from queue: [idea] — or "nothing queued, try /cc-capture first"

   Next: Run `/cc-draft --platform x` or `/cc-draft --platform threads` with [idea]
```

- [ ] **Step 3: Update streak calculation**

Replace step 2 with:

```markdown
2. **Calculate posting streaks (per platform):**
   - Look at dates and platform fields in `content-posts.md`
   - Count consecutive days with at least one post per platform, ending at today or yesterday
   - If no post today yet on a platform, that platform's streak is "at risk"
   - Posts without a platform field count toward Threads streak (backward compat)
```

- [ ] **Step 4: Update calendar check**

Replace step 3 with:

```markdown
3. **Check calendar:** Read `references/content-calendar.md`, find today's day of week, suggest the matching content type for BOTH X and Threads.
```

- [ ] **Step 5: Verify the complete file reads correctly**

Read the entire file back and confirm.

- [ ] **Step 6: Commit**

```bash
git add ~/.claude/skills/cc-review/SKILL.md
git commit -m "feat(cc-review): update dashboard for dual-track with per-platform streaks"
```

### Task 10: Update `/cc-recap` Skill

Update recap to cover both platforms.

**Files:**
- Modify: `/Users/mikeweng/.claude/skills/cc-recap/SKILL.md`

- [ ] **Step 1: Update the presentation format**

Replace step 6 with:

```markdown
6. **Present:**

   📋 Daily Recap

   **Today:**
   - X: [what was posted, with links — or "nothing posted"]
   - Threads: [what was posted, with links — or "nothing posted"]

   **Streaks:**
   - X: N days [🔥 or ⚠️]
   - Threads: N days [🔥 or ⚠️]

   Queue: X raw | Y drafted
   New insights today: N captured

   **Tomorrow ([day]):**
   - X: [suggestion from calendar]
   - Threads: [suggestion from calendar]
   - Best queued idea: [idea] — or "queue is empty"
```

- [ ] **Step 2: Update streak step to be per-platform**

Replace step 3 with:

```markdown
3. **Streak:** Calculate consecutive posting days from `content-posts.md`, per platform. Posts without a platform field count toward Threads.
```

- [ ] **Step 3: Verify the complete file reads correctly**

Read the entire file back and confirm.

- [ ] **Step 4: Commit**

```bash
git add ~/.claude/skills/cc-recap/SKILL.md
git commit -m "feat(cc-recap): update recap for dual-track with per-platform streaks"
```

---

## Chunk 3: X Posting Script

Create the Python script for posting to X via the API.

### Task 11: Create X Posting Script

**Files:**
- Create: `/Users/mikeweng/Desktop/Projects/content/scripts/post-to-x.py`

- [ ] **Step 1: Create the X posting script**

```python
#!/usr/bin/env python3
"""Post text content to X (Twitter) via API v2.

Usage:
  python3 post-to-x.py "Post text here"
  python3 post-to-x.py --dry-run "Post text here"

Requires env vars:
  X_API_KEY — API key (consumer key)
  X_API_SECRET — API secret (consumer secret)
  X_ACCESS_TOKEN — user access token
  X_ACCESS_TOKEN_SECRET — user access token secret

Note: Requires X API Basic tier ($100/month) for write access.
"""

import json
import os
import sys
import time
import hashlib
import hmac
import base64
import urllib.parse
import uuid
import requests


TWEET_URL = "https://api.twitter.com/2/tweets"


def _oauth_header(method, url, params, api_key, api_secret, token, token_secret):
    """Generate OAuth 1.0a Authorization header."""
    oauth_params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }

    all_params = {**oauth_params, **params}
    sorted_params = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in sorted(all_params.items())
    )
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
    signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"

    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()

    oauth_params["oauth_signature"] = signature
    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    return auth_header


def _handle_error(resp, step_name):
    """Handle 4xx/5xx errors with user-friendly messages."""
    if resp.status_code == 401:
        print("Error: 401 Unauthorized — token expired or invalid.", file=sys.stderr)
        print("Check your X API credentials (X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET).", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 403:
        print("Error: 403 Forbidden — your X API plan may not support posting.", file=sys.stderr)
        print("X API Basic tier ($100/month) is required for write access.", file=sys.stderr)
        sys.exit(1)
    if 400 <= resp.status_code < 500:
        try:
            detail = json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            detail = resp.text
        print(f"Error in {step_name}: {resp.status_code}", file=sys.stderr)
        print(detail, file=sys.stderr)
        sys.exit(1)


def _retry_on_5xx(make_request, step_name):
    """Execute request, retry once on 5xx."""
    resp = make_request()
    if resp.status_code >= 500:
        print(f"Server error in {step_name} ({resp.status_code}), retrying once...", file=sys.stderr)
        time.sleep(2)
        resp = make_request()
    _handle_error(resp, step_name)
    resp.raise_for_status()
    return resp


def post_to_x(text: str, dry_run: bool = False) -> str:
    """Publish a tweet. Returns the tweet URL."""
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_SECRET")
    token = os.environ.get("X_ACCESS_TOKEN")
    token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET")

    missing = []
    if not api_key:
        missing.append("X_API_KEY")
    if not api_secret:
        missing.append("X_API_SECRET")
    if not token:
        missing.append("X_ACCESS_TOKEN")
    if not token_secret:
        missing.append("X_ACCESS_TOKEN_SECRET")

    if missing:
        print(f"Error: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        print("Set up X API credentials. Basic tier ($100/month) required for posting.", file=sys.stderr)
        sys.exit(1)

    if len(text) > 280:
        print(f"Warning: Tweet is {len(text)} chars (limit 280). May be truncated.", file=sys.stderr)

    if dry_run:
        print(f"[DRY RUN] Would post to X ({len(text)} chars):", file=sys.stderr)
        print(text, file=sys.stderr)
        return "https://x.com/dry-run"

    payload = json.dumps({"text": text})

    def make_request():
        auth = _oauth_header("POST", TWEET_URL, {}, api_key, api_secret, token, token_secret)
        return requests.post(
            TWEET_URL,
            headers={
                "Authorization": auth,
                "Content-Type": "application/json",
            },
            data=payload,
        )

    resp = _retry_on_5xx(make_request, "post tweet")
    data = resp.json()
    tweet_id = data.get("data", {}).get("id")

    if tweet_id:
        # We don't know the username from the API response, but we can construct a generic URL
        # The user can find their tweet at this URL pattern
        return f"https://x.com/i/status/{tweet_id}"
    else:
        return f"Tweet posted but could not get ID. Response: {json.dumps(data)}"


if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = False
    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    if not args:
        print('Usage: python3 post-to-x.py [--dry-run] "Post text"', file=sys.stderr)
        sys.exit(1)

    text = args[0]
    url = post_to_x(text, dry_run=dry_run)
    print(url)
```

- [ ] **Step 2: Verify the script is syntactically valid**

```bash
python3 -c "import py_compile; py_compile.compile('scripts/post-to-x.py', doraise=True)"
```

- [ ] **Step 3: Test with dry run**

```bash
X_API_KEY=test X_API_SECRET=test X_ACCESS_TOKEN=test X_ACCESS_TOKEN_SECRET=test python3 scripts/post-to-x.py --dry-run "Hello from the content engine"
```

Expected: `[DRY RUN] Would post to X (36 chars):` followed by the text, then `https://x.com/dry-run`

- [ ] **Step 4: Commit**

```bash
git add scripts/post-to-x.py
git commit -m "feat: add X/Twitter posting script with OAuth 1.0a"
```

---

## Chunk 4: Final Verification

### Task 12: End-to-End Verification

Verify all skills read correctly and the system is consistent.

**Files:** All modified files from Tasks 1-11

- [ ] **Step 1: Verify all skill files parse correctly**

Read each skill file and confirm:
- `/Users/mikeweng/.claude/skills/cc-capture/SKILL.md` — has platform classification step
- `/Users/mikeweng/.claude/skills/cc-draft/SKILL.md` — has platform parameter, voice routing, both character limits
- `/Users/mikeweng/.claude/skills/cc-post/SKILL.md` — has X posting with manual fallback
- `/Users/mikeweng/.claude/skills/cc-research/SKILL.md` — has English and Chinese search queries
- `/Users/mikeweng/.claude/skills/cc-review/SKILL.md` — has per-platform streaks and suggestions
- `/Users/mikeweng/.claude/skills/cc-recap/SKILL.md` — has per-platform recap

- [ ] **Step 2: Verify reference files exist**

```bash
ls -la ~/.claude/skills/cc-draft/references/anti-ai-patterns.md
ls -la ~/.claude/skills/cc-draft/references/anti-ai-patterns-en.md
ls -la ~/.claude/skills/cc-capture/references/ideas-vault-format.md
ls -la ~/.claude/skills/cc-review/references/content-calendar.md
```

All four files should exist.

- [ ] **Step 3: Verify Obsidian vault files**

```bash
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/content/voice.md
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/content/voice-en.md
```

Both voice profiles should exist.

- [ ] **Step 4: Verify X posting script**

```bash
ls -la ~/Desktop/Projects/content/scripts/post-to-x.py
ls -la ~/Desktop/Projects/content/scripts/post-to-threads.py
```

Both scripts should exist.

- [ ] **Step 5: Check for consistency across all files**

Verify that:
- Platform values are consistent: `x | threads | both` everywhere
- Voice profile paths are consistent across cc-draft and any references
- Post log format includes platform field in cc-post, cc-review, cc-recap
- Backward compatibility: entries without platform default to `threads`

- [ ] **Step 6: Final commit if any fixes were needed**

```bash
git add -u && git commit -m "fix: address consistency issues from verification" || echo "Nothing to fix"
```
