import asyncio

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import LoggingMessageNotificationParams
from utils import Logger

load_dotenv()

server_params = StdioServerParameters(
    command="uv",
    args=["run", "--project", "notifications", "-m", "notifications.server"],
)


async def logging_callback(params: LoggingMessageNotificationParams):
    Logger.info(f"[CLIENT] Server log notification: {params.data}")


async def print_progress_callback(
    progress: float, total: float | None, message: str | None
):
    if total is not None:
        percentage = (progress / total) * 100
        Logger.info(
            f"[CLIENT] Progress notification: {progress}/{total} ({percentage:.1f}%)"
        )
    else:
        Logger.info(f"[CLIENT] Progress notification: {progress}")


async def run():
    Logger.info("[CLIENT] Starting notifications client")
    Logger.info("[CLIENT] Connecting to MCP server over stdio")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, logging_callback=logging_callback
        ) as session:
            await session.initialize()
            Logger.info("[CLIENT] MCP session initialized")

            Logger.info("[CLIENT] Calling add tool on MCP server with a=1, b=3")
            result = await session.call_tool(
                name="add",
                arguments={"a": 1, "b": 3},
                progress_callback=print_progress_callback,
            )
            Logger.info(f"[CLIENT] Final tool result: {result.content}")


if __name__ == "__main__":
    asyncio.run(run())
