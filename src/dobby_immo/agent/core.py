"""Dobby LLM agent powered by OpenAI Responses API."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from openai import AsyncOpenAI

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

from dobby_immo.agent.history import ChatHistory
from dobby_immo.agent.profile import ProfileStore
from dobby_immo.agent.prompts import DOBBY_SYSTEM_PROMPT
from dobby_immo.agent.tools import get_tool_schemas
from dobby_immo.protocols import AgentReply

logger = logging.getLogger(__name__)

_MAX_TOOL_ROUNDS = 10


class DobbyAgent:
    """Stateful LLM agent that uses OpenAI Responses API with per-chat history."""

    def __init__(
        self, *, api_key: str, model: str, profile_path: Path, max_history: int = 30
    ) -> None:
        """Initialise the agent with an OpenAI API key, model, and profile path."""
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._history = ChatHistory(max_messages=max_history)
        self._profile = ProfileStore(profile_path)
        self._tool_handlers: dict[str, Callable[..., str]] = {
            "read_apartment_profile": lambda **_kw: self._profile.read(),
            "update_apartment_profile": lambda *, content: self._profile.write(content),
        }

    async def reply(self, chat_id: int, user_message: str) -> AgentReply:
        """Send a user message to the LLM and return a structured reply."""
        self._history.append(chat_id, "user", user_message)

        response = await self._client.responses.create(
            model=self._model,
            instructions=DOBBY_SYSTEM_PROMPT,
            input=self._history.get(chat_id),  # type: ignore[arg-type]
            tools=get_tool_schemas(),  # type: ignore[arg-type]
        )
        logger.info("LLM response for chat %d (response_id=%s)", chat_id, response.id)

        use_voice = False
        voice_text: str | None = None

        for _round in range(_MAX_TOOL_ROUNDS):
            function_calls = [i for i in response.output if i.type == "function_call"]
            if not function_calls:
                break

            tool_outputs: list[dict[str, str]] = []
            for item in function_calls:
                args = json.loads(item.arguments)

                if item.name == "speak_reply":
                    voice_text = args["text"]
                    use_voice = True
                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": "Voice message delivered.",
                        }
                    )
                    continue

                handler = self._tool_handlers.get(item.name)
                if handler is None:
                    output = f"Unknown tool: {item.name}"
                    logger.warning(output)
                else:
                    output = handler(**args)

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": output,
                    }
                )

            response = await self._client.responses.create(
                model=self._model,
                instructions=DOBBY_SYSTEM_PROMPT,
                input=tool_outputs,  # type: ignore[arg-type]
                tools=get_tool_schemas(),  # type: ignore[arg-type]
                previous_response_id=response.id,
            )

        text = voice_text if (use_voice and voice_text is not None) else response.output_text
        self._history.append(chat_id, "assistant", text)

        if use_voice and voice_text is not None:
            return AgentReply(text=voice_text, use_voice=True)
        return AgentReply(text=response.output_text)
