"""Standalone test runner for Sprint 7 validator tests (post self-review).

Runs all contract-table scenarios and key validation paths using plain
assert statements. Fixes applied from self-review:
  - [item 1] ddof=1: outlier Row 3 uses N=81 (was 80); hand-calc z=0.9487
  - [item 2] trend_break no target filtering: Row 6 removed (N/A)
  - [item 3] break_point at top level: trend patterns use top-level key
"""
from __future__ import annotations

import copy
import sys
import traceback
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/claude")

from agpds.exceptions import InvalidParameterError, PatternInjectionError
from agpds.validator import (
    Check,
    ValidationReport,
    amplify_magnitude,
    check_outlier_entity,
    check_trend_break,
    check_row_count,
    match_strategy,
    max_conditional_deviation,
    reshuffle_pair,
    widen_variance,
)


# ===== Test Harness =====

_passed = 0
_failed = 0
_errors: list[str] = []


def run_test(name: str, fn) -> None:
    global _passed, _failed
    try:
        fn()
        _passed += 1
        print(f"  \u2713 {name}")
    except AssertionError as e:
        _failed += 1
        _errors.append(f"FAIL: {name} \u2014 {e}")
        print(f"  \u2717 {name} \u2014 {e}")
    except Exception as e:
        _failed += 1
        _errors.append(f"ERROR: {name} \u2014 {type(e).__name__}: {e}")
        print(f"  \u2717 {name} \u2014 {type(e).__name__}: {e}")
        traceback.print_exc(limit=2)


def approx(a: float, b: float, tol: float = 1e-4) -> bool:
    return abs(a - b) < tol


# ===== Fixtures =====

META_WITH_TIME: dict[str, Any] = {
    "dimension_groups": {
        "time": {"columns": ["visit_date"], "hierarchy": ["visit_date"]},
        "entity": {"columns": ["hospital"], "hierarchy": ["hospital"]},
    },
    "total_rows": 500,
}

OUTLIER_PATTERN: dict[str, Any] = {
    "type": "outlier_entity",
    "target": "hospital == 'Xiehe' & severity == 'Severe'",
    "col": "wait_minutes",
    "params": {"z_score": 3.0},
}


def _make_check(name="test_check", passed=False):
    return Check(name=name, passed=passed, detail="test")


# =====================================================================
# check_outlier_entity [8.4.1] — Contract rows 1-12
# =====================================================================

def test_outlier_row1_happy_pass():
    """[8.4.1] Row 1: z=2.5 -> passes.
    z(ddof=1) = sqrt(N*(S-1)/(M*S)). N=125,M=20,S=145 -> z=2.491.
    """
    df = pd.DataFrame({
        "hospital": ["Xiehe"] * 20 + ["B"] * 125,
        "severity": ["Severe"] * 20 + ["Mild"] * 125,
        "wait_minutes": [200.0] * 20 + [100.0] * 125,
    })
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert result.passed is True, f"detail: {result.detail}"


def test_outlier_row2_happy_fail():
    """[8.4.1] Row 2: z=1.5 -> fails. N=45,M=20 -> z=1.488."""
    df = pd.DataFrame({
        "hospital": ["Xiehe"] * 20 + ["B"] * 45,
        "severity": ["Severe"] * 20 + ["Mild"] * 45,
        "wait_minutes": [200.0] * 20 + [100.0] * 45,
    })
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert result.passed is False


# FIX: [self-review item 1] — N changed from 80 to 81 because ddof=1
# shifts the boundary: z(N=80,M=20,ddof=1) = 1.990 < 2.0.
# With N=81: z(ddof=1) = 2.0025 >= 2.0.
def test_outlier_row3_boundary_z_exactly_2():
    """[8.4.1] Row 3: z>=2.0 boundary -> passes. N=81,M=20 -> z=2.0025."""
    df = pd.DataFrame({
        "hospital": ["Xiehe"] * 20 + ["B"] * 81,
        "severity": ["Severe"] * 20 + ["Mild"] * 81,
        "wait_minutes": [200.0] * 20 + [100.0] * 81,
    })
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert result.passed is True, f"detail: {result.detail}"


