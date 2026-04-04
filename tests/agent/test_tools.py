"""Tests for the agent tool registry and schema generation."""

from typing import Any

import pytest

from dobby_immo.agent.tools import get_tool, get_tool_schemas


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


@pytest.mark.parametrize("tool_name", ["read_apartment_profile", "update_apartment_profile"])
def test_profile_tools_registered(tool_name: str) -> None:
    schemas = get_tool_schemas()
    names = [s["name"] for s in schemas]
    assert tool_name in names


def test_read_apartment_profile_schema():
    tool = get_tool("read_apartment_profile")
    assert tool is not None
    params: dict[str, Any] = tool.schema["parameters"]  # type: ignore[assignment]
    assert params["properties"] == {}
    assert params["required"] == []


def test_update_apartment_profile_schema():
    tool = get_tool("update_apartment_profile")
    assert tool is not None
    params: dict[str, Any] = tool.schema["parameters"]  # type: ignore[assignment]
    assert "content" in params["properties"]
    assert params["properties"]["content"]["type"] == "string"
    assert "content" in params["required"]
