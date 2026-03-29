> **SUPERSEDED** by `2026-03-29-postiz-to-direct-api-migration-design.md` — Postiz was removed in favor of direct API scripts.

# Postiz Integration Design — Unified Cross-Platform Posting

## Overview

Replace the unbuilt Python posting scripts with Postiz, a self-hosted open-source social media scheduler. Postiz handles OAuth, scheduling, and multi-platform delivery for 6 platforms. RED (Xiaohongshu) uses Playwright browser automation since no API exists.

**Platforms supported:** X, LinkedIn, Instagram, Threads, TikTok, YouTube, RED

**Ramp-up (aligns with content system design):**
- **Week 1:** X, Threads, Instagram (text + video where ready)
- **Week 2:** + RED (via Playwright)
- **Month 2:** + LinkedIn content posts
- **Video (parallel):** TikTok, YouTube — available once video content is being produced
- All platforms are wired up in Postiz from day one, but posting follows the content system's phased schedule

**Integration method:** Postiz CLI (`postiz` npm package) for API-supported platforms; Playwright MCP for RED; Claude-in-Chrome as RED fallback.

## Context

### What Exists
- **cc-post skill** — orchestrates posting with user confirmation, tracks in Obsidian posts log
- **cc-draft skill** — generates per-platform drafts (X, Threads, Instagram, RED, LinkedIn, video)
- **Content pipeline** — Obsidian queue → draft → review → post → log
- **Platform modules** — format specs for each platform in `cc-draft/references/platforms/`
- **Playwright MCP** — available in Claude Code for browser automation
- **Claude-in-Chrome MCP** — available as fallback browser automation

### What's Missing
- Python posting scripts referenced by cc-post don't exist (`post-to-x.py`, `post-to-threads.py`, `post-to-instagram.py`)
- No posting infrastructure for LinkedIn, TikTok, or YouTube
- No scheduling capability
- No RED automation

### What This Replaces
- `~/Desktop/Projects/content/scripts/post-to-x.py` → `postiz posts:create`
- `~/Desktop/Projects/content/scripts/post-to-threads.py` → `postiz posts:create`
- `~/Desktop/Projects/content/scripts/post-to-instagram.py` → `postiz posts:create`
- LinkedIn manual copy-paste → `postiz posts:create`
- RED manual copy-paste → Playwright browser automation
- No TikTok/YouTube support → `postiz posts:create` with media upload

## Design

### Architecture

```
/cc-post (Claude Code skill)
    │
    ├─ API platforms ──→ Postiz CLI ──→ Postiz (Docker) ──→ X, LinkedIn, Instagram, Threads, TikTok, YouTube
    │
    └─ RED ──→ Playwright MCP (default) ──→ RED web UI
              └─ Chrome fallback ──→ Claude-in-Chrome MCP ──→ RED web UI
```

### Component 1: Postiz Self-Hosted (Docker)

**What:** Run Postiz locally via Docker Compose on Mike's Mac.

**Setup:**
1. Clone Postiz repo or use their Docker image
2. `docker compose up -d` — runs Postiz web UI + backend + database
3. Access Postiz web UI (port varies by Postiz version — commonly 4200 for frontend, 3000 for backend; check their docker-compose.yml)
4. Connect social accounts via OAuth through the Postiz UI (one-time per platform)
5. Generate API key in Postiz settings
6. Store API key and integration IDs in `~/.env.postiz` (sourced by cc-post)

**Environment file** (`~/.env.postiz`):
```bash
export POSTIZ_API_KEY=pos_xxxxx
export POSTIZ_API_URL=http://localhost:XXXX  # Set to actual Postiz backend port after docker setup

# Integration IDs (populated after connecting accounts)
export POSTIZ_X_ID=xxx
export POSTIZ_LINKEDIN_ID=xxx
export POSTIZ_INSTAGRAM_ID=xxx
export POSTIZ_THREADS_ID=xxx
export POSTIZ_TIKTOK_ID=xxx
export POSTIZ_YOUTUBE_ID=xxx
```

**Docker health:** cc-post checks if Postiz is running before attempting to post (`curl -sf $POSTIZ_API_URL` — exact health endpoint TBD during setup). If Docker container is down, prompt user to start it.

### Component 2: Postiz CLI Integration

**What:** Install `postiz` npm package globally. cc-post calls it via Bash instead of the Python scripts.

**Install:** `npm install -g postiz`

> **CLI flag verification needed:** The examples below use flags from the Postiz CLI docs (`-c`, `-i`, `-s`, `-m`). During implementation, verify exact flag names and output formats by running `postiz --help` and `postiz posts:create --help`. The `postiz upload` output format (JSON structure, field names) must be verified before building the media upload flow.

**Posting flow (text platforms — X, LinkedIn, Threads):**
```bash
source ~/.env.postiz
postiz posts:create \
  -c "Post content here" \
  -i "$POSTIZ_X_ID"
```

