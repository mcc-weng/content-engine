# Multi-Agent Content Team Design

**Date:** 2026-04-01
**Status:** Draft
**Supersedes:** Single-skill cc-draft/cc-adapt architecture

## Problem

The current cc-draft skill is a 439-line monolith that handles 6 platforms. When Mike edits a draft for one platform, those changes don't translate well to other platforms. He's playing whack-a-mole — editing Threads, then re-editing LinkedIn, then catching inconsistencies across both. He's doing the job of platform editor, copy editor, and creative director simultaneously.

## Solution

A multi-agent content team where specialized agents handle execution roles (platform editing, quality review, brand consistency) and Mike retains the Creative Director role — approving angles and final sign-off.

## Team Composition

```
YOU (Creative Director)
 │
 ▼
cc-strategist (Manager Agent)
 │
 ├──▶ cc-researcher     (trend scanning, competitive intel)
 ├──▶ cc-editor-x        (subagent)
 ├──▶ cc-editor-threads   (subagent)
 ├──▶ cc-editor-linkedin  (subagent)
 ├──▶ cc-editor-instagram (subagent)
 ├──▶ cc-editor-youtube   (subagent)
 │
 ▼
cc-reviewer (Individual draft quality check)
 │
 ▼
cc-copy-chief (Cross-platform consistency review)
 │
 ▼
YOU (Approve / Edit / Kill)
 │
 ▼
cc-copy-chief (Second pass on your edits)
 │
 ▼
cc-post (Publish — unchanged)
```

### Agent Responsibilities

**cc-strategist** — The only skill invoked directly for drafting. Takes a topic from Mike, proposes an angle, decides which platforms to target (not always all 5), orchestrates the team. Reads ideas.md, posts.md, and content calendar for context. Can dispatch cc-researcher as a subagent when trend context is needed. Absorbs the role previously held by cc-brainstorm.

**cc-researcher** — Trend scanning and competitive intel. Searches for what's working around a specific topic across platforms. Called by the strategist when needed, not every time. Can also be invoked standalone by Mike ("what's trending?").

**cc-editor-[platform]** (5 agents) — Each drafts natively for one platform. Has its own voice feedback file. Loads only its platform module, hooks research, humanizer, and scoring rubric. Returns a scored draft to the strategist. Runs as a subagent in parallel with other editors.

**cc-reviewer** — Reviews individual draft quality. Checks: is the hook strong? Is the structure right for this platform? Does the angle land? Reviews one draft at a time. If quality is lacking, sends feedback to the specific editor for one revision round.

**cc-copy-chief** — Reviews all drafts together for cross-platform consistency, brand voice drift, and AI-isms. Makes surgical edits — does not rewrite. Runs two passes: once before Mike sees the drafts, once after Mike's edits to catch cross-platform conflicts introduced by editing.

**cc-post** — Publishing mechanics. Unchanged from current implementation.

**cc-capture** — Raw idea intake. Unchanged, standalone utility.

### Retired Skills

- **cc-draft** — Replaced by cc-editor-* agents. SKILL.md retired, directory renamed to `cc-shared-refs` as a shared reference library.
- **cc-adapt** — Replaced entirely. Editors draft natively in parallel — no "adapt from one platform" step.
- **cc-brainstorm** — Absorbed into cc-strategist's angle proposal step.
- **cc-review** — Retired. Not used.
- **cc-recap** — Retired. Not used.

## Workflow

### Step-by-Step Flow

