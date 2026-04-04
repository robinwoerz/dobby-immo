"""Agent tool definitions with auto-generated OpenAI function schemas.

New tools are added by decorating a function with ``@agent_tool``.
The JSON schema is derived from the function signature, type hints,
and Google-style docstring -- no manual schema required.
"""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass, field
from typing import Any, get_type_hints

_PYTHON_TO_JSON: dict[type[Any], str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}

_ARG_LINE_RE = re.compile(r"^\s{4,}(\w+)\s*(?:\(.*?\))?\s*:\s*(.+)", re.MULTILINE)


@dataclass(frozen=True)
class ToolDef:
    """Registered tool: its OpenAI schema and the original function name."""

    name: str
    schema: dict[str, object]


@dataclass
class _ToolRegistry:
    _tools: dict[str, ToolDef] = field(default_factory=dict)

    def register(self, tool: ToolDef) -> None:
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict[str, object]]:
        """All registered tool schemas for ``responses.create(tools=...)``."""
        return [t.schema for t in self._tools.values()]

    def get(self, name: str) -> ToolDef | None:
        return self._tools.get(name)


_registry = _ToolRegistry()


def _parse_arg_descriptions(docstring: str) -> dict[str, str]:
    """Extract parameter descriptions from a Google-style Args section."""
    match = re.search(r"Args:\s*\n", docstring)
    if not match:
        return {}
    args_block = docstring[match.end() :]
    return dict(_ARG_LINE_RE.findall(args_block))


def _extract_description(docstring: str) -> str:
    """Return the docstring body before the Args/Returns/Raises sections."""
    cut = re.search(r"\n\s*(Args|Returns|Raises|Yields|Examples):", docstring)
    body = docstring[: cut.start()] if cut else docstring
    return " ".join(body.split())


def _build_schema(func: Any) -> dict[str, object]:  # noqa: ANN401
    """Build an OpenAI function-tool schema from a decorated function."""
    hints = get_type_hints(func)
    sig = inspect.signature(func)
    docstring = inspect.getdoc(func) or ""

    arg_docs = _parse_arg_descriptions(docstring)

    properties: dict[str, dict[str, str]] = {}
    required: list[str] = []
    for name, param in sig.parameters.items():
        json_type = _PYTHON_TO_JSON.get(hints.get(name, str), "string")
        prop: dict[str, str] = {"type": json_type}
        if name in arg_docs:
            prop["description"] = arg_docs[name]
        properties[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "name": func.__name__,
        "description": _extract_description(docstring),
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


def agent_tool(func: Any) -> Any:  # noqa: ANN401
    """Decorator that registers a function as an agent tool."""
    schema = _build_schema(func)
    _registry.register(ToolDef(name=func.__name__, schema=schema))
    return func


def get_tool_schemas() -> list[dict[str, object]]:
    """Return all registered tool schemas."""
    return _registry.schemas()


def get_tool(name: str) -> ToolDef | None:
    """Look up a registered tool by name."""
    return _registry.get(name)


# ---------------------------------------------------------------------------
# Tool definitions -- add new tools below
# ---------------------------------------------------------------------------


@agent_tool
def speak_reply(text: str) -> None:
    """Send the reply as a voice message instead of text.

    Use when the user explicitly asks for a voice response
    or when replying to a voice message.

    Args:
        text: The text to speak aloud.
    """


@agent_tool
def read_apartment_profile() -> None:
    """Read the current apartment search profile with all stored preferences."""


@agent_tool
def update_apartment_profile(content: str) -> None:
    """Update the apartment search profile. Expects the complete profile as markdown.

    Always read the current profile first, then send the full updated version.

    Args:
        content: The full updated profile in markdown format.
    """
