"""Tests for check_convergence (IS-3)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.phase_2.validation.pattern_checks import check_convergence


HOSPITALS = ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"]


def _meta_with_entity_and_time() -> dict:
    return {
        "dimension_groups": {
            "entity": {"columns": ["hospital"], "hierarchy": ["hospital"]},
            "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        }
    }


def _build_df(early_means: list[float], late_means: list[float]) -> pd.DataFrame:
    """Per-hospital rows split across an early period and a late period.

    early_means[i] / late_means[i] control hospital i's mean on each side.
    The list length determines how many hospitals appear; per-row noise is
    small (σ=0.1) so per-entity sample means stay close to their target.
    """
    if len(early_means) != len(late_means):
        raise ValueError("early_means and late_means must have same length")

    rng = np.random.default_rng(0)
    rows = []
    pre_dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    post_dates = pd.date_range("2024-07-01", "2024-09-30", freq="D")

    hospitals = HOSPITALS[: len(early_means)]
    for i, h in enumerate(hospitals):
        for d in pre_dates[:30]:
            rows.append(
                {"hospital": h, "visit_date": d,
                 "value": early_means[i] + rng.normal(0, 0.1)}
            )
        for d in post_dates[:30]:
            rows.append(
                {"hospital": h, "visit_date": d,
                 "value": late_means[i] + rng.normal(0, 0.1)}
            )
    return pd.DataFrame(rows)


def _pattern(**overrides) -> dict:
    p = {
        "type": "convergence",
        "target": "value == value",  # all rows
        "col": "value",
        "params": {},
    }
    p["params"].update(overrides)
    return p


class TestCheckConvergence:
    def test_convergence_passes_when_late_means_uniform(self):
        # Early spread {2, 5, 8, 11} → high inter-group variance.
        # Late means all 6.5 → ~zero inter-group variance. reduction ≈ 1.0.
        df = _build_df(
            early_means=[2.0, 5.0, 8.0, 11.0],
            late_means=[6.5, 6.5, 6.5, 6.5],
        )
        result = check_convergence(df, _pattern(), _meta_with_entity_and_time())
        assert result.passed is True
        assert "reduction=" in result.detail

    def test_stable_spread_fails(self):
        # Same spread on both sides → reduction ≈ 0 → fails threshold 0.3.
        df = _build_df(
            early_means=[2.0, 5.0, 8.0, 11.0],
            late_means=[2.0, 5.0, 8.0, 11.0],
        )
        result = check_convergence(df, _pattern(), _meta_with_entity_and_time())
        assert result.passed is False

    def test_single_entity_graceful_fail(self):
        # Only one entity → groupby produces a 1-element series on each
        # side → check should bail out gracefully.
        df = _build_df(early_means=[5.0], late_means=[5.0])
        result = check_convergence(df, _pattern(), _meta_with_entity_and_time())
        assert result.passed is False
        assert "Need >=2 entities" in result.detail

    def test_missing_temporal_column_graceful_fail(self):
        df = _build_df(
            early_means=[2.0, 5.0, 8.0, 11.0],
            late_means=[6.5, 6.5, 6.5, 6.5],
        )
        meta = {
            "dimension_groups": {
                "entity": {
                    "columns": ["hospital"], "hierarchy": ["hospital"],
                },
            }  # no "time" group
        }
        result = check_convergence(df, _pattern(), meta)
        assert result.passed is False
        assert "temporal_col" in result.detail

    def test_constant_column_early_var_zero_graceful_fail(self):
        # All entities at exactly the same value on the early side →
        # early per-entity means are identical → early_var = 0 →
        # reduction undefined → graceful fail. Build noise-free DF so the
        # zero-variance branch is exercised directly (the parametric
        # _build_df adds σ=0.1 jitter that hides this branch).
        pre_dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
        post_dates = pd.date_range("2024-07-01", "2024-09-30", freq="D")
        rows = []
        for h in HOSPITALS[:4]:
            for d in pre_dates[:30]:
                rows.append({"hospital": h, "visit_date": d, "value": 5.0})
            for d in post_dates[:30]:
                rows.append({"hospital": h, "visit_date": d, "value": 5.0})
        df = pd.DataFrame(rows)
        result = check_convergence(df, _pattern(), _meta_with_entity_and_time())
        assert result.passed is False
        assert "Early-period inter-group variance" in result.detail

    def test_custom_split_point_used(self):
        df = _build_df(
            early_means=[2.0, 5.0, 8.0, 11.0],
            late_means=[6.5, 6.5, 6.5, 6.5],
        )
        # Split between the two periods (post starts 2024-07-01).
        pattern = _pattern(split_point="2024-04-15")
        result = check_convergence(df, pattern, _meta_with_entity_and_time())
        assert result.passed is True

    def test_custom_reduction_threshold_blocks_pass(self):
        # ~50% reduction: passes 0.3 threshold but fails 0.95.
        df = _build_df(
            early_means=[2.0, 5.0, 8.0, 11.0],
            late_means=[3.5, 5.0, 6.5, 8.0],
        )
        permissive = check_convergence(
            df, _pattern(reduction=0.3), _meta_with_entity_and_time()
        )
        strict = check_convergence(
            df, _pattern(reduction=0.95), _meta_with_entity_and_time()
        )
        assert permissive.passed is True
        assert strict.passed is False

    def test_entity_col_fallback_uses_first_dim_root(self):
        # No entity_col in params — meta's first dim group is "entity"
        # whose hierarchy root is "hospital" → should resolve.
        df = _build_df(
            early_means=[2.0, 5.0, 8.0, 11.0],
            late_means=[6.5, 6.5, 6.5, 6.5],
        )
        result = check_convergence(df, _pattern(), _meta_with_entity_and_time())
        assert result.passed is True

    # ---------------------------------------------------------------------
    # T2.2 of TEST_AUDIT_2026-05-07.md — boundary cases.
    #
    # Pre-existing tests cover (a) full convergence (reduction ≈ 1.0) and
    # (b) stable spread (reduction ≈ 0). They never test:
    #  - DIVERGENCE: late variance > early variance → reduction is NEGATIVE
    #    → must fail any positive threshold.
    #  - Threshold boundary: reduction *exactly* at the threshold → must
    #    pass under `>=` semantics.
    # ---------------------------------------------------------------------

    def test_divergence_negative_reduction_fails(self):
        """Late means more spread than early means → reduction < 0 →
        must fail the default threshold of 0.3 with a reported negative
        reduction."""
        df = _build_df(
            early_means=[6.5, 6.5, 6.5, 6.5],   # zero spread early
            late_means=[2.0, 5.0, 8.0, 11.0],   # large spread late
        )
        result = check_convergence(df, _pattern(), _meta_with_entity_and_time())
        assert result.passed is False
        # The validator's early_var=0 path triggers a graceful "undefined"
        # fail rather than a negative reduction; the audit's intent —
        # "spread WIDENED → don't claim convergence" — is satisfied either
        # way. Verify the failure mode reported is one of the two.
        assert (
            "reduction undefined" in result.detail
            or "reduction=-" in result.detail
        )

    def test_divergence_with_nonzero_early_var_yields_negative_reduction(self):
        """When early_var > 0 but late_var > early_var, the formula
        `(early - late)/early` is negative — exercise the explicit
        negative-reduction branch (avoids the early_var=0 short-circuit)."""
        df = _build_df(
            early_means=[5.0, 6.0, 7.0, 8.0],   # small spread early (var≈1.67)
            late_means=[1.0, 5.0, 10.0, 14.0],  # larger spread late
        )
        result = check_convergence(df, _pattern(), _meta_with_entity_and_time())
        assert result.passed is False
        assert "reduction=-" in result.detail, (
            f"Expected negative reduction, got: {result.detail}"
        )

    def test_threshold_boundary_at_exact_equality(self):
        """Pin `>=` (not `>`) at the boundary. The validator computes
        `reduction = (early_var - late_var) / early_var` and gates on
        `reduction >= threshold` (pattern_checks.py:393-394). This test
        replicates the validator's arithmetic in-test to obtain the
        bit-identical float, then feeds that exact float as the threshold.
        At `threshold == actual_reduction`, `>=` passes but `>` would not
        — so a refactor that flipped the operator would flip this assertion.

        Replaces the prior `test_threshold_boundary_inequality_is_inclusive`
        which only probed strictly-below vs strictly-above (and so tolerated
        an erroneous `>` regression).
        """
        df = _build_df(
            early_means=[2.0, 5.0, 8.0, 11.0],
            late_means=[6.0, 6.5, 6.5, 7.0],
        )

        # Reproduce the validator's reduction calculation. Must use the
        # same per-entity means + the same `pd.Series.var()` (default
        # ddof=1) so the float is bit-identical to the validator's.
        # An explicit split_point is passed below so the validator and
        # this test agree on which rows fall on which side.
        split = pd.Timestamp("2024-04-15")
        pre_means = (
            df[df["visit_date"] < split]
            .groupby("hospital")["value"].mean()
        )
        post_means = (
            df[df["visit_date"] >= split]
            .groupby("hospital")["value"].mean()
        )
        early_var = float(pre_means.var())
        late_var = float(post_means.var())
        expected_reduction = (early_var - late_var) / early_var

        # threshold == actual reduction → must PASS under `>=`.
        # A regression that flipped `>=` to `>` would trip exactly here.
        eq = check_convergence(
            df,
            _pattern(reduction=expected_reduction, split_point="2024-04-15"),
            _meta_with_entity_and_time(),
        )
        assert eq.passed is True, (
            f"reduction={expected_reduction!r} should satisfy "
            f"`>= threshold={expected_reduction!r}`; got {eq.detail}. "
            f"This assertion is the `>=` vs `>` regression guard."
        )

        # threshold = reduction + tiny epsilon → must FAIL (strict-side guard).
        # Confirms we're not just matching everything; the comparison is
        # active and the boundary is real.
        above = check_convergence(
            df,
            _pattern(
                reduction=expected_reduction + 1e-9,
                split_point="2024-04-15",
            ),
            _meta_with_entity_and_time(),
        )
        assert above.passed is False, (
            f"reduction={expected_reduction!r} < threshold="
            f"{expected_reduction + 1e-9!r} must fail; got {above.detail}"
        )
