import json
import os
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from openai import AsyncOpenAI

from utils import Logger


@dataclass
class OpenAITextBlock:
    text: str
    type: str = "text"


@dataclass
class OpenAIToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
    type: str = "tool_use"


@dataclass
class OpenAIMessage:
    content: list[OpenAITextBlock | OpenAIToolUseBlock]
    stop_reason: str


class OpenAI:
    def __init__(self, model: str):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def add_user_message(self, messages: list, message):
        user_message = {
            "role": "user",
            "content": message.content if hasattr(message, "content") else message,
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        assistant_message = {
            "role": "assistant",
            "content": message.content if hasattr(message, "content") else message,
        }
        messages.append(assistant_message)

    def text_from_message(self, message: OpenAIMessage) -> str:
        return "\n".join(
            block.text for block in message.content if block.type == "text"
        )

    def _build_tools(self, tools: list[dict[str, Any]] | None):
        if not tools:
            return None

        return [
            {
                "type": "function",
                "name": tool["name"],
                "description": tool.get("description"),
                "parameters": tool.get("input_schema"),
                "strict": False,
            }
            for tool in tools
        ]

    def _assistant_items_from_content(self, content: list[Any]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        text_parts: list[str] = []

        for block in content:
            block_type = getattr(block, "type", None)
            if block_type == "text":
                text_parts.append(getattr(block, "text", ""))
            elif block_type == "tool_use":
                items.append(
                    {
                        "type": "function_call",
                        "call_id": getattr(block, "id"),
                        "name": getattr(block, "name"),
                        "arguments": json.dumps(getattr(block, "input", {})),
                    }
                )

        if text_parts:
            items.insert(
                0,
                {
                    "role": "assistant",
                    "content": "\n".join(part for part in text_parts if part),
                },
            )

        return items

    def _user_items_from_content(self, content: Any) -> list[dict[str, Any]]:
        if isinstance(content, str):
            return [{"role": "user", "content": content}]

        if isinstance(content, list):
            function_outputs: list[dict[str, Any]] = []
            text_parts: list[str] = []

            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    function_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": block["tool_use_id"],
                            "output": block["content"],
                        }
                    )
                elif isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))

            items = []
            if text_parts:
                items.append(
                    {"role": "user", "content": "\n".join(text_parts)}
                )
            items.extend(function_outputs)
            return items

        return [{"role": "user", "content": str(content)}]

    def _build_input(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []

        for message in messages:
            role = message.get("role")
            content = message.get("content")

            if role == "user":
                items.extend(self._user_items_from_content(content))
            elif role == "assistant":
                if isinstance(content, str):
                    items.append({"role": "assistant", "content": content})
                elif isinstance(content, list):
                    items.extend(self._assistant_items_from_content(content))

        return items

    def _message_from_response(self, response) -> OpenAIMessage:
        content: list[OpenAITextBlock | OpenAIToolUseBlock] = []
        stop_reason = "end_turn"

        for item in response.output:
            if item.type == "message":
                for part in item.content:
                    if part.type == "output_text" and part.text:
                        content.append(OpenAITextBlock(text=part.text))
            elif item.type == "function_call":
                stop_reason = "tool_use"
                arguments = {}
                if item.arguments:
                    arguments = json.loads(item.arguments)
                content.append(
                    OpenAIToolUseBlock(
                        id=item.call_id,
                        name=item.name,
                        input=arguments,
                    )
                )

        return OpenAIMessage(content=content, stop_reason=stop_reason)

    async def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ) -> OpenAIMessage:
        Logger.info("[OPENAI] Sending request to OpenAI Responses API")

        params = {
            "model": self.model,
            "input": self._build_input(messages),
            "instructions": system,
            "max_output_tokens": 8000,
            "temperature": temperature,
        }
        built_tools = self._build_tools(tools)
        if built_tools:
            params["tools"] = built_tools

        response = await self.client.responses.create(**params)

        message = self._message_from_response(response)
        Logger.info(
            f"[OPENAI] Response received with stop_reason={message.stop_reason}"
        )
        return message

    async def chat_stream(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
        on_event=None,
    ) -> OpenAIMessage:
        Logger.info("[OPENAI] Starting streaming request to OpenAI Responses API")

        params = {
            "model": self.model,
            "input": self._build_input(messages),
            "instructions": system,
            "temperature": temperature,
            "max_output_tokens": 8000,
        }
        built_tools = self._build_tools(tools)
        if built_tools:
            params["tools"] = built_tools

        async with self.client.responses.stream(**params) as stream:
            async for event in stream:
                if on_event is None:
                    continue

                if event.type == "response.output_text.delta":
                    await on_event(
                        SimpleNamespace(
                            type="content_block_delta",
                            index=event.output_index,
                            delta=SimpleNamespace(
                                type="text_delta",
                                text=event.delta,
                            ),
                        )
                    )
                elif event.type == "response.output_item.added":
                    if event.item.type == "function_call":
                        await on_event(
                            SimpleNamespace(
                                type="content_block_start",
                                index=event.output_index,
                                content_block=SimpleNamespace(
                                    type="tool_use",
                                    name=event.item.name,
                                ),
                            )
                        )
                elif event.type == "response.function_call_arguments.delta":
                    await on_event(
                        SimpleNamespace(
                            type="content_block_delta",
                            index=event.output_index,
                            delta=SimpleNamespace(
                                type="input_json_delta",
                                partial_json=event.delta,
                            ),
                        )
                    )
                elif event.type == "response.output_item.done":
                    if event.item.type == "function_call":
                        await on_event(
                            SimpleNamespace(
                                type="content_block_stop",
                                index=event.output_index,
                            )
                        )

            final_response = await stream.get_final_response()

        message = self._message_from_response(final_response)
        Logger.info(
            f"[OPENAI] Streaming response completed with stop_reason={message.stop_reason}"
        )
        return message
