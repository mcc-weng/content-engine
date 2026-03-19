# OpenClaw Real Estate Agent Co-Pilot

## Overview

An AI co-pilot for real estate agents serving overseas Chinese/Taiwanese buyers, built on OpenClaw with custom middleware. The agent monitors buyer conversations across WhatsApp, Line, and Email, tracks leads, drafts follow-ups in the buyer's language, and learns to mimic the agent's voice over time.

The first deployment is for Mike's older sister — a Sydney real estate agent specialising in overseas Chinese buyers who loses deals because she forgets to follow up.

## Context

### Why OpenClaw

OpenClaw is an open-source, locally-run AI agent with persistent memory, WhatsApp integration, and 50+ connectors. Rather than building a custom agent from scratch or buying into a platform like Wayscape, we use OpenClaw as the AI brain and build thin middleware around it for channel monitoring, approval workflows, and voice learning.

### Why Not Wayscape

Wayscape is an Australian real estate platform (CRM + off-market listings + AI assistant + training). It's the "Salesforce" approach — broad, platform-first, English-only. We don't compete with Wayscape on listings, CRM, or agent networks. We compete on the communication layer that overseas buyer agents struggle with: multilingual follow-ups, cross-timezone responses, and conversational memory across messaging apps buyers actually use.

**One-liner:** Wayscape is a tool agents log into. This is an AI colleague that lives where they already work — and speaks their buyers' language.

### Beta Client Profile

- Sydney real estate agent, overseas Chinese buyer specialist
- ~200 Instagram, ~300 Facebook, ~598 YouTube followers
- Uses WhatsApp and Line for buyer communication (not WeChat)
- No CRM — works from memory and chat history
- Tech comfort 7/10 — can use a web interface, not terminal/APIs
- Confirmed pain: forgets to follow up with buyers
- Commission ~7% — one lost deal on a $1M property = $70k lost
- <10 active leads at any time
- Has colleagues who reply through her accounts
- Buyer journeys range from days to 6+ months

---

## Architecture

### Approach: OpenClaw Core + Custom Middleware

Use OpenClaw as the AI brain (memory, reasoning, message drafting). Build lightweight middleware for channel monitoring, approval queue, and voice learning.

