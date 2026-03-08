# Incremental Content Extraction Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make content extraction incremental — re-process growing conversations without duplicating insights, and skip unchanged ones.

**Architecture:** Change state tracking from a flat list of processed session IDs to per-session records storing bytes_processed and previously extracted insights. The shell script loops per-session instead of batching, sending full transcript + previous insights to Claude with dedup instructions. Both cron and `/log-content` use the same logic.

**Tech Stack:** Python 3, Bash, Claude CLI (`claude --print`)

---

### Task 1: Migrate State File Format

**Files:**
- Modify: `scripts/extract-conversations.py`

**Step 1: Update state file load/save functions**

Replace the current flat list format:
```json
{"processed": ["id1", "id2"]}
```

With per-session records:
```json
{
  "sessions": {
    "session-id": {
      "bytes_processed": 12345,
      "insights": [
        "1. **Title**\n   - Context: ...\n   - Hook: ...\n   - Angle: ...\n   - Format: ...\n   - Category: ...\n   - [ ] Posted"
      ]
    }
  }
}
```

Replace `load_processed_ids` and `save_processed_ids` with:

```python
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
```

**Step 2: Run migration manually to verify**

```bash
python3 -c "
from scripts.extract_conversations import load_state
state = load_state()
print(f'Migrated {len(state)} sessions')
print(list(state.values())[0])
"
```

Expected: 65 sessions migrated, each with `bytes_processed: 0` and `insights: []`.

**Step 3: Commit**

```bash
git add scripts/extract-conversations.py
git commit -m "feat: migrate state file to per-session format with bytes tracking"
```

---

### Task 2: Add Incremental Change Detection to Python Script

**Files:**
- Modify: `scripts/extract-conversations.py`

**Step 1: Replace session skip logic with size-based change detection**

Replace the current main() function's processing loop. Instead of checking `if session_id in processed_ids: continue`, check if the file has grown:

```python
def has_new_content(jsonl_path, session_id, state):
    """Check if conversation has new content since last processing."""
    current_bytes = jsonl_path.stat().st_size
    if session_id not in state:
        return True, current_bytes
    stored_bytes = state[session_id].get("bytes_processed", 0)
    if current_bytes > stored_bytes:
        return True, current_bytes
    return False, current_bytes
```

**Step 2: Add `--list-changed` mode**

Add a new mode that outputs JSON metadata for sessions with new content (used by the shell script to loop):

```python
def list_changed_sessions(target_date, process_all, state):
    """Output JSON array of sessions with new content."""
    convos = get_conversations(target_date if not process_all else None, process_all=process_all)
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
```

**Step 3: Add `--extract-session PATH` mode**

Outputs full transcript for a single session:

```python
# In main(), add argument:
parser.add_argument("--extract-session", help="Extract transcript from a single JSONL file")

# And handler:
if args.extract_session:
    session_id, project, messages = extract_messages(Path(args.extract_session))
    if messages:
        mod_date = datetime.fromtimestamp(Path(args.extract_session).stat().st_mtime).strftime("%Y-%m-%d")
        print(f"=== SESSION: {session_id} | PROJECT: {project} | DATE: {mod_date} ===")
        for msg in messages:
            print(msg)
        print(f"=== END SESSION ===")
    sys.exit(0)
```

**Step 4: Add `--get-insights SESSION_ID` mode**

Outputs previously extracted insights for a session:

```python
parser.add_argument("--get-insights", help="Get previously extracted insights for a session ID")

# Handler:
if args.get_insights:
    state = load_state()
    session_data = state.get(args.get_insights, {})
    insights = session_data.get("insights", [])
    for insight in insights:
        print(insight)
    sys.exit(0)
```

**Step 5: Add `--update-state` mode**

Updates state after processing. Reads new insights from stdin:

