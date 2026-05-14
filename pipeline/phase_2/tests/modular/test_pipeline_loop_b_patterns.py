"""Regression test for pipeline.py:281 patterns-plumbing bug.

`run_loop_b_from_declarations` must forward `raw_declarations["patterns"]` to
the validator. The earlier bug read `metadata.get("patterns", [])` instead,
and since callers (`agpds_execute.py`) don't pass `metadata`, the validator
saw an empty patterns list. This silently broke `check_structural_residuals`'s
P3-8 pattern-row exclusion, causing pattern-injected outliers to be counted
into residual std, blowing up the ratio.
"""
from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd

from pipeline.phase_2.pipeline import run_loop_b_from_declarations
from pipeline.phase_2.sdk.simulator import FactTableSimulator


def _build_declarations_with_outlier_pattern() -> dict:
    """Return a raw_declarations dict whose LLM script declares an
    `inject_pattern("outlier_entity", ...)` — a pattern whose target rows
    would inflate residual_std unless the validator excludes them."""
    sim = FactTableSimulator(target_rows=400, seed=42)
    sim.add_category(
        "region", values=["N", "S"], weights=[0.5, 0.5], group="geo",
    )
    sim.add_measure(
        "applied",
        family="gaussian",
        param_model={
            "mu": {"intercept": 1000.0},
            "sigma": {"intercept": 100.0},
        },
    )
    sim.add_measure_structural(
        "accepted",
        formula="applied * 0.5",
        effects={},
        noise={"sigma": 50.0},
    )
    # Inject an outlier pattern that, if NOT excluded by validator, inflates
    # residual_std and triggers a false residual_* failure.
    sim.inject_pattern(
        "outlier_entity",
        target="region == 'N'",
        col="accepted",
        params={"z_score": 10.0},
    )
    return {
        "columns": sim._columns,
        "groups": sim._groups,
        "group_dependencies": sim._group_dependencies,
        "measure_dag": sim._measure_dag,
        "target_rows": sim.target_rows,
        "patterns": sim._patterns,
        "seed": sim.seed,
        "orthogonal_pairs": sim._orthogonal_pairs,
    }


def test_loop_b_forwards_patterns_from_declarations_to_validator():
    """When agpds_execute.py-style call path is used (no metadata kwarg),
    the validator must still receive the declared patterns. Without the
    fix this test would fail because pattern-injected outliers leak into
    residual_std and trip the validator on a measure that should pass."""
    raw_declarations = _build_declarations_with_outlier_pattern()
    assert len(raw_declarations["patterns"]) == 1, "test fixture sanity"

    # Spy on SchemaAwareValidator to confirm patterns are non-empty when
    # validate() is called.
    captured: dict = {"patterns_seen": None}

    from pipeline.phase_2.validation.validator import SchemaAwareValidator
    original_validate = SchemaAwareValidator.validate

    def spy_validate(self, df, patterns=None):
        captured["patterns_seen"] = patterns
        return original_validate(self, df, patterns)

    with patch.object(SchemaAwareValidator, "validate", spy_validate):
        result = run_loop_b_from_declarations(
            raw_declarations, max_retries=0,
        )

    assert captured["patterns_seen"] is not None, (
        "validate() was never called"
    )
    assert len(captured["patterns_seen"]) == 1, (
        "validator received empty patterns — pipeline.py:281 bug regressed"
    )
    assert captured["patterns_seen"][0]["type"] == "outlier_entity"
