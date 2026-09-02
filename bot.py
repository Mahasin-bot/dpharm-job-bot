# bot.py
# Entry point. Runs a Telegram bot that:
#   - On a schedule (default every 6 hours), scans all configured SOURCES
#     for new D.Pharm Government Pharmacist postings and pushes them to you,
#     West Bengal jobs first.
#   - Responds to /latest for an on-demand full scan.
#   - Responds to /start and /help.

import os
import logging
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from sources import SOURCES
from scraper import scrape_all
from storage import filter_new_jobs

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("dpharm-bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]          # required
CHAT_ID = os.environ["CHAT_ID"]              # required - your personal chat id

IST = ZoneInfo("Asia/Kolkata")
# Fixed daily scan times (IST): 6:00 AM and 6:00 PM.
# Override via env vars if you ever want different times, e.g. SCAN_TIMES=07:00,19:30
_default_times = ["06:00", "18:00"]
SCAN_TIMES = [
    time(*map(int, t.split(":")), tzinfo=IST)
    for t in os.environ.get("SCAN_TIMES", ",".join(_default_times)).split(",")
]


def format_job(job: dict) -> str:
    loc = job["state"]
    if job.get("district"):
        loc += f" — {job['district']}"
    return (
        f"{job['priority_label']}\n"
        f"*{job['title']}*\n"
        f"📍 Location: {loc}\n"
        f"🏢 Recruitment: {job['source']}\n"
        f"📅 Last Date: {job['last_date']}\n"
        f"🔗 [Apply / Notice link]({job['link']})"
    )


async def run_scan(context: ContextTypes.DEFAULT_TYPE, chat_id: str, notify_if_empty: bool):
    all_jobs = scrape_all(SOURCES)

    errors = [j for j in all_jobs if j.get("error")]
    for e in errors:
        log.warning(f"Source failed: {e['source']} -> {e['message']}")

    valid_jobs = [j for j in all_jobs if not j.get("error")]
    new_jobs = filter_new_jobs(valid_jobs)

    if not new_jobs:
        if notify_if_empty:
            await context.bot.send_message(chat_id=chat_id, text="No new D.Pharm pharmacist postings found right now.")
        return

    for job in new_jobs:
        await context.bot.send_message(
            chat_id=chat_id,
            text=format_job(job),
            parse_mode="Markdown",
            disable_web_page_preview=False,
        )


async def scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    await run_scan(context, CHAT_ID, notify_if_empty=False)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "D.Pharm Govt Pharmacist Job Alert Bot is running.\n\n"
        "I scan Central & State government sources for D.Pharm Pharmacist "
        "vacancies, with West Bengal jobs prioritized.\n\n"
        f"Auto-scan runs daily at {', '.join(t.strftime('%I:%M %p') for t in SCAN_TIMES)} IST.\n"
        "Use /latest to force a scan right now."
    )


async def cmd_latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Scanning all sources now, this may take a moment...")
    await run_scan(context, update.effective_chat.id, notify_if_empty=True)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/latest - run an on-demand scan\n"
        "/start - bot info\n"
        "/help - this message\n\n"
        "Sources are configured in sources.py - add more state PSCs or WB "
        "district health societies there any time."
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("latest", cmd_latest))
    app.add_handler(CommandHandler("help", cmd_help))

    for t in SCAN_TIMES:
        app.job_queue.run_daily(scheduled_job, time=t)
    log.info(f"Scheduled daily scans at (IST): {[t.strftime('%H:%M') for t in SCAN_TIMES]}")

    log.info("Bot starting, polling for updates...")
    app.run_polling()


if __name__ == "__main__":
    main()
