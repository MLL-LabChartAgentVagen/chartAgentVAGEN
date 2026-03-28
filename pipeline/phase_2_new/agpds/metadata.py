"""
Schema metadata builder extracted from FactTableSimulator.

Builds the §2.6 schema metadata dict from registries and pre-computed
DAG data.  This function has no dependency on FactTableSimulator instance
state — all inputs are passed explicitly.

Extracted during the Sprint 6 post-completion refactoring.
Original location: FactTableSimulator._build_schema_metadata.
"""
from __future__ import annotations

import logging
from typing import Any

from agpds.models import DimensionGroup, OrthogonalPair

logger = logging.getLogger(__name__)


def build_schema_metadata(
    groups: dict[str, DimensionGroup],
    orthogonal_pairs: list[OrthogonalPair],
    target_rows: int,
    measure_dag_order: list[str],
) -> dict[str, Any]:
    """Build the §2.6 schema metadata dict for all SPEC_READY fields.

    [Subtask 5.1.1, 5.1.2, 5.1.5, 5.1.7]

    Emits:
      - dimension_groups (5.1.1): group name → {columns, hierarchy}
      - orthogonal_groups (5.1.2): list of {group_a, group_b, rationale}
      - measure_dag_order (5.1.5): list of measure names in topo order
      - total_rows (5.1.7): target_rows integer

    Args:
        groups: Mapping of group name → DimensionGroup.
        orthogonal_pairs: List of OrthogonalPair declarations.
        target_rows: Declared target row count.
        measure_dag_order: Pre-computed topological order of measures.

    Returns:
        Dict with the four SPEC_READY metadata fields.  All returned data
        is defensively copied.
    """
    metadata: dict[str, Any] = {}

    dimension_groups: dict[str, dict[str, Any]] = {}
    for group_name, group in groups.items():
        dimension_groups[group_name] = group.to_metadata()
    metadata["dimension_groups"] = dimension_groups

    metadata["orthogonal_groups"] = [
        pair.to_metadata() for pair in orthogonal_pairs
    ]

    metadata["measure_dag_order"] = list(measure_dag_order)

    metadata["total_rows"] = target_rows

    logger.debug(
        "build_schema_metadata: emitted keys=%s.",
        list(metadata.keys()),
    )
    return metadata
