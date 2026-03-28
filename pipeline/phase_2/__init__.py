"""
AGPDS Phase 2: Agentic Data Simulator (SDK-Driven)

Core module providing the FactTableSimulator SDK, distribution samplers,
pattern injection, schema metadata, three-layer validation, and sandbox
execution with error feedback.
"""

from .fact_table_simulator import FactTableSimulator
from .schema_metadata import SchemaMetadata, ColumnMeta
from .validators import (
    SchemaAwareValidator, generate_with_validation,
    FixAction, apply_fixes,
)
from .sandbox_executor import SandboxExecutor, ExecutionResult, run_with_retries

__all__ = [
    "FactTableSimulator",
    "SchemaMetadata",
    "ColumnMeta",
    "SchemaAwareValidator",
    "generate_with_validation",
    "FixAction",
    "apply_fixes",
    "SandboxExecutor",
    "ExecutionResult",
    "run_with_retries",
]
