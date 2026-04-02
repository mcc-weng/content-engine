# multipost Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package Mike's multi-platform posting scripts into an open-source tool with interactive OAuth setup, a Claude Code skill, and bilingual docs.

**Architecture:** Shared module (`shared.py`) provides error handling, env management, token refresh, and OAuth flows. 6 posting scripts import from it — each detects missing tokens and triggers interactive setup. A Claude Code skill wraps everything with conversational guidance and Playwright fallback for X.

**Tech Stack:** Python 3.10+, requests, python-dotenv, stdlib (http.server, webbrowser for OAuth)

**Source scripts:** `~/Projects/content/scripts/post-to-{threads,x,instagram,linkedin,tiktok,youtube}.py` + `token_refresh.py` + `refresh-tokens.py`

**Spec:** `~/Projects/content/docs/specs/2026-03-30-multipost-design.md`

---

## File Map

| File | Status | Responsibility |
|------|--------|---------------|
| `scripts/shared.py` | **NEW** | Error handling, retry, env management, token refresh, OAuth browser flow, interactive setup per platform |
| `scripts/post_threads.py` | Copy + modify | Threads posting. Add: import shared, ensure_setup, remove duplicated helpers |
| `scripts/post_x.py` | Copy + modify | X posting. Same changes. Keep OAuth 1.0a signature logic (unique to X) |
| `scripts/post_instagram.py` | Copy + modify | Instagram carousel posting. Same changes |
| `scripts/post_linkedin.py` | Copy + modify | LinkedIn posting. Same changes |
| `scripts/post_tiktok.py` | Copy + modify | TikTok video posting. Same changes |
| `scripts/post_youtube.py` | Copy + modify | YouTube video posting. Same changes. Move `_refresh_access_token` to shared |
| `scripts/refresh_tokens.py` | Copy + modify | CLI token refresh. Use shared.py instead of duplicating refresh logic |
| `configure.py` | **NEW** | Setup wizard CLI — calls shared.ensure_setup() per platform |
| `skill/SKILL.md` | **NEW** | Claude Code skill — setup guidance + posting orchestration + X Playwright |
| `README.md` | **NEW** | Bilingual EN/ZH setup guide |
| `.env.example` | **EXISTS** | Already created at `~/Projects/content/packages/multi-post/.env.example` |
| `requirements.txt` | **NEW** | requests, python-dotenv |
| `LICENSE` | **NEW** | MIT |

---

## Task 1: Scaffold Repo

