"""The Gemini implementation of the provider seam, over the google-genai SDK.

Two differences from the other vendors are handled here and nowhere else. The
assistant role is called `model`, and the output cap covers the thinking tokens
as well as the reply, so a request with a deep effort level and a tight cap comes
back cut off with no text at all -- give `max_tokens` room for both.
"""

from __future__ import annotations

import base64
import time
from typing import Any, Sequence

from ..types import Image, Message, Response, Usage
from . import Effort, check_strict, map_effort

#: Gemini exposes thinking as four levels; the two deepest shared names both land
#: on the deepest one it defines.
EFFORT = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH", "xhigh": "HIGH", "max": "HIGH"}

#: The embedding endpoint the deduper can be pointed at.
EMBED_MODEL = "gemini-embedding-001"

#: Why generation stopped, in this package's words. Anything not listed is a
#: content decision by the service, which is a declined reply.
_STOP_REASONS = {"STOP": "end_turn", "MAX_TOKENS": "max_tokens", "FINISH_REASON_UNSPECIFIED": "end_turn"}


def message_content(message: Message) -> dict:
    """Images first, then the text. `assistant` is `model` on this vendor."""
    parts: list[dict] = [{"inline_data": {"mime_type": im.media_type,
                                          "data": base64.b64decode(im.data)}}
                         for im in message.images]
    if message.content:
        parts.append({"text": message.content})
    return {"role": "model" if message.role == "assistant" else "user", "parts": parts}


class GeminiProvider:
    """The official google-genai SDK.

    Sampling parameters are not sent, as with the other two providers, so the
    three requests differ only where the vendors' names differ.
    """

    name = "gemini"

    def __init__(self, api_key: str | None = None, **client_kwargs: Any) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key, **client_kwargs) if api_key \
            else genai.Client(**client_kwargs)

    @staticmethod
    def build_request(*, model: str, system: str, messages: Sequence[Message],
                      max_tokens: int, effort: Effort | None, schema: dict | None,
                      extra: dict) -> dict:
        """Assemble the request body. Separate so its shape can be checked offline."""
        config: dict[str, Any] = {"max_output_tokens": max_tokens}
        if system:
            config["system_instruction"] = system
        if effort:
            config["thinking_config"] = {"thinking_level": map_effort(effort, EFFORT, "gemini")}
        if schema is not None:
            check_strict(schema)
            # `response_json_schema` takes a JSON schema as written; `response_schema`
            # is the SDK's own dialect and would need the schema translated.
            config["response_mime_type"] = "application/json"
            config["response_json_schema"] = schema
        body = {"model": model,
                "contents": [message_content(m) for m in messages],
                "config": config}
        body["config"].update(extra)
        return body

    def complete(self, *, model: str, system: str, messages: Sequence[Message],
                 max_tokens: int, effort: Effort | None, schema: dict | None,
                 extra: dict) -> Response:
        body = self.build_request(model=model, system=system, messages=messages,
                                  max_tokens=max_tokens, effort=effort,
                                  schema=schema, extra=extra)
        started = time.monotonic()
        response = self._client.models.generate_content(**body)
        latency = time.monotonic() - started

        return Response(self.text_of(response), getattr(response, "model_version", None) or model,
                        self.usage_of(response), self.stop_reason(response), latency)

    @staticmethod
    def text_of(response: Any) -> str:
        """Join the reply's text parts, leaving the thought summaries out."""
        candidates = getattr(response, "candidates", None) or ()
        parts = getattr(getattr(candidates[0], "content", None), "parts", None) or () \
            if candidates else ()
        return "".join(p.text for p in parts if getattr(p, "text", None) and not getattr(p, "thought", False))

    @staticmethod
    def usage_of(response: Any) -> Usage:
        """Thinking tokens are billed as output, so they are counted as output here."""
        meta = getattr(response, "usage_metadata", None)
        if meta is None:
            return Usage()
        return Usage((meta.prompt_token_count or 0),
                     (meta.candidates_token_count or 0) + (meta.thoughts_token_count or 0),
                     (meta.cached_content_token_count or 0))

    @staticmethod
    def stop_reason(response: Any) -> str:
        if getattr(getattr(response, "prompt_feedback", None), "block_reason", None):
            return "refusal"
        candidates = getattr(response, "candidates", None) or ()
        if not candidates:
            return "refusal"
        reason = getattr(candidates[0], "finish_reason", None)
        name = getattr(reason, "name", None) or (str(reason) if reason else "STOP")
        return _STOP_REASONS.get(name, "refusal")

    def embed(self, texts: Sequence[str], model: str = EMBED_MODEL) -> list[list[float]]:
        reply = self._client.models.embed_content(model=model, contents=list(texts))
        return [list(e.values) for e in reply.embeddings]