**Posting flow (media platforms — Instagram, TikTok, YouTube):**
```bash
source ~/.env.postiz

# Step 1: Upload media (verify output format during implementation)
MEDIA_RESULT=$(postiz upload /path/to/video.mp4)
# Parse media ID or URL from result — exact field TBD

# Step 2: Create post with media
postiz posts:create \
  -c "Caption text" \
  -i "$POSTIZ_TIKTOK_ID" \
  -m "$MEDIA_RESULT"
```

**Scheduling:**

Two layers — cc-post's `--at` flag (human-readable) and Postiz CLI's `-s` flag (ISO 8601):

| Layer | Flag | Format | Example |
|-------|------|--------|---------|
| cc-post skill | `--at` | Human-readable | `--at "tomorrow 9am"` |
| Postiz CLI | `-s` | ISO 8601 | `-s "2026-03-26T09:00:00+11:00"` |

cc-post translates `--at` → ISO 8601 (Sydney timezone AEDT/AEST) → passes `-s` to Postiz CLI.

```bash
# Immediate (default — no -s flag)
postiz posts:create -c "Content" -i "$POSTIZ_X_ID"

# Scheduled (cc-post converts "tomorrow 9am" to ISO 8601 and passes -s)
postiz posts:create -c "Content" -i "$POSTIZ_X_ID" -s "2026-03-26T09:00:00+11:00"
```

**Multi-platform posting:**
Each platform gets its own `posts:create` call since content differs per platform (X in English, Threads in Chinese, etc.). cc-post loops through the target platforms and calls the CLI once per platform.

**Postiz API rate limit:** 30 requests/hour. A single posting session to 6 platforms with media uploads could consume ~12 requests (upload + create per platform). This is well within limits for normal use, but batch sessions (posting multiple topics) should pace requests. cc-post should warn if approaching the limit.

### Component 3: RED Browser Automation (Playwright)

**What:** Use Playwright MCP to automate posting to RED's web UI (`xiaohongshu.com`), since RED has no public API.

