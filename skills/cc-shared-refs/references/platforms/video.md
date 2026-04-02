# Video Script Module

Scoring criteria: see `scoring-rubric.md`

---

## Format Spec

- **Post type:** Short-form video script (talking head + visual inserts)
- **Output:** Two scripts per invocation — one EN, one ZH (Traditional Chinese)
- **Length:** Flexible — default 60s, max 3 minutes
- **Language:** EN script for TikTok, Instagram Reels, YouTube Shorts. ZH script for RED video notes.
- **Visual cue tags:** `[TALKING HEAD]`, `[SHOW: description]`, `[SCREEN RECORDING: description]`, `[TEXT ON SCREEN: text]`

### Length Guidelines

| Target Length | ~Words (EN) | ~Characters (ZH) | When to Use |
|--------------|-------------|-------------------|-------------|
| 30s | 75 | 150 | Hot takes, single punchy insight |
| 60s (default) | 150 | 300 | Most topics — one idea, one demo |
| 90s | 225 | 450 | Tutorials with multi-step demos |
| 3min (max) | 450 | 900 | Deep walkthrough, complex build |

### Script Structure

Every script follows this structure:

1. **Hook (0-3s)** — The scroll-stopper. Under 8-10 words EN / 15-20 characters ZH.
2. **Setup (3-10s)** — The problem or context. Why should they care?
3. **Body** — The meat. Demo, explanation, story. Alternate talking head with visual proof.
4. **CTA** — Natural closer. What should they do or take away?

### Visual Cue Rules

- Every visual cue must have a description specific enough to find or record later
- BAD: `[SHOW: screenshot]`
- GOOD: `[SHOW: screenshot of Vercel deploy success page with 0 errors]`
- No more than 20 seconds of unbroken `[TALKING HEAD]` — alternate with visual proof
- `[TEXT ON SCREEN: text]` for key phrases, stats, or terms viewers should remember

---

## Algorithm Signals

| Platform | Primary Signal | Implication |
|----------|---------------|-------------|
| TikTok | Completion rate | Front-load value. No slow intros. If they leave at 3s, nothing else matters. |
| Instagram Reels | Shares + saves | Make it useful enough to save. Referenceable. Teach something concrete. |
| YouTube Shorts | Completion rate + subscribes | Hook hard, deliver value, end with reason to subscribe. |
| RED (video notes) | Save rate + comment depth | Educational tone. Show real results. Informative > entertaining. |

**Cross-platform truth:** The hook is everything. All four platforms weight the first 1-3 seconds heavily. If the hook doesn't land, the algorithm buries the video regardless of how good the body is.

---

## Tone Rules

### EN Script (TikTok, Reels, Shorts)

- **Style:** Direct, build-in-public, conversational — like explaining to a smart friend
- **Feel:** Energetic but not performative. Genuine excitement, not hype.
- **Pacing:** Speak in short sentences. Pause before key reveals. Let screenshots breathe.
- **Voice file:** Load `voice-en.md` (no platform subsection — video is cross-platform)
- **Humanizer:** Load `humanizer-en.md`

### ZH Script (RED video notes)

- **Style:** 台灣人口吻, informative but personal — like sharing a discovery with a friend
- **Feel:** Excited builder energy, not teacher energy. 你一定要看這個 > 今天來教大家
- **Pacing:** Short sentences. Let visuals carry complexity. Don't over-explain.
- **Voice file:** Load `voice-zh.md` → apply `## RED Adjustments`
- **Humanizer:** Load `humanizer-zh.md`

### Both Languages

- NEVER start with "Hey guys" / "大家好" — waste of hook time
- NEVER use "in this video I'm going to..." — just start with the value
- NEVER end with generic "follow for more" — CTA must be specific to the content
- Contractions always in EN (don't, can't, I'm)
- Traditional Chinese always in ZH — Mike is Taiwanese

---

## Content Strategy

Video scripts share the same topic as text posts for the day. The video adds a visual dimension — demos, screenshots, screen recordings — that text posts can't provide.

| Content Type | Video Format | Visual Inserts |
|---|---|---|
| Build logs | Screen recording of the thing working | Deploy screens, dashboards, before/after |
| AI tutorials | Step-by-step demo | Terminal, IDE, config files |
| Hot takes | Talking head heavy | Maybe 1-2 screenshots as evidence |
| The journey | Mix of talking head and proof | Screenshots of metrics, messages, progress |

---

## Anti-Patterns

- ❌ Reading from a script robotically — write for spoken delivery, not reading
- ❌ Long unbroken talking head segments (>20s) — viewers lose interest
- ❌ Vague visual cues ("show something here") — be specific or cut it
- ❌ Multiple CTAs — one clear ask, not "like subscribe comment and follow"
- ❌ Slow reveal / burying the lead — front-load the payoff
- ❌ Translating EN→ZH literally — write native ZH from scratch
- ❌ Same energy for both languages — ZH for RED should be more structured/informative than EN

---

## Dual-Language Rules

The ZH script is a **native rewrite**, not a translation. Rules:

1. Start from the same topic and visual cues
2. Write the ZH script independently following `voice-zh.md`
3. Cultural references can differ (EN: "FAANG" → ZH: "大廠")
4. ZH can restructure the order if it flows better in Chinese
5. Both scripts use the same `[SHOW:]` and `[SCREEN RECORDING:]` cues — the visuals are shared, the words are not

---

## Example Scripts

### EN Example (60s — Build Log)

```
# Built an AI employee for my sister's real estate business

**Language:** EN
**Target Length:** 60s
**Pillar:** What I Built

## Hook (0-3s)
[TALKING HEAD]
"My sister's a real estate agent. She was spending 3 hours a day on WhatsApp follow-ups."

## Setup (3-10s)
[TALKING HEAD]
"So I built her an AI co-pilot that drafts messages for her — in the buyer's language."

## Body
[SHOW: screenshot of WhatsApp conversation with AI-drafted message]
"It reads the conversation, pulls up the lead's profile, and writes a follow-up that sounds like her."

[SCREEN RECORDING: Telegram approval flow — message arrives, agent taps approve]
"She gets the draft on Telegram. One tap to approve, one tap to send."

[TALKING HEAD]
"Took her from 3 hours to 20 minutes a day."

## CTA
[TALKING HEAD]
"Building this open source. Link in bio if you want to try it."
```

### ZH Example (60s — Build Log)

```
# 幫我姐做了一個 AI 房產助理

**Language:** ZH
**Target Length:** 60s
**Pillar:** What I Built

## Hook (0-3s)
[TALKING HEAD]
"我姐是墨爾本的房產經紀，每天花三小時回 WhatsApp。"

## Setup (3-10s)
[TALKING HEAD]
"所以我幫她做了一個 AI 助理，自動用買家的語言寫回覆。"

## Body
[SHOW: screenshot of WhatsApp conversation with AI-drafted message]
"它會讀對話紀錄、查買家檔案，然後用我姐的口氣寫訊息。"

[SCREEN RECORDING: Telegram approval flow — message arrives, agent taps approve]
"草稿送到 Telegram，一鍵核准、一鍵發送。"

[TALKING HEAD]
"每天三小時變二十分鐘。"

## CTA
[TALKING HEAD]
"開源專案，有興趣的連結在 bio。"
```

---

## Scoring

Uses the standard 3-pillar model from `scoring-rubric.md` (Hook / Retention / CTA). No video-specific calibration yet — will be added after real-world usage data.
