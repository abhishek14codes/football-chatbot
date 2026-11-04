from langchain_core.tools import tool

from football_chatbot.models import llm, llm1, llm2


@tool
def team_results(team: str, limit: int = 5) -> str:
    """Get a team's most recent finished matches."""
    return "dummy"


CANDIDATES = {"openrouter-nex": llm, "gemini": llm1, "openrouter-dots": llm2}

for name, model in CANDIDATES.items():
    print(f"\n== {name} ==")
    try:
        print("basic:", model.invoke("Say hi in 3 words").content)
        reply = model.bind_tools([team_results]).invoke(
            "How did Barcelona do in their last 3 matches?"
        )
        print("tool calls:", reply.tool_calls)
    except Exception as e:
        print("FAILED:", type(e).__name__, str(e)[:200])