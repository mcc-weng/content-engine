# Postiz to Direct API Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Postiz Docker stack with per-platform Python scripts calling social media APIs directly, and rewrite the cc-post skill to orchestrate them.

**Architecture:** One Python script per platform (6 total — 3 existing, 3 new) loaded from `~/Projects/content/scripts/`. The cc-post skill handles confirmation, time selection, and dispatch. X and RED use browser automation fallbacks (unchanged). Scheduling uses macOS `at`.

**Tech Stack:** Python 3, `requests`, `python-dotenv`, `google-auth`/`google-auth-oauthlib` (YouTube only), macOS `at` for scheduling.

**Spec:** `docs/specs/2026-03-29-postiz-to-direct-api-migration-design.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|---------------|
| Create | `~/Projects/content/.env` | All platform API credentials |
| Modify | `~/Projects/content/.gitignore` | Add `.env` |
| Modify | `scripts/post-to-threads.py` | Add `python-dotenv` loading |
| Modify | `scripts/post-to-instagram.py` | Add `python-dotenv` loading |
| Modify | `scripts/post-to-x.py` | Add `python-dotenv` loading |
| Create | `scripts/post-to-linkedin.py` | LinkedIn Community Management API |
| Create | `scripts/post-to-tiktok.py` | TikTok Content Posting API v2 |
| Create | `scripts/post-to-youtube.py` | YouTube Data API v3 |
| Rewrite | `~/.claude/skills/cc-post/SKILL.md` | Skill orchestration layer |
| Move | openclaw Postiz spec → `docs/specs/` | Historical reference |

---

### Task 1: Env File & Gitignore Setup

**Files:**
- Create: `~/Projects/content/.env`
- Modify: `~/Projects/content/.gitignore`

- [ ] **Step 1: Add `.env` to `.gitignore`**

Add to the end of `/Users/mikeweng/Projects/content/.gitignore`:

```
# Environment variables
.env
```

- [ ] **Step 2: Create `.env` with app credentials from docker-compose.yaml**

Create `/Users/mikeweng/Projects/content/.env`:

```bash
# --- Threads ---
THREADS_ACCESS_TOKEN=PLACEHOLDER_run_extract_or_reauth
THREADS_USER_ID=PLACEHOLDER_run_extract_or_reauth

# --- Instagram ---
INSTAGRAM_BUSINESS_ACCOUNT_ID=PLACEHOLDER_run_extract_or_reauth
INSTAGRAM_ACCESS_TOKEN=PLACEHOLDER_run_extract_or_reauth

# --- X (API credits depleted — kept for future use) ---
X_API_KEY=S1rGsrEHooiznmaodxfEKuxib
X_API_SECRET=NxhscTd2hXtMXH2eLqncvE4OaVpTNcefVNdCG4DQchmcOxMa7N
X_ACCESS_TOKEN=PLACEHOLDER_run_extract_or_reauth
X_ACCESS_TOKEN_SECRET=PLACEHOLDER_run_extract_or_reauth

# --- LinkedIn ---
LINKEDIN_CLIENT_ID=865ixu2mgkqmqc
LINKEDIN_CLIENT_SECRET=WPL_AP1.6DBL83bYQ2T2CxP8.HgdfAg==
LINKEDIN_ACCESS_TOKEN=PLACEHOLDER_run_extract_or_reauth
LINKEDIN_PERSON_ID=PLACEHOLDER_get_via_userinfo_endpoint

# --- TikTok ---
TIKTOK_CLIENT_KEY=sbawngpa1dpp3sue1f
TIKTOK_CLIENT_SECRET=P2IP7Q80VQIUfsENTChlqpDpa5XbZidc
TIKTOK_ACCESS_TOKEN=PLACEHOLDER_run_extract_or_reauth

