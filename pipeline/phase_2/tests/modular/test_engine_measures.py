"""Tests for Phase 2 measure generation — covers:
  - The per-row structural-formula ZeroDivisionError guard.
  - The per-family stochastic-distribution param guard (prevents bare
    `ValueError: a <= 0` from numpy bubbling up to the LLM)."""
from __future__ import annotations

import numpy as np
import pytest

from pipeline.phase_2.engine.measures import (
    _eval_structural,
    _safe_eval_formula,
    _sample_stochastic,
)
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


# ---------------------------------------------------------------------------
# Stochastic-distribution param guard
# ---------------------------------------------------------------------------

def _stoch_meta(family: str, mu_intercept: float, sigma_intercept: float) -> dict:
    """Build a minimal stochastic col_meta with scalar intercept-only params."""
    return {
        "type": "measure",
        "measure_type": "stochastic",
        "family": family,
        "param_model": {
            "mu": {"intercept": mu_intercept},
            "sigma": {"intercept": sigma_intercept},
        },
    }


class TestDistributionParamGuards:
    def _rows(self, n: int = 3) -> dict:
        return {"_dummy": np.arange(n)}

    def test_beta_with_zero_mu_raises_invalid_parameter_error(self):
        col_meta = _stoch_meta("beta", mu_intercept=0.0, sigma_intercept=2.0)
        with pytest.raises(InvalidParameterError) as exc:
            _sample_stochastic(
                "accept_rate", col_meta, self._rows(), np.random.default_rng(0),
            )
        msg = str(exc.value)
        assert "accept_rate" in msg
        assert "beta" in msg
        assert "mu" in msg

    def test_gamma_with_zero_mu_raises_structured_error(self):
        col_meta = _stoch_meta("gamma", mu_intercept=0.0, sigma_intercept=2.0)
        with pytest.raises(InvalidParameterError) as exc:
            _sample_stochastic(
                "wait_time", col_meta, self._rows(), np.random.default_rng(0),
            )
        assert "gamma" in str(exc.value)
        assert "mu" in str(exc.value)

    def test_lognormal_with_zero_sigma_is_silently_clamped(self):
        """Lognormal sigma=0 is already handled by the existing P3-1 clamp in
        `_compute_per_row_params` (sigma -> max(sigma, 1e-6)); sampling
        succeeds with near-deterministic output. The distribution guard
        intentionally does not re-raise here to avoid contradicting the
        clamp."""
        col_meta = _stoch_meta("lognormal", mu_intercept=3.0, sigma_intercept=0.0)
        out = _sample_stochastic(
            "price", col_meta, self._rows(n=5), np.random.default_rng(0),
        )
        assert out.shape == (5,)
        assert np.all(np.isfinite(out))
        # With sigma clamped to 1e-6, all samples are nearly exp(3) ≈ 20.09
        np.testing.assert_allclose(out, np.full(5, np.exp(3.0)), rtol=1e-3)

    def test_poisson_with_negative_mu_raises_structured_error(self):
        col_meta = _stoch_meta("poisson", mu_intercept=-1.0, sigma_intercept=1.0)
        with pytest.raises(InvalidParameterError) as exc:
            _sample_stochastic(
                "count", col_meta, self._rows(), np.random.default_rng(0),
            )
        assert "poisson" in str(exc.value)
        assert "mu" in str(exc.value)

    def test_happy_path_beta_with_positive_params(self):
        """Regression: valid params pass the guard and produce samples in (0,1)."""
        col_meta = _stoch_meta("beta", mu_intercept=2.0, sigma_intercept=5.0)
        out = _sample_stochastic(
            "rate", col_meta, self._rows(n=10), np.random.default_rng(0),
        )
        assert out.shape == (10,)
        assert np.all((out > 0) & (out < 1))

    def test_gaussian_not_blocked_by_guard(self):
        """Gaussian has unrestricted mu and accepts sigma >= 0; guard must not fire."""
        col_meta = _stoch_meta("gaussian", mu_intercept=0.0, sigma_intercept=1.0)
        out = _sample_stochastic(
            "x", col_meta, self._rows(n=5), np.random.default_rng(0),
        )
        assert out.shape == (5,)


