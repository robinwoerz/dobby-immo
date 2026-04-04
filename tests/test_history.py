"""Tests for the rolling-window chat history."""

from dobby_immo.history import ChatHistory


def test_append_and_get():
    h = ChatHistory(max_messages=10)
    h.append(1, "user", "hello")
    h.append(1, "assistant", "hi")
    assert h.get(1) == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]


def test_get_returns_empty_for_unknown_chat():
    h = ChatHistory()
    assert h.get(999) == []


def test_rolling_window_evicts_oldest():
    h = ChatHistory(max_messages=3)
    h.append(1, "user", "a")
    h.append(1, "assistant", "b")
    h.append(1, "user", "c")
    h.append(1, "assistant", "d")
    assert len(h.get(1)) == 3
    assert h.get(1)[0] == {"role": "assistant", "content": "b"}
    assert h.get(1)[-1] == {"role": "assistant", "content": "d"}


def test_separate_chats_are_isolated():
    h = ChatHistory()
    h.append(1, "user", "chat one")
    h.append(2, "user", "chat two")
    assert len(h.get(1)) == 1
    assert len(h.get(2)) == 1
    assert h.get(1)[0]["content"] == "chat one"
    assert h.get(2)[0]["content"] == "chat two"


def test_get_returns_copy():
    h = ChatHistory()
    h.append(1, "user", "hello")
    result = h.get(1)
    result.clear()
    assert len(h.get(1)) == 1