# --- YouTube ---
YOUTUBE_CLIENT_ID=915530216100-ojf4nc399oe6ih43r1nocfou0gk3f601.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=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
YOUTUBE_REFRESH_TOKEN=PLACEHOLDER_run_extract_or_reauth
```

- [ ] **Step 3: Extract OAuth tokens from Postiz DB**

The Postiz PostgreSQL container stores user OAuth tokens. Before shutting down Postiz, extract them:

```bash
docker exec postiz-postgres psql -U postiz-user -d postiz-db-local -c "SELECT \"providerId\", \"accessToken\", \"refreshToken\", \"profile\" FROM \"Integration\";"
```

This returns the OAuth tokens for each connected platform. Map the `providerId` values to the corresponding env vars in `.env` and fill in the PLACEHOLDER values.

If the Postiz containers are already stopped, the user will need to re-authenticate via each platform's OAuth flow instead.

- [ ] **Step 4: Install python-dotenv**

```bash
pip3 install python-dotenv
```

- [ ] **Step 5: Verify .env is gitignored**

```bash
cd /Users/mikeweng/Projects/content && git status
```

Expected: `.env` should NOT appear in untracked files.

- [ ] **Step 6: Commit**

```bash
cd /Users/mikeweng/Projects/content
git add .gitignore
git commit -m "chore: add .env to gitignore for API credentials"
```

---

### Task 2: Add dotenv Loading to Existing Scripts

**Files:**
- Modify: `scripts/post-to-threads.py`
- Modify: `scripts/post-to-instagram.py`
- Modify: `scripts/post-to-x.py`

- [ ] **Step 1: Add dotenv import to `post-to-threads.py`**

At the top of `/Users/mikeweng/Projects/content/scripts/post-to-threads.py`, after the existing imports (line 17), add:

```python
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
```

- [ ] **Step 2: Add dotenv import to `post-to-instagram.py`**

At the top of `/Users/mikeweng/Projects/content/scripts/post-to-instagram.py`, after the existing imports (line 17), add:

```python
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
```

- [ ] **Step 3: Add dotenv import to `post-to-x.py`**

At the top of `/Users/mikeweng/Projects/content/scripts/post-to-x.py`, after the existing imports (line 27), add:

```python
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
```

- [ ] **Step 4: Verify dotenv loading works**

```bash
cd /Users/mikeweng/Projects/content
python3 -c "from pathlib import Path; from dotenv import load_dotenv; load_dotenv(Path('scripts/post-to-threads.py').resolve().parent.parent / '.env'); import os; print('THREADS_ACCESS_TOKEN' in os.environ)"
```

Expected: `True` (even if the value is the placeholder)

- [ ] **Step 5: Test dry-run with dotenv**

```bash
cd /Users/mikeweng/Projects/content
python3 scripts/post-to-threads.py --dry-run "Test dotenv loading"
```

Expected: `[DRY RUN] Would post to Threads` (or an error about placeholder token — either confirms dotenv is loading)

- [ ] **Step 6: Commit**

```bash
cd /Users/mikeweng/Projects/content
git add scripts/post-to-threads.py scripts/post-to-instagram.py scripts/post-to-x.py
git commit -m "chore: add python-dotenv loading to existing posting scripts"
```

---

### Task 3: Build `post-to-linkedin.py`

**Files:**
- Create: `scripts/post-to-linkedin.py`

- [ ] **Step 1: Write the script**

Create `/Users/mikeweng/Projects/content/scripts/post-to-linkedin.py`:

```python
#!/usr/bin/env python3
"""Post text content to LinkedIn via Community Management API.

Usage:
  python3 post-to-linkedin.py "Post text here"
  python3 post-to-linkedin.py --media /path/to/image.jpg "Post text here"
  python3 post-to-linkedin.py --dry-run "Post text here"

Requires env vars:
  LINKEDIN_ACCESS_TOKEN — OAuth 2.0 token (~60 day expiry)
  LINKEDIN_PERSON_ID    — URN like urn:li:person:xxxxx
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_BASE = "https://api.linkedin.com/v2"


def _handle_error(resp, step_name):
    """Handle 4xx/5xx errors with user-friendly messages."""
    if resp.status_code == 401:
        print("Error: 401 Unauthorized — LinkedIn token expired.", file=sys.stderr)
        print("Re-authenticate via LinkedIn OAuth flow and update LINKEDIN_ACCESS_TOKEN in .env.", file=sys.stderr)
        print("Token expires every ~60 days.", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 403:
        print("Error: 403 Forbidden — check LinkedIn app scopes (need w_member_social).", file=sys.stderr)
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


def _upload_image(image_path, token, person_id):
    """Upload an image to LinkedIn. Returns the image URN."""
    # Step 1: Register upload
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_id,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    register_resp = _retry_on_5xx(
        lambda: requests.post(
            f"{API_BASE}/assets?action=registerUpload",
            headers=headers,
            json=register_payload,
        ),
        "register image upload",
    )
    register_data = register_resp.json()
    upload_url = register_data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset = register_data["value"]["asset"]

    # Step 2: Upload binary
    with open(image_path, "rb") as f:
        image_data = f.read()
    upload_resp = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
        data=image_data,
    )
    if upload_resp.status_code not in (200, 201):
        print(f"Error uploading image: {upload_resp.status_code}", file=sys.stderr)
        print(upload_resp.text, file=sys.stderr)
        sys.exit(1)

    return asset


def post_to_linkedin(text, media_path=None, dry_run=False):
    """Publish a post to LinkedIn. Returns the post URL."""
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    person_id = os.environ.get("LINKEDIN_PERSON_ID")

    if not token:
        print("Error: LINKEDIN_ACCESS_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)
    if not person_id:
        print("Error: LINKEDIN_PERSON_ID env var not set", file=sys.stderr)
        print("Get it via: curl -H 'Authorization: Bearer $TOKEN' https://api.linkedin.com/v2/userinfo", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        print(f"[DRY RUN] Would post to LinkedIn ({len(text)} chars):", file=sys.stderr)
        print(text, file=sys.stderr)
        if media_path:
            print(f"  With image: {media_path}", file=sys.stderr)
        return "https://linkedin.com/feed/dry-run"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Build payload
    payload = {
        "author": person_id,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    # If image provided, upload and attach
    if media_path:
        print(f"Uploading image: {media_path}...", file=sys.stderr)
        asset_urn = _upload_image(media_path, token, person_id)
        share_content = payload["specificContent"]["com.linkedin.ugc.ShareContent"]
        share_content["shareMediaCategory"] = "IMAGE"
        share_content["media"] = [
            {
                "status": "READY",
                "media": asset_urn,
            }
        ]

    resp = _retry_on_5xx(
        lambda: requests.post(
            f"{API_BASE}/ugcPosts", headers=headers, json=payload
        ),
        "create post",
    )

    # LinkedIn returns the post URN in the id header
    post_urn = resp.headers.get("X-RestLi-Id", resp.json().get("id", ""))
    # Convert URN to URL: urn:li:share:12345 → linkedin.com/feed/update/urn:li:share:12345
    if post_urn:
        return f"https://www.linkedin.com/feed/update/{post_urn}"
    return "Post published but could not get URL."


if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = False
    media_path = None

    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    if "--media" in args:
        idx = args.index("--media")
        if idx + 1 >= len(args):
            print("Error: --media requires a file path", file=sys.stderr)
            sys.exit(1)
        media_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if not args:
        print('Usage: python3 post-to-linkedin.py [--dry-run] [--media /path/to/image] "Post text"', file=sys.stderr)
        sys.exit(1)

    url = post_to_linkedin(args[0], media_path=media_path, dry_run=dry_run)
    print(url)
```

- [ ] **Step 2: Test dry-run**

```bash
cd /Users/mikeweng/Projects/content
python3 scripts/post-to-linkedin.py --dry-run "Test LinkedIn posting"
```

Expected: `[DRY RUN] Would post to LinkedIn (23 chars):`

- [ ] **Step 3: Test dry-run with media flag**

```bash
cd /Users/mikeweng/Projects/content
python3 scripts/post-to-linkedin.py --dry-run --media /tmp/test.jpg "Test with image"
```

Expected: `[DRY RUN] Would post to LinkedIn` with image path shown.

- [ ] **Step 4: Commit**

```bash
cd /Users/mikeweng/Projects/content
git add scripts/post-to-linkedin.py
git commit -m "feat: add LinkedIn posting script via Community Management API"
```

---

### Task 4: Build `post-to-tiktok.py`

**Files:**
- Create: `scripts/post-to-tiktok.py`

- [ ] **Step 1: Write the script**

Create `/Users/mikeweng/Projects/content/scripts/post-to-tiktok.py`:

```python
#!/usr/bin/env python3
"""Post video content to TikTok via Content Posting API v2.

