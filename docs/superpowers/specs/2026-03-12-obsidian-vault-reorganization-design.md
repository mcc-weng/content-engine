# Obsidian Vault Reorganization — Design Spec

## Purpose

Reorganize Mike's Obsidian vault ("brain") to serve as an AI-accessible second brain. The vault is primarily written to and read by Claude, with Mike browsing occasionally via Obsidian. Optimize for predictable file locations, easy linking, and minimal friction for AI reads/writes.

## Vault Structure

```
brain/
├── daily/              # daily notes (one per day)
├── content/            # content pipeline (single files, append-style)
│   ├── ideas.md
│   ├── drafts.md
│   ├── posts.md
│   ├── log.md
│   ├── research.md
│   └── voice.md
├── projects/           # one note per project
│   ├── openclaw.md
│   ├── kali-app.md
│   └── content-engine.md
├── interests/          # one note per topic/obsession
│   ├── elon-musk.md
│   ├── tesla.md
│   ├── badminton.md
│   ├── calisthenics.md
│   └── ...
├── resources/          # frameworks, courses, reference material
│   ├── justin-welsh-creator-mba.md
│   └── ...
├── me/                 # personal identity, goals, planning
│   ├── skills.md
│   ├── goals.md
│   └── obsessions.md
├── templates/          # note templates
└── MOCs/               # maps of content (index pages)
    ├── Home.md
    ├── Projects.md
    ├── Content.md
    ├── Interests.md
    ├── Resources.md
    ├── Me.md
    └── Daily Notes.md
```

## Conventions

### Two file strategies

1. **Content pipeline (`content/`):** Single files, append-style. Optimized for linear workflow (capture → draft → post → archive). No individual notes per idea.
2. **Everything else:** One note per topic. Linked with `[[backlinks]]`. Optimized for knowledge retrieval and dot-connecting.

### Frontmatter on every note

```yaml
---
title: Tesla
tags: [interest, technology]
created: 2026-03-12
updated: 2026-03-12
---
```

### Tags complement folders

- Folders = what type (project, interest, resource)
- Tags = what about (`#elon-musk`, `#ai`, `#fitness`)

### Linking rules

- When mentioning a concept that has its own note, link it: `[[elon-musk]]`
- Cross-link related notes in a `## Links` section at the bottom

### Note template (non-content)

```markdown
---
title: {Topic}
tags: [{type}, {topics}]
created: {date}
updated: {date}
---

# {Topic}

## Key Thoughts
- {dated observations, opinions, ideas}

## Links
- [[related-note]]
```

### Max folder depth

One level of subfolders maximum. No deep nesting.

## AI Read/Write Protocol

### Reading

1. Check relevant folder first (e.g., "Tesla?" → `interests/tesla.md`)
2. Follow `[[backlinks]]` to related notes
3. If unsure, scan the relevant MOC for pointers

### Writing

1. **New topic** → create note in correct folder with frontmatter
2. **Existing topic** → append under a dated section (`## 2026-03-12`)
3. **Content pipeline** → append to the single file in `content/`
4. **Cross-link** → add `[[backlinks]]` to related notes
5. **Update MOC** → add note to relevant MOC if new

### Consent

- Claude offers to save meaningful insights: "want me to save that to your vault?"
- Does not silently write unless explicitly told to capture something

## Migration Plan

### File moves

| Current | New | Notes |
|---|---|---|
| `projects/content-ideas.md` | `content/ideas.md` | Keep content |
| `projects/content-log.md` | `content/log.md` | Keep content |
| `projects/content-posts.md` | `content/posts.md` | Keep content |
| `projects/content-research.md` | `content/research.md` | Keep content |
| `projects/content-voice.md` | `content/voice.md` | Keep content |
| `projects/2026-03-09-first-dollar-sprint-plan.md` | `projects/first-dollar-sprint.md` | Rename |
| `Plan.md` (root) | `me/skills-and-obsessions.md` | It's personal inventory |
| `MOCs/References.md` | `MOCs/Resources.md` | Match folder name |

### New files to create

- `MOCs/Content.md` — index for content pipeline
- `MOCs/Interests.md` — index for interests
- `MOCs/Me.md` — index for personal
- `me/goals.md` — seeded from Plan.md goals list
- `me/obsessions.md` — seeded from obsession audit
- `interests/elon-musk.md` — seeded from today's captured idea
- New templates: `templates/interest-note.md`, `templates/resource-note.md`

### Downstream updates

**Content skills (7 files in `~/.claude/skills/`):**
- `cc-capture` — path: `content/ideas.md`
- `cc-draft` — paths: `content/drafts.md`, `content/ideas.md`
- `cc-post` — path: `content/posts.md`
- `cc-review` — update all content paths
- `cc-recap` — paths: `content/log.md`, `content/posts.md`
- `cc-research` — path: `content/research.md`
- `log-content` — path: `content/log.md`

**Claude memory files:**
- `~/.claude/projects/-Users-mikeweng-Desktop-Projects-content/memory/social-media-engine.md` — update vault paths
- `MEMORY.md` — update quick reference
- `~/.claude/CLAUDE.md` — update `/content` capture section path

**Scripts (verify paths):**
- `scripts/post-to-threads.py`
- `scripts/extract-content-insights.sh`

## Verification

End-to-end test after migration:

1. Run `/cc-capture` with a test idea — verify it appends to `content/ideas.md`
2. Run `/cc-draft` — verify it reads from `content/ideas.md` and writes to `content/drafts.md`
3. Run `/cc-review` — verify it reads the right files
4. Run `/cc-research` — verify it writes to `content/research.md`
5. Run `/cc-recap` — verify it reads correct paths
6. Run `/log-content` — verify it writes to `content/log.md`
7. Verify `extract-content-insights.sh` writes to correct path
8. Verify all MOCs have correct links
9. Verify no orphaned files in old locations
