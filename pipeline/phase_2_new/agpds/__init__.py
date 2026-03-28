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
from agpds.exceptions import (
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
    # FIX: [self-review item 6] — Added PatternInjectionError for typed
    # generation-time injection errors, replacing bare ValueError.
    PatternInjectionError,
)
from agpds.models import DimensionGroup, OrthogonalPair, GroupDependency
from agpds.simulator import FactTableSimulator
from agpds.validator import (
    # Sprint 6 — Validator data classes and L1 checks
    Check,
    ValidationReport,
    check_row_count,
    check_categorical_cardinality,
    check_orthogonal_independence,
    check_measure_dag_acyclic,
    # Sprint 7 — L3 checks, L2 helper, strategy dispatch, fix stubs
    check_outlier_entity,
    check_trend_break,
    max_conditional_deviation,
    match_strategy,
    widen_variance,
    amplify_magnitude,
    reshuffle_pair,
)

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
    # Data models
    "DimensionGroup",
    "OrthogonalPair",
    "GroupDependency",
    # Simulator
    "FactTableSimulator",
    # Validator — data classes (Sprint 6)
    "Check",
    "ValidationReport",
    # Validator — L1 structural checks (Sprint 6)
    "check_row_count",
    "check_categorical_cardinality",
    "check_orthogonal_independence",
    "check_measure_dag_acyclic",
    # Validator — L3 pattern checks (Sprint 7)
    "check_outlier_entity",
    "check_trend_break",
    # Validator — L2 helper (Sprint 7)
    "max_conditional_deviation",
    # Validator — auto-fix strategy dispatch (Sprint 7)
    "match_strategy",
    # Validator — auto-fix strategy stubs (Sprint 7, isolated — B2/B3)
    "widen_variance",
    "amplify_magnitude",
    "reshuffle_pair",
]
