# Instagram Module

Scoring criteria: see `scoring-rubric.md`

---

## Format Spec

- **Post type:** Carousels (primary format)
- **Slide count:** 8-10 slides for maximum engagement
- **Ratio:** 4:5 portrait (1080x1350px) — first slide dictates ratio for entire carousel
- **Slide design:** Bold header, minimal text (under 20% text overlay), hook under 12 words per slide
- **Each swipe:** A distinct engagement event — more slides = more algorithm signal
- **Image creation:** Manual — engine outputs slide text and caption only; user creates visuals
- **Caption:** 150-300 characters summarizing the post + hashtags

---

## Algorithm Signals

- **Primary signals:** Dwell time + swipe-through velocity
- **Each swipe:** Counts as a distinct engagement event — longer carousels compound engagement
- **Highest-value signal:** Saves (people want to reference this later)
- **Critical threshold:** Completion rate above 60%
- **Caption reach:** Keyword-rich captions generate 30% more reach and 2x more likes than hashtag-heavy captions

---

## Tone Rules

- **Style:** Educational, value-driven, professional but personal
- **Design:** Clean, consistent brand (2-3 colors, 1-2 fonts across all slides)
- **Content principle:** Make people want to save and reference this later
- **Avoid:** Cluttered slides, inconsistent design, weak CTAs
- **Voice file:** Load `voice-en.md` → apply `## Instagram Adjustments`

---

## Content Strategy

| Content Type | Mix | Audience |
|---|---|---|
| Research drops | 25% | Agents |
| Build logs | 35% | Agents + tech audience |
| Personal brand | 20% | Agents + general |
| Offers | 20% | Agents |

- **Audience split:** 70% agent-facing, 30% personal brand
- **Primary persona:** Real estate agents wanting to adopt AI tools

---

## Hashtag Strategy

- **Volume:** 3-5 highly relevant tags
- **Priority:** Keyword-rich captions over hashtag stuffing
- **Examples:** #realestate #proptech #aitools #realestateagent #realestateinvesting
- Avoid: Banned tags, irrelevant trending tags, over-tagging (feels spammy)

---

## Anti-Patterns

- **Inconsistent design** across slides (mixing fonts, colors, spacing) → breaks brand trust
- **Cluttered slides** with too much text or low-contrast text → viewers abandon carousel
- **Mixing aspect ratios** within a carousel → first slide ratio locks all others
- **Weak/absent CTAs** → no action guidance means no action taken
- **Caption keyword gaps** → missing keywords costs 30% reach
- **Single-image posts** for educational content → carousels get significantly more reach

**Image creation note:** `/cc-draft` and `/cc-adapt` output slide text and caption only. User creates visual slides manually using Canva, Figma, or similar tools. `post-to-instagram.py` accepts publicly accessible image URLs.

---

## Scaffold Adaptation

- **Slide 1:** Hook/promise — bold text, answers "is this for me?" in under 12 words
- **Slides 2-9:** Value delivery — each slide = one idea, one header, minimal supporting text
  - Follow scaffold body flow, one point per slide
  - Each slide should be readable in 3-5 seconds
- **Final slide:** CTA — "Save this", "DM me [trigger word]", "Share with someone who needs this"
- **Caption:** 150-300 chars summarizing the post → hashtags
- **Design note:** Consistent color palette, same font pair across all slides

---

## Example Posts

---

**Example 1 — Research Drop (Slide-by-Slide)**

*Caption:* Real estate agents — stop spending 4 hours on market reports. Here's how AI cuts it to 45 minutes. Save this. #realestate #proptech #aitools

