"""A small, reusable layer for calling a model.

It knows nothing about chart generation and can be used anywhere a model is
needed: one structured call, a batch of prompts, a comparison across models.

    from llmkit import LLM, Image
    llm = LLM(cache_dir=".cache/llm")
    spec = llm.json("You are a data modelling assistant", prompt, schema=SCHEMA)
    read = llm.json(system, prompt, schema=SCHEMA, images=[Image.from_path("page.png")])
"""

from .cache import ResponseCache
from .client import LLM
from .embed import Deduper, cosine
from .parse import ParseError, extract_json, validate
from .providers import DEFAULT_MODEL, AnthropicProvider, Provider
from .types import Image, LLMError, Message, Refusal, Response, Truncated, Usage

__all__ = [
    "LLM", "Message", "Image", "Response", "Usage", "Provider", "AnthropicProvider",
    "DEFAULT_MODEL", "ResponseCache", "Deduper", "cosine",
    "extract_json", "validate", "ParseError", "LLMError", "Refusal", "Truncated",
]
