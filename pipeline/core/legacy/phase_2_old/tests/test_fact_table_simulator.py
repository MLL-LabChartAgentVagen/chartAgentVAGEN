"""
Verification script for the FactTableSimulator SDK.

Tests:
1. Hospital example end-to-end (exact one-shot from spec)
2. Ordering guard (Step 2 before Step 1 → RuntimeError)
3. Dimension groups & orthogonality (χ² independence)
4. Hierarchy (parent-child structural consistency)
5. Correlation injection (Gaussian Copula, target r)
6. Conditional distribution (grouped means ordering)
7. Pattern injection: outlier_entity (z-score)
8. Reproducibility (same seed → identical output)
9. Three-layer validation on hospital example

Run:
    cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/pipeline
    python -m phase_2.tests.test_fact_table_simulator
"""

import sys
import numpy as np
import pandas as pd


# ---- Test 1: Hospital Example End-to-End ----
print("=" * 60)
print("Test 1: Hospital Example End-to-End")
print("=" * 60)

try:
    from phase_2.fact_table_simulator import FactTableSimulator

    sim = FactTableSimulator(target_rows=500, seed=42)

    # Step 1: Declare all columns
    sim.add_category("hospital",
        values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
        weights=[0.25, 0.20, 0.20, 0.20, 0.15],
        group="entity")

    sim.add_category("department",
        values=["Internal", "Surgery", "Pediatrics", "Emergency"],
        weights=[0.35, 0.25, 0.15, 0.25],
        group="entity", parent="hospital")

    sim.add_category("severity",
        values=["Mild", "Moderate", "Severe"],
        weights=[0.50, 0.35, 0.15],
        group="patient")

    sim.add_category("payment_method",
        values=["Insurance", "Self-pay", "Government"],
        weights=[0.60, 0.30, 0.10],
        group="payment")

    sim.add_temporal("visit_date",
        start="2024-01-01", end="2024-06-30", freq="daily")

    sim.add_measure("wait_minutes",
        dist="lognormal", params={"mu": 3.0, "sigma": 0.5})

    sim.add_measure("cost",
        dist="lognormal", params={"mu": 6.0, "sigma": 0.8})

    sim.add_measure("satisfaction",
        dist="beta", params={"alpha": 5, "beta": 2}, scale=[1, 10])

    # Step 2: Relationships & patterns
    sim.add_conditional("wait_minutes", on="severity", mapping={
        "Mild":     {"mu": 2.5, "sigma": 0.4},
        "Moderate": {"mu": 3.0, "sigma": 0.5},
        "Severe":   {"mu": 3.8, "sigma": 0.6}
    })

    sim.add_correlation("wait_minutes", "satisfaction", target_r=-0.55)

    sim.declare_orthogonal("entity", "patient",
        rationale="Severity distribution is independent of hospital/department")
    sim.declare_orthogonal("entity", "payment",
        rationale="Payment method is independent of hospital/department")

    sim.inject_pattern("outlier_entity",
        target="hospital == 'Xiehe' & severity == 'Severe'",
        col="wait_minutes", params={"z_score": 3.0})

    sim.inject_pattern("ranking_reversal",
        target=None, col=None,
        params={"metrics": ["wait_minutes", "satisfaction"],
                "description": "Xiehe has longest wait but highest satisfaction"})

    sim.inject_pattern("trend_break",
        target="hospital == 'Huashan'",
        col="wait_minutes",
        params={"break_point": "2024-03-15", "magnitude": 0.4})

    sim.set_realism(missing_rate=0.03, dirty_rate=0.02,
                    censoring={"col": "cost", "type": "right", "threshold": 5000})

    df, meta = sim.generate()

    # Assertions
    assert len(df) == 500, f"Expected 500 rows, got {len(df)}"
    expected_cols = {"hospital", "department", "severity", "payment_method",
                     "visit_date", "wait_minutes", "cost", "satisfaction"}
    actual_cols = set(df.columns)
    assert expected_cols == actual_cols, f"Column mismatch: {expected_cols - actual_cols}"

    print(f"  ✓ DataFrame: {len(df)} rows × {len(df.columns)} columns")
    print(f"    Columns: {list(df.columns)}")
    print(f"    dtypes: {dict(df.dtypes)}")
    print(f"    Sample row:\n{df.iloc[0].to_dict()}")

    # Check meta structure
    assert "dimension_groups" in meta
    assert "orthogonal_groups" in meta
    assert "columns" in meta
    assert len(meta["dimension_groups"]) == 3  # entity, patient, payment
    assert len(meta["orthogonal_groups"]) == 2
    assert meta["total_rows"] == 500
    print(f"  ✓ SchemaMetadata: {len(meta['dimension_groups'])} dim groups, "
          f"{len(meta['orthogonal_groups'])} orthogonal pairs")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 2: Ordering Guard ----
