"""Telegram voice message handler."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from openai import OpenAIError

from dobby_immo.voice.audio_convert import AudioConversionError

if TYPE_CHECKING:
    from telegram import Update, Voice
    from telegram.ext import ContextTypes

    from dobby_immo.agent import DobbyAgent
    from dobby_immo.voice.transcription import OpenAITranscriptionRepository

logger = logging.getLogger(__name__)

_MAX_OPENAI_AUDIO_BYTES = 25 * 1024 * 1024

_MSG_TOO_LARGE = (
    "Dobby liebt lange Geschichten — aber dieses Sprachmemo ist zu gross! "
    "Bitte etwas Kuerzeres schicken."
)
_MSG_DOWNLOAD_FAILED = (
    "Dobby konnte die Stimme nicht vom Telegram-Floo holen! Bitte noch einmal versuchen."
)


@dataclass(frozen=True)
class _PreparedVoice:
    """Downloaded voice payload ready for transcription."""

    audio: bytes
    filename: str


async def _prepare_voice_audio(
    context: ContextTypes.DEFAULT_TYPE,
    voice: Voice,
    chat_id: int,
) -> _PreparedVoice | str:
    """Download voice bytes or return a user-facing error message."""
    if voice.file_size is not None and voice.file_size > _MAX_OPENAI_AUDIO_BYTES:
        return _MSG_TOO_LARGE

    try:
        tg_file = await context.bot.get_file(voice.file_id)
        audio = await tg_file.download_as_bytearray()
    except Exception:
        logger.exception("Voice file download failed for chat %s", chat_id)
        return _MSG_DOWNLOAD_FAILED

    if len(audio) > _MAX_OPENAI_AUDIO_BYTES:
        return _MSG_TOO_LARGE

    path = tg_file.file_path or "voice.oga"
    filename = path.rsplit("/", maxsplit=1)[-1]
    if "." not in filename:
        filename = f"{filename}.oga"
    return _PreparedVoice(audio=bytes(audio), filename=filename)


async def handle_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Download a voice memo, transcribe it, and pass the text to the LLM agent."""
    if update.message is None or update.message.voice is None:
        return

    voice = update.message.voice
    chat_id = update.message.chat_id
    agent: DobbyAgent = context.bot_data["agent"]
    transcription: OpenAITranscriptionRepository = context.bot_data["transcription"]

    prepared = await _prepare_voice_audio(context, voice, chat_id)
    if isinstance(prepared, str):
        await update.message.reply_text(prepared)
        return

    try:
        transcript = await transcription.transcribe(prepared.audio, prepared.filename)
    except AudioConversionError:
        logger.exception("Voice conversion failed for chat %s", chat_id)
        await update.message.reply_text(
            "Dobby braucht ffmpeg auf dem Server, um Sprachmemos zu verstehen — "
            "und die Magie ist gerade fehlgeschlagen!"
        )
        return
    except OpenAIError:
        logger.exception("OpenAI transcription failed for chat %s", chat_id)
        await update.message.reply_text(
            "Dobby hat gehoert, aber die Elfen-Schreibmaschine war kaputt! "
            "Bitte spaeter noch einmal probieren."
        )
        return

    text = transcript.strip()
    if not text:
        await update.message.reply_text(
            "Dobby hat nur Stille gehoert — bitte etwas lauter oder ein Textmemo?"
        )
        return

    logger.info("Voice transcript for chat %s: %s", chat_id, text[:500])
    reply = await agent.reply(chat_id, text)
    await update.message.reply_text(reply)
