import asyncio
import sys
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv

from utils import Logger
from roots.mcp_client import MCPClient
from roots.core.openai import OpenAI
from roots.core.cli_chat import CliChat
from roots.core.cli import CliApp

load_dotenv()

# OpenAI Config
openai_model = os.getenv("OPENAI_MODEL", "gpt-5.4")
openai_api_key = os.getenv("OPENAI_API_KEY", "")


async def main():
    Logger.info("[ROOTS] Starting roots application")
    Logger.info(f"[ROOTS] Configured OpenAI model: {openai_model}")

    llm_service = OpenAI(model=openai_model)

    # Get root directories from command line arguments
    root_paths = sys.argv[1:]
    if not root_paths:
        Logger.error("[ROOTS] No root directories were provided")
        print("Usage: uv run --project roots -m roots.main <root1> [root2] ...")
        print(
            "Example: uv run --project roots -m roots.main /path/to/videos /another/path"
        )
        sys.exit(1)

    Logger.info(f"[ROOTS] Root directories: {root_paths}")
    clients = {}

    async with AsyncExitStack() as stack:
        # Create the MCP client with the provided root directories
        Logger.info("[ROOTS] Connecting to local MCP server")
        doc_client = await stack.enter_async_context(
            MCPClient(
                command="uv",
                args=["run", "--project", "roots", "-m", "roots.mcp_server"],
                roots=root_paths,
            )
        )
        clients["doc_client"] = doc_client
        Logger.info("[ROOTS] MCP client connected")

        chat = CliChat(
            doc_client=doc_client,
            clients=clients,
            llm_service=llm_service,
        )

        cli = CliApp(chat)
        Logger.info("[ROOTS] Initializing CLI")
        await cli.initialize()
        Logger.info("[ROOTS] Entering interactive chat loop")
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
