# Content Insight Extraction System

## Purpose
Continuously capture content-worthy moments from Claude Code conversations and log them in a structured format for short-form video, Twitter threads, and occasional long-form content.

## Target audience
Mixed — non-technical people discovering AI + developers leveling up with Claude Code.

## Goal
Build distribution by positioning Mike as someone who deeply understands AI tools, builds real things, and can help others do the same. Product/service TBD — audience first.

## Content log location
`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`

## Insight format
```
1. **Short description**
   - Context: What happened, backstory, key details needed to retell this
   - Hook: "The scroll-stopper"
   - Angle: Why the audience cares / takeaway
   - Format: short-form | thread | long-form
   - Category: struggle | aha | decision | hot-take | authority
   - [ ] Posted
```

Organized by date headings (`## YYYY-MM-DD`), with `### Themes` sections when patterns emerge.

## Five insight categories
1. **Struggle moments** — things that went wrong or were harder than expected
2. **Aha moments** — discoveries, clever solutions, unexpected wins
3. **Decision points** — choices others will face too
4. **Hot takes** — strong reactions to how something works (or doesn't)
5. **Authority builders** — things built/solved that demonstrate expertise

## Three capture mechanisms

### 1. Daily cron (primary, automatic)
- Scheduled job runs once daily (e.g. midnight)
- Processes all conversations from that day
- Extracts messages from JSONL files, invokes `claude` CLI to analyze and extract insights
- Appends to content-log.md under the right date heading
- Tracks processed session IDs to avoid duplicates

### 2. Inline flagging (experimental)
- During conversations, Claude notes content-worthy moments as they happen
- No strict rules yet — testing to see if it's annoying or helpful
- User can tell Claude to stop if it's disruptive

### 3. Manual `/content` (fallback)
- User says "/content" or "log that" during a conversation
- Claude captures the moment and appends to content-log.md immediately

## One-time backfill
Process all ~135 existing conversations across all projects to build an initial content bank.

## Technical details
- Conversation files stored at `~/.claude/projects/<project-name>/<session-id>.jsonl`
- Each line is a JSON object with `type` (human/assistant/progress) and message content
- Daily cron uses `claude` CLI with a prompt to analyze conversations — no separate API key needed
- Processed session IDs tracked in a state file to avoid re-processing
