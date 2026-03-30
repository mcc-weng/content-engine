# Alex Hormozi Deep Dive Research — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Systematically index, transcribe, and analyze Alex Hormozi's content across all platforms, producing an actionable business playbook and content strategy guide.

**Architecture:** Phase 1 builds two Python scripts (YouTube indexer via yt-dlp, Playwright scraper for social platforms) that output structured markdown. Phase 2 uses existing `/transcribe` skill + Claude analysis. Phase 3 is pure synthesis — no new code.

**Tech Stack:** Python 3 (requests, python-dotenv), yt-dlp CLI, Playwright MCP, Whisper (via /transcribe skill)

---

## File Structure

```
scripts/
├── hormozi-index.py          # YouTube channel indexer (yt-dlp + optional API)
└── hormozi-scrape.py          # Playwright scraper for social platforms

docs/research/hormozi/
├── content-index.md           # Master catalogue (Phase 1 output)
├── content-index-youtube.md   # YouTube-specific index (if >500 entries)
├── transcripts/               # Raw transcripts (Phase 2)
├── analyses/                  # Per-piece analysis (Phase 2)
├── hormozi-business-playbook.md   # Phase 3
├── hormozi-content-strategy.md    # Phase 3
└── hormozi-style-guide.md         # Phase 3
```

---

## Phase 1: Map the Territory

### Task 1: Create directory structure

