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
