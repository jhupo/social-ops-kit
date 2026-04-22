from __future__ import annotations

from typing import Any

from mcp import types

from social_ops_kit.models import ToolParameter
from social_ops_kit.registry import build_default_registry


_TYPE_MAP = {
    "string": {"type": "string"},
    "integer": {"type": "integer"},
    "number": {"type": "number"},
    "boolean": {"type": "boolean"},
    "object": {"type": "object"},
    "array[string]": {"type": "array", "items": {"type": "string"}},
    "array[object]": {"type": "array", "items": {"type": "object"}},
}


def parameter_to_schema(parameter: ToolParameter) -> dict[str, Any]:
    schema = dict(_TYPE_MAP.get(parameter.type_name, {"type": "string"}))
    schema["description"] = parameter.description
    return schema


def build_input_schema(parameters: tuple[ToolParameter, ...]) -> dict[str, Any]:
    properties = {parameter.name: parameter_to_schema(parameter) for parameter in parameters}
    required = [parameter.name for parameter in parameters if parameter.required]
    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def build_tool_manifest() -> list[dict[str, object]]:
    return [tool.as_dict() for tool in build_default_registry()]


def build_mcp_tool_definitions() -> list[types.Tool]:
    return [
        types.Tool(
            name=tool.name,
            description=tool.summary,
            inputSchema=build_input_schema(tool.parameters),
        )
        for tool in build_default_registry()
    ]
