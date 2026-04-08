"""
Engine pipeline orchestrator.

Coordinates the four-stage generation pipeline:
  M = τ_post ∘ δ? ∘ γ ∘ β ∘ α(seed)

Implements: §2.8
"""
from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..sdk import dag as _dag
from . import skeleton as _skeleton
from . import measures as _measures
from . import postprocess as _postprocess
from ..types import DimensionGroup, GroupDependency

logger = logging.getLogger(__name__)


def run_pipeline(
    columns: OrderedDict[str, dict[str, Any]],
    groups: dict[str, DimensionGroup],
    group_dependencies: list[GroupDependency],
    measure_dag: dict[str, list[str]],
    target_rows: int,
    seed: int,
    patterns: list[dict[str, Any]] | None = None,
    realism_config: dict[str, Any] | None = None,
    overrides: dict | None = None,
    orthogonal_pairs: list | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Execute the deterministic engine pipeline.

    [Subtask 4.1.1–4.1.5, 4.5.1, 5.1.1]

    Pipeline:
      1. Pre-flight: build full DAG, compute topo order
      2. Init RNG from seed
      3. Phase α: build skeleton (non-measure columns)
      4. Phase β: generate measures
      5. Post-process: convert to DataFrame
      6. Phase γ: inject patterns (if any)
      7. Phase δ: inject realism (if configured)
      8. Build schema metadata

    Args:
        columns: Column registry.
        groups: Group registry.
        group_dependencies: Cross-group dependencies.
        measure_dag: Measure DAG adjacency.
        target_rows: Number of rows to generate.
        seed: Random seed.
        patterns: Optional pattern specifications.
        realism_config: Optional realism configuration.
        overrides: Optional parameter overrides for Loop B.
        orthogonal_pairs: Optional list of OrthogonalPair for metadata.

    Returns:
        Tuple of (DataFrame, schema_metadata dict).
    """
    if patterns is None:
        patterns = []
    if orthogonal_pairs is None:
        orthogonal_pairs = []

    # Phase 1: Initialize deterministic RNG
    rng = np.random.default_rng(seed)

    # Phase 2: Build and sort the full generation DAG
    full_dag = _dag.build_full_dag(
        columns, groups, group_dependencies, measure_dag,
    )
    topo_order = _dag.topological_sort(full_dag)

    # Phase α: Skeleton builder — non-measure columns
    rows = _skeleton.build_skeleton(
        columns, target_rows, group_dependencies, topo_order, rng,
    )

    # Phase β: Measure generation
    rows = _measures.generate_measures(
        columns, topo_order, rows, rng, overrides,
    )

    # Post-processing: assemble DataFrame
    df = _postprocess.to_dataframe(rows, topo_order, columns, target_rows)

    # Phase γ: Pattern injection
    if patterns:
        from . import patterns as _patterns_mod
        df = _patterns_mod.inject_patterns(df, patterns, columns, rng)

    # Phase δ: Realism injection
    if realism_config is not None:
        from . import realism as _realism_mod
        df = _realism_mod.inject_realism(df, realism_config, columns, rng)

    # Build schema metadata
    from ..metadata.builder import build_schema_metadata as _build_meta

    # Extract measure order for metadata
    measure_names: set[str] = {
        col_name for col_name, col_meta in columns.items()
        if col_meta.get("type") == "measure"
    }
    if measure_names:
        _, measure_order = _dag.extract_measure_sub_dag(full_dag, measure_names)
    else:
        measure_order = []

    metadata = _build_meta(
        groups=groups,
        orthogonal_pairs=orthogonal_pairs,
        target_rows=target_rows,
        measure_dag_order=list(measure_order),
        columns=columns,
        group_dependencies=group_dependencies,
        patterns=patterns,
    )

    logger.debug(
        "run_pipeline: produced DataFrame shape=%s, %d metadata keys.",
        df.shape, len(metadata),
    )

    return df, metadata
