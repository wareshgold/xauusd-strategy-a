import asyncio
import os

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    headers = {
        "Authorization": f"Bearer {os.environ['MT5_MCP_API_KEY']}",
        "MCP-Protocol-Version": "2025-06-18",
    }

    targets = {
        "get_terminal_journal",
        "get_expert_journal",
        "get_trading_history_positions",
        "get_trading_history_orders",
    }

    async with httpx.AsyncClient(headers=headers, timeout=15.0) as http_client:
        async with streamable_http_client(
            "http://127.0.0.1:22346/mcp",
            http_client=http_client,
        ) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()

                print("MT5 MCP JOURNAL / HISTORY TOOL SCHEMAS")
                print("Read-only inspection; no tool is executed.\n")

                for tool in tools.tools:
                    if tool.name in targets:
                        print(f"=== {tool.name} ===")
                        print(tool.input_schema)
                        print()

                print("SCHEMA INSPECTION COMPLETE.")


if __name__ == "__main__":
    asyncio.run(main())
