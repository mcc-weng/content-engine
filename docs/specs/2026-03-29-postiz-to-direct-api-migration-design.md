# Postiz to Direct API Migration Design

**Date:** 2026-03-29
**Status:** Draft
**Supersedes:** `2026-03-25-postiz-integration-design.md` (in openclaw repo)

## Problem

The Postiz self-hosted stack (Postiz app + PostgreSQL + Redis + Temporal + Elasticsearch + admin tools + UI) requires 7+ Docker containers just to POST JSON to social media APIs. This overhead is not justified when lightweight Python scripts can hit the same APIs directly.

Three direct-API scripts already exist and work (`post-to-threads.py`, `post-to-instagram.py`, `post-to-x.py`). The migration completes the set and removes Postiz entirely.

## Decision

Replace Postiz with per-platform Python scripts calling APIs directly. The cc-post skill remains the orchestration layer.

## Architecture

```
/cc-post skill (orchestration + user confirmation)
  ├─ Threads  → scripts/post-to-threads.py   → Threads Graph API
  ├─ Instagram → scripts/post-to-instagram.py → Facebook Graph API
  ├─ LinkedIn → scripts/post-to-linkedin.py   → LinkedIn Community Management API
  ├─ TikTok  → scripts/post-to-tiktok.py     → TikTok Content Posting API
  ├─ YouTube → scripts/post-to-youtube.py     → YouTube Data API v3
  ├─ X       → Playwright → Chrome → manual   (API credits depleted)
  └─ RED     → Playwright → Chrome → manual   (no API)
```

## Env File

**Location:** `~/Projects/content/.env` (gitignored)

Credentials extracted from `~/postiz/docker-compose.yaml`:

```bash
# --- Threads ---
THREADS_ACCESS_TOKEN=<from Postiz OAuth — stored in Postiz DB>
THREADS_USER_ID=<numeric user ID>

# --- Instagram ---
INSTAGRAM_BUSINESS_ACCOUNT_ID=<numeric account ID>
INSTAGRAM_ACCESS_TOKEN=<from Postiz OAuth — stored in Postiz DB>

# --- X (API credits depleted — kept for future use) ---
X_API_KEY=S1rGsrEHooiznmaodxfEKuxib
X_API_SECRET=NxhscTd2hXtMXH2eLqncvE4OaVpTNcefVNdCG4DQchmcOxMa7N
X_ACCESS_TOKEN=<from Postiz OAuth — stored in Postiz DB>
X_ACCESS_TOKEN_SECRET=<from Postiz OAuth — stored in Postiz DB>

# --- LinkedIn ---
LINKEDIN_CLIENT_ID=865ixu2mgkqmqc
LINKEDIN_CLIENT_SECRET=WPL_AP1.6DBL83bYQ2T2CxP8.HgdfAg==
LINKEDIN_ACCESS_TOKEN=<from Postiz OAuth — stored in Postiz DB>
LINKEDIN_PERSON_ID=<urn:li:person:xxxxx — get via GET /v2/userinfo with access token>

# --- TikTok ---
TIKTOK_CLIENT_KEY=sbawngpa1dpp3sue1f
TIKTOK_CLIENT_SECRET=P2IP7Q80VQIUfsENTChlqpDpa5XbZidc
TIKTOK_ACCESS_TOKEN=<from Postiz OAuth — stored in Postiz DB>

# --- YouTube ---
YOUTUBE_CLIENT_ID=915530216100-ojf4nc399oe6ih43r1nocfou0gk3f601.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=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
YOUTUBE_REFRESH_TOKEN=<from Postiz OAuth — stored in Postiz DB>
```

**Note:** Some tokens (Threads, Instagram, LinkedIn, X user tokens, TikTok, YouTube refresh token) were obtained via Postiz's OAuth flow and are stored in the Postiz PostgreSQL database. These need to be extracted from the running DB before shutting down Postiz, or re-authenticated via each platform's OAuth flow.

The docker-compose.yaml contains client IDs/secrets (app credentials) which are extractable directly. User-specific OAuth tokens are in the Postiz DB.

## Python Scripts

### Existing (no changes)

| Script | API | Key env vars |
|--------|-----|-------------|
| `post-to-threads.py` | Threads Graph API v1.0 | `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID` |
| `post-to-instagram.py` | Facebook Graph API v21.0 | `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN` |
| `post-to-x.py` | X API v2 + OAuth 1.0a | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` |

### New Scripts

All new scripts follow the same interface pattern:

```bash
python3 scripts/post-to-<platform>.py "post text" [--media /path/to/file] [--title "title"] [--dry-run]
```

All scripts:
- Load credentials from `~/Projects/content/.env` via `python-dotenv` (add `dotenv` loading to existing scripts too for consistency — they currently use bare `os.environ`)
- Print permalink URL on success
- Exit 0 on success, non-zero on failure
- Support `--dry-run` flag (validate inputs, skip actual API call)
- Detect 401 errors and print token refresh instructions

#### `post-to-linkedin.py`

- **API:** LinkedIn Community Management API (`POST https://api.linkedin.com/v2/ugcPosts`)
- **Scopes:** `r_liteprofile`, `w_member_social`
- **Env vars:** `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_ID` (URN like `urn:li:person:xxxxx`)
- **Features:** Text posts, optional article/image sharing via `--media`
- **Token expiry:** ~60 days — script detects 401 and warns about re-auth
- **Returns:** Post URL

