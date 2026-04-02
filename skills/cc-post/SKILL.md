---
name: cc-post
description: Publish approved content to any platform (RED, Instagram, Threads, X, LinkedIn, TikTok, YouTube). Use when user says "/cc-post", "publish to threads", "post to X", "post to instagram", "post this", or approves a draft for posting. Also triggers on "publish this" or "send it". Does NOT trigger on general publishing or deploy tasks.
---

# Post to Platform

Publish approved content to the target platform and update tracking files. Uses Python scripts for API platforms and Playwright/Chrome/manual fallback for X and RED.

## Paths

- Scripts dir: `~/Projects/multipost/scripts/`
- Env file: `~/Projects/multipost/.env`
- Ideas vault: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/ideas.md`
- Posts log: `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/brain/content/posts.md`

## Steps

1. **Get the post text and platform:**
   - If provided directly → use it
   - If user says "post the last draft" → use the most recent draft from this conversation
   - Platform should be clear from the draft context
   - If platform is ambiguous → ask: "Which platform? (x / threads / instagram / tiktok / youtube / linkedin / red)"
   - If posting to multiple platforms → handle each separately (content may differ per platform)

2. **Final confirmation:** Show the full post text and ask:

   Ready to post to **[Platform]**?

   ---
   [post text]
   ---

   Post this? (y/n)

3. **Wait for explicit "y" or "yes"** before proceeding. Never auto-post.

4. **Time selection:**

   > **Post now, schedule for a specific time, or research best time?**

   - **Now** → proceed to step 5 immediately
   - **Schedule** → user provides a time → construct the `at` command (see Scheduling section) → tell user the job number → done
   - **Research best time** → show the guidelines below, suggest a specific time based on platform, then ask user to confirm → schedule via `at`

   **Best-Time Guidelines (AEST):**

   | Platform | Best times | Notes |
   |----------|-----------|-------|
   | RED | 7-9 PM | Chinese audience evening browse |
   | Threads | 8-10 AM or 6-8 PM | Engagement peaks |
   | Instagram | 8-10 AM or 6-8 PM | Same as Threads |
   | X | 8-10 AM or 12-1 PM | Weekday mornings/lunch |
   | LinkedIn | Tue-Thu 8-10 AM | Professional morning hours |
   | TikTok | 7-9 PM | Evening entertainment window |
   | YouTube | Fri-Sat 5-7 PM | Weekend leisure time |

5. **Publish per platform:**

   ### Threads (Python script)

   Before posting, ask the user which topic tag to use (Threads allows 1 topic per post). Suggest a relevant topic based on the post content. Topic must be 1-50 chars, no periods or ampersands, plain text (no `#` prefix).

   Without topic:
   ```bash
   cd ~/Projects/content && python3 scripts/post_threads.py "[post text]"
   ```

   With topic:
   ```bash
   cd ~/Projects/content && python3 scripts/post_threads.py --topic "[topic]" "[post text]"
   ```

   ### Instagram (Python script)

   Requires image media. If user hasn't provided image URLs, ask:
   "Instagram requires images (at least 2 for carousel). Paste the URLs (comma-separated):"

   ```bash
   cd ~/Projects/content && python3 scripts/post_instagram.py --images "[url1,url2]" "[caption text]"
   ```

   ### LinkedIn (Python script)

   ```bash
   cd ~/Projects/content && python3 scripts/post_linkedin.py "[post text]"
   ```

   With image:
   ```bash
   cd ~/Projects/content && python3 scripts/post_linkedin.py --media "/path/to/image.jpg" "[post text]"
   ```

   ### TikTok (Python script)

   Requires video media. If user hasn't provided a video, ask:
   "TikTok requires a video. Paste the file path:"

   ```bash
   cd ~/Projects/content && python3 scripts/post_tiktok.py --media "/path/to/video.mp4" "[caption text]"
   ```

   ### YouTube (Python script)

   Requires video media and a title. If user hasn't provided these, ask.

   ```bash
   cd ~/Projects/content && python3 scripts/post_youtube.py --media "/path/to/video.mp4" --title "[title]" "[description]"
   ```

   For Shorts:
   ```bash
   cd ~/Projects/content && python3 scripts/post_youtube.py --short --media "/path/to/video.mp4" --title "[title]" "[description]"
   ```

   ### X (Playwright browser automation — triple fallback)

   X API credits are depleted. Use browser automation instead.

   **Fallback 1: Playwright MCP**

   **Single tweet:**
   1. `browser_navigate` to `https://x.com/compose/post`
   2. `browser_snapshot` — check if login page appears
      - If login page: tell user "X needs you to log in. Please log in in the Playwright browser window, then tell me when you're done." Wait for user confirmation, then `browser_snapshot` again.
   3. `browser_snapshot` — find the compose text area
   4. `browser_click` on the text input area (ref from snapshot)
   5. `browser_type` the tweet text into the compose box
   6. `browser_snapshot` — find the "Post" button
   7. `browser_click` the "Post" button
   8. `browser_wait_for` — wait 3 seconds for post to complete
   9. `browser_snapshot` — verify post was submitted (compose should close or show success)

   **Thread (multiple tweets):**
   1. `browser_navigate` to `https://x.com/compose/post`
   2. `browser_click` the compose text area
   3. `browser_type` tweet 1 text
   4. `browser_snapshot` — find the "+" button to add another tweet to the thread
   5. `browser_click` the "+" button
   6. `browser_type` tweet 2 text in the new compose box
   7. Repeat steps 4-6 for all remaining tweets
   8. `browser_click` "Post all" button to publish the entire thread at once

   If any Playwright step fails or times out → move to Fallback 2.

   **Fallback 2: Chrome MCP**

   Same flow using `mcp__claude-in-chrome__*` tools:
   1. `tabs_context_mcp` to get tab context
   2. `tabs_create_mcp` to create a new tab
   3. `navigate` to `https://x.com/compose/post`
   4. `read_page` to inspect the compose form
   5. `form_input` or `computer` to type the tweet
   6. `computer` to click Post

   If Chrome MCP fails → move to Fallback 3.

   **Fallback 3: Manual copy-paste**

   Present each tweet as a numbered copy-paste block:
   ```
   --- X THREAD ---

   Tweet 1:
   [tweet 1 text]

   Tweet 2 (reply to tweet 1):
   [tweet 2 text]

   ...

   --- END ---

   Post tweet 1 first, then reply to it with tweet 2, and so on.
   ```

   Then say: "Automated posting to X failed. Copy-paste blocks ready above. Tell me when you've posted and I'll update the tracking files."

   ### RED (Triple fallback — no API)

   RED has no public API. Try methods in this order:

   **Fallback 1: Playwright MCP**

   If `~/.config/cc-post/red-selectors.json` exists, read it for selectors. Otherwise use defaults:
   - Navigate to `https://creator.xiaohongshu.com/publish/publish`
   - Look for the title input, body textarea, and publish button
   - Fill in title and body, upload cover image if provided, then click publish

   Use `mcp__plugin_playwright_playwright__browser_navigate`, `browser_snapshot`, `browser_fill_form`, `browser_click` etc. If any Playwright step fails or times out, move to Fallback 2.

   **Fallback 2: Chrome MCP**

   Use `mcp__claude-in-chrome__navigate` to open the RED creator page, then `mcp__claude-in-chrome__read_page` to inspect the DOM, and `mcp__claude-in-chrome__form_input` / `mcp__claude-in-chrome__computer` to fill and submit. If this fails, move to Fallback 3.

   **Fallback 3: Manual copy-paste**

   Present structured copy-paste block:
   ```
   --- RED POST ---

   Title: [title text — first 18 chars contain 2 core keywords]

   [body text]

   [hashtags]

   --- END ---

   Remember: Add cover image (3:4 vertical, bold text overlay) before posting.
   ```

   Then say: "Automated posting to RED failed. Copy-paste block ready above. Tell me when you've posted and I'll update the tracking files."

