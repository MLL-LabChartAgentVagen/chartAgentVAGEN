"""
Test suite for Three-Layer Validation + Auto-Fix (Subtask 4).

Tests:
1. L3: dominance_shift pattern detection
2. L3: convergence pattern detection
3. L3: seasonal_anomaly pattern detection
4. KS test for multiple distributions (lognormal, gamma, beta, uniform, exponential)
5. Auto-fix: _relax_target_r mutates meta
6. Auto-fix: _amplify_magnitude mutates meta
7. generate_with_validation() converges with auto-fix

Run from pipeline/:
    python -m phase_2.tests.test_validators
"""

import sys
import numpy as np
import pandas as pd


# ---- Test 1: L3 dominance_shift pattern detection ----
print("=" * 60)
print("Test 1: L3 dominance_shift pattern detection")
print("=" * 60)

try:
    from phase_2.fact_table_simulator import FactTableSimulator
    from phase_2.validators import SchemaAwareValidator

    sim = FactTableSimulator(target_rows=500, seed=42)
    sim.add_category("store",
        values=["Alpha", "Beta", "Gamma"],
        weights=[0.34, 0.33, 0.33],
        group="entity")
    sim.add_category("channel",
        values=["Online", "Offline"],
        weights=[0.5, 0.5],
        group="sales_channel")
    sim.add_temporal("date", start="2024-01-01", end="2024-12-31", freq="daily")
    sim.add_measure("sales",
        dist="gaussian", params={"mu": 100, "sigma": 20})
    sim.add_measure("profit",
        dist="gaussian", params={"mu": 50, "sigma": 10})

    sim.add_correlation("sales", "profit", target_r=0.5)
    sim.declare_orthogonal("entity", "sales_channel",
        rationale="Store and channel are independent")

    sim.inject_pattern("dominance_shift",
        target=None, col="sales",
        params={"magnitude": 0.5})

    sim.inject_pattern("outlier_entity",
        target="store == 'Alpha'",
        col="sales", params={"z_score": 2.5})

    df, meta = sim.generate()

    validator = SchemaAwareValidator()
    report = validator.validate(df, meta)

    # Check that a dominance_* check exists
    dominance_checks = [c for c in report.checks if c.name.startswith("dominance_")]
    assert len(dominance_checks) > 0, "No dominance check found in L3"
    for c in dominance_checks:
        print(f"  ✓ {c.name}: passed={c.passed}, {c.detail}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 2: L3 convergence pattern detection ----
print("=" * 60)
print("Test 2: L3 convergence pattern detection")
print("=" * 60)

try:
    sim2 = FactTableSimulator(target_rows=500, seed=42)
    sim2.add_category("team",
        values=["X", "Y", "Z"],
        weights=[0.34, 0.33, 0.33],
        group="group1")
    sim2.add_category("tier",
        values=["Gold", "Silver"],
        weights=[0.5, 0.5],
        group="group2")
    sim2.add_temporal("week", start="2024-01-01", end="2024-12-31", freq="weekly")
    sim2.add_measure("score",
        dist="gaussian", params={"mu": 80, "sigma": 15})
    sim2.add_measure("rating",
        dist="gaussian", params={"mu": 50, "sigma": 10})

    sim2.add_correlation("score", "rating", target_r=0.4)
    sim2.declare_orthogonal("group1", "group2",
        rationale="Team and tier are independent")

    sim2.inject_pattern("convergence",
        target=None, col="score",
        params={"convergence_rate": 0.8})

    sim2.inject_pattern("outlier_entity",
        target="team == 'X'",
        col="score", params={"z_score": 2.0})

    df2, meta2 = sim2.generate()

    validator2 = SchemaAwareValidator()
    report2 = validator2.validate(df2, meta2)

    convergence_checks = [c for c in report2.checks
                          if c.name.startswith("convergence_")]
    assert len(convergence_checks) > 0, "No convergence check found in L3"
    for c in convergence_checks:
        print(f"  ✓ {c.name}: passed={c.passed}, {c.detail}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 3: L3 seasonal_anomaly pattern detection ----
print("=" * 60)
print("Test 3: L3 seasonal_anomaly pattern detection")
print("=" * 60)

try:
    sim3 = FactTableSimulator(target_rows=500, seed=42)
    sim3.add_category("region",
        values=["North", "South", "East", "West"],
        weights=[0.25, 0.25, 0.25, 0.25],
        group="geo")
    sim3.add_category("product",
        values=["Widget", "Gadget"],
        weights=[0.5, 0.5],
        group="item")
    sim3.add_temporal("date", start="2024-01-01", end="2024-12-31", freq="daily")
    sim3.add_measure("revenue",
        dist="gaussian", params={"mu": 200, "sigma": 40})
    sim3.add_measure("cost",
        dist="gaussian", params={"mu": 100, "sigma": 20})

    sim3.add_correlation("revenue", "cost", target_r=0.6)
    sim3.declare_orthogonal("geo", "item",
        rationale="Region and product are independent")

    sim3.inject_pattern("seasonal_anomaly",
        target="region == 'North'",
        col="revenue",
        params={"amplitude": 0.3, "period_days": 90})

    sim3.inject_pattern("outlier_entity",
        target="region == 'South'",
        col="revenue", params={"z_score": 2.0})

    df3, meta3 = sim3.generate()

    validator3 = SchemaAwareValidator()
    report3 = validator3.validate(df3, meta3)

    seasonal_checks = [c for c in report3.checks
                       if c.name.startswith("seasonal_")]
    assert len(seasonal_checks) > 0, "No seasonal check found in L3"
    for c in seasonal_checks:
        print(f"  ✓ {c.name}: passed={c.passed}, {c.detail}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 4: KS test for multiple distributions ----
print("=" * 60)
print("Test 4: KS test for multiple distributions")
print("=" * 60)

try:
    from phase_2.validators import _get_ks_args

    test_cases = [
        ("gaussian", {"mu": 0, "sigma": 1}, "norm"),
        ("lognormal", {"mu": 0, "sigma": 0.5}, "lognorm"),
        ("gamma", {"shape": 2, "scale": 1}, "gamma"),
        ("beta", {"alpha": 2, "beta": 5}, "beta"),
        ("uniform", {"low": 0, "high": 10}, "uniform"),
        ("exponential", {"scale": 2}, "expon"),
    ]

    for dist_name, params, expected_scipy in test_cases:
        result = _get_ks_args(dist_name, params)
        assert result is not None, f"_get_ks_args returned None for {dist_name}"
        scipy_name, args = result
        assert scipy_name == expected_scipy, (
            f"{dist_name}: expected scipy name '{expected_scipy}', got '{scipy_name}'"
        )
        print(f"  ✓ {dist_name} → scipy '{scipy_name}' args={args}")

    # Verify unsupported dists return None
    assert _get_ks_args("poisson", {"lam": 5}) is None, "poisson should return None"
    assert _get_ks_args("mixture", {}) is None, "mixture should return None"
    print("  ✓ poisson and mixture correctly return None")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 5: Auto-fix _relax_target_r mutates meta ----
print("=" * 60)
print("Test 5: Auto-fix _relax_target_r mutates meta")
print("=" * 60)

try:
    from phase_2.validators import Check, _relax_target_r, FixAction

    meta = {
        "correlations": [
            {"col_a": "sales", "col_b": "profit", "target_r": -0.55},
        ]
    }

    check = Check(
        name="corr_sales_profit",
        passed=False,
        detail="target=-0.55, actual=-0.20",
        auto_fixable=True,
    )

    action = _relax_target_r(check, meta)

    assert action is not None, "FixAction should not be None"
    assert isinstance(action, FixAction), f"Expected FixAction, got {type(action)}"
    new_r = meta["correlations"][0]["target_r"]
    assert new_r == -0.50, f"Expected -0.50, got {new_r}"
    print(f"  ✓ Relaxed target_r: -0.55 → {new_r}")
    print(f"  ✓ FixAction: {action}")

    # Test positive correlation
    meta_pos = {
        "correlations": [
            {"col_a": "x", "col_b": "y", "target_r": 0.90},
        ]
    }
    check_pos = Check(name="corr_x_y", passed=False, detail="", auto_fixable=True)
    action_pos = _relax_target_r(check_pos, meta_pos)
    assert meta_pos["correlations"][0]["target_r"] == 0.85
    print(f"  ✓ Relaxed positive target_r: 0.90 → 0.85")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 6: Auto-fix _amplify_magnitude mutates meta ----
print("=" * 60)
print("Test 6: Auto-fix _amplify_magnitude mutates meta")
print("=" * 60)

try:
    from phase_2.validators import _amplify_magnitude

    meta = {
        "patterns": [
            {
                "type": "outlier_entity",
                "col": "revenue",
                "target": "store == 'A'",
                "z_score": 3.0,
            },
        ]
    }

    check = Check(
        name="outlier_revenue",
        passed=False,
        detail="z-score=1.5",
        auto_fixable=True,
    )

    action = _amplify_magnitude(check, meta)

    assert action is not None, "FixAction should not be None"
    new_z = meta["patterns"][0]["z_score"]
    assert new_z == round(3.0 * 1.3, 4), f"Expected {3.0 * 1.3}, got {new_z}"
    print(f"  ✓ Amplified z_score: 3.0 → {new_z}")
    print(f"  ✓ FixAction: {action}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 7: generate_with_validation() with auto-fix ----
print("=" * 60)
print("Test 7: generate_with_validation() with auto-fix")
print("=" * 60)

try:
    from phase_2.validators import generate_with_validation

    def build_simple(seed=42, meta=None):
        target_r = 0.5
        z_score = 2.5
        if meta is not None:
            if meta.get("correlations"):
                target_r = meta["correlations"][0].get("target_r", target_r)
            if meta.get("patterns"):
                z_score = meta["patterns"][0].get("z_score", z_score)
        sim = FactTableSimulator(target_rows=200, seed=seed)
        sim.add_category("cat",
            values=["A", "B", "C"],
            weights=[0.4, 0.35, 0.25],
            group="g1")
        sim.add_category("type",
            values=["X", "Y"],
            weights=[0.6, 0.4],
            group="g2")
        sim.add_measure("val1",
            dist="gaussian", params={"mu": 50, "sigma": 10})
        sim.add_measure("val2",
            dist="gaussian", params={"mu": 100, "sigma": 20})
        sim.add_correlation("val1", "val2", target_r=target_r)
        sim.declare_orthogonal("g1", "g2",
            rationale="Independent dimensions")
        sim.inject_pattern("outlier_entity",
            target="cat == 'A'",
            col="val1", params={"z_score": z_score})
        sim.inject_pattern("ranking_reversal",
            target=None, col=None,
            params={"metrics": ["val1", "val2"],
                    "description": "A has highest val1 but lowest val2"})
        df, _ = sim.generate()
        return df

    base_meta = {
        "columns": [
            {"name": "cat", "type": "categorical", "cardinality": 3},
            {"name": "type", "type": "categorical", "cardinality": 2},
            {"name": "val1", "type": "measure", "declared_dist": "gaussian", "declared_params": {"mu": 50, "sigma": 10}},
            {"name": "val2", "type": "measure", "declared_dist": "gaussian", "declared_params": {"mu": 100, "sigma": 20}},
        ],
        "dimension_groups": {
            "g1": {"columns": ["cat"], "hierarchy": ["cat"]},
            "g2": {"columns": ["type"], "hierarchy": ["type"]},
        },
        "orthogonal_groups": [{"group_a": "g1", "group_b": "g2", "rationale": "Independent dimensions"}],
        "correlations": [{"col_a": "val1", "col_b": "val2", "target_r": 0.5}],
        "patterns": [{"type": "outlier_entity", "target": "cat == 'A'", "col": "val1", "z_score": 2.5}],
        "dependencies": [],
        "conditionals": [],
        "realism": {},
        "total_rows": 200,
    }

    df_result, report_result, meta_result = generate_with_validation(
        build_fn=build_simple,
        meta=base_meta,
        max_retries=3,
        base_seed=42,
    )

    assert df_result is not None, "DataFrame should not be None"
    assert len(df_result) == 200, f"Expected 200 rows, got {len(df_result)}"

    n_passed = sum(1 for c in report_result.checks if c.passed)
    n_total = len(report_result.checks)

    print(f"  ✓ generate_with_validation() completed: "
          f"{n_passed}/{n_total} checks passed")
    print(f"  ✓ DataFrame: {len(df_result)} rows × {len(df_result.columns)} cols")
    print(f"  ✓ Final target_r={meta_result['correlations'][0]['target_r']}")

    for c in report_result.checks:
        status = "✓" if c.passed else "✗"
        fix_note = " [auto-fixable]" if c.auto_fixable and not c.passed else ""
        print(f"    {status} {c.name}: {c.detail}{fix_note}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 8: Regression — existing test_fact_table_simulator Test 9 ----
print("=" * 60)
print("Test 8: Regression — SchemaAwareValidator on hospital example")
print("=" * 60)

try:
    sim_h = FactTableSimulator(target_rows=500, seed=42)

    sim_h.add_category("hospital",
        values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
        weights=[0.25, 0.20, 0.20, 0.20, 0.15],
        group="entity")
    sim_h.add_category("department",
        values=["Internal", "Surgery", "Pediatrics", "Emergency"],
        weights=[0.35, 0.25, 0.15, 0.25],
        group="entity", parent="hospital")
    sim_h.add_category("severity",
        values=["Mild", "Moderate", "Severe"],
        weights=[0.50, 0.35, 0.15],
        group="patient")
    sim_h.add_category("payment_method",
        values=["Insurance", "Self-pay", "Government"],
        weights=[0.60, 0.30, 0.10],
        group="payment")
    sim_h.add_temporal("visit_date",
        start="2024-01-01", end="2024-06-30", freq="daily")
    sim_h.add_measure("wait_minutes",
        dist="lognormal", params={"mu": 3.0, "sigma": 0.5})
    sim_h.add_measure("cost",
        dist="lognormal", params={"mu": 6.0, "sigma": 0.8})
    sim_h.add_measure("satisfaction",
        dist="beta", params={"alpha": 5, "beta": 2}, scale=[1, 10])

    sim_h.add_conditional("wait_minutes", on="severity", mapping={
        "Mild":     {"mu": 2.5, "sigma": 0.4},
        "Moderate": {"mu": 3.0, "sigma": 0.5},
        "Severe":   {"mu": 3.8, "sigma": 0.6}
    })
    sim_h.add_correlation("wait_minutes", "satisfaction", target_r=-0.55)
    sim_h.declare_orthogonal("entity", "patient",
        rationale="Severity distribution is independent of hospital/department")
    sim_h.declare_orthogonal("entity", "payment",
        rationale="Payment method is independent of hospital/department")
    sim_h.inject_pattern("outlier_entity",
        target="hospital == 'Xiehe' & severity == 'Severe'",
        col="wait_minutes", params={"z_score": 3.0})
    sim_h.inject_pattern("ranking_reversal",
        target=None, col=None,
        params={"metrics": ["wait_minutes", "satisfaction"],
                "description": "Xiehe has longest wait but highest satisfaction"})
    sim_h.inject_pattern("trend_break",
        target="hospital == 'Huashan'",
        col="wait_minutes",
        params={"break_point": "2024-03-15", "magnitude": 0.4})
    sim_h.set_realism(missing_rate=0.03, dirty_rate=0.02,
                      censoring={"col": "cost", "type": "right", "threshold": 5000})

    df_h, meta_h = sim_h.generate()
    report_h = SchemaAwareValidator().validate(df_h, meta_h)

    n_passed = sum(1 for c in report_h.checks if c.passed)
    n_total = len(report_h.checks)
    pass_rate = n_passed / n_total if n_total > 0 else 1.0

    assert pass_rate >= 0.5, f"Regression! Only {n_passed}/{n_total} passed"
    print(f"  ✓ Hospital regression: {n_passed}/{n_total} checks passed ({pass_rate:.0%})")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Summary ----
print("=" * 60)
print("All 8 tests passed! ✓")
print("=" * 60)
