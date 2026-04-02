# X (Twitter) Module

Scoring criteria: see `scoring-rubric.md`

---

## Format Spec

- **Post type:** Short text posts
- **Length:** Under 280 characters (single tweet) or threads of 2-4 posts
- **Thread frequency:** Max 1 thread per week — threads are high-effort, high-reward
- **Format benchmark:** Text-only outperforms video by 30% on X
- **Language:** English (primary)

---

## Algorithm Signals

- **#1 signal:** Conversation depth — replies drive distribution more than anything else
- **Reply value:** A reply is worth ~27x a like in algorithmic weight
- **Premium reach:** X Premium accounts get ~10x more reach than non-Premium
- **Link penalty (March 2026+):** Non-Premium accounts posting links receive near-zero median engagement
- **Best posting windows:** When your audience is active (check analytics — typically 7-9am, 12-1pm, 7-9pm local)

---

## Tone Rules

- **Style:** Direct, build-in-public, show-your-work
- **Feel:** Opinionated, concise — every word earns its place
- **What works:** Screenshots, code snippets, specific data points, honest progress updates
- **Avoid:** Vague inspiration, corporate speak, surface-level takes
- **Voice file:** Load `voice-en.md` → apply `## X Adjustments`

---

## Content Strategy

| Content Type | Mix | Audience |
|---|---|---|
| Build logs | 50% | AI/tech community |
| AI hot takes | 30% | AI/tech community |
| Progress updates | 20% | Build-in-public audience |

- **Audience split:** 100% build-in-public / AI community
- **Primary persona:** Developers and practitioners building with AI

---

## Hashtag Strategy

- **Volume:** 0-2 maximum per post
- **Rule:** Only use when genuinely relevant, never trending hashtags on unrelated content
- **Examples when relevant:** #buildinpublic #AI #realestate
- **Default:** Most posts should have 0 hashtags — X's algorithm doesn't reward hashtag usage the way Instagram does

---

## Anti-Patterns

- **Follow-unfollow tactics** → detected within 24-48 hours, #1 shadowban trigger on X
- **Generic replies** ("Great post!", "100%", "This!") → looks automated, suppressed
- **Repetitive content patterns** (same template, same link structure) → flagged as spam
- **Excessive hashtags** → triggers spam detection
- **Links without Premium** → near-zero distribution since March 2026
- **Over-scheduling** → posting the same way every day at the same time looks like automation

**Premium awareness:** X Premium is essentially required for meaningful reach in 2026. Without it, link posts get near-zero distribution. Factor this into effort allocation — if not on Premium, focus on text-only posts and replies.

---

## Scaffold Adaptation

**Single tweet:** Compress scaffold to one core idea + punchy delivery. Remove all padding.

**Thread format:**
- Tweet 1: Hook — the problem or the counterintuitive claim (must work as standalone)
- Tweets 2-N: Body — scaffold flow maps to individual tweets, one idea per tweet
- Final tweet: Closing thought + CTA (ask a question, invite a reply)

**Build-in-public formula:**
```
Problem → Tried → Worked → Lesson
```
This is the single most reliable format for this audience.

**Hot take formula:**
```
[Contrarian claim] + [specific evidence or data] + [implication]
```

---

## Example Posts

---

**Example 1 — Build Log (Single Tweet)**

```
Built a property red-flag detector for my sister (Melbourne RE agent).

It pulls flood risk, price history anomalies, and development pipeline for any Australian address in 2 minutes.

Before: 3 hours of manual research per property.
Now: 15 minutes total.

The ROI math is obvious.
```

---

**Example 2 — AI Hot Take**

```
Real estate agents aren't being replaced by AI.

They're being replaced by agents who use AI.

The bottleneck was never local knowledge or relationships.

It was the time cost of research, reporting, and follow-up.

That bottleneck is gone now. The gap between top and average agents is about to widen.
```

---

**Example 3 — Thread (Build-in-Public)**

```
Tweet 1:
I've been building AI tools for real estate agents serving overseas buyers.

Here's what I've learned after 3 months and 4 properties of my own:

🧵

Tweet 2:
The problem: overseas buyers have massive information asymmetry.

Listings look clean. But comparable sales, flood risk, development approvals, and school enrollment trends are buried across 5+ data sources.

Most buyers never check. That's when they get burned.

Tweet 3:
What I built: a prompt chain that aggregates all of this for any Australian address.

Input: property address + client brief
Output: bilingual (EN + ZH) market summary with red flags flagged

Time: 15 minutes vs 3+ hours manually.

Tweet 4:
The surprising part: the tool isn't the hard part.

The hard part is knowing what questions to ask.

Agents who understand the market well already know what red flags to look for.

AI just removes the time cost of checking.

Tweet 5:
If you're building AI tools for a specific industry — find a practitioner who already does the work well.

They know the questions. You build the tooling.

That's the actual collaboration model.

What are you building? Reply — I read everything.
```
