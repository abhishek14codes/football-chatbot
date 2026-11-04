import os
import time
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

from football_chatbot.db import get_connection, init_db

load_dotenv()
API_KEY = os.getenv("GUARDIAN_API_KEY")
URL = "https://content.guardianapis.com/search"
BACKFILL_DAYS = 14
MAX_PAGES = 20

INSERT = """
INSERT OR IGNORE INTO articles (url, source, title, published_at, body, fetched_at)
VALUES (:url, 'guardian', :title, :published_at, :body, :fetched_at)
"""


def fetch_page(from_date: str, page: int) -> dict:
    r = requests.get(
        URL,
        params={
            "section": "football",
            "order-by": "newest",
            "from-date": from_date,
            "page-size": 50,
            "page": page,
            "show-fields": "bodyText",
            "api-key": API_KEY,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["response"]


def ingest_articles():
    init_db()
    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=BACKFILL_DAYS)).strftime("%Y-%m-%d")
    saved = 0
    with get_connection() as conn:
        page = 1
        while page <= MAX_PAGES:
            resp = fetch_page(from_date, page)
            for item in resp["results"]:
                body = item.get("fields", {}).get("bodyText", "")
                if not body:
                    continue  # skip items with no text
                cur = conn.execute(INSERT, {
                    "url": item["webUrl"],
                    "title": item["webTitle"],
                    "published_at": item["webPublicationDate"],
                    "body": body,
                    "fetched_at": now.isoformat(),
                })
                saved += cur.rowcount  # 1 if new, 0 if already stored
            if page >= resp["pages"]:
                break
            page += 1
            time.sleep(1)
    print(f"{saved} new articles saved")


if __name__ == "__main__":
    ingest_articles()