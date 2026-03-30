#!/usr/bin/env python3
"""Extract human/assistant messages from Claude Code conversation JSONL files."""

import json
import os
import re
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
STATE_FILE = Path.home() / ".claude" / "content-extraction-state.json"


def load_state():
    """Load state file, migrating from old format if needed."""
    if not STATE_FILE.exists():
        return {}
    data = json.loads(STATE_FILE.read_text())
    # Migrate old format: {"processed": ["id1", ...]}
    if "processed" in data:
        migrated = {}
        for sid in data["processed"]:
            migrated[sid] = {"bytes_processed": 0, "insights": []}
        save_state(migrated)
        return migrated
    return data.get("sessions", {})


def save_state(sessions):
    STATE_FILE.write_text(json.dumps({"sessions": sessions}, indent=2))


def extract_messages(jsonl_path):
    """Extract user/assistant text messages from a JSONL file.

    Filters out tool_result blocks, image blocks, and progress messages
    to keep only the human conversation and assistant reasoning.
    """
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
                elif isinstance(content, list):
                    # Extract only human-typed text, skip tool_result/image blocks
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "").strip()
                            if text:
                                messages.append(f"USER: {text}")
                        elif isinstance(block, str) and block.strip():
                            messages.append(f"USER: {block.strip()}")

            elif msg_type == "assistant":
                content = obj.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "").strip()
                            if text:
                                messages.append(f"ASSISTANT: {text}")
                        # Skip tool_use blocks — no content value for insights
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


def has_new_content(jsonl_path, session_id, state):
    """Check if file has grown since last processing."""
    current_bytes = jsonl_path.stat().st_size
    stored_bytes = state.get(session_id, {}).get("bytes_processed", 0)
    return current_bytes > stored_bytes, current_bytes


def list_changed_sessions(target_date, state):
    """Return list of sessions with new content."""
    convos = get_conversations(target_date, process_all=target_date is None)
    changed = []
    for jsonl_path in convos:
        session_id, project, messages = extract_messages(jsonl_path)
        if not messages or len(messages) < 4:
            continue
        has_new, current_bytes = has_new_content(jsonl_path, session_id, state)
        if not has_new:
            continue
        changed.append({
            "session_id": session_id,
            "path": str(jsonl_path),
            "project": project,
            "current_bytes": current_bytes,
            "date": datetime.fromtimestamp(jsonl_path.stat().st_mtime).strftime("%Y-%m-%d"),
        })
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Date to process (YYYY-MM-DD). If omitted, scans all files.")
    parser.add_argument("--all", action="store_true", help="(deprecated, now default) Process all conversations")
    parser.add_argument("--skip-processed", action="store_true", default=True)
    parser.add_argument("--list-changed", action="store_true", help="Output JSON array of sessions with new content")
    parser.add_argument("--extract-session", metavar="PATH", help="Output full transcript for a single session JSONL file")
    parser.add_argument("--get-insights", metavar="SESSION_ID", help="Output previously extracted insights for a session")
    parser.add_argument("--update-state", nargs=2, metavar=("SESSION_ID", "BYTES"), help="Read insights from stdin and update state")
    args = parser.parse_args()

    state = load_state()

    # --list-changed mode
    if args.list_changed:
        target_date = None  # default: scan all files
        if args.date:
            target_date = date.fromisoformat(args.date)
        changed = list_changed_sessions(target_date, state)
        print(json.dumps(changed, indent=2))
        return

    # --extract-session mode
    if args.extract_session:
        jsonl_path = Path(args.extract_session)
        if not jsonl_path.exists():
            print(f"Error: {jsonl_path} not found", file=sys.stderr)
            sys.exit(1)
        session_id, project, messages = extract_messages(jsonl_path)
        if not messages:
            print(f"Error: no messages found in {jsonl_path}", file=sys.stderr)
            sys.exit(1)
        mod_date = datetime.fromtimestamp(jsonl_path.stat().st_mtime).strftime("%Y-%m-%d")
        print(f"=== SESSION: {session_id} | PROJECT: {project} | DATE: {mod_date} ===")
        for msg in messages:
            print(msg)
        print(f"=== END SESSION ===")
        return

    # --get-insights mode
    if args.get_insights:
        session_id = args.get_insights
        insights = state.get(session_id, {}).get("insights", [])
        if insights:
            print("\n".join(insights))
        return

    # --update-state mode
    if args.update_state:
        session_id, bytes_str = args.update_state
        new_insights_text = sys.stdin.read().strip()
        # Parse insights from formatted output — split on numbered entries
        new_insights = []
        if new_insights_text:
            entries = re.split(r'\n(?=\d+\. \*\*)', new_insights_text)
            new_insights = [e.strip() for e in entries if e.strip()]
        # Combine with existing insights
        existing_insights = state.get(session_id, {}).get("insights", [])
        state[session_id] = {
            "bytes_processed": int(bytes_str),
            "insights": existing_insights + new_insights,
        }
        save_state(state)
        return

    # Default mode: extract and print transcripts (backward compat)
    target_date = date.today()
    if args.date:
        target_date = date.fromisoformat(args.date)

    convos = get_conversations(target_date if not args.all else None, process_all=args.all)

    new_processed = {}
    for jsonl_path in convos:
        session_id, project, messages = extract_messages(jsonl_path)

        if not messages or len(messages) < 4:
            continue

        if session_id in state:
            has_new, current_bytes = has_new_content(jsonl_path, session_id, state)
            if not has_new:
                continue

        mod_date = datetime.fromtimestamp(jsonl_path.stat().st_mtime).strftime("%Y-%m-%d")
        print(f"=== SESSION: {session_id} | PROJECT: {project} | DATE: {mod_date} ===")
        for msg in messages:
            print(msg)
        print(f"=== END SESSION ===\n")

        current_bytes = jsonl_path.stat().st_size
        existing_insights = state.get(session_id, {}).get("insights", [])
        new_processed[session_id] = {
            "bytes_processed": current_bytes,
            "insights": existing_insights,
        }

    if new_processed:
        state.update(new_processed)
        save_state(state)


if __name__ == "__main__":
    main()
