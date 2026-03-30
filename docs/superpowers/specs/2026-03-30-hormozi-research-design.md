# Alex Hormozi Deep Dive Research — Design Spec

**Date:** 2026-03-30
**Status:** Draft
**Goal:** Comprehensive research on Alex Hormozi's business knowledge, strategies, and content system, organized as an actionable playbook for building a business from zero through agency → personal brand → info products → SaaS.

---

## 1. Background & Motivation

Mike is building a business from scratch, following the progression: agency (trade time for money) → personal brand via content with funnels → courses/coaching/community → SaaS once patterns emerge. Alex Hormozi has documented this exact playbook publicly across hundreds of pieces of content and two bestselling books. The goal is to systematically extract, organize, and internalize Hormozi's frameworks — both the business knowledge and the content strategy that distributes it.

## 2. Scope — Platforms & Content Types

| Platform | Content Type | Estimated Volume | Access Method |
|----------|-------------|-----------------|---------------|
| YouTube (main channel) | Long-form videos, shorts | 500+ videos | YouTube Data API / yt-dlp |
| YouTube (Hormozi Clips) | Short clips from longer content | 200+ | YouTube Data API / yt-dlp |
| Podcast (The Game) | Audio/video episodes | 300+ episodes | YouTube API (video versions) + RSS |
| Books | $100M Offers, $100M Leads | 2 books | Manual (Mike owns copies) |
| Instagram | Reels, carousels, stories | 1000+ posts | Playwright (login required) |
| X/Twitter | Text posts, threads | Active | Playwright (login required) |
| LinkedIn | Long-form posts | Active | Playwright (login required) |
| TikTok | Short-form video | Repurposed content | Playwright (login required) |
| Skool | Community posts, courses | Gated content | Playwright (login required) |
| acquisition.com | Blog posts, resources | Website content | Web fetch / Playwright |

## 3. Phased Approach

### Phase 1: Map the Territory

**Objective:** Build a comprehensive index of Hormozi's entire content library with metadata for intelligent prioritization.

**Process per platform:**

1. **YouTube (both channels)** — Scrape all video metadata: title, view count, like count, publish date, duration, description. Categorize by topic (offers, leads, sales, hiring, content, mindset, scaling, etc.)
2. **Podcast** — Index all episodes with titles, dates, guest names, descriptions via RSS feed + YouTube versions
3. **Instagram** — Scrape post metadata: type (reel/carousel/image), caption, like count, comment count, date. Focus on top-performing posts sorted by engagement
4. **X/Twitter** — Scrape tweets sorted by engagement. Capture text, retweet count, like count, reply count
5. **LinkedIn** — Scrape posts sorted by engagement (reactions, comments)
6. **TikTok** — Scrape video metadata: title/caption, view count, like count, date
7. **acquisition.com** — Crawl blog and resources sections for all article titles and URLs
8. **Skool** — If accessible, index available courses and top community posts
9. **Books** — No scraping needed; indexed manually as two entries

**Auth handling:** For platforms requiring login (Instagram, X, LinkedIn, TikTok, Skool), use Playwright browser automation. Prompt Mike to login when hitting auth walls. Mike will handle CAPTCHA/2FA manually.

**Output:** `docs/research/hormozi/content-index.md` — Master catalogue with:
- Platform-by-platform content listing (split into separate sections; if any platform exceeds 500 entries, break into its own file e.g. `content-index-youtube.md`)
- Engagement metrics (views, likes, comments where available)
- Topic tags per piece
- Priority ranking (P1/P2/P3) for Phase 2 deep dive candidates
- Total content count and breakdown stats

### Phase 2: Deep Dive the Best

**Objective:** Transcribe and extract frameworks from the top 15-20 pieces across all platforms, plus both books.

**Selection criteria** (applied to Phase 1 index):
- Engagement-to-age ratio (recent viral > old viral)
- Framework density — prioritize "how to" and strategy content over motivational/entertainment clips
- Relevance to Mike's business path (agency → brand → info products → SaaS)
- Diversity across topics — don't over-index on one area

**Process:**

1. **Video transcription** — Use existing `/transcribe` skill on top YouTube videos and podcast episodes
2. **Per-piece analysis** — For each transcribed/collected piece, extract:
   - Core frameworks and models (named if Hormozi names them, described if not)
   - Actionable tactics with specific numbers/benchmarks
   - Memorable quotes and one-liners
   - Examples and case studies cited
   - Content format/structure patterns (hooks, transitions, CTAs)
3. **Book deep dives** — Extract complete framework summaries from $100M Offers and $100M Leads. These are likely his most concentrated thinking and get priority.
4. **Social post analysis** — Top posts catalogued with hook patterns, format choices, engagement analysis

**Output:** Individual analysis files in `docs/research/hormozi/analyses/` per piece, plus running frameworks document.

### Phase 3: Synthesize

