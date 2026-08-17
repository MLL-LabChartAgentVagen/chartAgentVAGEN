"""可复用的 LLM 调用层。

与 chartgen 无关，任何需要调模型的地方都可以用：数据生成里的那一次调用、
横向评测多个模型、批量跑提示词。

    from llmkit import LLM
    llm = LLM(cache_dir=".cache/llm")
    spec = llm.json("你是数据建模助手", prompt, schema=SCHEMA)
"""

from .cache import ResponseCache
from .client import LLM
from .embed import Deduper, cosine
from .parse import ParseError, extract_json, validate
from .providers import DEFAULT_MODEL, AnthropicProvider, Provider
from .types import LLMError, Message, Refusal, Response, Truncated, Usage

__all__ = [
    "LLM", "Message", "Response", "Usage", "Provider", "AnthropicProvider",
    "DEFAULT_MODEL", "ResponseCache", "Deduper", "cosine",
    "extract_json", "validate", "ParseError", "LLMError", "Refusal", "Truncated",
]