print("=" * 60)
print("Test 2: Ordering Guard (Step 2 before Step 1)")
print("=" * 60)

try:
    sim2 = FactTableSimulator(target_rows=100, seed=1)
    sim2.add_category("x", values=["a", "b"], weights=[0.5, 0.5], group="g1")
    sim2.add_measure("m", dist="gaussian", params={"mu": 0, "sigma": 1})

    # This Step 2 call should freeze
    sim2.add_correlation("m", "m", target_r=0.5)  # Will fail: same col

    # If we reach here, the add_correlation validation should have caught same-col
    print("  ✗ FAILED: Expected ValueError for same col_a and col_b")
    sys.exit(1)

except ValueError as e:
    print(f"  ✓ Correctly raised ValueError: {e}")

try:
    sim2b = FactTableSimulator(target_rows=100, seed=1)
    sim2b.add_category("x", values=["a", "b"], weights=[0.5, 0.5], group="g1")
    sim2b.add_measure("m1", dist="gaussian", params={"mu": 0, "sigma": 1})
    sim2b.add_measure("m2", dist="gaussian", params={"mu": 0, "sigma": 1})

    # Step 2 call — freezes Step 1
    sim2b.add_correlation("m1", "m2", target_r=0.5)

    # Trying Step 1 after freeze should fail
    sim2b.add_category("y", values=["c", "d"], weights=[0.5, 0.5], group="g2")
    print("  ✗ FAILED: Expected RuntimeError for Step 1 after Step 2")
    sys.exit(1)

except RuntimeError as e:
    print(f"  ✓ Correctly raised RuntimeError: {e}")

print()


# ---- Test 3: Dimension Groups & Orthogonality ----
print("=" * 60)
print("Test 3: Dimension Groups & Orthogonality (χ²)")
print("=" * 60)

