"""llmkit 的基本类型：消息、用量、回复，以及三类异常。"""

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
    """llmkit 抛出的所有异常的基类。"""


class Refusal(LLMError):
    """安全分类器拒答。文本可能为空或只有一半，不要当成正常回复。"""


class Truncated(LLMError):
    """回复被 max_tokens 截断。"""
