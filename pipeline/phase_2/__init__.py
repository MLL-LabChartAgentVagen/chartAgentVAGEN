"""
AGPDS — Agentic Data Simulator SDK.

Sprint 1–5 exports: exception hierarchy, data models, and FactTableSimulator.
Sprint 4 additions: inject_pattern(), set_realism(), and DAG construction
methods are on the FactTableSimulator class (no new public types).
Sprint 5 additions: generate() is now functional on the FactTableSimulator
class, producing skeleton DataFrames (non-measure columns) and SPEC_READY
metadata. No new public types.
Sprint 6 additions: Check and ValidationReport data classes for the three-layer
validator framework. Four L1 structural check functions. Pattern injection
(outlier_entity, trend_break) and realism injection (missing, dirty) are now
wired into generate(). No new public types beyond Check and ValidationReport.
Sprint 7 additions: Two L3 pattern validation checks (check_outlier_entity,
check_trend_break), one L2 helper (max_conditional_deviation), the auto-fix
strategy matcher (match_strategy), and three isolated auto-fix stubs
(widen_variance, amplify_magnitude, reshuffle_pair). No new public types.
"""
from .exceptions import (
    SimulatorError,
    CyclicDependencyError,
    UndefinedEffectError,
    NonRootDependencyError,
    InvalidParameterError,
    DuplicateColumnError,
    EmptyValuesError,
    WeightLengthMismatchError,
    DegenerateDistributionError,
    ParentNotFoundError,
    DuplicateGroupRootError,
    PatternInjectionError,
    SkipResult,
)
from .types import (
    DimensionGroup, OrthogonalPair, GroupDependency,
    Check, ValidationReport,
    PatternSpec, RealismConfig, DeclarationStore,
    SandboxResult, RetryLoopResult,
)
from .sdk.simulator import FactTableSimulator
from .validation.structural import (
    check_row_count,
    check_categorical_cardinality,
    check_orthogonal_independence,
    check_measure_dag_acyclic,
)
from .validation.pattern_checks import (
    check_outlier_entity,
    check_trend_break,
)
from .validation.statistical import (
    max_conditional_deviation,
)
from .validation.autofix import (
    match_strategy,
    widen_variance,
    amplify_magnitude,
    reshuffle_pair,
)
from .orchestration.sandbox import (
    execute_in_sandbox,
    format_error_feedback,
    run_retry_loop,
)
from .pipeline import run_phase2

__all__ = [
    # Exceptions
    "SimulatorError",
    "CyclicDependencyError",
    "UndefinedEffectError",
    "NonRootDependencyError",
    "InvalidParameterError",
    "DuplicateColumnError",
    "EmptyValuesError",
    "WeightLengthMismatchError",
    "DegenerateDistributionError",
    "ParentNotFoundError",
    "DuplicateGroupRootError",
    "PatternInjectionError",
    "SkipResult",
    # Data types
    "DimensionGroup",
    "OrthogonalPair",
    "GroupDependency",
    "Check",
    "ValidationReport",
    "PatternSpec",
    "RealismConfig",
    "DeclarationStore",
    # Simulator
    "FactTableSimulator",
    # Validator — L1 structural checks
    "check_row_count",
    "check_categorical_cardinality",
    "check_orthogonal_independence",
    "check_measure_dag_acyclic",
    # Validator — L3 pattern checks
    "check_outlier_entity",
    "check_trend_break",
    # Validator — L2 helper
    "max_conditional_deviation",
    # Validator — auto-fix strategy dispatch
    "match_strategy",
    # Validator — auto-fix strategy stubs
    "widen_variance",
    "amplify_magnitude",
    "reshuffle_pair",
    # Sandbox types
    "SandboxResult",
    "RetryLoopResult",
    # Sandbox logic
    "execute_in_sandbox",
    "format_error_feedback",
    "run_retry_loop",
    # Pipeline entry point
    "run_phase2",
]