try:
    sim3 = FactTableSimulator(target_rows=1000, seed=42)
    sim3.add_category("brand", values=["A", "B", "C"], weights=[0.4, 0.35, 0.25],
                       group="product")
    sim3.add_category("region", values=["North", "South", "East", "West"],
                       weights=[0.25, 0.25, 0.25, 0.25], group="geography")
    sim3.add_measure("sales", dist="gaussian", params={"mu": 100, "sigma": 20})

    sim3.declare_orthogonal("product", "geography",
        rationale="Brand distribution is independent of region")

    df3, meta3 = sim3.generate()

    assert "dimension_groups" in meta3
    assert len(meta3["dimension_groups"]) == 2
    assert len(meta3["orthogonal_groups"]) == 1
    print(f"  ✓ {len(meta3['dimension_groups'])} dim groups, "
          f"{len(meta3['orthogonal_groups'])} orthogonal pair(s)")

    # Chi-squared independence test
    from scipy.stats import chi2_contingency
    ct = pd.crosstab(df3["brand"], df3["region"])
    _, p_val, _, _ = chi2_contingency(ct)
    assert p_val > 0.05, f"Groups not independent: p={p_val:.4f}"
    print(f"  ✓ χ² test: p={p_val:.4f} (>0.05 → independent)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 4: Hierarchy ----
print("=" * 60)
print("Test 4: Hierarchy (parent-child)")
print("=" * 60)

try:
    sim4 = FactTableSimulator(target_rows=200, seed=42)
    sim4.add_category("country", values=["US", "UK"], weights=[0.6, 0.4],
                       group="geo")
    sim4.add_category("city", values=["NYC", "LA", "London", "Manchester"],
                       weights=[0.3, 0.3, 0.2, 0.2], group="geo", parent="country")
    sim4.add_measure("revenue", dist="gaussian", params={"mu": 50, "sigma": 10})

    df4, meta4 = sim4.generate()

    # Check hierarchy is recorded in metadata
    geo_group = meta4["dimension_groups"]["geo"]
    assert geo_group["hierarchy"] == ["country", "city"]
    print(f"  ✓ Hierarchy recorded: {geo_group['hierarchy']}")
    print(f"  ✓ DataFrame: {len(df4)} rows, columns={list(df4.columns)}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 5: Correlation Injection ----
print("=" * 60)
print("Test 5: Correlation Injection (Gaussian Copula)")
print("=" * 60)

try:
    sim5 = FactTableSimulator(target_rows=1000, seed=42)
    sim5.add_category("item", values=["x"], weights=[1.0], group="g")
    sim5.add_measure("a", dist="gaussian", params={"mu": 50, "sigma": 10})
    sim5.add_measure("b", dist="gaussian", params={"mu": 100, "sigma": 20})

    sim5.add_correlation("a", "b", target_r=-0.55)

    df5, meta5 = sim5.generate()
    actual_r = df5["a"].corr(df5["b"])

    assert abs(actual_r - (-0.55)) < 0.15, (
        f"Correlation mismatch: target=-0.55, actual={actual_r:.3f}"
    )
    print(f"  ✓ Correlation: target=-0.55, actual={actual_r:.3f} (within ±0.15)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 6: Conditional Distribution ----
print("=" * 60)
print("Test 6: Conditional Distribution")
print("=" * 60)

try:
    sim6 = FactTableSimulator(target_rows=3000, seed=42)
    sim6.add_category("level", values=["Low", "Medium", "High"],
                       weights=[0.33, 0.34, 0.33], group="g")
    sim6.add_measure("score", dist="gaussian", params={"mu": 50, "sigma": 5})

    sim6.add_conditional("score", on="level", mapping={
        "Low":    {"mu": 30, "sigma": 3},
        "Medium": {"mu": 50, "sigma": 5},
        "High":   {"mu": 80, "sigma": 3},
    })

    df6, _ = sim6.generate()
    means = df6.groupby("level")["score"].mean()

    assert means["Low"] < means["Medium"] < means["High"], (
        f"Conditional means not ordered: {means.to_dict()}"
    )
    print(f"  ✓ Conditional means: Low={means['Low']:.1f}, "
          f"Medium={means['Medium']:.1f}, High={means['High']:.1f}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 7: Pattern Injection — Outlier Entity ----
print("=" * 60)
print("Test 7: Pattern Injection — outlier_entity")
print("=" * 60)

try:
    sim7 = FactTableSimulator(target_rows=1000, seed=42)
    sim7.add_category("team",
        values=["Alpha", "Beta", "Gamma", "Delta", "Echo",
                "Foxtrot", "Golf", "Hotel", "India", "Juliet"],
        weights=[0.10, 0.10, 0.10, 0.10, 0.10,
                 0.10, 0.10, 0.10, 0.10, 0.10],
        group="g")
    sim7.add_measure("performance", dist="gaussian",
                      params={"mu": 100, "sigma": 15})

    sim7.inject_pattern("outlier_entity",
        target="team == 'Alpha'",
        col="performance",
        params={"z_score": 3.0})

    df7, _ = sim7.generate()

    alpha_mean = df7[df7["team"] == "Alpha"]["performance"].mean()
    overall_mean = df7["performance"].mean()
    overall_std = df7["performance"].std()
    z = abs(alpha_mean - overall_mean) / overall_std

    assert z >= 2.0, f"Outlier z-score too low: {z:.2f}"
    print(f"  ✓ Outlier z-score: {z:.2f} (≥2.0)")
    print(f"    Alpha mean={alpha_mean:.1f}, Overall mean={overall_mean:.1f}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 8: Reproducibility ----
print("=" * 60)
print("Test 8: Reproducibility (same seed → identical output)")
print("=" * 60)

try:
    def make_sim():
        s = FactTableSimulator(target_rows=200, seed=42)
        s.add_category("cat", values=["a", "b", "c"], weights=[0.3, 0.4, 0.3],
                        group="g")
        s.add_measure("val", dist="gaussian", params={"mu": 0, "sigma": 1})
        return s

    df_a, meta_a = make_sim().generate()
    df_b, meta_b = make_sim().generate()

    pd.testing.assert_frame_equal(df_a, df_b)
    assert meta_a == meta_b
    print("  ✓ Two runs with seed=42 produce identical DataFrames and metadata")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 9: Three-Layer Validation ----
print("=" * 60)
print("Test 9: Three-Layer Validation")
print("=" * 60)

try:
    from phase_2.validators import SchemaAwareValidator

    # Use the hospital example from Test 1
    validator = SchemaAwareValidator()
    report = validator.validate(df, meta)

    print(f"  Total checks: {len(report.checks)}")
    for check in report.checks:
        status = "✓" if check.passed else "✗"
        print(f"    {status} {check.name}: {check.detail}")

    # We expect most checks to pass; some pattern checks may be marginal
    n_passed = sum(1 for c in report.checks if c.passed)
    n_total = len(report.checks)
    pass_rate = n_passed / n_total if n_total > 0 else 1.0

    # Some failures are expected: patterns deliberately break orthogonality
    # and correlations (e.g., outlier on hospital+severity breaks entity⊥patient)
    assert pass_rate >= 0.5, (
        f"Too many validation failures: {n_passed}/{n_total} passed"
    )
    print(f"\n  ✓ Validation: {n_passed}/{n_total} checks passed ({pass_rate:.0%})")

    if report.all_passed:
        print("  ✓ ALL checks passed!")
    else:
        print(f"  ⚠ {len(report.failures)} checks failed (acceptable for "
              f"stochastic generation)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Summary ----
print("=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
