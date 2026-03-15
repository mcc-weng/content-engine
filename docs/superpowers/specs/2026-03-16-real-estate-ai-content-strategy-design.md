# Real Estate AI Content Strategy: Overseas Buyer Niche

## Overview

A content strategy for attracting real estate agents (particularly those selling to overseas Chinese and Taiwanese buyers) and getting them to hire Mike to build AI systems for their business. Uses research-in-public as both the content mechanism and the client acquisition funnel.

## Context

### Previous Strategy (Superseded)
- Dual-track X (English) + Threads (Chinese) engine
- Brand narrative: "Building my way from Taiwan to America — one AI automation at a time"
- This spec replaces the platform strategy entirely

### What This Spec Covers
A full pivot to a real estate vertical with a new 5-platform mix. The content mechanics, positioning, and build strategy are redesigned around two target audiences: overseas Chinese/Taiwanese property buyers and the agents who serve them.

### Key Assets
- Older sister is a real estate agent specialising in overseas Chinese buyers (beta client, open to collaboration)
- Older sister has existing audience: ~598 YouTube, ~300 Facebook, ~200 Instagram followers — all warm, targeted
- Mike is Taiwanese, bilingual, with personal experience as an overseas property buyer
- Direct access to real pain points via older sister before writing a single post
- Older sister confirmed pain: forgets to follow up with buyers — deals lost to silence, not rejection

### Research Findings (Pre-Spec)
- **Older sister's workflow:** DM/message inquiry → send property listings + PDFs → call if lead qualifies
- **Primary communication tool:** WhatsApp and Line (not WeChat — simplifies integration significantly)
- **Active leads at any time:** <10 (small volume but high value per deal)
- **CRM:** None — works from memory and chat history
- **Tech comfort:** 7/10 — can use a web interface, not comfortable with terminal or APIs
- **Commission structure:** ~7% per deal on Australian properties — high willingness to pay for tools
- **Language:** Buyers communicate primarily in Mandarin
- **Confirmed lost deal:** Yes, due to communication delay with overseas buyer

---

## Positioning

**Core statement:** "The only AI builder who's Taiwanese, bilingual, and has lived the overseas buyer experience."

Agents who sell to Chinese/Taiwanese overseas buyers have a specific, underserved problem set: leads go quiet for weeks, inquiries arrive at 2am Sydney time, contracts need explaining in Mandarin. Mike understands all of this personally. That's the moat.

### Two Audiences, One Business

| Audience | Platform | Language | Positioning |
|---|---|---|---|
| Overseas Chinese/Taiwanese buyers | RED, Instagram, Threads | Traditional Chinese | Bilingual guide helping overseas buyers navigate Australian property |
| Real estate agents (overseas buyer segment) | RED, Instagram, Threads, LinkedIn | Traditional Chinese + English | AI builder who deeply understands the overseas buyer problem set |

Both audiences point at the same business. Agents hire Mike to build. Buyers become leads referrable to agent clients.

> **Future consideration (not Month 1-3):** Once a base of agent clients exists, explore a tech-enabled overseas buyer referral service — connecting qualified Chinese/Taiwanese buyers directly to agents, charging a referral fee. Leverages both audiences simultaneously.

### Niche Strategy
Start with overseas buyer agents as beachhead. Niche is not the ceiling — it's the hook. Expand: overseas buyer agents → all Australian agents with Chinese buyer exposure → all Australian agents.

---

## Platform Strategy

**Language:** Traditional Chinese across all Chinese-language platforms. Mike is Taiwanese — Traditional Chinese is his native script, authentic to his identity, and readable by all overseas Chinese audiences (mainland, Taiwan, HK, Singapore, Malaysia).

### Month 1 Platforms

| Platform | Language | Approach | Audience | Format |
|---|---|---|---|---|
| **Xiaohongshu (RED)** | Traditional Chinese | Manual, primary | Overseas buyers + agents | Long-form notes, photo essays |
| **Instagram** | Traditional Chinese | Automated carousel | Taiwanese buyers + agents | Carousel (3–5 slides) |
| **Threads** | Traditional Chinese | Automated | Taiwanese audience | Short conversational posts |
| **X** | English | Automated | AI/build-in-public community | Short posts, build logs |
| **LinkedIn** | English | Profile only | Australian agents (professional) | No posting until Month 2 |

