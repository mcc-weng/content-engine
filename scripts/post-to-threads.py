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
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

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
