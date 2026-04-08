"""
SDK Simulator Module.

This module provides the central FactTableSimulator class.
In the Phase 2 architecture, this class serves primarily as a lightweight 
delegation shell. It holds internal state (registries, DAGs, etc.) and exposes 
the public API, while routing actual business logic (validation, computation, 
and metadata generation) to specialized submodules in phase_2.sdk and phase_2.engine.

Implements: §2.5 (Simulator API)
"""
from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any, Optional

import pandas as pd

from ..types import DeclarationStore, DimensionGroup, OrthogonalPair, GroupDependency
from ..exceptions import InvalidParameterError
from . import columns as _columns_api
from . import relationships as _rels_api
from ..engine import generator as _generator_api

logger = logging.getLogger(__name__)

class FactTableSimulator:
    """
    Simulator for synthetic tabular data per AGPDS specs.

    # TODO [M3-NC-3]: The sandbox currently catches one error at a time.
    # Multiple simultaneous SDK validation errors (e.g. two bad effects +
    # a cycle) are surfaced one per retry attempt. A future enhancement
    # could collect all validation errors in a single pass and relay them
    # as a batch to reduce retry iterations.
    """
    def __init__(self, target_rows: int, seed: int = 42) -> None:
        if not isinstance(target_rows, int) or isinstance(target_rows, bool):
            raise TypeError(f"target_rows must be an int, got {type(target_rows).__name__}.")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(f"seed must be an int, got {type(seed).__name__}.")
        if target_rows <= 0:
            raise ValueError(f"target_rows must be a positive integer, got {target_rows}.")

        self.target_rows: int = target_rows
        self.seed: int = seed

        logger.debug("FactTableSimulator initialized: target_rows=%d, seed=%d", target_rows, seed)

        self._store = DeclarationStore(target_rows, seed)
        # Alias mutable registries — same object references, so in-place
        # mutations by columns.py / relationships.py update the store.
        self._columns = self._store.columns
        self._groups = self._store.groups
        self._orthogonal_pairs = self._store.orthogonal_pairs
        self._group_dependencies = self._store.group_dependencies
        self._patterns = self._store.patterns
        self._measure_dag = self._store.measure_dag
        self._phase: str = "declaring"  # "declaring" or "relating"

    # _realism_config is reassigned (not mutated in-place) by set_realism(),
    # so a simple alias would break. Property delegates to the store.
    @property
    def _realism_config(self) -> Optional[dict[str, Any]]:
        return self._store.realism_config

    @_realism_config.setter
    def _realism_config(self, value: Optional[dict[str, Any]]) -> None:
        self._store.realism_config = value

    # P3-6: Step 1 / Step 2 ordering enforcement
    def _ensure_declaring_phase(self) -> None:
        if self._phase == "relating":
            raise InvalidParameterError(
                param_name="phase",
                value=0.0,
                reason="Column declarations (Step 1) must come before relationship "
                       "declarations (Step 2). A Step 2 method has already been called."
            )

    def _ensure_relating_phase(self) -> None:
        self._phase = "relating"

    def add_category(
        self,
        name: str,
        values: list[str],
        weights: list[float] | dict[str, list[float]],
        group: str,
        parent: str | None = None,
    ) -> None:
        self._store._check_mutable()
        self._ensure_declaring_phase()
        _columns_api.add_category(self._columns, self._groups, name, values, weights, group, parent)

    def add_temporal(
        self,
        name: str,
        start: str,
        end: str,
        freq: str,
        derive: list[str] | None = None,
    ) -> None:
        self._store._check_mutable()
        self._ensure_declaring_phase()
        _columns_api.add_temporal(self._columns, self._groups, name, start, end, freq, derive)

    def add_measure(
        self,
        name: str,
        family: str,
        param_model: dict[str, Any],
        scale: float | None = None,
    ) -> None:
        self._store._check_mutable()
        self._ensure_declaring_phase()
        _columns_api.add_measure(self._columns, name, family, param_model, scale)

    def add_measure_structural(
        self,
        name: str,
        formula: str,
        effects: dict[str, dict[str, float]] | None = None,
        noise: dict[str, Any] | None = None,
    ) -> None:
        self._store._check_mutable()
        self._ensure_declaring_phase()
        _columns_api.add_measure_structural(self._columns, self._measure_dag, name, formula, effects, noise)

    def declare_orthogonal(
        self, group_a: str, group_b: str, rationale: str = "",
    ) -> None:
        self._store._check_mutable()
        self._ensure_relating_phase()
        _rels_api.declare_orthogonal(
            self._groups, self._orthogonal_pairs,
            self._group_dependencies, self._columns,
            group_a, group_b, rationale,
        )

    def add_group_dependency(
        self,
        child_root: str,
        on: list[str],
        conditional_weights: dict[str, dict[str, float]],
    ) -> None:
        self._store._check_mutable()
        self._ensure_relating_phase()
        _rels_api.add_group_dependency(
            self._columns, self._groups,
            self._group_dependencies, self._orthogonal_pairs,
            child_root, on, conditional_weights,
        )

    def inject_pattern(
        self, type: str, target: str, col: str,
        params: dict[str, Any] | None = None, **extra_params: Any,
    ) -> None:
        self._store._check_mutable()
        self._ensure_relating_phase()
        # Accept both calling conventions:
        #   sim.inject_pattern(..., params={"z_score": 3.0})  ← prompt/one-shot style
        #   sim.inject_pattern(..., z_score=3.0)              ← kwargs style
        merged = dict(extra_params)
        if params is not None:
            merged.update(params)
        _rels_api.inject_pattern(
            self._columns, self._patterns,
            type, target, col, **merged,
        )

    def set_realism(
        self,
        missing_rate: float = 0.0,
        dirty_rate: float = 0.0,
        censoring: Optional[dict[str, Any]] = None,
    ) -> None:
        self._store._check_mutable()
        self._ensure_relating_phase()
        self._realism_config = _rels_api.set_realism(
            [], missing_rate, dirty_rate, censoring,
        )

    def generate(self) -> tuple[pd.DataFrame, dict[str, Any]]:
        self._store.freeze()
        df, schema_metadata = _generator_api.run_pipeline(
            columns=self._columns,
            groups=self._groups,
            group_dependencies=self._group_dependencies,
            measure_dag=self._measure_dag,
            target_rows=self.target_rows,
            seed=self.seed,
            patterns=self._patterns,
            realism_config=self._realism_config,
            orthogonal_pairs=self._orthogonal_pairs,
        )
        return df, schema_metadata