**Posting cadence:**
- RED: 1 post/day (manual, high effort, deep engagement)
- Instagram + Threads + X: adapted auto-distribution from RED content, 3–5x/week
- LinkedIn: profile setup only in Month 1; first post Month 2

**Platform format guide:**

| Platform | Format | Length | Tone |
|---|---|---|---|
| RED | Long-form note with headers | 300–800 chars | Structured, informative, authentic |
| Instagram | Carousel (3–5 slides) | Caption 150–300 chars | Visual-first, clear slide text |
| Threads | Short text post | 100–300 chars | Informal, conversational |
| X | Short text | 280 chars | Direct, build-in-public voice |

### Month 2 Activations (after validated demand)
- **LinkedIn:** First post = older sister case study. Manual, high quality. Targets English-speaking Australian agents.
- **YouTube/Reels:** Short-form video. Mike is comfortable on camera. Suburb walkthroughs, tool demos, building process.

### WeChat
Not a content platform — a conversion tool. Set up personal WeChat presence once warm relationships form via RED/Instagram.

---

## The MVP: Follow-Up Memory Tool

### The Confirmed Pain
Older sister forgets to follow up with buyers. Leads go cold not because she's slow — but because they fall out of her head entirely. With <10 active leads at any time, this should be manageable. But it's not, because there's no system.

**One forgotten follow-up at 7% commission on a $1M+ property = $70k+ lost.**

### What to Build
A tool that remembers her buyers for her and generates the follow-up message when she's forgotten.

**Inputs:** Buyer name, inquiry details, last contacted date, language preference
**Outputs:** Reminder when follow-up is overdue + personalised Mandarin follow-up message
**Delivery:** She copies the message into WhatsApp or Line manually

**Architecture (simplest viable):**
- Airtable base (her leads + last contact date)
- Automation checks for leads not contacted in X days
- Claude API generates personalised Mandarin follow-up message
- Sends her a WhatsApp/Line reminder with the draft message

**Build time: 2–3 days, not 3 weeks.**

### Buildability Check
Before committing to this build:
- ✅ No restricted APIs (WhatsApp/Line, not WeChat)
- ✅ Buildable in <1 week
- ✅ Sister can use it without help (Airtable UI is familiar enough at 7/10 tech comfort)
- ✅ No CRM integration needed (she has none)

### Fallback Hierarchy
If this specific build turns out to be blocked during the interview (e.g., she wants WeChat integration specifically):
1. **Fallback 1:** After-hours inquiry auto-responder (webhook + Claude API → sends Mandarin acknowledgement to new WhatsApp/Line inquiries at 2am)
2. **Fallback 2:** Document explanation tool (upload PDF contract → Claude explains key points in plain Mandarin)

Both fallbacks are equally buildable in <1 week without restricted APIs.

---

## Content Mechanics

### Phase 1: Research-in-Public (Weeks 1–2)

Post before building. Interview older sister AND 2 outside agents. Content attracts agents who recognise their own problem.

**RED post examples (Traditional Chinese):**
> "我在研究海外買家的房仲到底在痛什麼。我姐做這行多年了，第一個發現是..."
> "問了我姐：海外買家沉默三週突然說要簽約，怎麼辦？她的答案讓我重新思考這個問題"

**Beta offer post — Day 9 (not Day 17):**
> "我姐做澳洲海外買家房仲，她說她最頭痛的是忘記跟進買家。
> 我正在幫她建一個AI系統解決這件事。
> 找2個願意免費試用的海外買家房仲——你只需要給我真實反饋。
> 有興趣的話留言或DM我 👇"

### Phase 2: Build-in-Public (Weeks 2–3)

MVP is a 2-day build. Post the process — including the simplicity of it.

> "Day 1 build: 用 Airtable + Claude API 幫我姐建了一個追蹤系統。比你想象的簡單多了。這是我的設計思路："

### Phase 3: Case Study → Client Acquisition (Month 2+)