**Objective:** Distill everything into actionable documents mapped to Mike's business stages.

**Output files:**

#### `docs/research/hormozi/hormozi-business-playbook.md`
Organized by Mike's business stages:
1. **Stage 1: Agency** — Offer creation (Value Equation), pricing strategy, lead generation, sales frameworks (CLOSER), fulfillment systems, hiring first employees
2. **Stage 2: Personal Brand** — Content strategy, platform selection, distribution, audience building, authority positioning
3. **Stage 3: Info Products** — Course creation, coaching models, community building (Skool playbook), funnels, pricing tiers
4. **Stage 4: SaaS** — Pattern recognition from services, when to build, validation approaches
5. **Cross-cutting** — Mindset frameworks, decision-making models, time management, compounding principles

#### `docs/research/hormozi/hormozi-content-strategy.md`
- His content machine structure (team composition, cadence, repurposing pipeline)
- Hook formulas and thumbnail/title patterns
- Content sequencing strategy (awareness → authority → monetization)
- Platform-specific tactics
- What Mike can replicate solo vs what requires a team
- Distribution and amplification tactics

#### `docs/research/hormozi/hormozi-style-guide.md`
Same format as the Ray Fu style guide:
- Voice and tone analysis
- Script structure patterns
- Hook templates
- CTA patterns
- Visual/editing style notes
- Engagement tactics

#### `knowledge/hormozi.md` (Obsidian vault)
Quick-reference summary for mobile access with links to full docs.

## 4. Technical Implementation

### Scripts to Build

#### `scripts/hormozi-index.py`
- YouTube Data API v3 integration for channel metadata scraping
- Accepts channel ID, fetches all videos with metadata
- Falls back to `yt-dlp --flat-playlist --dump-json` if API quota exhausted
- Outputs structured data (JSON + markdown)
- Env var: `YOUTUBE_API_KEY`

#### `scripts/hormozi-scrape.py`
- Playwright-based scraper for auth-walled platforms
- Supports: Instagram, X/Twitter, LinkedIn, TikTok, Skool, acquisition.com
- Prompts user to login when hitting auth walls (interactive — waits for user)
- Handles pagination and rate limiting
- Outputs structured data per platform
- Configurable per-platform scrapers (modular design)

### Existing Tools
- `/transcribe` skill — YouTube/Instagram video transcription (already built)
- Playwright MCP — Browser automation (already configured)
- Claude analysis — No tooling needed; done in conversation

### Data Flow

```
YouTube API / yt-dlp / Playwright scraping
        ↓
docs/research/hormozi/content-index.md     (Phase 1 output)
        ↓
/transcribe on top picks
        ↓
docs/research/hormozi/transcripts/         (Raw transcripts)
        ↓
Claude analysis
        ↓
docs/research/hormozi/analyses/            (Per-piece analysis)
        ↓
Synthesis
        ↓
docs/research/hormozi/playbook + strategy + style guide  (Phase 3)
knowledge/hormozi.md in Obsidian vault                    (Summary)
```

### Directory Structure

```
docs/research/hormozi/
├── content-index.md              # Master catalogue (Phase 1)
├── transcripts/                  # Raw transcripts (Phase 2)
│   ├── yt-{video-id}.md
│   └── ...
├── analyses/                     # Per-piece analysis (Phase 2)
│   ├── yt-{video-id}-analysis.md
│   ├── book-100m-offers.md
│   ├── book-100m-leads.md
│   └── ...
├── hormozi-business-playbook.md  # Master frameworks (Phase 3)
├── hormozi-content-strategy.md   # Content machine analysis (Phase 3)
└── hormozi-style-guide.md        # Voice & format guide (Phase 3)
```

## 5. Dependencies & Constraints

- **YouTube API key** — Mike needs to create one in Google Cloud Console. Fallback: yt-dlp (no key needed, slightly less metadata).
- **Platform logins** — Mike must be logged into Instagram, X, LinkedIn, TikTok, Skool in Chrome for Playwright scraping. Will be prompted interactively.
- **Rate limiting** — Social platforms throttle scraping. Scripts must include delays and handle rate limit responses gracefully.
- **Gated content** — Skool community content may require paid membership. We capture what's accessible.
- **Book content** — Not scrapable. Mike can provide highlights/notes, or we summarize from publicly available summaries and Hormozi's own video explanations of book concepts.
- **Volume** — Phase 1 indexing is largely automated. Phase 2 transcription of 15-20 videos will take meaningful compute time. Phase 3 synthesis is Claude analysis work.

## 6. Success Criteria

- Phase 1: Complete index with engagement metrics across all accessible platforms
- Phase 2: 15-20 highest-value pieces fully transcribed and analyzed, both books summarized
- Phase 3: Business playbook that Mike can reference at each stage of his journey, content strategy doc he can apply immediately, style guide for content creation
- All outputs in `docs/research/hormozi/` with Obsidian summary for mobile access
