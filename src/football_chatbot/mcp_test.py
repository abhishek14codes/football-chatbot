import asyncio

from fastmcp import Client
from fastmcp.exceptions import ToolError

from football_chatbot.mcp_server import mcp


async def main():
    async with Client(mcp) as client:
        tools=  await client.list_tools()
        for t in tools:
            print(t.name,"-",t.description)
        result = await client.call_tool("team_results",{"team":"Real Betis","limit":2}) 
        print(result.data)

        try:
            await client.call_tool("team_results",{"team":"xyz","limit":2})
        except ToolError as e:
            print("Error",e)

asyncio.run(main())