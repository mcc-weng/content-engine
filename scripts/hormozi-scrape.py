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
