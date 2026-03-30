#!/bin/bash
set -uo pipefail
# NOTE: NOT using set -e — we handle errors explicitly per-session
# so one failure doesn't kill the entire batch

# Allow running from within a Claude Code session or cron
unset CLAUDECODE 2>/dev/null || true
export USER="${USER:-$(whoami)}"

# Raise file descriptor limit (cron defaults to 256, claude needs more)
ulimit -n 2147483646 2>/dev/null || ulimit -n 10240 2>/dev/null || true

# Load auth for cron (keychain not accessible from cron)
CRED_FILE="$HOME/.claude/.credentials"
if [ -f "$CRED_FILE" ]; then
  export CLAUDE_CODE_OAUTH_TOKEN="$(tr -d '\n' < "$CRED_FILE")"
fi

# Guard: skip if too many claude sessions already running (rate limit protection)
MAX_SESSIONS=8
RUNNING=$(pgrep -f "claude.*--print.*--dangerously-skip-permissions" 2>/dev/null | wc -l | tr -d ' ')
if [ "$RUNNING" -ge "$MAX_SESSIONS" ]; then
  echo "SKIP: $RUNNING claude sessions already running (max $MAX_SESSIONS)"
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTENT_LOG="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/ideas.md"
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

# Build session list into a temp file (avoids subshell pipe issues)
SESSION_LIST=$(mktemp)
echo "$CHANGED" | python3 -c "
import json, sys
sessions = json.load(sys.stdin)
for s in sessions:
    print(f\"{s['session_id']}|{s['path']}|{s['current_bytes']}|{s['date']}\")
" > "$SESSION_LIST"

# Process each session
PROCESSED=0
FAILED=0
while IFS='|' read -r SESSION_ID SESSION_PATH CURRENT_BYTES SESSION_DATE; do
    echo "Processing session $SESSION_ID ($SESSION_DATE)..."

    # Extract full transcript
    TRANSCRIPT=$(python3 "$EXTRACTOR" --extract-session "$SESSION_PATH" 2>/dev/null) || true

    if [ -z "$TRANSCRIPT" ]; then
        echo "  Skipping — empty transcript."
        # Still update bytes so we don't retry empty sessions
        echo "" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES" 2>/dev/null || true
        continue
    fi

    # Get previously extracted insights
    PREV_INSIGHTS=$(python3 "$EXTRACTOR" --get-insights "$SESSION_ID" 2>/dev/null) || true

    # Build the prompt with dedup instructions
    DEDUP_SECTION=""
    if [ -n "$PREV_INSIGHTS" ]; then
        DEDUP_SECTION="

PREVIOUSLY EXTRACTED INSIGHTS (do NOT re-extract these — only find NEW insights not covered below):

$PREV_INSIGHTS

END OF PREVIOUSLY EXTRACTED INSIGHTS."
    fi

    PROMPT="You are a content strategist analyzing Claude Code conversation transcripts. Extract content-worthy insights for short-form video and Twitter threads.

Target audience: Mixed — non-technical people discovering AI + developers learning Claude Code.

For each insight, use EXACTLY this format (output raw markdown, no code fences):

1. **Short description**
   - Context: What happened, backstory, key details
   - Hook: \"The scroll-stopping one-liner\"
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
- If no NEW insights found, output exactly \"No content-worthy insights found.\"
$DEDUP_SECTION"

    # Truncate very large transcripts to avoid hanging the CLI (keep last 200KB)
    TRANSCRIPT_SIZE=${#TRANSCRIPT}
    MAX_SIZE=200000
    if [ "$TRANSCRIPT_SIZE" -gt "$MAX_SIZE" ]; then
        echo "  Transcript too large (${TRANSCRIPT_SIZE} chars), truncating to last ${MAX_SIZE} chars..."
        TRANSCRIPT="${TRANSCRIPT: -$MAX_SIZE}"
    fi

    # Send to claude CLI for analysis (5 min timeout via background + wait)
    TMPFILE=$(mktemp)
    ( echo "$TRANSCRIPT" | /Users/mikeweng/.local/bin/claude --print --dangerously-skip-permissions "$PROMPT" > "$TMPFILE" 2>&1 ) &
    CLAUDE_PID=$!
    TIMEOUT=300
    ELAPSED=0
    TIMED_OUT=false
    while kill -0 "$CLAUDE_PID" 2>/dev/null; do
        if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
            echo "  Timed out after ${TIMEOUT}s, skipping session."
            kill "$CLAUDE_PID" 2>/dev/null || true
            wait "$CLAUDE_PID" 2>/dev/null || true
            rm -f "$TMPFILE"
            # Update bytes so we don't retry this session forever
            echo "" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES" 2>/dev/null || true
            TIMED_OUT=true
            break
        fi
        sleep 5
        ELAPSED=$((ELAPSED + 5))
    done

    if [ "$TIMED_OUT" = "true" ]; then
        FAILED=$((FAILED + 1))
        continue
    fi

    CLAUDE_EXIT=0
    wait "$CLAUDE_PID" || CLAUDE_EXIT=$?
    INSIGHTS=$(cat "$TMPFILE")
    rm -f "$TMPFILE"

    if [ "$CLAUDE_EXIT" -ne 0 ]; then
        echo "  Claude CLI failed (exit $CLAUDE_EXIT), skipping session."
        echo "" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES" 2>/dev/null || true
        FAILED=$((FAILED + 1))
        continue
    fi

    if [ "$INSIGHTS" = "No content-worthy insights found." ]; then
        echo "  No new insights found."
        echo "" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES" 2>/dev/null || true
        continue
    fi

    # Append insights to content log (after header)
    HEADER_END=$(grep -n "^---$" "$CONTENT_LOG" 2>/dev/null | head -1 | cut -d: -f1) || true
    if [ -n "$HEADER_END" ]; then
        HEAD_PART=$(head -n "$HEADER_END" "$CONTENT_LOG")
        TAIL_PART=$(tail -n +"$((HEADER_END + 1))" "$CONTENT_LOG" | sed '/./,$!d')
        {
            echo "$HEAD_PART"
            echo ""
            echo "$INSIGHTS"
            echo ""
            echo "$TAIL_PART"
        } > "$CONTENT_LOG"
    else
        # No header — just append
        echo "" >> "$CONTENT_LOG"
        echo "$INSIGHTS" >> "$CONTENT_LOG"
    fi

    # Update state with new insights and bytes
    echo "$INSIGHTS" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES" 2>/dev/null || true

    echo "  Insights appended to content log."
    PROCESSED=$((PROCESSED + 1))
done < "$SESSION_LIST"

rm -f "$SESSION_LIST"

echo "Done. Processed: $PROCESSED, Failed: $FAILED, Total: $SESSION_COUNT"