```
Step 1: Mike → cc-strategist
  "Draft about how I used Claude to automate my listing photos"

Step 2: cc-strategist → cc-researcher (optional)
  "What's working around AI + real estate content right now?"
  Researcher returns trend context.

Step 3: cc-strategist → Mike (CHECKPOINT 1)
  "Angle: 'I saved 3 hours per listing — here's the ugly truth about AI photos'
   Platforms: Threads (hot take), LinkedIn (case study), YouTube (demo)
   Skipping: X (similar post 2 days ago), Instagram (no visual asset ready)"
  
  Mike: "yes" / "change angle" / "add X too"

Step 4: cc-strategist → cc-editor-* (parallel subagents)
  Fans out to cc-editor-threads, cc-editor-linkedin, cc-editor-youtube.
  Each drafts independently using its own voice profile + platform module.

Step 5: cc-reviewer checks each draft individually
  "Threads hook is strong. LinkedIn structure works. YouTube hook is weak —
   sending feedback to cc-editor-youtube for revision."
  Editor revises. Max 1 revision round.

Step 6: cc-copy-chief reviews all drafts together (PASS 1)
  - Checks messaging consistency across platforms
  - Catches brand voice drift and AI-isms editors missed
  - Ensures core angle survived adaptation to each platform
  - Makes surgical edits or flags issues to specific editors (max 1 round)

Step 7: cc-strategist → Mike (CHECKPOINT 2)
  Presents all drafts with scores and notes:
  
  THREADS: [draft] — Hook 8 / Retention 7 / CTA 8
  LINKEDIN: [draft] — Hook 7 / Retention 8 / CTA 7
  YOUTUBE: [script] — Hook 7 / Retention 8 / CTA 7
  
  Copy chief notes: [any flags]
  
  Mike: approve all / edit specific ones / kill one

Step 8: Mike edits → feedback routing
  If Mike edits the Threads draft:
  - Edit pattern → voice-feedback-threads.md (platform-specific learning)
  - cc-copy-chief PASS 2: re-checks all drafts for consistency
  - "Your Threads edit changed the framing. LinkedIn still says the old angle.
     Updating LinkedIn to match." → auto-fix or flag to Mike

Step 9: Final approval → cc-post
  Mike approves → hand off to cc-post for publishing.
```

### Checkpoint Design

- **2 checkpoints only:** Angle approval (step 3) and final draft approval (step 7).
- Reviewer and copy chief passes are automatic — no user input needed.
- Skipping platforms is normal — strategist actively recommends NOT posting where the topic doesn't fit.

### Revision Limits

- Editor → Reviewer loop: max 1 revision round
- Editor → Copy chief loop: max 1 revision round
- Total: a draft sees at most 2 revision rounds before reaching Mike

## Voice Feedback & Learning

