import os

import requests
from dotenv import load_dotenv

load_dotenv()

r = requests.get(
    "https://content.guardianapis.com/search",
    params={
        "q": "Barcelona",
        "section": "football",
        "order-by": "newest",
        "page-size": 5,
        "show-fields": "headline,bodyText",
        "api-key": os.getenv("GUARDIAN_API_KEY"),
    },
    timeout=30,
)
print(r.status_code)
r.raise_for_status()

for item in r.json()["response"]["results"]:
    body = item["fields"].get("bodyText", "")
    print(item["webPublicationDate"], "|", item["webTitle"])
    print("  ", item["webUrl"])
    print("  body chars:", len(body))