"""
pipeline.core — Reusable building blocks for AGPDS and ChartAgentVAGEN.

Quick usage::

    from pipeline.core import LLMClient
    from pipeline.core.utils import META_CATEGORIES
"""

from .llm_client import (
    LLMClient,
    ParameterAdapter,
    ProviderCapabilities,
    get_provider_capabilities,
)
from .utils import (
    META_CATEGORIES,
    validate_category,
    get_category_by_id,
    get_available_categories,
    print_available_categories,
)

__all__ = [
    # LLM
    "LLMClient",
    "ParameterAdapter",
    "ProviderCapabilities",
    "get_provider_capabilities",
    # Utilities
    "META_CATEGORIES",
    "validate_category",
    "get_category_by_id",
    "get_available_categories",
    "print_available_categories",
]