**Files:**
- Create: `docs/research/hormozi/transcripts/.gitkeep`
- Create: `docs/research/hormozi/analyses/.gitkeep`

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p docs/research/hormozi/transcripts docs/research/hormozi/analyses
touch docs/research/hormozi/transcripts/.gitkeep docs/research/hormozi/analyses/.gitkeep
```

- [ ] **Step 2: Commit**

```bash
git add docs/research/hormozi/
git commit -m "chore: create hormozi research directory structure"
```

---

### Task 2: Build YouTube channel indexer script

**Files:**
- Create: `scripts/hormozi-index.py`

This script uses `yt-dlp --flat-playlist --dump-json` to fetch all video metadata from a YouTube channel. No API key required. If `YOUTUBE_API_KEY` is set in `.env`, it uses the YouTube Data API v3 instead for richer metadata (like counts, descriptions).

- [ ] **Step 1: Create the script with yt-dlp approach**

```python
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

    # Extract channel handle or ID from URL
    # e.g. https://www.youtube.com/@AlexHormozi -> @AlexHormozi
    handle = channel_url.rstrip("/").split("/")[-1]

    # Resolve handle to channel ID
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

    # Get uploads playlist
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "contentDetails", "id": channel_id, "key": api_key},
    )
    uploads_playlist = resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Paginate through all videos
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

        # Batch fetch video stats
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
        return seconds  # Already formatted (API returns ISO 8601)
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
    # Sort by view count descending
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

    # Priority recommendations
    lines.extend([
        "",
        "---",
        "",
        "## Phase 2 Candidates (P1 — High Priority)",
        "",
        "Videos recommended for deep-dive transcription based on views, topic relevance, and framework density:",
        "",
    ])

    # Auto-flag top 30 by views as P1 candidates (human will curate)
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
```

- [ ] **Step 2: Verify yt-dlp is installed**

Run: `which yt-dlp`
Expected: a valid path like `/opt/homebrew/bin/yt-dlp`

If not installed: `brew install yt-dlp`

- [ ] **Step 3: Test with a small channel first (dry run)**

Run: `python scripts/hormozi-index.py "https://www.youtube.com/@AlexHormozi" --output docs/research/hormozi/content-index-youtube.md 2>&1 | head -20`

Expected: Progress output showing video count, then markdown file created.

- [ ] **Step 4: Verify output file**

Run: `head -30 docs/research/hormozi/content-index-youtube.md`

Expected: Markdown table with video titles, view counts, dates.

- [ ] **Step 5: Commit**

```bash
git add scripts/hormozi-index.py docs/research/hormozi/content-index-youtube.md
git commit -m "feat: add YouTube channel indexer for Hormozi research"
```

---

### Task 3: Index Hormozi's second YouTube channel (Hormozi Clips)

**Files:**
- Modify: `docs/research/hormozi/content-index-youtube.md` (append or create separate file)

- [ ] **Step 1: Run indexer on Hormozi Clips channel**

```bash
python scripts/hormozi-index.py "https://www.youtube.com/@HormoziClips" --output docs/research/hormozi/content-index-youtube-clips.md
```

- [ ] **Step 2: Verify output**

Run: `head -30 docs/research/hormozi/content-index-youtube-clips.md`

- [ ] **Step 3: Commit**

```bash
git add docs/research/hormozi/content-index-youtube-clips.md
git commit -m "feat: index Hormozi Clips YouTube channel"
```

---

### Task 4: Build Playwright scraper for social platforms

**Files:**
- Create: `scripts/hormozi-scrape.py`

This script uses Playwright MCP (via Claude's browser automation) to scrape social platforms. It's designed to be run interactively — Claude navigates the browser, extracts data, and writes results. The script itself is a CLI tool that coordinates the scraping and formats output.

**Important:** Social platform scraping is inherently interactive (login prompts, pagination, rate limits). This script handles the non-interactive parts (data formatting, output). The actual browser automation happens through Claude + Playwright MCP during execution.

- [ ] **Step 1: Create the scraper script**

```python
#!/usr/bin/env python3
"""Scrape Alex Hormozi's social media profiles for content indexing.

This script formats scraped data into markdown. The actual scraping
is done interactively via Claude + Playwright MCP browser automation.

Usage:
    python scripts/hormozi-scrape.py format --platform instagram --input data.json --output index.md
    python scripts/hormozi-scrape.py format --platform x --input data.json --output index.md

The expected workflow:
1. Claude uses Playwright MCP to navigate to Hormozi's profile
2. Claude extracts post data (captions, engagement, dates) into JSON
3. This script formats that JSON into the standard markdown index format

Supported platforms: instagram, x, linkedin, tiktok, skool, acquisition.com
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def format_count(n) -> str:
    if n is None:
        return "N/A"
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


PLATFORM_FORMATTERS = {
    "instagram": {
        "columns": ["#", "Type", "Caption", "Likes", "Comments", "Date"],
        "row": lambda i, p: f"| {i} | {p.get('type', 'post')} | {p.get('caption', '')[:80].replace('|', '\\|')} | {format_count(p.get('likes'))} | {format_count(p.get('comments'))} | {p.get('date', 'N/A')} |",
    },
    "x": {
        "columns": ["#", "Tweet", "Retweets", "Likes", "Replies", "Date"],
        "row": lambda i, p: f"| {i} | {p.get('text', '')[:100].replace('|', '\\|')} | {format_count(p.get('retweets'))} | {format_count(p.get('likes'))} | {format_count(p.get('replies'))} | {p.get('date', 'N/A')} |",
    },
    "linkedin": {
        "columns": ["#", "Post", "Reactions", "Comments", "Date"],
        "row": lambda i, p: f"| {i} | {p.get('text', '')[:100].replace('|', '\\|')} | {format_count(p.get('reactions'))} | {format_count(p.get('comments'))} | {p.get('date', 'N/A')} |",
    },
    "tiktok": {
        "columns": ["#", "Caption", "Views", "Likes", "Comments", "Date"],
        "row": lambda i, p: f"| {i} | {p.get('caption', '')[:80].replace('|', '\\|')} | {format_count(p.get('views'))} | {format_count(p.get('likes'))} | {format_count(p.get('comments'))} | {p.get('date', 'N/A')} |",
    },
}


def format_platform_index(platform: str, posts: list[dict], profile_url: str) -> str:
    """Format scraped posts into markdown index."""
    fmt = PLATFORM_FORMATTERS.get(platform)
    if not fmt:
        print(f"Unknown platform: {platform}. Supported: {list(PLATFORM_FORMATTERS.keys())}", file=sys.stderr)
        sys.exit(1)

    header = " | ".join(fmt["columns"])
    separator = " | ".join(["---"] * len(fmt["columns"]))

    lines = [
        f"# {platform.title()} Content Index — Alex Hormozi",
        "",
        f"**Source:** {profile_url}",
        f"**Indexed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total posts scraped:** {len(posts)}",
        "",
        "---",
        "",
        f"## Top Posts by Engagement",
        "",
        f"| {header} |",
        f"| {separator} |",
    ]

    for i, post in enumerate(posts, 1):
        lines.append(fmt["row"](i, post))

    return "\n".join(lines)


def main():
    args = list(sys.argv[1:])

    if not args or args[0] != "format":
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    platform = None
    input_path = None
    output_path = None
    profile_url = ""

    i = 1
    while i < len(args):
        if args[i] == "--platform" and i + 1 < len(args):
            platform = args[i + 1]
            i += 2
        elif args[i] == "--input" and i + 1 < len(args):
            input_path = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        elif args[i] == "--url" and i + 1 < len(args):
            profile_url = args[i + 1]
            i += 2
        else:
            i += 1

    if not platform or not input_path:
        print("--platform and --input are required", file=sys.stderr)
        sys.exit(1)

    posts = json.loads(Path(input_path).read_text())

    md = format_platform_index(platform, posts, profile_url)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(md)
        print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/hormozi-scrape.py
git commit -m "feat: add social platform scraper formatter for Hormozi research"
```

---

### Task 5: Scrape acquisition.com blog

**Files:**
- Create: `docs/research/hormozi/content-index-blog.md`

This task uses Playwright MCP (Claude browser automation) — no script needed.

- [ ] **Step 1: Navigate to acquisition.com blog/resources**

Use Playwright MCP to navigate to `https://www.acquisition.com/blog` (or similar resource page). Take a snapshot to see the page structure.

- [ ] **Step 2: Extract blog post titles, URLs, and dates**

Use Playwright `browser_evaluate` to extract all article links and metadata from the page. Paginate through all pages if needed.

- [ ] **Step 3: Write blog index**

Format extracted data into `docs/research/hormozi/content-index-blog.md` with title, URL, date, and topic columns.

- [ ] **Step 4: Commit**

```bash
git add docs/research/hormozi/content-index-blog.md
git commit -m "feat: index acquisition.com blog posts"
```

---

### Task 6: Scrape Instagram profile (interactive)

**Files:**
- Create: `docs/research/hormozi/content-index-instagram.md`

- [ ] **Step 1: Navigate to Instagram profile**

Use Playwright MCP to navigate to `https://www.instagram.com/hormozi/`. If login wall appears, prompt Mike to log in manually.

- [ ] **Step 2: Scroll and extract post data**

Use Playwright to scroll the profile grid, capturing post metadata (type, caption preview, like count, comment count). Extract at least the top 100 posts by engagement.

- [ ] **Step 3: Format and save**

Save extracted data to JSON, then format with:
```bash
python scripts/hormozi-scrape.py format --platform instagram --input /tmp/hormozi-ig.json --output docs/research/hormozi/content-index-instagram.md --url "https://www.instagram.com/hormozi/"
```

- [ ] **Step 4: Commit**

```bash
git add docs/research/hormozi/content-index-instagram.md
git commit -m "feat: index Hormozi Instagram posts"
```

---

### Task 7: Scrape X/Twitter profile (interactive)

**Files:**
- Create: `docs/research/hormozi/content-index-x.md`

- [ ] **Step 1: Navigate to X profile**

Use Playwright MCP to navigate to `https://x.com/AlexHormozi`. If login wall appears, prompt Mike to log in.

- [ ] **Step 2: Scroll and extract top tweets**

Extract tweet text, retweet count, like count, reply count, date. Focus on top-performing tweets. Extract at least top 100.

- [ ] **Step 3: Format and save**

```bash
python scripts/hormozi-scrape.py format --platform x --input /tmp/hormozi-x.json --output docs/research/hormozi/content-index-x.md --url "https://x.com/AlexHormozi"
```

- [ ] **Step 4: Commit**

```bash
git add docs/research/hormozi/content-index-x.md
git commit -m "feat: index Hormozi X/Twitter posts"
```

---

### Task 8: Scrape LinkedIn profile (interactive)

**Files:**
- Create: `docs/research/hormozi/content-index-linkedin.md`

- [ ] **Step 1: Navigate to LinkedIn profile**

Use Playwright MCP to navigate to `https://www.linkedin.com/in/alexhormozi/` (or search for Alex Hormozi). Login required — prompt Mike.

- [ ] **Step 2: Navigate to Posts tab and extract**

Click "Posts" tab, scroll and extract post text, reaction count, comment count, date. Get at least top 50.

- [ ] **Step 3: Format and save**

```bash
python scripts/hormozi-scrape.py format --platform linkedin --input /tmp/hormozi-li.json --output docs/research/hormozi/content-index-linkedin.md --url "https://www.linkedin.com/in/alexhormozi/"
```

- [ ] **Step 4: Commit**

```bash
git add docs/research/hormozi/content-index-linkedin.md
git commit -m "feat: index Hormozi LinkedIn posts"
```

---

### Task 9: Scrape TikTok profile (interactive)

**Files:**
- Create: `docs/research/hormozi/content-index-tiktok.md`

- [ ] **Step 1: Navigate to TikTok profile**

Use Playwright MCP to navigate to `https://www.tiktok.com/@hormozi`. Login may be required.

- [ ] **Step 2: Scroll and extract video metadata**

Extract caption, view count, like count, comment count, date. Focus on top videos by views.

- [ ] **Step 3: Format and save**

```bash
python scripts/hormozi-scrape.py format --platform tiktok --input /tmp/hormozi-tt.json --output docs/research/hormozi/content-index-tiktok.md --url "https://www.tiktok.com/@hormozi"
```

- [ ] **Step 4: Commit**

```bash
git add docs/research/hormozi/content-index-tiktok.md
git commit -m "feat: index Hormozi TikTok posts"
```

---

### Task 10: Build master content index

**Files:**
- Create: `docs/research/hormozi/content-index.md`

- [ ] **Step 1: Create master index that links to all platform indices**

Write `docs/research/hormozi/content-index.md` that:
- Summarizes total content count per platform
- Links to each platform-specific index file
- Lists the top 30 Phase 2 candidates across ALL platforms (curated from each platform's top performers)
- Includes selection rationale based on: engagement-to-age ratio, framework density, relevance to agency → brand → info → SaaS path

```markdown
# Alex Hormozi — Master Content Index

**Indexed:** 2026-03-30
**Total content pieces:** [sum across platforms]

## Platform Breakdown

| Platform | Posts Indexed | Top Performer Views | Index File |
|----------|-------------|--------------------|-----------|
| YouTube (main) | X | Y | [content-index-youtube.md](content-index-youtube.md) |
| YouTube (clips) | X | Y | [content-index-youtube-clips.md](content-index-youtube-clips.md) |
| Instagram | X | Y | [content-index-instagram.md](content-index-instagram.md) |
| X/Twitter | X | Y | [content-index-x.md](content-index-x.md) |
| LinkedIn | X | Y | [content-index-linkedin.md](content-index-linkedin.md) |
| TikTok | X | Y | [content-index-tiktok.md](content-index-tiktok.md) |
| Blog | X | N/A | [content-index-blog.md](content-index-blog.md) |
| Books | 2 | N/A | N/A (manual) |

## Phase 2 Deep Dive Candidates

### Priority 1 — Must Transcribe/Analyze (15-20 pieces)

[Curated list with rationale for each pick]

### Priority 2 — If Time Permits

[Secondary list]
```

- [ ] **Step 2: Commit**

```bash
git add docs/research/hormozi/content-index.md
git commit -m "feat: create master Hormozi content index with Phase 2 picks"
```

---

## Phase 2: Deep Dive the Best

### Task 11: Transcribe top YouTube videos

**Files:**
- Create: `docs/research/hormozi/transcripts/yt-{video-id}.md` (one per video)

- [ ] **Step 1: Select top 10 YouTube videos from Phase 2 candidates**

Review `docs/research/hormozi/content-index.md` Phase 2 candidates. Pick the 10 YouTube videos with highest framework density (not just views — prefer "How to create an irresistible offer" over "I'm worth $100M").

- [ ] **Step 2: Transcribe each video using /transcribe skill**

For each video, run:
```
/transcribe https://www.youtube.com/watch?v={VIDEO_ID}
```

Save each transcript to `docs/research/hormozi/transcripts/yt-{video-id}.md` with header:
```markdown
# [Video Title]

**URL:** https://www.youtube.com/watch?v={id}
**Views:** X | **Duration:** Y | **Date:** Z
**Topics:** [from index]

---

[transcript content]
```

- [ ] **Step 3: Commit after each batch of 3-5 transcripts**

```bash
git add docs/research/hormozi/transcripts/
git commit -m "feat: transcribe top Hormozi YouTube videos (batch N)"
```

---

### Task 12: Transcribe top podcast episodes

**Files:**
- Create: `docs/research/hormozi/transcripts/pod-{id}.md` (one per episode)

- [ ] **Step 1: Select 3-5 podcast episodes from Phase 2 candidates**

Pick episodes that cover deep business strategy (not interviews with guests — Hormozi solo episodes or ones where he teaches).

- [ ] **Step 2: Transcribe each episode**

Use `/transcribe` on the YouTube version of each podcast episode.

Save to `docs/research/hormozi/transcripts/pod-{id}.md` with same header format.

- [ ] **Step 3: Commit**

```bash
git add docs/research/hormozi/transcripts/
git commit -m "feat: transcribe top Hormozi podcast episodes"
```

---

### Task 13: Analyze each transcribed piece

**Files:**
- Create: `docs/research/hormozi/analyses/yt-{video-id}-analysis.md` (one per piece)

- [ ] **Step 1: For each transcript, create an analysis document**

Read the transcript and extract into this structure:

```markdown
# Analysis: [Video Title]

**Source:** [URL]
**Key Topic:** [primary topic]

## Core Frameworks

[Named frameworks Hormozi presents — e.g., "Value Equation: Dream Outcome × Perceived Likelihood / Time Delay × Effort & Sacrifice"]

## Actionable Tactics

[Specific, numbered tactics with benchmarks where given]

## Key Quotes

[Memorable one-liners and quotable moments]

## Case Studies & Examples

[Stories and examples he uses to illustrate points]

## Content Structure Notes

[How this video is structured — hook style, transitions, pacing, CTA]
```

- [ ] **Step 2: Commit after each batch of analyses**

```bash
git add docs/research/hormozi/analyses/
git commit -m "feat: analyze Hormozi content (batch N)"
```

---

### Task 14: Book analysis — $100M Offers

**Files:**
- Create: `docs/research/hormozi/analyses/book-100m-offers.md`

- [ ] **Step 1: Create comprehensive book analysis**

Use publicly available summaries, Hormozi's own video explanations of book concepts, and Mike's notes (if provided) to create:

```markdown
# Book Analysis: $100M Offers — Alex Hormozi

## Core Thesis
[One paragraph]

## Key Frameworks

### 1. The Value Equation
Dream Outcome × Perceived Likelihood of Achievement / Time Delay × Effort & Sacrifice = Value

[Detailed breakdown with examples]

### 2. Grand Slam Offer
[Framework + how to apply]

### 3. [Continue for all major frameworks]

## Chapter-by-Chapter Key Takeaways
[Condensed takeaways per chapter]

## Application to Agency Model
[How Mike can apply these frameworks to starting an agency]
```

- [ ] **Step 2: Commit**

```bash
git add docs/research/hormozi/analyses/book-100m-offers.md
git commit -m "feat: analyze $100M Offers frameworks"
```

---

### Task 15: Book analysis — $100M Leads

**Files:**
- Create: `docs/research/hormozi/analyses/book-100m-leads.md`

- [ ] **Step 1: Create comprehensive book analysis**

Same structure as Task 14 but for $100M Leads. Key frameworks to extract:
- The 4 Core Lead Generation Methods (warm outreach, cold outreach, content, paid ads)
- The Lead Generation Framework
- Core Four advertising methods
- How to get engaged leads vs strangers
- Give-to-ask ratio

- [ ] **Step 2: Commit**

```bash
git add docs/research/hormozi/analyses/book-100m-leads.md
git commit -m "feat: analyze $100M Leads frameworks"
```

---

## Phase 3: Synthesize

### Task 16: Write business playbook

**Files:**
- Create: `docs/research/hormozi/hormozi-business-playbook.md`

- [ ] **Step 1: Read all analysis files**

Read every file in `docs/research/hormozi/analyses/` to have full context.

- [ ] **Step 2: Write the playbook**

Organize ALL extracted frameworks by Mike's business stages:

```markdown
# Alex Hormozi Business Playbook

**Purpose:** Actionable frameworks for building from zero → agency → brand → info products → SaaS.
**Based on:** [list of all analyzed sources]

---

## Stage 1: Starting an Agency (Trade Time for Money)

### Creating Your Offer
[Value Equation, Grand Slam Offer framework, pricing]

### Getting Leads
[From $100M Leads — warm outreach first, then cold, then content, then paid]

### Closing Sales
[CLOSER framework, objection handling]

### Delivering & Retaining
[Fulfillment, reducing churn, increasing LTV]

### Hiring Your First Team
[When to hire, who to hire first, how to manage]

---

## Stage 2: Building a Personal Brand

### Why Content
[Hormozi's thesis on content as a lead gen machine]

### What to Post
[Content categories, framework density vs entertainment]

### Platform Strategy
[His multi-platform approach and repurposing]

---

## Stage 3: Info Products, Coaching & Community

### Course Creation
[How he structures educational content]

### Coaching Models
[1:1 vs group, pricing tiers]

### Community (Skool)
[His Skool playbook, engagement mechanics]

---

## Stage 4: SaaS & Portfolio

### Pattern Recognition
[How to spot SaaS opportunities from service delivery]

### When to Build
[His criteria for building vs buying]

---

## Cross-Cutting Frameworks

### Mindset
[Key mental models]

### Decision Making
[How he thinks about time, money, leverage]

### Compounding
[His philosophy on consistency and long-term thinking]
```

- [ ] **Step 3: Commit**

```bash
git add docs/research/hormozi/hormozi-business-playbook.md
git commit -m "feat: write Hormozi business playbook"
```

---

### Task 17: Write content strategy analysis

**Files:**
- Create: `docs/research/hormozi/hormozi-content-strategy.md`

- [ ] **Step 1: Analyze his content machine from the indexed data + transcripts**

Study the posting patterns from Phase 1 index (cadence, platform mix, format distribution) and content structure from Phase 2 analyses.

- [ ] **Step 2: Write content strategy document**

```markdown
# Alex Hormozi Content Strategy Analysis

## The Machine
[Team structure, production pipeline, repurposing flow]
[What he does: 1 long-form → many short-form across platforms]

## Posting Cadence
[Frequency per platform based on indexed data]

## Content Formula
[Hook patterns, script structures, CTA patterns]

## What Works (Data-Driven)
[Top-performing content types from index data]
[Topics that get most engagement]
[Format patterns — length, style]

## Platform-Specific Tactics
[Per-platform observations]

## Solo Creator Adaptation
[What Mike can replicate without a team]
[Minimum viable content machine]
[Recommended starting cadence]
```

- [ ] **Step 3: Commit**

```bash
git add docs/research/hormozi/hormozi-content-strategy.md
git commit -m "feat: write Hormozi content strategy analysis"
```

---

### Task 18: Write style guide

**Files:**
- Create: `docs/research/hormozi/hormozi-style-guide.md`

- [ ] **Step 1: Write style guide (same format as Ray Fu guide)**

Reference `docs/research/2026-03-28-raycfu-style-guide.md` for the format template. Create equivalent analysis for Hormozi:

```markdown
# Alex Hormozi — Style Guide

## Voice & Tone
[Direct, authoritative, uses profanity strategically, storytelling-heavy]

## Speaking Style
[Pace, energy, word choice patterns, signature phrases]

## Script Architecture
[Hook → Setup → Framework → Examples → CTA]
[How he structures different content lengths]

## Hook Templates
[Extracted hook formulas with examples from transcripts]

## CTA Patterns
[How he drives engagement — comments, follows, book purchases]

## Visual Style
[Thumbnail patterns, editing style, on-screen text]

## Anti-Patterns
[What to avoid — what doesn't work in his style]

## Style Checklist
[Quick checklist for creating Hormozi-influenced content]
```

- [ ] **Step 2: Commit**

```bash
git add docs/research/hormozi/hormozi-style-guide.md
git commit -m "feat: write Hormozi style guide"
```

---

### Task 19: Create Obsidian knowledge summary

**Files:**
- Create: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/knowledge/hormozi.md`

- [ ] **Step 1: Write mobile-friendly summary**

```markdown
---
updated: 2026-03-30
---

# Alex Hormozi — Key Frameworks

Quick reference. Full research: `~/Projects/content/docs/research/hormozi/`

## Business Stages Playbook
[Condensed 1-2 line summaries of each framework per stage]

## Top Quotes
[10 best one-liners]

## Content Strategy TL;DR
[5 bullet points on his content machine]

## Books
- $100M Offers: [one-line summary]
- $100M Leads: [one-line summary]
```

- [ ] **Step 2: Commit content project files**

```bash
cd ~/Projects/content
git add docs/research/hormozi/
git commit -m "feat: complete Hormozi research Phase 3 synthesis"
```

---

## Task Dependencies

```
Task 1 (dirs) → Task 2 (YT indexer) → Task 3 (YT clips)
Task 1 → Task 4 (scraper script)
Task 4 → Tasks 5-9 (platform scraping, can run in parallel)
Tasks 2,3,5-9 → Task 10 (master index)
Task 10 → Tasks 11-15 (deep dives, can run in parallel)
Tasks 11-15 → Tasks 16-18 (synthesis, sequential)
Task 18 → Task 19 (Obsidian summary)
```

**Parallelization opportunities:**
- Tasks 5-9 (platform scraping) can run in parallel via subagents
- Tasks 11-12 (transcription) can run in parallel
- Tasks 14-15 (book analyses) can run in parallel
