# storage.py
# Tracks which job postings have already been sent to Telegram, so repeated
# scans only alert on NEW postings, not the same ones every run.

import sqlite3
import hashlib
import os

DB_PATH = os.environ.get("DB_PATH", "/data/jobs.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            source TEXT,
            first_seen TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn


def _job_id(job: dict) -> str:
    raw = (job.get("title", "") + job.get("link", "")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def filter_new_jobs(jobs: list) -> list:
    """Given a list of scraped jobs, return only the ones not seen before,
    and record them as seen."""
    conn = _connect()
    new_jobs = []
    for job in jobs:
        if job.get("error"):
            continue
        jid = _job_id(job)
        row = conn.execute("SELECT 1 FROM seen_jobs WHERE id = ?", (jid,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO seen_jobs (id, title, link, source) VALUES (?, ?, ?, ?)",
                (jid, job["title"], job["link"], job["source"]),
            )
            new_jobs.append(job)
    conn.commit()
    conn.close()
    return new_jobs
