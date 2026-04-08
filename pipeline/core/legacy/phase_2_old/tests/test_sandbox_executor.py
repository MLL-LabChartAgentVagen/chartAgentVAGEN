"""
Test suite for SandboxExecutor + Error Feedback Loop.

Tests:
1. Valid script execution → (df, meta)
2. SyntaxError capture
3. SDK ValueError capture (infeasible parameters)
4. Blocked imports (import os)
5. Blocked builtins (open, exec)
6. Timeout enforcement (infinite loop)
7. Error feedback formatting
8. Seed propagation (reproducibility)

Run from pipeline/:
    python -m phase_2.tests.test_sandbox_executor
"""

import sys

# ---- Prompt Contract Tests ----
print("=" * 60)
print("Prompt Contract Tests")
print("=" * 60)

try:
    from phase_2.sandbox_executor import PHASE2_SYSTEM_PROMPT

    assert "mapping value MUST be a flat params dict" in PHASE2_SYSTEM_PROMPT
    assert "outlier_entity: params={\"z_score\": float}" in PHASE2_SYSTEM_PROMPT
    assert "trend_break: params={\"break_point\": \"YYYY-MM-DD\", \"magnitude\": float}" in PHASE2_SYSTEM_PROMPT
    assert "Do NOT call add_correlation() on any dependency target column" in PHASE2_SYSTEM_PROMPT
    print("  ✓ Prompt includes all required hard constraints")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 1: Valid Script Execution ----
print("=" * 60)
print("Test 1: Valid Script Execution")
print("=" * 60)

try:
    from phase_2.sandbox_executor import SandboxExecutor, ExecutionResult

    executor = SandboxExecutor(timeout_seconds=30)

    valid_script = '''
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=100, seed=seed)

    sim.add_category("region",
        values=["North", "South", "East", "West"],
        weights=[0.25, 0.25, 0.25, 0.25],
        group="geo")

    sim.add_category("product",
        values=["Widget", "Gadget", "Doohickey"],
        weights=[0.4, 0.35, 0.25],
        group="item")

    sim.add_measure("revenue",
        dist="gaussian", params={"mu": 1000, "sigma": 200})

    sim.add_measure("units",
        dist="poisson", params={"lam": 50})

    sim.add_correlation("revenue", "units", target_r=0.6)

    sim.declare_orthogonal("geo", "item",
        rationale="Region and product are independent")

    sim.inject_pattern("outlier_entity",
        target="region == 'North'",
        col="revenue", params={"z_score": 3.0})

    sim.inject_pattern("ranking_reversal",
        target=None, col=None,
        params={"metrics": ["revenue", "units"],
                "description": "North has highest revenue but lowest units"})

    return sim.generate()
'''

    result = executor.execute(valid_script, seed=42)

    assert result.success, f"Expected success, got: {result.error_type}: {result.error_message}"
    assert result.df is not None, "DataFrame should not be None"
    assert result.schema_metadata is not None, "SchemaMetadata should not be None"
    assert len(result.df) == 100, f"Expected 100 rows, got {len(result.df)}"
    assert "region" in result.df.columns, "Missing 'region' column"
    assert "revenue" in result.df.columns, "Missing 'revenue' column"
    assert result.script == valid_script, "Script should be stored in result"
    print(f"  ✓ Execution succeeded: {len(result.df)} rows, "
          f"{len(result.df.columns)} columns")
    print(f"  ✓ Schema metadata: {len(result.schema_metadata.get('columns', []))} columns, "
          f"{len(result.schema_metadata.get('dimension_groups', {}))} dim groups")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 2: SyntaxError Capture ----
print("=" * 60)
print("Test 2: SyntaxError Capture")
print("=" * 60)

