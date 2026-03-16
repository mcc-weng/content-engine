# Real Estate AI Content Strategy: 30-Day Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Launch on 5 platforms Day 1, interview older sister + 2 outside agents, build a follow-up memory tool for older sister (2-day build), post a beta offer by Day 9 and a paid offer by Day 20, end Month 1 with at least 1 paying client and older sister using the tool daily.

**Architecture:** Research-in-public → 3 agent interviews → confirmed pain (follow-up memory) → 2-day MVP build → document everything as content → sell fast. The MVP is an Airtable base + Claude API prompt + WhatsApp/Line reminder. No complex integrations, no restricted APIs.

**Platforms:** RED + Threads (Traditional Chinese), Instagram + X (English, automated), LinkedIn (English, profile only Month 1).

**This plan covers Days 1–30.** Month 2 activations (LinkedIn case study, YouTube/video) are out of scope but noted at the end.

---

## Pre-Launch: Before Day 1

### Task 0: Platform Setup + Instagram Carousel Automation

Complete all of this before posting a single piece of content.

**Account Setup:**

- [ ] **Step 1: Create Xiaohongshu (RED) account 5–7 days before Day 1**
  - RED suppresses posts from brand-new accounts and can shadowban accounts that engage aggressively immediately after creation
  - After creating: browse passively for 2–3 days before following accounts or commenting
  - Username: consistent handle (e.g. `mikeweng_ai`)
  - Bio (Traditional Chinese):
    ```
    🇹🇼 台灣人，在澳洲買了4間房（布里斯本×1 墨爾本×3）
    現在用 AI 幫海外買家的房仲自動化工作流程
    我姐是雪梨海外買家專業房仲，我在幫她建 AI 系統
    全程公開記錄 ↓
    ```
  - Profile photo: real face, approachable
  - Follow 15 accounts in `#澳洲買房` `#海外買房` `#雪梨房產`

- [ ] **Step 2: Create/optimise Instagram account**
  - Switch to Professional/Creator account
  - Same username and profile photo as RED
  - Bio (English — Instagram is your English personal brand):
    ```
    Taiwanese AI engineer 🤖
    Building AI tools for real estate agents with overseas buyers
    Bought 4 properties across Brisbane & Melbourne
    Documenting the build → sister is my first client
    ```

- [ ] **Step 3: Connect Threads to Instagram** (shared login, then customise Threads bio separately)
  - Threads bio (Traditional Chinese — Threads serves Taiwanese audience):
    ```
    台灣人 × AI 工程師
    在澳洲買了4間房，我姐在雪梨做海外買家房仲
    現在用 AI 幫她解決最頭痛的問題
    過程都記錄在這裡
    ```

- [ ] **Step 4: Create/optimise X account**
  - Bio (English):
    ```
    Taiwanese AI engineer
    Building AI tools for real estate agents with overseas Chinese buyers
    Bought 4 properties in Australia — my sister is a Sydney agent
    Documenting the build →
    ```

- [ ] **Step 5: Set up LinkedIn profile**
  - Professional headshot
  - Headline: `AI Engineer | Building automation for real estate agents serving overseas buyers`
  - About:
    ```
    Taiwanese AI engineer based between Taiwan and Melbourne. I've bought
    4 properties across Brisbane and Melbourne, and my older sister is a
    Sydney real estate agent specialising in overseas Chinese and Taiwanese buyers.

    I'm building AI tools that solve the problems generic CRMs miss for
    agents in this niche — multilingual follow-up, timezone-aware
    communication, and buyer qualification in Mandarin.

    Currently documenting the entire journey on Instagram and Xiaohongshu.

    Open to connecting with agents, buyer's agents, and anyone in Australian PropTech.
    ```
  - Connect with 20–30 Australian real estate agents (search: "buyer's agent Sydney", "overseas buyer specialist Australia")
  - **Do not post anything yet — profile only**

**Instagram Carousel Automation:**

- [ ] **Step 6: Set up Instagram Graph API access**
  - Ensure Instagram account is a Business account linked to a Facebook Page
  - Get `INSTAGRAM_BUSINESS_ACCOUNT_ID` from Facebook Developer portal
  - Get `INSTAGRAM_ACCESS_TOKEN` (long-lived token)
  - Store in `.env`: `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`

