import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient


async def test_ping_tool():

    client = MultiServerMCPClient({
        "ueba": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp"
        }
    })

    tools = await client.get_tools()
    ping_tool = next(t for t in tools if t.name == "ping")

    result = await ping_tool.ainvoke({})

    # extract actual response
    data = json.loads(result[0]["text"])

    print("Tool response:", data)

    assert data["status"] == "success"
    assert data["message"] == "pong"

    print("Ping tool test passed")


asyncio.run(test_ping_tool())