from football_chatbot.competitions import resolve_competition
from football_chatbot.db import get_connection
from football_chatbot.teams import resolve_team

# competitions that have one table (WC and EC have groups, so they're excluded)
TABLE_COMPETITIONS = {"PD", "PL", "BL1", "SA", "FL1", "DED", "PPL", "ELC", "BSA", "CL"}


def _team_or_error(team: str) -> str:
    resolved = resolve_team(team)
    if resolved is None:
        raise ValueError(f"Unknown team: {team!r}")
    return resolved


def get_team_results(team: str, limit: int = 5, competition: str | None = None) -> list[dict]:
    team = _team_or_error(team)
    code = None
    if competition:
        code = resolve_competition(competition)
        if code is None:
            raise ValueError(f"Unknown competition: {competition!r}")
    sql = """
    SELECT utc_date, competition, stage, matchday, home_team, away_team,
           home_goals, away_goals
    FROM matches
    WHERE status = 'FINISHED' AND (home_team = :team OR away_team = :team)
      AND (:comp IS NULL OR competition = :comp)
    ORDER BY utc_date DESC
    LIMIT :limit
    """
    with get_connection() as conn:
        rows = conn.execute(sql, {"team": team, "comp": code, "limit": limit})
        return [dict(r) for r in rows]


def get_fixtures(team: str, competition: str | None = None, limit: int = 5) -> list[dict]:
    team = _team_or_error(team)
    code = None
    if competition:
        code = resolve_competition(competition)
        if code is None:
            raise ValueError(f"Unknown competition: {competition!r}")
    sql = """
    SELECT utc_date, competition, stage, matchday, home_team, away_team
    FROM matches
    WHERE status IN ('SCHEDULED', 'TIMED')
      AND (home_team = :team OR away_team = :team)
      AND (:comp IS NULL OR competition = :comp)
      AND utc_date >= strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
    ORDER BY utc_date ASC
    LIMIT :limit
    """
    with get_connection() as conn:
        rows = conn.execute(sql, {"team": team, "comp": code, "limit": limit})
        return [dict(r) for r in rows]


def get_standings(competition: str) -> list[dict]:
    code = resolve_competition(competition)
    if code is None:
        raise ValueError(f"Unknown competition: {competition!r}")
    if code not in TABLE_COMPETITIONS:
        raise ValueError(f"{code} has no single league table (groups or knockouts)")
    sql = """
    WITH results AS (
        SELECT home_team AS team, home_goals AS gf, away_goals AS ga
        FROM matches
        WHERE competition = :comp AND status = 'FINISHED'
          AND stage IN ('REGULAR_SEASON', 'LEAGUE_STAGE')
        UNION ALL
        SELECT away_team, away_goals, home_goals
        FROM matches
        WHERE competition = :comp AND status = 'FINISHED'
          AND stage IN ('REGULAR_SEASON', 'LEAGUE_STAGE')
    )
    SELECT team,
           COUNT(*) AS played,
           SUM(gf > ga) AS won, SUM(gf = ga) AS drawn, SUM(gf < ga) AS lost,
           SUM(gf) AS goals_for, SUM(ga) AS goals_against,
           SUM(gf) - SUM(ga) AS goal_diff,
           SUM(CASE WHEN gf > ga THEN 3 WHEN gf = ga THEN 1 ELSE 0 END) AS points
    FROM results
    GROUP BY team
    ORDER BY points DESC, goal_diff DESC, goals_for DESC
    """
    with get_connection() as conn:
        rows = [dict(r) for r in conn.execute(sql, {"comp": code})]
    for i, row in enumerate(rows, start=1):
        row["position"] = i
    return rows
def get_head_to_head(team_a: str, team_b: str, limit: int = 5) -> list[dict]:
    a, b = _team_or_error(team_a), _team_or_error(team_b)
    sql = """
    SELECT utc_date, competition, home_team, away_team, home_goals, away_goals
    FROM matches
    WHERE status = 'FINISHED'
      AND ((home_team = :a AND away_team = :b) OR (home_team = :b AND away_team = :a))
    ORDER BY utc_date DESC
    LIMIT :limit
    """
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, {"a": a, "b": b, "limit": limit})]


