"""ChartAgent pipeline (Phase 0–2 implementation).

Top-level package surface (Sprint D.4): the only intentional re-export is
:class:`AGPDSPipeline`, the four-phase orchestrator. Everything else is
addressed via fully-qualified subpackage paths (``pipeline.phase_0``,
``pipeline.phase_1``, ``pipeline.phase_2``, ``pipeline.core``).
"""
from pipeline.agpds_pipeline import AGPDSPipeline

__all__ = ["AGPDSPipeline"]
