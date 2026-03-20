# Obsidian Vault Reorganization — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the Obsidian vault from a flat `projects/` layout into a structured second-brain with `content/`, `projects/`, `interests/`, `resources/`, `me/` folders, then update all downstream references.

**Architecture:** Move content pipeline files from `projects/content-*.md` to `content/*.md` (renamed). Split `Plan.md` into `me/` files. Create new folders and seed notes. Update 11 files with new paths. End-to-end verify all skills still work.

**Tech Stack:** Bash (file moves), Obsidian markdown, Claude Code skills (SKILL.md files)

**Vault path:** `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/`
**Spec:** `docs/superpowers/specs/2026-03-12-obsidian-vault-reorganization-design.md`

---

## Chunk 1: Backup & Folder Structure

### Task 1: Backup vault

**Files:**
- Read: vault root

- [ ] **Step 1: Create backup**

```bash
cp -r ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain-backup-2026-03-12
```

- [ ] **Step 2: Verify backup**

```bash
diff <(find ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain -name "*.md" -not -path "*/.obsidian/*" | sort) <(find ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain-backup-2026-03-12 -name "*.md" -not -path "*/.obsidian/*" | sort | sed 's/brain-backup-2026-03-12/brain/g')
```

Expected: no differences

### Task 2: Create new folder structure

- [ ] **Step 1: Create folders**

```bash
VAULT=~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain
mkdir -p "$VAULT/content" "$VAULT/interests" "$VAULT/me"
```

- [ ] **Step 2: Verify folders exist**

```bash
ls -d "$VAULT"/{content,interests,me,daily,projects,templates,MOCs}
```

Expected: all 7 directories listed (resources/ will be created by renaming references/ in Task 5)

## Chunk 2: File Moves

### Task 3: Move content pipeline files

**Files:**
- Move: `projects/content-ideas.md` → `content/ideas.md`
- Move: `projects/content-log.md` → `content/log.md`
- Move: `projects/content-posts.md` → `content/posts.md`
- Move: `projects/content-research.md` → `content/research.md`
- Move: `projects/content-voice.md` → `content/voice.md`

- [ ] **Step 1: Move files**

```bash
VAULT=~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain
mv "$VAULT/projects/content-ideas.md" "$VAULT/content/ideas.md"
mv "$VAULT/projects/content-log.md" "$VAULT/content/log.md"
mv "$VAULT/projects/content-posts.md" "$VAULT/content/posts.md"
mv "$VAULT/projects/content-research.md" "$VAULT/content/research.md"
mv "$VAULT/projects/content-voice.md" "$VAULT/content/voice.md"
```

- [ ] **Step 2: Verify moves**

```bash
ls "$VAULT/content/"
```

Expected: `ideas.md  log.md  posts.md  research.md  voice.md`

- [ ] **Step 3: Verify source is clean**

```bash
ls "$VAULT/projects/"
```

Expected: only `2026-03-09-first-dollar-sprint-plan.md` remains

### Task 4: Rename project file

- [ ] **Step 1: Rename**

```bash
mv "$VAULT/projects/2026-03-09-first-dollar-sprint-plan.md" "$VAULT/projects/first-dollar-sprint.md"
```

### Task 5: Rename references folder and template

- [ ] **Step 1: Rename folder**

```bash
mv "$VAULT/references" "$VAULT/resources"
```

- [ ] **Step 2: Rename template**

```bash
mv "$VAULT/templates/reference-note.md" "$VAULT/templates/resource-note.md"
```

- [ ] **Step 3: Rename MOC**

```bash
mv "$VAULT/MOCs/References.md" "$VAULT/MOCs/Resources.md"
```

### Task 6: Split Plan.md into me/ files

**Files:**
- Read: `Plan.md` (root)
- Create: `me/skills-inventory.md`, `me/goals.md`, `me/obsessions.md`
- Delete: `Plan.md`

- [ ] **Step 1: Read Plan.md and create me/goals.md**

Extract the goals list (items 1-6 at top) into `me/goals.md` with proper frontmatter:

