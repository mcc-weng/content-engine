# Content Insight Extraction System — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatically extract content-worthy insights from Claude Code conversations into an Obsidian content log.

**Architecture:** A Python script extracts human/assistant messages from JSONL conversation files, pipes them to `claude` CLI for insight extraction, and appends structured results to an Obsidian markdown file. A cron job runs this daily. A CLAUDE.md instruction enables inline flagging and manual `/content` capture.

**Tech Stack:** Python 3, claude CLI, cron, markdown

---

### Task 1: Create the conversation extractor script

**Files:**
- Create: `~/Desktop/Projects/personal/scripts/extract-conversations.py`

**Step 1: Write the Python script**

This script:
- Finds all JSONL conversation files across `~/.claude/projects/`
- Filters to files modified today (or a given date)
- Extracts `user` and `assistant` text messages (skipping tool calls, thinking, progress, system)
- Outputs a clean transcript per conversation
- Accepts `--date YYYY-MM-DD` flag (defaults to today)
- Accepts `--all` flag for backfill mode (processes all conversations)
- Skips session IDs already listed in a state file at `~/.claude/content-extraction-state.json`

```python
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
        # Skip subagent conversations
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

        if not messages or len(messages) < 4:  # Skip trivial conversations
            continue

        if session_id in processed_ids:
            continue

        # Output transcript with metadata
        mod_date = datetime.fromtimestamp(jsonl_path.stat().st_mtime).strftime("%Y-%m-%d")
        print(f"=== SESSION: {session_id} | PROJECT: {project} | DATE: {mod_date} ===")
        for msg in messages:
            print(msg)
        print(f"=== END SESSION ===\n")

        new_processed.add(session_id)

    # Update state file with newly processed IDs
    if new_processed:
        all_processed = processed_ids | new_processed
        save_processed_ids(all_processed)


if __name__ == "__main__":
    main()
```

**Step 2: Make it executable and test**

Run: `chmod +x ~/Desktop/Projects/personal/scripts/extract-conversations.py`
Run: `python3 ~/Desktop/Projects/personal/scripts/extract-conversations.py --date 2026-03-06 | head -50`
Expected: Clean USER/ASSISTANT transcript output from March 6 conversations.

**Step 3: Commit**

```bash
cd ~/Desktop/Projects/personal
git add scripts/extract-conversations.py
git commit -m "feat: add conversation extractor script for content insights"
```

---

### Task 2: Create the insight extraction wrapper script

**Files:**
- Create: `~/Desktop/Projects/personal/scripts/extract-content-insights.sh`

**Step 1: Write the shell script**

This script:
- Runs the Python extractor
- Pipes output to `claude` CLI with a prompt to identify content-worthy insights
- Appends output to the Obsidian content log
- Accepts `--all` for backfill, `--date` for specific date

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTENT_LOG="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md"
EXTRACTOR="$SCRIPT_DIR/extract-conversations.py"

DATE_FLAG=""
ALL_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --date) DATE_FLAG="--date $2"; shift 2 ;;
        --all) ALL_FLAG="--all"; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# Extract conversations
TRANSCRIPTS=$(python3 "$EXTRACTOR" $DATE_FLAG $ALL_FLAG)

if [ -z "$TRANSCRIPTS" ]; then
    echo "No new conversations to process."
    exit 0
fi

# Create content log if it doesn't exist
if [ ! -f "$CONTENT_LOG" ]; then
    echo "# Content Log" > "$CONTENT_LOG"
    echo "" >> "$CONTENT_LOG"
fi

PROMPT=$(cat <<'PROMPT_EOF'
You are a content strategist analyzing Claude Code conversation transcripts. Extract content-worthy insights for short-form video and Twitter threads.

Target audience: Mixed — non-technical people discovering AI + developers learning Claude Code.

For each insight, use EXACTLY this format (output raw markdown, no code fences):

1. **Short description**
   - Context: What happened, backstory, key details
   - Hook: "The scroll-stopping one-liner"
   - Angle: Why the audience cares / takeaway
   - Format: short-form | thread | long-form
   - Category: struggle | aha | decision | hot-take | authority
   - [ ] Posted

Categories:
1. Struggle moments — things that went wrong or were harder than expected
2. Aha moments — discoveries, clever solutions, unexpected wins
3. Decision points — choices others will face too
4. Hot takes — strong reactions to how something works
5. Authority builders — things built/solved that demonstrate expertise

Rules:
- Only extract genuinely interesting moments (would someone stop scrolling for this?)
- Skip mundane debugging, routine file edits, or boilerplate conversations
- Group by date using ## YYYY-MM-DD headings
- Add a ### Themes section per date if patterns emerge
- Output ONLY the formatted insights, nothing else
- If no insights found, output "No content-worthy insights found."
PROMPT_EOF
)

