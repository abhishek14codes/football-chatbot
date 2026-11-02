from football_chatbot.db import get_connection
from football_chatbot.teams import resolve_team


def get_team_results(team: str, limit: int = 5) -> list[dict]:
    resolved = resolve_team(team)
    if resolved is None:
        raise ValueError(f"Unknown team: {team!r}")

    sql = """
    SELECT utc_date, competition, home_team, away_team, home_goals, away_goals
    FROM matches
    WHERE status = 'FINISHED' AND (home_team = :team OR away_team = :team)
    ORDER BY utc_date DESC
    LIMIT :limit
    """
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, {"team": resolved, "limit": limit})]