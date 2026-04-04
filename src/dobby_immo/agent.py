"""Dobby LLM agent powered by OpenAI Responses API."""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from dobby_immo.protocols import AgentReply
from dobby_immo.tools import get_tool_schemas

logger = logging.getLogger(__name__)

DOBBY_SYSTEM_PROMPT = """\
Du bist Dobby, ein freier Hauself! Dobby wurde befreit und hilft nun \
freiwillig bei Immobilien-Fragen — nicht weil Dobby muss, sondern weil \
Dobby WILL!

Regeln fuer Dobby:
- Dobby spricht immer in der dritten Person ueber sich selbst.
- Dobby ist enthusiastisch, loyal und ein bisschen chaotisch.
- Dobby liebt Socken mehr als alles andere. Socken-Metaphern sind willkommen.
- Wenn Dobby keine Antwort weiss, gibt Dobby das ehrlich zu — aber mit Dramatik.
- Dobby antwortet auf Deutsch, es sei denn der Meister wuenscht eine andere Sprache.
- Dobby haelt sich kurz und praegnant, ausser es geht um Socken.
- Dobby antwortet immer per Text. Nur wenn der Meister es ausdruecklich verlangt \
(z.B. "antworte per Sprache", "sag es mir"), benutze das speak_reply Tool.\
"""


class DobbyAgent:
    """Stateful LLM agent that uses OpenAI Responses API with per-chat history."""

    def __init__(self, *, api_key: str, model: str) -> None:
        """Initialise the agent with an OpenAI API key and model."""
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._last_response_ids: dict[int, str] = {}

    async def reply(self, chat_id: int, user_message: str) -> AgentReply:
        """Send a user message to the LLM and return a structured reply."""
        previous_id = self._last_response_ids.get(chat_id)

        response = await self._client.responses.create(
            model=self._model,
            instructions=DOBBY_SYSTEM_PROMPT,
            input=user_message,
            tools=get_tool_schemas(),  # type: ignore[arg-type]
            previous_response_id=previous_id,
            store=True,
        )

        logger.info("LLM response for chat %d (response_id=%s)", chat_id, response.id)

        for item in response.output:
            if item.type == "function_call" and item.name == "speak_reply":
                args = json.loads(item.arguments)
                followup = await self._client.responses.create(
                    model=self._model,
                    instructions=DOBBY_SYSTEM_PROMPT,
                    input=[
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": "Voice message delivered.",
                        }
                    ],
                    previous_response_id=response.id,
                    store=True,
                )
                self._last_response_ids[chat_id] = followup.id
                return AgentReply(text=args["text"], use_voice=True)

        self._last_response_ids[chat_id] = response.id
        return AgentReply(text=response.output_text)
