"""The OpenAI implementation of the provider seam, over the Responses API.

Responses rather than Chat Completions: it is where reasoning effort and strict
structured output live, and the reasoning models are only fully addressable there.

Three names differ from the other vendors and are translated here, so nothing
above this file knows about them: the system prompt is `instructions`, the output
cap is `max_output_tokens`, and one message's parts are typed `input_text` /
`input_image` on the way in and `output_text` on the way back.
"""

from __future__ import annotations

import time
from typing import Any, Sequence

from ..types import Image, Message, Response, Usage
from . import Effort, check_strict, map_effort

#: `none` and `minimal` exist as well, but they are below the range this package
#: offers; `max` is served by the deepest level the API defines.
EFFORT = {"low": "low", "medium": "medium", "high": "high", "xhigh": "xhigh", "max": "xhigh"}

#: The embedding endpoint the deduper can be pointed at.
EMBED_MODEL = "text-embedding-3-small"


def fully_required(schema: dict) -> bool:
    """Whether every object in the schema lists all its declared properties as required.

    That is the one precondition strict mode adds over `check_strict`. A schema
    with a genuinely optional field is legitimate and the other two vendors take
    it, so it is sent non-strict rather than refused: the reply is then checked
    against the same schema by the client, which feeds any mismatch back.
    """
    if schema.get("type") == "object":
        if any(k not in schema.get("required", ()) for k in schema.get("properties", {})):
            return False
    return (all(fully_required(sub) for sub in schema.get("properties", {}).values())
            and (not isinstance(schema.get("items"), dict) or fully_required(schema["items"])))


def image_part(image: Image) -> dict:
    """An image is sent inline as a data URI; the API takes no raw base64 field."""
    return {"type": "input_image",
            "image_url": f"data:{image.media_type};base64,{image.data}"}


def message_content(message: Message) -> list[dict]:
    """Images first, then the text: the question is about them, and parts are read
    in order. An assistant turn carries `output_text`, which is what the API
    accepts when a previous reply is fed back in."""
    text_type = "output_text" if message.role == "assistant" else "input_text"
    parts: list[dict] = [image_part(im) for im in message.images]
    if message.content:
        parts.append({"type": text_type, "text": message.content})
    return parts


class OpenAIProvider:
    """The official OpenAI SDK.

    Sampling parameters are not sent: reasoning models reject or ignore them, and
    leaving them out keeps one request shape across the three vendors.
    """

    name = "openai"

    def __init__(self, api_key: str | None = None, **client_kwargs: Any) -> None:
        import openai

        self._client = openai.OpenAI(api_key=api_key, **client_kwargs) \
            if api_key else openai.OpenAI(**client_kwargs)

    @staticmethod
    def build_request(*, model: str, system: str, messages: Sequence[Message],
                      max_tokens: int, effort: Effort | None, schema: dict | None,
                      extra: dict) -> dict:
        """Assemble the request body. Separate so its shape can be checked offline."""
        body: dict[str, Any] = {
            "model": model,
            "max_output_tokens": max_tokens,
            "input": [{"role": m.role, "content": message_content(m)} for m in messages],
        }
        if system:
            body["instructions"] = system
        if effort:
            body["reasoning"] = {"effort": map_effort(effort, EFFORT, "openai")}
        if schema is not None:
            check_strict(schema)
            body["text"] = {"format": {"type": "json_schema", "name": "reply",
                                       "schema": schema, "strict": fully_required(schema)}}
        body.update(extra)
        return body

    def complete(self, *, model: str, system: str, messages: Sequence[Message],
                 max_tokens: int, effort: Effort | None, schema: dict | None,
                 extra: dict) -> Response:
        body = self.build_request(model=model, system=system, messages=messages,
                                  max_tokens=max_tokens, effort=effort,
                                  schema=schema, extra=extra)
        started = time.monotonic()
        response = self._client.responses.create(**body)
        latency = time.monotonic() - started

        usage = Usage(getattr(response.usage, "input_tokens", 0) if response.usage else 0,
                      getattr(response.usage, "output_tokens", 0) if response.usage else 0,
                      self._cached_tokens(response))
        return Response(response.output_text or "", response.model, usage,
                        self.stop_reason(response), latency)

    @staticmethod
    def _cached_tokens(response: Any) -> int:
        details = getattr(getattr(response, "usage", None), "input_tokens_details", None)
        return getattr(details, "cached_tokens", 0) or 0

    @staticmethod
    def stop_reason(response: Any) -> str:
        """Map the API's two separate signals onto the one word the client checks.

        A declined reply is a `refusal` part inside an otherwise complete response,
        while a cut-off one is a status of `incomplete` with a reason beside it.
        """
        for item in getattr(response, "output", ()) or ():
            for part in getattr(item, "content", ()) or ():
                if getattr(part, "type", "") == "refusal":
                    return "refusal"
        reason = getattr(getattr(response, "incomplete_details", None), "reason", None)
        if reason == "max_output_tokens":
            return "max_tokens"
        if reason == "content_filter":
            return "refusal"
        return "end_turn"

    def embed(self, texts: Sequence[str], model: str = EMBED_MODEL) -> list[list[float]]:
        reply = self._client.embeddings.create(model=model, input=list(texts))
        return [item.embedding for item in sorted(reply.data, key=lambda d: d.index)]