```python
parser.add_argument("--update-state", nargs=2, metavar=("SESSION_ID", "BYTES"),
                    help="Update state for a session after processing")

# Handler:
if args.update_state:
    session_id, bytes_str = args.update_state
    state = load_state()
    new_insights_text = sys.stdin.read().strip()
    # Parse insights from the formatted output — split on numbered entries
    new_insights = []
    if new_insights_text and new_insights_text != "No content-worthy insights found.":
        # Split on pattern like "\n\n1. " or "\n\n2. " etc
        import re
        entries = re.split(r'\n(?=\d+\. \*\*)', new_insights_text)
        new_insights = [e.strip() for e in entries if e.strip()]

    existing_insights = state.get(session_id, {}).get("insights", [])
    state[session_id] = {
        "bytes_processed": int(bytes_str),
        "insights": existing_insights + new_insights,
    }
    save_state(state)
    sys.exit(0)
```

**Step 6: Update main() to wire up `--list-changed`**

```python
parser.add_argument("--list-changed", action="store_true",
                    help="Output JSON of sessions with new content")

# In main body:
if args.list_changed:
    state = load_state()
    changed = list_changed_sessions(
        target_date if not args.all else None, args.all, state
    )
    print(json.dumps(changed))
    sys.exit(0)
```

**Step 7: Verify old `--date` mode still works (backward compat for any other callers)**

Keep the existing default behavior working but using new state format.

**Step 8: Commit**

```bash
git add scripts/extract-conversations.py
git commit -m "feat: add incremental modes — list-changed, extract-session, get-insights, update-state"
```

---

### Task 3: Rewrite Shell Script for Per-Session Processing

**Files:**
- Modify: `scripts/extract-content-insights.sh`

**Step 1: Replace the batch approach with per-session loop**

Rewrite the shell script:

```bash
#!/bin/bash
set -euo pipefail

# Allow running from within a Claude Code session or cron
unset CLAUDECODE 2>/dev/null || true

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

# Get sessions with new content
CHANGED=$(python3 "$EXTRACTOR" --list-changed $DATE_FLAG $ALL_FLAG)

# Check if any sessions need processing
SESSION_COUNT=$(echo "$CHANGED" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")

if [ "$SESSION_COUNT" = "0" ]; then
    echo "No new conversations to process."
    exit 0
fi

echo "Found $SESSION_COUNT session(s) with new content."

# Create content log if it doesn't exist
if [ ! -f "$CONTENT_LOG" ]; then
    echo "# Content Log" > "$CONTENT_LOG"
    echo "" >> "$CONTENT_LOG"
fi

# Process each session
echo "$CHANGED" | python3 -c "
import json, sys
sessions = json.load(sys.stdin)
for s in sessions:
    print(f\"{s['session_id']}|{s['path']}|{s['current_bytes']}|{s['date']}\")
" | while IFS='|' read -r SESSION_ID SESSION_PATH CURRENT_BYTES SESSION_DATE; do
    echo "Processing session $SESSION_ID ($SESSION_DATE)..."

    # Extract full transcript
    TRANSCRIPT=$(python3 "$EXTRACTOR" --extract-session "$SESSION_PATH")

    if [ -z "$TRANSCRIPT" ]; then
        echo "  Skipping — empty transcript."
        continue
    fi

    # Get previously extracted insights
    PREV_INSIGHTS=$(python3 "$EXTRACTOR" --get-insights "$SESSION_ID")

    # Build the prompt with dedup instructions
    if [ -n "$PREV_INSIGHTS" ]; then
        DEDUP_SECTION=$(cat <<DEDUP_EOF

PREVIOUSLY EXTRACTED INSIGHTS (do NOT re-extract these — only find NEW insights not covered below):

$PREV_INSIGHTS

END OF PREVIOUSLY EXTRACTED INSIGHTS.
DEDUP_EOF
        )
    else
        DEDUP_SECTION=""
    fi

    PROMPT=$(cat <<PROMPT_EOF
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
- If no NEW insights found, output exactly "No content-worthy insights found."
$DEDUP_SECTION
PROMPT_EOF
    )

    # Send to claude CLI for analysis
    INSIGHTS=$(echo "$TRANSCRIPT" | claude --print --dangerously-skip-permissions "$PROMPT")

    if [ "$INSIGHTS" = "No content-worthy insights found." ]; then
        echo "  No new insights found."
        # Still update bytes so we don't re-process unchanged content
        echo "" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES"
        continue
    fi

    # Append to content log
    echo "" >> "$CONTENT_LOG"
    echo "$INSIGHTS" >> "$CONTENT_LOG"

    # Update state with new insights and bytes
    echo "$INSIGHTS" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES"

    echo "  Insights appended to content log."
done

echo "Done."
```

