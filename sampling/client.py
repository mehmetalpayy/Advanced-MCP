import asyncio
import os

from openai import AsyncOpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    TextContent,
    SamplingMessage,
)

from utils import Logger

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_client = AsyncOpenAI(api_key=openai_api_key)
model = "gpt-5.4"

server_params = StdioServerParameters(
    command="uv",
    args=["run", "--project", "sampling", "-m", "sampling.server"],
)


async def chat(
    input_messages: list[SamplingMessage],
    max_tokens=4000,
    system_prompt: str | None = None,
):
    if not openai_api_key:
        Logger.error("[CLIENT] OPENAI_API_KEY is not set")
        raise RuntimeError("OPENAI_API_KEY is not set")

    messages = []
    for msg in input_messages:
        if msg.role == "user" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "user", "content": content})
        elif msg.role == "assistant" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "assistant", "content": content})

    Logger.info(f"[CLIENT] Messages forwarded to OpenAI:\n{messages}")
    Logger.info("[CLIENT] Sending sampling request to OpenAI")
    response = await openai_client.responses.create(
        model=model,
        instructions=system_prompt,
        input=messages,
        max_output_tokens=max_tokens,
    )
    Logger.info("[CLIENT] Received response from OpenAI")
    Logger.info(f"[CLIENT] OpenAI raw text output:\n{response.output_text}")

    return response.output_text


async def sampling_callback(
    context: RequestContext, params: CreateMessageRequestParams
):
    Logger.info("[CLIENT] Sampling callback invoked by MCP server")
    Logger.info(
        f"[CLIENT] Sampling request system prompt:\n{params.systemPrompt}"
    )

    text = await chat(params.messages, system_prompt=params.systemPrompt)
    Logger.info("[CLIENT] Returning model output back to MCP server")

    return CreateMessageResult(
        role="assistant",
        model=model,
        content=TextContent(type="text", text=text),
    )


async def run():
    Logger.info("[CLIENT] Starting sampling client")
    Logger.info(f"[CLIENT] Configured OpenAI model: {model}")
    Logger.info("[CLIENT] Connecting to MCP server over stdio")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=sampling_callback
        ) as session:
            await session.initialize()
            Logger.info("[CLIENT] MCP session initialized")

            Logger.info("[CLIENT] Calling summarize tool on MCP server")
            result = await session.call_tool(
                name="summarize",
                arguments={"text_to_summarize": "lots of text"},
            )
            Logger.info(f"[CLIENT] Final tool result: {result.content}")


if __name__ == "__main__":
    asyncio.run(run())