```markdown
---
title: Goals
tags: [me, goals]
created: 2026-03-12
updated: 2026-03-12
---

# Goals

## Things I Want To Build
1. Build automated content engine
2. Build openclaw
3. Build kali app

## Links
- [[skills-inventory]]
- [[obsessions]]
```

- [ ] **Step 2: Create me/obsessions.md**

Extract Task 2 (Obsession Audit) from Plan.md:

```markdown
---
title: Obsessions
tags: [me, obsessions]
created: 2026-03-12
updated: 2026-03-12
---

# Obsessions

## What I Read/Watch/Follow For Fun
entrepreneurs, tesla, elon musk, shark tank, mark cuban, personal development channels, solopreneurs, ai news, ai tools, claude code, openclaw, saas apps, starter story, badminton lessons, badminton games, workout, calisthenics, body building, tech gadgets, manga, webtoon, anime, movies, actors interviews, tv shows

## Problems I Think About
- How to start a company
- How to build a personal brand
- How to build automations

## If Money Wasn't A Factor
Building business. Physical mastery and creative engineering as full-time jobs — perfecting calisthenics (handstand, muscle-up), training for badminton. Exploring, learning, tinkering — iOS app ideas, automation workflows, video ideas, AI tools, new ways of making money. Max out drumming skills.

## Links
- [[goals]]
- [[skills-inventory]]
- [[elon-musk]]
```

- [ ] **Step 3: Create me/skills-inventory.md**

Extract Tasks 1 & 3 from Plan.md:

```markdown
---
title: Skills Inventory
tags: [me, skills]
created: 2026-03-12
updated: 2026-03-12
---

# Skills Inventory

## 1000+ Hours Professional Experience
- Building apps, coding

## What People Ask Advice On (Unprompted)
- Software, AI, solo dev experience, badminton, weight loss, gymming

## Can Teach 30 Min With No Prep
- How to use AI, Claude Code, vibe coding, full stack apps, mobile apps, badminton tips

## Unique Knowledge Zone (Skills × Obsessions Intersection)
_To be defined — see [[obsessions]] and Justin Welsh's framework in [[justin-welsh-creator-mba]]_

## Links
- [[obsessions]]
- [[goals]]
```

- [ ] **Step 4: Delete Plan.md**

```bash
rm "$VAULT/Plan.md"
```

- [ ] **Step 5: Verify me/ folder**

```bash
ls "$VAULT/me/"
```

Expected: `goals.md  obsessions.md  skills-inventory.md`

## Chunk 3: Create New Files

### Task 7: Create content/drafts.md

- [ ] **Step 1: Create empty drafts file**

```markdown
---
title: Content Drafts
tags: [content, drafts]
created: 2026-03-12
updated: 2026-03-12
---

# Content Drafts

## In Progress

## Ready to Post

## Posted
```

### Task 8: Create interest notes

- [ ] **Step 1: Create interests/elon-musk.md**

```markdown
---
title: Elon Musk
tags: [interest, entrepreneur, technology]
created: 2026-03-12
updated: 2026-03-12
---

# Elon Musk

## Key Thoughts
- 2026-03-12: Realised this is my core obsession. Thinking about making Elon/Tesla/his companies the focus of my content business, inspired by [[justin-welsh-creator-mba]] obsession framework.

## Companies
- [[tesla]]
- SpaceX
- xAI
- Neuralink
- The Boring Company

## Links
- [[obsessions]]
- [[tesla]]
```

### Task 9: Create templates

- [ ] **Step 1: Create templates/interest-note.md**

```markdown
---
title: "{{title}}"
tags: [interest]
created: "{{date}}"
updated: "{{date}}"
---

# {{title}}

## Key Thoughts
-

## Links
-
```

### Task 10: Create & update MOCs

- [ ] **Step 1: Create MOCs/Content.md**

```markdown
---
tags: [MOC]
---

# Content

## Pipeline
- [[content/ideas]] - Raw ideas queue
- [[content/drafts]] - Work in progress
- [[content/posts]] - Published posts
- [[content/log]] - Content insights log
- [[content/research]] - Trending topics & research
- [[content/voice]] - Voice & style guide
```

