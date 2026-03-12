#!/bin/bash
set -euo pipefail

# Allow running from within a Claude Code session or cron
unset CLAUDECODE 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTENT_LOG="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/log.md"
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
        DEDUP_SECTION="

PREVIOUSLY EXTRACTED INSIGHTS (do NOT re-extract these — only find NEW insights not covered below):

$PREV_INSIGHTS

END OF PREVIOUSLY EXTRACTED INSIGHTS."
    else
        DEDUP_SECTION=""
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

    # Send to claude CLI for analysis
    INSIGHTS=$(echo "$TRANSCRIPT" | /Users/mikeweng/.local/bin/claude --print --dangerously-skip-permissions "$PROMPT")

    if [ "$INSIGHTS" = "No content-worthy insights found." ]; then
        echo "  No new insights found."
        # Still update bytes so we don't re-process unchanged content
        echo "" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES"
        continue
    fi

    # Prepend to content log (after header)
    # Header ends at "---" line, insert new content right after it
    HEADER_END=$(grep -n "^---$" "$CONTENT_LOG" | head -1 | cut -d: -f1)
    if [ -n "$HEADER_END" ]; then
        # Split file: header (lines 1-HEADER_END) + rest
        HEAD_PART=$(head -n "$HEADER_END" "$CONTENT_LOG")
        TAIL_PART=$(tail -n +"$((HEADER_END + 1))" "$CONTENT_LOG")
        {
            echo "$HEAD_PART"
            echo ""
            echo "$INSIGHTS"
            echo "$TAIL_PART"
        } > "$CONTENT_LOG"
    else
        # No header found, just prepend
        EXISTING=$(cat "$CONTENT_LOG")
        {
            echo "$INSIGHTS"
            echo ""
            echo "$EXISTING"
        } > "$CONTENT_LOG"
    fi

    # Update state with new insights and bytes
    echo "$INSIGHTS" | python3 "$EXTRACTOR" --update-state "$SESSION_ID" "$CURRENT_BYTES"

    echo "  Insights appended to content log."
done

echo "Done."
