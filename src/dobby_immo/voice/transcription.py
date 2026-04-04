"""OpenAI Audio API transcription adapter."""

from __future__ import annotations

import io
import logging

from openai import AsyncOpenAI, BadRequestError

from dobby_immo.voice.audio_convert import ogg_opus_to_wav

logger = logging.getLogger(__name__)


def _is_unsupported_audio_format(exc: BadRequestError) -> bool:
    """Return True if the error likely indicates an unsupported or invalid audio file."""
    hints = ("format", "unsupported", "invalid file", "decode", "could not")
    text = str(exc).lower()
    if any(s in text for s in hints):
        return True
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error", {})
        em = str(err.get("message", "")).lower()
        return any(s in em for s in hints)
    return False


class OpenAITranscriptionService:
    """Transcribe voice audio via OpenAI ``/v1/audio/transcriptions``."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        prompt: str | None = None,
    ) -> None:
        """Initialise the repository with API credentials and model name.

        Args:
            api_key: OpenAI API key.
            model: Transcription model id (e.g. ``gpt-4o-mini-transcribe``).
            prompt: Optional prompt to bias vocabulary (e.g. domain terms).
        """
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._prompt = prompt

    async def transcribe(self, audio: bytes, filename: str) -> str:
        """Transcribe ``audio`` to plain text.

        Tries the upload as-is first. On a format-related ``400``, decodes Telegram-style
        OGG Opus with ffmpeg to WAV and retries once.

        Args:
            audio: Raw audio file bytes.
            filename: Suggested filename for multipart upload (affects type sniffing).

        Returns:
            Trimmed transcript text (may be empty).

        Raises:
            BadRequestError: If the API rejects the request for reasons other than format.
            AudioConversionError: If ffmpeg conversion was required but failed.
        """
        try:
            text = await self._transcribe_bytes(audio, filename)
        except BadRequestError as exc:
            if not _is_unsupported_audio_format(exc):
                raise
            logger.info("Transcription rejected format for %s; retrying after ffmpeg", filename)
            wav = await ogg_opus_to_wav(audio)
            text = await self._transcribe_bytes(wav, "voice.wav")
        return text.strip()

    async def _transcribe_bytes(self, audio: bytes, filename: str) -> str:
        file_arg = (filename, io.BytesIO(audio))
        if self._prompt:
            result = await self._client.audio.transcriptions.create(
                file=file_arg, model=self._model, prompt=self._prompt
            )
        else:
            result = await self._client.audio.transcriptions.create(
                file=file_arg, model=self._model
            )
        if isinstance(result, str):
            return result
        text = getattr(result, "text", "") or ""
        return str(text)
