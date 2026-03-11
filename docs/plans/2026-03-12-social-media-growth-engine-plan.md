# Social Media Growth Engine — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build 6 Claude Code skills (`/cc-*`) that form a content creation pipeline for Threads (Chinese), plus supporting data files and a posting script.

**Architecture:** Claude Code skills (SKILL.md + references/) in `~/.claude/skills/cc-*/`, data files in Obsidian vault, one Python posting script in `~/Desktop/Projects/content/scripts/`. Skills are instruction documents that guide Claude's behavior — no compiled code, no build step.

**Tech Stack:** Claude Code skills (Markdown + YAML frontmatter), Python 3 (requests library), Threads Graph API v1.0, Obsidian vault (iCloud-synced Markdown)

**Spec:** `~/Desktop/Projects/content/docs/specs/2026-03-12-social-media-growth-engine-design.md`

---

## Chunk 1: Foundation + /cc-capture

### Task 1: Create Obsidian Data Files

Create the 3 new data files that all skills depend on.

**Files:**
- Create: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md`
- Create: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-voice.md`
- Create: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-posts.md`

- [ ] **Step 1: Create content-ideas.md (ideas vault)**

```markdown
# Content Ideas

## Queue

## Used
```

- [ ] **Step 2: Create content-voice.md (voice profile — single source of truth)**

Copy the full Voice Profile section from the spec (lines 281-341) into this file. This is the canonical voice reference that `/cc-draft` reads at runtime.

```markdown
# Voice Profile

## Tone: 朋友 + 實驗者

Casual friend who experiments with AI and shows receipts. Not a teacher, not a guru.

## Voice DNA (from real LINE conversations)

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
```

- [ ] **Step 3: Create content-posts.md (published post log)**

```markdown
# Published Posts
```

- [ ] **Step 4: Verify all 4 content files exist**

Run: `ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/projects/content-*.md`
Expected: 4 files — content-log.md (existing), content-ideas.md, content-voice.md, content-posts.md

- [ ] **Step 5: Commit**

```bash
cd ~/Desktop/Projects/content
git add docs/plans/2026-03-12-social-media-growth-engine-plan.md
git commit -m "docs: add implementation plan for social media growth engine"
```

Note: Obsidian vault files are outside the git repo — no git tracking for them.

---

### Task 2: Build /cc-capture Skill

The simplest skill — accepts raw ideas and appends them to the ideas vault.

**Files:**
- Create: `~/.claude/skills/cc-capture/SKILL.md`
- Create: `~/.claude/skills/cc-capture/references/ideas-vault-format.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p ~/.claude/skills/cc-capture/references
```

- [ ] **Step 2: Create references/ideas-vault-format.md**

````markdown
# Ideas Vault Format

## Entry Format (append under `## Queue`)

```
- **[YYYY-MM-DD]** [type] Short description
  - Raw: (original input verbatim)
  - Angle: (suggested angle, or "none yet")
  - Source: (URL if applicable)
  - Status: raw | drafted | posted
```

## Types
- `thought` — half-formed idea, observation, shower thought
- `link` — URL to article, post, video worth commenting on
- `demo` — something Mike built that's worth showing
- `reference` — useful resource to cite or build content around
- `hot-take` — strong opinion, contrarian view, reaction

## Moving to Used (when posted)

Move the entry from `## Queue` to `## Used` and add:
```
- **[YYYY-MM-DD]** [type] Short description
  - Posted: YYYY-MM-DD
  - Link: (threads URL)
```
````

- [ ] **Step 3: Create SKILL.md**

```markdown
---
name: cc-capture
description: Capture raw content ideas into the ideas vault. Use when user says "/cc-capture", "capture this for content", "idea for a post", or "save this for threads". Does NOT trigger on general URL sharing or non-content tasks.
---

# Capture Content Idea

Capture a raw content idea and store it in the ideas vault for later drafting.

## Paths

- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md`
- Format reference: `references/ideas-vault-format.md`

## Steps

1. **Accept input** — text, URL, screenshot, or half-formed thought. Whatever the user gives you.

2. **If URL:** Use WebFetch to retrieve and summarize the content in 1-2 sentences.

3. **Classify type:** Pick one: `thought` | `link` | `demo` | `reference` | `hot-take`

4. **Append to ideas vault:** Read `content-ideas.md`, then append a new entry under `## Queue` using the format in `references/ideas-vault-format.md`. Use today's date. Preserve the user's original input verbatim in the `Raw:` field.

5. **Suggest angle** if one is obvious from the input. Otherwise set to "none yet".

