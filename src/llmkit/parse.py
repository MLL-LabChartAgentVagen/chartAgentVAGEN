"""从模型回复里取出 JSON，并按 schema 做最小校验。

只做两件事：把 JSON 从散文或围栏里挖出来，以及检查必填字段和类型。
不引第三方校验库——schema 是我们自己写的，需要的判定就这么几条。
"""

from __future__ import annotations

import json
import re
from typing import Any

FENCE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.S)


class ParseError(ValueError):
    """回复里没有合法 JSON，或者不满足 schema。"""


def extract_json(text: str) -> Any:
    """依次尝试：整段、围栏里的一段、第一个平衡的花括号块。"""
    for candidate in _candidates(text):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ParseError(f"回复里没有合法 JSON: {text[:400]}")


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
    """必填字段、类型、枚举三项。不满足就抛 ParseError，消息进回喂文本。"""
    expected = schema.get("type")
    if expected and not isinstance(value, _TYPES[expected]):
        raise ParseError(f"应当是 {expected}，实际是 {type(value).__name__}")
    if expected == "object":
        for key in schema.get("required", ()):
            if key not in value:
                raise ParseError(f"缺少必填字段 {key!r}")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                validate(value[key], sub)
    elif expected == "array" and "items" in schema:
        for item in value:
            validate(item, schema["items"])
    if "enum" in schema and value not in schema["enum"]:
        raise ParseError(f"{value!r} 不在 {schema['enum']} 里")