**Step 2: Commit**

```bash
git add scripts/extract-content-insights.sh
git commit -m "feat: per-session processing with incremental dedup"
```

---

### Task 4: Update the `/log-content` Skill

**Files:**
- Modify: `~/.claude/skills/log-content/SKILL.md`

**Step 1: Update skill to reflect new behavior**

```markdown
---
name: log-content
description: Use when the user says /log-content, "log this", or asks to extract content insights from the current or recent Claude Code conversations into the content log.
---

# Log Content Insights

Extract content-worthy insights from Claude Code conversations and append them to the Obsidian content log.

## How It Works

The script processes conversations incrementally:
- Tracks how much of each conversation was previously processed (by file size)
- Sends the full conversation for context, but tells the LLM to skip already-extracted insights
- Only processes sessions that have grown since last run
- Both cron and manual `/log-content` use the same logic — no conflicts

## Steps

1. **Run the script:**
   ```bash
   cd ~/Desktop/Projects/content && bash scripts/extract-content-insights.sh --date YYYY-MM-DD
   ```
   Default to today's date. Use `--date` flag if user specifies a different date.

2. **Show the user what was extracted** by reading the tail of:
   `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`

3. **If "No new conversations to process"** — the current active session may not be saved to JSONL yet (still active), or all sessions are unchanged since last extraction.

## Key Paths

- Script: `~/Desktop/Projects/content/scripts/extract-content-insights.sh`
- Content log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`
- State file: `~/.claude/content-extraction-state.json`
```

**Step 2: Commit**

```bash
git add ~/.claude/skills/log-content/SKILL.md
git commit -m "docs: update log-content skill for incremental extraction"
```

---

### Task 5: End-to-End Testing

**Test all scenarios manually:**

**Scenario A: Brand new session (never processed)**

```bash
# Find a session ID not in state file, or create a short test conversation
# Run the script for that date
cd ~/Desktop/Projects/content && bash scripts/extract-content-insights.sh --date YYYY-MM-DD
# Verify: insights appended to content log
# Verify: state file has new entry with bytes_processed > 0 and insights populated
```

**Scenario B: Already processed session, unchanged**

```bash
# Run the script again for the same date
cd ~/Desktop/Projects/content && bash scripts/extract-content-insights.sh --date YYYY-MM-DD
# Verify: "No new conversations to process." (file size hasn't changed)
# Verify: state file unchanged
```

**Scenario C: Already processed session, has grown**

```bash
# This is the key scenario — simulated by the current active conversation
# The current session (16219b01...) was processed earlier today
# It has since grown (we kept talking)
# Run the script
cd ~/Desktop/Projects/content && bash scripts/extract-content-insights.sh --date 2026-03-09
# Verify: script detects file growth, re-processes
# Verify: sends full transcript + previous insights to LLM
# Verify: only NEW insights appended (not duplicates of the 5 already extracted)
# Verify: state file updated with new bytes and combined insights list
```

**Scenario D: Multiple sessions same day, mixed states**

```bash
# Verify script processes only changed sessions, skips unchanged ones
# Check output shows per-session status messages
```

**Scenario E: Cron after manual `/log-content`**

```bash
# Run /log-content manually
# Then run the cron script again
# Verify: cron skips sessions that haven't grown since /log-content ran
# Verify: no duplicate insights in content log
```

**Scenario F: State file migration from old format**

```bash
# Restore old format state file from backup
cp ~/.claude/content-extraction-state.json.bak ~/.claude/content-extraction-state.json
# Run script
# Verify: migrates to new format automatically
# Verify: all 65 sessions preserved with bytes_processed: 0
```

**Step: Commit test results / any fixes**

```bash
git add -A
git commit -m "test: verify all incremental extraction scenarios"
```