6. **Confirm** with one line: what was captured, what type, and the angle (if any).

## Rules

- Do NOT draft the post — that's `/cc-draft`
- Do NOT ask clarifying questions unless the input is completely ambiguous
- Keep it fast — capture should feel instant
- Always set Status to `raw`
```

- [ ] **Step 4: Test — trigger with a sample idea**

Open a new Claude Code session and test:
```
/cc-capture 我用 Claude Code 幫自己寫了一個社群引擎，從想法到發文全部自動化
```
Expected: Entry appended to content-ideas.md under Queue, type `thought` or `demo`, one-line confirmation.

- [ ] **Step 5: Test — verify no false positive**

Test that these do NOT trigger cc-capture:
- "check this URL for me" (general URL, no content intent)
- "draft a PR description" (unrelated task)

Expected: No cc-capture behavior.

- [ ] **Step 6: Review content-ideas.md**

Read `content-ideas.md` and verify the entry format matches the spec exactly.

---

## Chunk 2: /cc-draft (Core Skill)

### Task 3: Build /cc-draft Skill

The most complex skill — reads voice profile, drafts posts, self-checks against anti-AI patterns.

**Files:**
- Create: `~/.claude/skills/cc-draft/SKILL.md`
- Create: `~/.claude/skills/cc-draft/references/anti-ai-patterns.md`
- Create: `~/.claude/skills/cc-draft/references/post-examples.md`
- Create: `~/.claude/skills/cc-draft/assets/post-templates.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p ~/.claude/skills/cc-draft/{references,assets}
```

- [ ] **Step 2: Create references/anti-ai-patterns.md**

```markdown
# Anti-AI Patterns — Self-Check Guide

Read this BEFORE writing and AFTER writing. If any "Never" pattern appears in your draft, rewrite.

## Never

- Perfect parallel structure (A does X. B does Y. C does Z.)
- Exactly 3 of anything (3 tips, 3 reasons, 3 examples)
- "在這個...的時代" / "讓我們來看看" / "不得不說"
- Neat conclusions or moral of the story
- Balanced takes or hedging ("雖然...但是...")
- Same sentence lengths throughout
- Transitions between paragraphs ("另外", "此外", "接下來")
- 您 anywhere — always 你

## Always

- Vary sentence length wildly (5 chars then 25 chars then 8 chars)
- Start mid-thought sometimes (no intro, just jump in)
- Incomplete sentences are fine
- Strong opinions without hedging
- 口語 not 書面語 (spoken, not written Chinese)
- Specific numbers and details ("凌晨2點", "3間房子", "跑了5次")
- Emotional reactions ("我嚇到" not "這非常有趣", "靠" not "令人驚訝")
- Some posts can be just 2-3 sentences

## Self-Check (run after every draft)

1. Could any AI account have written this? → rewrite
2. Is there a detail only Mike would know? → if not, add one
3. Friend texting or teacher lecturing? → must sound like friend
4. Would Mike say this out loud? → mentally read it aloud
```

- [ ] **Step 3: Create references/post-examples.md**

Seed with 3-5 example posts adapted from Mike's LINE message style. These are synthetic examples based on the voice profile, NOT real posts. They serve as style reference.

```markdown
# Post Examples — Style Reference

These are reference examples showing the target voice. Use them to calibrate tone, not to copy.

## Example 1: Demo Post
```
靠 我剛用 AI 幫自己做了一個記帳 app
從零到上架 AppStore 花不到一週
重點是我根本不會寫 Swift

你覺得呢 這算作弊嗎 哈哈哈哈
```

## Example 2: Curated Insight
```
欸 OpenAI 昨天丟了一個新東西出來
簡單講就是：你可以用講話的方式寫程式了

不是那種「嘿 Siri」的程度
是真的可以蓋一整個網站的那種

我試了一下
嗯
還沒到那麼神
但已經嚇到我了
```

## Example 3: Hot Take
```
AI 不會取代你的工作

但會用 AI 的人會

這句話聽到爛了對不對
問題是 真的沒幾個人在用

我問了身邊20個朋友
只有2個有在用 ChatGPT
其他人連帳號都沒註冊

所以與其怕被取代
不如現在花30分鐘註冊一個來玩玩
```

## Example 4: Short Reaction (2-3 sentences)
```
今天看到有人用 Claude 寫了一整本小說
200頁欸
我連 200 字的文案都還在跟 AI 吵架 哈哈哈哈
```
```

- [ ] **Step 4: Create assets/post-templates.md**

```markdown
# Post Templates