- [ ] **Step 7: Build carousel posting script**
  - File: `scripts/post-to-instagram.py`
  - Pattern: follow existing `post-to-threads.py` structure
  - Carousel flow: upload each image as media object → create carousel container → publish
  - Required env vars: `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_ACCESS_TOKEN`
  - Test with a 3-slide carousel before Day 1

  ```python
  # Core flow
  def post_carousel(image_urls: list[str], caption: str) -> dict:
      # 1. Upload each image as media object
      media_ids = []
      for url in image_urls:
          res = requests.post(
              f"{BASE_URL}/{ACCOUNT_ID}/media",
              params={"image_url": url, "is_carousel_item": "true", "access_token": TOKEN}
          )
          media_ids.append(res.json()["id"])

      # 2. Create carousel container
      container = requests.post(
          f"{BASE_URL}/{ACCOUNT_ID}/media",
          params={
              "media_type": "CAROUSEL",
              "children": ",".join(media_ids),
              "caption": caption,
              "access_token": TOKEN
          }
      )

      # 3. Publish
      return requests.post(
          f"{BASE_URL}/{ACCOUNT_ID}/media_publish",
          params={"creation_id": container.json()["id"], "access_token": TOKEN}
      )
  ```

- [ ] **Step 8: Update cc-draft skill for multi-platform**
  - Add platform parameter support: `--platform red`, `--platform instagram`, `--platform threads`, `--platform x`
  - RED: long-form Traditional Chinese
  - Instagram: carousel slide text (English)
  - Threads: short Traditional Chinese
  - X: short English build-in-public voice
  - Routing: RED + Threads use `content-voice.md` (Chinese); Instagram + X use English voice

- [ ] **Step 9: Update cc-post skill**
  - Add Instagram carousel posting via `post-to-instagram.py`
  - Add X posting via existing `post-to-x.py`
  - Platform selection at post time

- [ ] **Step 10: Create research notes file**
  ```
  ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/real-estate-research.md
  ```
  With sections: `## Audience Replies`, `## Sister Interview`, `## Outside Agent Interviews`, `## Pain Points (Ranked)`, `## Build Decision`

- [ ] **Step 11: Test full automation pipeline**
  - Draft a test post with cc-draft → post to Instagram + Threads + X
  - Verify formatting on each platform
  - Fix any issues before Day 1

---

## Chunk 1: Launch + Community Seeding (Days 1–7)

### Task 1: Day 1 — All Platforms Live

- [ ] **Step 1: Publish intro posts on all platforms simultaneously**

  **RED (Traditional Chinese, long-form):**
  ```
  我是台灣 AI 工程師，最近在做一件很有意思的事。

  我姐在雪梨做房仲，專門幫海外買家（很多是台灣人）買澳洲房子。

  我發現她每天有很多重複性的工作可以用 AI 自動化——
  但市面上沒有專門為她這種房仲設計的工具。

  所以接下來我要花時間深入研究海外買家房仲到底在痛什麼，
  然後一邊建工具一邊記錄整個過程。

  如果你是海外買家，或認識做這行的房仲，我很想聽你們的故事 👇

  #澳洲買房 #海外買房 #雪梨房產 #AI工具 #澳洲房仲
  ```

  **Instagram (English, carousel):**
  - Slide 1: `I'm a Taiwanese AI engineer. I'm about to change how my sister does real estate.`
  - Slide 2: "My sister is a Sydney agent specialising in overseas Chinese buyers. Her 3 biggest daily frustrations: chasing buyers who go silent / responding to enquiries at 2am / explaining contracts in two languages"
  - Slide 3: "My plan: deeply research the problem → build AI tools to fix it → document everything. Are you an agent dealing with similar issues? 👇"
  - Caption: `Taiwanese AI engineer × Australian real estate — the build starts now. I've bought 4 properties here, my sister sells them. Now I'm building AI to fix what's broken. #PropTech #AItools #RealEstateAI #AustralianProperty`

  **Threads (Traditional Chinese, short):**
  ```
  有點緊張地發這個。

  我姐在雪梨做房仲，專門幫海外買家買澳洲房子。

  我是 AI 工程師。我要幫她用 AI 解決她工作上最頭痛的事。
  整個過程我都會記錄在這裡。

  如果你有買澳洲房的經驗——我很想聽你的故事。
  ```

  **X (English, short):**
  ```
  Starting something new.

  My sister is a Sydney real estate agent specialising in overseas Chinese buyers.

  I'm a Taiwanese AI engineer. I'm going to deeply research her biggest pain points and build AI tools to fix them.

  Documenting everything. Day 1.
  ```

