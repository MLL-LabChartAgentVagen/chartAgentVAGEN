"""
Schema metadata builder — enriched version.

Builds the §2.6 schema_metadata dictionary with all 7 top-level keys.
Enriched beyond the §2.6 example to include fields needed by M5 validation:
  - columns: type-discriminated descriptors with values/weights/param_model
  - group_dependencies: includes conditional_weights
  - patterns: includes full params

Implements: §2.6 (P0-1 enrichment)
"""
from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any

from ..types import DimensionGroup, OrthogonalPair, GroupDependency

logger = logging.getLogger(__name__)


def build_schema_metadata(
    groups: dict[str, DimensionGroup],
    orthogonal_pairs: list[OrthogonalPair],
    target_rows: int,
    measure_dag_order: list[str],
    columns: OrderedDict[str, dict[str, Any]] | None = None,
    group_dependencies: list[GroupDependency] | None = None,
    patterns: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the §2.6 schema metadata dict with all 7 keys.

    [Subtask 5.1.1, 5.1.2, 5.1.5, 5.1.7 + P0-1 enrichment]

    The 7 top-level keys:
      1. dimension_groups: group name → {columns, hierarchy}
      2. orthogonal_groups: list of {group_a, group_b, rationale}
      3. group_dependencies: list of {child_root, on, conditional_weights}
      4. columns: dict of column name → type-discriminated descriptor
      5. measure_dag_order: list of measure names in topo order
      6. patterns: list of pattern specs with full params
      7. total_rows: target_rows integer

    Args:
        groups: Mapping of group name → DimensionGroup.
        orthogonal_pairs: List of OrthogonalPair declarations.
        target_rows: Declared target row count.
        measure_dag_order: Pre-computed topological order of measures.
        columns: Optional column registry for enriched output.
        group_dependencies: Optional cross-group dependencies.
        patterns: Optional pattern specifications.

    Returns:
        Dict with all 7 metadata keys. All returned data is defensively copied.
    """
    metadata: dict[str, Any] = {}

    # Key 1: dimension_groups
    dimension_groups: dict[str, dict[str, Any]] = {}
    for group_name, group in groups.items():
        dimension_groups[group_name] = group.to_metadata()
    metadata["dimension_groups"] = dimension_groups

    # Key 2: orthogonal_groups
    metadata["orthogonal_groups"] = [
        pair.to_metadata() for pair in orthogonal_pairs
    ]

    # Key 3: group_dependencies (enriched with conditional_weights)
    if group_dependencies is not None:
        metadata["group_dependencies"] = [
            dep.to_metadata() for dep in group_dependencies
        ]
    else:
        metadata["group_dependencies"] = []

    # Key 4: columns (enriched — type-discriminated descriptors)
    if columns is not None:
        metadata["columns"] = _build_columns_metadata(columns)
    else:
        metadata["columns"] = {}

    # Key 5: measure_dag_order
    metadata["measure_dag_order"] = list(measure_dag_order)

    # Key 6: patterns (enriched with full params)
    if patterns is not None:
        metadata["patterns"] = [
            {
                "type": p["type"],
                "target": p["target"],
                "col": p["col"],
                "params": dict(p.get("params", {})),
            }
            for p in patterns
        ]
    else:
        metadata["patterns"] = []

    # Key 7: total_rows
    metadata["total_rows"] = target_rows

    # Post-build consistency check
    _assert_metadata_consistency(metadata)

    logger.debug(
        "build_schema_metadata: emitted keys=%s.",
        list(metadata.keys()),
    )
    return metadata


def _build_columns_metadata(
    columns: OrderedDict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build the enriched columns sub-dict.

    For each column, includes type-specific fields:
      - categorical: type, values, weights, cardinality, group, parent
      - temporal: type, start, end, freq, derive, group
      - temporal_derived: type, derivation, source, group
      - measure (stochastic): type, measure_type, family, param_model
      - measure (structural): type, measure_type, formula, effects, noise

    Args:
        columns: Column registry.

    Returns:
        Dict mapping column name → enriched descriptor.
    """
    result: dict[str, dict[str, Any]] = {}

    for col_name, col_meta in columns.items():
        col_type = col_meta.get("type")
        entry: dict[str, Any] = {"type": col_type}

        if col_type == "categorical":
            entry["values"] = list(col_meta.get("values", []))
            entry["weights"] = col_meta.get("weights")
            entry["cardinality"] = len(col_meta.get("values", []))
            entry["group"] = col_meta.get("group")
            entry["parent"] = col_meta.get("parent")

        elif col_type == "temporal":
            entry["start"] = col_meta.get("start")
            entry["end"] = col_meta.get("end")
            entry["freq"] = col_meta.get("freq")
            entry["derive"] = list(col_meta.get("derive", []))
            entry["group"] = col_meta.get("group")

        elif col_type == "temporal_derived":
            entry["derivation"] = col_meta.get("derivation")
            entry["source"] = col_meta.get("source")
            entry["group"] = col_meta.get("group")

        elif col_type == "measure":
            entry["measure_type"] = col_meta.get("measure_type")
            measure_type = col_meta.get("measure_type")

            if measure_type == "stochastic":
                entry["family"] = col_meta.get("family")
                # Deep copy param_model to prevent mutation
                pm = col_meta.get("param_model", {})
                entry["param_model"] = _deep_copy_param_model(pm)
            elif measure_type == "structural":
                entry["formula"] = col_meta.get("formula")
                entry["effects"] = {
                    k: dict(v) for k, v in col_meta.get("effects", {}).items()
                }
                entry["noise"] = dict(col_meta.get("noise", {}))

        result[col_name] = entry

    return result


def _deep_copy_param_model(pm: dict[str, Any]) -> dict[str, Any]:
    """Deep copy a param_model dict, handling both scalar and effects forms."""
    result: dict[str, Any] = {}
    for key, value in pm.items():
        if isinstance(value, dict):
            inner = dict(value)
            if "effects" in inner and isinstance(inner["effects"], dict):
                inner["effects"] = {
                    k: dict(v) for k, v in inner["effects"].items()
                }
            result[key] = inner
        else:
            result[key] = value
    return result


def _assert_metadata_consistency(meta: dict[str, Any]) -> None:
    """Post-build self-validation of metadata internal consistency.

    [Target Architecture — metadata/builder.py]

    Checks:
      - Every column in dimension_groups appears in columns
      - Every measure_dag_order entry exists in columns
      - Every pattern col is a measure
      - Every orthogonal_groups entry references valid groups

    Args:
        meta: The assembled metadata dict.

    Raises:
        ValueError: If any consistency check fails.
    """
    columns_meta = meta.get("columns", {})
    dim_groups = meta.get("dimension_groups", {})

    # Check: dimension_groups columns exist in columns metadata
    for group_name, group_info in dim_groups.items():
        for col_name in group_info.get("columns", []):
            if columns_meta and col_name not in columns_meta:
                logger.warning(
                    "Metadata consistency: column '%s' in group '%s' "
                    "not found in columns metadata.",
                    col_name, group_name,
                )

    # Check: measure_dag_order entries exist in columns
    for measure_name in meta.get("measure_dag_order", []):
        if columns_meta and measure_name not in columns_meta:
            logger.warning(
                "Metadata consistency: measure '%s' in measure_dag_order "
                "not found in columns metadata.",
                measure_name,
            )

    # Check: pattern cols are measures
    for pattern in meta.get("patterns", []):
        col = pattern.get("col", "")
        if columns_meta and col in columns_meta:
            if columns_meta[col].get("type") != "measure":
                logger.warning(
                    "Metadata consistency: pattern col '%s' is not a "
                    "measure column.", col,
                )

    # Check: orthogonal_groups reference valid groups
    for pair in meta.get("orthogonal_groups", []):
        for key in ("group_a", "group_b"):
            gname = pair.get(key, "")
            if gname and gname not in dim_groups:
                logger.warning(
                    "Metadata consistency: orthogonal group '%s' "
                    "not found in dimension_groups.", gname,
                )
