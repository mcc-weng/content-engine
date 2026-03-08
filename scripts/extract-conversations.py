#!/usr/bin/env python3
"""Extract human/assistant messages from Claude Code conversation JSONL files."""

import json
import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
STATE_FILE = Path.home() / ".claude" / "content-extraction-state.json"


def load_processed_ids():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()).get("processed", []))
    return set()


def save_processed_ids(ids):
    STATE_FILE.write_text(json.dumps({"processed": sorted(ids)}, indent=2))


def extract_messages(jsonl_path):
    """Extract user/assistant text messages from a JSONL file."""
    messages = []
    session_id = None
    project = jsonl_path.parent.name

    with open(jsonl_path) as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not session_id:
                session_id = obj.get("sessionId")

            msg_type = obj.get("type")

            if msg_type == "user":
                content = obj.get("message", {}).get("content", "")
                if isinstance(content, str) and content.strip():
                    messages.append(f"USER: {content.strip()}")

            elif msg_type == "assistant":
                content = obj.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "").strip()
                            if text:
                                messages.append(f"ASSISTANT: {text}")
                elif isinstance(content, str) and content.strip():
                    messages.append(f"ASSISTANT: {content.strip()}")

    return session_id, project, messages


def get_conversations(target_date=None, process_all=False):
    """Find conversation JSONL files, optionally filtered by date."""
    convos = []
    for jsonl_path in PROJECTS_DIR.rglob("*.jsonl"):
        if "subagents" in str(jsonl_path):
            continue

        if not process_all and target_date:
            mod_time = datetime.fromtimestamp(jsonl_path.stat().st_mtime).date()
            if mod_time != target_date:
                continue

        convos.append(jsonl_path)

    return sorted(convos, key=lambda p: p.stat().st_mtime)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Date to process (YYYY-MM-DD), defaults to today")
    parser.add_argument("--all", action="store_true", help="Process all conversations (backfill)")
    parser.add_argument("--skip-processed", action="store_true", default=True)
    args = parser.parse_args()

    target_date = date.today()
    if args.date:
        target_date = date.fromisoformat(args.date)

    processed_ids = load_processed_ids() if args.skip_processed else set()
    convos = get_conversations(target_date if not args.all else None, process_all=args.all)

    new_processed = set()
    for jsonl_path in convos:
        session_id, project, messages = extract_messages(jsonl_path)

        if not messages or len(messages) < 4:
            continue

        if session_id in processed_ids:
            continue

        mod_date = datetime.fromtimestamp(jsonl_path.stat().st_mtime).strftime("%Y-%m-%d")
        print(f"=== SESSION: {session_id} | PROJECT: {project} | DATE: {mod_date} ===")
        for msg in messages:
            print(msg)
        print(f"=== END SESSION ===\n")

        new_processed.add(session_id)

    if new_processed:
        all_processed = processed_ids | new_processed
        save_processed_ids(all_processed)


if __name__ == "__main__":
    main()
