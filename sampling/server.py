from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from dotenv import load_dotenv

from utils import Logger

load_dotenv()

mcp = FastMCP(name="Demo Server", log_level="ERROR")


@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):
    Logger.info("[SERVER] Received summarize tool request from client")

    prompt = f"""
        Please summarize the following text:
        {text_to_summarize}
    """
    Logger.info(f"[SERVER] User prompt sent for sampling:\n{prompt.strip()}")
    Logger.info("[SERVER] Forwarding summarize request through MCP sampling")
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user", content=TextContent(type="text", text=prompt)
            )
        ],
        max_tokens=4000,
        system_prompt="You are a helpful research assistant.",
    )

    if result.content.type == "text":
        Logger.info("[SERVER] Sampling response received successfully")
        Logger.info("[SERVER] Returning summarized text back to client")
        return result.content.text
    else:
        Logger.error("[SERVER] Sampling response did not contain text")
        raise ValueError("Sampling failed")


if __name__ == "__main__":
    Logger.info("[SERVER] Starting sampling MCP server")
    mcp.run(transport="stdio")