- [ ] **Step 2: Verify all 4 platforms are live with correct formatting**

---

### Task 2: Community Seeding (Days 2–7)

- [ ] **Step 3: Daily engagement routine (repeat every day, 15 min)**
  - RED: Comment on 3–5 posts in `#澳洲買房` `#海外買房` `#雪梨房產` (Traditional Chinese)
  - Instagram: Comment on 3–5 posts from Australian agents or property-related accounts (English)
  - Threads: Reply to 3–5 overseas buyer / Taiwan–Australia property conversations (Traditional Chinese)
  - Save any agents you interact with to a shortlist for interview outreach

- [ ] **Step 4: Day 3 — personal buyer story post (all platforms)**
  - Share your experience buying 4 properties across Brisbane and Melbourne
  - RED (Traditional Chinese): long-form — what was confusing, what you wished existed, specific suburb details
  - Instagram (English): carousel — "4 properties, 2 cities, here's what I learned buying Australian property as an overseas buyer"
  - Threads (Traditional Chinese): short personal take with question at end
  - X (English): one-line hook version

- [ ] **Step 5: Day 5 — audience question post**
  - RED/Threads (Traditional Chinese): `如果你是做海外買家業務的房仲，你最頭痛的一件事是什麼？`
  - Instagram (English): "Agents who work with overseas buyers: what's the #1 thing that wastes your time every week?"
  - X (English): same as Instagram
  - Save every reply to `real-estate-research.md`

- [ ] **Step 6: Days 5–7 — identify 2 outside agents to interview**
  - Review agents who commented on your posts or who you engaged with during seeding
  - Search RED for agents posting about overseas buyers (Chinese-speaking agents)
  - Search Instagram for Australian agents in the overseas buyer segment (English-speaking agents)
  - DM outreach — match the platform language:
    RED/Threads (Traditional Chinese):
    ```
    你好，我是 AI 工程師，正在研究海外買家房仲在工作上最頭痛的問題。
    你願意跟我聊 20 分鐘嗎？
    我想聽聽你的經驗——不是要賣你東西。
    ```
    Instagram (English):
    ```
    Hey, I'm an AI engineer researching the biggest pain points for agents
    who work with overseas buyers. Would you be open to a 20-minute chat?
    I'm genuinely interested in your experience — not trying to sell anything.
    ```
  - Goal: 2 confirmed conversations booked before Day 8
  - If <2 confirmed by Day 7: ask older sister if she can introduce 1 colleague

---

## Chunk 2: Research Phase (Days 8–13)

**Contingency:** If older sister is unavailable before Day 10, post a bridge post: "Still in deep research mode — here's what I've found so far from the audience." Reschedule to Day 12. Do NOT publish the Day 9 beta offer or Day 13 build announcement until the interview is done.

### Task 3: Sister Interview (Day 8–9)

- [ ] **Step 1: Prepare question list** (save to `real-estate-research.md` before call)

  **Workflow questions:**
  1. Walk me through your typical week — what takes the most time?
  2. What task do you dread most on Monday morning?
  3. How many active leads are you managing right now? How do you track them?

  **Pain point questions:**
  4. When a buyer goes quiet for 2–3 weeks, what do you do? Walk me through exactly.
  5. How do you handle inquiries that come in at 2am your time?
  6. When was the last time you forgot to follow up with a buyer? What happened?
  7. How do you explain contracts and strata reports to buyers who don't read English?

  **Tools questions:**
  8. You're not using a CRM — is that intentional? What stops you from using one?
  9. What do you do in WhatsApp/Line that you wish was automatic?
  10. Have you tried any AI tools? What happened?

  **Value questions:**
  11. If I could save you 5 hours a week, what would you want automated first?
  12. How much would it be worth if you never lost a lead to slow follow-up again?
  13. Would you be comfortable mentioning on your Instagram/Facebook that your brother built you an AI tool? (Confirm cross-promotion)