Usage:
  python3 post-to-tiktok.py --media /path/to/video.mp4 "Caption text"
  python3 post-to-tiktok.py --dry-run --media /path/to/video.mp4 "Caption text"

Requires env vars:
  TIKTOK_ACCESS_TOKEN — OAuth 2.0 token
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_BASE = "https://open.tiktokapis.com/v2"
POLL_INTERVAL_SECS = 5
POLL_TIMEOUT_SECS = 120


def _handle_error(resp, step_name):
    """Handle 4xx/5xx errors with user-friendly messages."""
    if resp.status_code == 401:
        print("Error: 401 Unauthorized — TikTok token expired.", file=sys.stderr)
        print("Re-authenticate via TikTok OAuth flow and update TIKTOK_ACCESS_TOKEN in .env.", file=sys.stderr)
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


def post_to_tiktok(text, video_path, dry_run=False):
    """Upload and publish a video to TikTok. Returns publish ID."""
    token = os.environ.get("TIKTOK_ACCESS_TOKEN")

    if not token:
        print("Error: TIKTOK_ACCESS_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)

    video_file = Path(video_path)
    if not video_file.exists():
        print(f"Error: video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    video_size = video_file.stat().st_size

    if dry_run:
        print(f"[DRY RUN] Would post to TikTok:", file=sys.stderr)
        print(f"  Video: {video_path} ({video_size} bytes)", file=sys.stderr)
        print(f"  Caption ({len(text)} chars): {text}", file=sys.stderr)
        return "https://tiktok.com/dry-run"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Step 1: Initialize upload via direct post
    init_payload = {
        "post_info": {
            "title": text,
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": video_size,
            "total_chunk_count": 1,
        },
    }

    print("Initializing TikTok upload...", file=sys.stderr)
    init_resp = _retry_on_5xx(
        lambda: requests.post(
            f"{API_BASE}/post/publish/video/init/",
            headers=headers,
            json=init_payload,
        ),
        "init upload",
    )
    init_data = init_resp.json()

    if init_data.get("error", {}).get("code") != "ok":
        print(f"Error initializing upload: {json.dumps(init_data, indent=2)}", file=sys.stderr)
        sys.exit(1)

    upload_url = init_data["data"]["upload_url"]
    publish_id = init_data["data"]["publish_id"]

    # Step 2: Upload video binary
    print(f"Uploading video ({video_size} bytes)...", file=sys.stderr)
    with open(video_path, "rb") as f:
        video_data = f.read()

    upload_resp = requests.put(
        upload_url,
        headers={
            "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
            "Content-Type": "video/mp4",
        },
        data=video_data,
    )
    if upload_resp.status_code not in (200, 201):
        print(f"Error uploading video: {upload_resp.status_code}", file=sys.stderr)
        print(upload_resp.text, file=sys.stderr)
        sys.exit(1)

    # Step 3: Poll for publish status
    print("Waiting for TikTok to process video...", file=sys.stderr)
    elapsed = 0
    while elapsed < POLL_TIMEOUT_SECS:
        status_resp = requests.post(
            f"{API_BASE}/post/publish/status/fetch/",
            headers=headers,
            json={"publish_id": publish_id},
        )
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            pub_status = status_data.get("data", {}).get("status")
            if pub_status == "PUBLISH_COMPLETE":
                print("Published!", file=sys.stderr)
                return f"TikTok publish ID: {publish_id} (check your profile for the video)"
            if pub_status in ("FAILED", "PUBLISH_FAILED"):
                fail_reason = status_data.get("data", {}).get("fail_reason", "unknown")
                print(f"Error: TikTok publish failed — {fail_reason}", file=sys.stderr)
                sys.exit(1)
        time.sleep(POLL_INTERVAL_SECS)
        elapsed += POLL_INTERVAL_SECS

    print(f"Error: publish status polling timed out after {POLL_TIMEOUT_SECS}s", file=sys.stderr)
    print(f"Publish ID: {publish_id} — check TikTok Creator Portal for status.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = False
    media_path = None

    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    if "--media" in args:
        idx = args.index("--media")
        if idx + 1 >= len(args):
            print("Error: --media requires a file path", file=sys.stderr)
            sys.exit(1)
        media_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if not media_path:
        print("Error: TikTok requires a video. Use --media /path/to/video.mp4", file=sys.stderr)
        sys.exit(1)

    if not args:
        print('Usage: python3 post-to-tiktok.py [--dry-run] --media /path/to/video.mp4 "Caption text"', file=sys.stderr)
        sys.exit(1)

    url = post_to_tiktok(args[0], media_path, dry_run=dry_run)
    print(url)
```

- [ ] **Step 2: Test dry-run**

```bash
cd /Users/mikeweng/Projects/content
touch /tmp/test-video.mp4
python3 scripts/post-to-tiktok.py --dry-run --media /tmp/test-video.mp4 "Test TikTok post"
```

Expected: `[DRY RUN] Would post to TikTok:` with video path and caption.

- [ ] **Step 3: Test missing media error**

```bash
cd /Users/mikeweng/Projects/content
python3 scripts/post-to-tiktok.py --dry-run "No video provided"
```

Expected: `Error: TikTok requires a video. Use --media /path/to/video.mp4`

- [ ] **Step 4: Commit**

```bash
cd /Users/mikeweng/Projects/content
git add scripts/post-to-tiktok.py
git commit -m "feat: add TikTok posting script via Content Posting API v2"
```

---

### Task 5: Build `post-to-youtube.py`

**Files:**
- Create: `scripts/post-to-youtube.py`

- [ ] **Step 1: Install google-auth libraries**

```bash
pip3 install google-auth google-auth-oauthlib google-api-python-client
```

- [ ] **Step 2: Write the script**

Create `/Users/mikeweng/Projects/content/scripts/post-to-youtube.py`:

```python
#!/usr/bin/env python3
"""Upload video to YouTube via Data API v3.

Usage:
  python3 post-to-youtube.py --media /path/to/video.mp4 --title "Video Title" "Description text"
  python3 post-to-youtube.py --dry-run --media /path/to/video.mp4 --title "Title" "Description"
  python3 post-to-youtube.py --media /path/to/short.mp4 --title "Short Title" --short "Description"

Requires env vars:
  YOUTUBE_CLIENT_ID     — OAuth 2.0 client ID
  YOUTUBE_CLIENT_SECRET — OAuth 2.0 client secret
  YOUTUBE_REFRESH_TOKEN — OAuth 2.0 refresh token
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
YOUTUBE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _refresh_access_token():
    """Exchange refresh token for a fresh access token."""
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    resp = requests.post(
        YOUTUBE_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    if resp.status_code != 200:
        print(f"Error refreshing YouTube token: {resp.status_code}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        print("Re-authenticate via Google OAuth and update YOUTUBE_REFRESH_TOKEN in .env.", file=sys.stderr)
        sys.exit(1)
    return resp.json()["access_token"]


def _handle_error(resp, step_name):
    """Handle 4xx/5xx errors with user-friendly messages."""
    if resp.status_code == 401:
        print("Error: 401 Unauthorized — YouTube token refresh failed.", file=sys.stderr)
        print("Re-authenticate via Google OAuth and update YOUTUBE_REFRESH_TOKEN in .env.", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 403:
        print("Error: 403 Forbidden — check YouTube Data API quota or channel permissions.", file=sys.stderr)
        try:
            print(json.dumps(resp.json(), indent=2), file=sys.stderr)
        except Exception:
            print(resp.text, file=sys.stderr)
        sys.exit(1)
    if 400 <= resp.status_code < 500:
        try:
            detail = json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            detail = resp.text
        print(f"Error in {step_name}: {resp.status_code}", file=sys.stderr)
        print(detail, file=sys.stderr)
        sys.exit(1)


def post_to_youtube(description, video_path, title, is_short=False, dry_run=False):
    """Upload a video to YouTube. Returns the video URL."""
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    missing = []
    if not client_id:
        missing.append("YOUTUBE_CLIENT_ID")
    if not client_secret:
        missing.append("YOUTUBE_CLIENT_SECRET")
    if not refresh_token:
        missing.append("YOUTUBE_REFRESH_TOKEN")
    if missing:
        print(f"Error: Missing env vars: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    video_file = Path(video_path)
    if not video_file.exists():
        print(f"Error: video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    video_size = video_file.stat().st_size

    if dry_run:
        vid_type = "Short" if is_short else "Video"
        print(f"[DRY RUN] Would upload YouTube {vid_type}:", file=sys.stderr)
        print(f"  Title: {title}", file=sys.stderr)
        print(f"  Video: {video_path} ({video_size} bytes)", file=sys.stderr)
        print(f"  Description ({len(description)} chars): {description}", file=sys.stderr)
        return "https://youtube.com/dry-run"

    # Get fresh access token
    print("Refreshing YouTube access token...", file=sys.stderr)
    access_token = _refresh_access_token()

    # For Shorts, prepend #Shorts to title if not present
    if is_short and "#Shorts" not in title:
        title = f"{title} #Shorts"

    # Metadata
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    # Resumable upload: Step 1 — initiate
    print("Initiating YouTube upload...", file=sys.stderr)
    init_resp = requests.post(
        f"{YOUTUBE_UPLOAD_URL}?uploadType=resumable&part=snippet,status",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Upload-Content-Length": str(video_size),
            "X-Upload-Content-Type": "video/mp4",
        },
        json=metadata,
    )
    _handle_error(init_resp, "initiate upload")

    upload_url = init_resp.headers.get("Location")
    if not upload_url:
        print("Error: YouTube did not return an upload URL.", file=sys.stderr)
        sys.exit(1)

    # Resumable upload: Step 2 — upload video
    print(f"Uploading video ({video_size} bytes)...", file=sys.stderr)
    with open(video_path, "rb") as f:
        upload_resp = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "video/mp4",
                "Content-Length": str(video_size),
            },
            data=f,
        )
    _handle_error(upload_resp, "upload video")

    video_data = upload_resp.json()
    video_id = video_data.get("id")
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"

    return f"Video uploaded but could not get ID. Response: {json.dumps(video_data)}"


if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = False
    media_path = None
    title = None
    is_short = False

    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    if "--short" in args:
        is_short = True
        args.remove("--short")

    if "--media" in args:
        idx = args.index("--media")
        if idx + 1 >= len(args):
            print("Error: --media requires a file path", file=sys.stderr)
            sys.exit(1)
        media_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if "--title" in args:
        idx = args.index("--title")
        if idx + 1 >= len(args):
            print("Error: --title requires a value", file=sys.stderr)
            sys.exit(1)
        title = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if not media_path:
        print("Error: YouTube requires a video. Use --media /path/to/video.mp4", file=sys.stderr)
        sys.exit(1)

    if not title:
        print("Error: YouTube requires a title. Use --title \"Video Title\"", file=sys.stderr)
        sys.exit(1)

    if not args:
        print('Usage: python3 post-to-youtube.py [--dry-run] [--short] --media /path/to/video.mp4 --title "Title" "Description"', file=sys.stderr)
        sys.exit(1)

    url = post_to_youtube(args[0], media_path, title, is_short=is_short, dry_run=dry_run)
    print(url)
```

- [ ] **Step 3: Test dry-run**

```bash
cd /Users/mikeweng/Projects/content
touch /tmp/test-video.mp4
python3 scripts/post-to-youtube.py --dry-run --media /tmp/test-video.mp4 --title "Test Video" "Test description"
```

Expected: `[DRY RUN] Would upload YouTube Video:` with title, path, description.

- [ ] **Step 4: Test dry-run as Short**

```bash
python3 scripts/post-to-youtube.py --dry-run --short --media /tmp/test-video.mp4 --title "Short Title" "Short description"
```

Expected: `[DRY RUN] Would upload YouTube Short:`

- [ ] **Step 5: Test missing flags**

```bash
python3 scripts/post-to-youtube.py --dry-run "No video or title"
```

Expected: `Error: YouTube requires a video.`

- [ ] **Step 6: Commit**

```bash
cd /Users/mikeweng/Projects/content
git add scripts/post-to-youtube.py
git commit -m "feat: add YouTube posting script via Data API v3 with resumable upload"
```

---

### Task 6: Rewrite cc-post Skill

**Files:**
- Rewrite: `~/.claude/skills/cc-post/SKILL.md`

- [ ] **Step 1: Rewrite the skill**

Replace the entire contents of `/Users/mikeweng/.claude/skills/cc-post/SKILL.md` with:

```markdown
---
name: cc-post
description: Publish approved content to any platform (RED, Instagram, Threads, X, LinkedIn, TikTok, YouTube). Use when user says "/cc-post", "publish to threads", "post to X", "post to instagram", "post this", or approves a draft for posting. Also triggers on "publish this" or "send it". Does NOT trigger on general publishing or deploy tasks.
---

# Post to Platform

Publish approved content to the target platform and update tracking files. Uses Python scripts for API platforms and Playwright/Chrome/manual fallback for X and RED.

## Paths

- Scripts dir: `~/Projects/content/scripts/`
- Env file: `~/Projects/content/.env`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/ideas.md`
- Posts log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/posts.md`

## Steps

1. **Get the post text and platform:**
   - If provided directly → use it
   - If user says "post the last draft" → use the most recent draft from this conversation
   - Platform should be clear from the draft context
   - If platform is ambiguous → ask: "Which platform? (x / threads / instagram / tiktok / youtube / linkedin / red)"
   - If posting to multiple platforms → handle each separately (content may differ per platform)

2. **Final confirmation:** Show the full post text and ask:

   Ready to post to **[Platform]**?

   ---
   [post text]
   ---

   Post this? (y/n)

3. **Wait for explicit "y" or "yes"** before proceeding. Never auto-post.

4. **Time selection:**

   > **Post now, schedule for a specific time, or research best time?**

   - **Now** → proceed to step 5 immediately
   - **Schedule** → user provides a time → construct the `at` command (see Scheduling section) → tell user the job number → done
   - **Research best time** → show the guidelines below, suggest a specific time based on platform, then ask user to confirm → schedule via `at`

   **Best-Time Guidelines (AEST):**

   | Platform | Best times | Notes |
   |----------|-----------|-------|
   | RED | 7-9 PM | Chinese audience evening browse |
   | Threads | 8-10 AM or 6-8 PM | Engagement peaks |
   | Instagram | 8-10 AM or 6-8 PM | Same as Threads |
   | X | 8-10 AM or 12-1 PM | Weekday mornings/lunch |
   | LinkedIn | Tue-Thu 8-10 AM | Professional morning hours |
   | TikTok | 7-9 PM | Evening entertainment window |
   | YouTube | Fri-Sat 5-7 PM | Weekend leisure time |

5. **Publish per platform:**

   ### Threads (Python script)

   ```bash
   cd ~/Projects/content && python3 scripts/post-to-threads.py "[post text]"
   ```

   ### Instagram (Python script)

   Requires image media. If user hasn't provided image URLs, ask:
   "Instagram requires images (at least 2 for carousel). Paste the URLs (comma-separated):"

   ```bash
   cd ~/Projects/content && python3 scripts/post-to-instagram.py --images "[url1,url2]" "[caption text]"
   ```

   ### LinkedIn (Python script)

   ```bash
   cd ~/Projects/content && python3 scripts/post-to-linkedin.py "[post text]"
   ```

   With image:
   ```bash
   cd ~/Projects/content && python3 scripts/post-to-linkedin.py --media "/path/to/image.jpg" "[post text]"
   ```

   ### TikTok (Python script)

   Requires video media. If user hasn't provided a video, ask:
   "TikTok requires a video. Paste the file path:"

   ```bash
   cd ~/Projects/content && python3 scripts/post-to-tiktok.py --media "/path/to/video.mp4" "[caption text]"
   ```

   ### YouTube (Python script)

   Requires video media and a title. If user hasn't provided these, ask.

   ```bash
   cd ~/Projects/content && python3 scripts/post-to-youtube.py --media "/path/to/video.mp4" --title "[title]" "[description]"
   ```

   For Shorts:
   ```bash
   cd ~/Projects/content && python3 scripts/post-to-youtube.py --short --media "/path/to/video.mp4" --title "[title]" "[description]"
   ```

   ### X (Playwright browser automation — triple fallback)

   X API credits are depleted. Use browser automation instead.

   **Fallback 1: Playwright MCP**

   **Single tweet:**
   1. `browser_navigate` to `https://x.com/compose/post`
   2. `browser_snapshot` — check if login page appears
      - If login page: tell user "X needs you to log in. Please log in in the Playwright browser window, then tell me when you're done." Wait for user confirmation, then `browser_snapshot` again.
   3. `browser_snapshot` — find the compose text area
   4. `browser_click` on the text input area (ref from snapshot)
   5. `browser_type` the tweet text into the compose box
   6. `browser_snapshot` — find the "Post" button
   7. `browser_click` the "Post" button
   8. `browser_wait_for` — wait 3 seconds for post to complete
   9. `browser_snapshot` — verify post was submitted (compose should close or show success)

   **Thread (multiple tweets):**
   1. `browser_navigate` to `https://x.com/compose/post`
   2. `browser_click` the compose text area
   3. `browser_type` tweet 1 text
   4. `browser_snapshot` — find the "+" button to add another tweet to the thread
   5. `browser_click` the "+" button
   6. `browser_type` tweet 2 text in the new compose box
   7. Repeat steps 4-6 for all remaining tweets
   8. `browser_click` "Post all" button to publish the entire thread at once

   If any Playwright step fails or times out → move to Fallback 2.

   **Fallback 2: Chrome MCP**

   Same flow using `mcp__claude-in-chrome__*` tools:
   1. `tabs_context_mcp` to get tab context
   2. `tabs_create_mcp` to create a new tab
   3. `navigate` to `https://x.com/compose/post`
   4. `read_page` to inspect the compose form
   5. `form_input` or `computer` to type the tweet
   6. `computer` to click Post

   If Chrome MCP fails → move to Fallback 3.

   **Fallback 3: Manual copy-paste**

   Present each tweet as a numbered copy-paste block:
   ```
   --- X THREAD ---

   Tweet 1:
   [tweet 1 text]

   Tweet 2 (reply to tweet 1):
   [tweet 2 text]

   ...

   --- END ---

   Post tweet 1 first, then reply to it with tweet 2, and so on.
   ```

   Then say: "Automated posting to X failed. Copy-paste blocks ready above. Tell me when you've posted and I'll update the tracking files."

   ### RED (Triple fallback — no API)

   RED has no public API. Try methods in this order:

   **Fallback 1: Playwright MCP**

   If `~/.config/cc-post/red-selectors.json` exists, read it for selectors. Otherwise use defaults:
   - Navigate to `https://creator.xiaohongshu.com/publish/publish`
   - Look for the title input, body textarea, and publish button
   - Fill in title and body, upload cover image if provided, then click publish

   Use `mcp__plugin_playwright_playwright__browser_navigate`, `browser_snapshot`, `browser_fill_form`, `browser_click` etc. If any Playwright step fails or times out, move to Fallback 2.

   **Fallback 2: Chrome MCP**

   Use `mcp__claude-in-chrome__navigate` to open the RED creator page, then `mcp__claude-in-chrome__read_page` to inspect the DOM, and `mcp__claude-in-chrome__form_input` / `mcp__claude-in-chrome__computer` to fill and submit. If this fails, move to Fallback 3.

   **Fallback 3: Manual copy-paste**

   Present structured copy-paste block:
   ```
   --- RED POST ---

   Title: [title text — first 18 chars contain 2 core keywords]

   [body text]

   [hashtags]

   --- END ---

   Remember: Add cover image (3:4 vertical, bold text overlay) before posting.
   ```

   Then say: "Automated posting to RED failed. Copy-paste block ready above. Tell me when you've posted and I'll update the tracking files."

## Scheduling via `at`

For scheduled posts, construct and run:

```bash
echo "cd /Users/mikeweng/Projects/content && python3 scripts/post-to-<platform>.py '[post text]'" | at <time>
```

Examples:
- `at 0830 tomorrow` — 8:30 AM tomorrow
- `at 7:00 PM` — 7 PM today
- `at 2:00 PM Mar 30` — specific date/time

After scheduling:
- Tell the user the `at` job number (from the output)
- Tell them they can cancel with `atrm <job_number>` or list pending jobs with `atq`

**Scheduling limitations:**
- X and RED use browser automation — cannot be scheduled. Warn user: "X/RED posting uses browser automation which can't schedule ahead. I'll post it now instead."
- If Mac sleeps through the scheduled time, the job runs on wake

## On Success

- Read ideas vault — if this post came from a queued idea, update its status to `posted` with today's date and platform
- Append to posts log:
  ```
  - **[YYYY-MM-DD]** [platform] [first 30 chars of post text]...
    - Text: [full post text]
    - Platform: [x | threads | instagram | tiktok | youtube | linkedin | red]
    - Link: [permalink URL or "manual post"]
  ```
- For automated platforms: "Posted to [Platform]! [permalink URL]"
- For manual platforms (RED/X fallback): "Copy-paste block ready above. Tell me when you've posted and I'll update the tracking files."

## On Failure

- If 401 / auth error: "Token expired. Update the token in `~/Projects/content/.env` for [platform]."
- If 403: "Permission denied — check API scopes/tier for [platform]."
- If 4xx: Show the error message and suggest a fix
- If 5xx: "[Platform] server error. Try again in a minute."
- Do NOT retry automatically — show the error and let user decide

## On Partial Failure (multi-platform)

- Log and report successes immediately
- Report each failure with its error
- Ask: "Retry failed platforms? (y/n)"
- Only retry the specific platforms that failed

## Rules

- NEVER post without explicit user confirmation
- NEVER modify the post text — post exactly what was approved
- Each platform gets its own separate script call — never batch
- If a script fails, do NOT retry automatically — show the error and let user decide
- For manual platforms (RED/X fallback): present the copy-paste block and wait for user to confirm they've posted
- Instagram requires image media (at least 2) — ask before posting
- TikTok requires video media — ask before posting
- YouTube requires video media and a title — ask before posting
```

- [ ] **Step 2: Verify skill loads correctly**

Read back the first 10 lines to confirm frontmatter is valid:

```bash
head -10 ~/.claude/skills/cc-post/SKILL.md
```

Expected: Valid YAML frontmatter with `name: cc-post` and the updated description.

- [ ] **Step 3: Commit**

```bash
cd /Users/mikeweng/Projects/content
git -C ~/.claude add skills/cc-post/SKILL.md
git -C ~/.claude commit -m "feat: rewrite cc-post skill to use direct API scripts instead of Postiz"
```

Note: The skill lives in `~/.claude/skills/`, not in the content project repo. Commit it in the `~/.claude` repo if it's tracked there, or just save it — skills don't need to be committed to a repo.

---

### Task 7: Cleanup — Move Spec, Remove Postiz References

**Files:**
- Move: `~/Projects/openclaw/docs/superpowers/specs/2026-03-25-postiz-integration-design.md`
- Delete: `~/.env.postiz`

- [ ] **Step 1: Copy the Postiz spec to this project**

```bash
cp ~/Projects/openclaw/docs/superpowers/specs/2026-03-25-postiz-integration-design.md \
   ~/Projects/content/docs/specs/2026-03-25-postiz-integration-design-SUPERSEDED.md
```

- [ ] **Step 2: Add superseded notice to the moved spec**

Prepend to the top of `~/Projects/content/docs/specs/2026-03-25-postiz-integration-design-SUPERSEDED.md`:

```markdown
> **SUPERSEDED** by `2026-03-29-postiz-to-direct-api-migration-design.md` — Postiz was removed in favor of direct API scripts.

```

- [ ] **Step 3: Delete `~/.env.postiz`**

```bash
rm ~/.env.postiz
```

- [ ] **Step 4: Verify no Postiz references remain in active files**

```bash
grep -r "postiz\|Postiz\|POSTIZ" ~/.claude/skills/cc-post/ ~/Projects/content/scripts/
```

Expected: No matches (or only in the SUPERSEDED spec file).

- [ ] **Step 5: Commit**

```bash
cd /Users/mikeweng/Projects/content
git add docs/specs/2026-03-25-postiz-integration-design-SUPERSEDED.md
git commit -m "chore: move Postiz spec to content project, mark as superseded"
```

---

### Task 8: End-to-End Verification

- [ ] **Step 1: Verify all scripts have consistent interface**

```bash
cd /Users/mikeweng/Projects/content
python3 scripts/post-to-threads.py --dry-run "Test" 2>&1
python3 scripts/post-to-instagram.py --dry-run --images "http://example.com/1.jpg,http://example.com/2.jpg" "Test" 2>&1
python3 scripts/post-to-x.py --dry-run "Test" 2>&1
python3 scripts/post-to-linkedin.py --dry-run "Test" 2>&1
touch /tmp/test-video.mp4
python3 scripts/post-to-tiktok.py --dry-run --media /tmp/test-video.mp4 "Test" 2>&1
python3 scripts/post-to-youtube.py --dry-run --media /tmp/test-video.mp4 --title "Test" "Test" 2>&1
```

Expected: All 6 scripts print `[DRY RUN]` output and exit 0.

- [ ] **Step 2: Verify `at` is available**

```bash
echo "echo test" | at now + 1 minute 2>&1
atq
```

Expected: Job queued successfully. If `at` is not enabled, run `sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist`.

- [ ] **Step 3: Verify `.env` is gitignored**

```bash
cd /Users/mikeweng/Projects/content
git status --porcelain | grep "\.env$"
```

Expected: No output (`.env` is not tracked).

- [ ] **Step 4: Test one real post (Threads dry-run with real token)**

If real tokens have been extracted into `.env`:

```bash
cd /Users/mikeweng/Projects/content
python3 scripts/post-to-threads.py --dry-run "Migration test — if you see this as a real post, something went wrong"
```

Expected: `[DRY RUN]` output with no actual API call.

- [ ] **Step 5: Remind user about deferred cleanup**

Print to user:
> Migration complete. When you're confident everything works, you can delete the Postiz stack:
> ```bash
> docker compose -f ~/postiz/docker-compose.yml down -v
> rm -rf ~/postiz/
> ```
