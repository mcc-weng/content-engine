# multipost — Open Source Multi-Platform Posting Tool

**Date:** 2026-03-30
**Status:** Design
**Repo:** `~/Projects/multipost/` → `github.com/mikeweng/multipost`

---

## Context

Mike posted on Threads about his multi-platform posting setup. People commented "發文" wanting it. This spec packages his posting scripts + a Claude Code skill into an open-source tool that lets anyone post to 6 platforms from the terminal.

## Target User

Claude Code users (semi-technical). They can use a terminal and follow instructions but may not be comfortable debugging OAuth errors. The skill guides them; the scripts work standalone for more technical users.

---

## Architecture

```
~/Projects/multipost/
├── README.md                    # Bilingual EN/ZH
├── .env.example                 # All platform vars blanked
├── requirements.txt             # requests, python-dotenv
├── LICENSE                      # MIT
├── configure.py                 # Convenience setup wizard
├── scripts/
│   ├── shared.py                # Common: errors, retry, OAuth, env, token refresh
│   ├── post_threads.py          # Threads via Meta Graph API
│   ├── post_x.py                # X via OAuth 1.0a API
│   ├── post_instagram.py        # Instagram carousel via Graph API
│   ├── post_linkedin.py         # LinkedIn via Community Management API
│   ├── post_tiktok.py           # TikTok via Content Posting API v2
│   ├── post_youtube.py          # YouTube via Data API v3
│   └── refresh_tokens.py        # Standalone CLI token refresh
└── skill/
    └── SKILL.md                 # Claude Code skill
```

## Approach: Smart Scripts

Each posting script calls `shared.ensure_setup("platform")` before posting. If tokens are missing and the script is running in an interactive terminal, it walks the user through setup (open browser, guide app creation, paste or OAuth for tokens). If not interactive (called from Claude Code), it returns False and the skill handles the interaction instead.

Scripts work standalone without Claude Code. The skill is a thin orchestration layer that adds Playwright fallback for X and conversational setup guidance.

---

## `shared.py` — Core Module

### Error Handling (extracted from duplicated code in all 6 scripts)

```python
def handle_error(resp, step_name):
    """Handle 401/403/4xx with user-friendly messages. Calls sys.exit(1) on fatal."""

def retry_on_5xx(make_request, step_name):
    """Execute request, retry once on 5xx with 2s backoff."""
```

### Env Management

```python
def load_env():
    """Find and load .env from project root."""

def update_env(key, value):
    """Update .env file + os.environ in-place."""

def check_setup(platform) -> bool:
    """Return True if required tokens exist for platform."""

def check_all() -> dict[str, bool]:
    """Return {"threads": True, "x": False, ...} status dict."""
```

Required env vars per platform:

| Platform | Required Vars |
|----------|--------------|
| Threads | `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID` |
| Instagram | `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN` |
| X | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` |
| LinkedIn | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_ID` |
| TikTok | `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN` |
| YouTube | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` |

### Token Refresh (absorbed from token_refresh.py)

```python
def ensure_fresh_token(platform):
    """Refresh token if possible. Silent no-op if not needed."""
```

Handles: Threads (Meta Graph API exchange), Instagram (same), TikTok (OAuth 2.0 refresh_token flow), LinkedIn (OAuth 2.0 refresh_token if available).

YouTube uses a different pattern: `shared.refresh_youtube_token()` exchanges the refresh_token for a short-lived access_token on every post call. The YouTube script calls this directly, not through `ensure_fresh_token()`.

X tokens never expire (OAuth 1.0a).

### Interactive Setup

```python
def ensure_setup(platform, interactive=True) -> bool:
    """Check if platform is configured. If not and interactive, guide through setup."""
```

Dispatches to platform-specific setup functions:

**Meta platforms (Threads, Instagram) — guide + paste:**
1. Open Meta Developer Portal in browser (`webbrowser.open()`)
2. Print step-by-step instructions for creating app + generating token
3. `input()` to paste access token and user/account ID
4. Validate with test API call (GET /me or equivalent)
5. Save to .env via `update_env()`

**OAuth 2.0 platforms (LinkedIn, TikTok, YouTube) — browser flow:**
1. Print instructions for creating developer app on platform
2. `input()` to paste client_id + client_secret, save to .env
3. Run `oauth_browser_flow()`:
   - Build consent URL with scopes + `redirect_uri=http://localhost:{port}/callback`
   - Open browser via `webbrowser.open()`
   - Start `http.server` on port 8789 (fallback to 8790-8799 if busy)
   - Wait for callback with auth code (timeout 120s)
   - Exchange code for access_token + refresh_token via POST
   - Save tokens to .env
