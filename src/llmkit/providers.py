"""Provider 接口与 Anthropic 实现。

`Provider` 是唯一的接缝：换一家模型只加一个文件，`client.py` 一行不改。
目前只落地 Anthropic 官方 SDK 一家——别的家真的要用时再加，不预先抽象。
"""

from __future__ import annotations

import time
from typing import Any, Protocol, Sequence

from .types import Message, Response, Usage

#: 当前默认模型。
DEFAULT_MODEL = "claude-opus-5"

#: 只在这里出现一次的推理深度取值。
Effort = str  # low | medium | high | xhigh | max


class Provider(Protocol):
    name: str

    def complete(self, *, model: str, system: str, messages: Sequence[Message],
                 max_tokens: int, effort: Effort | None, schema: dict | None,
                 extra: dict) -> Response:
        ...

    def embed(self, texts: Sequence[str], model: str) -> list[list[float]]:
        ...


class AnthropicProvider:
    """官方 `anthropic` SDK。

    Claude Opus 5 起 `temperature` / `top_p` / `top_k` 与 `budget_tokens` 都已移除，
    推理深度改由 `output_config.effort` 控制，结构化输出由 `output_config.format` 保证。
    """

    name = "anthropic"

    def __init__(self, api_key: str | None = None, **client_kwargs: Any) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key, **client_kwargs) \
            if api_key else anthropic.Anthropic(**client_kwargs)

    @staticmethod
    def build_request(*, model: str, system: str, messages: Sequence[Message],
                      max_tokens: int, effort: Effort | None, schema: dict | None,
                      extra: dict) -> dict:
        """组装请求体。单独拎出来，便于不联网检查请求形状。"""
        output_config: dict[str, Any] = {}
        if effort:
            output_config["effort"] = effort
        if schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": schema}

        body: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if system:
            body["system"] = system
        if output_config:
            body["output_config"] = output_config
        body.update(extra)
        return body

    def complete(self, *, model: str, system: str, messages: Sequence[Message],
                 max_tokens: int, effort: Effort | None, schema: dict | None,
                 extra: dict) -> Response:
        body = self.build_request(model=model, system=system, messages=messages,
                                  max_tokens=max_tokens, effort=effort,
                                  schema=schema, extra=extra)
        started = time.monotonic()
        message = self._client.messages.create(**body)
        latency = time.monotonic() - started

        text = "".join(b.text for b in message.content if b.type == "text")
        usage = Usage(getattr(message.usage, "input_tokens", 0),
                      getattr(message.usage, "output_tokens", 0),
                      getattr(message.usage, "cache_read_input_tokens", 0) or 0)
        # stop_reason 只如实带回来；拒答与截断的处理是 client 的策略，
        # 放在那里所有 provider 都能享受到同一套判定。
        return Response(text, message.model, usage, message.stop_reason or "end_turn", latency)

    def embed(self, texts: Sequence[str], model: str) -> list[list[float]]:
        raise NotImplementedError(
            "Anthropic 没有 embedding 接口。给 Deduper 传一个 embed 函数，"
            "或者加一个实现了 embed 的 provider。")
