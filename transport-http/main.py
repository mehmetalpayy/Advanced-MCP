import asyncio
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import Response
from utils import Logger

load_dotenv()

mcp = FastMCP(
    "mcp-server",
    stateless_http=True,
    json_response=True,
    log_level="ERROR",
)

INDEX_HTML_PATH = Path(__file__).with_name("index.html")


@mcp.tool()
async def add(a: int, b: int, ctx: Context) -> int:
    Logger.info(f"[SERVER] Received add tool request with a={a}, b={b}")
    Logger.info("[SERVER] Sending log notification: Preparing to add...")
    await ctx.info("Preparing to add...")

    Logger.info("[SERVER] Waiting before reporting progress")
    await asyncio.sleep(2)

    Logger.info("[SERVER] Reporting progress: 80/100")
    await ctx.report_progress(80, 100)

    result = a + b
    Logger.info(f"[SERVER] Returning add result: {result}")
    return result


# Load the demo HTML page
@mcp.custom_route("/", methods=["GET"])
async def get(request: Request) -> Response:
    Logger.info("[SERVER] Received HTTP GET request for demo page")
    html_content = INDEX_HTML_PATH.read_text(encoding="utf-8")
    return Response(content=html_content, media_type="text/html")


if __name__ == "__main__":
    Logger.info("[SERVER] Starting streamable HTTP MCP server")
    mcp.run(transport="streamable-http")