**Files:**
- Create: `~/Projects/multipost/` (directory)
- Create: `~/Projects/multipost/scripts/` (directory)
- Create: `~/Projects/multipost/skill/` (directory)
- Create: `~/Projects/multipost/requirements.txt`
- Create: `~/Projects/multipost/LICENSE`
- Copy: `~/Projects/content/packages/multi-post/.env.example` → `~/Projects/multipost/.env.example`
- Create: `~/Projects/multipost/scripts/__init__.py` (empty, makes scripts importable)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p ~/Projects/multipost/scripts ~/Projects/multipost/skill
```

- [ ] **Step 2: Copy .env.example**

```bash
cp ~/Projects/content/packages/multi-post/.env.example ~/Projects/multipost/.env.example
```

- [ ] **Step 3: Create requirements.txt**

Write to `~/Projects/multipost/requirements.txt`:
```
requests
python-dotenv
```

- [ ] **Step 4: Create LICENSE**

Write MIT license to `~/Projects/multipost/LICENSE` with copyright `2026 Mike Weng`.

- [ ] **Step 5: Create empty __init__.py**

```bash
touch ~/Projects/multipost/scripts/__init__.py
```

- [ ] **Step 6: Init git repo**

```bash
cd ~/Projects/multipost && git init
```

- [ ] **Step 7: Commit scaffold**

```bash
cd ~/Projects/multipost && git add -A && git commit -m "chore: scaffold multipost repo"
```

---

## Task 2: Build `shared.py` — Error Handling + Env Management

The foundation module. Build incrementally — this task covers the non-OAuth parts.

**Files:**
- Create: `~/Projects/multipost/scripts/shared.py`

- [ ] **Step 1: Write env management functions**

Write `scripts/shared.py` with these functions:

```python
"""Shared utilities for multipost scripts.

Provides: error handling, retry logic, env management, token refresh, OAuth flows.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Find .env relative to this file (project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


def load_env():
    """Load .env from project root. Create from .env.example if missing."""
    if not ENV_PATH.exists():
        example = PROJECT_ROOT / ".env.example"
        if example.exists():
            import shutil
            shutil.copy(example, ENV_PATH)
            print(f"Created .env from .env.example at {ENV_PATH}", file=sys.stderr)
        else:
            ENV_PATH.touch()
            print(f"Created empty .env at {ENV_PATH}", file=sys.stderr)
    load_dotenv(ENV_PATH)


def update_env(key, value):
    """Update a key in .env file and os.environ."""
    if not ENV_PATH.exists():
        ENV_PATH.touch()
    content = ENV_PATH.read_text()
    pattern = re.compile(rf'^({re.escape(key)}=)(.*)$', re.MULTILINE)
    if pattern.search(content):
        content = pattern.sub(rf'\g<1>{value}', content)
    else:
        if content and not content.endswith('\n'):
            content += '\n'
        content += f"{key}={value}\n"
    ENV_PATH.write_text(content)
    os.environ[key] = value


# Required env vars per platform
PLATFORM_VARS = {
    "threads": ["THREADS_ACCESS_TOKEN", "THREADS_USER_ID"],
    "instagram": ["INSTAGRAM_BUSINESS_ACCOUNT_ID", "INSTAGRAM_ACCESS_TOKEN"],
    "x": ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"],
    "linkedin": ["LINKEDIN_ACCESS_TOKEN", "LINKEDIN_PERSON_ID"],
    "tiktok": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_ACCESS_TOKEN"],
    "youtube": ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"],
}


def check_setup(platform):
    """Return True if all required env vars exist for a platform."""
    load_env()
    required = PLATFORM_VARS.get(platform, [])
    return all(os.environ.get(var) for var in required)


def check_all():
    """Return dict of {platform: bool} for all platforms."""
    load_env()
    return {p: check_setup(p) for p in PLATFORM_VARS}
```

- [ ] **Step 2: Write error handling + retry functions**

Append to `scripts/shared.py`:

```python
def handle_error(resp, step_name):
    """Handle 401/403/4xx errors with user-friendly messages. Exits on fatal."""
    if resp.status_code == 401:
        print(f"Error: 401 Unauthorized in {step_name} — token expired or invalid.", file=sys.stderr)
        print("Run: python3 configure.py <platform> to re-authenticate.", file=sys.stderr)
        sys.exit(1)
    if resp.status_code == 403:
        print(f"Error: 403 Forbidden in {step_name} — check API permissions/tier.", file=sys.stderr)
        sys.exit(1)
    if 400 <= resp.status_code < 500:
        try:
            detail = json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            detail = resp.text
        print(f"Error in {step_name}: {resp.status_code}", file=sys.stderr)
        print(detail, file=sys.stderr)
        sys.exit(1)


def retry_on_5xx(make_request, step_name):
    """Execute request, retry once on 5xx with 2s backoff."""
    resp = make_request()
    if resp.status_code >= 500:
        print(f"Server error in {step_name} ({resp.status_code}), retrying...", file=sys.stderr)
        time.sleep(2)
        resp = make_request()
    handle_error(resp, step_name)
    resp.raise_for_status()
    return resp
```

- [ ] **Step 3: Verify module loads**

```bash
cd ~/Projects/multipost && python3 -c "from scripts.shared import check_all, handle_error, retry_on_5xx, update_env; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
cd ~/Projects/multipost && git add scripts/shared.py scripts/__init__.py && git commit -m "feat: add shared.py — env management, error handling, retry"
```

---

## Task 3: Build `shared.py` — Token Refresh

Add token refresh functions (ported from existing `token_refresh.py`).

**Files:**
- Modify: `~/Projects/multipost/scripts/shared.py`

- [ ] **Step 1: Add token refresh functions**

Append to `scripts/shared.py`:

```python
# --- Token Refresh ---

def _refresh_threads():
    """Refresh Threads token via Meta Graph API."""
    token = os.environ.get("THREADS_ACCESS_TOKEN", "")
    if not token:
        return
    resp = requests.get(
        "https://graph.threads.net/refresh_access_token",
        params={"grant_type": "th_refresh_token", "access_token": token},
    )
    if resp.status_code == 200 and resp.json().get("access_token"):
        update_env("THREADS_ACCESS_TOKEN", resp.json()["access_token"])
        days = int(resp.json().get("expires_in", 0)) // 86400
        print(f"  Threads token refreshed (expires in {days} days)", file=sys.stderr)


def _refresh_instagram():
    """Refresh Instagram token via Meta Graph API."""
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if not token:
        return
    resp = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
    )
    if resp.status_code == 200 and resp.json().get("access_token"):
        update_env("INSTAGRAM_ACCESS_TOKEN", resp.json()["access_token"])
        days = int(resp.json().get("expires_in", 0)) // 86400
        print(f"  Instagram token refreshed (expires in {days} days)", file=sys.stderr)


def _refresh_tiktok():
    """Refresh TikTok token via OAuth 2.0 refresh_token flow."""
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
    refresh_token = os.environ.get("TIKTOK_REFRESH_TOKEN", "")
    if not all([client_key, client_secret, refresh_token]):
        return
    resp = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("access_token"):
            update_env("TIKTOK_ACCESS_TOKEN", data["access_token"])
        if data.get("refresh_token"):
            update_env("TIKTOK_REFRESH_TOKEN", data["refresh_token"])
        days = int(data.get("expires_in", 0)) // 86400
        print(f"  TikTok token refreshed (expires in {days} days)", file=sys.stderr)


def _refresh_linkedin():
    """Refresh LinkedIn token via OAuth 2.0 refresh_token flow."""
    client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
    refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN", "")
    if not all([client_id, client_secret, refresh_token]):
        return
    resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("access_token"):
            update_env("LINKEDIN_ACCESS_TOKEN", data["access_token"])
        if data.get("refresh_token"):
            update_env("LINKEDIN_REFRESH_TOKEN", data["refresh_token"])
        days = int(data.get("expires_in", 0)) // 86400
        print(f"  LinkedIn token refreshed (expires in {days} days)", file=sys.stderr)


def refresh_youtube_token():
    """Exchange YouTube refresh_token for a fresh access_token. Returns access_token string."""
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
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
        sys.exit(1)
    return resp.json()["access_token"]


_REFRESHERS = {
    "threads": _refresh_threads,
    "instagram": _refresh_instagram,
    "tiktok": _refresh_tiktok,
    "linkedin": _refresh_linkedin,
    # youtube: calls refresh_youtube_token() directly per request
    # x: OAuth 1.0a tokens don't expire
}


def ensure_fresh_token(platform):
    """Refresh token for a platform before posting. Silent no-op if not needed."""
    refresher = _REFRESHERS.get(platform)
    if refresher:
        try:
            refresher()
        except Exception as e:
            print(f"  Token refresh warning: {e}", file=sys.stderr)
```

- [ ] **Step 2: Verify refresh functions load**

```bash
cd ~/Projects/multipost && python3 -c "from scripts.shared import ensure_fresh_token, refresh_youtube_token; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd ~/Projects/multipost && git add scripts/shared.py && git commit -m "feat: add token refresh to shared.py"
```

---

## Task 4: Build `shared.py` — OAuth Browser Flow + Token Validation

The interactive setup infrastructure.

**Files:**
- Modify: `~/Projects/multipost/scripts/shared.py`

- [ ] **Step 1: Add OAuth browser flow helper**

Append to `scripts/shared.py`:

```python
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler that captures OAuth callback and stores the auth code."""
    auth_code = None
    error = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            _OAuthCallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Success!</h1><p>You can close this tab and return to the terminal.</p></body></html>")
        elif "error" in params:
            _OAuthCallbackHandler.error = params.get("error_description", params["error"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Error</h1><p>{_OAuthCallbackHandler.error}</p></body></html>".encode())
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logging


def oauth_browser_flow(auth_url_base, token_url, client_id, client_secret,
                        scopes, redirect_port=8789):
    """Open browser for OAuth consent, capture callback, exchange for tokens.

    Returns dict with "access_token", "refresh_token", etc.
    Tries ports 8789-8799 if default is busy. Timeout 120s.
    """
    # Find available port
    port = None
    server = None
    for p in range(redirect_port, redirect_port + 10):
        try:
            server = HTTPServer(("localhost", p), _OAuthCallbackHandler)
            port = p
            break
        except OSError:
            continue
    if not server:
        print("Error: Could not find an available port (tried 8789-8799).", file=sys.stderr)
        sys.exit(1)

    redirect_uri = f"http://localhost:{port}/callback"

    # Build auth URL
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes if isinstance(scopes, str) else " ".join(scopes),
    }
    auth_url = f"{auth_url_base}?{urllib.parse.urlencode(auth_params)}"

    # Reset handler state
    _OAuthCallbackHandler.auth_code = None
    _OAuthCallbackHandler.error = None

    print(f"\nOpening browser for authorization...", file=sys.stderr)
    print(f"If the browser doesn't open, visit: {auth_url}\n", file=sys.stderr)
    webbrowser.open(auth_url)

    # Wait for callback (timeout 120s)
    server.timeout = 120
    print("Waiting for authorization (timeout: 120s)...", file=sys.stderr)
    while _OAuthCallbackHandler.auth_code is None and _OAuthCallbackHandler.error is None:
        server.handle_request()

    server.server_close()

    if _OAuthCallbackHandler.error:
        print(f"OAuth error: {_OAuthCallbackHandler.error}", file=sys.stderr)
        sys.exit(1)
    if not _OAuthCallbackHandler.auth_code:
        print("Error: No authorization code received (timeout?).", file=sys.stderr)
        sys.exit(1)

    # Exchange code for tokens
    print("Exchanging authorization code for tokens...", file=sys.stderr)
    token_resp = requests.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "code": _OAuthCallbackHandler.auth_code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    if token_resp.status_code != 200:
        print(f"Error exchanging code: {token_resp.status_code}", file=sys.stderr)
        print(token_resp.text, file=sys.stderr)
        sys.exit(1)

    return token_resp.json()
```

- [ ] **Step 2: Add token validation functions**

Append to `scripts/shared.py`:

```python
# --- Token Validation ---

VALIDATION_ENDPOINTS = {
    "threads": ("GET", "https://graph.threads.net/v1.0/me", {"fields": "id,username"}),
    "instagram": ("GET", "https://graph.facebook.com/v21.0/{account_id}", {"fields": "id,username"}),
    "x": ("GET", "https://api.twitter.com/2/users/me", {}),
    "linkedin": ("GET", "https://api.linkedin.com/v2/userinfo", {}),
    "tiktok": ("GET", "https://open.tiktokapis.com/v2/user/info/", {}),
    "youtube": ("GET", "https://www.googleapis.com/youtube/v3/channels", {"part": "id", "mine": "true"}),
}


def validate_token(platform):
    """Test API call to check if token works. Returns True/False."""
    load_env()
    try:
        if platform == "threads":
            token = os.environ.get("THREADS_ACCESS_TOKEN", "")
            resp = requests.get("https://graph.threads.net/v1.0/me",
                                params={"fields": "id,username", "access_token": token})
            return resp.status_code == 200

        elif platform == "instagram":
            token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
            account_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
            resp = requests.get(f"https://graph.facebook.com/v21.0/{account_id}",
                                params={"fields": "id,username", "access_token": token})
            return resp.status_code == 200

        elif platform == "x":
            # X validation requires OAuth 1.0a header — skip for now, just check vars exist
            return check_setup("x")

        elif platform == "linkedin":
            token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
            resp = requests.get("https://api.linkedin.com/v2/userinfo",
                                headers={"Authorization": f"Bearer {token}"})
            return resp.status_code == 200

        elif platform == "tiktok":
            token = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
            resp = requests.get("https://open.tiktokapis.com/v2/user/info/",
                                headers={"Authorization": f"Bearer {token}"})
            return resp.status_code == 200

        elif platform == "youtube":
            access_token = refresh_youtube_token()
            resp = requests.get("https://www.googleapis.com/youtube/v3/channels",
                                params={"part": "id", "mine": "true"},
                                headers={"Authorization": f"Bearer {access_token}"})
            return resp.status_code == 200
    except Exception:
        return False
    return False
```

- [ ] **Step 3: Verify OAuth + validation load**

```bash
cd ~/Projects/multipost && python3 -c "from scripts.shared import oauth_browser_flow, validate_token; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
cd ~/Projects/multipost && git add scripts/shared.py && git commit -m "feat: add OAuth browser flow + token validation to shared.py"
```

---

## Task 5: Build `shared.py` — Interactive Setup Functions

Platform-specific setup guides that walk users through auth.

**Files:**
- Modify: `~/Projects/multipost/scripts/shared.py`

- [ ] **Step 1: Add Meta platform setup (Threads + Instagram)**

Append to `scripts/shared.py`:

```python
# --- Interactive Setup ---

def _setup_threads():
    """Guide user through Threads setup (Meta Developer Portal)."""
    print("\n=== Threads Setup ===\n")
    print("You need a Meta Developer account and app with Threads API enabled.")
    print()
    print("Steps:")
    print("  1. Go to https://developers.facebook.com/apps/")
    print("  2. Click 'Create App' → select 'Business' type")
    print("  3. Add the 'Threads API' product to your app")
    print("  4. Go to Threads API → API Explorer")
    print("  5. Generate a long-lived access token")
    print("  6. Copy your User ID from the same page")
    print()
    webbrowser.open("https://developers.facebook.com/apps/")
    print("(Opening Meta Developer Portal in your browser...)\n")

    token = input("Paste your Threads access token: ").strip()
    if not token:
        print("Aborted — no token provided.", file=sys.stderr)
        return False
    update_env("THREADS_ACCESS_TOKEN", token)

    user_id = input("Paste your Threads user ID: ").strip()
    if not user_id:
        print("Aborted — no user ID provided.", file=sys.stderr)
        return False
    update_env("THREADS_USER_ID", user_id)

    print("Validating...", file=sys.stderr)
    if validate_token("threads"):
        print("✅ Threads configured successfully!")
        return True
    else:
        print("❌ Validation failed — check your token and user ID.", file=sys.stderr)
        return False


def _setup_instagram():
    """Guide user through Instagram setup (Meta Developer Portal)."""
    print("\n=== Instagram Setup ===\n")
    print("You need a Meta Developer app with Instagram Graph API,")
    print("and an Instagram Business or Creator account (not personal).")
    print()
    print("Steps:")
    print("  1. Go to https://developers.facebook.com/apps/")
    print("  2. Use the same app as Threads (or create a new one)")
    print("  3. Add the 'Instagram Graph API' product")
    print("  4. Go to API Explorer → generate a long-lived token")
    print("  5. Get your Business Account ID from:")
    print("     curl 'https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_TOKEN'")
    print("     Then: curl 'https://graph.facebook.com/v21.0/PAGE_ID?fields=instagram_business_account&access_token=YOUR_TOKEN'")
    print()
    webbrowser.open("https://developers.facebook.com/apps/")
    print("(Opening Meta Developer Portal in your browser...)\n")

    token = input("Paste your Instagram access token: ").strip()
    if not token:
        print("Aborted.", file=sys.stderr)
        return False
    update_env("INSTAGRAM_ACCESS_TOKEN", token)

    account_id = input("Paste your Instagram Business Account ID: ").strip()
    if not account_id:
        print("Aborted.", file=sys.stderr)
        return False
    update_env("INSTAGRAM_BUSINESS_ACCOUNT_ID", account_id)

    print("Validating...", file=sys.stderr)
    if validate_token("instagram"):
        print("✅ Instagram configured successfully!")
        return True
    else:
        print("❌ Validation failed — check your token and account ID.", file=sys.stderr)
        return False
```

- [ ] **Step 2: Add X setup (guide + paste with cost warning)**

Append to `scripts/shared.py`:

```python
def _setup_x():
    """Guide user through X setup. Warns about $100/month cost."""
    print("\n=== X (Twitter) Setup ===\n")
    print("⚠️  X API requires the Basic tier ($100/month) for posting.")
    print("If you use the Claude Code skill, you can post to X for FREE via browser automation.")
    print()
    choice = input("Set up X API anyway? (y/n): ").strip().lower()
    if choice != "y":
        print("Skipped X setup. Use the Claude Code skill for free X posting.")
        return False

    print()
    print("Steps:")
    print("  1. Go to https://developer.x.com/en/portal/dashboard")
    print("  2. Create a Project + App")
    print("  3. Set app permissions to 'Read and Write'")
    print("  4. Go to 'Keys and Tokens' tab")
    print("  5. Generate all 4 tokens:")
    print("     - API Key (Consumer Key)")
    print("     - API Secret (Consumer Secret)")
    print("     - Access Token")
    print("     - Access Token Secret")
    print()
    webbrowser.open("https://developer.x.com/en/portal/dashboard")
    print("(Opening X Developer Portal in your browser...)\n")

    api_key = input("Paste API Key: ").strip()
    api_secret = input("Paste API Secret: ").strip()
    access_token = input("Paste Access Token: ").strip()
    access_token_secret = input("Paste Access Token Secret: ").strip()

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("Aborted — missing values.", file=sys.stderr)
        return False

    update_env("X_API_KEY", api_key)
    update_env("X_API_SECRET", api_secret)
    update_env("X_ACCESS_TOKEN", access_token)
    update_env("X_ACCESS_TOKEN_SECRET", access_token_secret)

    print("✅ X configured! (Token validation skipped — X uses OAuth 1.0a)")
    return True
```

- [ ] **Step 3: Add OAuth platform setups (LinkedIn, TikTok, YouTube)**

Append to `scripts/shared.py`:

```python
def _setup_linkedin():
    """Guide user through LinkedIn OAuth setup."""
    print("\n=== LinkedIn Setup ===\n")
    print("Steps to create a LinkedIn app:")
    print("  1. Go to https://www.linkedin.com/developers/apps")
    print("  2. Click 'Create App'")
    print("  3. Fill in company name (can be your own name)")
    print("  4. Under 'Auth' tab, add redirect URL: http://localhost:8789/callback")
    print("  5. Under 'Products' tab, request 'Community Management API'")
    print("  6. Copy your Client ID and Client Secret from the 'Auth' tab")
    print()
    webbrowser.open("https://www.linkedin.com/developers/apps")
    print("(Opening LinkedIn Developer Portal in your browser...)\n")

    client_id = input("Paste Client ID: ").strip()
    client_secret = input("Paste Client Secret: ").strip()
    if not client_id or not client_secret:
        print("Aborted.", file=sys.stderr)
        return False
    update_env("LINKEDIN_CLIENT_ID", client_id)
    update_env("LINKEDIN_CLIENT_SECRET", client_secret)

    print("\nStarting OAuth flow to get your access token...")
    tokens = oauth_browser_flow(
        auth_url_base="https://www.linkedin.com/oauth/v2/authorization",
        token_url="https://www.linkedin.com/oauth/v2/accessToken",
        client_id=client_id,
        client_secret=client_secret,
        scopes="openid profile w_member_social",
    )

    if tokens.get("access_token"):
        update_env("LINKEDIN_ACCESS_TOKEN", tokens["access_token"])
    if tokens.get("refresh_token"):
        update_env("LINKEDIN_REFRESH_TOKEN", tokens["refresh_token"])

    # Get person ID
    print("Getting your LinkedIn person ID...", file=sys.stderr)
    resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    if resp.status_code == 200:
        sub = resp.json().get("sub", "")
        person_id = f"urn:li:person:{sub}"
        update_env("LINKEDIN_PERSON_ID", person_id)
        print(f"✅ LinkedIn configured! Person ID: {person_id}")
        return True
    else:
        print("❌ Could not get LinkedIn person ID.", file=sys.stderr)
        return False


def _setup_tiktok():
    """Guide user through TikTok OAuth setup."""
    print("\n=== TikTok Setup ===\n")
    print("Steps to create a TikTok app:")
    print("  1. Go to https://developers.tiktok.com/apps/")
    print("  2. Click 'Create App' → select 'Web' platform")
    print("  3. Add redirect URL: http://localhost:8789/callback")
    print("  4. Request 'Content Posting API' scope")
    print("  5. Copy Client Key and Client Secret")
    print()
    print("Note: New apps start in sandbox mode (posts only visible to you).")
    print("Submit your app for review to go live.")
    print()
    webbrowser.open("https://developers.tiktok.com/apps/")
    print("(Opening TikTok Developer Portal in your browser...)\n")

    client_key = input("Paste Client Key: ").strip()
    client_secret = input("Paste Client Secret: ").strip()
    if not client_key or not client_secret:
        print("Aborted.", file=sys.stderr)
        return False
    update_env("TIKTOK_CLIENT_KEY", client_key)
    update_env("TIKTOK_CLIENT_SECRET", client_secret)

    print("\nStarting OAuth flow...")
    tokens = oauth_browser_flow(
        auth_url_base="https://www.tiktok.com/v2/auth/authorize/",
        token_url="https://open.tiktokapis.com/v2/oauth/token/",
        client_id=client_key,
        client_secret=client_secret,
        scopes="user.info.basic,video.publish",
    )

    if tokens.get("access_token"):
        update_env("TIKTOK_ACCESS_TOKEN", tokens["access_token"])
    if tokens.get("refresh_token"):
        update_env("TIKTOK_REFRESH_TOKEN", tokens["refresh_token"])

    print("Validating...", file=sys.stderr)
    if validate_token("tiktok"):
        print("✅ TikTok configured!")
        return True
    else:
        print("❌ Validation failed.", file=sys.stderr)
        return False


def _setup_youtube():
    """Guide user through YouTube/Google OAuth setup."""
    print("\n=== YouTube Setup ===\n")
    print("Steps to create Google OAuth credentials:")
    print("  1. Go to https://console.cloud.google.com/apis/credentials")
    print("  2. Create a project (or select existing)")
    print("  3. Enable 'YouTube Data API v3' in the API Library")
    print("  4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID")
    print("  5. Application type: 'Web application'")
    print("  6. Add redirect URI: http://localhost:8789/callback")
    print("  7. Copy Client ID and Client Secret")
    print()
    webbrowser.open("https://console.cloud.google.com/apis/credentials")
    print("(Opening Google Cloud Console in your browser...)\n")

    client_id = input("Paste Client ID: ").strip()
    client_secret = input("Paste Client Secret: ").strip()
    if not client_id or not client_secret:
        print("Aborted.", file=sys.stderr)
        return False
    update_env("YOUTUBE_CLIENT_ID", client_id)
    update_env("YOUTUBE_CLIENT_SECRET", client_secret)

    print("\nStarting OAuth flow to get refresh token...")
    tokens = oauth_browser_flow(
        auth_url_base="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes="https://www.googleapis.com/auth/youtube.upload",
    )

    if tokens.get("refresh_token"):
        update_env("YOUTUBE_REFRESH_TOKEN", tokens["refresh_token"])
    else:
        print("Warning: No refresh token received. You may need to revoke access and re-authorize.", file=sys.stderr)
        print("Visit: https://myaccount.google.com/permissions", file=sys.stderr)

    print("Validating...", file=sys.stderr)
    if validate_token("youtube"):
        print("✅ YouTube configured!")
        return True
    else:
        print("❌ Validation failed.", file=sys.stderr)
        return False
```

- [ ] **Step 4: Add ensure_setup dispatcher**

Append to `scripts/shared.py`:

```python
_SETUP_FUNCTIONS = {
    "threads": _setup_threads,
    "instagram": _setup_instagram,
    "x": _setup_x,
    "linkedin": _setup_linkedin,
    "tiktok": _setup_tiktok,
    "youtube": _setup_youtube,
}


def ensure_setup(platform, interactive=True):
    """Check if platform is configured. If not and interactive, guide through setup.

    Returns True if platform is ready to use, False otherwise.
    """
    if check_setup(platform):
        return True
    if not interactive:
        return False
    setup_fn = _SETUP_FUNCTIONS.get(platform)
    if not setup_fn:
        print(f"Error: Unknown platform '{platform}'", file=sys.stderr)
        return False
    return setup_fn()
```

- [ ] **Step 5: Verify all setup functions load**

```bash
cd ~/Projects/multipost && python3 -c "from scripts.shared import ensure_setup, check_all; print(check_all()); print('OK')"
```

Expected: All platforms show False (no .env), then `OK`.

- [ ] **Step 6: Commit**

```bash
cd ~/Projects/multipost && git add scripts/shared.py && git commit -m "feat: add interactive setup flows for all 6 platforms"
```

---

## Task 6: Port Posting Scripts

Copy existing scripts, rename, and refactor to use shared.py. Each script follows the same pattern — I'll show Threads in full and note the delta for others.

**Files:**
- Create: `~/Projects/multipost/scripts/post_threads.py`
- Create: `~/Projects/multipost/scripts/post_x.py`
- Create: `~/Projects/multipost/scripts/post_instagram.py`
- Create: `~/Projects/multipost/scripts/post_linkedin.py`
- Create: `~/Projects/multipost/scripts/post_tiktok.py`
- Create: `~/Projects/multipost/scripts/post_youtube.py`

- [ ] **Step 1: Create post_threads.py**

Write `scripts/post_threads.py` — this is the existing `post-to-threads.py` with these changes:
1. Replace `from token_refresh import ensure_fresh_token` with `from scripts.shared import ensure_setup, ensure_fresh_token, handle_error, retry_on_5xx, load_env`
2. Remove duplicated `_handle_error()` and `_retry_on_5xx()` functions
3. Remove `load_dotenv(...)` line — call `load_env()` from shared instead
4. Add `ensure_setup("threads", interactive=sys.stdin.isatty())` at top of `post_to_threads()`
5. Add `--setup` flag handling in `__main__`
6. Replace calls to `_handle_error` with `handle_error`, `_retry_on_5xx` with `retry_on_5xx`

The core posting logic (create container → wait → publish → get permalink) stays identical.

- [ ] **Step 2: Create post_x.py**

Copy from existing `post-to-x.py` with same shared.py refactoring. Keep the `_oauth_header()` function in-script (OAuth 1.0a signature is unique to X).

- [ ] **Step 3: Create post_instagram.py**

Copy from existing. Same refactoring. Keep the carousel upload flow identical.

- [ ] **Step 4: Create post_linkedin.py**

Copy from existing. Same refactoring. Keep `_upload_image()` in-script (LinkedIn-specific upload protocol).

- [ ] **Step 5: Create post_tiktok.py**

Copy from existing. Same refactoring. Keep video upload + polling flow identical.

- [ ] **Step 6: Create post_youtube.py**

Copy from existing. Replace `_refresh_access_token()` with `from scripts.shared import refresh_youtube_token`. Keep resumable upload flow identical.

- [ ] **Step 7: Test each script loads**

```bash
cd ~/Projects/multipost
for script in post_threads post_x post_instagram post_linkedin post_tiktok post_youtube; do
    python3 -c "import scripts.${script}" && echo "✅ ${script}" || echo "❌ ${script}"
done
```

Expected: All ✅

- [ ] **Step 8: Test --dry-run on one script** (doesn't need tokens)

```bash
cd ~/Projects/multipost
echo "THREADS_ACCESS_TOKEN=test\nTHREADS_USER_ID=123" > .env
python3 scripts/post_threads.py --dry-run "Test post"
rm .env
```

Expected: `[DRY RUN] Would post to Threads (9 chars): Test post`

- [ ] **Step 9: Commit**

```bash
cd ~/Projects/multipost && git add scripts/ && git commit -m "feat: add all 6 posting scripts with shared.py integration"
```

---

## Task 7: Create `refresh_tokens.py`

Port the standalone CLI refresh tool.

**Files:**
- Create: `~/Projects/multipost/scripts/refresh_tokens.py`

- [ ] **Step 1: Write refresh_tokens.py**

Write `scripts/refresh_tokens.py` — a simplified version of the existing one that calls into `shared.py`:

```python
#!/usr/bin/env python3
"""Refresh expiring OAuth tokens for all configured platforms.

Usage:
  python3 scripts/refresh_tokens.py              # Refresh all
  python3 scripts/refresh_tokens.py threads      # Refresh specific platform
  python3 scripts/refresh_tokens.py --dry-run    # Show what would refresh
"""

import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.shared import load_env, check_setup, ensure_fresh_token, PLATFORM_VARS

REFRESHABLE = ["threads", "instagram", "tiktok", "linkedin"]
# youtube: auto-refreshes per request
# x: tokens don't expire


def main():
    load_env()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv

    platforms = args if args else REFRESHABLE

    for platform in platforms:
        if platform not in REFRESHABLE:
            print(f"⏭️  {platform} — no refresh needed")
            continue
        if not check_setup(platform):
            print(f"⏭️  {platform} — not configured")
            continue
        if dry_run:
            print(f"🔄 {platform} — would refresh")
            continue
        print(f"🔄 {platform} — refreshing...", end=" ")
        try:
            ensure_fresh_token(platform)
            print("done")
        except Exception as e:
            print(f"failed: {e}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
cd ~/Projects/multipost && git add scripts/refresh_tokens.py && git commit -m "feat: add refresh_tokens.py CLI"
```

---

## Task 8: Create `configure.py`

The setup wizard.

**Files:**
- Create: `~/Projects/multipost/configure.py`

- [ ] **Step 1: Write configure.py**

```python
#!/usr/bin/env python3
"""Interactive setup wizard for multipost.

Usage:
  python3 configure.py              # Setup all platforms
  python3 configure.py threads      # Setup one platform
  python3 configure.py --status     # Show what's configured
"""

import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scripts.shared import load_env, check_setup, check_all, ensure_setup, validate_token, PLATFORM_VARS

ALL_PLATFORMS = ["threads", "instagram", "x", "linkedin", "tiktok", "youtube"]


def show_status():
    """Print configuration status for all platforms."""
    load_env()
    print("\nmultipost — platform status\n")
    for platform in ALL_PLATFORMS:
        if not check_setup(platform):
            if platform == "x":
                print(f"⏭️  {platform:12s} not configured (free via Playwright in Claude Code skill)")
            else:
                print(f"❌ {platform:12s} not configured")
        else:
            valid = validate_token(platform)
            if valid:
                print(f"✅ {platform:12s} configured (token valid)")
            else:
                print(f"⚠️  {platform:12s} configured but token may be expired")
    print()


def setup_all():
    """Walk through setup for each unconfigured platform."""
    load_env()
    print("\nmultipost — setup wizard\n")
    for platform in ALL_PLATFORMS:
        if check_setup(platform):
            print(f"✅ {platform} — already configured, skipping")
            continue
        choice = input(f"\nSet up {platform}? (y/n): ").strip().lower()
        if choice == "y":
            ensure_setup(platform, interactive=True)
        else:
            print(f"⏭️  Skipped {platform}")

    print("\n--- Final Status ---")
    show_status()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if "--status" in sys.argv:
        show_status()
        return

    if args:
        platform = args[0].lower()
        if platform not in ALL_PLATFORMS:
            print(f"Unknown platform: {platform}", file=sys.stderr)
            print(f"Available: {', '.join(ALL_PLATFORMS)}", file=sys.stderr)
            sys.exit(1)
        load_env()
        ensure_setup(platform, interactive=True)
    else:
        setup_all()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test --status on fresh repo**

```bash
cd ~/Projects/multipost && python3 configure.py --status
```

Expected: All platforms show ❌ or ⏭️

- [ ] **Step 3: Commit**

```bash
cd ~/Projects/multipost && git add configure.py && git commit -m "feat: add configure.py setup wizard"
```

---

## Task 9: Create Claude Code Skill

**Files:**
- Create: `~/Projects/multipost/skill/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Write the skill file with setup detection, posting orchestration, and X Playwright fallback. The skill should:

1. Detect which platforms are configured via `python3 configure.py --status`
2. Guide setup for unconfigured platforms via `python3 configure.py <platform>`
3. Post to API platforms via `python3 scripts/post_<platform>.py "text"`
4. Post to X via Playwright (navigate → type → click Post)
5. Present copy-paste block for RED
6. Support "post everywhere" to hit all configured platforms
7. Always confirm before posting, suggest dry-run on first use
8. Use relative paths (assume user is in project root)

This is a markdown skill file — no code to test, just write it clearly.

- [ ] **Step 2: Commit**

```bash
cd ~/Projects/multipost && git add skill/SKILL.md && git commit -m "feat: add Claude Code skill for guided setup + posting"
```

---

## Task 10: Write README.md

**Files:**
- Create: `~/Projects/multipost/README.md`

- [ ] **Step 1: Write bilingual README**

Cover:
- One-line description (EN + ZH)
- Quick Start: With Claude Code (3 steps) + Without Claude Code (4 steps)
- Supported Platforms table (6 platforms, what each supports, cost)
- Platform setup details (per-platform instructions summary)
- Usage examples (per-platform CLI examples)
- Token refresh (auto + manual)
- "How I Built This" section (content angle — Claude Code built it)
- Troubleshooting (common auth errors and fixes)
- License (MIT)

- [ ] **Step 2: Commit**

```bash
cd ~/Projects/multipost && git add README.md && git commit -m "docs: add bilingual README"
```

---

## Task 11: Final Verification + Cleanup

- [ ] **Step 1: Verify full project structure**

```bash
cd ~/Projects/multipost && find . -type f | sort | grep -v '.git/'
```

Expected files:
```
./.env.example
./LICENSE
./README.md
./configure.py
./requirements.txt
./scripts/__init__.py
./scripts/post_instagram.py
./scripts/post_linkedin.py
./scripts/post_threads.py
./scripts/post_tiktok.py
./scripts/post_x.py
./scripts/post_youtube.py
./scripts/refresh_tokens.py
./scripts/shared.py
./skill/SKILL.md
```

- [ ] **Step 2: Check for personal data**

```bash
cd ~/Projects/multipost && grep -rn "mikeweng\|mcc.weng\|mccweng\|THAANq\|25932\|openclaw\|sister\|Brisbane\|Melbourne" . --include='*.py' --include='*.md' | grep -v '.git/'
```

Expected: Only README.md "How I Built This" section may mention personal story (acceptable). No tokens, no personal paths.

- [ ] **Step 3: Test fresh clone experience**

```bash
cd /tmp && cp -r ~/Projects/multipost multipost-test && cd multipost-test
pip install -r requirements.txt
python3 configure.py --status
python3 scripts/post_threads.py --dry-run "Hello from multipost"
```

Expected: Status shows all ❌. Dry-run triggers setup prompt (interactive) or fails gracefully (non-interactive).

- [ ] **Step 4: Commit any cleanup**

```bash
cd ~/Projects/multipost && git add -A && git status
# If changes: git commit -m "chore: final cleanup"
```

---

## Task 12: Publish

- [ ] **Step 1: Create GitHub repo**

```bash
cd ~/Projects/multipost
gh repo create mikeweng/multipost --public --source=. --push --description "Post to 6 platforms with one command. 一個指令，發到 6 個平台。"
```

- [ ] **Step 2: DM the link to Threads commenters**

Share `https://github.com/mikeweng/multipost` with everyone who commented "發文".

- [ ] **Step 3: Publish skill to prompts.chat** (optional, can do later)

Use the prompts.chat skill-manager to publish `skill/SKILL.md`.