```
┌─────────────────────────────────────────────────────────┐
│                    Mike's Laptop (Day 1)                 │
│                                                         │
│  ┌──────────────────────────────────────────────┐       │
│  │           Channel Adapters Layer              │       │
│  │                                               │       │
│  │  [WhatsApp Business API] ← monitors convos   │       │
│  │  [Line Official Account] ← monitors convos   │       │
│  │  [Email IMAP listener]   ← monitors inbox    │       │
│  │                                               │       │
│  │  All adapters normalize messages into:        │       │
│  │  { channel, sender, content, timestamp, lang }│       │
│  └──────────────┬────────────────────────────────┘       │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────┐       │
│  │           OpenClaw (AI Brain)                 │       │
│  │                                               │       │
│  │  - Persistent memory (lead profiles)          │       │
│  │  - Conversation context per lead              │       │
│  │  - Follow-up scheduling logic                 │       │
│  │  - Message drafting (Claude under the hood)   │       │
│  │  - Language detection + mirroring             │       │
│  │  - Natural language command parsing           │       │
│  └──────────────┬────────────────────────────────┘       │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────┐       │
│  │         Approval Queue + Voice Store          │       │
│  │                                               │       │
│  │  - Pending messages wait for approve/edit     │       │
│  │  - Agent's edits stored as voice examples     │       │
│  │  - Explicit rules ("never say 您好")          │       │
│  │  - Auto-pilot settings per message type       │       │
│  └──────────────┬────────────────────────────────┘       │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────┐       │
│  │       Command Interface (separate contact)    │       │
│  │                                               │       │
│  │  WhatsApp or Line (TBD — ask sister)          │       │
│  │  - Receives approval requests                 │       │
│  │  - Accepts natural language commands           │       │
│  │  - Lead summaries and daily digests           │       │
│  │  - Auto-pilot toggle                          │       │
│  └──────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Channel adapters are dumb pipes** — normalize messages into a common format. Adding Instagram DMs, iMessage, SMS later is trivial.
2. **OpenClaw is stateful** — holds all lead memory and conversation context. No separate database needed.
3. **Approval queue is custom code, not OpenClaw's** — full control over UX and auto-pilot gating logic.
4. **Voice store is append-only** — every edit and explicit rule stored. OpenClaw pulls from this when drafting.
5. **Deployed on Mike's laptop for Day 1** — migrate to VPS when scaling to multiple clients.

---

## Lead Memory Model

When the agent texts "just talked to Mrs Chen, wants a 3BR in Chatswood under $2M, she's visiting Sydney in April" — OpenClaw parses this into:

```
Lead {
  id: auto-generated
  name: "Mrs Chen"
  preferred_channel: "whatsapp"
  language: "zh-TW"  (detected from conversations)

  // Property preferences
  property_criteria: {
    type: "3BR house"
    location: "Chatswood"
    budget: "< $2M AUD"
  }

  // Relationship context
  stage: "active"          // exploring | active | negotiating | closed | dormant
  temperature: "warm"      // hot | warm | cold
  follow_up_cadence: 5     // days — auto-adjusted by temperature
  next_follow_up: "2026-03-24"

  // Voice + relationship
  tone: "formal"           // learned from conversation history
  notes: "visiting Sydney in April, timezone UTC+8"

  // Conversation history (summarized, not raw)
  last_contact: "2026-03-19"
  last_contact_by: "agent"  // agent | buyer | colleague
  conversation_summary: "Discussed 3BR options in Chatswood..."

  // Multi-channel identity (future-proofed)
  channel_identities: [
    { channel: "whatsapp", identifier: "+61..." }
  ]
}
```

### Temperature and Follow-Up Cadence

| Temperature | Follow-up Cadence | Trigger to Change |
|---|---|---|
| **Hot** — actively buying | Every 2-3 days | Visiting properties, requesting contracts, asking about offers |
| **Warm** — interested, not urgent | Every 5-7 days | Browsing, asking questions, comparing areas |
| **Cold** — long-term / exploratory | Every 2-3 weeks | "Maybe next year", no trip planned, just researching |
| **Dormant** — gone quiet | One final nudge after 30 days, then archive | No response after 3 follow-ups |

OpenClaw auto-adjusts temperature based on conversation signals. The agent can override manually ("Mrs Chen is hot now, she wants to buy this month").

---

## Core Workflows

### Workflow 1: New Lead Capture

```
Buyer messages on WhatsApp/Line/Email
  → Channel adapter normalizes message
  → OpenClaw checks: known lead or new?
  → If new: creates lead profile from first message
  → Sends agent a notification: "New lead: [name], [channel], [language].
     They asked about [topic]. Want me to draft an acknowledgement?"
  → Agent approves/edits → message sent
```

### Workflow 2: Follow-Up Engine

```
Daily at 8am (configurable):
  → OpenClaw scans all leads
  → Identifies leads past their follow-up date
  → For each: drafts a follow-up appropriate to stage/temperature
      - Hot lead: property-specific ("那個Chatswood的房子明天有open house...")
      - Warm lead: check-in + value add ("最近Chatswood有幾個新盤...")
      - Cold lead: light touch ("好久沒聯繫了，澳洲市場最近...")
  → Queues all drafts in approval queue
  → Agent gets one consolidated message: "3 follow-ups ready for review"
  → She approves/edits/skips each one
```

### Workflow 3: After-Hours Smart Reply

```
Buyer messages outside business hours (e.g. 10pm-7am Sydney):
  → Channel adapter catches it
  → OpenClaw drafts acknowledgement in buyer's language:
     "Hi [name], thanks for reaching out. [Agent] will get back to
      you during business hours. In the meantime — are you looking
      to buy soon or still in the research phase?"
  → If auto-pilot ON for after-hours: sends immediately
  → If auto-pilot OFF: queues for approval
  → Buyer's response gets stored, enriches lead profile