class TestSafeEvalFormulaSecurityPayloads:
    """Spec §2.1.1 + P0-2 (decisions/blocker_resolutions.md): formulas are
    parsed by a restricted AST walker. Allowed nodes: Expression, BinOp
    (+,-,*,/,**), UnaryOp (USub), Constant (numeric), Num, Name. Everything
    else must raise.

    Closes T1.7 in `docs/TEST_AUDIT_2026-05-07.md`. Pre-fix the only sandbox
    tests were `division_by_zero` and `normal_division`; classic AST escape
    payloads (`__import__`, `eval`, `open`, attribute chain, lambda, walrus,
    list comp, disallowed binops) were untested.
    """

    @pytest.mark.parametrize("formula", [
        "__import__('os').system('echo pwn')",
        "__import__('subprocess').call(['rm', '-rf', '/'])",
        "eval('1+1')",
        "exec('x=1')",
        "open('/etc/passwd')",
        "getattr(int, '__class__')",
    ])
    def test_call_payloads_rejected(self, formula):
        """Every Call node is rejected — covers __import__/eval/exec/open/getattr."""
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula(formula, {})

    def test_attribute_chain_subclass_escape_rejected(self):
        """Classic Python sandbox-escape: `().__class__.__bases__[0].__subclasses__()`
        relies on Attribute + Subscript + Call. Any of those three is enough
        to reject; the walker hits Tuple/Attribute first."""
        payload = "().__class__.__bases__[0].__subclasses__()"
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula(payload, {})

    def test_lambda_rejected(self):
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula("(lambda: 1)()", {})

    def test_list_comprehension_rejected(self):
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula("[i for i in range(10)]", {})

    def test_walrus_operator_rejected(self):
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula("(x := 5) + 1", {})

    def test_attribute_access_rejected(self):
        # Even a benign-looking `a.b` is rejected — there is no Attribute path
        # in the allow-list, so all attribute access is sealed off.
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula("a.b", {"a": 1.0})

    def test_subscript_rejected(self):
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula("a[0]", {"a": 1.0})

    def test_compare_node_rejected(self):
        # `a < b` is a Compare node, not whitelisted.
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula("a < b", {"a": 1.0, "b": 2.0})

    def test_boolop_rejected(self):
        with pytest.raises(ValueError, match="Disallowed AST node"):
            _safe_eval_formula("a and b", {"a": 1.0, "b": 1.0})

    def test_string_constant_rejected(self):
        # The walker accepts only numeric Constants; raw string literal must fail.
        with pytest.raises(ValueError, match="Non-numeric constant"):
            _safe_eval_formula("'malicious'", {})

    @pytest.mark.parametrize("op,formula", [
        ("FloorDiv", "a // b"),
        ("Mod",      "a % b"),
        ("BitOr",    "a | b"),
        ("BitAnd",   "a & b"),
        ("BitXor",   "a ^ b"),
        ("LShift",   "a << b"),
        ("RShift",   "a >> b"),
    ])
    def test_disallowed_binops_rejected(self, op, formula):
        """The allow-list permits only Add/Sub/Mult/Div/Pow. Every other
        BinOp variant must raise with the operator class name in the message."""
        with pytest.raises(ValueError, match=f"Disallowed binary operator: {op}"):
            _safe_eval_formula(formula, {"a": 4.0, "b": 2.0})

    def test_unary_not_rejected(self):
        # Only USub is allowed; UAdd/Not/Invert must fail.
        with pytest.raises(ValueError, match="Disallowed unary operator"):
            _safe_eval_formula("not a", {"a": 1.0})

    def test_undefined_symbol_named_in_error(self):
        # When a symbol like `eval` is referenced as a Name (no Call yet),
        # resolution fails before any execution. Verifies error message
        # surfaces the symbol name rather than executing it.
        with pytest.raises(ValueError, match="Undefined symbol 'evil'"):
            _safe_eval_formula("evil + 1", {"a": 1.0})

    def test_allowed_arithmetic_still_works(self):
        """Regression guard: tightening the allow-list must not break the
        spec-blessed arithmetic core (+,-,*,/,**, unary -, parens)."""
        ctx = {"a": 4.0, "b": 2.0, "c": 3.0}
        assert _safe_eval_formula("a + b * c", ctx) == 10.0
        assert _safe_eval_formula("(a - b) ** c", ctx) == 8.0
        assert _safe_eval_formula("-a + b", ctx) == -2.0