4. Validate with test API call

**X — guide + paste with cost warning:**
1. Print: "X API requires Basic tier ($100/month) for posting."
2. Print: "Alternative: Use the Claude Code skill which posts via browser automation for free."
3. Ask: "Set up X API anyway? (y/n)"
4. If yes: guide through developer.x.com, paste 4 tokens
5. If no: skip, user relies on Playwright via skill

### Token Validation Endpoints

After setup, validate each token with a lightweight test call:

| Platform | Validation Call | Success |
|----------|----------------|---------|
| Threads | `GET graph.threads.net/v1.0/me?fields=id,username` | Returns user ID + username |
| Instagram | `GET graph.facebook.com/v21.0/{account_id}?fields=id,username` | Returns account info |
| X | `GET api.twitter.com/2/users/me` | Returns user ID |
| LinkedIn | `GET api.linkedin.com/v2/userinfo` | Returns sub + name |
| TikTok | `GET open.tiktokapis.com/v2/user/info/` | Returns user info |
| YouTube | `GET www.googleapis.com/youtube/v3/channels?part=id&mine=true` | Returns channel ID |

### OAuth Browser Flow Helper

```python
def oauth_browser_flow(auth_url, token_url, client_id, client_secret,
                        scopes, redirect_port=8789) -> dict:
    """Open browser for OAuth consent, capture callback, exchange for tokens.

    Returns {"access_token": "...", "refresh_token": "...", ...}

    Uses only stdlib: http.server, webbrowser, urllib.parse
    Edge cases: port busy (try 8789-8799), timeout 120s, user cancels.
    """
```

---

## Posting Scripts — Changes from Existing

Each script gets these modifications:

**1. Imports change:**
```python
# Remove: duplicated _handle_error, _retry_on_5xx, token_refresh import
# Add:
from shared import ensure_setup, ensure_fresh_token, handle_error, retry_on_5xx
```

**2. Setup check at top of main function:**
```python
def post_to_threads(text, topic=None, dry_run=False):
    if not ensure_setup("threads", interactive=sys.stdin.isatty()):
        print("Error: Threads not configured. Run: python3 configure.py threads", file=sys.stderr)
        sys.exit(1)
    ensure_fresh_token("threads")
    # ... rest unchanged
```

`sys.stdin.isatty()` determines interactivity — True in terminal, False when called from Claude Code.

**3. `--setup` flag for skill integration:**
```python
if __name__ == "__main__":
    if "--setup" in sys.argv:
        ensure_setup("threads", interactive=True)
        sys.exit(0)
    # ... existing arg parsing
```

**4. Duplicated helpers removed:** Each script loses ~20 lines of duplicated `_handle_error()` and `_retry_on_5xx()`.

**5. YouTube special case:** `_refresh_access_token()` moves to shared.py as `refresh_youtube_token()`. YouTube script calls it directly before each upload (not via `ensure_fresh_token()` — YouTube needs a fresh access_token per request).

**Net per script:** ~5 lines added, ~20 removed. Scripts get shorter and cleaner.

### Script CLI Interface (unchanged)

| Script | Usage |
|--------|-------|
| `post_threads.py` | `[--dry-run] [--setup] [--topic "Topic"] "text"` |
| `post_x.py` | `[--dry-run] [--setup] "text"` |
| `post_instagram.py` | `[--dry-run] [--setup] --images "url1,url2" "caption"` |
| `post_linkedin.py` | `[--dry-run] [--setup] [--media /path/to/img] "text"` |
| `post_tiktok.py` | `[--dry-run] [--setup] --media /path/to/video.mp4 "caption"` |
| `post_youtube.py` | `[--dry-run] [--setup] [--short] --media /path/to/video.mp4 --title "Title" "description"` |

---

## `configure.py` — Setup Wizard

Convenience wrapper at project root. Calls `shared.ensure_setup()` for each platform.