**Authentication:**
- First-time: Playwright opens headed browser (`headless: false`), user scans QR code on phone
- Session cookies saved to `~/.red-session/cookies.json` via Playwright's `context.storageState()`
- On subsequent runs: Playwright creates browser context with saved storage state (`browser.newContext({ storageState: path })`)
- If session expired (detected by URL redirect to login page or absence of editor element): prompt user to re-authenticate via QR
- **Session lifetime:** RED sessions typically last 7-30 days. Expect re-auth ~2-4 times per month.
- **Anti-automation risk:** RED may detect Playwright via browser fingerprinting. Mitigations: use `playwright-extra` with stealth plugin if needed, keep interactions human-paced (add small delays between actions). If RED starts blocking Playwright, fall back to Chrome (where user's real browser profile is trusted).

**Posting flow:**
1. Navigate to RED creator publish URL (stored in `red-selectors.json`, default: `https://creator.xiaohongshu.com/publish/publish`)
2. Wait for page load (check for post editor element)
3. If redirected to login → session expired → prompt for QR re-auth
4. Fill title field
5. Fill body text field
6. Add hashtags
7. Upload cover image if provided
8. Click publish button
9. Verify success (check for success confirmation element)

**Fallback to Chrome:**
If Playwright fails (browser crash, element selectors changed, session issue):
1. cc-post detects the failure
2. Switches to Claude-in-Chrome MCP
3. Navigates to RED creator page in user's existing Chrome session
4. Performs the same fill-and-post flow using Chrome tools
5. Reports which method was used

**Selectors and resilience:**
- RED's web UI changes frequently. Selectors are stored in a config file (`~/.config/cc-post/red-selectors.json`) so they can be updated without modifying the skill
- cc-post logs the exact selectors used on each post for debugging
- If both Playwright and Chrome fail, fall back to manual copy-paste block (current behavior)

### Component 4: Updated cc-post Skill

**What:** Rewrite cc-post SKILL.md to use Postiz CLI + Playwright instead of Python scripts.

**New interface:**
```
/cc-post                              → post to the platform from the draft
/cc-post --at "tomorrow 9am"          → schedule via Postiz
```

Note: Each platform gets its own draft (per the content system's independent-drafts-per-platform model). To post a topic to all platforms, run `/cc-post` once per platform-specific draft. There is no `--platforms` flag — each platform's content is different.

**Updated flow:**
1. **Get post text and platform** (unchanged)
2. **Final confirmation** (unchanged — never auto-post)
3. **Pre-flight checks:**
   - Source `~/.env.postiz`
   - Check Postiz Docker is running: `curl -sf $POSTIZ_API_URL` (exact health endpoint TBD)
   - If down: "Postiz isn't running. Start it with `docker compose -f ~/postiz/docker-compose.yml up -d`"
4. **Publish:**
   - **X, LinkedIn, Threads** → `postiz posts:create -c "..." -i "$ID"`
   - **Instagram** → upload images first, then `postiz posts:create -c "..." -i "$ID" -m "$MEDIA_IDS"`
   - **TikTok, YouTube** → upload video first, then `postiz posts:create -c "..." -i "$ID" -m "$MEDIA_ID"`
   - **RED** → Playwright automation (fallback: Chrome, then manual)
5. **On success** (unchanged — update ideas vault, append to posts log)
6. **On partial failure (multi-platform):**
   - When posting to multiple platforms, each call is independent
   - Log successful posts to Obsidian immediately (don't wait for all to succeed)
   - Report failures with platform name + error, ask user if they want to retry the failed platform(s)
   - Never re-post to already-succeeded platforms
7. **On failure:**
   - Postiz errors: show CLI stderr, suggest checking Postiz web UI
   - RED Playwright errors: auto-fallback to Chrome, then manual
   - Auth errors: platform-specific re-auth instructions

**Scheduling logic:**
- If `--at` provided: parse human time to ISO 8601 (Sydney timezone), pass `-s` to Postiz CLI
- If no `--at`: post immediately
- After scheduling: "Scheduled for [Platform] at [time]. Postiz will publish automatically. Your Mac needs to be awake at that time."

### Component 5: Media Upload Flow

**What:** Handle image and video uploads for visual platforms.

**Image uploads (Instagram carousels, RED cover images):**
- User provides local file paths or URLs
- If local: `postiz upload /path/to/image.jpg` → returns media ID
- If URL: pass URL directly to Postiz (it supports URL-based media)
- Instagram carousels: upload each slide, collect media IDs, pass all to `posts:create`

**Video uploads (TikTok, YouTube, Instagram Reels):**
- User provides local video file path
- `postiz upload /path/to/video.mp4` → returns media ID
- Pass media ID to `posts:create` with appropriate integration ID
- YouTube-specific: title and description passed as post content. Additional metadata (visibility, tags, category, "made for kids") may require Postiz's `--settings` JSON flag — verify during implementation via `postiz integrations:settings $POSTIZ_YOUTUBE_ID`

**For RED (Playwright):**
- Cover image uploaded via Playwright file input interaction
- No Postiz involved for RED media

## Platform-Specific Notes

| Platform | Method | Content Type | Media | Scheduling |
|----------|--------|-------------|-------|------------|
| X | Postiz CLI | Text (280 chars) | Optional images | Yes |
| Threads | Postiz CLI | Text (500 chars, Traditional Chinese) | Optional images | Yes |
| Instagram | Postiz CLI | Carousel or Reel | Required (images or video) | Yes |
| LinkedIn | Postiz CLI | Text (hook in first 210 chars) | Optional images | Yes |
| TikTok | Postiz CLI | Video with caption | Required (video) | Yes |
| YouTube | Postiz CLI | Shorts with title/description | Required (video) | Yes |
| RED | Playwright | Title + body + hashtags (Trad Chinese) | Cover image (3:4) | No (immediate only) |

## File Changes

| File | Change |
|------|--------|
| `~/.claude/skills/cc-post/SKILL.md` | Rewrite to use Postiz CLI + Playwright |
| `~/.env.postiz` | New — Postiz API key + integration IDs |
| `~/.config/cc-post/red-selectors.json` | New — RED web UI selectors (updateable) |
| `~/.red-session/cookies.json` | New — Playwright session cookies for RED |
| `~/postiz/docker-compose.yml` | New — Postiz Docker Compose config |

## What's NOT Changing

- cc-draft skill — no changes needed, it already outputs per-platform content
- Obsidian content pipeline (queue, drafts, posts log) — unchanged
- Content system daily routine — same flow, just faster posting step
- cc-review, cc-brainstorm, cc-capture, cc-recap — unchanged
- The "never auto-post" rule — user confirmation still required

## Out of Scope

- **RED scheduling** — no API, Playwright can only post immediately
- **Postiz MCP integration** — may add later if CLI feels limiting
- **VPS hosting** — local Docker for now, migrate when scheduling needs always-on
- **Analytics/metrics** — Postiz has analytics but not integrating with content pipeline yet
- **Auto-retry on failure** — show error, let user decide

## Risks

1. **Postiz Docker resource usage** — runs PostgreSQL + Redis + Node.js. Monitor memory on Mac.
2. **RED selector breakage** — RED updates their web UI frequently. Selectors may break. Mitigation: config file for selectors, triple fallback (Playwright → Chrome → manual).
3. **Scheduled posts require Mac awake** — if Mac sleeps, Postiz can't fire scheduled posts. Mitigation: schedule posts during waking hours, or set Mac to prevent sleep during posting windows.
4. **Platform OAuth token expiry** — tokens expire. Postiz handles refresh for most platforms, but may need manual re-auth occasionally.
5. **Postiz is open-source, community-maintained** — could have bugs or breaking changes on updates. Pin Docker image version.
