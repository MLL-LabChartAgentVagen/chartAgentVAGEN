"""The basic types: a message, a usage tally, a reply, and the errors that can occur."""

from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass, field
from hashlib import blake2b
from pathlib import Path
from typing import Literal

Role = Literal["user", "assistant"]

#: What the Anthropic image block accepts.
IMAGE_MEDIA_TYPES = ("image/png", "image/jpeg", "image/gif", "image/webp")


@dataclass(frozen=True)
class Image:
    """One image to send with a message, already base64 encoded.

    The bytes are never put in a cache key or a log line -- `digest` stands in
    for them, so a keyed request stays the size of a request.
    """

    media_type: str
    data: str

    def __post_init__(self) -> None:
        if self.media_type not in IMAGE_MEDIA_TYPES:
            raise ValueError(f"{self.media_type!r} is not one of {IMAGE_MEDIA_TYPES}")

    @classmethod
    def from_path(cls, path: str | Path) -> "Image":
        path = Path(path)
        media_type, _ = mimetypes.guess_type(path.name)
        return cls(media_type or "image/png", base64.b64encode(path.read_bytes()).decode("ascii"))

    @property
    def digest(self) -> str:
        return blake2b(f"{self.media_type}\n{self.data}".encode("utf-8"), digest_size=12).hexdigest()


@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    images: tuple[Image, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(self.input_tokens + other.input_tokens,
                     self.output_tokens + other.output_tokens,
                     self.cache_read_tokens + other.cache_read_tokens)


@dataclass(frozen=True)
class Response:
    text: str
    model: str
    usage: Usage = Usage()
    stop_reason: str = "end_turn"
    latency_s: float = 0.0


class LLMError(RuntimeError):
    """Base class for everything this package raises."""


class Refusal(LLMError):
    """The request was declined. The text may be empty or partial; it is not a reply."""


class Truncated(LLMError):
    """The reply was cut off by the output limit, so it is incomplete."""
