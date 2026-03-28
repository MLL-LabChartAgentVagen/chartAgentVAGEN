"""
Schema Metadata TypedDict — the contract between Phase 2 and Phase 3.

Matches the specification in phase_2.md §2.3.
"""

from typing import TypedDict, Optional, Literal


class ColumnMeta(TypedDict, total=False):
    """Metadata for a single column in the Master Table."""
    name: str
    type: Literal["categorical", "temporal", "measure"]
    role: Optional[Literal["primary", "secondary", "temporal", "measure"]]
    group: Optional[str]
    parent: Optional[str]
    cardinality: Optional[int]
    orthogonal: Optional[bool]
    declared_dist: Optional[str]
    declared_params: Optional[dict]
    scale: Optional[list[float]]


class DimensionGroupMeta(TypedDict):
    """Metadata for a dimension group."""
    columns: list[str]
    hierarchy: list[str]  # ordered root → leaf


class OrthogonalPair(TypedDict):
    """Pair of dimension groups declared as statistically independent."""
    group_a: str
    group_b: str
    rationale: str


class ConditionalMeta(TypedDict, total=False):
    """Conditional distribution specification."""
    measure: str
    on: str
    mapping: dict  # category_value → param overrides


class CorrelationMeta(TypedDict):
    """Correlation target between two measures."""
    col_a: str
    col_b: str
    target_r: float


class DependencyMeta(TypedDict, total=False):
    """Functional dependency specification."""
    target: str
    formula: str
    noise_sigma: float


class PatternMeta(TypedDict, total=False):
    """Injected pattern specification — all fields stored flat at top level (spec §2.3).

    Common fields:
        type, target, col

    outlier_entity:
        z_score

    trend_break:
        break_point, magnitude

    ranking_reversal:
        metrics, description

    dominance_shift:
        magnitude

    convergence:
        convergence_rate

    seasonal_anomaly:
        amplitude, period_days
    """
    type: str
    target: Optional[str]
    col: Optional[str]
    # outlier_entity
    z_score: Optional[float]
    # trend_break / dominance_shift
    break_point: Optional[str]
    magnitude: Optional[float]
    # ranking_reversal
    metrics: Optional[list[str]]
    description: Optional[str]
    # convergence
    convergence_rate: Optional[float]
    # seasonal_anomaly
    amplitude: Optional[float]
    period_days: Optional[int]


class SchemaMetadata(TypedDict, total=False):
    """
    Complete schema metadata output from FactTableSimulator.generate().

    This is the contract between Phase 2 (data generation) and
    Phase 3 (view amortization + QA instantiation).
    """
    dimension_groups: dict[str, DimensionGroupMeta]
    orthogonal_groups: list[OrthogonalPair]
    columns: list[ColumnMeta]
    conditionals: list[ConditionalMeta]
    correlations: list[CorrelationMeta]
    dependencies: list[DependencyMeta]
    patterns: list[PatternMeta]
    realism: dict
    total_rows: int  # target row count requested by simulator
    actual_rows: int  # actual generated row count