- [ ] **Step 2: Conduct 90-minute interview, take notes in real time**

- [ ] **Step 3: Document findings**
  ```markdown
  ## Sister Interview — [Date]
  ### Top Pain Points (ranked by her emotion)
  1.
  2.
  3.
  ### Confirmed: follow-up memory problem? [Y/N + quote]
  ### WhatsApp vs Line preference: [answer]
  ### Cross-promotion: [willing / not sure / no]
  ### Most surprising finding:
  ### Build decision: [confirmed / fallback 1 / fallback 2]
  ```

### Task 4: Outside Agent Interviews (Days 9–12)

- [ ] **Step 4: Conduct 2 × 20-minute conversations with outside agents**
  - Key questions: same pain point questions from sister interview
  - **Listen for:** do they mention follow-up / forgetting buyers unprompted?
  - Document each in `real-estate-research.md`

- [ ] **Step 5: Validate: do all 3 agents share the same #1 pain?**
  - If yes → proceed to build with confidence
  - If no → note the divergence, weight sister's input most heavily (she's your beta client)

- [ ] **Step 5b: Offer beta access directly to the 2 outside agents**
  - After each interview ends, say: "I'm building this system now and looking for 2 agents to test it for free. Would you be one of them?"
  - If they say yes → they are your beta testers (no need to recruit separately from the Day 9 post)
  - If they say no → the Day 9 post handles external beta recruitment
  - This gives you a warm reason to follow up after the build is done

### Task 5: Research Content + Beta Offer (Days 9–13)

- [ ] **Step 6: Day 9 — publish "first finding" post + beta offer**
  *Note: only publish if sister interview is done. If delayed, publish bridge post instead.*

  **RED:**
  ```
  採訪了我姐（雪梨海外買家專業房仲）90分鐘。

  最讓我意外的發現是：她說她最頭痛的不是語言問題，
  而是——她忘記跟進買家。

  海外買家沉默2週，她也忘了。
  直到買家突然說要看別家了。
  一筆交易就這樣沒了。

  我正在幫她建一個 AI 系統解決這個問題。
  現在在找 2 個願意免費試用的海外買家房仲。
  你只需要給我真實反饋。
  有興趣的話 DM 我 👇

  #澳洲房仲 #海外買家 #AI工具 #雪梨房產
  ```

  **Threads:**
  ```
  跟我姐聊了90分鐘。

  我以為她最頭痛的是語言問題。
  結果不是。

  是她忘記跟進買家。
  沉默了2週，她也忘了。
  買家就跑了。

  這個問題聽起來熟悉嗎？

  我在找2個願意試用 AI 解決方案的海外買家房仲——免費，只需要你的反饋。DM 我。
  ```

- [ ] **Step 7: Day 11 — scope of problem post**
  - Expand the pain: how often does this happen, what's the financial cost of one missed follow-up
  - Anchor to the commission math: one lost deal at 7% commission on $1M property = $70k
  - RED: long-form with numbers
  - Instagram: carousel with the math made visual

- [ ] **Step 8: Days 11–12 — architecture scoping**
  Based on 3 interviews, confirm build decision:
  - Primary: Follow-up memory tool (Airtable + Claude API + WhatsApp/Line reminder)
  - Fallback 1: After-hours auto-responder
  - Fallback 2: Document explanation tool
  Document decision in `real-estate-research.md` under `## Build Decision`

- [ ] **Step 9: Day 13 — build announcement post**
  *(Only after architecture scoped and interviews complete)*

  **RED:**
  ```
  研究了兩週，採訪了3個海外買家房仲。

  三個人都說了同一件事：他們忘記跟進買家。

  我決定要建的第一個 AI 系統是：
  **海外買家跟進提醒 + 自動生成中文訊息**

  具體怎麼運作：
  • 輸入買家資訊 + 上次聯絡時間
  • 系統在買家沉默太久時提醒你
  • 自動生成個性化的中文跟進訊息
  • 你複製貼上到 WhatsApp / Line

  目標：3–5天內給我姐一個可以用的版本。

  #AI開發 #澳洲房仲 #建設中
  ```

---