def get_results_vs_top_teams(team: str, competition: str, top_n: int = 6) -> dict:
    team = _team_or_error(team)
    table = get_standings(competition)  # raises for unknown/no-table competitions
    code = resolve_competition(competition)
    top = {r["team"] for r in table[:top_n]} - {team}
    sql = """
    SELECT utc_date, home_team, away_team, home_goals, away_goals
    FROM matches
    WHERE competition = :comp AND status = 'FINISHED'
      AND (home_team = :team OR away_team = :team)
    ORDER BY utc_date
    """
    with get_connection() as conn:
        rows = [dict(r) for r in conn.execute(sql, {"comp": code, "team": team})]

    matches = []
    for r in rows:
        home = r["home_team"] == team
        opponent = r["away_team"] if home else r["home_team"]
        if opponent not in top:
            continue
        gf, ga = (r["home_goals"], r["away_goals"]) if home else (r["away_goals"], r["home_goals"])
        result = "W" if gf > ga else "D" if gf == ga else "L"
        matches.append({
            "date": r["utc_date"], "opponent": opponent,
            "venue": "home" if home else "away", "score": f"{gf}-{ga}", "result": result,
        })
    record = {k: sum(m["result"] == k for m in matches) for k in ("W", "D", "L")}
    return {"team": team, "competition": code, "top_n": top_n,
            "opponents": sorted(top), "record": record, "matches": matches}


def get_team_stats(team: str, competition: str | None = None) -> dict:
    team = _team_or_error(team)
    code = None
    if competition:
        code = resolve_competition(competition)
        if code is None:
            raise ValueError(f"Unknown competition: {competition!r}")
    sql = """
    WITH g AS (
        SELECT 'home' AS venue, home_goals AS gf, away_goals AS ga FROM matches
        WHERE status = 'FINISHED' AND home_team = :team AND (:comp IS NULL OR competition = :comp)
        UNION ALL
        SELECT 'away', away_goals, home_goals FROM matches
        WHERE status = 'FINISHED' AND away_team = :team AND (:comp IS NULL OR competition = :comp)
    )
    SELECT venue, COUNT(*) AS played, SUM(gf > ga) AS won, SUM(gf = ga) AS drawn,
           SUM(gf < ga) AS lost, SUM(gf) AS goals_for, SUM(ga) AS goals_against,
           SUM(ga = 0) AS clean_sheets
    FROM g GROUP BY venue
    """
    with get_connection() as conn:
        splits = {r["venue"]: dict(r) for r in conn.execute(sql, {"team": team, "comp": code})}

    keys = ("played", "won", "drawn", "lost", "goals_for", "goals_against", "clean_sheets")
    total = {k: sum(s[k] for s in splits.values()) for k in keys}
    if total["played"]:
        total["goals_for_per_game"] = round(total["goals_for"] / total["played"], 2)
        total["goals_against_per_game"] = round(total["goals_against"] / total["played"], 2)
    return {"team": team, "competition": code or "all", "home": splits.get("home"),
            "away": splits.get("away"), "total": total}


def get_upcoming_matches(competition: str, days: int = 7, limit: int = 20) -> list[dict]:
    code = resolve_competition(competition)
    if code is None:
        raise ValueError(f"Unknown competition: {competition!r}")
    sql = """
    SELECT utc_date, stage, matchday, home_team, away_team
    FROM matches
    WHERE competition = :comp AND status IN ('SCHEDULED', 'TIMED')
      AND utc_date >= strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
      AND utc_date <= strftime('%Y-%m-%dT%H:%M:%SZ', 'now', '+' || :days || ' days')
    ORDER BY utc_date
    LIMIT :limit
    """
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, {"comp": code, "days": days, "limit": limit})]

def search_articles(
    topics: list[str], team: str | None = None, days: int = 90, limit: int = 5) -> list[dict]:
    def quote(t: str) -> str:
        return '"' + t.replace('"', " ").strip() + '"'

    terms = [quote(t) for t in topics if t.strip()]
    if not terms:
        raise ValueError("Give at least one search phrase")
    match = "(" + " OR ".join(terms) + ")"
    if team:
        match = f"{quote(team)} AND {match}"

    sql = """
    SELECT a.title, a.url, a.source, a.published_at,
           snippet(articles_fts, 1, '[', ']', ' ... ', 64) AS excerpt
    FROM articles_fts JOIN articles a ON a.id = articles_fts.rowid
    WHERE articles_fts MATCH :q
      AND a.published_at >= strftime('%Y-%m-%dT%H:%M:%SZ', 'now', '-' || :days || ' days')
    ORDER BY articles_fts.rank
    LIMIT :limit
    """
    with get_connection() as conn:
        rows = conn.execute(sql, {"q": match, "days": days, "limit": min(limit, 10)})
        return [dict(r) for r in rows]

def get_article(url: str, max_chars: int = 12000) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT title, url, source, published_at, body FROM articles WHERE url = ?",
            (url,),
        ).fetchone()
    if row is None:
        raise ValueError("Article not found; use a url returned by search_articles")
    article = dict(row)
    article["truncated"] = len(article["body"]) > max_chars
    article["body"] = article["body"][:max_chars]
    return article