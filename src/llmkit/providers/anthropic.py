"""The Anthropic implementation of the provider seam."""

from __future__ import annotations

import time
from typing import Any, Sequence

from ..types import Message, Response, Usage
from . import Effort, check_strict, map_effort

#: Anthropic names the effort levels the same way this package does.
EFFORT = {"low": "low", "medium": "medium", "high": "high", "xhigh": "xhigh", "max": "max"}

#: What the embedding-based deduper would call; Anthropic serves no such endpoint.
EMBED_MODEL = ""


def message_content(message: Message) -> str | list[dict]:
    """A text-only message stays a plain string; one with images becomes blocks.

    Images go before the text: the question is about them, and a model reads the
    blocks in order.
    """
    if not message.images:
        return message.content
    blocks: list[dict] = [
        {"type": "image", "source": {"type": "base64", "media_type": im.media_type, "data": im.data}}
        for im in message.images
    ]
    if message.content:
        blocks.append({"type": "text", "text": message.content})
    return blocks


class AnthropicProvider:
    """The official Anthropic SDK.

    Sampling parameters and fixed thinking budgets are not sent: current models
    reject them. Reasoning depth is set by an effort level, and structured output
    is guaranteed by a JSON schema, both inside the output configuration.
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
        """Assemble the request body. Separate so its shape can be checked offline."""
        output_config: dict[str, Any] = {}
        if effort:
            output_config["effort"] = map_effort(effort, EFFORT, "anthropic")
        if schema is not None:
            check_strict(schema)
            output_config["format"] = {"type": "json_schema", "schema": schema}

        body: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": m.role, "content": message_content(m)} for m in messages],
        }
        if system:
            body["system"] = system
        if output_config:
            body["output_config"] = output_config
        body.update(extra)
        return body

    #: Fields the SDK has always had a keyword for. Everything else goes through
    #: `extra_body`, which older and newer SDK versions both accept.
    TYPED_FIELDS = ("model", "max_tokens", "messages", "system", "stream")

    @classmethod
    def split_body(cls, body: dict) -> tuple[dict, dict | None]:
        """Split a request body into SDK keywords and an `extra_body` remainder.

        Newer request parameters have no keyword on an older SDK and passing them
        directly raises. `extra_body` is merged into the JSON body untouched, so
        splitting once here works against either.
        """
        kwargs = {k: v for k, v in body.items() if k in cls.TYPED_FIELDS}
        extra_body = {k: v for k, v in body.items() if k not in cls.TYPED_FIELDS}
        return kwargs, extra_body or None

    def complete(self, *, model: str, system: str, messages: Sequence[Message],
                 max_tokens: int, effort: Effort | None, schema: dict | None,
                 extra: dict) -> Response:
        body = self.build_request(model=model, system=system, messages=messages,
                                  max_tokens=max_tokens, effort=effort,
                                  schema=schema, extra=extra)
        kwargs, extra_body = self.split_body(body)
        started = time.monotonic()
        # Streamed, then reassembled: a high-effort structured reply can run past the
        # SDK's ceiling on a single non-streaming request, and the ceiling is a
        # function of `max_tokens`, so it is reached before the reply is long.
        with self._client.messages.stream(**kwargs, extra_body=extra_body) as stream:
            message = stream.get_final_message()
        latency = time.monotonic() - started

        text = "".join(b.text for b in message.content if b.type == "text")
        usage = Usage(getattr(message.usage, "input_tokens", 0),
                      getattr(message.usage, "output_tokens", 0),
                      getattr(message.usage, "cache_read_input_tokens", 0) or 0)
        # The stop reason is reported as-is. What to do about a declined or cut-off
        # reply is a policy decision, and it lives one level up so every provider
        # inherits the same one.
        return Response(text, message.model, usage, message.stop_reason or "end_turn", latency)

    def embed(self, texts: Sequence[str], model: str) -> list[list[float]]:
        raise NotImplementedError(
            "this provider has no embedding endpoint. The deduper defaults to a "
            "local lexical similarity, or pass it any embedding function you like.")