## Chunk 3: Build + First Delivery (Days 14–21)

### Task 6: Build the MVP (Days 14–16)

**Target: 2-day build. Ship before you're proud of it.**

- [ ] **Step 1: Day 14 — set up project**
  ```bash
  mkdir ~/Desktop/Projects/real-estate-ai
  cd ~/Desktop/Projects/real-estate-ai
  git init
  touch .env README.md
  ```

- [ ] **Step 2: Day 14 — build Airtable base**
  - Table: Leads
  - Fields: Name, Phone/WhatsApp, Line ID, Inquiry Details, Budget, Preferred Suburbs, Language (Mandarin/English), Last Contacted (date), Status (Active/Cold/Qualified), Notes
  - Set up Airtable API key in `.env`

- [ ] **Step 3: Day 14 — build Claude API message generator**
  - File: `generate_followup.py`
  - Input: lead details from Airtable row
  - Output: personalised Mandarin follow-up message
  - Prompt template:

  ```python
  FOLLOWUP_PROMPT = """
  你是一個澳洲房仲的助理。請根據以下買家資訊，
  生成一條自然、溫暖的中文跟進訊息（用繁體中文）。

  訊息要：
  - 不超過100字
  - 提到買家上次詢問的具體細節
  - 自然，不要像是機器人寫的
  - 結尾問一個問題讓買家容易回覆

  買家資訊：
  姓名：{name}
  上次詢問：{inquiry}
  偏好區域：{suburbs}
  預算：{budget}
  上次聯絡：{last_contacted}天前
  """
  ```

- [ ] **Step 4: Day 15 — build reminder check**
  - File: `check_followups.py`
  - Logic: query Airtable for leads where Last Contacted > X days ago AND Status = Active
  - For each: call `generate_followup.py` → **send reminder via email** (default for MVP — zero setup, works Day 1)
  - WhatsApp delivery is a Month 2 upgrade once the tool is proven (Twilio WhatsApp requires Meta Business API template approval — not same-day)
  - X days threshold: ask sister during interview (default: 5 days)

- [ ] **Step 5: Day 15 — build simple runner script**
  - `run_daily.py` — runs the check, generates messages, sends reminders
  - README: step-by-step instructions for sister to add a new lead to Airtable

- [ ] **Step 6: Day 15 — publish build log post**

  **RED:**
  ```
  開始建了。比你想象的簡單多了。

  我姐說她最大的問題是忘記跟進買家。

  所以我不需要建什麼複雜的自動化系統——
  我只需要建一個幫她「記住」的工具。

  架構：
  • Airtable（記錄買家）
  • Claude AI（生成個性化中文訊息）
  • 每天檢查誰沉默太久了 → 自動提醒她

  第一版目標：讓她明天就能開始用

  #AI開發 #澳洲房仲 #建設中
  ```

- [ ] **Step 7: Day 16 — dry run and fix**
  - Add 3 fake leads to Airtable
  - Run `run_daily.py`
  - Check: do the generated messages sound natural? Would sister actually send them?
  - Fix any obvious issues

### Task 7: Demo to Sister + Iterate (Days 17–19)

- [ ] **Step 8: Day 17 — demo session with older sister**
  - Walk her through adding a lead to Airtable
  - Run the daily check in front of her
  - Show her the generated message
  - **Capture her reaction in writing** — write her exact words during/after the call
  - Ask: "Would you use this tomorrow? What feels wrong?"
  - Ask about cross-promotion if not confirmed yet
  - **Have her enter all real current leads immediately** — not test data. With <10 active leads she can do this in 10 minutes. Real leads in the system from Day 17 = at least one real usage event before the Day 26 check-in, which means real numbers for the case study.

- [ ] **Step 9: Day 17 — publish demo reaction post**

  **Threads:**
  ```
  今天給我姐看了我建的東西。

  她的第一反應：「[她說的話]」

  [她喜歡的部分]
  [她覺得需要改的部分]

  這就是為什麼要早點讓真實用戶看，
  而不是在腦子裡想象什麼是好的。

  下一步：[具體改動]
  ```

- [ ] **Step 10: Days 18–19 — fix top 2 issues from sister's feedback**
  - Only fix what stops her from using it daily
  - Don't rebuild. Two targeted fixes max.

