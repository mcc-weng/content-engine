# LinkedIn Module

Scoring criteria: see `scoring-rubric.md`

---

## Format Spec

- **Post types:** Text posts (primary) + Document posts (PDF carousels)
- **Text post length:** 1,300-1,900 characters (under 500 flagged as low-effort)
- **Document posts:** 6.6% engagement rate — highest-performing format on LinkedIn
- **Visibility cutoff:** First 210-235 characters visible before "See more" — 60-70% of readers are lost here if the hook doesn't land
- **Paragraph structure:** Short paragraphs (2-3 sentences), aggressive line breaks, one idea per paragraph
- **Language:** English (primary)

---

## Algorithm Signals

- **Highest-value signal:** Saves (1 save = ~5x reach of a like)
- **First-hour window:** First 60-90 minutes determine 70% of total post reach — must engage actively during this window
- **Comment weight:** Comments worth 2x likes
- **External link penalty:** Links in post body = ~60% less reach — put all links in first comment
- **Posting frequency:** 2+ posts/day drops per-post reach by 40%+ — quality over volume
- **New account penalty:** Aggressive early posting gets flagged — ramp up gradually

---

## Tone Rules

- **Style:** Process-driven — step-by-step methods, frameworks, structured approaches
- **Feel:** Professional but personal — real results, real numbers, real context
- **What works:** Specific numbers, data points, concrete examples that make content saveable
- **Avoid:** Generic AI-sounding language, vague inspiration, pure theory without examples
- **Voice file:** Load `voice-en.md` → apply `## LinkedIn Adjustments`

---

## Content Strategy

| Content Type | Mix | Audience |
|---|---|---|
| Case studies | 40% | Agents + brokers |
| Process frameworks | 35% | Agents + brokers |
| Personal credibility | 25% | Agents + industry |

- **Audience split:** Primary B2B agent-facing, professional credibility
- **Start:** Month 2+ only — first post is sister case study
- **Persona:** AI engineer who invested in Australian real estate, building tools for the industry

---

## Hashtag Strategy

- **Volume:** 3-5 relevant tags
- **Placement:** End of post, after the main content
- **Examples:** #realestate #proptech #artificialintelligence #realestateagent #aitools
- **Rule:** No hashtag stuffing — LinkedIn penalizes excessive tags

---

## Anti-Patterns

- **"Post and ghost"** (not engaging in first 60 minutes) → #1 reach killer on LinkedIn
- **External links in post body** → -60% reach; always put links in first comment
- **Generic AI-generated content** → LinkedIn filters detect and reduce reach ~45% of the time
- **Engagement pods** → detected by LinkedIn's systems
- **New account posting aggressively immediately** → algorithm flags new accounts that post too fast too soon
- **One giant wall of text** → no line breaks = readers abandon immediately
- **Weak hook in first 210 chars** → 60-70% never click "See more"

---

## Scaffold Adaptation

**Text post format:**
- **Hook (first 210 chars):** Choose one opener style — contrarian claim, narrative setup, or specific statistic
  - Must make readers click "See more" — this is the highest-leverage line in the post
- **Body:** Scaffold flow expanded to 1,300-1,900 chars
  - Short paragraphs (2-3 sentences max)
  - Aggressive line breaks — blank line between every paragraph
  - One idea per paragraph
  - Concrete numbers and examples throughout
- **Close:** Summary + CTA (save this, share with someone, drop a question)

**Document post (PDF carousel):**
- Scaffold maps to PDF slides — similar to Instagram carousel but more text-heavy and professional
- Each slide: one point, supporting detail, clean visual hierarchy
- First slide: bold hook statement
- Last slide: summary + CTA

**Hook patterns:**
```
Contrarian: "Most [audience] are [doing X wrong]. Here's what actually works."
Narrative: "My sister went from [state A] to [state B] in [timeframe]. Here's how."
Statistics: "[Specific number] [surprising fact]. Here's what it means for [audience]."
```

---

## Example Posts

---

**Example 1 — Case Study**

