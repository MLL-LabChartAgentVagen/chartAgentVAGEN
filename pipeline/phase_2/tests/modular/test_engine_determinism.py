"""Stage-by-stage determinism guards (closes T1.2 of TEST_AUDIT_2026-05-07.md).

Spec §2.5: *"Given the same `seed`, output is bit-for-bit reproducible.
Pipeline composition: M = τ_post ∘ ρ ∘ φ ∘ ψ ∘ λ ∘ γ ∘ δ ∘ β(seed)."*

The pre-existing `test_engine_generator.py::test_pipeline_phases_called_in_order`
mocks `_postprocess.to_dataframe`, `_measures.generate_measures`,
`_skeleton.build_skeleton`, `_dag.topological_sort`, `_dag.build_full_dag`,
and `metadata.builder.build_schema_metadata` — it verifies *call order* but
never that any of those stages produce the same output across two runs with
the same seed. Loop B (`generate_with_validation`) explicitly relies on
deterministic re-execution; if `np.random.default_rng(seed)` were ever moved
out of `run_pipeline` into a stage that re-seeds, every existing test would
still pass while the autofix loop silently broke.

These tests run each stage twice with a fresh `np.random.default_rng(42)` and
assert exact equality (`np.testing.assert_array_equal` for ndarrays,
`pd.testing.assert_frame_equal` for DataFrames). The final test runs the
whole `run_pipeline` end-to-end twice with no mocks.
"""
from __future__ import annotations

from collections import OrderedDict

import numpy as np
import pandas as pd
import pytest

from pipeline.phase_2.engine.generator import run_pipeline
from pipeline.phase_2.engine.measures import _sample_stochastic, generate_measures
from pipeline.phase_2.engine.patterns import inject_patterns
from pipeline.phase_2.engine.realism import inject_realism
from pipeline.phase_2.engine.skeleton import (
    build_skeleton,
    sample_dependent_root,
    sample_independent_root,
)
from pipeline.phase_2.types import DimensionGroup, GroupDependency


def _independent_root_col_meta() -> dict:
    return {
        "type": "categorical",
        "group": "g1",
        "values": ["A", "B", "C"],
        "weights": [0.5, 0.3, 0.2],
    }


def _gaussian_col_meta(mu: float = 100.0, sigma: float = 10.0) -> dict:
    return {
        "type": "measure",
        "measure_type": "stochastic",
        "family": "gaussian",
        "param_model": {
            "mu": {"intercept": mu, "effects": {}},
            "sigma": {"intercept": sigma, "effects": {}},
        },
    }


class TestStageAlphaDeterminism:
    """β stage — skeleton (categorical roots, children, temporals)."""

    def test_sample_independent_root_is_deterministic(self):
        col_meta = _independent_root_col_meta()
        a = sample_independent_root(
            "hospital", col_meta, 1000, np.random.default_rng(42),
        )
        b = sample_independent_root(
            "hospital", col_meta, 1000, np.random.default_rng(42),
        )
        np.testing.assert_array_equal(a, b)

    def test_sample_dependent_root_is_deterministic(self):
        # Build a fixture where 'severity' is conditional on 'hospital'.
        rng_setup = np.random.default_rng(0)
        hospital_arr = rng_setup.choice(
            np.array(["A", "B"], dtype=object), size=300, p=[0.5, 0.5],
        )
        rows = {"hospital": hospital_arr}
        col_meta = {
            "type": "categorical",
            "group": "g2",
            "values": ["Mild", "Severe"],
        }
        dep = GroupDependency(
            child_root="severity",
            on=["hospital"],
            conditional_weights={
                "A": {"Mild": 0.7, "Severe": 0.3},
                "B": {"Mild": 0.4, "Severe": 0.6},
            },
        )
        a = sample_dependent_root(
            "severity", col_meta, dep, dict(rows), 300,
            np.random.default_rng(42),
        )
        b = sample_dependent_root(
            "severity", col_meta, dep, dict(rows), 300,
            np.random.default_rng(42),
        )
        np.testing.assert_array_equal(a, b)

    def test_build_skeleton_full_pass_is_deterministic(self):
        columns = OrderedDict({
            "hospital": _independent_root_col_meta(),
        })
        topo_order = ["hospital"]
        a = build_skeleton(columns, 500, [], topo_order, np.random.default_rng(42))
        b = build_skeleton(columns, 500, [], topo_order, np.random.default_rng(42))
        # Same set of columns, same shape, same byte-level values.
        assert set(a.keys()) == set(b.keys())
        for k in a:
            np.testing.assert_array_equal(a[k], b[k])


