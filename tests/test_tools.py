"""Tests for the agent tool registry and schema generation."""

from typing import Any

from dobby_immo.tools import get_tool, get_tool_schemas


def test_speak_reply_registered():
    schemas = get_tool_schemas()
    names = [s["name"] for s in schemas]
    assert "speak_reply" in names


def test_speak_reply_schema_structure():
    tool = get_tool("speak_reply")
    assert tool is not None
    schema = tool.schema
    assert schema["type"] == "function"
    assert schema["name"] == "speak_reply"
    assert isinstance(schema["description"], str)
    assert len(schema["description"]) > 10

    params: dict[str, Any] = schema["parameters"]  # type: ignore[assignment]
    assert params["type"] == "object"
    assert "text" in params["properties"]
    assert params["properties"]["text"]["type"] == "string"
    assert "text" in params["required"]
