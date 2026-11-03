import asyncio
import json

from fastmcp import Client

from football_chatbot.mcp_server import mcp


async def main():
    async with Client(mcp) as client:
        r = await client.call_tool(
            "team_results",
            {"team": "Barca", "competition": "champions league", "limit": 10},
        )
        print(json.dumps(r.data, indent=2, default=str))


asyncio.run(main())