def test_outlier_row4_boundary_z_below_2():
    """[8.4.1] Row 4: z<2.0 -> fails. N=79,M=20 -> z=1.977."""
    df = pd.DataFrame({
        "hospital": ["Xiehe"] * 20 + ["B"] * 79,
        "severity": ["Severe"] * 20 + ["Mild"] * 79,
        "wait_minutes": [200.0] * 20 + [100.0] * 79,
    })
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert result.passed is False


def test_outlier_row5_zero_std():
    """[8.4.1] Row 5: constant column -> fails."""
    df = pd.DataFrame({
        "hospital": ["Xiehe"] * 5 + ["B"] * 5,
        "severity": ["Severe"] * 5 + ["Mild"] * 5,
        "wait_minutes": [100.0] * 10,
    })
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert result.passed is False


def test_outlier_row6_single_target_row():
    """[8.4.1] Row 6: 1 row matches -> Check computed."""
    df = pd.DataFrame({
        "hospital": ["Xiehe"] + ["B"] * 99,
        "severity": ["Severe"] + ["Mild"] * 99,
        "wait_minutes": [300.0] + [100.0] * 99,
    })
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert isinstance(result, Check)
    assert result.name == "outlier_wait_minutes"


def test_outlier_row7_missing_target_key():
    """[8.4.1] Row 7: missing 'target' -> KeyError."""
    df = pd.DataFrame({"wait_minutes": [100.0] * 10})
    try:
        check_outlier_entity(df, {"col": "wait_minutes", "params": {"z_score": 3.0}})
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_outlier_row8_missing_col_key():
    """[8.4.1] Row 8: missing 'col' -> KeyError."""
    df = pd.DataFrame({"wait_minutes": [100.0] * 10, "hospital": ["A"] * 10})
    try:
        check_outlier_entity(df, {"target": "hospital == 'A'", "params": {"z_score": 3.0}})
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_outlier_row9_missing_z_score():
    """[8.4.1] Row 9: missing z_score -> KeyError."""
    df = pd.DataFrame({"wait_minutes": [100.0] * 10, "hospital": ["A"] * 10})
    try:
        check_outlier_entity(df, {"target": "hospital == 'A'", "col": "wait_minutes", "params": {}})
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_outlier_row10_col_not_in_df():
    """[8.4.1] Row 10: col='nonexistent' -> KeyError."""
    df = pd.DataFrame({"hospital": ["A"] * 10, "wait_minutes": [100.0] * 10})
    try:
        check_outlier_entity(df, {"target": "hospital == 'A'", "col": "nonexistent", "params": {"z_score": 3.0}})
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_outlier_row11_zero_match():
    """[8.4.1] Row 11: target matches nothing -> Check(passed=False)."""
    df = pd.DataFrame({"hospital": ["B"] * 10, "severity": ["Mild"] * 10, "wait_minutes": [100.0] * 10})
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert result.passed is False
    assert "zero rows" in result.detail.lower()


def test_outlier_row12_done_condition():
    """[8.4.1] Row 12 / Done: z=2.5 -> passes."""
    test_outlier_row1_happy_pass()


# FIX: [self-review item 1] — z changes from 1.0000 to 0.9487 with ddof=1
def test_outlier_hand_calculated_z():
    """[8.4.1] Output: hand-calculated z with ddof=1.
    5 at 50 + 5 at 100: mean=75, std(ddof=1)=26.3523, z=25/26.3523=0.9487.
    """
    df = pd.DataFrame({"group": ["A"] * 5 + ["B"] * 5, "val": [50.0] * 5 + [100.0] * 5})
    pattern = {"target": "group == 'A'", "col": "val", "params": {"z_score": 2.0}}
    result = check_outlier_entity(df, pattern)
    assert result.passed is False
    assert "z=0.9487" in result.detail, f"Expected z=0.9487, got: {result.detail}"


def test_outlier_return_type():
    """[8.4.1] Output: returns Check."""
    df = pd.DataFrame({"hospital": ["Xiehe"] * 20 + ["B"] * 80,
                        "severity": ["Severe"] * 20 + ["Mild"] * 80,
                        "wait_minutes": [200.0] * 20 + [100.0] * 80})
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert isinstance(result, Check)


