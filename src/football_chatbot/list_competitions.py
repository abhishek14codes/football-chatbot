import os

import requests
from dotenv import load_dotenv

load_dotenv()

r = requests.get(
    "https://api.football-data.org/v4/competitions",
    headers={"X-Auth-Token": os.getenv("FOOTBALL_DATA")},
    timeout=30,
)
r.raise_for_status()

for c in r.json()["competitions"]:
    print(c["code"], "|", c["name"], "|", c["area"]["name"], "|", c.get("plan"))