```bash
python3 configure.py              # Setup all platforms interactively
python3 configure.py threads      # Setup one platform
python3 configure.py --status     # Show what's configured
```

**`--status` output:**
```
multipost — platform status

✅ Threads     configured (token valid)
✅ Instagram   configured (token valid)
⏭️  X           skipped (use Playwright via Claude Code skill)
✅ LinkedIn    configured (expires in 52 days)
✅ TikTok      configured (token valid)
✅ YouTube     configured (token valid)
```

**Setup flow:** For each platform, check if configured → if not, ask "Set up [platform]? (y/n/skip)" → if yes, call `ensure_setup()` → validate token → show result.

~60-80 lines. All real logic in shared.py.

---

## `refresh_tokens.py` — Token Refresh CLI

Standalone CLI for refreshing expiring tokens. Calls into `shared.ensure_fresh_token()`.

```bash
python3 scripts/refresh_tokens.py              # Refresh all
python3 scripts/refresh_tokens.py threads      # Refresh one
python3 scripts/refresh_tokens.py --dry-run    # Show what would refresh
```

Handles: Threads, Instagram, TikTok, LinkedIn.
Skips: YouTube (auto-refreshes per request), X (tokens don't expire).

---

## Claude Code Skill (`skill/SKILL.md`)

### Two Modes

**Setup mode** — "set up multipost" or auto-triggered on missing tokens:
1. Run `python3 configure.py --status` to check state
2. For each unconfigured platform, guide user conversationally
3. For Meta platforms: tell user what to do, ask for pasted tokens
4. For OAuth platforms: run `python3 scripts/post_{platform}.py --setup` and relay prompts
5. Show final status summary

**Post mode** — "post [text] to [platform]" or "post everywhere":

| Command | Action |
|---------|--------|
| "post to threads/instagram/linkedin/tiktok/youtube" | Run corresponding script |
| "post to x" | Playwright: navigate x.com/compose/post → type → click Post |
| "post to red" | Manual: present copy-paste block (title + body + hashtags) |
| "post everywhere" | Run each configured platform in sequence |

### Skill Behaviors
- Always confirms before posting
- Suggests dry-run on first post
- Uses relative paths (`./scripts/post_threads.py`)
- No Obsidian integration, no scheduling, no tracking files

### X Playwright Fallback
1. `browser_navigate` to `https://x.com/compose/post`
2. `browser_snapshot` — check for login wall, find compose area
3. `browser_click` compose area
4. `browser_type` the post text
5. `browser_snapshot` — find Post button
6. `browser_click` Post button
7. `browser_wait_for` 3s → `browser_snapshot` to verify

### RED Manual Fallback
Present structured copy-paste block:
```
--- RED POST ---
Title: [title]
[body text]
[hashtags]
--- END ---
Add cover image (3:4 vertical) before posting.
```

---

## Dependencies

```
# requirements.txt
requests
python-dotenv
```

No other dependencies. OAuth flow uses stdlib only (`http.server`, `webbrowser`, `urllib.parse`, `hashlib`, `hmac`).

---

## What's NOT Included (Mike's Private System)

- cc-draft, cc-brainstorm, cc-research, cc-review, cc-recap, cc-adapt, cc-capture skills
- Voice profiles (voice-en.md, voice-zh.md)
- Humanizer references
- Hook types, CTA bank, scoring rubric, post templates
- Obsidian vault integration
- Ideas vault, posts log, drafts tracking
- Scheduling via `at`
- Best-time posting recommendations

---

## Verification Plan

1. Fresh clone → `python3 configure.py --status` → all ❌
2. `python3 configure.py threads` → follow guide → paste token → ✅ validated
3. `python3 scripts/post_threads.py --dry-run "test"` → succeeds
4. `python3 scripts/post_threads.py "test"` with empty .env → auto-triggers interactive setup
5. `python3 scripts/post_threads.py --setup` → runs setup only, exits
6. Install skill → "set up multipost" → detects unconfigured → guides through
7. "post hello to threads" via skill → posts successfully
8. "post to x" via skill → Playwright fallback works
9. `python3 configure.py --status` → shows correct state
10. `python3 scripts/refresh_tokens.py` → refreshes configured platforms
