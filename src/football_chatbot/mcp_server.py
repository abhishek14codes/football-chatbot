from fastmcp import FastMCP 
from fastmcp.exceptions import ToolError

from football_chatbot.queries import get_team_results 

mcp = FastMCP("football") 

@mcp.tool
def team_results(team: str, limit: int = 5) -> list[dict]:
    """Get a team's most recent finished matches (La Liga, Premier League,
    Champions League), newest first. Accepts nicknames like 'Barca' or 'psg'.
    Returns match dates, competition, teams and scores."""
    try:
        return get_team_results(team, limit)
    except ValueError as e:
        raise ToolError(str(e))


if __name__ == "__main__":
    mcp.run()