def test_outlier_passed_is_python_bool():
    """[8.4.1] Output: passed is native bool."""
    df = pd.DataFrame({"hospital": ["Xiehe"] * 20 + ["B"] * 80,
                        "severity": ["Severe"] * 20 + ["Mild"] * 80,
                        "wait_minutes": [200.0] * 20 + [100.0] * 80})
    result = check_outlier_entity(df, OUTLIER_PATTERN)
    assert type(result.passed) is bool


# =====================================================================
# check_trend_break [8.4.3] — Contract rows 1-12
# FIX: [self-review item 2] — Tests use full-df semantics (no target filter)
# FIX: [self-review item 3] — Patterns use top-level "break_point"
# =====================================================================

def test_trend_row1_happy_pass():
    """[8.4.3] Row 1: 25% shift -> passes. before=100, after=125."""
    df = pd.DataFrame({
        "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                       + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
        "wait_minutes": [100.0] * 5 + [125.0] * 5,
    })
    # FIX: [self-review item 3] — Top-level break_point per §2.6 metadata
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15",
               "params": {"magnitude": 0.4}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is True
    assert result.name == "trend_wait_minutes"


def test_trend_row2_happy_fail():
    """[8.4.3] Row 2: 10% shift -> fails. before=100, after=110."""
    df = pd.DataFrame({
        "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                       + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
        "wait_minutes": [100.0] * 5 + [110.0] * 5,
    })
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15",
               "params": {"magnitude": 0.1}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is False


def test_trend_row3_boundary_exactly_15():
    """[8.4.3] Row 3: ratio==0.15 exactly -> fails (strict >)."""
    df = pd.DataFrame({
        "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                       + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
        "wait_minutes": [100.0] * 5 + [115.0] * 5,
    })
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15",
               "params": {"magnitude": 0.15}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is False


def test_trend_row4_boundary_just_above_15():
    """[8.4.3] Row 4: ratio ~ 15.02% -> passes."""
    df = pd.DataFrame({
        "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                       + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
        "wait_minutes": [100.0] * 5 + [115.02] * 5,
    })
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15",
               "params": {"magnitude": 0.15}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is True


def test_trend_row5_before_mean_zero():
    """[8.4.3] Row 5: before_mean=0 -> fails."""
    df = pd.DataFrame({
        "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                       + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
        "wait_minutes": [0.0] * 5 + [50.0] * 5,
    })
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15",
               "params": {"magnitude": 0.5}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is False


