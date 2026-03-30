import asyncio

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from utils import Logger

load_dotenv()

mcp = FastMCP(name="Demo Server", log_level="ERROR")


@mcp.tool()
async def add(a: int, b: int, ctx: Context) -> int:
    Logger.info(f"[SERVER] Received add tool request with a={a}, b={b}")
    await ctx.info("Preparing to add...")
    await ctx.report_progress(20, 100)

    await asyncio.sleep(2)

    await ctx.info("OK, adding...")
    await ctx.report_progress(80, 100)

    return a + b


if __name__ == "__main__":
    Logger.info("[SERVER] Starting notifications MCP server")
    mcp.run(transport="stdio")