## Template: Demo Post
```
[驚嘆/反應] 我 [做了什麼]
[具體數字/結果]
[一個轉折或意外]

[互動收尾]
```

## Template: Curated Insight
```
[Hook — 發生了什麼]
[用最少的字解釋]
[我的反應/試用心得]
[問題或 CTA]
```

## Template: Hot Take
```
[強烈觀點]
[為什麼 — 用具體數字或經驗]
[所以呢 — 行動建議]
```

## Template: Personal Journey
```
[故事的結果先講]
[怎麼發生的 — 短版]
[學到什麼 — 不要說教]
```

## Guidelines
- Templates are starting points, not rigid formats
- Break any template rule if it makes the post sound more natural
- Under 300 characters unless it's a story post
- Hook in first line ALWAYS
```

- [ ] **Step 5: Create SKILL.md**

```markdown
---
name: cc-draft
description: Draft Threads posts in Mike's authentic voice. Use when user says "/cc-draft", "write a threads post", or "draft something for threads". Does NOT trigger on general writing tasks like docs, emails, or code comments.
---

# Draft Threads Post

Write a Threads post in Mike's authentic voice — casual Taiwanese Mandarin, 朋友 + 實驗者 tone.

## Paths

- Voice profile (MUST read first): `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-voice.md`
- Anti-AI patterns (MUST read first): `references/anti-ai-patterns.md`
- Post examples: `references/post-examples.md`
- Post templates: `assets/post-templates.md`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md`
- Content log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`

## Steps

1. **Always first:** Read `content-voice.md` AND `references/anti-ai-patterns.md`. Do not skip this.

2. **Get the topic:**
   - If user provides a specific idea → use it
   - If user says "from queue" or "pick one" → read `content-ideas.md`, suggest top 3 from Queue with `raw` status
   - If user says "from research" → read `content-research.md` (if it exists)

3. **Gather source material:** Read `content-ideas.md` and `content-log.md` for relevant context, examples, or data points that could strengthen the post.

4. **Read** `references/post-examples.md` and `assets/post-templates.md` for style reference.

5. **Draft the post:**
   - 朋友 + 實驗者 tone from voice profile
   - Taiwanese Mandarin casual vocabulary (靠、哈哈哈哈、蝦米、欸)
   - Under 300 characters (each Chinese char = 1 character)
   - Hook in first line
   - Engagement close (question, CTA, or "你覺得呢？")
   - Break into 2-3 short lines, not one paragraph

6. **Self-check gate:** Review the draft against `references/anti-ai-patterns.md`:
   - Any "Never" pattern detected? → rewrite that part
   - All 4 self-check questions pass? → proceed
   - If rewritten, re-check again

7. **Present to user:**
   ```
   ---
   [post text]
   ---
   Source: [where the idea came from]
   Characters: [count]

   Does this sound like you? Edit inline, or say "reject" to start fresh.
   ```

8. **Handle feedback:**
   - User edits inline → apply edits, re-count characters
   - User says "reject" or "try again" → draft from scratch with different angle
   - User approves → update ideas vault status to `drafted` (if idea came from queue)

## Character Count

- 300 is a style guideline for readability
- Threads API limit is 500 — stay well under
- Count Unicode characters (each Chinese character = 1)
- Emoji = 1 character

## Rules

- NEVER sound like a tutorial or educational content
- NEVER use 您 — always 你
- NEVER hedge or give balanced takes
- If you catch yourself writing "在這個...的時代" — stop and rewrite everything
- Short > long. 2 sentences > 5 sentences.
```

- [ ] **Step 6: Test — draft from a specific idea**

```
/cc-draft 我用 Claude Code 花了三天做了一個自動發文引擎
```

Expected: Post in Mike's voice, under 300 chars, hook first, no anti-AI patterns.

- [ ] **Step 7: Test — draft from queue**

```
/cc-draft pick one from queue
```

Expected: Shows top ideas from Queue, user picks one, drafts in voice.

- [ ] **Step 8: Voice fidelity check**

Read the generated draft and compare against LINE chat patterns. Check:
- Does it use interjections (欸、靠、喔對)?
- Are sentences under 20 chars each?
- Is it broken into short lines?
- No parallel structure?
- Would Mike say this out loud?

If score < 4/5 on "sounds like me" → adjust voice profile or anti-AI patterns.

- [ ] **Step 9: Commit**

No git commit needed — skills live in `~/.claude/skills/` which is outside the repo.

---

## Chunk 3: /cc-post + Posting Script

### Task 4: Build post-to-threads.py

The only real Python code in this project. Sync version of the threads-poster API logic.

**Files:**
- Create: `~/Desktop/Projects/content/scripts/post-to-threads.py`

- [ ] **Step 1: Write the posting script**

```python
#!/usr/bin/env python3
"""Post text content to Threads via Graph API.

Usage:
  python3 post-to-threads.py "Post text here"
  python3 post-to-threads.py --dry-run "Post text here"

Requires env vars:
  THREADS_ACCESS_TOKEN — long-lived token (~60 day expiry)
  THREADS_USER_ID — numeric Threads user ID
"""

