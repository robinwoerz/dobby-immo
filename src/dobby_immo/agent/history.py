"""In-memory rolling-window chat history for the Responses API."""

from __future__ import annotations

from collections import defaultdict, deque

_DEFAULT_MAX_MESSAGES = 30


class ChatHistory:
    """Rolling window of conversation messages per chat.

    Each message is a ``{"role": ..., "content": ...}`` dict compatible
    with the OpenAI Responses API ``input`` parameter.
    """

    def __init__(self, max_messages: int = _DEFAULT_MAX_MESSAGES) -> None:
        """Initialise with a maximum number of messages to retain per chat."""
        self._max = max_messages
        self._chats: defaultdict[int, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=self._max)
        )

    def append(self, chat_id: int, role: str, content: str) -> None:
        """Add a message to the history for *chat_id*."""
        self._chats[chat_id].append({"role": role, "content": content})

    def get(self, chat_id: int) -> list[dict[str, str]]:
        """Return the current message window for *chat_id*."""
        return list(self._chats[chat_id])
