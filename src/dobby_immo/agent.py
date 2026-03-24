"""Dobby LLM agent powered by OpenAI Responses API."""

import logging

from openai import AsyncOpenAI

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
- Dobby haelt sich kurz und praegnant, ausser es geht um Socken.\
"""


class DobbyAgent:
    """Stateful LLM agent that uses OpenAI Responses API with per-chat history."""

    def __init__(self, api_key: str) -> None:
        """Initialise the agent with an OpenAI API key."""
        self._client = AsyncOpenAI(api_key=api_key)
        self._last_response_ids: dict[int, str] = {}

    async def reply(self, chat_id: int, user_message: str) -> str:
        """Send a user message to the LLM and return the assistant reply."""
        previous_id = self._last_response_ids.get(chat_id)

        response = await self._client.responses.create(
            model="gpt-5-mini",
            instructions=DOBBY_SYSTEM_PROMPT,
            input=user_message,
            previous_response_id=previous_id,
            store=True,
        )

        self._last_response_ids[chat_id] = response.id
        text: str = response.output_text
        logger.info("LLM response for chat %d (response_id=%s)", chat_id, response.id)
        return text
