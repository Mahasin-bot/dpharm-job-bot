# D.Pharm Government Pharmacist Job Alert Bot

Personal Telegram bot that scans Central & State government recruitment
pages for D.Pharm Pharmacist vacancies, tags location (with West Bengal
district detection), scores priority, and pushes **only new** postings to
your phone. West Bengal postings are boosted to top priority automatically.

## What it sends you, per job
- Priority (🔴 High = West Bengal / 🟠 Medium = other state / 🟡 Standard = Central)
- Recruitment body
- Location (state, + district if it's a WB posting)
- Last date (best-effort extracted — always verify on the source page)
- Direct link to the notice/apply page

## 1. Get your Telegram Chat ID
You already have a bot token from BotFather. Now get your personal chat ID:
1. Open Telegram, search for your bot, send it any message (e.g. "hi").
2. In a browser, visit:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat":{"id":123456789,...}` in the response — that number is your `CHAT_ID`.

## 2. Deploy on Railway (free tier)
1. Create a new GitHub repo and push these files to it (or use Railway's
   "Deploy from local folder" via their CLI).
2. Go to https://railway.app → New Project → Deploy from GitHub repo → select this repo.
3. Railway should auto-detect Python. If it doesn't pick up the `Procfile`,
   set the **Start Command** manually to: `python bot.py`
4. Under **Variables**, add:
   - `BOT_TOKEN` = your BotFather token
   - `CHAT_ID` = your chat id from step 1
   - `SCAN_TIMES` = `06:00,18:00` (IST — scans run daily at 6 AM and 6 PM; optional, this is already the default)
   - `DB_PATH` = `/data/jobs.db`
5. Add a **Volume** mounted at `/data` (Railway → your service → Volumes tab)
   so the "already seen" job database survives restarts/redeploys — without
   this, the bot will re-notify you of the same jobs after every redeploy.
6. Deploy. Check the logs — you should see `Bot starting, polling for updates...`
7. Message your bot `/start` on Telegram to confirm it's alive.

(Render works the same way: create a **Background Worker** service instead
of a Web Service, same env vars, same volume-for-`/data` idea using Render's
persistent disks.)

## 3. Commands
- `/start` — confirms the bot is running
- `/latest` — force an immediate full scan (useful for testing)
- `/help` — command list

## 4. Extending sources (important — read this)
`sources.py` currently ships with the major official WB and Central bodies
(WBHRB, WBPSC, WB Health Dept, SSC, ESIC, DGHS, Indian Army, RRB). Government
sites restructure their pages often, and there is no single official
aggregator for "all D.Pharm pharmacist jobs in India" — so realistically
you'll want to:

- Check the bot's Railway logs occasionally for `Source failed:` warnings
  (means a URL changed/moved) and update the URL in `sources.py`.
- Add more state PSCs / Health Recruitment Boards as you find them, and — this
  is the biggest opportunity for better WB district coverage — add each WB
  **District Health & Family Welfare Samiti** notice page as you locate a
  stable URL for it (template provided as a comment in `sources.py`).
- Each source just needs `name`, `url`, `state`, `district`, `base_priority`
  — no code changes required elsewhere.

## 5. Known limitations (honest list)
- The scraper is intentionally generic (reads HTML tables/link lists) rather
  than hand-tuned per site, so it's more resilient to redesigns but can
  occasionally miss postings on unusually-structured pages, or extract an
  imprecise "last date" — always confirm on the source page before relying
  on a deadline.
- Sites requiring JavaScript to render their listings (rare for these
  official portals, but possible) won't be readable by this scraper as-is;
  those would need a headless-browser approach (e.g. Playwright) added to
  `scraper.py` for that specific source.
- This was built without live network access to test against the real
  current HTML of each site, so double-check each URL in `sources.py` still
  points to the correct notice page before your first deploy.
