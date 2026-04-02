# RED (Xiaohongshu) Module

Scoring criteria: see `scoring-rubric.md`

---

## Format Spec

- **Post type:** Long-form image-text notes
- **Length:** 600-800 characters (hard minimum 300 for shorter topics)
- **Originality:** 60%+ required — do not copy-paste from other platforms
- **Cover image:** 3:4 vertical ratio, bold text overlay, subject occupies 70% of frame, resolution 1080P+
- **Title:** First 18 characters carry maximum weight — embed 2 core keywords in opening 10 characters
- **Body structure:** Hook → context → value delivery → engagement question → hashtags
- **Image creation:** Manual — engine outputs post text and title only

---

## Algorithm Signals

- **CES scoring:** Click-through rate + completion rate + interaction value
- **Signal hierarchy:** Saves > shares > comments > likes (saves are the strongest signal)
- **Initial distribution:** 200-500 test impressions per post; engagement in first 2 hours determines broader push
- **Search traffic:** ~50% of total RED traffic comes from search — title front 10 characters carry 60%+ weight for search ranking
- **Account age bonus:** Accounts active 180+ days receive additional exposure
- **Keyword matching:** RED search indexes titles and body — use region + audience + scenario keyword combinations

---

## Tone Rules

- **Style:** KOC (Key Opinion Consumer) — authentic, personal, detailed honest review voice
- **Feel:** Practical, actionable, relatable, down-to-earth
- **Avoid:** Corporate language, overly polished marketing tone, superlatives, hype
- **Voice file:** Load `voice-zh.md` → apply `## RED Adjustments`

---

## Content Strategy

| Content Type | Mix | Audience |
|---|---|---|
| Research drops | 25% | Buyers |
| Build logs | 30% | Buyers + agents |
| Buyer guides | 25% | Buyers |
| Case studies + offers | 20% | Agents |

- **Audience split:** 70% buyer-facing, 30% agent-facing
- **Primary persona:** Overseas Chinese/Taiwanese buyers researching Australian property

---

## Hashtag Strategy

- **Volume:** 1-2 precise keyword tags + 3-5 long-tail tags
- **Formula:** Region + audience + scenario combinations
- **Examples:** #澳洲買房 #海外買家 #雪梨房產 #台灣人移民 #澳洲置業 #墨爾本房產 #海外置業攻略
- Build a personal keyword library — reuse high-performing tags

---

## Anti-Patterns

- **Superlatives** ("全網最好用", "行業最低價", "最便宜") → direct traffic throttling
- **Contact info** (WeChat ID, phone number, email) in post body → traffic diversion violation
- **External URLs** or QR codes → violation, post gets suppressed
- **Other platform watermarks** (TikTok watermark, Instagram handles) → RED flags cross-platform reposts
- **Fake personas** without evidence or verification → flagged by trust system
- **Excessive ads** without disclosure → policy violation

**AI labeling note:** RED policy requires labeling AI-assisted content ("AI輔助創作"). Content that goes through brainstorm → draft → human edit → manual posting is sufficiently modified to meet the spirit of this policy. Note for awareness — not a hard gate on posting.

---

## Scaffold Adaptation

- **Format:** Long-form note with section headers using emoji bullets (✅ 📌 🔑 etc.)
- **Hook:** Title must open with 2 core keywords in first 10 characters — answers "who is this for + what will I learn"
- **Body:** Follows scaffold flow but expanded to 600+ characters; use numbered lists, line breaks, concrete details
- **Close:** Engagement question (invites saves + comments) + hashtag block

---

## Example Posts

---

**Example 1 — Research Drop (買家向)**

```
【澳洲買房避坑】AI幫我查出來的5個紅旗信號 🚩

上個月幫朋友看一套雪梨西區的house，傳統方式看起來沒問題，但我用AI工具跑了一遍數據之後，發現幾個細節很值得注意：

1️⃣ 成交價比掛牌價低了12%，但同街道其他房子只低了3-5%——說明這間有定價問題，值得深挖原因

2️⃣ 過去5年轉手了3次，平均持有期18個月——業主為什麼不長持？有沒有我們不知道的問題？

3️⃣ 周邊500m內在建項目3個，未來供應量大，租金壓力不小

4️⃣ 學區校名氣不小，但最近入學率下降了——要查清楚是什麼原因

5️⃣ 洪水風險評級B（中等），但這個信息在掛牌頁面上根本看不到

這些資料用AI彙整只需要幾分鐘，但如果靠人工一個一個查可能要花好幾天。

海外買家資訊不對等是最大的風險，用AI補齊這個缺口是我最近學到最有用的一件事。

你們買房前都會做哪些功課？留言分享一下 👇

#澳洲買房 #海外買家 #雪梨房產 #買房避坑 #AI工具 #海外置業攻略
```

---

**Example 2 — Buyer Guide (攻略向)**

```
【台灣人在澳洲買房】完整流程我幫你整理好了 📋

作為一個在澳洲買了4間房的台灣人，我發現很多同胞在買第一間的時候都踩了同樣的坑。

整個流程大概長這樣：

🔍 第一步：資格確認
海外買家需要申請FIRB（外國投資審查委員會）批准，費用依房價而定，通常$10,000-$15,000 AUD。新建案比中古屋好過。

📊 第二步：市場研究
這步很多人做不夠深。我現在的做法是用AI工具分析：過去12個月成交價趨勢、租金回報率、空置率、基礎建設計劃。

💰 第三步：貸款前置作業
澳洲銀行對海外買家貸款比較嚴格，建議同時接觸3-4家broker。台灣的收入認定方式也不一樣，要問清楚。

🏠 第四步：找房 + 盡職調查
找有服務海外華人經驗的代理，不要只看網路上的listing。看屋前先用AI跑一遍數據，帶著問題去看。

📝 第五步：簽約 + 交割
澳洲房產用律師（conveyancer）做交割，費用約$1,500-$3,000。海外買家記得提前開好澳洲銀行帳戶。

有任何問題歡迎留言，我盡量回 🙌

#台灣人移民 #澳洲置業 #海外買房攻略 #FIRB #澳洲移民
```

---

**Example 3 — Build Log (工具向)**

```
【老實說】我姐用AI做客戶報告，省了多少時間？

我姐在雪梨做房產代理，專門服務海外華人買家。上個月我幫她把AI工具整合進她的工作流程，今天來分享一下真實數據。

改變前：
- 每份客戶市場報告需要3-4小時
- 主要時間花在找數據、翻譯、整理格式
- 一周最多做5-6份報告

改變後：
- 同樣的報告只需要45分鐘
- AI負責抓數據、初步分析、生成中文摘要
- 她專注在解讀數據和客戶溝通
- 一周可以做15份以上

重點不是「AI取代她」，而是讓她可以服務更多客戶、做更高質量的分析。

她說最大的改變是：不再因為報告太花時間而拒絕潛在客戶。

這個故事讓我更確定我在做的事情是對的。

有在做房產的朋友嗎？你們目前最花時間的工作是什麼？

#澳洲房產 #AI工具 #房產代理 #效率工具 #海外買家服務
```
