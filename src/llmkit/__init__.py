"""A small, reusable layer for calling a model.

It knows nothing about chart generation and can be used anywhere a model is
needed: one structured call, a batch of prompts, a comparison across models.

    from llmkit import LLM, Image
    llm = LLM(cache_dir=".cache/llm")
    spec = llm.json("You are a data modelling assistant", prompt, schema=SCHEMA)
    read = llm.json(system, prompt, schema=SCHEMA, images=[Image.from_path("page.png")])

Naming a model picks the provider that serves it, so the same three lines run on
another vendor: `LLM("gpt-5.2")`, `LLM("gemini-3.1-pro-preview")`. Only that
vendor's SDK has to be installed -- the provider classes are imported on demand.
"""

from .cache import ResponseCache
from .client import LLM
from .embed import Deduper, cosine
from .parse import ParseError, extract_json, validate
from .providers import DEFAULT_MODEL, Provider, provider_for
from .types import Image, LLMError, Message, Refusal, Response, Truncated, Usage

__all__ = [
    "LLM", "Message", "Image", "Response", "Usage", "Provider", "AnthropicProvider",
    "OpenAIProvider", "GeminiProvider", "provider_for",
    "DEFAULT_MODEL", "ResponseCache", "Deduper", "cosine",
    "extract_json", "validate", "ParseError", "LLMError", "Refusal", "Truncated",
]

#: The three provider classes stay importable from the top level, but each one
#: needs its vendor's SDK, so they are fetched only when named.
_PROVIDERS = ("AnthropicProvider", "OpenAIProvider", "GeminiProvider")


def __getattr__(name: str):
    if name in _PROVIDERS:
        from . import providers

        return getattr(providers, name)
    raise AttributeError(name)
