"""Shared token refresh logic for posting scripts.

Each posting script calls ensure_fresh_token("platform") before making API calls.
This refreshes the token if possible and updates both .env and os.environ.

Usage in posting scripts:
    from token_refresh import ensure_fresh_token
    ensure_fresh_token("threads")  # refreshes token, updates .env + os.environ
"""

import os
import re
import sys
from pathlib import Path

import requests

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _update_env_file(key, new_value):
    """Update a single key in the .env file in-place."""
    content = ENV_PATH.read_text()
    pattern = re.compile(rf'^({re.escape(key)}=)(.*)$', re.MULTILINE)
    if pattern.search(content):
        content = pattern.sub(rf'\g<1>{new_value}', content)
    else:
        content += f"\n{key}={new_value}\n"
    ENV_PATH.write_text(content)


def _update(key, value):
    """Update both .env file and current process environment."""
    _update_env_file(key, value)
    os.environ[key] = value


def _refresh_threads():
    token = os.environ.get("THREADS_ACCESS_TOKEN", "")
    if not token or token.startswith("PLACEHOLDER"):
        return
    resp = requests.get(
        "https://graph.threads.net/refresh_access_token",
        params={"grant_type": "th_refresh_token", "access_token": token},
    )
    if resp.status_code == 200 and resp.json().get("access_token"):
        _update("THREADS_ACCESS_TOKEN", resp.json()["access_token"])
        days = int(resp.json().get("expires_in", 0)) // 86400
        print(f"  Token refreshed (expires in {days} days)", file=sys.stderr)


def _refresh_instagram():
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    if not token or token.startswith("PLACEHOLDER"):
        return
    resp = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
    )
    if resp.status_code == 200 and resp.json().get("access_token"):
        _update("INSTAGRAM_ACCESS_TOKEN", resp.json()["access_token"])
        days = int(resp.json().get("expires_in", 0)) // 86400
        print(f"  Token refreshed (expires in {days} days)", file=sys.stderr)


def _refresh_tiktok():
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET", "")
    refresh_token = os.environ.get("TIKTOK_REFRESH_TOKEN", "")
    if not all([client_key, client_secret, refresh_token]) or refresh_token.startswith("PLACEHOLDER"):
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
            _update("TIKTOK_ACCESS_TOKEN", data["access_token"])
        if data.get("refresh_token"):
            _update("TIKTOK_REFRESH_TOKEN", data["refresh_token"])
        days = int(data.get("expires_in", 0)) // 86400
        print(f"  Token refreshed (expires in {days} days)", file=sys.stderr)


def _refresh_linkedin():
    client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
    refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN", "")
    if not all([client_id, client_secret, refresh_token]) or refresh_token.startswith("PLACEHOLDER"):
        return  # LinkedIn often has no refresh token — long-lived access token instead
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
            _update("LINKEDIN_ACCESS_TOKEN", data["access_token"])
        if data.get("refresh_token"):
            _update("LINKEDIN_REFRESH_TOKEN", data["refresh_token"])
        days = int(data.get("expires_in", 0)) // 86400
        print(f"  Token refreshed (expires in {days} days)", file=sys.stderr)


_REFRESHERS = {
    "threads": _refresh_threads,
    "instagram": _refresh_instagram,
    "tiktok": _refresh_tiktok,
    "linkedin": _refresh_linkedin,
    # youtube: auto-refreshes in its own script via refresh token
    # x: OAuth 1.0a tokens don't expire
}


def ensure_fresh_token(platform):
    """Refresh the token for a platform before posting. Silent no-op if refresh isn't needed/possible."""
    refresher = _REFRESHERS.get(platform)
    if refresher:
        try:
            refresher()
        except Exception as e:
            # Don't block posting if refresh fails — the post itself will fail with 401
            # and show a clear error message
            print(f"  Token refresh warning: {e}", file=sys.stderr)
