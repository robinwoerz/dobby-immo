"""OpenAI Text-to-Speech adapter."""

from __future__ import annotations

from openai import AsyncOpenAI

DOBBY_TTS_INSTRUCTIONS = (
    "Speak as Dobby the free house-elf: high-pitched, enthusiastic, slightly squeaky "
    "voice with dramatic intonation. Speak in German. Excited and loyal tone, fast "
    "pace, occasional dramatic pauses for emphasis."
)


class OpenAISpeechService:
    """Synthesize speech via OpenAI ``/v1/audio/speech``."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gpt-4o-mini-tts",
        voice: str = "fable",
        speed: float = 1.2,
    ) -> None:
        """Initialise the repository.

        Args:
            api_key: OpenAI API key.
            model: TTS model id.
            voice: Built-in voice name (e.g. ``fable``).
            speed: Playback speed multiplier (0.25 -- 4.0).
        """
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._voice = voice
        self._speed = speed

    async def synthesize(self, text: str) -> bytes:
        """Convert *text* to Opus audio bytes.

        Args:
            text: The text to speak.

        Returns:
            Raw Opus audio data (OGG container).
        """
        response = await self._client.audio.speech.create(
            input=text,
            model=self._model,
            voice=self._voice,
            instructions=DOBBY_TTS_INSTRUCTIONS,
            response_format="opus",
            speed=self._speed,
        )
        return response.content
