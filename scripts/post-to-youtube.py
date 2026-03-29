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

    print("Refreshing YouTube access token...", file=sys.stderr)
    access_token = _refresh_access_token()

    if is_short and "#Shorts" not in title:
        title = f"{title} #Shorts"

    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

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
