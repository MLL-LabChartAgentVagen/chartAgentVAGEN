"""
pipeline.core — Reusable building blocks for AGPDS and ChartAgentVAGEN.

This package collects the production-ready components salvaged from the
monolithic ``generation_pipeline.py`` and ``generation_runner.py``.

Quick usage::

    from pipeline.core import LLMClient, GeminiClient
    from pipeline.core.topic_agent import NodeA_TopicAgent
    from pipeline.core.utils import META_CATEGORIES
"""

from .llm_client import (
    LLMClient,
    GeminiClient,
    ParameterAdapter,
    ProviderCapabilities,
    get_provider_capabilities,
)
from .utils import (
    META_CATEGORIES,
    generate_unique_id,
    validate_category,
    get_category_by_id,
    get_available_categories,
    print_available_categories,
)

__all__ = [
    # LLM
    "LLMClient",
    "GeminiClient",
    "ParameterAdapter",
    "ProviderCapabilities",
    "get_provider_capabilities",
    # Utilities
    "META_CATEGORIES",
    "generate_unique_id",
    "validate_category",
    "get_category_by_id",
    "get_available_categories",
    "print_available_categories",
]