- [ ] **Step 2: Create MOCs/Interests.md**

```markdown
---
tags: [MOC]
---

# Interests

- [[elon-musk]]
```

- [ ] **Step 3: Create MOCs/Me.md**

```markdown
---
tags: [MOC]
---

# Me

- [[skills-inventory]] - What I'm good at
- [[goals]] - What I'm building toward
- [[obsessions]] - What I can't stop thinking about
```

- [ ] **Step 4: Update MOCs/Resources.md**

Update content (was References.md, already renamed in Task 5):

```markdown
---
tags: [MOC]
---

# Resources

## Frameworks & Courses
_Add resources as they come up_
```

- [ ] **Step 5: Update MOCs/Home.md**

```markdown
---
tags: [MOC]
---

# Home

Welcome to your vault. This is your main hub.

## Maps of Content
- [[Projects]] - Active and past projects
- [[Content]] - Content creation pipeline
- [[Interests]] - Topics and obsessions
- [[Resources]] - Frameworks, courses, references
- [[Me]] - Goals, skills, identity
- [[Daily Notes]] - Day-to-day logs
```

- [ ] **Step 6: Update MOCs/Projects.md**

```markdown
---
tags: [MOC]
---

# Projects

## Active
- [[first-dollar-sprint]]

## Completed

## Ideas
```

- [ ] **Step 7: Commit vault changes**

Not git-tracked, so skip. Verify via file listing instead:

```bash
find "$VAULT" -name "*.md" -not -path "*/.obsidian/*" -not -path "*/brain-backup*" | sort
```

## Chunk 4: Update Downstream References

### Task 11: Update content skills (path: `projects/content-*.md` → `content/*.md`)

All paths change from `brain/projects/content-X.md` to `brain/content/X.md`.

**Files to modify:**
- `~/.claude/skills/cc-capture/SKILL.md`
- `~/.claude/skills/cc-draft/SKILL.md`
- `~/.claude/skills/cc-post/SKILL.md`
- `~/.claude/skills/cc-review/SKILL.md`
- `~/.claude/skills/cc-recap/SKILL.md`
- `~/.claude/skills/cc-research/SKILL.md`
- `~/.claude/skills/log-content/SKILL.md`

- [ ] **Step 1: Update cc-capture/SKILL.md**

Replace: `brain/projects/content-ideas.md` → `brain/content/ideas.md`

- [ ] **Step 2: Update cc-draft/SKILL.md**

Replace all 3 paths:
- `brain/projects/content-voice.md` → `brain/content/voice.md`
- `brain/projects/content-ideas.md` → `brain/content/ideas.md`
- `brain/projects/content-log.md` → `brain/content/log.md`

Also add `brain/content/drafts.md` as the drafts output path (new file, no old path to replace — add to the Paths section of the skill).

- [ ] **Step 3: Update cc-post/SKILL.md**

Replace:
- `brain/projects/content-ideas.md` → `brain/content/ideas.md`
- `brain/projects/content-posts.md` → `brain/content/posts.md`

- [ ] **Step 4: Update cc-review/SKILL.md**

Replace:
- `brain/projects/content-ideas.md` → `brain/content/ideas.md`
- `brain/projects/content-posts.md` → `brain/content/posts.md`
- `brain/projects/content-log.md` → `brain/content/log.md`
- `brain/projects/content-research.md` → `brain/content/research.md`

- [ ] **Step 5: Update cc-recap/SKILL.md**

Replace:
- `brain/projects/content-posts.md` → `brain/content/posts.md`
- `brain/projects/content-ideas.md` → `brain/content/ideas.md`
- `brain/projects/content-log.md` → `brain/content/log.md`

- [ ] **Step 6: Update cc-research/SKILL.md**

Replace:
- `brain/projects/content-research.md` → `brain/content/research.md`
- `brain/projects/content-ideas.md` → `brain/content/ideas.md`
- `brain/projects/content-log.md` → `brain/content/log.md`

- [ ] **Step 7: Update log-content/SKILL.md**

Replace: `brain/projects/content-log.md` → `brain/content/log.md`

### Task 12: Update scripts

