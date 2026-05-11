"""
pipeline.core — Reusable building blocks for AGPDS and ChartAgentVAGEN.

Quick usage::

    from pipeline.core import LLMClient
    from pipeline.core.utils import META_CATEGORIES
"""

from .llm_client import (
    LLMClient,
    LLMResponse,
    ParameterAdapter,
    ProviderCapabilities,
    TokenUsage,
    get_provider_capabilities,
)
from .utils import (
    META_CATEGORIES,
    get_category_by_id,
)

__all__ = [
    # LLM
    "LLMClient",
    "LLMResponse",
    "ParameterAdapter",
    "ProviderCapabilities",
    "TokenUsage",
    "get_provider_capabilities",
    # Legacy CLI taxonomy (gated on Sprint F.4 CLI rename)
    "META_CATEGORIES",
    "get_category_by_id",
]