# FIX: [self-review item 2] — Row 6 (zero-match target -> PIE) REMOVED.
# The spec §2.9 L3 pseudocode does not filter by target for trend_break.
# Row 6 is replaced with a test for the break_point fallback path (item 3).
def test_trend_row6_break_point_fallback_to_params():
    """[8.4.3] Row 6 (replaced): break_point read from params when missing at top level."""
    df = pd.DataFrame({
        "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                       + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
        "wait_minutes": [100.0] * 5 + [130.0] * 5,
    })
    # No top-level "break_point"; falls back to params
    pattern = {"col": "wait_minutes",
               "params": {"break_point": "2024-03-15", "magnitude": 0.3}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is True


def test_trend_row7_no_temporal():
    """[8.4.3] Row 7: no temporal group -> PatternInjectionError."""
    df = pd.DataFrame({"visit_date": pd.date_range("2024-01-01", periods=5), "wait_minutes": [100.0] * 5})
    meta = {"dimension_groups": {"entity": {"columns": ["hospital"], "hierarchy": ["hospital"]}}}
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15", "params": {"magnitude": 0.4}}
    try:
        check_trend_break(df, pattern, meta)
        assert False, "Should have raised PatternInjectionError"
    except PatternInjectionError as e:
        assert "temporal" in e.detail.lower()


def test_trend_row8_missing_break_point():
    """[8.4.3] Row 8: missing break_point at both levels -> KeyError."""
    df = pd.DataFrame({"visit_date": pd.date_range("2024-01-01", periods=5), "wait_minutes": [100.0] * 5})
    pattern = {"col": "wait_minutes", "params": {"magnitude": 0.4}}
    try:
        check_trend_break(df, pattern, META_WITH_TIME)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_trend_row9_missing_col():
    """[8.4.3] Row 9: missing col -> KeyError."""
    df = pd.DataFrame({"visit_date": pd.date_range("2024-01-01", periods=5), "wait_minutes": [100.0] * 5})
    pattern = {"break_point": "2024-03-15", "params": {"magnitude": 0.4}}
    try:
        check_trend_break(df, pattern, META_WITH_TIME)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_trend_row10_all_after():
    """[8.4.3] Row 10: all rows after break -> fails (empty before)."""
    df = pd.DataFrame({
        "visit_date": pd.date_range("2024-06-01", periods=10, freq="D"),
        "wait_minutes": [100.0] * 10,
    })
    pattern = {"col": "wait_minutes", "break_point": "2024-01-01",
               "params": {"magnitude": 0.4}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is False


def test_trend_row11_all_before():
    """[8.4.3] Row 11: all rows before break -> fails (empty after)."""
    df = pd.DataFrame({
        "visit_date": pd.date_range("2024-01-01", periods=10, freq="D"),
        "wait_minutes": [100.0] * 10,
    })
    pattern = {"col": "wait_minutes", "break_point": "2025-01-01",
               "params": {"magnitude": 0.4}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is False


def test_trend_row12_done_condition():
    """[8.4.3] Row 12 / Done: 20% passes, 10% fails."""
    def _mk(after_mean):
        return pd.DataFrame({
            "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                           + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
            "wait_minutes": [100.0] * 5 + [after_mean] * 5,
        })
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15",
               "params": {"magnitude": 0.4}}
    assert check_trend_break(_mk(120.0), pattern, META_WITH_TIME).passed is True
    assert check_trend_break(_mk(110.0), pattern, META_WITH_TIME).passed is False


def test_trend_hand_calculated():
    """[8.4.3] Output: before=100, after=130 -> ratio=0.30 -> passes."""
    df = pd.DataFrame({
        "visit_date": (pd.date_range("2024-01-01", periods=5, freq="D").tolist()
                       + pd.date_range("2024-03-15", periods=5, freq="D").tolist()),
        "wait_minutes": [100.0] * 5 + [130.0] * 5,
    })
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15",
               "params": {"magnitude": 0.3}}
    result = check_trend_break(df, pattern, META_WITH_TIME)
    assert result.passed is True
    assert "ratio=0.3000" in result.detail


# =====================================================================
# max_conditional_deviation [8.3.7] — Contract rows 1-9
# =====================================================================

def test_mcd_row1(): assert max_conditional_deviation({"M": {"I": 0.5, "S": 0.5}}, {"M": {"I": 0.5, "S": 0.5}}) == 0.0
def test_mcd_row2(): assert approx(max_conditional_deviation({"M": {"I": 0.62, "S": 0.38}}, {"M": {"I": 0.50, "S": 0.50}}), 0.12)
def test_mcd_row3(): assert approx(max_conditional_deviation({"M": {"I": 0.5, "S": 0.5}, "V": {"I": 0.58, "S": 0.42}}, {"M": {"I": 0.5, "S": 0.5}, "V": {"I": 0.50, "S": 0.50}}), 0.08)
def test_mcd_row4(): assert max_conditional_deviation({}, {}) == 0.0
def test_mcd_row5(): assert approx(max_conditional_deviation({"M": {"I": 0.5}, "X": {"I": 0.3}}, {"M": {"I": 0.5}}), 0.3)
def test_mcd_row6(): assert approx(max_conditional_deviation({"M": {"I": 0.5}}, {"M": {"I": 0.5, "G": 0.2}}), 0.2)
def test_mcd_row7(): assert approx(max_conditional_deviation({"M": {"I": 0.7}}, {"M": {"I": 0.6}}), 0.1)
def test_mcd_row8(): assert approx(max_conditional_deviation({"A": {"X": 1.0}}, {"A": {"X": 0.0}}), 1.0)
def test_mcd_row9():
    d = {"M": {"I": 0.5, "S": 0.5}}
    assert max_conditional_deviation(d, d) == 0.0
    assert approx(max_conditional_deviation({"M": {"I": 0.62, "S": 0.38}}, {"M": {"I": 0.50, "S": 0.50}}), 0.12)


# =====================================================================
# match_strategy [9.1.1] — Contract rows 1-10
# =====================================================================

def test_match_row1(): assert match_strategy("ks_wait_minutes_marginal", {"ks_*": widen_variance}) is widen_variance
def test_match_row2(): assert match_strategy("outlier_cost", {"outlier_*": amplify_magnitude}) is amplify_magnitude
def test_match_row3(): assert match_strategy("trend_wait_minutes", {"trend_*": amplify_magnitude}) is amplify_magnitude
def test_match_row4(): assert match_strategy("orthogonal_hospital_severity", {"orthogonal_*": reshuffle_pair}) is reshuffle_pair
def test_match_row5(): assert match_strategy("row_count", {"ks_*": widen_variance}) is None
def test_match_row6(): assert match_strategy("anything", {}) is None
def test_match_row7(): assert match_strategy("", {"ks_*": widen_variance}) is None
def test_match_row8():
    fn_a = lambda c: "A"
    assert match_strategy("ks_cost", {"ks_*": fn_a, "ks_cost": lambda c: "B"}) is fn_a
def test_match_row9():
    fix_fn = lambda c: "fix"
    assert match_strategy("row_count", {"row_count": fix_fn}) is fix_fn
def test_match_row10():
    auto_fix = {"ks_*": widen_variance, "outlier_*": amplify_magnitude, "trend_*": amplify_magnitude, "orthogonal_*": reshuffle_pair}
    assert match_strategy("ks_wait_minutes_marginal", auto_fix) is widen_variance


# =====================================================================
# widen_variance [9.2.1] — Contract rows 1-10
# =====================================================================

def test_wv_row1(): r = widen_variance(_make_check("ks_x"), {"mu": 5.0, "sigma": 0.35}); assert approx(r["sigma"], 0.42) and r["mu"] == 5.0
def test_wv_row2(): r = widen_variance(_make_check("ks_x"), {"shape": 2.0, "scale": 1.0}); assert approx(r["scale"], 1.2)
def test_wv_row3(): assert approx(widen_variance(_make_check("ks_x"), {"mu": 0, "sigma": 1.0}, factor=2.0)["sigma"], 2.0)
def test_wv_row4(): assert approx(widen_variance(_make_check("ks_x"), {"mu": 0, "sigma": 0.5}, factor=1.0)["sigma"], 0.5)
def test_wv_row5():
    try: widen_variance(_make_check("ks_x"), {"mu": 5.0, "lambda": 1.0}); assert False
    except InvalidParameterError: pass
def test_wv_row6(): r = widen_variance(_make_check("ks_x"), {"sigma": 0.5, "scale": 1.0}); assert approx(r["sigma"], 0.6) and r["scale"] == 1.0
def test_wv_row7(): p = {"mu": 5.0, "sigma": 0.35}; widen_variance(_make_check("ks_x"), p); assert p["sigma"] == 0.35
def test_wv_row8(): assert widen_variance(_make_check("ks_x"), {"mu": 0, "sigma": 0.0})["sigma"] == 0.0
def test_wv_row9(): assert approx(widen_variance(_make_check("ks_x"), {"mu": 0, "sigma": 0.5}, factor=-1.0)["sigma"], -0.5)
def test_wv_row10(): assert approx(widen_variance(_make_check("ks_w"), {"mu": 5.0, "sigma": 0.35})["sigma"], 0.42)


# =====================================================================
# amplify_magnitude [9.2.2] — Contract rows 1-9
# =====================================================================

def test_am_row1(): assert approx(amplify_magnitude(_make_check("o"), {"type": "outlier_entity", "params": {"z_score": 3.0}})["params"]["z_score"], 3.9)
def test_am_row2(): assert approx(amplify_magnitude(_make_check("t"), {"type": "trend_break", "params": {"magnitude": 0.4, "break_point": "x"}})["params"]["magnitude"], 0.52)
def test_am_row3(): assert approx(amplify_magnitude(_make_check("o"), {"params": {"z_score": 2.0}}, factor=2.0)["params"]["z_score"], 4.0)
def test_am_row4(): assert approx(amplify_magnitude(_make_check("o"), {"params": {"z_score": 3.0}}, factor=1.0)["params"]["z_score"], 3.0)
def test_am_row5():
    try: amplify_magnitude(_make_check("o"), {"params": {"break_point": "x"}}); assert False
    except InvalidParameterError: pass
def test_am_row6(): r = amplify_magnitude(_make_check("o"), {"params": {"z_score": 3.0, "magnitude": 0.4}}); assert approx(r["params"]["z_score"], 3.9) and approx(r["params"]["magnitude"], 0.4)
def test_am_row7(): s = {"params": {"z_score": 3.0}}; amplify_magnitude(_make_check("o"), s); assert s["params"]["z_score"] == 3.0
def test_am_row8():
    s = {"type": "trend_break", "target": "h=='H'", "col": "wm", "params": {"magnitude": 0.4, "break_point": "x"}}
    r = amplify_magnitude(_make_check("t"), s)
    assert r["params"]["break_point"] == "x" and r["type"] == "trend_break" and r["target"] == "h=='H'"
def test_am_row9(): assert approx(amplify_magnitude(_make_check("o"), {"params": {"z_score": 3.0}})["params"]["z_score"], 3.9)
def test_am_deep_copy():
    s = {"params": {"z_score": 3.0, "extra": [1, 2, 3]}}
    r = amplify_magnitude(_make_check("o"), s)
    r["params"]["extra"].append(4)
    assert len(s["params"]["extra"]) == 3


# =====================================================================
# reshuffle_pair [9.2.3] — Contract rows 1-8
# =====================================================================

def test_rp_row1():
    rng = np.random.default_rng(42)
    df = pd.DataFrame({"severity": ["Mild"] * 50 + ["Severe"] * 50, "hospital": [f"H{i}" for i in range(100)]})
    r = reshuffle_pair(_make_check("orth"), df, "severity", rng)
    assert Counter(r["severity"]) == Counter(df["severity"])
    assert list(r["hospital"]) == list(df["hospital"])

def test_rp_row2():
    rng = np.random.default_rng(42)
    df = pd.DataFrame({"severity": ["Mild"], "hospital": ["H1"]})
    assert reshuffle_pair(_make_check("orth"), df, "severity", rng)["severity"].iloc[0] == "Mild"

def test_rp_row3():
    try: reshuffle_pair(_make_check("orth"), pd.DataFrame({"severity": ["Mild"]}), "nonexistent", np.random.default_rng(42)); assert False
    except KeyError: pass

def test_rp_row4():
    rng = np.random.default_rng(42)
    df = pd.DataFrame({"severity": ["Mild", "Severe", "Mild", "Severe"]})
    orig = list(df["severity"])
    reshuffle_pair(_make_check("orth"), df, "severity", rng)
    assert list(df["severity"]) == orig

def test_rp_row5():
    df = pd.DataFrame({"severity": ["A", "B", "C", "D", "E"] * 20})
    r1 = reshuffle_pair(_make_check("o"), df, "severity", np.random.default_rng(99))
    r2 = reshuffle_pair(_make_check("o"), df, "severity", np.random.default_rng(99))
    assert list(r1["severity"]) == list(r2["severity"])

def test_rp_row6():
    assert list(reshuffle_pair(_make_check("o"), pd.DataFrame({"c": ["A"] * 3}), "c", np.random.default_rng(42))["c"]) == ["A"] * 3

def test_rp_row7():
    assert len(reshuffle_pair(_make_check("o"), pd.DataFrame({"c": pd.Series([], dtype=str)}), "c", np.random.default_rng(42))) == 0

def test_rp_row8():
    rng = np.random.default_rng(42)
    df = pd.DataFrame({"severity": ["Mild"] * 30 + ["Severe"] * 20 + ["Critical"] * 10})
    assert Counter(reshuffle_pair(_make_check("o"), df, "severity", rng)["severity"]) == Counter(df["severity"])


# =====================================================================
# Integration tests
# =====================================================================

def test_integration_l3_in_report():
    df = pd.DataFrame({"hospital": ["Xiehe"] * 20 + ["B"] * 80,
                        "severity": ["Severe"] * 20 + ["Mild"] * 80,
                        "wait_minutes": [200.0] * 20 + [100.0] * 80})
    check = check_outlier_entity(df, OUTLIER_PATTERN)
    report = ValidationReport()
    report.add_checks([check])
    assert len(report.checks) == 1

def test_integration_mixed_l1_l3():
    df = pd.DataFrame({"hospital": ["Xiehe"] * 20 + ["B"] * 80,
                        "severity": ["Severe"] * 20 + ["Mild"] * 80,
                        "wait_minutes": [200.0] * 20 + [100.0] * 80})
    l1 = check_row_count(df, {"total_rows": 100})
    l3 = check_outlier_entity(df, OUTLIER_PATTERN)
    report = ValidationReport()
    report.add_checks([l1, l3])
    assert len(report.checks) == 2

def test_integration_full_autofix_dispatch():
    auto_fix = {"ks_*": widen_variance, "outlier_*": amplify_magnitude, "trend_*": amplify_magnitude, "orthogonal_*": reshuffle_pair}
    assert match_strategy("ks_wait_minutes_marginal", auto_fix) is widen_variance
    assert match_strategy("outlier_cost", auto_fix) is amplify_magnitude
    assert match_strategy("trend_wait_minutes", auto_fix) is amplify_magnitude
    assert match_strategy("orthogonal_hospital_severity", auto_fix) is reshuffle_pair
    assert match_strategy("row_count", auto_fix) is None

def test_integration_dispatch_execute_wv():
    check = Check(name="ks_wait_minutes_marginal", passed=False)
    strategy = match_strategy(check.name, {"ks_*": widen_variance})
    assert approx(strategy(check, {"mu": 5.0, "sigma": 0.35})["sigma"], 0.42)

def test_integration_dispatch_execute_am():
    check = Check(name="outlier_wait_minutes", passed=False)
    strategy = match_strategy(check.name, {"outlier_*": amplify_magnitude})
    assert approx(strategy(check, {"params": {"z_score": 3.0}})["params"]["z_score"], 3.9)

def test_integration_dispatch_execute_rp():
    check = Check(name="orthogonal_hospital_severity", passed=False)
    strategy = match_strategy(check.name, {"orthogonal_*": reshuffle_pair})
    df = pd.DataFrame({"sev": ["A", "B", "C"] * 10})
    assert Counter(strategy(check, df, "sev", np.random.default_rng(42))["sev"]) == Counter(df["sev"])

def test_integration_pie_attrs():
    df = pd.DataFrame({"visit_date": pd.date_range("2024-01-01", periods=5), "wait_minutes": [100.0] * 5})
    meta = {"dimension_groups": {"entity": {"columns": ["h"], "hierarchy": ["h"]}}}
    pattern = {"col": "wait_minutes", "break_point": "2024-03-15", "params": {"magnitude": 0.4}}
    try: check_trend_break(df, pattern, meta); assert False
    except PatternInjectionError as e: assert e.pattern_type == "trend_break"

def test_integration_ipe_wv():
    try: widen_variance(_make_check("ks_x"), {"mu": 5.0}); assert False
    except InvalidParameterError as e: assert e.param_name == "sigma|scale"

def test_integration_ipe_am():
    try: amplify_magnitude(_make_check("o"), {"params": {"break_point": "x"}}); assert False
    except InvalidParameterError as e: assert e.param_name == "z_score|magnitude"


# =====================================================================
# Run all tests
# =====================================================================

if __name__ == "__main__":
    all_test_fns = [(name, obj) for name, obj in sorted(globals().items())
                    if name.startswith("test_") and callable(obj)]
    print(f"\nRunning {len(all_test_fns)} tests...\n")
    for name, fn in all_test_fns:
        run_test(name, fn)
    print(f"\n{'=' * 60}")
    print(f"Results: {_passed} passed, {_failed} failed, {_passed + _failed} total")
    if _errors:
        print(f"\nFailures:")
        for e in _errors:
            print(f"  {e}")
    print(f"{'=' * 60}")
    sys.exit(1 if _failed else 0)
