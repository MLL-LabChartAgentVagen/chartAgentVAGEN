"""Pulling JSON out of a reply and checking it against a schema.

Two jobs only: find the JSON whether it arrived bare, fenced or wrapped in prose,
and check required fields, types and enums. No validation library, because the
schemas are ours and these are the only checks they need.
"""

from __future__ import annotations

import json
import re
from typing import Any

FENCE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.S)


class ParseError(ValueError):
    """The reply held no valid JSON, or JSON that does not match the schema."""


def extract_json(text: str) -> Any:
    """Try the whole reply, then any fenced block, then the first balanced braces."""
    for candidate in _candidates(text):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ParseError(f"no valid JSON in the reply: {text[:400]}")


def _candidates(text: str):
    text = text.strip()
    yield text
    for m in FENCE.finditer(text):
        yield m.group(1)
    start = text.find("{")
    if start >= 0:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if in_str:
                esc = c == "\\" and not esc
                in_str = not (c == '"' and not esc)
                continue
            if c == '"':
                in_str, esc = True, False
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    yield text[start:i + 1]
                    return


_TYPES = {"object": dict, "array": list, "string": str, "number": (int, float),
          "integer": int, "boolean": bool, "null": type(None)}


def validate(value: Any, schema: dict) -> None:
    """Check required fields, types and enums. The message becomes feedback text."""
    expected = schema.get("type")
    if expected and not isinstance(value, _TYPES[expected]):
        raise ParseError(f"expected {expected}, got {type(value).__name__}")
    if expected == "object":
        for key in schema.get("required", ()):
            if key not in value:
                raise ParseError(f"missing required field {key!r}")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                validate(value[key], sub)
    elif expected == "array" and "items" in schema:
        for item in value:
            validate(item, schema["items"])
    if "enum" in schema and value not in schema["enum"]:
        raise ParseError(f"{value!r} is not one of {schema['enum']}")
