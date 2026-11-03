from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from football_chatbot import queries

mcp = FastMCP("football")


def _run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except ValueError as e:
        raise ToolError(str(e))


@mcp.tool
def team_results(team: str, limit: int = 5, competition: str | None = None) -> list[dict]:
    """Get a team's most recent finished matches, newest first. Optionally
    filter by competition ('champions league', 'la liga', ...). Accepts
    nicknames like 'Barca' or 'psg'. Current season only. Dates are UTC."""
    return _run(queries.get_team_results, team, limit, competition)


@mcp.tool
def fixtures(team: str, competition: str | None = None, limit: int = 5) -> list[dict]:
    """Get a team's upcoming matches, soonest first. Optionally filter by
    competition ('la liga', 'champions league', ...). Dates are UTC."""
    return _run(queries.get_fixtures, team, competition, limit)


@mcp.tool
def standings(competition: str) -> list[dict]:
    """Get the current league table for a competition ('la liga', 'premier
    league', 'champions league', ...), computed from finished matches.
    Not available for the World Cup or Euros (groups, knockouts)."""
    return _run(queries.get_standings, competition)
@mcp.tool
def head_to_head(team_a: str, team_b: str, limit: int = 5) -> list[dict]:
    """Get finished matches between two teams, newest first. Only covers the
    current season, so it may be empty or hold one or two games."""
    return _run(queries.get_head_to_head, team_a, team_b, limit)


@mcp.tool
def results_vs_top_teams(team: str, competition: str, top_n: int = 6) -> dict:
    """A team's record (W/D/L and every match) against the teams currently in
    the top N of a league table, in one competition, this season. 'Top N'
    uses the current table, not the table at the time of each match."""
    return _run(queries.get_results_vs_top_teams, team, competition, top_n)


@mcp.tool
def team_stats(team: str, competition: str | None = None) -> dict:
    """A team's season totals: played, W/D/L, goals for and against, clean
    sheets, goals per game, with home and away splits. Optionally limited to
    one competition."""
    return _run(queries.get_team_stats, team, competition)


@mcp.tool
def upcoming_matches(competition: str, days: int = 7, limit: int = 20) -> list[dict]:
    """Matches scheduled in a competition over the next N days, soonest first.
    Dates are UTC."""
    return _run(queries.get_upcoming_matches, competition, days, limit)





if __name__ == "__main__":
    mcp.run()