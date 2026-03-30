#!/usr/bin/env python3
"""Index all videos from a YouTube channel into structured markdown.

Usage:
    python scripts/hormozi-index.py CHANNEL_URL [--output PATH] [--api]

Examples:
    python scripts/hormozi-index.py "https://www.youtube.com/@AlexHormozi"
    python scripts/hormozi-index.py "https://www.youtube.com/@AlexHormozi" --output docs/research/hormozi/content-index-youtube.md
    python scripts/hormozi-index.py "https://www.youtube.com/@AlexHormozi" --api  # use YouTube Data API
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def fetch_via_ytdlp(channel_url: str) -> list[dict]:
    """Fetch all video metadata from a channel using yt-dlp."""
    print(f"Fetching video list from {channel_url} via yt-dlp...", file=sys.stderr)
    print("This may take a few minutes for large channels.", file=sys.stderr)

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        channel_url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        print(f"yt-dlp error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            videos.append({
                "id": data.get("id", ""),
                "title": data.get("title", ""),
                "url": data.get("url", "") or f"https://www.youtube.com/watch?v={data.get('id', '')}",
                "duration": data.get("duration"),
                "view_count": data.get("view_count"),
                "like_count": data.get("like_count"),
                "upload_date": data.get("upload_date", ""),
                "description": (data.get("description") or "")[:200],
            })
        except json.JSONDecodeError:
            continue

    return videos


def fetch_via_api(channel_url: str) -> list[dict]:
    """Fetch all video metadata using YouTube Data API v3."""
    import requests

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY not set in .env, falling back to yt-dlp", file=sys.stderr)
        return fetch_via_ytdlp(channel_url)

    handle = channel_url.rstrip("/").split("/")[-1]

    print(f"Resolving channel {handle}...", file=sys.stderr)
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={"part": "snippet", "q": handle, "type": "channel", "key": api_key},
    )
    if resp.status_code != 200:
        print(f"API error resolving channel: {resp.status_code} {resp.text}", file=sys.stderr)
        print("Falling back to yt-dlp...", file=sys.stderr)
        return fetch_via_ytdlp(channel_url)

    items = resp.json().get("items", [])
    if not items:
        print(f"No channel found for {handle}, falling back to yt-dlp", file=sys.stderr)
        return fetch_via_ytdlp(channel_url)

    channel_id = items[0]["snippet"]["channelId"]

    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "contentDetails", "id": channel_id, "key": api_key},
    )
    uploads_playlist = resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    page_token = None
    while True:
        params = {
            "part": "snippet",
            "playlistId": uploads_playlist,
            "maxResults": 50,
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params,
        )
        if resp.status_code != 200:
            print(f"API error fetching videos: {resp.status_code}", file=sys.stderr)
            break

        data = resp.json()
        video_ids = [item["snippet"]["resourceId"]["videoId"] for item in data.get("items", [])]

        if video_ids:
            stats_resp = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics,contentDetails,snippet",
                    "id": ",".join(video_ids),
                    "key": api_key,
                },
            )
            if stats_resp.status_code == 200:
                for item in stats_resp.json().get("items", []):
                    snippet = item["snippet"]
                    stats = item.get("statistics", {})
                    videos.append({
                        "id": item["id"],
                        "title": snippet.get("title", ""),
                        "url": f"https://www.youtube.com/watch?v={item['id']}",
                        "duration": item.get("contentDetails", {}).get("duration", ""),
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "upload_date": snippet.get("publishedAt", "")[:10].replace("-", ""),
                        "description": snippet.get("description", "")[:200],
                    })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

        print(f"  Fetched {len(videos)} videos so far...", file=sys.stderr)

    return videos


def format_date(date_str: str) -> str:
    """Convert YYYYMMDD to YYYY-MM-DD."""
    if not date_str or len(date_str) < 8:
        return date_str
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"


def format_duration(seconds) -> str:
    """Convert seconds to HH:MM:SS or MM:SS."""
    if not seconds:
        return "N/A"
    if isinstance(seconds, str):
        return seconds
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_count(n) -> str:
    """Format large numbers: 1234567 -> 1.2M, 12345 -> 12.3K."""
    if n is None:
        return "N/A"
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def categorize_topic(title: str, description: str) -> str:
    """Auto-categorize video by topic based on title/description keywords."""
    text = (title + " " + description).lower()
    categories = {
        "offers": ["offer", "$100m offers", "grand slam", "value equation"],
        "leads": ["lead", "$100m leads", "lead magnet", "lead gen"],
        "sales": ["sales", "closing", "closer", "objection", "selling"],
        "pricing": ["price", "pricing", "charge", "premium"],
        "hiring": ["hire", "hiring", "employee", "team", "recruit", "talent"],
        "content": ["content", "youtube", "social media", "posting", "viral"],
        "branding": ["brand", "branding", "personal brand", "reputation"],
        "scaling": ["scale", "scaling", "growth", "grow", "million", "billion"],
        "mindset": ["mindset", "motivation", "discipline", "habit", "success"],
        "ads": ["ads", "advertising", "paid", "facebook ads", "google ads"],
        "retention": ["retention", "churn", "keep", "lifetime value", "ltv"],
        "gym": ["gym", "fitness", "gym launch"],
    }
    found = []
    for cat, keywords in categories.items():
        if any(kw in text for kw in keywords):
            found.append(cat)
    return ", ".join(found[:3]) if found else "general"


def generate_markdown(videos: list[dict], channel_url: str) -> str:
    """Generate markdown index from video list."""
    videos_sorted = sorted(videos, key=lambda v: int(v.get("view_count") or 0), reverse=True)

    lines = [
        f"# YouTube Content Index — Alex Hormozi",
        f"",
        f"**Source:** {channel_url}",
        f"**Indexed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total videos:** {len(videos)}",
        f"",
        f"---",
        f"",
        f"## Top Videos by Views",
        f"",
        f"| # | Title | Views | Likes | Duration | Date | Topics |",
        f"|---|-------|-------|-------|----------|------|--------|",
    ]

    for i, v in enumerate(videos_sorted, 1):
        title = v["title"].replace("|", "\\|")
        url = v["url"]
        views = format_count(v.get("view_count"))
        likes = format_count(v.get("like_count"))
        dur = format_duration(v.get("duration"))
        date = format_date(v.get("upload_date", ""))
        topic = categorize_topic(v["title"], v.get("description", ""))
        lines.append(f"| {i} | [{title}]({url}) | {views} | {likes} | {dur} | {date} | {topic} |")

    lines.extend([
        "",
        "---",
        "",
        "## Phase 2 Candidates (P1 — High Priority)",
        "",
        "Videos recommended for deep-dive transcription based on views, topic relevance, and framework density:",
        "",
    ])

    for i, v in enumerate(videos_sorted[:30], 1):
        title = v["title"]
        views = format_count(v.get("view_count"))
        url = v["url"]
        lines.append(f"{i}. [{title}]({url}) — {views} views")

    lines.append("")
    lines.append("*Review and refine this list based on framework density and relevance to agency → brand → info → SaaS path.*")

    return "\n".join(lines)


def main():
    args = list(sys.argv[1:])

    use_api = "--api" in args
    if use_api:
        args.remove("--api")

    output_path = None
    if "--output" in args:
        idx = args.index("--output")
        output_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if not args:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    channel_url = args[0]

    if use_api:
        videos = fetch_via_api(channel_url)
    else:
        videos = fetch_via_ytdlp(channel_url)

    print(f"Found {len(videos)} videos.", file=sys.stderr)

    md = generate_markdown(videos, channel_url)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(md)
        print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