- [ ] **Step 11: Day 19 — deliver final version to sister**
  - Send README with clear instructions
  - Set a check-in for Day 26 to review real usage
  - Ask sister: are you comfortable posting about this on your Instagram/Facebook?

### Task 8: Day 15 Pulse Check

- [ ] **Step 12: Day 15 — pulse check (hard stop, 30 min)**
  Answer these three questions honestly:
  1. Have any agents commented, DM'd, or replied — even just "interesting"?
  2. Which platform is getting the most engagement?
  3. Do outside agents mention the same pain as sister?

  If all three are no/flat:
  - Change the hook on the next 3 RED posts (try a different angle — buyer perspective vs agent perspective)
  - Post more specifically: name the exact pain, name the exact loss ("一筆$70萬的佣金")
  - Do NOT wait until Day 30 to adjust

- [ ] **Step 12b: Set your paid offer price before Day 20**
  - Decision must be made at Day 15 — not Day 19
  - Anchor: at 7% commission on a $1M property = $70k per deal. Your tool protects that.
  - Suggested range: $800–$1500 for the first client (confident but accessible)
  - Pick one number. A specific price converts better than a range.
  - Write the exact number into the Day 20 post draft today so you're not deciding under pressure

---

## Chunk 4: First Paid Offer + Month 1 Wrap (Days 20–30)

### Task 9: First Paid Offer (Day 20)

- [ ] **Step 1: Day 20 — publish paid offer post**

  **RED:**
  ```
  幫我姐建好了。

  她說：「[原文引用]」

  如果你是做海外買家的澳洲房仲，我可以幫你建同樣的系統。

  具體是這樣的：
  • AI自動提醒你哪個買家沉默太久了
  • 幫你生成個性化的中文跟進訊息
  • 你複製貼上到 WhatsApp / Line

  費用：$[X]
  交付時間：3天
  不好用：全退

  有興趣的話 DM 我。找2個人。
  ```

  **Threads:**
  ```
  幫我姐建好了。

  她說：「[原文引用]」

  現在找2個願意付費的海外買家房仲——
  我可以幫你建同樣的系統。

  $[X]，3天交付，不好用全退。

  DM 我。
  ```

- [ ] **Step 2: DM the agents who engaged with your research posts**
  - Everyone who commented, replied, or DM'd in the last 3 weeks
  - Message: `你好，我剛幫我姐建好了那個 AI 跟進系統，她說還不錯。如果你有興趣我可以幫你也建一個。`
  - Goal: 5+ outreach DMs sent on Day 20

### Task 10: Sister Cross-Promotion (Day 22, if confirmed)

- [ ] **Step 3: If sister confirmed cross-promotion — coordinate her post**
  - She posts on her Instagram/Facebook: "My brother built me an AI tool to help with overseas buyer follow-ups. Testing it now — so far [reaction]."
  - Tag Mike's Instagram
  - This seeds Mike's account with her 200 Instagram + 300 Facebook followers
  - Mike reposts/shares on his Instagram

- [ ] **Step 4: If sister did NOT confirm — skip this task**
  - Not a failure, just don't have this asset yet
  - Add to Month 2: after she's been using it for 2 weeks and has results, ask again

### Task 11: Month 1 Wrap-Up (Days 26–30)

- [ ] **Step 5: Day 26 — sister check-in**
  - Has she been using the tool daily?
  - What's actually changed in her workflow?
  - Any deals followed up that she would have forgotten?
  - Collect this as case study material — exact numbers if possible

- [ ] **Step 6: Day 30 — publish Month 1 recap on all platforms**

  **RED (long-form):**
  ```
  第一個月總結

  30天前我決定深入研究海外買家房仲的痛點，然後用 AI 幫他們解決。

  這是我做到的事：
  ✅ 採訪了3個海外買家房仲（包括我姐）
  ✅ 確認了核心問題：忘記跟進買家
  ✅ 建了一個 AI 跟進提醒系統
  ✅ 交付給我姐，她說：「[引用]」
  ✅ 發出了第一個付費報價

  這是我沒做到的事：
  ❌ [誠實列出]

  最大的意外：[一個真實洞察]

  下個月計畫：[1–2件事]

  如果你是做海外買家的房仲，我們來聊聊。
  ```

  Instagram: Carousel version — visual arc of the month
  Threads: Short personal version in Traditional Chinese
  X: English build-in-public version with numbers