import json
import os
import sys
import time
import requests

BASE_URL = "https://graph.threads.net/v1.0"


def _handle_error(resp, step_name):
    """Handle 4xx/5xx errors with user-friendly messages. Returns True if fatal."""
    if resp.status_code == 401:
        print("Error: 401 Unauthorized — token expired or invalid.", file=sys.stderr)
        print("Regenerate token at Meta Developer Portal and update THREADS_ACCESS_TOKEN.", file=sys.stderr)
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


def post_to_threads(text: str, dry_run: bool = False) -> str:
    """Publish a text post to Threads. Returns permalink URL."""
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")

    if not token:
        print("Error: THREADS_ACCESS_TOKEN env var not set", file=sys.stderr)
        print("Get a token from Meta Developer Portal and export it.", file=sys.stderr)
        sys.exit(1)
    if not user_id:
        print("Error: THREADS_USER_ID env var not set", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        print(f"[DRY RUN] Would post to Threads ({len(text)} chars):", file=sys.stderr)
        print(text, file=sys.stderr)
        return "https://threads.net/dry-run"

    # Step 1: Create container
    create_resp = _retry_on_5xx(
        lambda: requests.post(
            f"{BASE_URL}/{user_id}/threads",
            params={
                "media_type": "TEXT",
                "text": text,
                "access_token": token,
            },
        ),
        "create container",
    )
    creation_id = create_resp.json()["id"]

    # Wait for container to finish processing
    time.sleep(3)

    # Step 2: Publish
    publish_resp = _retry_on_5xx(
        lambda: requests.post(
            f"{BASE_URL}/{user_id}/threads_publish",
            params={
                "creation_id": creation_id,
                "access_token": token,
            },
        ),
        "publish",
    )
    post_id = publish_resp.json()["id"]

    # Step 3: Get permalink
    permalink_resp = requests.get(
        f"{BASE_URL}/{post_id}",
        params={
            "fields": "permalink",
            "access_token": token,
        },
    )
    permalink_resp.raise_for_status()
    return permalink_resp.json().get("permalink", f"Post ID: {post_id}")


if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = False
    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    if not args:
        print("Usage: python3 post-to-threads.py [--dry-run] \"Post text\"", file=sys.stderr)
        sys.exit(1)

    text = args[0]
    permalink = post_to_threads(text, dry_run=dry_run)
    print(permalink)
```

- [ ] **Step 2: Verify script is syntactically valid**

Run: `python3 -m py_compile ~/Desktop/Projects/content/scripts/post-to-threads.py && echo OK`

Expected: Prints "OK" with no errors.

- [ ] **Step 3: Verify env vars are set**

Run: `echo "TOKEN: ${THREADS_ACCESS_TOKEN:+set}" && echo "USER_ID: ${THREADS_USER_ID:+set}"`

If not set, add them to shell profile. The token can be borrowed from the threads-poster project's .env file:
```bash
# Check threads-poster for existing values
cat ~/Desktop/Projects/threads-poster/.env | grep THREADS
```

- [ ] **Step 4: Commit**

```bash
cd ~/Desktop/Projects/content
git add scripts/post-to-threads.py
git commit -m "feat: add Threads posting script (sync, requests-based)"
```

---

### Task 5: Build /cc-post Skill

Wraps the posting script with confirmation flow and data file updates.

**Files:**
- Create: `~/.claude/skills/cc-post/SKILL.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p ~/.claude/skills/cc-post
```

- [ ] **Step 2: Create SKILL.md**

```markdown
---
name: cc-post
description: Publish approved content to Threads. Use when user says "/cc-post", "publish to threads", or approves a draft for posting. Does NOT trigger on general publishing or deploy tasks.
---

# Post to Threads

Publish approved content to Threads and update tracking files.

## Paths

- Posting script: `~/Desktop/Projects/content/scripts/post-to-threads.py`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md`
- Posts log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-posts.md`

## Steps

1. **Get the post text:**
   - If provided directly → use it
   - If user says "post the last draft" → use the most recent draft from this conversation

2. **Final confirmation:** Show the full post text and ask:
   ```
   Ready to post this to Threads?

   ---
   [post text]
   ---

   Post this? (y/n)
   ```

3. **Wait for explicit "y" or "yes"** before proceeding. Never auto-post.

4. **Publish:** Write the post text to a temp file, then run the posting script. This avoids shell quoting issues with Chinese characters, quotes, and special characters:
   ```bash
   # Write post text to temp file
   cat > /tmp/cc-post-text.txt << 'POSTEOF'
   [post text here]
   POSTEOF
   # Post using the temp file content
   python3 ~/Desktop/Projects/content/scripts/post-to-threads.py "$(cat /tmp/cc-post-text.txt)"
   ```

   The script prints the permalink URL on success.

5. **On success:**
   - Read `content-ideas.md` — if this post came from a queued idea, move it from `## Queue` to `## Used` with today's date and the permalink
   - Append to `content-posts.md`:
     ```
     - **[YYYY-MM-DD]** [first 30 chars of post text]...
       - Text: [full post text]
       - Link: [permalink URL]
     ```
   - Confirm: "Posted! [permalink URL]"

6. **On failure:**
   - If 401: "Token expired. Regenerate at Meta Developer Portal and run: `export THREADS_ACCESS_TOKEN=<new_token>`"
   - If 4xx: Show the error message and suggest a fix
   - If 5xx: "Threads server error. Try again in a minute."
   - If network error: "Can't reach Threads. Check your connection."

## Rules

- NEVER post without explicit user confirmation
- NEVER modify the post text — post exactly what was approved
- If the script fails, do NOT retry automatically — show the error and let user decide
```

- [ ] **Step 3: Test — end-to-end flow (use a test post)**

```
/cc-post 測試發文 請忽略
```

Expected: Shows confirmation prompt, waits for y/n, posts on approval, updates content-posts.md.

**Important:** Only test with a real post if you're OK with it appearing on Threads. For safe testing, use dry-run mode: `python3 ~/Desktop/Projects/content/scripts/post-to-threads.py --dry-run "測試發文"`

- [ ] **Step 4: Test — verify data file updates**

After a successful post, read:
- `content-posts.md` — should have new entry with date, text, and permalink
- `content-ideas.md` — if from queue, should be moved to Used

---

## Chunk 4: /cc-review + /cc-recap

### Task 6: Build /cc-review Skill (Daily Dashboard)

**Files:**
- Create: `~/.claude/skills/cc-review/SKILL.md`
- Create: `~/.claude/skills/cc-review/references/content-calendar.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p ~/.claude/skills/cc-review/references
```

- [ ] **Step 2: Create references/content-calendar.md**

```markdown
# Content Calendar — Weekly Rhythm

## Default Schedule

- **Mon:** Demo post (show something you built)
- **Tue:** Curated insight (translate English AI news)
- **Wed:** Hot take or personal journey
- **Thu:** Demo post or audience response
- **Fri:** Curated insight or trending topic
- **Sat:** Personal journey / week reflection
- **Sun:** Audience question / engagement post

## Rules

- Flexible — trends override calendar
- If a major AI announcement drops, post about it regardless of day
- Weekend posts can be lighter / more personal
- Don't force a category if nothing fits — skip and post what feels right
```

- [ ] **Step 3: Create SKILL.md**

```markdown
---
name: cc-review
description: Show daily content dashboard with queued drafts, recent posts, and posting streak. Use when user says "/cc-review", "content status", or "what should I post today". Does NOT trigger on code reviews or PR reviews.
---

# Content Dashboard

Show a quick overview of content status, streak, and today's suggestion.

## Paths

- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md`
- Posts log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-posts.md`
- Content log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`
- Content calendar: `references/content-calendar.md`
- Research (if exists): `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-research.md`

## Steps

1. **Read data files:**
   - `content-ideas.md` — count entries by status (raw, drafted, posted)
   - `content-posts.md` — get last 3-5 posts with dates
   - `content-log.md` — check for recent insights (last 3 days)

2. **Calculate posting streak:**
   - Look at dates in `content-posts.md`
   - Count consecutive days with at least one post, ending at today or yesterday
   - If no post today yet, the streak is "at risk"

3. **Check calendar:** Read `references/content-calendar.md`, find today's day of week, suggest the matching content type.

4. **Cross-reference:** Match today's suggested type against queued ideas with `raw` or `drafted` status. Prioritize ideas that match the day's theme. Also read `content-research.md` (if it exists) and flag any queued ideas that align with recent research trends.

5. **Present dashboard:**
   ```
   📊 Content Status

   Queue: X raw | Y drafted
   Recent:
     - [date] [first 30 chars]...
     - [date] [first 30 chars]...
     - [date] [first 30 chars]...
   Streak: N days [🔥 if 3+, ⚠️ if at risk]

   Today ([day]): [suggested type from calendar]
   Best match from queue: [idea] — or "nothing queued, try /cc-capture first"

   Next: Run `/cc-draft` with [idea] or `/cc-capture` to add ideas
   ```

6. **Handoff is manual** — suggest the next command but let user invoke it.

## Rules

- Keep the dashboard compact — this should take 2 seconds to scan
- Don't editorialize — just show the data
- If queue is empty, say so directly and suggest `/cc-capture`
```

- [ ] **Step 4: Test dashboard**

```
/cc-review
```

Expected: Dashboard with queue counts, streak, and suggestion. Since we just set up, queue should show the test idea from Task 2.

---

### Task 7: Build /cc-recap Skill (End of Day)

**Files:**
- Create: `~/.claude/skills/cc-recap/SKILL.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p ~/.claude/skills/cc-recap
```

- [ ] **Step 2: Create SKILL.md**

```markdown
---
name: cc-recap
description: End-of-day content summary with streak tracking and tomorrow's suggestions. Use when user says "/cc-recap", "content recap", or "how's my posting streak".
---

# Content Recap

End-of-day summary showing what was posted, streak status, and tomorrow's plan.

## Paths

- Posts log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-posts.md`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md`
- Content log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`
- Content calendar: `~/.claude/skills/cc-review/references/content-calendar.md`

## Steps

1. **Today's activity:** Read `content-posts.md` — list anything posted today.

2. **Queue status:** Read `content-ideas.md` — count by status.

3. **Streak:** Calculate consecutive posting days from `content-posts.md`.

4. **New insights:** Read `content-log.md` — count insights captured under today's date heading.

5. **Tomorrow's plan:** Check content calendar for tomorrow's day. Find the best matching queued idea.

6. **Present:**
   ```
   📋 Daily Recap

   Today: [what was posted, with links — or "nothing posted"]
   Streak: N days [🔥 or ⚠️]
   Queue: X raw | Y drafted
   New insights today: N captured

   Tomorrow ([day]): [suggestion from calendar]
   Best queued idea: [idea] — or "queue is empty"
   ```

## Rules

- This is a passive summary — no self-improvement, no analytics
- Self-improvement and performance analysis is `/cc-analyse` (Phase 2)
- Keep it scannable — 5 seconds to read
```

- [ ] **Step 3: Test recap**

```
/cc-recap
```

Expected: Recap showing today's activity and tomorrow's suggestion.

- [ ] **Step 4: Commit posting script if not already committed**

Verify all committed files are up to date:
```bash
cd ~/Desktop/Projects/content && git status
```

---

## Chunk 5: /cc-research

### Task 8: Build /cc-research Skill

Last in build order — uses WebSearch for trend scanning.

**Files:**
- Create: `~/.claude/skills/cc-research/SKILL.md`
- Create: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-research.md`

- [ ] **Step 1: Create directory and data file**

```bash
mkdir -p ~/.claude/skills/cc-research
```

Create `content-research.md` in Obsidian vault:
```markdown
# Content Research
```

- [ ] **Step 2: Create SKILL.md**

```markdown
---
name: cc-research
description: Research trending topics and content opportunities for Threads. Use when user says "/cc-research", "what's trending on threads", or "find me content ideas". Does NOT trigger on general web research or non-content questions.
---

# Research Trending Topics

Scan for trending AI topics in the Chinese-speaking Threads/social media space and identify content opportunities.

## Paths

- Research log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-research.md`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md`
- Content log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`

## Steps

1. **Search for trends:** Use WebSearch to find:
   - "Threads AI 趨勢 繁體中文" (Threads AI trends, Traditional Chinese)
   - "AI 工具 推薦 2026" (AI tool recommendations)
   - "ChatGPT Claude 使用心得" (usage experiences)
   - Adapt queries based on current events and recent AI releases

2. **Identify top 3-5 topics:**
   For each topic, note:
   - **Hook:** What's the attention-grabbing angle?
   - **Engagement signal:** Why is this getting traction?
   - **Our angle:** How can Mike talk about this authentically (from experience, not theory)?

3. **Cross-reference with ideas vault:**
   Read `content-ideas.md` — flag any queued ideas that match trending topics. These are high-priority drafts.

4. **Cross-reference with content log:**
   Read `content-log.md` — flag any extracted insights that could be turned into posts on trending topics.

5. **Save findings:** Append to `content-research.md` under today's date:
   ```markdown
   ## YYYY-MM-DD

   ### [Topic 1]
   - Hook: ...
   - Engagement: ...
   - Our angle: ...
   - Matched ideas: [idea from queue, if any]

   ### [Topic 2]
   ...
   ```

6. **Present summary:**
   ```
   🔍 Research Results

   Trending:
   1. [Topic] — [hook] — [matched idea or "new"]
   2. [Topic] — [hook] — [matched idea or "new"]
   3. [Topic] — [hook] — [matched idea or "new"]

   Recommended: [top pick with reason]

   Next: `/cc-draft` with [topic] or `/cc-capture` to queue for later
   ```

## Tools

- **WebSearch** — primary tool for trend scanning
- **Playwright** — aspirational for Phase 2, unreliable for Threads due to Meta anti-scraping

## Rules

- Focus on Chinese-speaking AI content space
- Prioritize topics Mike has personal experience with (can tell a real story)
- Don't research topics that require expertise Mike doesn't have
- Keep research focused — 15 minutes max, not a deep dive
```

- [ ] **Step 3: Test research**

```
/cc-research
```

Expected: WebSearch queries executed, 3-5 topics identified, cross-referenced with vault, saved to content-research.md.

- [ ] **Step 4: Final commit**

```bash
cd ~/Desktop/Projects/content
git status
# Commit any remaining changes
```

---

## Chunk 6: End-to-End Testing + Polish

### Task 9: Full Pipeline Test

Test the complete flow: capture → draft → post.

- [ ] **Step 1: Capture a real idea**

```
/cc-capture 我花了整整一個晚上跟 AI 討論怎麼幫自己建一個社群內容引擎，從研究、寫稿到發文全部 AI 化，但每一篇都要聽起來像是我本人寫的
```

Verify: Entry in content-ideas.md Queue section.

- [ ] **Step 2: Draft from the captured idea**

```
/cc-draft pick one from queue
```

Verify:
- Voice matches Mike's LINE style
- Under 300 chars
- Hook first, engagement close
- No anti-AI patterns
- "Does this sound like you?" prompt shown

- [ ] **Step 3: Post the approved draft**

```
/cc-post
```

Verify:
- Confirmation prompt shown
- After approval: script executes, permalink returned
- content-ideas.md: idea moved to Used
- content-posts.md: entry appended with date and link

- [ ] **Step 4: Check dashboard**

```
/cc-review
```

Verify: Dashboard shows updated queue, recent post, streak = 1.

- [ ] **Step 5: Run recap**

```
/cc-recap
```

Verify: Shows today's post, streak, tomorrow's suggestion.

---

### Task 10: Trigger Testing (Spec Level 1)

Verify skills trigger correctly. Spec requires 10 positive + 10 negative per skill; we test a representative set and expand if issues found.

- [ ] **Step 1: Test positive triggers (should trigger)**

Test each skill with 5+ varied phrasings:
- `/cc-capture` — "save this for threads", "idea for a post", "capture this for content", "save this for later posting", "這個可以拿來發文"
- `/cc-draft` — "write a threads post", "draft something for threads", "幫我寫一篇 threads", "draft a post about AI", "write something about this for threads"
- `/cc-post` — "publish to threads", "post this to threads", "發到 threads", "post the last draft", "publish this"
- `/cc-review` — "content status", "what should I post today", "show me my content dashboard", "content queue status", "今天發什麼"
- `/cc-recap` — "content recap", "how's my posting streak", "daily recap", "how did I do today", "posting streak"
- `/cc-research` — "what's trending on threads", "find me content ideas", "research trending AI topics", "what's hot in AI right now", "找靈感"

Expected: Each triggers the correct skill. Target: 90%+ success rate.

- [ ] **Step 2: Test negative triggers (should NOT trigger)**

Test 10 prompts that should NOT trigger any cc-* skill:
- "Draft a PR description" → NOT cc-draft
- "Review my code" → NOT cc-review
- "Post to GitHub" → NOT cc-post
- "Research this bug" → NOT cc-research
- "Check this URL for security issues" → NOT cc-capture
- "Deploy to production" → NOT cc-post
- "Write a README" → NOT cc-draft
- "What's the status of the build" → NOT cc-review
- "Summarize today's work" → NOT cc-recap
- "Find information about React hooks" → NOT cc-research

Expected: 0% false positive rate.

- [ ] **Step 3: Document any trigger issues and adjust skill descriptions**

If any false positives or negatives found, update the relevant SKILL.md `description` field to fix.

---

### Task 11: Voice Fidelity Testing (Spec Levels 2, 4, 6)

- [ ] **Step 1: Generate 5 drafts with /cc-draft (Level 2)**

Generate 5 posts on different topics:
1. A demo post about building the growth engine
2. A curated insight about a recent AI release
3. A hot take about AI in daily life
4. A personal journey post
5. A short 2-3 sentence reaction post

For each, score 1-5 on "sounds like me" / "would post this".

- [ ] **Step 2: Compare against LINE messages (Level 2)**

Take 5 real LINE messages from the chat exports (adapted to post format). Put them side by side with the 5 AI drafts. Can you tell which is which? Ask a friend to blind test if possible.

- [ ] **Step 3: Iterative scoring (Level 4)**

For any draft scoring < 4/5:
- Identify what's off (too formal? wrong vocabulary? too structured?)
- Update `content-voice.md` or `anti-ai-patterns.md` to fix
- Regenerate and re-score

Track scores — they should improve over iterations.

- [ ] **Step 4: Anti-AI detection check (Level 6)**

Run 3 generated posts through GPTZero or ZeroGPT:
- If flagged as AI → identify which patterns triggered detection → update `anti-ai-patterns.md`
- Re-generate and re-check
- Goal: consistently pass as human-written

Note: Levels 3 (A/B against sprint calendar) is an ongoing practice, not a one-time test. Do it naturally as you use the system over the first week.

---

### Task 12: Final Cleanup

- [ ] **Step 1: Verify all files exist**

```bash
# Skills (11 files)
ls -la ~/.claude/skills/cc-capture/SKILL.md
ls -la ~/.claude/skills/cc-capture/references/ideas-vault-format.md
ls -la ~/.claude/skills/cc-draft/SKILL.md
ls -la ~/.claude/skills/cc-draft/references/anti-ai-patterns.md
ls -la ~/.claude/skills/cc-draft/references/post-examples.md
ls -la ~/.claude/skills/cc-draft/assets/post-templates.md
ls -la ~/.claude/skills/cc-post/SKILL.md
ls -la ~/.claude/skills/cc-review/SKILL.md
ls -la ~/.claude/skills/cc-review/references/content-calendar.md
ls -la ~/.claude/skills/cc-recap/SKILL.md
ls -la ~/.claude/skills/cc-research/SKILL.md

# Data files (5 files — content-log.md is existing, rest are new)
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/projects/content-ideas.md
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/projects/content-voice.md
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/projects/content-posts.md
ls -la ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain/projects/content-research.md

# Script
ls -la ~/Desktop/Projects/content/scripts/post-to-threads.py
```

- [ ] **Step 2: Test cc-recap reads cc-review's calendar**

Run `/cc-recap` and verify the "Tomorrow" suggestion matches the content calendar. This validates the cross-skill file reference works.

- [ ] **Step 3: Final commit**

```bash
cd ~/Desktop/Projects/content
git add scripts/post-to-threads.py docs/plans/2026-03-12-social-media-growth-engine-plan.md
git commit -m "feat: social media growth engine — 6 skills + posting script

Phase 1 implementation: cc-capture, cc-draft, cc-post, cc-review, cc-recap, cc-research.
Skills in ~/.claude/skills/cc-*/, data files in Obsidian vault."
```

- [ ] **Step 4: Update memory**

Save to `~/.claude/projects/-Users-mikeweng-Desktop-Projects-content/memory/social-media-engine.md`:

```markdown
# Social Media Growth Engine

## Skills (in ~/.claude/skills/)
- cc-capture — raw idea intake → content-ideas.md
- cc-draft — post writer, reads content-voice.md + anti-ai-patterns.md
- cc-post — publishes via post-to-threads.py
- cc-review — daily dashboard with streak + calendar
- cc-recap — end-of-day summary
- cc-research — trend scanning via WebSearch

## Data Files (Obsidian vault)
- ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/
  - content-log.md (existing, cron-fed)
  - content-ideas.md (ideas vault: Queue + Used)
  - content-voice.md (voice profile, single source of truth)
  - content-posts.md (published post log)
  - content-research.md (research findings)

## Posting Script
- ~/Desktop/Projects/content/scripts/post-to-threads.py
- Env vars: THREADS_ACCESS_TOKEN, THREADS_USER_ID
- Supports --dry-run flag

## Spec & Plan
- Spec: docs/specs/2026-03-12-social-media-growth-engine-design.md
- Plan: docs/plans/2026-03-12-social-media-growth-engine-plan.md
```
