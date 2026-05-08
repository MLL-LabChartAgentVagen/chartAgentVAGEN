"""Tests for Phase 2 realism injection — covers ``inject_censoring``,
the ordering inside ``inject_realism``, and the schema validation that
``set_realism`` performs on the censoring config (DS-1)."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import pytest

from pipeline.phase_2.engine.realism import inject_censoring, inject_realism
from pipeline.phase_2.sdk.relationships import set_realism


class TestInjectCensoring:
    def test_right_censoring_masks_above_threshold(self):
        df = pd.DataFrame({"x": [10.0, 20.0, 30.0, 40.0, 50.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df, {"x": {"type": "right", "threshold": 25.0}}, rng,
        )

        assert result["x"].isna().tolist() == [False, False, True, True, True]
        assert result["x"].iloc[0] == 10.0
        assert result["x"].iloc[1] == 20.0

    def test_left_censoring_masks_below_threshold(self):
        df = pd.DataFrame({"x": [10.0, 20.0, 30.0, 40.0, 50.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df, {"x": {"type": "left", "threshold": 25.0}}, rng,
        )

        assert result["x"].isna().tolist() == [True, True, False, False, False]
        assert result["x"].iloc[2] == 30.0
        assert result["x"].iloc[4] == 50.0

    def test_interval_censoring_masks_out_of_range(self):
        df = pd.DataFrame({"x": [-1.0, 0.0, 5.0, 10.0, 11.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df, {"x": {"type": "interval", "low": 0.0, "high": 10.0}}, rng,
        )

        # Endpoints (0.0 and 10.0) are inside the interval; only -1 and 11 NaN.
        assert result["x"].isna().tolist() == [True, False, False, False, True]
        assert result["x"].iloc[1] == 0.0
        assert result["x"].iloc[3] == 10.0

    def test_missing_column_warns_and_skips(self, caplog):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        rng = np.random.default_rng(0)

        with caplog.at_level(logging.WARNING, logger="pipeline.phase_2.engine.realism"):
            result = inject_censoring(
                df, {"missing_col": {"type": "right", "threshold": 0.0}}, rng,
            )

        assert result["x"].isna().sum() == 0
        assert any(
            "missing_col" in rec.message and "skipping" in rec.message
            for rec in caplog.records
        )

    def test_empty_config_is_noop(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        rng = np.random.default_rng(0)

        result = inject_censoring(df, {}, rng)

        pd.testing.assert_frame_equal(result, df)

    def test_unknown_type_raises(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
        rng = np.random.default_rng(0)

        with pytest.raises(ValueError, match="Unknown censoring type"):
            inject_censoring(
                df, {"x": {"type": "bogus", "threshold": 0.0}}, rng,
            )

    def test_multiple_columns_independently_censored(self):
        df = pd.DataFrame({
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [10.0, 20.0, 30.0, 40.0],
            "c": [-5.0, 0.0, 5.0, 50.0],
        })
        rng = np.random.default_rng(0)

        result = inject_censoring(
            df,
            {
                "a": {"type": "right", "threshold": 2.5},
                "b": {"type": "left", "threshold": 25.0},
                "c": {"type": "interval", "low": 0.0, "high": 10.0},
            },
            rng,
        )

        assert result["a"].isna().tolist() == [False, False, True, True]
        assert result["b"].isna().tolist() == [True, True, False, False]
        assert result["c"].isna().tolist() == [True, False, False, True]


class TestInjectRealismOrdering:
    def test_censoring_runs_before_missing(self):
        """With missing_rate=0, censoring still applies via inject_realism."""
        df = pd.DataFrame({"x": [10.0, 20.0, 30.0, 40.0, 50.0]})
        rng = np.random.default_rng(0)

        result = inject_realism(
            df,
            {
                "censoring": {"x": {"type": "right", "threshold": 25.0}},
                "missing_rate": 0.0,
                "dirty_rate": 0.0,
            },
            columns={},
            rng=rng,
        )

        # Cells 30, 40, 50 should be NaN; cells 10, 20 untouched.
        assert result["x"].isna().sum() == 3
        assert result["x"].iloc[0] == 10.0
        assert result["x"].iloc[1] == 20.0

    def test_censoring_visible_through_missing_pipeline(self):
        """All values exceed the right-censor threshold, so all cells in
        the censored column are NaN regardless of missing_rate.  Verifies
        censoring ran first (otherwise some cells could survive the
        post-censor distribution and stay non-NaN with rate 0.0).
        """
        df = pd.DataFrame({"x": [100.0] * 50})
        rng = np.random.default_rng(0)

        result = inject_realism(
            df,
            {
                "censoring": {"x": {"type": "right", "threshold": 50.0}},
                "missing_rate": 0.5,
                "dirty_rate": 0.0,
            },
            columns={},
            rng=rng,
        )

        # Censoring NaN'd every cell; df.mask over already-NaN is still NaN.
        assert result["x"].isna().sum() == 50

    def test_no_censoring_key_is_backward_compatible(self):
        """Configs without a censoring key continue to behave as before."""
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 5.0]})
        rng = np.random.default_rng(0)

        result = inject_realism(
            df,
            {"missing_rate": 0.0, "dirty_rate": 0.0},
            columns={},
            rng=rng,
        )

        pd.testing.assert_frame_equal(result, df)


class TestSetRealismCensoringValidation:
    def test_accepts_valid_right_spec(self):
        cfg = set_realism(
            [],
            missing_rate=0.0,
            dirty_rate=0.0,
            censoring={"x": {"type": "right", "threshold": 5.0}},
        )
        assert cfg["censoring"] == {"x": {"type": "right", "threshold": 5.0}}

    def test_accepts_valid_left_spec(self):
        cfg = set_realism(
            [],
            censoring={"x": {"type": "left", "threshold": 5.0}},
        )
        assert cfg["censoring"]["x"]["type"] == "left"

    def test_accepts_valid_interval_spec(self):
        cfg = set_realism(
            [],
            censoring={"x": {"type": "interval", "low": 0.0, "high": 10.0}},
        )
        assert cfg["censoring"]["x"]["high"] == 10.0

    def test_rejects_non_dict_censoring(self):
        with pytest.raises(ValueError, match="must be a dict"):
            set_realism([], censoring=[("x", "right")])  # type: ignore[arg-type]

    def test_rejects_non_dict_per_column_spec(self):
        with pytest.raises(ValueError, match="must be a dict"):
            set_realism([], censoring={"x": "right"})  # type: ignore[dict-item]

    def test_rejects_missing_type_key(self):
        with pytest.raises(ValueError, match="missing required key 'type'"):
            set_realism([], censoring={"x": {"threshold": 5.0}})

    def test_rejects_unknown_type(self):
        with pytest.raises(ValueError, match="must be one of"):
            set_realism([], censoring={"x": {"type": "bogus"}})

    def test_rejects_right_without_threshold(self):
        with pytest.raises(ValueError, match="requires 'threshold'"):
            set_realism([], censoring={"x": {"type": "right"}})

    def test_rejects_left_without_threshold(self):
        with pytest.raises(ValueError, match="requires 'threshold'"):
            set_realism([], censoring={"x": {"type": "left"}})

    def test_rejects_interval_without_bounds(self):
        with pytest.raises(ValueError, match="requires both 'low' and 'high'"):
            set_realism([], censoring={"x": {"type": "interval", "low": 0.0}})


class TestSetRealismRateBounds:
    """Spec §2.1.1 — `set_realism` enforces rate bounds. Verified at the SDK
    layer (`relationships.py:300-307`).

    Closes the rate-boundary half of T1.10 in `docs/TEST_AUDIT_2026-05-07.md`.
    """

    def test_rejects_missing_rate_above_one(self):
        with pytest.raises(ValueError, match="missing_rate must be in"):
            set_realism([], missing_rate=1.5)

    def test_rejects_negative_missing_rate(self):
        with pytest.raises(ValueError, match="missing_rate must be in"):
            set_realism([], missing_rate=-0.1)

    def test_rejects_dirty_rate_above_one(self):
        with pytest.raises(ValueError, match="dirty_rate must be in"):
            set_realism([], dirty_rate=2.0)

    def test_accepts_rate_at_zero_boundary(self):
        cfg = set_realism([], missing_rate=0.0, dirty_rate=0.0)
        assert cfg["missing_rate"] == 0.0
        assert cfg["dirty_rate"] == 0.0

    def test_accepts_rate_at_one_boundary(self):
        # Spec allows rate==1.0 inclusive; the engine then nulls every cell.
        cfg = set_realism([], missing_rate=1.0)
        assert cfg["missing_rate"] == 1.0


class TestInjectMissingValuesBoundary:
    """The boundary-rate behavior of `inject_missing_values` is what users
    will see when an LLM script declares `missing_rate=1.0`. Lock it down
    so a future change to the masking logic (e.g., off-by-one with `< vs <=`)
    is caught."""

    def test_missing_rate_one_nulls_substantially_all_cells(self):
        # rng.random returns values in [0, 1); `< 1.0` is True for every
        # draw, so the mask is all-True and every cell becomes NaN.
        from pipeline.phase_2.engine.realism import inject_missing_values
        df = pd.DataFrame({
            "hospital": ["A", "B", "C"] * 50,
            "revenue": np.arange(150, dtype=float),
        })
        rng = np.random.default_rng(0)
        out = inject_missing_values(df.copy(), missing_rate=1.0, rng=rng)
        assert out["revenue"].isna().all()
        # `hospital` is object-typed; pandas mask sets to NaN equivalently.
        assert out["hospital"].isna().all()

    def test_missing_rate_zero_is_a_noop(self):
        from pipeline.phase_2.engine.realism import inject_missing_values
        df = pd.DataFrame({
            "revenue": np.arange(100, dtype=float),
        })
        rng = np.random.default_rng(0)
        out = inject_missing_values(df.copy(), missing_rate=0.0, rng=rng)
        assert out["revenue"].isna().sum() == 0
        np.testing.assert_array_equal(out["revenue"].values, df["revenue"].values)


class TestPrimaryKeyProtection:
    """Spec §2.1.1 — *"set_realism protects primary key"*.

    `inject_realism` computes the categorical-root set
    (`_primary_key_columns`) and forwards it to `inject_missing_values`
    as `protected_columns`, ensuring those cells are never NaN'd
    regardless of `missing_rate`. Resolved 2026-05-07; was previously
    xfail-marked while tracked in `docs/remaining_gaps.md` §4.1.

    Out of scope (separate spec violation): `inject_dirty_values` can
    still string-perturb a PK at `dirty_rate>0`. Tracked for a future
    round; the resolution note in `remaining_gaps.md` documents it.
    """

    def test_primary_key_categorical_root_never_nulled_at_rate_one(self):
        from pipeline.phase_2.engine.realism import inject_realism
        df = pd.DataFrame({
            "hospital": ["A", "B", "C"] * 50,   # categorical root → spec PK
            "revenue": np.arange(150, dtype=float),
        })
        columns = {
            "hospital": {"type": "categorical", "parent": None, "group": "g1"},
            "revenue":  {"type": "measure"},
        }
        rng = np.random.default_rng(0)
        out = inject_realism(
            df.copy(),
            {"missing_rate": 1.0, "dirty_rate": 0.0, "censoring": None},
            columns,
            rng,
        )
        # SPEC promise: PK column is untouched even at extreme rate.
        assert out["hospital"].isna().sum() == 0, \
            "Spec §2.1.1: set_realism must protect the primary key column"
        # Measure should be fully nulled at rate=1.0.
        assert out["revenue"].isna().sum() == 150

    def test_primary_key_protected_at_intermediate_rate(self):
        """At missing_rate=0.5 the measure column has ~50% NaN, but the
        categorical root stays at exactly 0 NaN. Catches a regression
        where the protection only fires at the extreme rate=1.0."""
        from pipeline.phase_2.engine.realism import inject_realism
        df = pd.DataFrame({
            "hospital": ["A", "B", "C"] * 100,
            "revenue": np.arange(300, dtype=float),
        })
        columns = {
            "hospital": {"type": "categorical", "parent": None, "group": "g1"},
            "revenue":  {"type": "measure"},
        }
        rng = np.random.default_rng(0)
        out = inject_realism(
            df.copy(),
            {"missing_rate": 0.5, "dirty_rate": 0.0, "censoring": None},
            columns,
            rng,
        )
        assert out["hospital"].isna().sum() == 0, (
            f"PK column should never be nulled; got "
            f"{out['hospital'].isna().sum()} NaN out of {len(out)}"
        )
        # Measure should be masked at roughly the declared rate.
        # Binomial 95% CI on 300 trials at p=0.5 is ~150 ± 17.
        rev_nans = int(out["revenue"].isna().sum())
        assert 110 < rev_nans < 190, (
            f"measure NaN count {rev_nans} far from expected ~150"
        )

    def test_child_categorical_NOT_protected(self):
        """Only categorical ROOTS are PKs. A categorical with a `parent`
        (e.g., department under hospital) is a drill-down, not an identity
        column — it gets the normal missing rate treatment."""
        from pipeline.phase_2.engine.realism import inject_realism
        df = pd.DataFrame({
            "hospital":   ["A", "B"] * 100,
            "department": ["Internal", "Surgery"] * 100,
            "revenue":    np.arange(200, dtype=float),
        })
        columns = {
            "hospital":   {"type": "categorical", "parent": None,       "group": "g1"},
            "department": {"type": "categorical", "parent": "hospital", "group": "g1"},
            "revenue":    {"type": "measure"},
        }
        rng = np.random.default_rng(0)
        out = inject_realism(
            df.copy(),
            {"missing_rate": 1.0, "dirty_rate": 0.0, "censoring": None},
            columns,
            rng,
        )
        # Only the root is protected; the child is fully NaN'd at rate=1.0.
        assert out["hospital"].isna().sum() == 0
        assert out["department"].isna().all()
        assert out["revenue"].isna().all()

    def test_multiple_group_roots_all_protected(self):
        """With three groups, all three roots are protected
        simultaneously."""
        from pipeline.phase_2.engine.realism import inject_realism
        df = pd.DataFrame({
            "hospital":  ["A", "B", "C"] * 50,
            "severity":  ["Mild", "Severe"] * 75,
            "payment":   ["Cash", "Card"] * 75,
            "revenue":   np.arange(150, dtype=float),
        })
        columns = {
            "hospital": {"type": "categorical", "parent": None, "group": "g1"},
            "severity": {"type": "categorical", "parent": None, "group": "g2"},
            "payment":  {"type": "categorical", "parent": None, "group": "g3"},
            "revenue":  {"type": "measure"},
        }
        rng = np.random.default_rng(0)
        out = inject_realism(
            df.copy(),
            {"missing_rate": 1.0, "dirty_rate": 0.0, "censoring": None},
            columns,
            rng,
        )
        assert out["hospital"].isna().sum() == 0
        assert out["severity"].isna().sum() == 0
        assert out["payment"].isna().sum() == 0
        assert out["revenue"].isna().all()

    def test_inject_missing_values_direct_no_protection_default(self):
        """Calling `inject_missing_values` directly without
        `protected_columns` preserves the pre-fix all-cells-masked
        behaviour — the boundary test at line 258 depends on this."""
        from pipeline.phase_2.engine.realism import inject_missing_values
        df = pd.DataFrame({
            "hospital": ["A", "B"] * 50,
            "revenue":  np.arange(100, dtype=float),
        })
        rng = np.random.default_rng(0)
        out = inject_missing_values(df.copy(), missing_rate=1.0, rng=rng)
        assert out["hospital"].isna().all()
        assert out["revenue"].isna().all()
