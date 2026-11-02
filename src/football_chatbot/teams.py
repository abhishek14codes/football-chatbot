import unicodedata
from difflib import get_close_matches

from football_chatbot.db import get_connection

# normalized nickname -> normalized official name
ALIASES = {
    "barca": "fc barcelona",
    "barcelona": "fc barcelona",  # "barcelona" alone also matches Espanyol, so we pin it
    "psg": "paris saint-germain fc",
    "atleti": "club atletico de madrid",
    "man united": "manchester united fc",
    "man utd": "manchester united fc",
    "man city": "manchester city fc",
}


def _norm(s: str) -> str:
    """Lowercase and strip accents, so 'Atlético' == 'atletico'."""
    decomposed = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn").strip()


def _all_team_names() -> list[str]:
    sql = """
    SELECT home_team AS name FROM matches WHERE home_team IS NOT NULL
    UNION
    SELECT away_team FROM matches WHERE away_team IS NOT NULL
    """
    with get_connection() as conn:
        return [r["name"] for r in conn.execute(sql)]


def resolve_team(name: str) -> str | None:
    names = {_norm(n): n for n in _all_team_names()}
    key = ALIASES.get(_norm(name), _norm(name))
    if key in names:  # exact match
        return names[key]
    hits = [n for k, n in names.items() if key in k]  # substring match
    if len(hits) == 1:  # only if unambiguous
        return hits[0]
    close = get_close_matches(key, list(names), n=1, cutoff=0.7)  # typo tolerance
    return names[close[0]] if close else None