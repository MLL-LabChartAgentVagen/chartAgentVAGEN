"""Tests for Phase 2 measure generation — specifically the per-row
structural formula evaluation path and its ZeroDivisionError guard."""
from __future__ import annotations

import numpy as np
import pytest

from pipeline.phase_2.engine.measures import _eval_structural, _safe_eval_formula
from pipeline.phase_2.exceptions import InvalidParameterError


class TestSafeEvalFormula:
    """The low-level evaluator intentionally still raises raw ZeroDivisionError;
    the caller (_eval_structural) is the one that wraps it with row context."""

    def test_division_by_zero_raises_zero_division_at_primitive_level(self):
        with pytest.raises(ZeroDivisionError):
            _safe_eval_formula("a / b", {"a": 1.0, "b": 0.0})

    def test_normal_division_works(self):
        assert _safe_eval_formula("a / b", {"a": 6.0, "b": 2.0}) == 3.0


class TestEvalStructuralZeroDivisionGuard:
    def test_zero_denominator_raises_invalid_parameter_error_with_context(self):
        col_meta = {
            "formula": "profit / revenue",
            "effects": {},
            "noise": {},
        }
        rows = {
            "profit": np.array([10.0, 20.0, 30.0]),
            "revenue": np.array([5.0, 0.0, 10.0]),  # row 1 is the poison pill
        }
        rng = np.random.default_rng(0)

        with pytest.raises(InvalidParameterError) as exc:
            _eval_structural(
                col_name="profit_margin",
                col_meta=col_meta,
                rows=rows,
                rng=rng,
                columns={},  # no categorical effects, empty is fine
            )

        msg = str(exc.value)
        # Structured message carries everything the LLM needs to fix it
        assert "profit_margin" in msg
        assert "profit / revenue" in msg
        assert "row 1" in msg
        assert "revenue" in msg  # named as the zero-valued symbol
        assert "max(b, 1e-6)" in msg  # the hint

    def test_non_zero_denominators_succeed(self):
        col_meta = {
            "formula": "profit / revenue",
            "effects": {},
            "noise": {},
        }
        rows = {
            "profit": np.array([10.0, 20.0, 30.0]),
            "revenue": np.array([5.0, 4.0, 10.0]),
        }
        rng = np.random.default_rng(0)

        out = _eval_structural(
            col_name="profit_margin",
            col_meta=col_meta,
            rows=rows,
            rng=rng,
            columns={},
        )

        np.testing.assert_allclose(out, [2.0, 5.0, 3.0])

    def test_empty_rows_returns_empty_array(self):
        """Guard should not mask the existing n_rows==0 early exit."""
        col_meta = {"formula": "a / b", "effects": {}, "noise": {}}
        rng = np.random.default_rng(0)
        out = _eval_structural(
            col_name="x",
            col_meta=col_meta,
            rows={},
            rng=rng,
            columns={},
        )
        assert out.shape == (0,)
