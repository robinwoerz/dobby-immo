"""Service protocols (structural interfaces) for dependency injection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

SERVICES_KEY = "services"


@dataclass(frozen=True)
class AgentReply:
    """Structured response from the agent."""

    text: str
    use_voice: bool = False


class TranscriptionService(Protocol):
    """Transcribe audio to text."""

    async def transcribe(self, audio: bytes, filename: str) -> str:
        """Return plain-text transcript of *audio*."""
        ...


class SpeechService(Protocol):
    """Synthesize text to audio."""

    async def synthesize(self, text: str) -> bytes:
        """Return audio bytes for *text*."""
        ...


class Agent(Protocol):
    """Conversational agent with per-chat history."""

    async def reply(self, chat_id: int, user_message: str) -> AgentReply:
        """Return a reply for *user_message* in the given chat."""
        ...


@dataclass(frozen=True)
class Services:
    """Typed dependency container wired in ``bot.create_app``."""

    agent: Agent
    transcription: TranscriptionService
    speech: SpeechService
    allowed_user_ids: list[int]


def get_services(context_bot_data: dict[str, object]) -> Services:
    """Extract the typed ``Services`` container from ``context.bot_data``."""
    svc = context_bot_data[SERVICES_KEY]
    if not isinstance(svc, Services):  # pragma: no cover
        msg = f"Expected Services, got {type(svc)}"
        raise TypeError(msg)
    return svc
