from typing import Any

from utils import Logger
from roots.mcp_client import MCPClient
from roots.core.tools import ToolManager


class Chat:
    def __init__(self, llm_service: Any, clients: dict[str, MCPClient]):
        self.llm_service = llm_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[dict[str, Any]] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})
        Logger.info("[CHAT] Added user query to conversation history")

    async def run(
        self,
        query: str,
        stream: bool = False,
        on_event=None,
    ) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            Logger.info("[CHAT] Collecting tools for the next model turn")
            tools = await ToolManager.get_all_tools(self.clients)

            if stream and on_event:
                response = await self.llm_service.chat_stream(
                    messages=self.messages,
                    tools=tools,
                    on_event=on_event,
                )
            else:
                response = await self.llm_service.chat(
                    messages=self.messages,
                    tools=tools,
                )

            self.llm_service.add_assistant_message(self.messages, response)

            if response.stop_reason == "tool_use":
                Logger.info("[CHAT] Model requested tool execution")
                if not stream:
                    print(self.llm_service.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )

                self.llm_service.add_user_message(
                    self.messages, tool_result_parts
                )
                Logger.info(
                    "[CHAT] Tool results added back into conversation history"
                )
            else:
                final_text_response = self.llm_service.text_from_message(
                    response
                )
                Logger.info("[CHAT] Final assistant response is ready")
                break

        return final_text_response