class TestStageDeltaDeterminism:
    """δ stage — measure generation (stochastic + structural)."""

    def test_sample_stochastic_gaussian_is_deterministic(self):
        col_meta = _gaussian_col_meta(100.0, 10.0)
        rows = {"_dummy": np.arange(500)}
        a = _sample_stochastic(
            "rev", col_meta, dict(rows), np.random.default_rng(42),
        )
        b = _sample_stochastic(
            "rev", col_meta, dict(rows), np.random.default_rng(42),
        )
        np.testing.assert_array_equal(a, b)

    def test_generate_measures_full_pass_is_deterministic(self):
        columns = OrderedDict({
            "hospital": _independent_root_col_meta(),
            "rev": _gaussian_col_meta(100.0, 10.0),
        })
        # build_skeleton the categoricals once, then run measures twice.
        rng_setup = np.random.default_rng(0)
        hospital_arr = rng_setup.choice(
            np.array(["A", "B", "C"], dtype=object),
            size=500,
            p=[0.5, 0.3, 0.2],
        )
        rows_input = {"hospital": hospital_arr}
        topo_order = ["hospital", "rev"]
        a = generate_measures(
            columns, topo_order, dict(rows_input), np.random.default_rng(42),
        )
        b = generate_measures(
            columns, topo_order, dict(rows_input), np.random.default_rng(42),
        )
        np.testing.assert_array_equal(a["rev"], b["rev"])


class TestStagePhiDeterminism:
    """φ stage — pattern injection.

    Same df + same patterns + same RNG seed → identical post-injection df.
    Verifies inject_patterns does not introduce hidden RNG state.
    """

    def test_inject_patterns_outlier_is_deterministic(self):
        rng_setup = np.random.default_rng(0)
        df = pd.DataFrame({
            "hospital": ["A"] * 300 + ["B"] * 200,
            "cost": rng_setup.normal(100.0, 10.0, 500),
        })
        columns = {
            "hospital": {"type": "categorical", "group": "g1"},
            "cost": _gaussian_col_meta(100.0, 10.0),
        }
        patterns = [{
            "type": "outlier_entity",
            "target": "hospital == 'A'",
            "col": "cost",
            "params": {"z_score": 3.0},
        }]
        a = inject_patterns(df.copy(), patterns, columns, np.random.default_rng(42))
        b = inject_patterns(df.copy(), patterns, columns, np.random.default_rng(42))
        pd.testing.assert_frame_equal(a, b)


class TestStageRhoDeterminism:
    """ρ stage — realism injection (missing/dirty/censoring)."""

    def test_inject_realism_missing_is_deterministic(self):
        df = pd.DataFrame({
            "hospital": ["A", "B", "C"] * 100,
            "rev": np.arange(300, dtype=float),
        })
        columns = {
            "hospital": {"type": "categorical", "group": "g1"},
            "rev": {"type": "measure"},
        }
        cfg = {"missing_rate": 0.2, "dirty_rate": 0.0, "censoring": None}
        a = inject_realism(df.copy(), cfg, columns, np.random.default_rng(42))
        b = inject_realism(df.copy(), cfg, columns, np.random.default_rng(42))
        pd.testing.assert_frame_equal(a, b)


class TestRunPipelineEndToEndDeterminism:
    """Headline guarantee — `run_pipeline(seed=42)` is bit-for-bit
    reproducible across two unmocked invocations.

    This is the single most direct test of spec §2.5. No mocks.
    """

    def test_run_pipeline_with_seed_42_is_deterministic(self):
        columns = OrderedDict({
            "hospital": _independent_root_col_meta(),
            "rev": _gaussian_col_meta(100.0, 10.0),
        })
        groups = {
            "g1": DimensionGroup(
                name="g1",
                root="hospital",
                columns=["hospital"],
                hierarchy=["hospital"],
            ),
        }
        df_a, meta_a = run_pipeline(
            columns=columns,
            groups=groups,
            group_dependencies=[],
            measure_dag={},
            target_rows=500,
            seed=42,
        )
        df_b, meta_b = run_pipeline(
            columns=columns,
            groups=groups,
            group_dependencies=[],
            measure_dag={},
            target_rows=500,
            seed=42,
        )
        pd.testing.assert_frame_equal(df_a, df_b)
        # Metadata must also match — measure_dag_order, columns dict, etc.
        # use plain `==` since both come from the same builder.
        assert meta_a == meta_b

    def test_run_pipeline_different_seeds_produce_different_output(self):
        """Cross-check: with a different seed, byte-identical output would
        indicate the seed isn't actually wired through anywhere. This is the
        minimum sanity check for `default_rng(seed)` plumbing."""
        columns = OrderedDict({
            "hospital": _independent_root_col_meta(),
            "rev": _gaussian_col_meta(100.0, 10.0),
        })
        groups = {
            "g1": DimensionGroup(
                name="g1",
                root="hospital",
                columns=["hospital"],
                hierarchy=["hospital"],
            ),
        }
        df_a, _ = run_pipeline(
            columns=columns, groups=groups, group_dependencies=[],
            measure_dag={}, target_rows=500, seed=42,
        )
        df_b, _ = run_pipeline(
            columns=columns, groups=groups, group_dependencies=[],
            measure_dag={}, target_rows=500, seed=43,
        )
        # Float column with 500 samples: probability of byte-identical match
        # under different seeds is effectively zero.
        assert not df_a["rev"].equals(df_b["rev"])