try:
    executor = SandboxExecutor(timeout_seconds=10)

    bad_syntax = '''
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=100, seed=seed)
    sim.add_category("x", values=["a", "b"],
                     weights=[0.5, 0.5], group="g"
    # Missing closing paren
    return sim.generate()
'''

    result = executor.execute(bad_syntax)

    assert not result.success, "Should have failed"
    assert result.error_type == "SyntaxError", f"Expected SyntaxError, got {result.error_type}"
    assert result.traceback_str is not None
    print(f"  ✓ Correctly captured SyntaxError: {result.error_message}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 3: SDK ValueError Capture ----
print("=" * 60)
print("Test 3: SDK ValueError Capture")
print("=" * 60)

try:
    executor = SandboxExecutor(timeout_seconds=10)

    # Script that declares a measure with an unsupported distribution
    bad_dist_script = '''
def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=100, seed=seed)
    sim.add_category("x",
        values=["a", "b"],
        weights=[0.5, 0.5],
        group="g")
    sim.add_measure("val",
        dist="nonexistent_distribution",
        params={"mu": 0, "sigma": 1})
    return sim.generate()
'''

    result = executor.execute(bad_dist_script)

    assert not result.success, "Should have failed"
    assert result.error_type == "ValueError", f"Expected ValueError, got {result.error_type}"
    assert "nonexistent_distribution" in result.error_message.lower() or \
           "distribution" in result.error_message.lower() or \
           "dist" in result.error_message.lower(), \
           f"Error should mention the distribution: {result.error_message}"
    print(f"  ✓ Correctly captured SDK ValueError: {result.error_message}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 4: Blocked Imports ----
print("=" * 60)
print("Test 4: Blocked Imports (import os)")
print("=" * 60)

try:
    executor = SandboxExecutor(timeout_seconds=10)

    import_os_script = '''
import os

def build_fact_table(seed=42):
    os.system("echo pwned")
    sim = FactTableSimulator(target_rows=100, seed=seed)
    sim.add_category("x", values=["a"], weights=[1.0], group="g")
    sim.add_measure("v", dist="gaussian", params={"mu": 0, "sigma": 1})
    return sim.generate()
'''

    result = executor.execute(import_os_script)

    assert not result.success, "Should have failed — import os should be blocked"
    print(f"  ✓ Correctly blocked import os: {result.error_type}: {result.error_message}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 5: Blocked Builtins ----
print("=" * 60)
print("Test 5: Blocked Builtins (open, exec)")
print("=" * 60)

try:
    executor = SandboxExecutor(timeout_seconds=10)

    # Test open()
    open_script = '''
def build_fact_table(seed=42):
    data = open("/etc/passwd").read()
    sim = FactTableSimulator(target_rows=100, seed=seed)
    sim.add_category("x", values=["a"], weights=[1.0], group="g")
    sim.add_measure("v", dist="gaussian", params={"mu": 0, "sigma": 1})
    return sim.generate()
'''

    result = executor.execute(open_script)
    assert not result.success, "Should have failed — open() should be blocked"
    print(f"  ✓ open() blocked: {result.error_type}: {result.error_message}")

    # Test exec()
    exec_script = '''
def build_fact_table(seed=42):
    exec("import os; os.system('echo pwned')")
    sim = FactTableSimulator(target_rows=100, seed=seed)
    sim.add_category("x", values=["a"], weights=[1.0], group="g")
    sim.add_measure("v", dist="gaussian", params={"mu": 0, "sigma": 1})
    return sim.generate()
'''

    result2 = executor.execute(exec_script)
    assert not result2.success, "Should have failed — exec() should be blocked"
    print(f"  ✓ exec() blocked: {result2.error_type}: {result2.error_message}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 6: Timeout Enforcement ----
print("=" * 60)
print("Test 6: Timeout Enforcement (infinite loop)")
print("=" * 60)

try:
    executor = SandboxExecutor(timeout_seconds=2)  # Short timeout for test

    infinite_script = '''
def build_fact_table(seed=42):
    while True:
        pass
    return None
'''

    result = executor.execute(infinite_script)

    assert not result.success, "Should have timed out"
    assert result.error_type == "TimeoutError", f"Expected TimeoutError, got {result.error_type}"
    print(f"  ✓ Correctly timed out: {result.error_message}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 7: Error Feedback Formatting ----
print("=" * 60)
print("Test 7: Error Feedback Formatting")
print("=" * 60)

try:
    from phase_2.sandbox_executor import format_error_feedback

    # Create a mock failed result
    failed_result = ExecutionResult(
        success=False,
        error_type="ValueError",
        error_message="Cannot achieve target_r=-0.95 between col_a and col_b",
        traceback_str="Traceback (most recent call last):\n  File ...\nValueError: ...",
        script="def build_fact_table(seed=42): ...",
    )

    feedback = format_error_feedback(failed_result)

    assert "EXECUTION ERROR" in feedback, "Feedback should contain header"
    assert "ValueError" in feedback, "Feedback should contain error type"
    assert "target_r" in feedback, "Feedback should contain error message"
    assert "Traceback" in feedback, "Feedback should contain traceback"
    assert "fix" in feedback.lower(), "Feedback should contain correction instruction"
    print(f"  ✓ Error feedback formatted correctly ({len(feedback)} chars)")
    print(f"  ✓ Preview: {feedback[:100]}...")

    # Verify no feedback for successful result
    ok_result = ExecutionResult(success=True)
    assert format_error_feedback(ok_result) == "", "No feedback for success"
    print("  ✓ No feedback generated for successful result")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 8: Seed Propagation (Reproducibility) ----
print("=" * 60)
print("Test 8: Seed Propagation (Reproducibility)")
print("=" * 60)

try:
    import pandas as pd

    executor = SandboxExecutor(timeout_seconds=30)

    repro_script = '''
def build_fact_table(seed=42):
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

    sim.add_correlation("val1", "val2", target_r=0.5)

    sim.declare_orthogonal("g1", "g2",
        rationale="Independent dimensions")

    sim.inject_pattern("outlier_entity",
        target="cat == 'A'",
        col="val1", params={"z_score": 2.5})

    sim.inject_pattern("ranking_reversal",
        target=None, col=None,
        params={"metrics": ["val1", "val2"],
                "description": "A has highest val1 but lowest val2"})

    return sim.generate()
'''

    result_a = executor.execute(repro_script, seed=42)
    result_b = executor.execute(repro_script, seed=42)

    assert result_a.success and result_b.success, "Both should succeed"

    pd.testing.assert_frame_equal(result_a.df, result_b.df)
    assert result_a.schema_metadata == result_b.schema_metadata
    print("  ✓ Same script + same seed → identical DataFrames and metadata")

    # Different seed should produce different data
    result_c = executor.execute(repro_script, seed=99)
    assert result_c.success, "Should succeed with different seed"
    # DataFrames should differ (except in very unlikely edge case)
    try:
        pd.testing.assert_frame_equal(result_a.df, result_c.df)
        print("  ⚠ Warning: Different seeds produced identical frames (unlikely)")
    except AssertionError:
        print("  ✓ Different seeds → different DataFrames (as expected)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 9: Missing build_fact_table ----
print("=" * 60)
print("Test 9: Missing build_fact_table function")
print("=" * 60)

try:
    executor = SandboxExecutor(timeout_seconds=10)

    no_func_script = '''
# Script that doesn't define build_fact_table
sim = FactTableSimulator(target_rows=100, seed=42)
sim.add_category("x", values=["a"], weights=[1.0], group="g")
sim.add_measure("v", dist="gaussian", params={"mu": 0, "sigma": 1})
result = sim.generate()
'''

    result = executor.execute(no_func_script)

    assert not result.success, "Should fail — no build_fact_table defined"
    assert result.error_type == "NameError", f"Expected NameError, got {result.error_type}"
    assert "build_fact_table" in result.error_message
    print(f"  ✓ Correctly caught missing function: {result.error_message}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()


# ---- Summary ----
print("=" * 60)
print("All 9 tests passed! ✓")
print("=" * 60)