Sister's results + cross-promotion from her existing 1,100 followers = first paying clients.

**Paid offer post — Day 20:**
> "幫我姐建好了。她說：「[原文引用]」
> 如果你是做海外買家的房仲，我可以幫你建同樣的系統。
> $[X]，3天交付，不好用全退。
> 有興趣的話DM我。"

---

## Content Pillars

### RED (Traditional Chinese) — Primary
- **Research drops** (25%): Pain point discoveries, agent interviews, industry observations
- **Build logs** (30%): Day-by-day building the AI system
- **Buyer guides** (25%): How AI is changing the overseas property buying experience
- **Case studies + offers** (20%): Results, beta offers, paid offers

### Instagram (Traditional Chinese)
- **Research drops** (25%): Carousel adaptations of RED content
- **Build logs** (35%): Visual build documentation
- **Personal brand** (20%): Taiwanese AI builder narrative
- **Offers** (20%): Beta and paid offer carousels

### Threads (Traditional Chinese)
- **Conversational research** (35%): Informal takes on agent pain points
- **Build updates** (35%): Casual build-in-public updates
- **Hot takes** (30%): Opinions on PropTech gaps

### X (English)
- **Build logs** (50%): Short build-in-public updates
- **AI hot takes** (30%): English-language AI tool opinions
- **Progress updates** (20%): Revenue/milestone transparency

---

## Selling Strategy

**Month 1 is about conversations, not followers.** Every post is designed to start a conversation with an agent. 10 agent conversations by Day 30 = at least 1 client.

| Days | Offer | Goal |
|---|---|---|
| 1–8 | No offer — just research posts | Get agents to self-identify |
| 9–19 | Beta tester spot (free, needs feedback) | Start conversations, validate interest |
| 20–30 | First paid offer ($X, 3-day delivery, money-back) | Find 1 paying client |
| Month 2+ | Productized offer backed by case study | Repeatability |

**Pricing anchor:** At 7% commission on Australian properties, one deal saved justifies $2–3k/month tool costs easily. Price the first paid engagement at $500–1500. Don't underprice — it signals low confidence.

---

## Monetization Path

- **Month 1:** Build for older sister (free), beta test with 1–2 outside agents (free), land first paid client ($500–1500)
- **Month 2–3:** Productized offer ("AI follow-up system for overseas buyer agents, $1200, 3 days") + LinkedIn case study activation
- **Month 4–6:** Retainer model ($500–800/month maintenance + updates) for 5–10 agents
- **Month 6+:** SaaS from repeated patterns, or scale service with help

---

## Architecture Decisions

1. **Traditional Chinese everywhere** — native script, authentic identity, readable by all overseas Chinese audiences
2. **RED primary, others automated** — RED deserves manual attention; Instagram/Threads/X run on content engine
3. **LinkedIn Month 2** — needs case study to be effective; profile built Month 1
4. **Follow-up memory, not automation** — the confirmed pain is forgetting, not speed. Build for memory first.
5. **WhatsApp/Line, not WeChat** — massively simplifies integration; no restricted API concerns
6. **2-day MVP, not 3-week MVP** — Airtable + Claude prompt + reminder. Ship fast, iterate on real usage.
7. **Sell in Week 2, not Week 3** — beta offer on Day 9, paid offer on Day 20
8. **3 agent interviews before building** — sister + 2 outside agents via RED/Instagram cold outreach
9. **Sister's existing audience is a seed** — confirm cross-promotion during interview; 1,100 warm followers = free Day 1 boost
10. **Bilingual moat is irreplaceable** — never dilute into generic AI content

---

## Success Criteria

- Week 1: All 5 platforms live; first posts on all; RED getting daily engagement
- Week 2: Sister + 2 outside agents interviewed; beta offer posted; first DMs from agents
- Week 3: MVP built and delivered to sister; "showed sister the demo" post published
- Day 20: First paid offer posted
- Month 1: First paying client ($500+); sister using the tool daily
- Month 2: LinkedIn case study published; YouTube/video content started; 3+ agents in pipeline
- Month 3: $1–3k/month recurring; productized offer live
