"""`LLM`：一个模型 + 一份默认参数 + 磁盘缓存 + 内容级重试。

三个方法：
    complete  一问一答，返回文本
    json      要求结构化输出，解析失败就把错误回喂给模型重来
    map       并发跑一批，用来横向比较不同模型 / 不同提示词
"""

from __future__ import annotations

import json as jsonlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Iterable, Sequence

from .cache import ResponseCache
from .parse import ParseError, extract_json, validate
from .providers import DEFAULT_MODEL, AnthropicProvider, Effort, Provider
from .types import LLMError, Message, Refusal, Response, Truncated, Usage

#: 解析失败时回喂给模型的模板。带上原文与具体错误，只说"格式不对"没有帮助。
RETRY_TEMPLATE = (
    "你上一次的回复无法解析：{error}\n\n"
    "原文如下：\n{text}\n\n"
    "请只输出满足 schema 的 JSON，不要加解释或围栏。"
)


def _check(response: Response, max_tokens: int) -> None:
    """拒答的文本可能为空或只有一半，截断的文本一定不完整——两者都不算正常回复。"""
    if response.stop_reason == "refusal":
        raise Refusal("安全分类器拒答，文本不完整，不要按正常回复处理")
    if response.stop_reason == "max_tokens":
        raise Truncated(f"回复被 max_tokens={max_tokens} 截断")


class LLM:
    def __init__(self, model: str = DEFAULT_MODEL, *, provider: Provider | None = None,
                 max_tokens: int = 8000, effort: Effort | None = "high",
                 cache_dir: str | Path | None = None,
                 max_content_retries: int = 3, extra: dict | None = None) -> None:
        self.model = model
        self.provider = provider or AnthropicProvider()
        self.max_tokens = max_tokens
        self.effort = effort
        self.max_content_retries = max_content_retries
        self.extra = dict(extra or {})
        self.cache = ResponseCache(cache_dir) if cache_dir else None
        self.usage = Usage()

    # ---------------------------------------------------------------- 一次调用

    def complete(self, system: str, user: str, *, messages: Sequence[Message] | None = None,
                 schema: dict | None = None) -> Response:
        msgs = list(messages) if messages is not None else [Message("user", user)]
        key = self._cache_key(system, msgs, schema)
        if self.cache is not None:
            hit = self.cache.get(key)
            if hit is not None:
                return hit

        response = self.provider.complete(
            model=self.model, system=system, messages=msgs,
            max_tokens=self.max_tokens, effort=self.effort,
            schema=schema, extra=self.extra)
        self.usage = self.usage + response.usage
        _check(response, self.max_tokens)          # 拒答与截断不进缓存
        if self.cache is not None:
            self.cache.put(key, response)
        return response

    # ---------------------------------------------------------------- 结构化输出

    def json(self, system: str, user: str, *, schema: dict) -> dict:
        """要 JSON。解析或校验失败就带着具体错误重来，上限 `max_content_retries`。"""
        messages = [Message("user", user)]
        last_error: Exception | None = None
        last_text = ""
        for _ in range(max(1, self.max_content_retries)):
            response = self.complete(system, user, messages=messages, schema=schema)
            last_text = response.text
            try:
                value = extract_json(response.text)
                validate(value, schema)
                return value
            except ParseError as exc:
                last_error = exc
                messages = [
                    Message("user", user),
                    Message("user", RETRY_TEMPLATE.format(error=exc, text=response.text[:2000])),
                ]
        raise ParseError(f"{self.max_content_retries} 次都没拿到合法 JSON："
                         f"{last_error}；最后一次回复：{last_text[:400]}")

    # ---------------------------------------------------------------- 批量

    def map(self, prompts: Iterable[tuple[str, str]], *, workers: int = 4,
            on_error: Callable[[Exception], None] | None = None) -> list[Response | None]:
        """并发跑一批 `(system, user)`，保持输入顺序。失败的那条返回 None。"""
        items = list(prompts)

        def run(pair: tuple[str, str]) -> Response | None:
            try:
                return self.complete(*pair)
            except Exception as exc:  # noqa: BLE001 — 批量里失败隔离
                if on_error:
                    on_error(exc)
                return None

        if workers <= 1:
            return [run(p) for p in items]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(run, items))

    # ---------------------------------------------------------------- 内部

    def _cache_key(self, system: str, messages: Sequence[Message], schema: dict | None) -> str:
        return jsonlib.dumps({
            "provider": self.provider.name,
            "model": self.model,
            "system": system,
            "messages": [[m.role, m.content] for m in messages],
            "max_tokens": self.max_tokens,
            "effort": self.effort,
            "schema": schema,
            "extra": self.extra,
        }, ensure_ascii=False, sort_keys=True)


__all__ = ["LLM", "LLMError"]