#### `post-to-tiktok.py`

- **API:** TikTok Content Posting API v2 (`POST https://open.tiktokapis.com/v2/post/publish/video/init/`)
- **Env vars:** `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN`
- **Features:** Video upload only (errors if no `--media` provided)
- **Flow:** Init upload → upload video → publish
- **Returns:** Video URL

#### `post-to-youtube.py`

- **API:** YouTube Data API v3 (resumable upload)
- **Env vars:** `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`
- **Features:** Video upload with `--title`, `--media` (required), description as positional arg
- **Supports:** Shorts (vertical, <60s) and regular videos
- **Token refresh:** Automatic via refresh token (no manual re-auth needed)
- **Returns:** Video URL

## cc-post Skill Rewrite

### Removed

- All Postiz CLI commands (`postiz posts:create`, `postiz upload`, etc.)
- Docker preflight check (`curl -sf "$POSTIZ_API_URL"`)
- `~/.env.postiz` sourcing
- Postiz-specific error messages (integration IDs, Docker compose commands)

### New Posting Flow

1. **Get post text + platform** (unchanged)
2. **Final confirmation** — show post, "Post this? (y/n)" (unchanged)
3. **Time prompt (new):**
   > Post now, schedule for a specific time, or research best time?

   - **Now** → run script immediately via Bash tool
   - **Schedule** → user provides time → queue via `echo "cd ~/Projects/content && python3 scripts/post-to-<platform>.py '...'" | at <time>`
   - **Research** → show platform-specific guidelines (see below), suggest a time, then schedule

4. **Platform dispatch:**

| Platform | Method |
|----------|--------|
| Threads | `python3 scripts/post-to-threads.py "text"` |
| Instagram | `python3 scripts/post-to-instagram.py --images "urls" "caption"` |
| LinkedIn | `python3 scripts/post-to-linkedin.py "text"` |
| TikTok | `python3 scripts/post-to-tiktok.py --media /path/to/video "text"` |
| YouTube | `python3 scripts/post-to-youtube.py --media /path/to/video --title "title" "description"` |
| X | Playwright → Chrome → manual (unchanged) |
| RED | Playwright → Chrome → manual (unchanged) |

5. **On success/failure** — update tracking files (unchanged)

### Static Best-Time Guidelines

Baked into the skill for the "research best time" option:

| Platform | Best times (AEST) | Notes |
|----------|-------------------|-------|
| RED | 7-9 PM | Chinese audience evening browse |
| Threads | 8-10 AM or 6-8 PM | Engagement peaks |
| Instagram | 8-10 AM or 6-8 PM | Same as Threads |
| X | 8-10 AM or 12-1 PM | Weekday mornings/lunch |
| LinkedIn | Tue-Thu 8-10 AM | Professional morning hours |
| TikTok | 7-9 PM | Evening entertainment window |
| YouTube | Fri-Sat 5-7 PM | Weekend leisure time |

### Scheduling via `at`

For scheduled posts, the skill constructs and queues:

```bash
echo "cd /Users/mikeweng/Projects/content && python3 scripts/post-to-threads.py 'post text'" | at 0830 tomorrow
```

- `at` runs the command once at the specified time
- If Mac is asleep, job runs on wake
- The skill tells the user the job number for cancellation (`atrm <job>`)
- X and RED (browser automation) do not support scheduling — warn user and post immediately

## Cleanup

### Remove
- All Postiz references from cc-post skill
- `~/.env.postiz` (after migration confirmed working)

### Move
- `~/Projects/openclaw/docs/superpowers/specs/2026-03-25-postiz-integration-design.md` → `~/Projects/content/docs/specs/2026-03-25-postiz-integration-design.md` (historical reference, clearly marked as superseded)

### Add
- `.env` entry to `~/Projects/content/.gitignore`

### Defer
- Deletion of `~/postiz/` directory — user confirms manually after confidence in new system

## Token Management

OAuth tokens obtained via Postiz need to be either:
1. **Extracted from Postiz DB** before shutdown (query the PostgreSQL container)
2. **Re-authenticated** via each platform's OAuth flow

Tokens with expiry (~60 days): Threads, Instagram, LinkedIn, TikTok
Tokens that auto-refresh: YouTube (via refresh token)
Tokens from docker-compose (no expiry): X API key/secret, all client IDs/secrets

The scripts detect 401 errors and print platform-specific re-auth instructions.