```

### Workflow 4: Inbound Message Processing

```
Any buyer message on any monitored channel:
  → Channel adapter normalizes
  → OpenClaw updates lead profile:
     - last_contact = now
     - last_contact_by = "buyer"
     - conversation_summary updated
     - temperature re-evaluated
     - follow_up_cadence adjusted if needed
  → If message needs a response (question, request):
     → Drafts response, queues for approval
  → If message is just info (acknowledgement, "ok thanks"):
     → No draft, just updates the record
```

### Workflow 5: Voice Learning

```
Agent edits a draft before approving:
  → Original draft + edited version stored as a pair
  → Over time, OpenClaw's system prompt includes:
     "Here are 20 examples of how [agent] actually writes..."
  → Drafts progressively match her voice

Agent gives explicit rule ("don't use 您好, I say 嗨"):
  → Stored as hard rule, always applied
  → Hard rules override learned patterns
```

---

## Approval System

### Default Mode: Approval Required

Every outgoing message requires explicit approve/edit/reject before sending. This is the Day 1 default and cannot be changed without the agent explicitly opting in.

### Future Mode: Auto-Pilot (Not Day 1)

After trust is established, the agent can unlock auto-send for specific message types:
- "Turn on auto-pilot for after-hours replies"
- "Turn off auto-pilot"
- "Always ask me before messaging Mrs Chen" (per-lead override)

Architecture supports this from Day 1 — the approval step is a configurable gate, not hardcoded. But the UI to toggle auto-pilot is not built until the agent requests it.

---

## Scope

### Day 1

- OpenClaw deployed on Mike's laptop
- Channel adapters: WhatsApp Business API, Line, Email (IMAP)
- Command interface: separate contact in WhatsApp or Line (ask sister)
- Lead memory with natural language input
- Follow-up engine with temperature-based cadence
- After-hours smart auto-reply with qualifying question
- Approval queue (approval-required for everything)
- Language auto-detection and mirroring
- Voice learning (passive from edits + explicit rules)

### Parked

- Auto-pilot mode
- Facebook Messenger, Instagram DMs, SMS, iMessage monitoring
- CRM integration
- Listing data integration / property matching
- Multi-agent deployment (multiple clients)
- VPS hosting
- Cross-channel identity merging
- Daily digest / reporting
- Web dashboard for reviewing leads

### Open Questions

- Command interface: WhatsApp or Line? (ask sister)
- Business hours definition — what's "after hours"?
- Voice note support — talk to AI instead of typing?

---

## Competitive Positioning

| Dimension | Wayscape | OpenClaw Co-Pilot |
|---|---|---|
| **Approach** | Platform — sign up, log in, learn the UI | Invisible — lives in existing messaging apps |
| **Target** | All Australian real estate agents | Agents serving overseas Chinese/Taiwanese buyers |
| **Language** | English only | Mandarin/English auto-detection and mirroring |
| **Interface** | Web dashboard + CRM | Texts her AI like a colleague |
| **Channel coverage** | Centralized inbox | Monitors WhatsApp, Line, Email — channels overseas buyers actually use |
| **Follow-ups** | Pipeline tracking — shows who's overdue | Drafts the actual message in buyer's language and tone |
| **Learning** | Training modules for agents | AI learns the agent's voice over time |
| **Listings** | Off-market national platform + WayIQ | Not competing here (parked for CRM integration) |
| **Pricing** | SaaS subscription | Done-for-you service ($500-1500 setup + monthly) |
| **Moat** | Platform scale, agent network, data | Niche depth — bilingual, culturally native, built by an overseas buyer |

---

## Success Criteria

- Sister can text the AI on WhatsApp/Line and it understands her commands
- All WhatsApp, Line, and email conversations are monitored and leads tracked
- Follow-up drafts are generated daily for overdue leads in the correct language
- After-hours messages get a smart auto-reply (when auto-pilot enabled)
- Voice quality improves over first 2 weeks of edits
- Sister reports she hasn't forgotten to follow up with any lead since deployment
- Zero messages sent without approval (until auto-pilot explicitly enabled)
