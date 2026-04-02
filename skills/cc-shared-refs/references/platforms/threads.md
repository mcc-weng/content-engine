# Threads Module

Scoring criteria: see `scoring-rubric.md`

---

## Format Spec

- **Post type:** Short text posts
- **Target length:** 100-300 characters (this is the sweet spot, not the ceiling)
- **Platform limit:** 500 characters — ceiling, not target
- **Dominant formats:** Conversation starters, hot takes, questions, quick observations
- **Images:** Optional — text-only posts frequently outperform image posts on Threads
- **Language:** Traditional Chinese (primary)

---

## Algorithm Signals

- **Strongest signal:** Replies — conversation depth drives distribution more than any other metric
- **Topic tags:** Generate meaningfully more views — use on every post
- **Suppression trigger:** Low-quality engagement bait gets detected and suppressed
- **Benchmark:** Median engagement rate 6.25% (73% higher than X)
- **Discovery:** Topic tags are the primary organic discovery mechanism

---

## Tone Rules

- **Style:** Conversational, witty, opinion-driven
- **Feel:** Authentic over polished — Threads rewards realness, not production value
- **Formats that work:** Questions, hot takes, observations that invite disagreement or discussion
- **Avoid:** Corporate polish, lectures, one-sided monologues
- **Voice file:** Load `voice-zh.md` → apply `## Threads Adjustments`

---

## Content Strategy

| Content Type | Mix | Audience |
|---|---|---|
| Build updates / AI tools | 40% | Chinese-speaking tech community |
| Overseas property insights | 30% | Chinese-speaking community interested in AU property |
| Hot takes / opinions | 30% | General audience |

- **Channel purpose:** Brand and awareness — NOT sales. Build audience as "Taiwanese AI engineer who understands both sides."
- **Audience:** Chinese-speaking community (Taiwan is Threads' #1 market). Not targeting agents directly.
- **Primary goal:** Start conversations — replies are the growth mechanism

---

## Hashtag Strategy

- **Topic tags:** Use on every post for discovery (Threads calls them "topic tags" not hashtags)
- **Volume:** 1-3 per post — enough for discovery, not so many it looks spammy
- **Examples:** #澳洲買房 #AI工具 #海外買家 #房產 #台灣人

---

## Anti-Patterns

- **"Follow for follow"** or **"Like if you agree"** → engagement bait detection → suppression
- **Identical replies** across multiple threads → detected as bot behavior
- **Scheduling tools** can backfire — Meta's systems detect automation patterns
- **Recovery protocol:** If you suspect shadowban, stop posting for 48 hours, then resume
- **Passive content** (no question or invitation) → fewer replies → weaker reach
- **Over-polished posts** → feels out of place, lower reply rates

---

## Scaffold Adaptation

- **Existing scaffolds + hooks are already optimized for Threads** — maintain existing format
- **Length:** Hard limit at 300 chars; mobile-first pacing (short sentences, line breaks)
- **CTA:** Integrated naturally — end with a question or provocative closer
- **Structure:** Hook → 1-2 key observations → question or hot take close
- **No headers or bullets** — Threads is prose, not structured notes

---

## Example Posts

---

**Example 1 — Conversational Research**

```
用AI幫朋友查了一間雪梨的房子

成交價比掛牌價低了12%，但同一條街其他房子只低了3-5%

為什麼？還沒查到答案

你們遇到這種情況會怎麼做？

#澳洲買房 #海外買家
```

---

**Example 2 — Hot Take**

```
老實說：台灣人在澳洲買房最大的風險不是房價

是資訊不對等

本地人看一眼就懂的東西，你要花好幾天才查得到

AI把這個差距縮短了很多——但前提是你知道要問什麼問題

#海外置業 #AI工具
```

---

**Example 3 — Build Update**

```
幫我姐整合AI進她的工作流程，第一週回報：

原本一份市場報告要4小時
現在45分鐘

她說最大的改變是：不再因為報告太花時間而拒絕客戶了

這才是真正的ROI

#AI工具 #房產代理
```
