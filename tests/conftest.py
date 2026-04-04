"""Shared test fixtures."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from dobby_immo.protocols import SERVICES_KEY, AgentReply, Services


@pytest.fixture
def agent():
    mock = AsyncMock()
    mock.reply.return_value = AgentReply(text="Dobby hilft!")
    return mock


@pytest.fixture
def transcription():
    mock = AsyncMock()
    mock.transcribe.return_value = "Was kostet die Wohnung?"
    return mock


@pytest.fixture
def speech():
    mock = AsyncMock()
    mock.synthesize.return_value = b"fake-opus"
    return mock


@pytest.fixture
def services(agent, transcription, speech):
    return Services(
        agent=agent,
        transcription=transcription,
        speech=speech,
        allowed_user_ids=[111, 222],
    )


@pytest.fixture
def context(services):
    ctx = MagicMock()
    ctx.bot_data = {SERVICES_KEY: services}
    ctx.bot.get_file = AsyncMock()
    ctx.bot.send_message = AsyncMock()
    return ctx


@pytest.fixture
def update():
    upd = MagicMock()
    upd.message = MagicMock()
    upd.message.chat_id = 42
    upd.message.reply_text = AsyncMock()
    upd.message.reply_voice = AsyncMock()
    return upd