## Scheduling via `at`

For scheduled posts, construct and run:

```bash
echo "cd /Users/mikeweng/Projects/content && python3 scripts/post_<platform>.py '[post text]'" | at <time>
```

Examples:
- `at 0830 tomorrow` — 8:30 AM tomorrow
- `at 7:00 PM` — 7 PM today
- `at 2:00 PM Mar 30` — specific date/time

After scheduling:
- Tell the user the `at` job number (from the output)
- Tell them they can cancel with `atrm <job_number>` or list pending jobs with `atq`

**Scheduling limitations:**
- X and RED use browser automation — cannot be scheduled. Warn user: "X/RED posting uses browser automation which can't schedule ahead. I'll post it now instead."
- If Mac sleeps through the scheduled time, the job runs on wake

## On Success

- Read ideas vault — if this post came from a queued idea, update its status to `posted` with today's date and platform
- Append to posts log:
  ```
  - **[YYYY-MM-DD]** [platform] [first 30 chars of post text]...
    - Text: [full post text]
    - Platform: [x | threads | instagram | tiktok | youtube | linkedin | red]
    - Link: [permalink URL or "manual post"]
  ```
- For automated platforms: "Posted to [Platform]! [permalink URL]"
- For manual platforms (RED/X fallback): "Copy-paste block ready above. Tell me when you've posted and I'll update the tracking files."

## On Failure

- If 401 / auth error: "Token expired. Update the token in `~/Projects/multipost/.env` for [platform]."
- If 403: "Permission denied — check API scopes/tier for [platform]."
- If 4xx: Show the error message and suggest a fix
- If 5xx: "[Platform] server error. Try again in a minute."
- Do NOT retry automatically — show the error and let user decide

## On Partial Failure (multi-platform)

- Log and report successes immediately
- Report each failure with its error
- Ask: "Retry failed platforms? (y/n)"
- Only retry the specific platforms that failed

## Rules

- NEVER post without explicit user confirmation
- NEVER modify the post text — post exactly what was approved
- Each platform gets its own separate script call — never batch
- If a script fails, do NOT retry automatically — show the error and let user decide
- For manual platforms (RED/X fallback): present the copy-paste block and wait for user to confirm they've posted
- Instagram requires image media (at least 2) — ask before posting
- TikTok requires video media — ask before posting
- YouTube requires video media and a title — ask before posting
