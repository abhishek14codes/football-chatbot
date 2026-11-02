import os
import time

import requests
from dotenv import load_dotenv

from football_chatbot.db import get_connection, init_db

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA")
BASE_URL = "https://api.football-data.org/v4"
COMPETITIONS = ["PD", "PL", "CL", "BL1", "SA", "FL1", "DED", "PPL", "ELC", "BSA", "WC", "EC"]
PAUSE_SECONDS = 7  # free tier allows 10 requests per minute

UPSERT = """
INSERT INTO matches (id, utc_date, status, competition, stage, matchday,
                     home_team, away_team, home_goals, away_goals, last_updated)
VALUES (:id, :utc_date, :status, :competition, :stage, :matchday,
        :home_team, :away_team, :home_goals, :away_goals, :last_updated)
ON CONFLICT(id) DO UPDATE SET
    utc_date=excluded.utc_date, status=excluded.status, stage=excluded.stage,
    matchday=excluded.matchday, home_team=excluded.home_team,
    away_team=excluded.away_team, home_goals=excluded.home_goals,
    away_goals=excluded.away_goals, last_updated=excluded.last_updated
"""


def fetch_matches(code):
    response = requests.get(
        f"{BASE_URL}/competitions/{code}/matches",
        headers={"X-Auth-Token": API_KEY},
        timeout=30,
    )
    response.raise_for_status()  # raises on 403/429 instead of crashing later
    return response.json()["matches"]


def to_row(m):
    full = m["score"]["fullTime"]
    return {
        "id": m["id"],
        "utc_date": m["utcDate"],
        "status": m["status"],
        "competition": m["competition"]["code"],
        "stage": m["stage"],
        "matchday": m["matchday"],
        "home_team": m["homeTeam"]["name"],
        "away_team": m["awayTeam"]["name"],
        "home_goals": full["home"],
        "away_goals": full["away"],
        "last_updated": m["lastUpdated"],
    }


def ingest():
    init_db()
    with get_connection() as conn:
        for code in COMPETITIONS:
            try:
                rows = [to_row(m) for m in fetch_matches(code)]
            except requests.HTTPError as e:
                print(f"{code}: skipped ({e})")
            else:
                conn.executemany(UPSERT, rows)
                print(f"{code}: {len(rows)} matches saved")
            time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    ingest()