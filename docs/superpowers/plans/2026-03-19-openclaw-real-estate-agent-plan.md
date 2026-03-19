# OpenClaw Real Estate Agent Co-Pilot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy an AI co-pilot that monitors a real estate agent's buyer conversations across WhatsApp, Line, and Email — tracking leads, drafting follow-ups in the buyer's language, and learning the agent's voice over time.

**Architecture:** OpenClaw serves as the AI brain (memory, reasoning, drafting) and command interface (agent chats with it). Custom Node.js middleware monitors buyer conversations via Baileys (WhatsApp), Line Messaging API, and IMAP (Email), feeding messages into OpenClaw via its webhook API. An approval queue gates all outgoing messages.

**Tech Stack:** OpenClaw (AI agent framework), Node.js, Baileys (WhatsApp Web protocol), Line Messaging API SDK, IMAP client (imapflow), SQLite (approval queue + voice store), Claude API (via OpenClaw)

**Spec:** `docs/superpowers/specs/2026-03-19-openclaw-real-estate-agent-design.md`

---

## Critical Discovery: OpenClaw Cannot Monitor Conversations

OpenClaw's WhatsApp integration only processes messages sent **directly to the bot**. It cannot monitor the agent's conversations with buyers. Line is not a supported channel at all.

**Impact on architecture:**
- Channel monitoring is 100% custom code (not OpenClaw's channel system)
- OpenClaw = AI brain + command interface only
- Custom middleware monitors channels and feeds into OpenClaw via webhook API (`POST /hooks/agent`)
- OpenClaw processes the message, updates memory, and responds via the command channel

This was anticipated by the spec's "Approach 2: OpenClaw Core + Custom Middleware" — but the middleware scope is larger than initially assumed.

---

## File Structure

```
~/Desktop/Projects/re-copilot/
├── package.json
├── tsconfig.json
├── .env                          # API keys, credentials
├── .env.example                  # Template without secrets
├── src/
│   ├── index.ts                  # Entry point — starts all services
│   ├── config.ts                 # Loads env vars, validates config
│   ├── types.ts                  # Shared types (NormalizedMessage, Lead, etc.)
│   ├── db.ts                     # SQLite database initialization
│   ├── adapters/
│   │   ├── base.ts               # Base adapter interface
│   │   ├── whatsapp.ts           # Baileys-based WhatsApp monitor
│   │   ├── line.ts               # Line Messaging API monitor
│   │   ├── email.ts              # IMAP email monitor
│   │   └── adapter-manager.ts    # Starts/stops all adapters, routes messages
│   ├── brain/
│   │   ├── openclaw-bridge.ts    # Sends messages to OpenClaw via webhook API
│   │   └── prompts.ts            # System prompts for lead parsing, drafting, etc.
│   ├── approval/
│   │   ├── queue.ts              # SQLite-backed approval queue
│   │   └── approval-handler.ts   # Handles approve/edit/reject from command channel
│   ├── voice/
│   │   ├── store.ts              # SQLite-backed voice example + rule store
│   │   └── voice-prompt.ts       # Builds voice context for drafting prompts
│   ├── leads/
│   │   ├── store.ts              # SQLite-backed lead storage (backup for OpenClaw memory)
│   │   └── follow-up-scheduler.ts # Cron-based follow-up scan
│   └── utils/
│       └── logger.ts             # Structured logging
├── skills/
│   └── re-copilot/
│       └── SKILL.md              # OpenClaw skill definition for RE co-pilot behavior
├── tests/
│   ├── adapters/
│   │   ├── whatsapp.test.ts
│   │   ├── line.test.ts
│   │   └── email.test.ts
│   ├── approval/
│   │   └── queue.test.ts
│   ├── voice/
│   │   └── store.test.ts
│   ├── leads/
│   │   ├── store.test.ts
│   │   └── follow-up-scheduler.test.ts
│   ├── brain/
│   │   └── openclaw-bridge.test.ts
│   └── integration/
│       └── smoke.test.ts
├── data/
│   └── re-copilot.db             # SQLite database (created at runtime)
└── backup/
    └── backup.sh                 # Daily backup script for data + OpenClaw memory
```

---

## Task 0: Technical Validation Spike (GATE — do this first)

**Purpose:** Verify OpenClaw capabilities before committing to the full build. If 3+ items fail, pivot to custom agent with Claude API directly.

**Files:**
- None — this is exploratory

- [ ] **Step 1: Install OpenClaw**

```bash
npm install -g openclaw@latest
openclaw --version
```

Expected: Version number printed. Requires Node >= 22.

- [ ] **Step 2: Run onboarding wizard**

```bash
openclaw onboard
```

Follow prompts. Set up with Anthropic API key (Claude). Skip channel setup for now.

- [ ] **Step 3: Test persistent memory**

Chat with OpenClaw:
```
"Remember that Mrs Chen wants a 3BR in Chatswood under $2M"
```

Close and reopen OpenClaw. Ask:
```
"What does Mrs Chen want?"
```

Expected: It recalls the information. If not, mark "Persistent memory" as FAILED.

- [ ] **Step 4: Test webhook API**

```bash
# Check if gateway is running
curl http://localhost:18789/health

# Send a test message via webhook
curl -X POST http://localhost:18789/hooks/agent \
  -H "Content-Type: application/json" \
  -d '{"text": "A new buyer just messaged: Hi, I am looking for 2BR in Sydney under 1.5M", "deliver": true}'
```

Expected: OpenClaw processes the message and responds on its default channel. If webhook endpoint doesn't exist, mark "Webhook API" as FAILED.

- [ ] **Step 5: Test WhatsApp channel (OpenClaw's built-in)**

```bash
openclaw channels login whatsapp
```

Scan QR code. Send a test message to OpenClaw from another phone.

Expected: OpenClaw receives and responds. This confirms the command interface works via WhatsApp. Note: This is for the command channel only, not for monitoring buyer conversations.

- [ ] **Step 6: Test custom skill loading**

Create `~/.openclaw/skills/test-skill/SKILL.md`:

```markdown
---
name: test-skill
description: Test skill for validation
---

When the user says "test skill", respond with "Skill loaded successfully!"
```

Restart OpenClaw and say "test skill".

Expected: Custom response. If not, mark "Custom skills" as FAILED.

- [ ] **Step 7: Document results and decide**

Create a file `docs/spike-results.md` with pass/fail for each capability. If 3+ fail, pivot plan. Commit results.

```bash
git add docs/spike-results.md
git commit -m "docs: OpenClaw technical validation spike results"
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `~/Desktop/Projects/re-copilot/package.json`
- Create: `~/Desktop/Projects/re-copilot/tsconfig.json`
- Create: `~/Desktop/Projects/re-copilot/.env.example`
- Create: `~/Desktop/Projects/re-copilot/.gitignore`
- Create: `~/Desktop/Projects/re-copilot/src/types.ts`
- Create: `~/Desktop/Projects/re-copilot/src/config.ts`
- Create: `~/Desktop/Projects/re-copilot/src/index.ts`
- Create: `~/Desktop/Projects/re-copilot/src/utils/logger.ts`

- [ ] **Step 1: Initialize project**

```bash
mkdir -p ~/Desktop/Projects/re-copilot
cd ~/Desktop/Projects/re-copilot
git init
npm init -y
```

- [ ] **Step 2: Install dependencies**

```bash
npm install @whiskeysockets/baileys @line/bot-sdk@7 imapflow better-sqlite3 node-cron dotenv zod pino @hapi/boom
npm install -D typescript @types/node @types/better-sqlite3 @types/node-cron vitest tsx pino-pretty
```

- [ ] **Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "declaration": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

- [ ] **Step 4: Create .env.example**

```env
# OpenClaw
OPENCLAW_GATEWAY_URL=http://localhost:18789
OPENCLAW_WEBHOOK_SECRET=

# WhatsApp (Baileys — no API key needed, uses QR code pairing)
WHATSAPP_ENABLED=true

# Line
LINE_CHANNEL_ACCESS_TOKEN=
LINE_CHANNEL_SECRET=
LINE_ENABLED=false

# Email
IMAP_HOST=
IMAP_PORT=993
IMAP_USER=
IMAP_PASSWORD=
EMAIL_ENABLED=true

# General
BUSINESS_HOURS_START=07
BUSINESS_HOURS_END=22
TIMEZONE=Australia/Sydney
```

- [ ] **Step 5: Create .gitignore**

```
node_modules/
dist/
data/
.env
auth_info_baileys/
```

- [ ] **Step 6: Create src/types.ts**

```typescript
export interface NormalizedMessage {
  id: string;
  channel: "whatsapp" | "line" | "email";
  sender: string;
  senderName?: string;
  content: string;
  timestamp: Date;
  lang?: string;
  direction: "inbound" | "outbound";
  messageType: "text" | "image" | "voice" | "document" | "other";
  threadId?: string;
  raw?: unknown;
}

export interface Lead {
  id: string;
  name: string;
  preferredChannel: NormalizedMessage["channel"];
  language: string;
  propertyCriteria: {
    type?: string;
    location?: string;
    budget?: string;
  };
  stage: "exploring" | "active" | "negotiating" | "closed" | "dormant";
  temperature: "hot" | "warm" | "cold";
  followUpCadenceDays: number;
  nextFollowUp: string; // ISO date
  tone?: string;
  notes?: string;
  lastContact: string; // ISO date
  lastContactBy: "agent" | "buyer" | "colleague";
  conversationSummary?: string;
  channelIdentities: Array<{
    channel: NormalizedMessage["channel"];
    identifier: string;
  }>;
  createdAt: string;
  updatedAt: string;
}

export interface ApprovalItem {
  id: string;
  leadId: string;
  draftMessage: string;
  channel: NormalizedMessage["channel"];
  recipientId: string;
  type: "follow_up" | "after_hours_reply" | "response";
  status: "pending" | "approved" | "edited" | "rejected";
  editedMessage?: string;
  createdAt: string;
  resolvedAt?: string;
}

export interface VoiceExample {
  id: string;
  originalDraft: string;
  editedVersion: string;
  language: string;
  createdAt: string;
}

export interface VoiceRule {
  id: string;
  rule: string;
  createdAt: string;
}
```

- [ ] **Step 7: Create src/config.ts**

```typescript
import { config as loadEnv } from "dotenv";
import { z } from "zod";

loadEnv();

const envSchema = z.object({
  OPENCLAW_GATEWAY_URL: z.string().default("http://localhost:18789"),
  OPENCLAW_WEBHOOK_SECRET: z.string().optional(),
  WHATSAPP_ENABLED: z.string().default("true"),
  LINE_CHANNEL_ACCESS_TOKEN: z.string().optional(),
  LINE_CHANNEL_SECRET: z.string().optional(),
  LINE_ENABLED: z.string().default("false"),
  IMAP_HOST: z.string().optional(),
  IMAP_PORT: z.string().default("993"),
  IMAP_USER: z.string().optional(),
  IMAP_PASSWORD: z.string().optional(),
  EMAIL_ENABLED: z.string().default("true"),
  BUSINESS_HOURS_START: z.string().default("07"),
  BUSINESS_HOURS_END: z.string().default("22"),
  TIMEZONE: z.string().default("Australia/Sydney"),
});

const env = envSchema.parse(process.env);

export const config = {
  openclaw: {
    gatewayUrl: env.OPENCLAW_GATEWAY_URL,
    webhookSecret: env.OPENCLAW_WEBHOOK_SECRET,
  },
  whatsapp: {
    enabled: env.WHATSAPP_ENABLED === "true",
  },
  line: {
    enabled: env.LINE_ENABLED === "true",
    channelAccessToken: env.LINE_CHANNEL_ACCESS_TOKEN,
    channelSecret: env.LINE_CHANNEL_SECRET,
  },
  email: {
    enabled: env.EMAIL_ENABLED === "true",
    host: env.IMAP_HOST,
    port: parseInt(env.IMAP_PORT),
    user: env.IMAP_USER,
    password: env.IMAP_PASSWORD,
  },
  businessHours: {
    start: parseInt(env.BUSINESS_HOURS_START),
    end: parseInt(env.BUSINESS_HOURS_END),
    timezone: env.TIMEZONE,
  },
} as const;
```

- [ ] **Step 8: Create src/utils/logger.ts**

```typescript
import pino from "pino";

export const logger = pino({
  transport: {
    target: "pino-pretty",
    options: { colorize: true },
  },
  level: process.env.LOG_LEVEL || "info",
});
```

- [ ] **Step 9: Create src/index.ts (stub)**

```typescript
import { logger } from "./utils/logger.js";
import { config } from "./config.js";

async function main() {
  logger.info("RE Co-Pilot starting...");
  logger.info({ channels: {
    whatsapp: config.whatsapp.enabled,
    line: config.line.enabled,
    email: config.email.enabled,
  }}, "Channel configuration");

  // TODO: Start adapter manager
  // TODO: Start follow-up scheduler
  // TODO: Start approval handler

  logger.info("RE Co-Pilot ready");
}

main().catch((err) => {
  logger.fatal(err, "Failed to start RE Co-Pilot");
  process.exit(1);
});
```

- [ ] **Step 10: Verify it compiles and runs**

```bash
npx tsx src/index.ts
```

Expected: "RE Co-Pilot starting..." and "RE Co-Pilot ready" in output.

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "feat: project scaffolding with types, config, and entry point"
```

---

## Task 2: SQLite Database Layer

**Files:**
- Create: `src/db.ts`
- Create: `tests/db.test.ts`

- [ ] **Step 1: Write failing test for database initialization**

```typescript
// tests/db.test.ts
import { describe, it, expect, afterEach } from "vitest";
import { Database } from "../../src/db.js";
import { unlinkSync, existsSync } from "fs";

const TEST_DB = "data/test.db";

afterEach(() => {
  if (existsSync(TEST_DB)) unlinkSync(TEST_DB);
});

describe("Database", () => {
  it("creates tables on init", () => {
    const db = new Database(TEST_DB);
    const tables = db.raw
      .prepare("SELECT name FROM sqlite_master WHERE type='table'")
      .all()
      .map((r: any) => r.name);
    expect(tables).toContain("leads");
    expect(tables).toContain("approval_queue");
    expect(tables).toContain("voice_examples");
    expect(tables).toContain("voice_rules");
    expect(tables).toContain("messages");
    db.close();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run tests/db.test.ts
```

Expected: FAIL — `Database` not found.

- [ ] **Step 3: Implement Database class**

```typescript
// src/db.ts
import BetterSqlite3 from "better-sqlite3";
import { mkdirSync } from "fs";
import { dirname } from "path";

export class Database {
  raw: BetterSqlite3.Database;

  constructor(dbPath: string = "data/re-copilot.db") {
    mkdirSync(dirname(dbPath), { recursive: true });
    this.raw = new BetterSqlite3(dbPath);
    this.raw.pragma("journal_mode = WAL");
    this.raw.pragma("foreign_keys = ON");
    this.migrate();
  }

  private migrate() {
    this.raw.exec(`
      CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        preferred_channel TEXT NOT NULL,
        language TEXT DEFAULT 'en',
        property_criteria TEXT DEFAULT '{}',
        stage TEXT DEFAULT 'exploring',
        temperature TEXT DEFAULT 'warm',
        follow_up_cadence_days INTEGER DEFAULT 5,
        next_follow_up TEXT,
        tone TEXT,
        notes TEXT,
        last_contact TEXT,
        last_contact_by TEXT DEFAULT 'buyer',
        conversation_summary TEXT,
        channel_identities TEXT DEFAULT '[]',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS approval_queue (
        id TEXT PRIMARY KEY,
        lead_id TEXT NOT NULL,
        draft_message TEXT NOT NULL,
        channel TEXT NOT NULL,
        recipient_id TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        edited_message TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        resolved_at TEXT,
        FOREIGN KEY (lead_id) REFERENCES leads(id)
      );

      CREATE TABLE IF NOT EXISTS voice_examples (
        id TEXT PRIMARY KEY,
        original_draft TEXT NOT NULL,
        edited_version TEXT NOT NULL,
        language TEXT DEFAULT 'en',
        created_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS voice_rules (
        id TEXT PRIMARY KEY,
        rule TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        channel TEXT NOT NULL,
        sender TEXT NOT NULL,
        sender_name TEXT,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        lang TEXT,
        direction TEXT NOT NULL,
        message_type TEXT DEFAULT 'text',
        thread_id TEXT,
        lead_id TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (lead_id) REFERENCES leads(id)
      );
    `);
  }

  close() {
    this.raw.close();
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
npx vitest run tests/db.test.ts
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/db.ts tests/db.test.ts
git commit -m "feat: SQLite database layer with schema for leads, approvals, voice, messages"
```

---

## Task 3: Lead Store

**Files:**
- Create: `src/leads/store.ts`
- Create: `tests/leads/store.test.ts`

- [ ] **Step 1: Write failing tests**

```typescript
// tests/leads/store.test.ts
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { LeadStore } from "../../src/leads/store.js";
import { Database } from "../../src/db.js";
import { unlinkSync, existsSync } from "fs";

const TEST_DB = "data/test-leads.db";
let db: Database;
let store: LeadStore;

beforeEach(() => {
  db = new Database(TEST_DB);
  store = new LeadStore(db);
});

afterEach(() => {
  db.close();
  if (existsSync(TEST_DB)) unlinkSync(TEST_DB);
});

describe("LeadStore", () => {
  it("creates a lead and retrieves it by id", () => {
    const lead = store.create({
      name: "Mrs Chen",
      preferredChannel: "whatsapp",
      language: "zh-TW",
      propertyCriteria: { type: "3BR", location: "Chatswood", budget: "< $2M" },
    });
    expect(lead.id).toBeDefined();
    expect(lead.name).toBe("Mrs Chen");

    const found = store.getById(lead.id);
    expect(found?.name).toBe("Mrs Chen");
    expect(found?.language).toBe("zh-TW");
  });

  it("lists leads due for follow-up", () => {
    const yesterday = new Date(Date.now() - 86400000).toISOString().split("T")[0];
    store.create({
      name: "Overdue Lead",
      preferredChannel: "line",
      language: "en",
      nextFollowUp: yesterday,
    });
    store.create({
      name: "Future Lead",
      preferredChannel: "whatsapp",
      language: "en",
      nextFollowUp: "2099-01-01",
    });

    const due = store.getDueForFollowUp();
    expect(due).toHaveLength(1);
    expect(due[0].name).toBe("Overdue Lead");
  });

  it("updates lead temperature and recalculates cadence", () => {
    const lead = store.create({ name: "Test", preferredChannel: "email", language: "en" });
    store.updateTemperature(lead.id, "hot");

    const updated = store.getById(lead.id);
    expect(updated?.temperature).toBe("hot");
    expect(updated?.followUpCadenceDays).toBeLessThanOrEqual(3);
  });

  it("finds lead by channel identity", () => {
    store.create({
      name: "Mrs Wang",
      preferredChannel: "whatsapp",
      language: "zh-TW",
      channelIdentities: [{ channel: "whatsapp", identifier: "+61412345678" }],
    });

    const found = store.findByChannelIdentity("whatsapp", "+61412345678");
    expect(found?.name).toBe("Mrs Wang");
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
npx vitest run tests/leads/store.test.ts
```

Expected: FAIL — `LeadStore` not found.

- [ ] **Step 3: Implement LeadStore**

```typescript
// src/leads/store.ts
import { randomUUID } from "crypto";
import { Database } from "../db.js";
import type { Lead } from "../types.js";

const CADENCE_MAP: Record<string, number> = {
  hot: 2,
  warm: 5,
  cold: 14,
};

export class LeadStore {
  constructor(private db: Database) {}

  create(input: Partial<Lead> & { name: string; preferredChannel: string; language: string }): Lead {
    const id = randomUUID();
    const now = new Date().toISOString();
    const cadence = CADENCE_MAP[input.temperature || "warm"] || 5;
    const nextFollowUp = input.nextFollowUp || this.addDays(now, cadence);

    this.db.raw.prepare(`
      INSERT INTO leads (id, name, preferred_channel, language, property_criteria, stage, temperature,
        follow_up_cadence_days, next_follow_up, tone, notes, last_contact, last_contact_by,
        conversation_summary, channel_identities, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      id, input.name, input.preferredChannel, input.language,
      JSON.stringify(input.propertyCriteria || {}),
      input.stage || "exploring", input.temperature || "warm",
      cadence, nextFollowUp,
      input.tone || null, input.notes || null,
      now, input.lastContactBy || "buyer",
      input.conversationSummary || null,
      JSON.stringify(input.channelIdentities || []),
      now, now
    );

    return this.getById(id)!;
  }

  getById(id: string): Lead | null {
    const row = this.db.raw.prepare("SELECT * FROM leads WHERE id = ?").get(id) as any;
    return row ? this.rowToLead(row) : null;
  }

  getAll(): Lead[] {
    const rows = this.db.raw.prepare("SELECT * FROM leads WHERE stage != 'closed'").all() as any[];
    return rows.map(this.rowToLead);
  }

  getDueForFollowUp(): Lead[] {
    const today = new Date().toISOString().split("T")[0];
    const rows = this.db.raw.prepare(
      "SELECT * FROM leads WHERE next_follow_up <= ? AND stage NOT IN ('closed', 'dormant')"
    ).all(today) as any[];
    return rows.map(this.rowToLead);
  }

  findByChannelIdentity(channel: string, identifier: string): Lead | null {
    const rows = this.db.raw.prepare("SELECT * FROM leads").all() as any[];
    for (const row of rows) {
      const identities = JSON.parse(row.channel_identities || "[]");
      if (identities.some((i: any) => i.channel === channel && i.identifier === identifier)) {
        return this.rowToLead(row);
      }
    }
    return null;
  }

  updateTemperature(id: string, temperature: "hot" | "warm" | "cold") {
    const cadence = CADENCE_MAP[temperature];
    const now = new Date().toISOString();
    const nextFollowUp = this.addDays(now, cadence);
    this.db.raw.prepare(
      "UPDATE leads SET temperature = ?, follow_up_cadence_days = ?, next_follow_up = ?, updated_at = ? WHERE id = ?"
    ).run(temperature, cadence, nextFollowUp, now, id);
  }

  updateLastContact(id: string, by: "agent" | "buyer" | "colleague") {
    const now = new Date().toISOString();
    const lead = this.getById(id);
    if (!lead) return;
    const nextFollowUp = this.addDays(now, lead.followUpCadenceDays);
    this.db.raw.prepare(
      "UPDATE leads SET last_contact = ?, last_contact_by = ?, next_follow_up = ?, updated_at = ? WHERE id = ?"
    ).run(now, by, nextFollowUp, now, id);
  }

  updateSummary(id: string, summary: string) {
    this.db.raw.prepare(
      "UPDATE leads SET conversation_summary = ?, updated_at = datetime('now') WHERE id = ?"
    ).run(summary, id);
  }

  private addDays(isoDate: string, days: number): string {
    const d = new Date(isoDate);
    d.setDate(d.getDate() + days);
    return d.toISOString().split("T")[0];
  }

  private rowToLead(row: any): Lead {
    return {
      id: row.id,
      name: row.name,
      preferredChannel: row.preferred_channel,
      language: row.language,
      propertyCriteria: JSON.parse(row.property_criteria || "{}"),
      stage: row.stage,
      temperature: row.temperature,
      followUpCadenceDays: row.follow_up_cadence_days,
      nextFollowUp: row.next_follow_up,
      tone: row.tone,
      notes: row.notes,
      lastContact: row.last_contact,
      lastContactBy: row.last_contact_by,
      conversationSummary: row.conversation_summary,
      channelIdentities: JSON.parse(row.channel_identities || "[]"),
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    };
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx vitest run tests/leads/store.test.ts
```

Expected: PASS (all 4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/leads/store.ts tests/leads/store.test.ts
git commit -m "feat: lead store with CRUD, follow-up scheduling, and channel identity lookup"
```

---

## Task 4: Approval Queue

**Files:**
- Create: `src/approval/queue.ts`
- Create: `tests/approval/queue.test.ts`

- [ ] **Step 1: Write failing tests**

```typescript
// tests/approval/queue.test.ts
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { ApprovalQueue } from "../../src/approval/queue.js";
import { Database } from "../../src/db.js";
import { unlinkSync, existsSync } from "fs";

const TEST_DB = "data/test-approval.db";
let db: Database;
let queue: ApprovalQueue;

beforeEach(() => {
  db = new Database(TEST_DB);
  queue = new ApprovalQueue(db);
  // Create a dummy lead for FK
  db.raw.prepare("INSERT INTO leads (id, name, preferred_channel, language) VALUES (?, ?, ?, ?)").run("lead-1", "Test", "whatsapp", "en");
});

afterEach(() => {
  db.close();
  if (existsSync(TEST_DB)) unlinkSync(TEST_DB);
});

describe("ApprovalQueue", () => {
  it("enqueues and retrieves pending items", () => {
    queue.enqueue({
      leadId: "lead-1",
      draftMessage: "Hi, just following up!",
      channel: "whatsapp",
      recipientId: "+61412345678",
      type: "follow_up",
    });

    const pending = queue.getPending();
    expect(pending).toHaveLength(1);
    expect(pending[0].draftMessage).toBe("Hi, just following up!");
    expect(pending[0].status).toBe("pending");
  });

  it("approves an item", () => {
    const item = queue.enqueue({
      leadId: "lead-1",
      draftMessage: "Draft message",
      channel: "whatsapp",
      recipientId: "+61412345678",
      type: "follow_up",
    });

    queue.approve(item.id);
    const resolved = queue.getById(item.id);
    expect(resolved?.status).toBe("approved");
    expect(resolved?.resolvedAt).toBeDefined();
  });

  it("edits and approves an item", () => {
    const item = queue.enqueue({
      leadId: "lead-1",
      draftMessage: "Original draft",
      channel: "whatsapp",
      recipientId: "+61412345678",
      type: "response",
    });

    queue.editAndApprove(item.id, "Edited version");
    const resolved = queue.getById(item.id);
    expect(resolved?.status).toBe("edited");
    expect(resolved?.editedMessage).toBe("Edited version");
  });

  it("rejects an item", () => {
    const item = queue.enqueue({
      leadId: "lead-1",
      draftMessage: "Bad draft",
      channel: "line",
      recipientId: "U123",
      type: "after_hours_reply",
    });

    queue.reject(item.id);
    const resolved = queue.getById(item.id);
    expect(resolved?.status).toBe("rejected");
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
npx vitest run tests/approval/queue.test.ts
```

- [ ] **Step 3: Implement ApprovalQueue**

```typescript
// src/approval/queue.ts
import { randomUUID } from "crypto";
import { Database } from "../db.js";
import type { ApprovalItem } from "../types.js";

interface EnqueueInput {
  leadId: string;
  draftMessage: string;
  channel: "whatsapp" | "line" | "email";
  recipientId: string;
  type: "follow_up" | "after_hours_reply" | "response";
}

export class ApprovalQueue {
  constructor(private db: Database) {}

  enqueue(input: EnqueueInput): ApprovalItem {
    const id = randomUUID();
    this.db.raw.prepare(`
      INSERT INTO approval_queue (id, lead_id, draft_message, channel, recipient_id, type)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(id, input.leadId, input.draftMessage, input.channel, input.recipientId, input.type);
    return this.getById(id)!;
  }

  getPending(): ApprovalItem[] {
    const rows = this.db.raw.prepare(
      "SELECT * FROM approval_queue WHERE status = 'pending' ORDER BY created_at ASC"
    ).all() as any[];
    return rows.map(this.rowToItem);
  }

  getById(id: string): ApprovalItem | null {
    const row = this.db.raw.prepare("SELECT * FROM approval_queue WHERE id = ?").get(id) as any;
    return row ? this.rowToItem(row) : null;
  }

  approve(id: string) {
    this.db.raw.prepare(
      "UPDATE approval_queue SET status = 'approved', resolved_at = datetime('now') WHERE id = ?"
    ).run(id);
  }

  editAndApprove(id: string, editedMessage: string) {
    this.db.raw.prepare(
      "UPDATE approval_queue SET status = 'edited', edited_message = ?, resolved_at = datetime('now') WHERE id = ?"
    ).run(editedMessage, id);
  }

  reject(id: string) {
    this.db.raw.prepare(
      "UPDATE approval_queue SET status = 'rejected', resolved_at = datetime('now') WHERE id = ?"
    ).run(id);
  }

  private rowToItem(row: any): ApprovalItem {
    return {
      id: row.id,
      leadId: row.lead_id,
      draftMessage: row.draft_message,
      channel: row.channel,
      recipientId: row.recipient_id,
      type: row.type,
      status: row.status,
      editedMessage: row.edited_message,
      createdAt: row.created_at,
      resolvedAt: row.resolved_at,
    };
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx vitest run tests/approval/queue.test.ts
```

Expected: PASS (all 4 tests)

- [ ] **Step 5: Commit**

```bash
git add src/approval/queue.ts tests/approval/queue.test.ts
git commit -m "feat: approval queue with enqueue, approve, edit, reject"
```

---

## Task 5: Voice Store

**Files:**
- Create: `src/voice/store.ts`
- Create: `src/voice/voice-prompt.ts`
- Create: `tests/voice/store.test.ts`

- [ ] **Step 1: Write failing tests**

```typescript
// tests/voice/store.test.ts
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { VoiceStore } from "../../src/voice/store.js";
import { buildVoicePrompt } from "../../src/voice/voice-prompt.js";
import { Database } from "../../src/db.js";
import { unlinkSync, existsSync } from "fs";

const TEST_DB = "data/test-voice.db";
let db: Database;
let store: VoiceStore;

beforeEach(() => {
  db = new Database(TEST_DB);
  store = new VoiceStore(db);
});

afterEach(() => {
  db.close();
  if (existsSync(TEST_DB)) unlinkSync(TEST_DB);
});

describe("VoiceStore", () => {
  it("stores a voice example pair", () => {
    store.addExample("Hello, how are you?", "嗨，最近好嗎？", "zh-TW");
    const examples = store.getExamples("zh-TW");
    expect(examples).toHaveLength(1);
    expect(examples[0].originalDraft).toBe("Hello, how are you?");
    expect(examples[0].editedVersion).toBe("嗨，最近好嗎？");
  });

  it("stores and retrieves voice rules", () => {
    store.addRule("Never use 您好, always use 嗨");
    const rules = store.getRules();
    expect(rules).toHaveLength(1);
    expect(rules[0].rule).toContain("您好");
  });

  it("limits examples to most recent 20", () => {
    for (let i = 0; i < 25; i++) {
      store.addExample(`draft ${i}`, `edited ${i}`, "en");
    }
    const examples = store.getExamples("en", 20);
    expect(examples).toHaveLength(20);
  });
});

describe("buildVoicePrompt", () => {
  it("builds a prompt from examples and rules", () => {
    store.addExample("Hi there", "嗨你好", "zh-TW");
    store.addRule("Always be casual, never formal");

    const prompt = buildVoicePrompt(store, "zh-TW");
    expect(prompt).toContain("嗨你好");
    expect(prompt).toContain("Always be casual");
  });

  it("returns empty string when no data", () => {
    const prompt = buildVoicePrompt(store, "en");
    expect(prompt).toBe("");
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
npx vitest run tests/voice/store.test.ts
```

- [ ] **Step 3: Implement VoiceStore**

```typescript
// src/voice/store.ts
import { randomUUID } from "crypto";
import { Database } from "../db.js";
import type { VoiceExample, VoiceRule } from "../types.js";

export class VoiceStore {
  constructor(private db: Database) {}

  addExample(originalDraft: string, editedVersion: string, language: string) {
    this.db.raw.prepare(
      "INSERT INTO voice_examples (id, original_draft, edited_version, language) VALUES (?, ?, ?, ?)"
    ).run(randomUUID(), originalDraft, editedVersion, language);
  }

  getExamples(language: string, limit: number = 20): VoiceExample[] {
    const rows = this.db.raw.prepare(
      "SELECT * FROM voice_examples WHERE language = ? ORDER BY created_at DESC LIMIT ?"
    ).all(language, limit) as any[];
    return rows.map((r) => ({
      id: r.id,
      originalDraft: r.original_draft,
      editedVersion: r.edited_version,
      language: r.language,
      createdAt: r.created_at,
    }));
  }

  addRule(rule: string) {
    this.db.raw.prepare(
      "INSERT INTO voice_rules (id, rule) VALUES (?, ?)"
    ).run(randomUUID(), rule);
  }

  getRules(): VoiceRule[] {
    const rows = this.db.raw.prepare(
      "SELECT * FROM voice_rules ORDER BY created_at DESC"
    ).all() as any[];
    return rows.map((r) => ({
      id: r.id,
      rule: r.rule,
      createdAt: r.created_at,
    }));
  }
}
```

- [ ] **Step 4: Implement buildVoicePrompt**

```typescript
// src/voice/voice-prompt.ts
import { VoiceStore } from "./store.js";

export function buildVoicePrompt(store: VoiceStore, language: string): string {
  const examples = store.getExamples(language, 20);
  const rules = store.getRules();

  if (examples.length === 0 && rules.length === 0) return "";

  const parts: string[] = [];

  if (rules.length > 0) {
    parts.push("## Hard Rules (always follow these)");
    for (const rule of rules) {
      parts.push(`- ${rule.rule}`);
    }
  }

  if (examples.length > 0) {
    parts.push("\n## Voice Examples (match this writing style)");
    for (const ex of examples) {
      parts.push(`Original: "${ex.originalDraft}"\nEdited to: "${ex.editedVersion}"\n`);
    }
  }

  return parts.join("\n");
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
npx vitest run tests/voice/store.test.ts
```

Expected: PASS (all 5 tests)

- [ ] **Step 6: Commit**

```bash
git add src/voice/store.ts src/voice/voice-prompt.ts tests/voice/store.test.ts
git commit -m "feat: voice store and prompt builder for learning agent's writing style"
```

---

## Task 6: OpenClaw Bridge

**Files:**
- Create: `src/brain/openclaw-bridge.ts`
- Create: `src/brain/prompts.ts`
- Create: `tests/brain/openclaw-bridge.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// tests/brain/openclaw-bridge.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { OpenClawBridge } from "../../src/brain/openclaw-bridge.js";

const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

describe("OpenClawBridge", () => {
  let bridge: OpenClawBridge;

  beforeEach(() => {
    bridge = new OpenClawBridge("http://localhost:18789");
    mockFetch.mockReset();
  });

  it("sends a message to OpenClaw webhook", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ response: "I'll track Mrs Chen as a warm lead." }),
    });

    const response = await bridge.send("New buyer message from Mrs Chen on WhatsApp: looking for 3BR in Chatswood");
    expect(response).toContain("Mrs Chen");
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:18789/hooks/agent",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
      })
    );
  });

  it("handles gateway errors gracefully", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Connection refused"));

    const response = await bridge.send("test");
    expect(response).toBeNull();
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
npx vitest run tests/brain/openclaw-bridge.test.ts
```

- [ ] **Step 3: Implement OpenClawBridge**

```typescript
// src/brain/openclaw-bridge.ts
import { logger } from "../utils/logger.js";

export class OpenClawBridge {
  constructor(
    private gatewayUrl: string,
    private webhookSecret?: string
  ) {}

  async send(message: string, deliver: boolean = false): Promise<string | null> {
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (this.webhookSecret) {
        headers["Authorization"] = `Bearer ${this.webhookSecret}`;
      }

      const res = await fetch(`${this.gatewayUrl}/hooks/agent`, {
        method: "POST",
        headers,
        body: JSON.stringify({ text: message, deliver }),
      });

      if (!res.ok) {
        logger.error({ status: res.status }, "OpenClaw webhook returned error");
        return null;
      }

      const data = await res.json();
      return data.response || data.text || JSON.stringify(data);
    } catch (err) {
      logger.error({ err }, "Failed to reach OpenClaw gateway");
      return null;
    }
  }

  async sendWithContext(context: string, message: string): Promise<string | null> {
    const fullMessage = `${context}\n\n---\n\n${message}`;
    return this.send(fullMessage);
  }
}
```

- [ ] **Step 4: Implement prompts**

```typescript
// src/brain/prompts.ts
import type { Lead, NormalizedMessage } from "../types.js";

export function buildInboundMessagePrompt(msg: NormalizedMessage, existingLead: Lead | null): string {
  const leadContext = existingLead
    ? `Known lead: ${existingLead.name} (${existingLead.temperature}, ${existingLead.stage}). Last contact: ${existingLead.lastContact}. Summary: ${existingLead.conversationSummary || "none"}`
    : "This appears to be a NEW lead — no existing record.";

  return `[CHANNEL MONITOR] New ${msg.direction} message on ${msg.channel}:
From: ${msg.senderName || msg.sender}
Content: "${msg.content}"
Timestamp: ${msg.timestamp.toISOString()}
Language detected: ${msg.lang || "unknown"}

${leadContext}

Tasks:
1. If this is a new lead, extract: name, language preference, property criteria, and suggested temperature.
2. Update the conversation summary with this new message.
3. If this is an inbound message that warrants a response, draft a reply in the buyer's language.
4. If this is an outbound message from the agent, just update the lead record — no response needed.

Respond in JSON format:
{
  "isNewLead": boolean,
  "leadUpdate": { name, language, propertyCriteria, temperature, conversationSummary, notes },
  "shouldDraftReply": boolean,
  "draftReply": "string or null",
  "reasoning": "brief explanation"
}`;
}

export function buildFollowUpPrompt(lead: Lead, voiceContext: string): string {
  return `Draft a follow-up message for this lead:

Name: ${lead.name}
Language: ${lead.language}
Temperature: ${lead.temperature} (${lead.stage})
Property criteria: ${JSON.stringify(lead.propertyCriteria)}
Last contact: ${lead.lastContact} by ${lead.lastContactBy}
Conversation summary: ${lead.conversationSummary || "none"}
Notes: ${lead.notes || "none"}

${voiceContext ? `\n## Agent Voice Guide\n${voiceContext}` : ""}

Guidelines:
- Write in ${lead.language === "zh-TW" ? "Traditional Chinese" : lead.language === "en" ? "English" : lead.language}
- Match the temperature: hot = specific/urgent, warm = helpful check-in, cold = light touch
- Keep it natural and conversational, not robotic
- Do NOT include a subject line — this is a chat message

Respond with just the message text, nothing else.`;
}

export function buildAfterHoursPrompt(msg: NormalizedMessage, lead: Lead | null): string {
  const lang = msg.lang || lead?.language || "en";
  return `Draft an after-hours auto-acknowledgement for this message:

From: ${msg.senderName || msg.sender}
Content: "${msg.content}"
Language: ${lang}
${lead ? `Known lead: ${lead.name}` : "New contact"}

The message should:
1. Acknowledge their message warmly in ${lang === "zh-TW" ? "Traditional Chinese" : "English"}
2. Let them know the agent will respond during business hours
3. Ask ONE qualifying question to move the lead forward (e.g., timeline, budget, property type)

Keep it short — 2-3 sentences max. Respond with just the message text.`;
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
npx vitest run tests/brain/openclaw-bridge.test.ts
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/brain/openclaw-bridge.ts src/brain/prompts.ts tests/brain/openclaw-bridge.test.ts
git commit -m "feat: OpenClaw bridge for webhook communication and prompt templates"
```

---

## Task 7: Channel Adapter Base + Email Adapter

**Files:**
- Create: `src/adapters/base.ts`
- Create: `src/adapters/email.ts`
- Create: `tests/adapters/email.test.ts`

Email is the simplest adapter (no API approval needed) so we build it first.

- [ ] **Step 1: Create base adapter interface**

```typescript
// src/adapters/base.ts
import type { NormalizedMessage } from "../types.js";

export type MessageHandler = (msg: NormalizedMessage) => Promise<void>;

export interface ChannelAdapter {
  name: string;
  start(onMessage: MessageHandler): Promise<void>;
  stop(): Promise<void>;
  sendMessage(recipientId: string, content: string): Promise<boolean>;
}
```

- [ ] **Step 2: Write failing test for email adapter**

```typescript
// tests/adapters/email.test.ts
import { describe, it, expect } from "vitest";
import { EmailAdapter } from "../../src/adapters/email.js";

describe("EmailAdapter", () => {
  it("has correct name", () => {
    const adapter = new EmailAdapter({
      host: "imap.test.com",
      port: 993,
      user: "test@test.com",
      password: "pass",
    });
    expect(adapter.name).toBe("email");
  });

  it("normalizes an email into NormalizedMessage format", () => {
    const adapter = new EmailAdapter({
      host: "imap.test.com",
      port: 993,
      user: "test@test.com",
      password: "pass",
    });

    const normalized = adapter.normalizeEmail({
      from: "buyer@example.com",
      fromName: "Mrs Chen",
      subject: "Property inquiry",
      text: "Hi, I'm interested in 3BR properties in Chatswood",
      date: new Date("2026-03-19T10:00:00Z"),
      messageId: "msg-123",
    });

    expect(normalized.channel).toBe("email");
    expect(normalized.sender).toBe("buyer@example.com");
    expect(normalized.senderName).toBe("Mrs Chen");
    expect(normalized.content).toContain("Chatswood");
    expect(normalized.direction).toBe("inbound");
    expect(normalized.messageType).toBe("text");
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

```bash
npx vitest run tests/adapters/email.test.ts
```

- [ ] **Step 4: Implement EmailAdapter**

```typescript
// src/adapters/email.ts
import { ImapFlow } from "imapflow";
import { randomUUID } from "crypto";
import { logger } from "../utils/logger.js";
import type { ChannelAdapter, MessageHandler } from "./base.js";
import type { NormalizedMessage } from "../types.js";

interface EmailConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  pollIntervalMs?: number;
}

interface RawEmail {
  from: string;
  fromName?: string;
  subject: string;
  text: string;
  date: Date;
  messageId: string;
}

export class EmailAdapter implements ChannelAdapter {
  name = "email" as const;
  private client: ImapFlow | null = null;
  private pollInterval: ReturnType<typeof setInterval> | null = null;
  private config: EmailConfig;
  private lastSeenUid: number = 0;

  constructor(config: EmailConfig) {
    this.config = config;
  }

  async start(onMessage: MessageHandler): Promise<void> {
    this.client = new ImapFlow({
      host: this.config.host,
      port: this.config.port,
      secure: true,
      auth: { user: this.config.user, pass: this.config.password },
      logger: false,
    });

    await this.client.connect();
    logger.info("Email adapter connected to IMAP");

    const lock = await this.client.getMailboxLock("INBOX");
    try {
      const status = await this.client.status("INBOX", { uidNext: true });
      this.lastSeenUid = (status.uidNext || 1) - 1;
    } finally {
      lock.release();
    }

    const interval = this.config.pollIntervalMs || 30000;
    this.pollInterval = setInterval(() => this.poll(onMessage), interval);
    logger.info({ intervalMs: interval }, "Email polling started");
  }

  private async poll(onMessage: MessageHandler) {
    if (!this.client) return;
    try {
      const lock = await this.client.getMailboxLock("INBOX");
      try {
        const range = `${this.lastSeenUid + 1}:*`;
        for await (const msg of this.client.fetch(range, {
          uid: true,
          envelope: true,
          source: true,
        })) {
          if (msg.uid <= this.lastSeenUid) continue;
          this.lastSeenUid = msg.uid;

          const from = msg.envelope.from?.[0];
          const normalized = this.normalizeEmail({
            from: from?.address || "unknown",
            fromName: from?.name,
            subject: msg.envelope.subject || "",
            text: msg.source?.toString() || "",
            date: msg.envelope.date || new Date(),
            messageId: msg.envelope.messageId || randomUUID(),
          });

          await onMessage(normalized);
        }
      } finally {
        lock.release();
      }
    } catch (err) {
      logger.error({ err }, "Email poll error");
    }
  }

  normalizeEmail(raw: RawEmail): NormalizedMessage {
    return {
      id: raw.messageId || randomUUID(),
      channel: "email",
      sender: raw.from,
      senderName: raw.fromName,
      content: raw.subject ? `[Subject: ${raw.subject}] ${raw.text}` : raw.text,
      timestamp: raw.date,
      direction: "inbound",
      messageType: "text",
      threadId: raw.messageId,
    };
  }

  async sendMessage(_recipientId: string, _content: string): Promise<boolean> {
    logger.warn("Email sending not implemented — agent should copy message manually");
    return false;
  }

  async stop(): Promise<void> {
    if (this.pollInterval) clearInterval(this.pollInterval);
    if (this.client) await this.client.logout();
    logger.info("Email adapter stopped");
  }
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
npx vitest run tests/adapters/email.test.ts
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/adapters/base.ts src/adapters/email.ts tests/adapters/email.test.ts
git commit -m "feat: base channel adapter interface and email IMAP adapter"
```

---

## Task 8: WhatsApp Adapter (Baileys)

**Files:**
- Create: `src/adapters/whatsapp.ts`
- Create: `tests/adapters/whatsapp.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// tests/adapters/whatsapp.test.ts
import { describe, it, expect } from "vitest";
import { WhatsAppAdapter } from "../../src/adapters/whatsapp.js";

describe("WhatsAppAdapter", () => {
  it("has correct name", () => {
    const adapter = new WhatsAppAdapter();
    expect(adapter.name).toBe("whatsapp");
  });

  it("normalizes a WhatsApp message", () => {
    const adapter = new WhatsAppAdapter();
    const normalized = adapter.normalizeMessage({
      key: { remoteJid: "61412345678@s.whatsapp.net", fromMe: false, id: "msg-1" },
      message: { conversation: "Hi, interested in Chatswood properties" },
      messageTimestamp: Math.floor(Date.now() / 1000),
      pushName: "Mrs Chen",
    });

    expect(normalized.channel).toBe("whatsapp");
    expect(normalized.sender).toBe("61412345678");
    expect(normalized.senderName).toBe("Mrs Chen");
    expect(normalized.content).toContain("Chatswood");
    expect(normalized.direction).toBe("inbound");
  });

  it("detects outbound messages", () => {
    const adapter = new WhatsAppAdapter();
    const normalized = adapter.normalizeMessage({
      key: { remoteJid: "61412345678@s.whatsapp.net", fromMe: true, id: "msg-2" },
      message: { conversation: "I'll send you the listings" },
      messageTimestamp: Math.floor(Date.now() / 1000),
    });

    expect(normalized.direction).toBe("outbound");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run tests/adapters/whatsapp.test.ts
```

- [ ] **Step 3: Implement WhatsAppAdapter**

```typescript
// src/adapters/whatsapp.ts
import makeWASocket, {
  DisconnectReason,
  useMultiFileAuthState,
} from "@whiskeysockets/baileys";
import { Boom } from "@hapi/boom";
import { randomUUID } from "crypto";
import { logger } from "../utils/logger.js";
import type { ChannelAdapter, MessageHandler } from "./base.js";
import type { NormalizedMessage } from "../types.js";

export class WhatsAppAdapter implements ChannelAdapter {
  name = "whatsapp" as const;
  private sock: ReturnType<typeof makeWASocket> | null = null;
  private authDir: string;

  constructor(authDir: string = "auth_info_baileys") {
    this.authDir = authDir;
  }

  async start(onMessage: MessageHandler): Promise<void> {
    const { state, saveCreds } = await useMultiFileAuthState(this.authDir);

    this.sock = makeWASocket({
      auth: state,
      printQRInTerminal: true,
    });

    this.sock.ev.on("creds.update", saveCreds);

    this.sock.ev.on("connection.update", (update) => {
      const { connection, lastDisconnect } = update;
      if (connection === "close") {
        const reason = (lastDisconnect?.error as Boom)?.output?.statusCode;
        if (reason !== DisconnectReason.loggedOut) {
          logger.warn("WhatsApp disconnected, reconnecting...");
          this.start(onMessage);
        } else {
          logger.error("WhatsApp logged out — re-scan QR code");
        }
      } else if (connection === "open") {
        logger.info("WhatsApp adapter connected");
      }
    });

    this.sock.ev.on("messages.upsert", async ({ messages }) => {
      for (const msg of messages) {
        if (msg.key.remoteJid === "status@broadcast") continue;
        if (!msg.message) continue;

        const normalized = this.normalizeMessage(msg);
        await onMessage(normalized);
      }
    });
  }

  normalizeMessage(msg: any): NormalizedMessage {
    const jid = msg.key.remoteJid || "";
    const sender = jid.replace("@s.whatsapp.net", "").replace("@g.us", "");
    const content =
      msg.message?.conversation ||
      msg.message?.extendedTextMessage?.text ||
      msg.message?.imageMessage?.caption ||
      "[non-text message]";

    return {
      id: msg.key.id || randomUUID(),
      channel: "whatsapp",
      sender,
      senderName: msg.pushName,
      content,
      timestamp: new Date((msg.messageTimestamp as number) * 1000),
      direction: msg.key.fromMe ? "outbound" : "inbound",
      messageType: this.detectMessageType(msg.message),
      threadId: jid,
    };
  }

  private detectMessageType(message: any): NormalizedMessage["messageType"] {
    if (!message) return "text";
    if (message.imageMessage) return "image";
    if (message.audioMessage) return "voice";
    if (message.documentMessage) return "document";
    return "text";
  }

  async sendMessage(recipientId: string, content: string): Promise<boolean> {
    if (!this.sock) return false;
    try {
      const jid = recipientId.includes("@") ? recipientId : `${recipientId}@s.whatsapp.net`;
      await this.sock.sendMessage(jid, { text: content });
      return true;
    } catch (err) {
      logger.error({ err, recipientId }, "Failed to send WhatsApp message");
      return false;
    }
  }

  async stop(): Promise<void> {
    this.sock?.end(undefined);
    logger.info("WhatsApp adapter stopped");
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx vitest run tests/adapters/whatsapp.test.ts
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/adapters/whatsapp.ts tests/adapters/whatsapp.test.ts
git commit -m "feat: WhatsApp adapter using Baileys for conversation monitoring"
```

---

## Task 9: Line Adapter

**Files:**
- Create: `src/adapters/line.ts`
- Create: `tests/adapters/line.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// tests/adapters/line.test.ts
import { describe, it, expect } from "vitest";
import { LineAdapter } from "../../src/adapters/line.js";

describe("LineAdapter", () => {
  it("has correct name", () => {
    const adapter = new LineAdapter({
      channelAccessToken: "test-token",
      channelSecret: "test-secret",
      port: 0,
    });
    expect(adapter.name).toBe("line");
  });

  it("normalizes a Line text message event", () => {
    const adapter = new LineAdapter({
      channelAccessToken: "test-token",
      channelSecret: "test-secret",
      port: 0,
    });

    const normalized = adapter.normalizeEvent({
      type: "message",
      message: { type: "text", id: "msg-1", text: "Looking for property in Sydney" },
      source: { type: "user", userId: "U123456" },
      timestamp: Date.now(),
      replyToken: "reply-token",
    });

    expect(normalized.channel).toBe("line");
    expect(normalized.sender).toBe("U123456");
    expect(normalized.content).toContain("Sydney");
    expect(normalized.direction).toBe("inbound");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run tests/adapters/line.test.ts
```

- [ ] **Step 3: Implement LineAdapter**

```typescript
// src/adapters/line.ts
import { Client, middleware, WebhookEvent } from "@line/bot-sdk";
import { createServer } from "http";
import { randomUUID } from "crypto";
import { logger } from "../utils/logger.js";
import type { ChannelAdapter, MessageHandler } from "./base.js";
import type { NormalizedMessage } from "../types.js";

interface LineConfig {
  channelAccessToken: string;
  channelSecret: string;
  port: number;
}

export class LineAdapter implements ChannelAdapter {
  name = "line" as const;
  private client: Client;
  private config: LineConfig;
  private server: ReturnType<typeof createServer> | null = null;

  constructor(config: LineConfig) {
    this.config = config;
    this.client = new Client({
      channelAccessToken: config.channelAccessToken,
    });
  }

  async start(onMessage: MessageHandler): Promise<void> {
    const mw = middleware({ channelSecret: this.config.channelSecret });

    this.server = createServer((req, res) => {
      if (req.url === "/webhook" && req.method === "POST") {
        mw(req, res, async () => {
          const body = (req as any).body as { events: WebhookEvent[] };
          for (const event of body.events) {
            if (event.type === "message" && event.message.type === "text") {
              const normalized = this.normalizeEvent(event as any);
              await onMessage(normalized);
            }
          }
          res.writeHead(200);
          res.end("OK");
        });
      } else {
        res.writeHead(404);
        res.end();
      }
    });

    this.server.listen(this.config.port, () => {
      logger.info({ port: this.config.port }, "Line webhook server started");
    });
  }

  normalizeEvent(event: any): NormalizedMessage {
    return {
      id: event.message?.id || randomUUID(),
      channel: "line",
      sender: event.source?.userId || "unknown",
      content: event.message?.text || "[non-text message]",
      timestamp: new Date(event.timestamp),
      direction: "inbound",
      messageType: event.message?.type === "image" ? "image" :
                   event.message?.type === "audio" ? "voice" : "text",
      threadId: event.source?.userId,
    };
  }

  async sendMessage(recipientId: string, content: string): Promise<boolean> {
    try {
      await this.client.pushMessage(recipientId, { type: "text", text: content });
      return true;
    } catch (err) {
      logger.error({ err, recipientId }, "Failed to send Line message");
      return false;
    }
  }

  async stop(): Promise<void> {
    return new Promise((resolve) => {
      if (this.server) {
        this.server.close(() => {
          logger.info("Line adapter stopped");
          resolve();
        });
      } else {
        resolve();
      }
    });
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx vitest run tests/adapters/line.test.ts
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/line.ts tests/adapters/line.test.ts
git commit -m "feat: Line adapter using Messaging API webhook"
```

---

## Task 10: Adapter Manager

**Files:**
- Create: `src/adapters/adapter-manager.ts`

- [ ] **Step 1: Implement AdapterManager**

```typescript
// src/adapters/adapter-manager.ts
import { config } from "../config.js";
import { logger } from "../utils/logger.js";
import type { ChannelAdapter, MessageHandler } from "./base.js";
import { WhatsAppAdapter } from "./whatsapp.js";
import { LineAdapter } from "./line.js";
import { EmailAdapter } from "./email.js";

export class AdapterManager {
  private adapters: ChannelAdapter[] = [];

  constructor() {
    if (config.whatsapp.enabled) {
      this.adapters.push(new WhatsAppAdapter());
    }
    if (config.line.enabled && config.line.channelAccessToken && config.line.channelSecret) {
      this.adapters.push(new LineAdapter({
        channelAccessToken: config.line.channelAccessToken,
        channelSecret: config.line.channelSecret,
        port: 3100,
      }));
    }
    if (config.email.enabled && config.email.host && config.email.user && config.email.password) {
      this.adapters.push(new EmailAdapter({
        host: config.email.host,
        port: config.email.port,
        user: config.email.user,
        password: config.email.password,
      }));
    }
  }

  async startAll(onMessage: MessageHandler): Promise<void> {
    for (const adapter of this.adapters) {
      try {
        await adapter.start(onMessage);
        logger.info({ adapter: adapter.name }, "Channel adapter started");
      } catch (err) {
        logger.error({ err, adapter: adapter.name }, "Failed to start channel adapter");
      }
    }
  }

  getAdapter(channel: string): ChannelAdapter | undefined {
    return this.adapters.find((a) => a.name === channel);
  }

  async stopAll(): Promise<void> {
    for (const adapter of this.adapters) {
      await adapter.stop();
    }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/adapters/adapter-manager.ts
git commit -m "feat: adapter manager to start/stop all channel adapters"
```

---

## Task 11: Follow-Up Scheduler

**Files:**
- Create: `src/leads/follow-up-scheduler.ts`
- Create: `tests/leads/follow-up-scheduler.test.ts`

- [ ] **Step 1: Write failing test**

```typescript
// tests/leads/follow-up-scheduler.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { FollowUpScheduler } from "../../src/leads/follow-up-scheduler.js";
import { LeadStore } from "../../src/leads/store.js";
import { ApprovalQueue } from "../../src/approval/queue.js";
import { VoiceStore } from "../../src/voice/store.js";
import { Database } from "../../src/db.js";
import { unlinkSync, existsSync } from "fs";

const TEST_DB = "data/test-followup.db";
let db: Database;

beforeEach(() => {
  db = new Database(TEST_DB);
});

afterEach(() => {
  db.close();
  if (existsSync(TEST_DB)) unlinkSync(TEST_DB);
});

describe("FollowUpScheduler", () => {
  it("generates follow-up drafts for overdue leads", async () => {
    const leadStore = new LeadStore(db);
    const approvalQueue = new ApprovalQueue(db);
    const voiceStore = new VoiceStore(db);

    const yesterday = new Date(Date.now() - 86400000).toISOString().split("T")[0];
    leadStore.create({
      name: "Mrs Chen",
      preferredChannel: "whatsapp",
      language: "zh-TW",
      nextFollowUp: yesterday,
      channelIdentities: [{ channel: "whatsapp", identifier: "+61412345678" }],
    });

    const mockDraft = vi.fn().mockResolvedValue("嗨 Mrs Chen，最近好嗎？");
    const scheduler = new FollowUpScheduler(leadStore, approvalQueue, voiceStore, mockDraft);

    await scheduler.checkAndQueue();

    const pending = approvalQueue.getPending();
    expect(pending).toHaveLength(1);
    expect(pending[0].type).toBe("follow_up");
    expect(pending[0].draftMessage).toContain("Mrs Chen");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run tests/leads/follow-up-scheduler.test.ts
```

- [ ] **Step 3: Implement FollowUpScheduler**

```typescript
// src/leads/follow-up-scheduler.ts
import * as cron from "node-cron";
import { logger } from "../utils/logger.js";
import { LeadStore } from "./store.js";
import { ApprovalQueue } from "../approval/queue.js";
import { VoiceStore } from "../voice/store.js";
import { buildFollowUpPrompt } from "../brain/prompts.js";
import { buildVoicePrompt } from "../voice/voice-prompt.js";

type DraftFn = (prompt: string) => Promise<string | null>;

export class FollowUpScheduler {
  private cronJob: cron.ScheduledTask | null = null;

  constructor(
    private leadStore: LeadStore,
    private approvalQueue: ApprovalQueue,
    private voiceStore: VoiceStore,
    private draftFn: DraftFn
  ) {}

  start(cronExpression: string = "0 8 * * *") {
    this.cronJob = cron.schedule(cronExpression, () => this.checkAndQueue());
    logger.info({ cron: cronExpression }, "Follow-up scheduler started");
  }

  async checkAndQueue(): Promise<number> {
    const dueLeads = this.leadStore.getDueForFollowUp();
    logger.info({ count: dueLeads.length }, "Leads due for follow-up");

    let queued = 0;
    for (const lead of dueLeads) {
      try {
        const voiceContext = buildVoicePrompt(this.voiceStore, lead.language);
        const prompt = buildFollowUpPrompt(lead, voiceContext);
        const draft = await this.draftFn(prompt);

        if (!draft) {
          logger.warn({ leadId: lead.id }, "Failed to draft follow-up");
          continue;
        }

        const primaryIdentity = lead.channelIdentities[0];
        this.approvalQueue.enqueue({
          leadId: lead.id,
          draftMessage: draft,
          channel: lead.preferredChannel as any,
          recipientId: primaryIdentity?.identifier || lead.name,
          type: "follow_up",
        });

        queued++;
      } catch (err) {
        logger.error({ err, leadId: lead.id }, "Error drafting follow-up");
      }
    }

    logger.info({ queued }, "Follow-up drafts queued for approval");
    return queued;
  }

  stop() {
    this.cronJob?.stop();
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx vitest run tests/leads/follow-up-scheduler.test.ts
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/leads/follow-up-scheduler.ts tests/leads/follow-up-scheduler.test.ts
git commit -m "feat: follow-up scheduler with cron-based lead scanning and draft queuing"
```

---

## Task 12: OpenClaw Skill Definition

**Files:**
- Create: `skills/re-copilot/SKILL.md`

- [ ] **Step 1: Create the skill**

```markdown
---
name: re-copilot
description: Real estate co-pilot for agents serving overseas Chinese/Taiwanese buyers. Tracks leads, drafts follow-ups, and learns the agent's voice.
---

You are a real estate co-pilot AI assistant for a real estate agent who specializes in serving overseas Chinese and Taiwanese property buyers in Australia.

## Your Role
- Track buyer leads and their property preferences
- Draft follow-up messages in the buyer's preferred language
- Detect when leads need attention and proactively suggest follow-ups
- Learn and mimic the agent's writing style over time
- Handle after-hours inquiries with smart acknowledgements

## Lead Management
When the agent tells you about a lead (e.g., "just talked to Mrs Chen, wants 3BR Chatswood under $2M"):
1. Extract: name, language, property criteria, temperature
2. Store in your memory
3. Set a follow-up reminder based on temperature:
   - Hot (actively buying): 2-3 days
   - Warm (interested): 5-7 days
   - Cold (exploring): 2-3 weeks
4. Confirm what you understood

When the channel monitor sends you a message from a buyer:
1. Check if this is a known lead
2. Update their profile with new information
3. If a response is needed, draft one in the buyer's language
4. Always include the lead's name and context in your response

## Language Rules
- Detect the buyer's language from their messages
- Mirror their language in all drafts
- Traditional Chinese for Taiwanese buyers — never Simplified
- English for Australian buyers
- If unsure, ask the agent

## Communication Style
- Conversational, warm, professional
- Never robotic or template-sounding
- Adapt to the agent's corrections — when they edit your drafts, learn from it

## Commands the Agent Can Give You
- "add lead [details]" — create a new lead
- "update [name] — [changes]" — update lead info
- "[name] is hot/warm/cold now" — change temperature
- "don't follow up on [name]" — pause follow-ups
- "that was [colleague name]" — mark last message as colleague, not agent
- "never say [X], always say [Y]" — add a voice rule
- "show me all leads" — list active leads
- "what's pending?" — show pending approvals
```

- [ ] **Step 2: Copy skill to OpenClaw skills directory**

```bash
mkdir -p ~/.openclaw/skills/re-copilot
cp skills/re-copilot/SKILL.md ~/.openclaw/skills/re-copilot/SKILL.md
```

- [ ] **Step 3: Commit**

```bash
git add skills/re-copilot/SKILL.md
git commit -m "feat: OpenClaw skill definition for real estate co-pilot behavior"
```

---

## Task 13: Approval Handler (Send After Approve)

**Files:**
- Create: `src/approval/approval-handler.ts`
- Create: `tests/approval/approval-handler.test.ts`

This connects the approval queue to the channel adapters — when the agent approves a draft, it gets sent via the correct channel. Edits are stored as voice examples.

- [ ] **Step 1: Write failing test**

```typescript
// tests/approval/approval-handler.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { ApprovalHandler } from "../../src/approval/approval-handler.js";
import { ApprovalQueue } from "../../src/approval/queue.js";
import { VoiceStore } from "../../src/voice/store.js";
import { Database } from "../../src/db.js";
import { unlinkSync, existsSync } from "fs";

const TEST_DB = "data/test-handler.db";
let db: Database;
let queue: ApprovalQueue;
let voiceStore: VoiceStore;
let handler: ApprovalHandler;
const mockSend = vi.fn().mockResolvedValue(true);

beforeEach(() => {
  db = new Database(TEST_DB);
  queue = new ApprovalQueue(db);
  voiceStore = new VoiceStore(db);
  handler = new ApprovalHandler(queue, voiceStore, mockSend);
  mockSend.mockClear();
  db.raw.prepare("INSERT INTO leads (id, name, preferred_channel, language) VALUES (?, ?, ?, ?)").run("lead-1", "Mrs Chen", "whatsapp", "zh-TW");
});

afterEach(() => {
  db.close();
  if (existsSync(TEST_DB)) unlinkSync(TEST_DB);
});

describe("ApprovalHandler", () => {
  it("sends message via adapter after approval", async () => {
    const item = queue.enqueue({
      leadId: "lead-1",
      draftMessage: "嗨 Mrs Chen",
      channel: "whatsapp",
      recipientId: "+61412345678",
      type: "follow_up",
    });

    queue.approve(item.id);
    await handler.processApproved();

    expect(mockSend).toHaveBeenCalledWith("whatsapp", "+61412345678", "嗨 Mrs Chen");
  });

  it("stores edit as voice example when message was edited", async () => {
    const item = queue.enqueue({
      leadId: "lead-1",
      draftMessage: "Original draft",
      channel: "whatsapp",
      recipientId: "+61412345678",
      type: "follow_up",
    });

    queue.editAndApprove(item.id, "Edited version");
    await handler.processApproved();

    expect(mockSend).toHaveBeenCalledWith("whatsapp", "+61412345678", "Edited version");
    const examples = voiceStore.getExamples("zh-TW");
    expect(examples).toHaveLength(1);
    expect(examples[0].originalDraft).toBe("Original draft");
    expect(examples[0].editedVersion).toBe("Edited version");
  });

  it("skips rejected items", async () => {
    const item = queue.enqueue({
      leadId: "lead-1",
      draftMessage: "Bad draft",
      channel: "whatsapp",
      recipientId: "+61412345678",
      type: "follow_up",
    });

    queue.reject(item.id);
    await handler.processApproved();

    expect(mockSend).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
npx vitest run tests/approval/approval-handler.test.ts
```

- [ ] **Step 3: Implement ApprovalHandler**

```typescript
// src/approval/approval-handler.ts
import { logger } from "../utils/logger.js";
import { ApprovalQueue } from "./queue.js";
import { VoiceStore } from "../voice/store.js";
import { Database } from "../db.js";

type SendFn = (channel: string, recipientId: string, content: string) => Promise<boolean>;

export class ApprovalHandler {
  constructor(
    private queue: ApprovalQueue,
    private voiceStore: VoiceStore,
    private sendFn: SendFn,
    private db?: Database
  ) {}

  async processApproved(): Promise<number> {
    // Get items that have been approved or edited but not yet sent
    const items = this.db
      ? this.db.raw.prepare(
          "SELECT aq.*, l.language FROM approval_queue aq JOIN leads l ON aq.lead_id = l.id WHERE aq.status IN ('approved', 'edited') AND aq.resolved_at IS NOT NULL"
        ).all() as any[]
      : [];

    let sent = 0;
    for (const item of items) {
      const messageToSend = item.edited_message || item.draft_message;

      try {
        const success = await this.sendFn(item.channel, item.recipient_id, messageToSend);
        if (!success) {
          logger.warn({ itemId: item.id }, "Failed to send approved message");
          continue;
        }

        // If the message was edited, store as voice example
        if (item.status === "edited" && item.edited_message) {
          this.voiceStore.addExample(item.draft_message, item.edited_message, item.language || "en");
          logger.info({ itemId: item.id }, "Voice example stored from edit");
        }

        // Mark as fully processed (update status to distinguish from pending approval)
        this.db?.raw.prepare(
          "UPDATE approval_queue SET status = 'sent' WHERE id = ?"
        ).run(item.id);

        sent++;
      } catch (err) {
        logger.error({ err, itemId: item.id }, "Error sending approved message");
      }
    }

    if (sent > 0) logger.info({ sent }, "Approved messages sent");
    return sent;
  }
}
```

Note: The `sent` status needs to be added to the schema. Update the `approval_queue` status to include `sent` as a valid value. The existing schema uses TEXT so no migration needed.

- [ ] **Step 4: Run tests to verify they pass**

```bash
npx vitest run tests/approval/approval-handler.test.ts
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/approval/approval-handler.ts tests/approval/approval-handler.test.ts
git commit -m "feat: approval handler — sends messages after approve, stores edits as voice examples"
```

---

## Task 14: Wire Everything Together in index.ts

**Files:**
- Modify: `src/index.ts`

- [ ] **Step 1: Implement the main orchestration**

```typescript
// src/index.ts
import { logger } from "./utils/logger.js";
import { config } from "./config.js";
import { Database } from "./db.js";
import { LeadStore } from "./leads/store.js";
import { ApprovalQueue } from "./approval/queue.js";
import { VoiceStore } from "./voice/store.js";
import { AdapterManager } from "./adapters/adapter-manager.js";
import { OpenClawBridge } from "./brain/openclaw-bridge.js";
import { FollowUpScheduler } from "./leads/follow-up-scheduler.js";
import { buildInboundMessagePrompt, buildAfterHoursPrompt } from "./brain/prompts.js";
import type { NormalizedMessage } from "./types.js";

async function main() {
  logger.info("RE Co-Pilot starting...");

  const db = new Database();
  const leadStore = new LeadStore(db);
  const approvalQueue = new ApprovalQueue(db);
  const voiceStore = new VoiceStore(db);
  const bridge = new OpenClawBridge(config.openclaw.gatewayUrl, config.openclaw.webhookSecret);
  const adapterManager = new AdapterManager();

  const handleMessage = async (msg: NormalizedMessage) => {
    logger.info({
      channel: msg.channel,
      sender: msg.sender,
      direction: msg.direction,
    }, "Message received");

    db.raw.prepare(`
      INSERT INTO messages (id, channel, sender, sender_name, content, timestamp, lang, direction, message_type, thread_id)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(msg.id, msg.channel, msg.sender, msg.senderName, msg.content, msg.timestamp.toISOString(),
           msg.lang, msg.direction, msg.messageType, msg.threadId);

    const existingLead = leadStore.findByChannelIdentity(msg.channel, msg.sender);

    // Timezone-aware business hours check
    const sydneyTime = new Date().toLocaleString("en-AU", { timeZone: config.businessHours.timezone });
    const hour = new Date(sydneyTime).getHours();
    const isAfterHours = hour < config.businessHours.start || hour >= config.businessHours.end;

    // After-hours prompt applies to ALL inbound buyer messages, not just new leads
    const prompt = isAfterHours && msg.direction === "inbound"
      ? buildAfterHoursPrompt(msg, existingLead)
      : buildInboundMessagePrompt(msg, existingLead);

    const response = await bridge.send(prompt);
    if (!response) {
      logger.warn("No response from OpenClaw — message logged but not processed");
      return;
    }

    logger.info({ response: response.substring(0, 100) }, "OpenClaw response");

    try {
      const parsed = JSON.parse(response);
      let resolvedLeadId = existingLead?.id;

      if (parsed.isNewLead && parsed.leadUpdate) {
        const newLead = leadStore.create({
          name: parsed.leadUpdate.name || msg.senderName || msg.sender,
          preferredChannel: msg.channel,
          language: parsed.leadUpdate.language || "en",
          propertyCriteria: parsed.leadUpdate.propertyCriteria,
          temperature: parsed.leadUpdate.temperature || "warm",
          conversationSummary: parsed.leadUpdate.conversationSummary,
          notes: parsed.leadUpdate.notes,
          channelIdentities: [{ channel: msg.channel, identifier: msg.sender }],
        });
        resolvedLeadId = newLead.id;
        logger.info({ leadId: newLead.id, name: newLead.name }, "New lead created");
      } else if (existingLead) {
        if (msg.direction === "inbound") {
          leadStore.updateLastContact(existingLead.id, "buyer");
        } else {
          leadStore.updateLastContact(existingLead.id, "agent");
        }
        if (parsed.leadUpdate?.conversationSummary) {
          leadStore.updateSummary(existingLead.id, parsed.leadUpdate.conversationSummary);
        }
      }

      if (parsed.shouldDraftReply && parsed.draftReply && resolvedLeadId) {
        approvalQueue.enqueue({
          leadId: resolvedLeadId,
          draftMessage: parsed.draftReply,
          channel: msg.channel as any,
          recipientId: msg.sender,
          type: isAfterHours ? "after_hours_reply" : "response",
        });
        logger.info({ leadId: resolvedLeadId }, "Draft queued for approval");
      }
    } catch {
      logger.warn("OpenClaw response was not parseable JSON — treating as conversational response");
    }
  };

  await adapterManager.startAll(handleMessage);

  const scheduler = new FollowUpScheduler(
    leadStore,
    approvalQueue,
    voiceStore,
    (prompt) => bridge.send(prompt)
  );
  scheduler.start();

  const shutdown = async () => {
    logger.info("Shutting down...");
    scheduler.stop();
    await adapterManager.stopAll();
    db.close();
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);

  logger.info({
    channels: {
      whatsapp: config.whatsapp.enabled,
      line: config.line.enabled,
      email: config.email.enabled,
    },
  }, "RE Co-Pilot ready");
}

main().catch((err) => {
  logger.fatal(err, "Failed to start RE Co-Pilot");
  process.exit(1);
});
```

- [ ] **Step 2: Verify it compiles**

```bash
npx tsx src/index.ts
```

Expected: Starts up, logs enabled channels, and begins monitoring.

- [ ] **Step 3: Commit**

```bash
git add src/index.ts
git commit -m "feat: wire all components together in main entry point"
```

---

## Task 15: Backup Script

**Files:**
- Create: `backup/backup.sh`

- [ ] **Step 1: Create backup script**

```bash
#!/bin/bash
# Daily backup of RE Co-Pilot data + OpenClaw memory
BACKUP_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/re-copilot-backups"
DATE=$(date +%Y-%m-%d_%H%M)
DEST="$BACKUP_DIR/$DATE"

mkdir -p "$DEST"

# Backup SQLite database
cp data/re-copilot.db "$DEST/" 2>/dev/null

# Backup OpenClaw memory
cp -r ~/.openclaw/memory "$DEST/openclaw-memory" 2>/dev/null

# Backup WhatsApp auth state
cp -r auth_info_baileys "$DEST/wa-auth" 2>/dev/null

# Keep only last 30 backups
ls -dt "$BACKUP_DIR"/*/ | tail -n +31 | xargs rm -rf 2>/dev/null

echo "Backup complete: $DEST"
```

- [ ] **Step 2: Make it executable and commit**

```bash
chmod +x backup/backup.sh
git add backup/backup.sh
git commit -m "feat: daily backup script for data and OpenClaw memory"
```

---

## Task 16: Integration Smoke Test

**Files:**
- Create: `tests/integration/smoke.test.ts`

- [ ] **Step 1: Write smoke test**

```typescript
// tests/integration/smoke.test.ts
import { describe, it, expect, afterEach } from "vitest";
import { Database } from "../../src/db.js";
import { LeadStore } from "../../src/leads/store.js";
import { ApprovalQueue } from "../../src/approval/queue.js";
import { VoiceStore } from "../../src/voice/store.js";
import { FollowUpScheduler } from "../../src/leads/follow-up-scheduler.js";
import { unlinkSync, existsSync } from "fs";

const TEST_DB = "data/test-smoke.db";

afterEach(() => {
  if (existsSync(TEST_DB)) unlinkSync(TEST_DB);
});

describe("End-to-end smoke test", () => {
  it("creates a lead, schedules follow-up, gets approval draft", async () => {
    const db = new Database(TEST_DB);
    const leadStore = new LeadStore(db);
    const approvalQueue = new ApprovalQueue(db);
    const voiceStore = new VoiceStore(db);

    // 1. Create a lead
    const lead = leadStore.create({
      name: "Mrs Chen",
      preferredChannel: "whatsapp",
      language: "zh-TW",
      propertyCriteria: { type: "3BR", location: "Chatswood", budget: "< $2M" },
      nextFollowUp: new Date(Date.now() - 86400000).toISOString().split("T")[0],
      channelIdentities: [{ channel: "whatsapp", identifier: "+61412345678" }],
    });
    expect(lead.id).toBeDefined();

    // 2. Add voice examples
    voiceStore.addExample("Hello, following up", "嗨，想跟你聊聊最近看房的進度", "zh-TW");
    voiceStore.addRule("Never use 您好, use 嗨 instead");

    // 3. Run follow-up scheduler with mock drafter
    const mockDraft = async () => "嗨 Mrs Chen，最近Chatswood有幾個不錯的房子，要不要看看？";
    const scheduler = new FollowUpScheduler(leadStore, approvalQueue, voiceStore, mockDraft);
    const queued = await scheduler.checkAndQueue();
    expect(queued).toBe(1);

    // 4. Check approval queue
    const pending = approvalQueue.getPending();
    expect(pending).toHaveLength(1);
    expect(pending[0].channel).toBe("whatsapp");
    expect(pending[0].type).toBe("follow_up");

    // 5. Simulate edit and approve
    approvalQueue.editAndApprove(pending[0].id, "嗨 Mrs Chen，Chatswood最近有個3房的不錯，有空聊聊嗎？");
    const resolved = approvalQueue.getById(pending[0].id);
    expect(resolved?.status).toBe("edited");

    // 6. Store the edit as a voice example
    voiceStore.addExample(pending[0].draftMessage, resolved!.editedMessage!, "zh-TW");
    const examples = voiceStore.getExamples("zh-TW");
    expect(examples).toHaveLength(2);

    db.close();
  });
});
```

- [ ] **Step 2: Run all tests**

```bash
npx vitest run
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/smoke.test.ts
git commit -m "test: end-to-end smoke test covering lead → follow-up → approval → voice learning"
```

---

## Post-Implementation Checklist

After all tasks are complete:

- [ ] Run `npx vitest run` — all tests pass
- [ ] Run `npx tsx src/index.ts` — starts without errors
- [ ] Complete Task 0 (OpenClaw validation spike) if not already done
- [ ] Connect WhatsApp via QR code and verify messages flow through
- [ ] Set up `.env` with real credentials
- [ ] Run `backup/backup.sh` and verify backup created
- [ ] Ask sister: WhatsApp or Line for command interface?
- [ ] Define business hours with sister
