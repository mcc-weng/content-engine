#!/usr/bin/env python3
"""Refresh expiring OAuth tokens and update .env file.

Usage:
  python3 refresh-tokens.py           # Refresh all expiring tokens
  python3 refresh-tokens.py --dry-run  # Show what would be refreshed without updating
  python3 refresh-tokens.py threads    # Refresh only Threads token
  python3 refresh-tokens.py instagram  # Refresh only Instagram token

Platforms with refreshable tokens:
  threads    — Meta Graph API token exchange (~60 day expiry)
  instagram  — Meta Graph API token exchange (~60 day expiry)
  tiktok     — OAuth 2.0 refresh token flow
  linkedin   — OAuth 2.0 refresh token flow

Skipped (no refresh needed):
  youtube    — auto-refreshes on every post via refresh token
  x          — OAuth 1.0a tokens don't expire
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)


def _update_env_file(key, new_value):
    """Update a single key in the .env file in-place."""
    content = ENV_PATH.read_text()
    # Match KEY=value (handles quoted and unquoted values)
    pattern = re.compile(rf'^({re.escape(key)}=)(.*)$', re.MULTILINE)
    if pattern.search(content):
        content = pattern.sub(rf'\g<1>{new_value}', content)
    else:
        content += f"\n{key}={new_value}\n"
    ENV_PATH.write_text(content)


def refresh_threads(dry_run=False):
    """Refresh Threads long-lived token via Meta Graph API."""
    token = os.environ.get("THREADS_ACCESS_TOKEN")
    app_secret = os.environ.get("THREADS_APP_SECRET")

    if not token or token.startswith("PLACEHOLDER"):
        print("  Threads: skipped (no token set)", file=sys.stderr)
        return False
    if not app_secret:
        print("  Threads: skipped (THREADS_APP_SECRET not set — needed for refresh)", file=sys.stderr)
        return False

    if dry_run:
        print("  Threads: would refresh token", file=sys.stderr)
        return True

    resp = requests.get(
        "https://graph.threads.net/refresh_access_token",
        params={
            "grant_type": "th_refresh_token",
            "access_token": token,
        },
    )
    if resp.status_code != 200:
        print(f"  Threads: refresh failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        return False

    new_token = resp.json().get("access_token")
    if new_token:
        _update_env_file("THREADS_ACCESS_TOKEN", new_token)
        expires_in = resp.json().get("expires_in", "unknown")
        print(f"  Threads: refreshed (expires in {int(expires_in)//86400} days)", file=sys.stderr)
        return True

    print(f"  Threads: unexpected response: {resp.text}", file=sys.stderr)
    return False


def refresh_instagram(dry_run=False):
    """Refresh Instagram long-lived token via Facebook Graph API."""
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")

    if not token or token.startswith("PLACEHOLDER"):
        print("  Instagram: skipped (no token set)", file=sys.stderr)
        return False

    if dry_run:
        print("  Instagram: would refresh token", file=sys.stderr)
        return True

    resp = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={
            "grant_type": "ig_refresh_token",
            "access_token": token,
        },
    )
    if resp.status_code != 200:
        print(f"  Instagram: refresh failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        return False

    new_token = resp.json().get("access_token")
    if new_token:
        _update_env_file("INSTAGRAM_ACCESS_TOKEN", new_token)
        expires_in = resp.json().get("expires_in", "unknown")
        print(f"  Instagram: refreshed (expires in {int(expires_in)//86400} days)", file=sys.stderr)
        return True

    print(f"  Instagram: unexpected response: {resp.text}", file=sys.stderr)
    return False


def refresh_tiktok(dry_run=False):
    """Refresh TikTok access token via OAuth 2.0 refresh token."""
    client_key = os.environ.get("TIKTOK_CLIENT_KEY")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET")
    refresh_token = os.environ.get("TIKTOK_REFRESH_TOKEN")

    if not refresh_token or refresh_token.startswith("PLACEHOLDER"):
        print("  TikTok: skipped (no refresh token set — add TIKTOK_REFRESH_TOKEN to .env)", file=sys.stderr)
        return False
    if not client_key or not client_secret:
        print("  TikTok: skipped (missing TIKTOK_CLIENT_KEY or TIKTOK_CLIENT_SECRET)", file=sys.stderr)
        return False

    if dry_run:
        print("  TikTok: would refresh token", file=sys.stderr)
        return True

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
    if resp.status_code != 200:
        print(f"  TikTok: refresh failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        return False

    data = resp.json()
    new_access = data.get("access_token")
    new_refresh = data.get("refresh_token")

    if new_access:
        _update_env_file("TIKTOK_ACCESS_TOKEN", new_access)
        if new_refresh:
            _update_env_file("TIKTOK_REFRESH_TOKEN", new_refresh)
        expires_in = data.get("expires_in", "unknown")
        print(f"  TikTok: refreshed (expires in {int(expires_in)//86400} days)", file=sys.stderr)
        return True

    print(f"  TikTok: unexpected response: {resp.text}", file=sys.stderr)
    return False


def refresh_linkedin(dry_run=False):
    """Refresh LinkedIn access token via OAuth 2.0 refresh token."""
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
    refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN")

    if not refresh_token or refresh_token.startswith("PLACEHOLDER"):
        print("  LinkedIn: skipped (no refresh token set — add LINKEDIN_REFRESH_TOKEN to .env)", file=sys.stderr)
        return False
    if not client_id or not client_secret:
        print("  LinkedIn: skipped (missing LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET)", file=sys.stderr)
        return False

    if dry_run:
        print("  LinkedIn: would refresh token", file=sys.stderr)
        return True

    resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    if resp.status_code != 200:
        print(f"  LinkedIn: refresh failed ({resp.status_code}): {resp.text}", file=sys.stderr)
        return False

    data = resp.json()
    new_access = data.get("access_token")
    new_refresh = data.get("refresh_token")

    if new_access:
        _update_env_file("LINKEDIN_ACCESS_TOKEN", new_access)
        if new_refresh:
            _update_env_file("LINKEDIN_REFRESH_TOKEN", new_refresh)
        expires_in = data.get("expires_in", "unknown")
        print(f"  LinkedIn: refreshed (expires in {int(expires_in)//86400} days)", file=sys.stderr)
        return True

    print(f"  LinkedIn: unexpected response: {resp.text}", file=sys.stderr)
    return False


REFRESHERS = {
    "threads": refresh_threads,
    "instagram": refresh_instagram,
    "tiktok": refresh_tiktok,
    "linkedin": refresh_linkedin,
}


if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = False

    if "--dry-run" in args:
        dry_run = True
        args.remove("--dry-run")

    # If specific platform(s) given, only refresh those
    platforms = args if args else list(REFRESHERS.keys())

    invalid = [p for p in platforms if p not in REFRESHERS]
    if invalid:
        print(f"Error: unknown platform(s): {', '.join(invalid)}", file=sys.stderr)
        print(f"Valid platforms: {', '.join(REFRESHERS.keys())}", file=sys.stderr)
        sys.exit(1)

    print(f"{'[DRY RUN] ' if dry_run else ''}Refreshing tokens for: {', '.join(platforms)}", file=sys.stderr)

    results = {}
    for platform in platforms:
        results[platform] = REFRESHERS[platform](dry_run=dry_run)

    # Summary
    refreshed = [p for p, ok in results.items() if ok]
    failed = [p for p, ok in results.items() if not ok]

    if refreshed:
        print(f"\nRefreshed: {', '.join(refreshed)}", file=sys.stderr)
    if failed:
        print(f"Skipped/failed: {', '.join(failed)}", file=sys.stderr)