```
My sister is a Melbourne real estate agent specializing in overseas Chinese buyers.

Last quarter, she was turning down clients.

Not because she didn't want the business. Because market reports were taking 4 hours each, and she didn't have enough hours in the week.

That changed 6 weeks ago.

Here's what happened when we integrated AI into her workflow:

THE OLD PROCESS (4 hours per report):
• Pull comparable sales from 3 platforms manually
• Research flood risk, zoning, development approvals separately
• Write bilingual summary (English + Chinese) from scratch
• Format everything for client presentation

THE NEW PROCESS (45 minutes per report):
• Input: property address + client brief
• AI pulls 12-month price trends, rental yield, vacancy rates
• AI generates bilingual draft summary
• She reviews, adds market context, personalizes
• Done

THE RESULTS (6 weeks in):
• Reports per week: 5-6 → 15+
• Client capacity: up 3x
• Report quality: same or better (more data, faster turnaround)
• Revenue impact: still calculating, but pipeline is noticeably fuller

THE PART PEOPLE GET WRONG:

This isn't "AI replacing an agent."

It's AI removing the time cost of research and formatting — so she can spend more time on the work that actually requires her judgment: reading clients, negotiating, building relationships.

The agents who thrive in the next 5 years won't be the ones who ignore AI. They'll be the ones who figure out how to offload the right tasks.

Her competitive advantage isn't the tool. It's that she already understood her market deeply enough to know what questions to ask.

That combination is what's hard to replicate.

Who else is experimenting with AI in their real estate workflow? I'd genuinely like to hear what's working.

#realestate #proptech #aitools #realestateagent #artificialintelligence
```

---

**Example 2 — Process Framework**

```
Real estate agents serving overseas buyers face a problem that almost no tool was designed to solve.

Their clients can't inspect in person. They rely entirely on what the agent tells them.

The information gap is enormous — and it creates liability for the agent if something goes wrong.

Here's the 5-point AI due diligence framework I developed after buying 4 properties in Australia as a Taiwanese investor:

POINT 1: PRICE ANOMALY CHECK
Compare listing price to comparable sales within 500m, same property type, last 12 months.

Flag: If asking price is 8%+ above comps, or if previous sale was 12%+ below comps, investigate before proceeding.

Takes AI: 3 minutes. Takes manually: 45+ minutes.

POINT 2: OWNERSHIP VELOCITY
How many times has this property changed hands in the last 10 years? What was the average hold period?

Flag: 3+ sales in 10 years or average hold under 24 months signals something worth investigating.

Takes AI: 2 minutes. Takes manually: 30+ minutes.

POINT 3: SUPPLY PIPELINE WITHIN 500M
How many approved or under-construction developments are within 500m?

Flag: 3+ projects = future rental competition that compresses yield and can pressure capital values.

Takes AI: 5 minutes. Takes manually: 1-2 hours across council planning portals.

POINT 4: FLOOD AND ENVIRONMENTAL RISK
Pull the council flood risk rating. Check bushfire zone. Check noise contours if near airports.

Flag: Anything rated B (moderate) or above that isn't disclosed in the listing.

Takes AI: 3 minutes. Takes manually: 20+ minutes per council database.

POINT 5: SCHOOL ENROLLMENT TRENDS
If buying in a school zone, check enrollment trends over 3-5 years — not just current ratings.

Flag: Top-rated school with declining enrollment. Find out why before buying.

Takes AI: 5 minutes. Takes manually: 15+ minutes if the data is even findable.

TOTAL TIME SAVINGS:
Manual: 2-3 hours per property
AI-assisted: ~20 minutes per property

For an agent running 15 client properties per month, that's 30+ hours saved.

That's not a marginal improvement. That's a different business model.

Save this framework. The prompt I use to run all 5 checks is in the comments.

#proptech #realestate #realestateagent #aitools #duediligence
```

---

**Example 3 — Personal Credibility**

```
I'm a Taiwanese AI engineer who owns 4 investment properties in Australia.

That combination is unusual enough that people ask me questions I didn't expect.

The most common one: "How did you even know what to look for?"

The honest answer is: I didn't, at first.

My first purchase was fine because I got lucky and had my sister in Melbourne to help me. She's a real estate agent who specializes in overseas Chinese buyers.

By my third purchase, I had built a systematic approach — and AI tools had become good enough to be genuinely useful.

Here's what the information gap actually looks like for overseas buyers:

WHAT'S EASY TO FIND:
• Listing price and photos
• Basic property specs
• Suburb median prices
• Agent contact info

WHAT'S HARD TO FIND IF YOU'RE NOT LOCAL:
• Comparable sales (requires knowing which platforms to check)
• FIRB requirements and recent policy changes
• Development approvals in the area
• Flood/fire/noise risk ratings
• School enrollment trends (not just rankings)
• Body corporate financials for apartments
• Building and pest inspection red flags to watch for

Every item on that second list is something a local investor checks before making an offer.

Most overseas buyers skip most of it. Not because they don't care — because they don't know it exists or don't know where to find it.

AI has changed this equation significantly. Not completely. But enough that the information gap is now a solvable problem rather than a permanent disadvantage.

The tools I've built for my sister's agency came directly from this list — each one addresses a specific item overseas buyers consistently miss.

If you're working with overseas buyers, these are the exact gaps your clients are walking into blind.

The agents who help them navigate these gaps earn the trust that turns into referrals.

What's the most common oversight you see from overseas buyer clients? I'm genuinely curious what shows up in your market.

#realestate #overseas #proptech #realestateagent #artificialintelligence
```
