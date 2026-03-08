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
