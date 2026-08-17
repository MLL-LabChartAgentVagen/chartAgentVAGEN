"""The basic types: a message, a usage tally, a reply, and the errors that can occur."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


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
