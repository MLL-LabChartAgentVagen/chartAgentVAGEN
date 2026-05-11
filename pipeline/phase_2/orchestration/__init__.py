"""
AGPDS LLM Orchestration — re-exports key components.

Sprint D.1 collapsed the per-Phase fork: LLMClient now lives in
``pipeline.core.llm_client``; this re-export preserves the historical
``from pipeline.phase_2.orchestration import LLMClient`` import path.
"""
from pipeline.core.llm_client import LLMClient

__all__ = ["LLMClient"]
