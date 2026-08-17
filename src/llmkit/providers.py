"""The provider seam, and the Anthropic implementation of it.

`Provider` is the only place that knows a vendor: adding one is adding a file, and
the client above it does not change. Only Anthropic is implemented, because
abstracting over a second vendor before there is one buys nothing.
"""

from __future__ import annotations

import time
from typing import Any, Protocol, Sequence

from .types import LLMError, Message, Response, Usage

#: The model used when none is named.
DEFAULT_MODEL = "claude-opus-5"

#: How much reasoning effort to spend on a request.
Effort = str  # low | medium | high | xhigh | max


def check_strict(schema: dict, path: str = "schema") -> None:
    """A schema for structured output must close every object it contains.

    An object that omits `additionalProperties: false` is refused by the service,
    and the refusal names only the innermost field, so a schema written a level
    away from the call is hard to correct. Checking before the request goes out
    names the whole path and costs nothing.
    """
    if schema.get("type") == "object" and schema.get("additionalProperties") is not False:
        raise LLMError(f"`{path}` is an object without `additionalProperties: false`; "
                       "structured output requires it on every object in the schema")
    for key, sub in schema.get("properties", {}).items():
        check_strict(sub, f"{path}.{key}")
    if isinstance(schema.get("items"), dict):
        check_strict(schema["items"], f"{path}[]")


class Provider(Protocol):
    name: str

    def complete(self, *, model: str, system: str, messages: Sequence[Message],
                 max_tokens: int, effort: Effort | None, schema: dict | None,
                 extra: dict) -> Response:
        ...

    def embed(self, texts: Sequence[str], model: str) -> list[list[float]]:
        ...


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
            output_config["effort"] = effort
        if schema is not None:
            check_strict(schema)
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
        message = self._client.messages.create(**kwargs, extra_body=extra_body)
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
