#!/bin/bash
# Batch transcribe and save Hormozi videos
# Usage: ./scripts/hormozi-transcribe-batch.sh

RESEARCH_DIR="docs/research/hormozi"
TRANSCRIPT_DIR="$RESEARCH_DIR/transcripts"

# Videos to process: ID|TITLE|DURATION|VIEWS|TOPICS
VIDEOS=(
  "F84olnKkseM|Business Was Hard Until I Understood These 4 Concepts|38:51|561K|scaling, mental models"
  "FMzKk73iUhw|How To Get Customers So Fast It Feels ILLEGAL|41:43|618K|leads, customer acquisition"
  "pLhQOYMGa88|Learn Email Marketing in 39 Minutes|39:18|596K|email marketing, leads"
  "MNll1BaskLA|How to Win At ANYTHING|47:25|2.3M|mindset, skill acquisition"
  "Nh8Oc7ERdIU|How to Get Ahead of 99% of People|56:26|1.8M|competitive advantage, compounding"
  "oZ-H_TjSzok|No BS Advice to Get Rich in the Next 10 Years|45:55|998K|wealth, long-term"
  "HsQeQM1jUeg|If I Had To Start a Business From Scratch|42:37|592K|starting, offers"
  "VBoRLJimVzc|If I Wanted to Become a Millionaire In 2024 FULL BLUEPRINT|1:03:41|4.0M|scaling, blueprint"
  "KhFlD54nQrY|13 Years Of Brutally Honest Business Advice in 90 Mins|1:30:00|3.6M|comprehensive, frameworks"
  "k834E6OTGTM|100M Leads Launch|1:27:39|1.1M|leads, book launch"
  "oRMG_HpOAN4|13 Years of No BS Business Advice in 79 Mins|1:19:43|2.8M|comprehensive, frameworks"
  "reisEL_D7xc|13 Years of Marketing Advice in 85 Mins|1:25:24|1.3M|marketing, frameworks"
  "AN2KpRBsmRY|If I Wanted To Become a Millionaire in 2026 FULL BLUEPRINT|1:18:24|1.4M|scaling, 2026, blueprint"
  "HxEQCHpZzHk|How to Grow Your Business SO Fast in 2026 It Feels ILLEGAL|1:03:08|1.3M|scaling, growth, 2026"
  "StVqS0jD7Ls|The Ultimate Sales Training for 2026 Full Course|2:34:01|943K|sales, 2026, comprehensive"
  "HKbFUWJwEG0|I Reverse Engineered the Perfect Business|1:04:11|520K|business model, scaling"
)

for entry in "${VIDEOS[@]}"; do
  IFS='|' read -r ID TITLE DURATION VIEWS TOPICS <<< "$entry"
  TRANSCRIPT_FILE="$TRANSCRIPT_DIR/yt-${ID}.md"

  # Skip if already transcribed
  if [ -f "$TRANSCRIPT_FILE" ]; then
    echo "SKIP: $TITLE (already transcribed)"
    continue
  fi

  # Check if audio exists, download if not
  if [ ! -f "/tmp/hormozi-${ID}.mp3" ]; then
    echo "DOWNLOAD: $TITLE"
    yt-dlp -x --audio-format mp3 -o "/tmp/hormozi-${ID}.%(ext)s" "https://www.youtube.com/watch?v=${ID}" 2>&1 | tail -1
  fi

  # Check if transcript txt exists, transcribe if not
  if [ ! -f "/tmp/hormozi-${ID}.txt" ]; then
    echo "TRANSCRIBE: $TITLE ($DURATION)"
    whisper "/tmp/hormozi-${ID}.mp3" --model small --output_format txt --output_dir /tmp/ 2>&1 | tail -1
  fi

  # Save transcript
  if [ -f "/tmp/hormozi-${ID}.txt" ]; then
    echo "SAVE: $TITLE"
    cat > "$TRANSCRIPT_FILE" << HEADER
# ${TITLE}

**URL:** https://www.youtube.com/watch?v=${ID}
**Views:** ${VIEWS} | **Duration:** ${DURATION}
**Topics:** ${TOPICS}

---

HEADER
    cat "/tmp/hormozi-${ID}.txt" >> "$TRANSCRIPT_FILE"
    git add "$TRANSCRIPT_FILE"
    git commit -m "feat: transcribe Hormozi \"${TITLE}\" (${DURATION})

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
    echo "DONE: $TITLE"
  else
    echo "FAILED: $TITLE - no transcript produced"
  fi
done

echo "=== BATCH COMPLETE ==="
ls "$TRANSCRIPT_DIR"/*.md | wc -l
echo "total transcripts"