### Per-Platform Feedback Files

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/
├── voice-en.md                    (base English voice — unchanged)
├── voice-zh.md                    (base Chinese voice — unchanged)
├── voice-feedback-threads.md      (learns from Threads edits)
├── voice-feedback-x.md            (learns from X edits)
├── voice-feedback-linkedin.md     (learns from LinkedIn edits)
├── voice-feedback-instagram.md    (learns from Instagram edits)
├── voice-feedback-youtube.md      (learns from YouTube edits)
└── voice-feedback-brand.md        (copy chief's cross-platform learnings)
```

### Feedback Flow

1. Mike edits a Threads draft → cc-editor-threads captures the pattern → writes to `voice-feedback-threads.md`
2. Same kind of edit appears on LinkedIn → cc-editor-linkedin captures it → writes to `voice-feedback-linkedin.md`
3. Copy chief notices the same edit across 3+ platforms → promotes to `voice-feedback-brand.md` as a universal rule

### What Each Editor Loads

- Base voice profile (`voice-en.md` or `voice-zh.md`)
- Its own platform feedback file (`voice-feedback-[platform].md`)
- Brand-level feedback (`voice-feedback-brand.md`)

### Migration

The existing `voice-feedback.md` gets split: platform-specific entries go to the right platform file, universal patterns go to `voice-feedback-brand.md`.

## Skill File Structure

```
~/.claude/skills/
├── cc-strategist/
│   └── SKILL.md
│
├── cc-researcher/
│   └── SKILL.md
│
├── cc-copy-chief/
│   └── SKILL.md
│
├── cc-reviewer/
│   └── SKILL.md
│
├── cc-editor-x/
│   └── SKILL.md
├── cc-editor-threads/
│   └── SKILL.md
├── cc-editor-linkedin/
│   └── SKILL.md
├── cc-editor-instagram/
│   └── SKILL.md
├── cc-editor-youtube/
│   └── SKILL.md
│
├── cc-shared-refs/                (shared reference library — renamed from cc-draft)
│   ├── assets/
│   │   └── post-templates.md
│   └── references/
│       ├── hook-types.md
│       ├── cta-bank.md
│       ├── scoring-rubric.md
│       ├── humanizer-en.md
│       ├── humanizer-zh.md
│       ├── post-examples.md
│       └── platforms/
│           ├── x.md
│           ├── threads.md
│           ├── linkedin.md
│           ├── instagram.md
│           ├── youtube.md
│           ├── x-hooks-research.md
│           ├── threads-hooks-research.md
│           ├── linkedin-hooks-research.md
│           ├── instagram-hooks-research.md
│           └── youtube-hooks-research.md
│
├── cc-capture/                    (unchanged)
└── cc-post/                       (unchanged)
```

### Skill Sizing

- **cc-strategist:** ~150-200 lines. Angle proposal logic, platform selection heuristics, orchestration flow, context loading (ideas.md, posts.md).
- **cc-researcher:** ~80-100 lines. WebSearch queries per platform, trend extraction, competitive intel formatting.
- **cc-editor-[platform]:** ~80-100 lines each. Loads platform module + shared refs, drafts, self-scores, returns structured output.
- **cc-reviewer:** ~80-100 lines. Quality rubric evaluation, feedback formatting for editors.
- **cc-copy-chief:** ~100-150 lines. Cross-platform comparison logic, brand consistency checks, surgical edit rules, two-pass flow.

### Shared References

All editors load from `~/.claude/skills/cc-shared-refs/references/`:
- `platforms/[platform].md` — format specs, algorithm signals, tone rules
- `platforms/[platform]-hooks-research.md` — viral hook patterns
- `hook-types.md` — 8 hook type definitions
- `assets/post-templates.md` — 6 scaffold types
- `cta-bank.md` — platform-specific CTA patterns
- `scoring-rubric.md` — Hook/Retention/CTA scoring
- `humanizer-en.md` / `humanizer-zh.md` — AI detection filters

## Execution Model

### Subagent Strategy

The cc-strategist is the orchestrator. It dispatches agents using Claude Code's Agent tool:

- **cc-researcher** — single subagent, called before angle proposal when needed
- **cc-editor-*** — parallel subagents (3-5 at once depending on platform selection)
- **cc-reviewer** — runs sequentially after editors return (needs their output)
- **cc-copy-chief** — runs sequentially after reviewer (needs reviewed drafts)

### Token Budget Considerations

A full 5-platform run involves: strategist + researcher + 5 editors + reviewer + copy chief = 9 agent invocations. To manage token costs:
- Strategist should actively skip platforms where the topic doesn't fit
- Typical run should target 2-3 platforms, not all 5
- Editors load only their platform's references, not all platforms

## Active Platforms

| Platform | Language | Editor | Content Type |
|----------|----------|--------|-------------|
| X | English | cc-editor-x | Tweets, threads |
| Threads | Traditional Chinese | cc-editor-threads | Short text posts |
| LinkedIn | English | cc-editor-linkedin | Long-form text |
| Instagram | English | cc-editor-instagram | Video scripts (Reels) |
| YouTube | English | cc-editor-youtube | Video scripts (Shorts/long-form) |

RED is not included. Adding it later = creating `cc-editor-red/SKILL.md`. Platform module and hooks research already exist in shared refs.

## What Stays Unchanged

- **cc-post** — all publishing scripts, token management, posting workflow
- **cc-capture** — raw idea intake to ideas.md
- **Obsidian data files** — ideas.md, posts.md, drafts.md (same structure)
- **Voice profiles** — voice-en.md, voice-zh.md (base profiles unchanged)
- **Shared references** — all platform modules, hooks research, templates, humanizers, scoring rubric

## Interaction Model

### Daily Usage

Mike's primary entry point is cc-strategist:
- "Draft about [topic]" — full pipeline
- "Draft about [topic] for threads only" — strategist dispatches single editor
- "What should I post today?" — strategist checks ideas.md + posts.md + calendar

Mike can also invoke directly:
- "cc-capture" — log an idea
- "cc-post" — publish an approved draft
- "cc-researcher" — standalone trend scan

### Evolution Path

Phase 1 (this spec): Collaborative with 2 checkpoints. Mike approves angle + final drafts.
Phase 2 (future): As voice feedback accumulates, reduce to 1 checkpoint (final approval only). Strategist gains autonomy on angle selection.
Phase 3 (future): Fully autonomous. Mike reviews batch output, veto-only. Add cc-analyst for post-performance feedback loops.