```
Slide 1:
[HOOK]
Agents: You're losing 4 hours per market report.
Here's the AI workflow that fixes it.

Slide 2:
[THE OLD WAY]
• Pull comps manually from 3 platforms
• Translate and format for overseas clients
• Write the summary narrative
• Total: 3-4 hours per report

Slide 3:
[THE NEW WAY — STEP 1]
Feed the property address + client brief to AI
→ It pulls 12-month price trends, rental yield,
vacancy rates in 2 minutes

Slide 4:
[STEP 2]
AI generates a bilingual summary
(English + Chinese)
→ No more manual translation

Slide 5:
[STEP 3]
You review, add context, personalize
→ 45 minutes total

Slide 6:
[REAL NUMBERS]
Before: 5-6 reports/week max
After: 15+ reports/week
Same quality. 3x the volume.

Slide 7:
[THE REAL WIN]
You stop turning down clients
because reports take too long.
That's the actual ROI.

Slide 8:
[WHAT AI CAN'T DO]
Read the room on a site visit.
Negotiate for your client.
Build the relationship.
That's still you.

Slide 9:
[BOTTOM LINE]
AI handles data + formatting.
You handle judgment + relationships.
This is how agents survive the next 5 years.

Slide 10:
[CTA]
Save this for when you're ready to try it.
DM me "REPORT" and I'll send you the exact prompt I use.
```

---

**Example 2 — Build Log**

*Caption:* Built a tool that finds red flags in Australian property listings before buyers waste time on inspections. Here's what it catches. #proptech #realestate #aitools #realestatetech

```
Slide 1:
[HOOK]
I built a tool that finds property red flags
before you waste time on an inspection.
Here's what it caught last month.

Slide 2:
[THE PROBLEM]
Overseas buyers can't easily inspect in person.
They rely on agents and listings alone.
Information asymmetry is the #1 risk.

Slide 3:
[RED FLAG #1: Price History]
Sold price 12% below asking.
Neighborhood average: 4% below.
→ Why is this seller discounting so hard?

Slide 4:
[RED FLAG #2: Ownership Churn]
3 owners in 5 years.
Average hold: 18 months.
→ Why does nobody stay?

Slide 5:
[RED FLAG #3: Supply Pipeline]
3 new developments within 500m.
Future rental competition = compressed yields.
→ Affects your investment math immediately.

Slide 6:
[RED FLAG #4: Flood Risk]
Rating: B (moderate risk).
Not disclosed in the listing.
→ Always check council flood maps.

Slide 7:
[RED FLAG #5: School Enrollment Trends]
Top-rated school zone.
But enrollment down 15% over 3 years.
→ Understand the why before buying for schools.

Slide 8:
[HOW LONG THIS TAKES]
Manual research: 2-3 days.
AI-assisted: 15 minutes.
→ Same flags. Fraction of the time.

Slide 9:
[WHO THIS IS FOR]
Agents serving overseas buyers who can't
be on the ground. This is your due diligence edge.

Slide 10:
[CTA]
Save this checklist.
Comment "FLAG" if you want the full prompt list.
```

---

**Example 3 — Personal Brand**

*Caption:* Bought 4 properties in Australia as a Taiwanese engineer. Here's what nobody told me about the process. #realestate #overseas #investing #proptech

```
Slide 1:
[HOOK]
I bought 4 properties in Australia
as a Taiwanese engineer living abroad.
Here's what nobody warns you about.

Slide 2:
[FIRB — THE FIRST SURPRISE]
Foreign buyers need government approval (FIRB).
Cost: $13,200 AUD on a $1M property.
Timeline: 30 days typical, but can be 6+ months.
→ Budget this before you fall in love with a property.

Slide 3:
[THE FINANCING MAZE]
Australian banks treat overseas income differently.
Some won't lend to non-residents at all.
→ Talk to 3-4 mortgage brokers before you start searching.

Slide 4:
[TIME ZONES KILL DEALS]
Auctions happen on Saturday mornings.
That's Saturday evening Taiwan time.
Deadlines don't care about your timezone.
→ Have a local power of attorney.

Slide 5:
[THE DATA GAP]
Listings look great online.
But comparable sales, flood risk, and
development plans aren't in the listing.
→ You need to dig for the real picture.

Slide 6:
[WHAT AI CHANGED FOR ME]
I can now run a full property analysis
from Taipei in 20 minutes.
Before AI, this took days and local contacts.

Slide 7:
[MY SISTER'S EDGE]
She's a Melbourne agent specializing in
overseas Chinese/Taiwanese buyers.
Using AI, she delivers bilingual market reports
in 45 minutes instead of 4 hours.

Slide 8:
[THE ACTUAL MOAT]
It's not the AI tool.
It's understanding what questions to ask.
And having the context to interpret the answers.

Slide 9:
[CTA]
Save this if you're thinking about buying overseas.
Questions? Drop them in the comments.
I read everything.
```
