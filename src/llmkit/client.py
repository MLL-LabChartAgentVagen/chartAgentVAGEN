"""One model, one set of defaults, a disk cache, and retries on unusable content.

    complete  ask once, get text back
    json      ask for structured output; on a parse failure, feed the error back
    map       run a batch concurrently, keeping input order
"""

from __future__ import annotations

import json as jsonlib
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Iterable, Sequence

from .cache import ResponseCache
from .parse import ParseError, extract_json, validate
from .providers import DEFAULT_MODEL, Effort, Provider, provider_for
from .types import Image, LLMError, Message, Refusal, Response, Truncated, Usage

#: Sent back after a parse failure. It carries the original text and the specific
#: error, because "that was not valid" gives the model nothing to fix.
RETRY_TEMPLATE = (
    "Your previous reply could not be parsed: {error}\n\n"
    "It was:\n{text}\n\n"
    "Reply with JSON matching the schema, with no explanation and no code fences."
)


def _check(response: Response, max_tokens: int) -> None:
    """A declined reply may be empty or partial and a cut-off one is always partial.
    Neither is a reply, so neither is returned or cached."""
    if response.stop_reason == "refusal":
        raise Refusal("the request was declined; the text is not a usable reply")
    if response.stop_reason == "max_tokens":
        raise Truncated(f"the reply was cut off at max_tokens={max_tokens}")


class LLM:
    def __init__(self, model: str = DEFAULT_MODEL, *, provider: Provider | None = None,
                 max_tokens: int = 8000, effort: Effort | None = "high",
                 cache_dir: str | Path | None = None, token_ceiling: int = 32000,
                 max_content_retries: int = 3, extra: dict | None = None) -> None:
        self.model = model
        self.provider = provider or provider_for(model)
        self.max_tokens = max_tokens
        self.token_ceiling = max(max_tokens, token_ceiling)
        self.effort = effort
        self.max_content_retries = max_content_retries
        self.extra = dict(extra or {})
        self.cache = ResponseCache(cache_dir) if cache_dir else None
        self.usage = Usage()
        # `map` runs calls on several threads and they all bill to one tally.
        self._usage_lock = threading.Lock()

    # ---------------------------------------------------------------- one call

    def complete(self, system: str, user: str, *, messages: Sequence[Message] | None = None,
                 schema: dict | None = None, images: Sequence[Image] = ()) -> Response:
        msgs = list(messages) if messages is not None else [Message("user", user, tuple(images))]
        key = self._cache_key(system, msgs, schema)
        if self.cache is not None:
            hit = self.cache.get(key)
            if hit is not None:
                return hit

        budget = self.max_tokens
        while True:
            response = self.provider.complete(
                model=self.model, system=system, messages=msgs,
                max_tokens=budget, effort=self.effort,
                schema=schema, extra=self.extra)
            with self._usage_lock:
                self.usage = self.usage + response.usage
            try:
                _check(response, budget)   # declined and cut-off replies are not cached
            except Truncated:
                # A cut-off reply is short of room, not wrong. The next attempt doubles
                # the room and asks the same question; the reasoning a model spends
                # before writing counts against this budget too, so a long declaration
                # script can run out of it on a question that has a good answer.
                if budget >= self.token_ceiling:
                    raise
                budget = min(budget * 2, self.token_ceiling)
                continue
            break
        if self.cache is not None:
            self.cache.put(key, response)
        return response

    # ---------------------------------------------------------------- structured output

    def json(self, system: str, user: str, *, schema: dict, images: Sequence[Image] = ()) -> dict:
        """Ask for JSON. On a parse or schema failure, ask again with the error attached."""
        first = Message("user", user, tuple(images))
        messages = [first]
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
                # The images ride on the first message only; resending them with the
                # correction would bill for the same pixels twice.
                messages = [
                    first,
                    Message("user", RETRY_TEMPLATE.format(error=exc, text=response.text[:2000])),
                ]
        raise ParseError(f"no valid JSON after {self.max_content_retries} attempts: "
                         f"{last_error}; last reply: {last_text[:400]}")

    # ---------------------------------------------------------------- batches

    def map(self, prompts: Iterable[Sequence], *, workers: int = 4, schema: dict | None = None,
            on_error: Callable[[Exception], None] | None = None) -> list[Response | dict | None]:
        """Run a batch concurrently, keeping input order. A failed item comes back as None.

        An item is `(system, user)` or `(system, user, images)`. With a schema every
        item goes through `json` instead of `complete`, so a batch gets the same
        parse-failure feedback a single structured call gets, and comes back as dicts.
        """
        items = list(prompts)

        def run(item: Sequence) -> Response | dict | None:
            system, user, *rest = item
            images = rest[0] if rest else ()
            try:
                if schema is not None:
                    return self.json(system, user, schema=schema, images=images)
                return self.complete(system, user, images=images)
            except Exception as exc:  # noqa: BLE001 -- one failure must not stop the batch
                if on_error:
                    on_error(exc)
                return None

        if workers <= 1:
            return [run(p) for p in items]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(run, items))

    # ---------------------------------------------------------------- internals

    def _cache_key(self, system: str, messages: Sequence[Message], schema: dict | None) -> str:
        return jsonlib.dumps({
            "provider": self.provider.name,
            "model": self.model,
            "system": system,
            # Image digests, not the bytes: the key is stored beside every cached
            # reply, so putting base64 in it would multiply the cache by its size.
            "messages": [[m.role, m.content, [im.digest for im in m.images]] for m in messages],
            # `max_tokens` is deliberately absent: only complete replies are cached, so
            # the budget that produced one says nothing about its content, and keying on
            # it would throw the cache away every time the budget moved.
            "effort": self.effort,
            "schema": schema,
            "extra": self.extra,
        }, ensure_ascii=False, sort_keys=True)


__all__ = ["LLM", "LLMError"]