**Files:**
- Modify: `scripts/extract-content-insights.sh`

- [ ] **Step 1: Update extract-content-insights.sh**

Replace: `$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/projects/content-log.md`
→ `$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/log.md`

- [ ] **Step 2: Commit script change**

```bash
git add scripts/extract-content-insights.sh
git commit -m "fix: update vault path in content extraction script"
```

### Task 13: Update Claude memory files

**Files:**
- Modify: `~/.claude/CLAUDE.md`
- Modify: `~/.claude/CLAUDE.legacy.md`
- Modify: `~/.claude/projects/-Users-mikeweng-Desktop-Projects-content/memory/social-media-engine.md`
- Modify: `~/.claude/projects/-Users-mikeweng-Desktop-Projects-content/memory/MEMORY.md`
- Modify: `~/.claude/projects/-Users-mikeweng-Desktop-Projects-personal/memory/MEMORY.md`

- [ ] **Step 1: Update CLAUDE.md**

Replace: `brain/projects/content-log.md` → `brain/content/log.md`

- [ ] **Step 2: Update CLAUDE.legacy.md**

Replace: `brain/projects/content-log.md` → `brain/content/log.md`

- [ ] **Step 3: Update social-media-engine.md**

Replace vault path references from `brain/projects/` to `brain/content/` and update file names (`content-*.md` → `*.md`).

- [ ] **Step 4: Update content project MEMORY.md**

Replace: `brain/projects/content-*.md` → `brain/content/*.md` (ideas.md, drafts.md, posts.md, log.md, research.md, voice.md)

- [ ] **Step 5: Update personal project MEMORY.md**

Replace: `brain/projects/content-log.md` → `brain/content/log.md`

## Chunk 5: End-to-End Verification

### Task 14: Verify all paths resolve

- [ ] **Step 1: Verify all content files exist at new paths**

```bash
VAULT=~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain
for f in content/ideas.md content/drafts.md content/posts.md content/log.md content/research.md content/voice.md; do
  test -f "$VAULT/$f" && echo "OK: $f" || echo "MISSING: $f"
done
```

Expected: all OK

- [ ] **Step 2: Verify no orphaned content files at old paths**

```bash
ls "$VAULT/projects/content-"* 2>/dev/null && echo "ORPHANS FOUND" || echo "Clean"
```

Expected: Clean

- [ ] **Step 3: Verify no stale path references in skills**

```bash
grep -r "projects/content-" ~/.claude/skills/cc-*/SKILL.md ~/.claude/skills/log-content/SKILL.md 2>/dev/null && echo "STALE PATHS FOUND" || echo "Clean"
```

Expected: Clean

- [ ] **Step 4: Verify no stale path in extraction script**

```bash
grep "projects/content-" ~/Desktop/Projects/content/scripts/extract-content-insights.sh && echo "STALE" || echo "Clean"
```

Expected: Clean

### Task 15: Functional smoke tests

- [ ] **Step 1: Test /cc-capture** — run the skill with a test idea, verify it appends to `content/ideas.md`
- [ ] **Step 2: Test /cc-draft** — run the skill, verify it reads from `content/ideas.md` and writes to `content/drafts.md`
- [ ] **Step 3: Test /cc-review** — run the skill, verify it reads from correct paths
- [ ] **Step 4: Test /cc-research** — run the skill, verify it writes to `content/research.md`
- [ ] **Step 5: Test /cc-recap** — run the skill, verify it reads correct paths
- [ ] **Step 6: Test /log-content** — run the skill, verify it writes to `content/log.md`
- [ ] **Step 7: Test extract-content-insights.sh** — run the script and verify it writes to `content/log.md`

### Task 16: Cleanup

- [ ] **Step 1: Delete vault backup**

```bash
rm -rf ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/brain-backup-2026-03-12
```

- [ ] **Step 2: Delete Plan.md if not already deleted**

```bash
rm -f "$VAULT/Plan.md"
```

- [ ] **Step 3: Final commit**

```bash
git add scripts/extract-content-insights.sh docs/superpowers/
git commit -m "chore: complete obsidian vault reorganization"
```
