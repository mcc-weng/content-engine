---
name: cc-capture
description: Capture raw content ideas into the ideas vault. Use when user says "/cc-capture", "capture this for content", "idea for a post", or "save this for content". Does NOT trigger on general URL sharing or non-content tasks.
---

# Capture Content Idea

Capture a raw content idea and store it in the ideas vault for later drafting.

## Paths

- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/ideas.md`
- Format reference: `references/ideas-vault-format.md`

## Steps

1. **Accept input** — text, URL, screenshot, or half-formed thought. Whatever the user gives you.

2. **If URL:** Use WebFetch to retrieve and summarize the content in 1-2 sentences.

3. **Classify type:** Pick one based on the Honest Tinkerer content types:
   - `i-tried` — tested something, honest result (tool review, experiment)
   - `what-i-built` — demo of real product/feature
   - `aha` — surprising insight from building or conversation
   - `mistake` — what went wrong and why
   - `cool-tool` — tool discovery, testing claims
   - `hot-take` — opinion, engineering lens on hype
   - `reference` — link or resource to revisit later (not a post itself)

4. **Classify platform:** Pick one: `red` | `instagram` | `threads` | `x` | `linkedin` | `all`
   - If user specifies a platform → use it
   - If idea is in Chinese → default to `red` (primary Chinese platform)
   - If idea is in English → default to `x` (primary English platform)
   - If idea works for multiple audiences → use `all`
   - When in doubt → use `all`

5. **Append to ideas vault:** Read `content-ideas.md`, then append a new entry under `## Queue` using the format in `references/ideas-vault-format.md`. Use today's date. Preserve the user's original input verbatim in the `Raw:` field.

6. **Suggest angle** if one is obvious from the input. Otherwise set to "none yet".

7. **Confirm** with one line: what was captured, what type, which platform, and the angle (if any).

## Rules

- Do NOT draft the post — that's `/cc-draft`
- Do NOT ask clarifying questions unless the input is completely ambiguous
- Keep it fast — capture should feel instant
- Always set Status to `raw`