# Send to claude CLI for analysis
INSIGHTS=$(echo "$TRANSCRIPTS" | claude --print --dangerously-skip-permissions "$PROMPT")

if [ "$INSIGHTS" = "No content-worthy insights found." ]; then
    echo "No content-worthy insights found."
    exit 0
fi

# Append to content log
echo "" >> "$CONTENT_LOG"
echo "$INSIGHTS" >> "$CONTENT_LOG"

echo "Content insights appended to $CONTENT_LOG"
```

**Step 2: Make it executable and test with a single date**

Run: `chmod +x ~/Desktop/Projects/personal/scripts/extract-content-insights.sh`
Run: `~/Desktop/Projects/personal/scripts/extract-content-insights.sh --date 2026-03-05`
Expected: Insights appended to the Obsidian content log.

**Step 3: Verify the content log**

Run: `cat "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md"`
Expected: Formatted insights matching the design spec format.

**Step 4: Commit**

```bash
cd ~/Desktop/Projects/personal
git add scripts/extract-content-insights.sh
git commit -m "feat: add insight extraction wrapper using claude CLI"
```

---

### Task 3: Set up the daily cron job

**Step 1: Add cron entry**

```bash
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/bin/env bash $HOME/Desktop/Projects/personal/scripts/extract-content-insights.sh >> $HOME/Desktop/Projects/personal/scripts/extract-content.log 2>&1") | crontab -
```

This runs at midnight daily, logs output to `extract-content.log`.

**Step 2: Verify cron is set**

Run: `crontab -l`
Expected: See the new entry alongside the existing CourtBooking cron.

**Step 3: Commit**

```bash
cd ~/Desktop/Projects/personal
git add scripts/
git commit -m "feat: add daily cron for content insight extraction"
```

---

### Task 4: Create the content-log.md with initial structure

**Files:**
- Create: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`

**Step 1: Create the initial file**

```markdown
# Content Log

Automatically extracted insights from Claude Code conversations.
Content-worthy moments for short-form video, Twitter threads, and long-form content.

---

```

**Step 2: Verify it exists in Obsidian vault**

Run: `ls -la "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md"`
Expected: File exists.

---

### Task 5: Add inline flagging and /content support via CLAUDE.md

**Files:**
- Modify: `~/.claude/CLAUDE.md`

**Step 1: Add content instructions to global CLAUDE.md**

Append the following section:

```markdown
## Content Insight Capture

### Inline Flagging (Experimental)
When you notice a content-worthy moment during a conversation — a struggle, aha moment, interesting decision, hot take, or something that demonstrates expertise — briefly flag it in one line like:
> Content-worthy: [brief description of the moment]

Keep it to one line max. Don't interrupt flow. If Mike says to stop, stop.

### Manual Capture (/content)
When Mike says "/content" or "log that", capture the current moment as a content insight and append it to:
`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`

Use this format:
1. **Short description**
   - Context: What happened, backstory, key details
   - Hook: "The scroll-stopping one-liner"
   - Angle: Why the audience cares / takeaway
   - Format: short-form | thread | long-form
   - Category: struggle | aha | decision | hot-take | authority
   - [ ] Posted

Append under the current date heading (## YYYY-MM-DD). Create the heading if it doesn't exist.
```

**Step 2: Verify**

Run: `cat ~/.claude/CLAUDE.md` and confirm the section was appended.

**Step 3: Commit**

```bash
cd ~/Desktop/Projects/personal
git add ~/.claude/CLAUDE.md
git commit -m "feat: add content capture instructions to CLAUDE.md"
```

---

### Task 6: One-time backfill of all existing conversations

**Step 1: Run backfill**

Run: `~/Desktop/Projects/personal/scripts/extract-content-insights.sh --all`

Note: This processes ~135 conversations. It will take a few minutes and use a meaningful amount of Claude CLI tokens. The transcripts may be large, so the script sends them all at once to claude CLI. If it's too large, we may need to batch by project or date.

**Step 2: Review the content log**

Run: `cat "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md"`
Expected: Insights organized by date from across all projects.

**Step 3: Manual review**

Skim the output and remove any low-quality or irrelevant entries. The AI won't be perfect — this is a starting point.

---

### Task 7: Test end-to-end flow

**Step 1: Verify daily extraction works**

Run: `~/Desktop/Projects/personal/scripts/extract-content-insights.sh --date 2026-03-07`
Expected: Today's conversation insights appended to content log (including this brainstorming session — which is itself content-worthy).

**Step 2: Test /content manual capture**

In a Claude Code session, say "/content" and verify it appends to the log.

**Step 3: Test inline flagging**

Verify Claude flags content-worthy moments in the current session without being disruptive.

---
