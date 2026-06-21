from __future__ import annotations

import argparse
import asyncio


DEFAULT_EXPECTED_TOOLS = ["get_categories", "get_recipes", "get_shopping_lists"]

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def list_tools(url: str) -> list[str]:
    async with streamablehttp_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            return sorted(tool.name for tool in result.tools)


def main() -> None:
    parser = argparse.ArgumentParser(description="List tools from a streamable HTTP MCP server.")
    parser.add_argument("url", help="MCP endpoint URL, for example http://localhost:8000/mcp")
    parser.add_argument(
        "--expect",
        action="append",
        default=DEFAULT_EXPECTED_TOOLS,
        help="Expected tool name. Can be supplied multiple times. Defaults to core Mealie tools.",
    )
    args = parser.parse_args()

    tool_names = asyncio.run(list_tools(args.url))
    missing_tools = sorted(set(args.expect) - set(tool_names))
    if missing_tools:
        raise SystemExit(f"Missing expected tools: {', '.join(missing_tools)}")

    for tool_name in tool_names:
        print(tool_name)


if __name__ == "__main__":
    main()