- [ ] **Step 7: DM every agent who engaged this month**
  - Short message: `謝謝你這個月的互動。我剛交付了第一個版本，有興趣的話很樂意聊聊。`
  - If fewer than 5 agents engaged total: add to Month 2 outreach backlog — normal for a new account

- [ ] **Step 8: Month 2 readiness check**
  Confirm YES/NO for each Month 2 activation:
  - **LinkedIn posting:** Do you have a case study quote from sister? If yes → write the LinkedIn post and schedule for Month 2 Week 1
  - **YouTube/video:** Are you back in Melbourne (or comfortable on camera from Taiwan)? If yes → plan first video topic
  - **Add agents:** Do you have 1+ paying client or strong interest? If yes → replicate for second client immediately

---

## Daily Rhythm

**Every day (15 min):**
- Check and reply to all comments/DMs on RED, Instagram, Threads
- Respond to every comment in Weeks 1–2 — builds algorithm trust and real relationships
- Save agent interactions to `real-estate-research.md`

**Posting cadence — minimum per platform per week:**

| Platform | Min posts/week | Who manages |
|---|---|---|
| RED | 5–7 | Manual (you) |
| Instagram | 3–5 | Automated from RED |
| Threads | 3–5 | Automated from RED |
| X | 3–5 | Automated (English adapted) |

**Audience + language per platform:**
- RED (Traditional Chinese): 70% buyer-facing, 30% agent-facing
- Instagram (English): 70% agent-facing, 30% personal brand
- Threads (Traditional Chinese): 60% buyer-facing, 40% casual updates
- X (English): 100% build-in-public / AI community

**Weekly review (Sunday, 30 min):**
- What performed best this week?
- 1 insight to amplify next week
- On track for weekly success criteria?

---

## Success Criteria

| Milestone | Target Date | Day 0 Baseline | Check |
|---|---|---|---|
| All 5 platforms live | Day 1 | 0 platforms | Posts published, profiles complete |
| Instagram carousel automation working | Pre-launch | Manual only | Test post successful |
| 2 outside agents booked for interviews | Day 7 | 0 interviews | Calendar invites sent |
| Sister interview + 2 outside interviews done | Day 12 | 0 interviews | Notes in research file |
| Beta offer posted | Day 9 | 0 offers | Post live, DMs open |
| Build announced | Day 13 | No code | Announcement post live |
| MVP delivered to sister | Day 19 | No tool | Sister using Airtable |
| Paid offer posted | Day 20 | 0 paid offers | Post live on RED + Threads |
| Day 15 pulse check done | Day 15 | No data | Adjustments made if needed |
| First paying client | By Day 30 | 0 clients | Invoice sent or agreed |
| Month 1 recap published | Day 30 | 0 recaps | Live on all platforms |

---

## What NOT to Do in Month 1

- **No Simplified Chinese** — Traditional Chinese everywhere, authentic to your identity
- **No LinkedIn posting** — profile only; save it for the case study in Month 2
- **No video yet** — defer Reels/YouTube to Month 2 after validating demand
- **No WeChat integration** — WhatsApp/Line only; WeChat API is restricted and not needed
- **No complex MVP** — if it takes more than 3 days to build, cut scope
- **No waiting until Day 30 to adjust** — Day 15 pulse check is mandatory
- **No announcing the build before architecture is scoped** — scoping on Days 11–12, announcement Day 13
- **No assuming sister's cross-promotion** — confirm during the interview, don't plan around it until confirmed

---

## Month 2 Activations (Out of Scope for This Plan)

- **LinkedIn:** Write case study post using sister's real numbers. Connect with 50+ Australian agents. Activate paid DM outreach to agents in the overseas buyer niche.
- **YouTube/Reels:** First video topic: "How I built an AI follow-up system for a Sydney real estate agent in 3 days." Comfortable on camera — start here.
- **Productized offer:** Package the build as a fixed-price service: "AI follow-up system for overseas buyer agents — $1200, delivered in 3 days."
- **Second client:** Replicate for outside agent who showed strongest interest in Month 1.
