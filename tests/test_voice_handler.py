"""Tests for the voice message handler."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import OpenAIError

from dobby_immo.protocols import AgentReply
from dobby_immo.voice import handle_voice


@pytest.fixture
def _tg_file():
    tg = MagicMock()
    tg.file_path = "voice/file_1.oga"
    tg.download_as_bytearray = AsyncMock(return_value=bytearray(b"fake-ogg"))
    return tg


@pytest.fixture
def _voice_update(update, context, _tg_file):
    """Prepare update and context for a standard voice message."""
    update.message.voice = MagicMock()
    update.message.voice.file_id = "fid"
    update.message.voice.file_size = 1024
    update.message.chat_id = 7
    context.bot.get_file = AsyncMock(return_value=_tg_file)
    return update


@pytest.mark.asyncio
async def test_transcribes_and_replies_text(_voice_update, context, agent, transcription):
    """Agent returns text-only reply (no voice)."""
    await handle_voice(_voice_update, context)

    transcription.transcribe.assert_called_once()
    args, _ = transcription.transcribe.call_args
    assert args[0] == b"fake-ogg"
    assert args[1] == "file_1.oga"
    agent.reply.assert_called_once_with(7, "Was kostet die Wohnung?")
    _voice_update.message.reply_text.assert_called_once_with("Dobby hilft!")
    _voice_update.message.reply_voice.assert_not_called()


@pytest.mark.asyncio
async def test_transcribes_and_replies_voice(_voice_update, context, agent, transcription, speech):
    """Agent requests voice reply via speak_reply tool."""
    agent.reply.return_value = AgentReply(text="Dobby spricht!", use_voice=True)

    await handle_voice(_voice_update, context)

    transcription.transcribe.assert_called_once()
    agent.reply.assert_called_once_with(7, "Was kostet die Wohnung?")
    speech.synthesize.assert_called_once_with("Dobby spricht!")
    _voice_update.message.reply_voice.assert_called_once_with(voice=b"fake-opus")
    _voice_update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_skips_when_no_voice(update, context):
    update.message.voice = None

    await handle_voice(update, context)

    context.bot.get_file.assert_not_called()


@pytest.mark.asyncio
async def test_rejects_oversized_file(update, context):
    update.message.voice = MagicMock()
    update.message.voice.file_id = "fid"
    update.message.voice.file_size = 30 * 1024 * 1024

    await handle_voice(update, context)

    update.message.reply_text.assert_called_once()
    context.bot.get_file.assert_not_called()


@pytest.mark.asyncio
async def test_empty_transcript(update, context, agent, transcription, _tg_file):
    update.message.voice = MagicMock()
    update.message.voice.file_id = "fid"
    update.message.voice.file_size = 10
    update.message.chat_id = 1
    transcription.transcribe.return_value = "   "
    context.bot.get_file = AsyncMock(return_value=_tg_file)

    await handle_voice(update, context)

    agent.reply.assert_not_called()
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_tts_fallback_to_text(_voice_update, context, agent, speech):
    """When TTS fails, the handler falls back to sending the reply as text."""
    agent.reply.return_value = AgentReply(text="Dobby hilft trotzdem!", use_voice=True)
    speech.synthesize.side_effect = OpenAIError("TTS down")

    await handle_voice(_voice_update, context)

    speech.synthesize.assert_called_once_with("Dobby hilft trotzdem!")
    _voice_update.message.reply_voice.assert_not_called()
    _voice_update.message.reply_text.assert_called_once_with("Dobby hilft trotzdem!")
