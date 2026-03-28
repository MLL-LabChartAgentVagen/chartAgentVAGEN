"""
Sprint 6 — Tests for agpds.validator module.

Subtask IDs covered: 8.1.1, 8.1.2, 8.2.1, 8.2.2, 8.2.5, 8.2.6

Test structure:
  1. Contract tests — one test per Message 1 contract table row
  2. Input validation tests — type enforcement, boundary values, constraints
  3. Output correctness tests — return types, fields, immutability
  4. State transition tests — report accumulation semantics
  5. Integration tests — validator functions against real simulator output
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from agpds.validator import (
    Check,
    ValidationReport,
    check_categorical_cardinality,
    check_measure_dag_acyclic,
    check_orthogonal_independence,
    check_row_count,
)


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def meta_500() -> dict:
    """Metadata with total_rows=500."""
    return {"total_rows": 500}


@pytest.fixture
def df_n():
    """Factory fixture: returns a DataFrame with exactly n rows."""
    def _make(n: int) -> pd.DataFrame:
        return pd.DataFrame({"x": range(n)})
    return _make


@pytest.fixture
def meta_with_orthogonal() -> dict:
    """Metadata with one orthogonal pair (entity ↔ patient)."""
    return {
        "orthogonal_groups": [
            {"group_a": "entity", "group_b": "patient", "rationale": "test"},
        ],
        "dimension_groups": {
            "entity": {"columns": ["root_e"], "hierarchy": ["root_e"]},
            "patient": {"columns": ["root_p"], "hierarchy": ["root_p"]},
        },
    }


# =====================================================================
# 1. CONTRACT TESTS — Check dataclass (8.1.1) — Table 3A rows 1-3
# =====================================================================

class TestCheckContract:
    """Contract tests for the Check dataclass [Subtask 8.1.1]."""

    def test_check_name_and_passed_no_detail(self):
        """Contract 3A row 1: name + passed, no detail."""
        # [Subtask 8.1.1]
        c = Check("row_count", True)
        assert c.name == "row_count"
        assert c.passed is True
        assert c.detail is None

    def test_check_with_detail(self):
        """Contract 3A row 2: name + passed + detail string."""
        # [Subtask 8.1.1]
        c = Check("x", False, "χ² p=0.02")
        assert c.detail == "χ² p=0.02"
        assert c.passed is False

    def test_check_empty_name(self):
        """Contract 3A row 3: empty name string is allowed."""
        # [Subtask 8.1.1]
        c = Check("", True)
        assert c.name == ""


# =====================================================================
# 1. CONTRACT TESTS — ValidationReport (8.1.2) — Table 3A rows 4-9
# =====================================================================

class TestValidationReportContract:
    """Contract tests for ValidationReport [Subtask 8.1.2]."""

    def test_empty_report_all_passed(self):
        """Contract 3A row 4: empty report → all_passed=True, failures=[], checks=[]."""
        # [Subtask 8.1.2]
        r = ValidationReport()
        assert r.all_passed is True
        assert r.failures == []
        assert r.checks == []

    def test_three_passing_checks(self):
        """Contract 3A row 5: 3 passing checks → all_passed=True, 0 failures."""
        # [Subtask 8.1.2]
        r = ValidationReport(checks=[
            Check("a", True), Check("b", True), Check("c", True),
        ])
        assert r.all_passed is True
        assert len(r.failures) == 0

    def test_two_pass_one_fail(self):
        """Contract 3A row 6: 2 pass + 1 fail → all_passed=False, failures=[failing]."""
        # [Subtask 8.1.2]
        failing = Check("bad", False)
        r = ValidationReport(checks=[
            Check("ok1", True), Check("ok2", True), failing,
        ])
        assert r.all_passed is False
        assert len(r.failures) == 1
        assert r.failures[0] is failing

    def test_three_failing_checks(self):
        """Contract 3A row 7: 3 failing checks → all_passed=False, 3 failures."""
        # [Subtask 8.1.2]
        r = ValidationReport(checks=[
            Check("a", False), Check("b", False), Check("c", False),
        ])
        assert r.all_passed is False
        assert len(r.failures) == 3

    def test_add_checks_increments_length(self):
        """Contract 3A row 8: add_checks appends to existing checks."""
        # [Subtask 8.1.2]
        r = ValidationReport()
        r.add_checks([Check("a", True)])
        assert len(r.checks) == 1

    def test_add_checks_empty_list_no_change(self):
        """Contract 3A row 9: add_checks([]) leaves checks unchanged."""
        # [Subtask 8.1.2]
        r = ValidationReport(checks=[Check("x", True)])
        r.add_checks([])
        assert len(r.checks) == 1


# =====================================================================
# 1. CONTRACT TESTS — Row Count Check (8.2.1) — Table 3B
# =====================================================================

class TestRowCountContract:
    """Contract tests for check_row_count [Subtask 8.2.1]."""

    def test_480_of_500_passes(self, df_n, meta_500):
        """Contract 3B row 1: 480 rows, target 500, deviation 4% < 10% → passes."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(480), meta_500)
        assert c.passed is True

    def test_exact_match_passes(self, df_n, meta_500):
        """Contract 3B row 2: 500 rows, target 500, exact match → passes."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(500), meta_500)
        assert c.passed is True

    def test_400_of_500_fails(self, df_n, meta_500):
        """Contract 3B row 3: 400 rows, target 500, deviation 20% > 10% → fails."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(400), meta_500)
        assert c.passed is False

    def test_449_boundary_fails(self, df_n, meta_500):
        """Contract 3B row 4: 449 rows, deviation 10.2% → fails (boundary)."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(449), meta_500)
        assert c.passed is False

    def test_451_boundary_passes(self, df_n, meta_500):
        """Contract 3B row 5: 451 rows, deviation 9.8% → passes (boundary)."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(451), meta_500)
        assert c.passed is True

    def test_550_exactly_10_percent_fails(self, df_n, meta_500):
        """Contract 3B row 6: 550 rows, exactly 10% deviation → fails (strict <)."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(550), meta_500)
        assert c.passed is False

    def test_zero_rows_fails(self, meta_500):
        """Contract 3B row 7: 0-row DataFrame → fails."""
        # [Subtask 8.2.1]
        c = check_row_count(pd.DataFrame({"x": []}), meta_500)
        assert c.passed is False

    def test_missing_total_rows_raises_key_error(self, df_n):
        """Contract 3B row 8: meta has no 'total_rows' → KeyError."""
        # [Subtask 8.2.1]
        with pytest.raises(KeyError):
            check_row_count(df_n(500), {})


# =====================================================================
# 1. CONTRACT TESTS — Categorical Cardinality (8.2.2) — Table 3C
# =====================================================================

class TestCategoricalCardinalityContract:
    """Contract tests for check_categorical_cardinality [Subtask 8.2.2]."""

    def test_matching_cardinality_passes(self):
        """Contract 3C row 1: 5 declared, 5 actual → passes."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B", "C", "D", "E"] * 10})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "cardinality": 5},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert len(checks) == 1
        assert checks[0].passed is True

    def test_fewer_unique_fails(self):
        """Contract 3C row 2: 5 declared, 4 actual unique → fails."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B", "C", "D"] * 10})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "cardinality": 5},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert len(checks) == 1
        assert checks[0].passed is False

    def test_more_unique_fails(self):
        """Contract 3C row 3: 5 declared, 6 actual (dirty data) → fails."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B", "C", "D", "E", "F"] * 5})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "cardinality": 5},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert checks[0].passed is False

    def test_multiple_cols_both_match(self):
        """Contract 3C row 4: 2 cols, both match → 2 checks, both passed."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B"] * 10, "s": ["X", "Y", "Z", "X"] * 5})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "cardinality": 2},
            {"name": "s", "type": "categorical", "cardinality": 3},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert len(checks) == 2
        assert all(c.passed for c in checks)

    def test_multiple_cols_one_mismatch(self):
        """Contract 3C row 5: 2 cols, one mismatch → 2 checks, one fails."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B"] * 10, "s": ["X", "Y"] * 10})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "cardinality": 2},
            {"name": "s", "type": "categorical", "cardinality": 3},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert len(checks) == 2
        passing = [c for c in checks if c.passed]
        failing = [c for c in checks if not c.passed]
        assert len(passing) == 1
        assert len(failing) == 1

    def test_no_categorical_columns(self):
        """Contract 3C row 6: no categorical columns in meta → empty list."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"m": range(10)})
        meta = {"columns": [{"name": "m", "type": "measure"}]}
        checks = check_categorical_cardinality(df, meta)
        assert checks == []

    def test_column_missing_from_df_raises(self):
        """Contract 3C row 7: column in meta but missing from df → KeyError."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"other": range(10)})
        meta = {"columns": [
            {"name": "missing_col", "type": "categorical", "cardinality": 3},
        ]}
        with pytest.raises(KeyError):
            check_categorical_cardinality(df, meta)


# =====================================================================
# 1. CONTRACT TESTS — Orthogonal Independence (8.2.5) — Table 3D
# =====================================================================

class TestOrthogonalIndependenceContract:
    """Contract tests for check_orthogonal_independence [Subtask 8.2.5]."""

    def test_independent_columns_pass(self, meta_with_orthogonal):
        """Contract 3D row 1: truly independent columns → p > 0.05 → passes."""
        # [Subtask 8.2.5]
        rng = np.random.default_rng(42)
        n = 2000
        df = pd.DataFrame({
            "root_e": rng.choice(["A", "B", "C"], n),
            "root_p": rng.choice(["X", "Y"], n),
        })
        checks = check_orthogonal_independence(df, meta_with_orthogonal)
        assert len(checks) == 1
        assert checks[0].passed is True

    def test_correlated_columns_fail(self, meta_with_orthogonal):
        """Contract 3D row 2: correlated columns (A→X, B→Y) → p < 0.05 → fails."""
        # [Subtask 8.2.5]
        df = pd.DataFrame({
            "root_e": ["A"] * 500 + ["B"] * 500,
            "root_p": ["X"] * 500 + ["Y"] * 500,
        })
        checks = check_orthogonal_independence(df, meta_with_orthogonal)
        assert len(checks) == 1
        assert checks[0].passed is False

    def test_two_orthogonal_pairs(self):
        """Contract 3D row 3: two orthogonal pairs → 2 Check objects."""
        # [Subtask 8.2.5]
        rng = np.random.default_rng(99)
        n = 1000
        df = pd.DataFrame({
            "ra": rng.choice(["A", "B"], n),
            "rb": rng.choice(["X", "Y"], n),
            "rc": rng.choice(["M", "N"], n),
        })
        meta = {
            "orthogonal_groups": [
                {"group_a": "g1", "group_b": "g2", "rationale": "t1"},
                {"group_a": "g1", "group_b": "g3", "rationale": "t2"},
            ],
            "dimension_groups": {
                "g1": {"columns": ["ra"], "hierarchy": ["ra"]},
                "g2": {"columns": ["rb"], "hierarchy": ["rb"]},
                "g3": {"columns": ["rc"], "hierarchy": ["rc"]},
            },
        }
        checks = check_orthogonal_independence(df, meta)
        assert len(checks) == 2

    def test_no_orthogonal_pairs_empty(self):
        """Contract 3D row 4: no orthogonal pairs → empty list."""
        # [Subtask 8.2.5]
        df = pd.DataFrame({"a": [1]})
        checks = check_orthogonal_independence(df, {"orthogonal_groups": []})
        assert checks == []

    def test_single_value_column_fails(self, meta_with_orthogonal):
        """Contract 3D row 5: single-value column → degenerate table → fails."""
        # [Subtask 8.2.5]
        df = pd.DataFrame({
            "root_e": ["A"] * 100,
            "root_p": ["X", "Y"] * 50,
        })
        checks = check_orthogonal_independence(df, meta_with_orthogonal)
        assert len(checks) == 1
        assert checks[0].passed is False
        assert "Degenerate" in checks[0].detail

    def test_missing_group_raises_key_error(self):
        """Contract 3D row 6: group_a not in dimension_groups → KeyError."""
        # [Subtask 8.2.5]
        meta = {
            "orthogonal_groups": [
                {"group_a": "missing_group", "group_b": "p", "rationale": "t"},
            ],
            "dimension_groups": {
                "p": {"columns": ["rp"], "hierarchy": ["rp"]},
            },
        }
        with pytest.raises(KeyError):
            check_orthogonal_independence(
                pd.DataFrame({"rp": ["X", "Y"]}), meta,
            )


# =====================================================================
# 1. CONTRACT TESTS — Measure DAG Acyclicity (8.2.6) — Table 3E
# =====================================================================

class TestMeasureDagAcyclicContract:
    """Contract tests for check_measure_dag_acyclic [Subtask 8.2.6]."""

    def test_unique_nodes_passes(self):
        """Contract 3E row 1: unique node list → passed=True."""
        # [Subtask 8.2.6]
        c = check_measure_dag_acyclic(
            {"measure_dag_order": ["wait_minutes", "cost", "satisfaction"]}
        )
        assert c.passed is True
        assert c.name == "measure_dag_acyclic"

    def test_empty_list_passes(self):
        """Contract 3E row 2: empty measure list → passed=True."""
        # [Subtask 8.2.6]
        c = check_measure_dag_acyclic({"measure_dag_order": []})
        assert c.passed is True

    def test_duplicate_node_fails(self):
        """Contract 3E row 3: repeated node → passed=False."""
        # [Subtask 8.2.6]
        c = check_measure_dag_acyclic(
            {"measure_dag_order": ["cost", "cost"]}
        )
        assert c.passed is False

    def test_missing_key_defaults_to_pass(self):
        """Contract 3E row 4: no 'measure_dag_order' key → defaults empty → passes."""
        # [Subtask 8.2.6]
        c = check_measure_dag_acyclic({})
        assert c.passed is True


# =====================================================================
# 2. INPUT VALIDATION TESTS
# =====================================================================

class TestCheckInputValidation:
    """Input edge cases for Check dataclass [Subtask 8.1.1]."""

    @pytest.mark.parametrize("passed_val", [True, False])
    def test_check_passed_is_python_bool(self, passed_val):
        """Verify passed field stores Python bool, not numpy.bool_."""
        # [Subtask 8.1.1]
        c = Check("test", passed_val)
        assert type(c.passed) is bool

    def test_check_with_none_detail(self):
        """Explicit None detail is the same as omitting it."""
        # [Subtask 8.1.1]
        c = Check("test", True, None)
        assert c.detail is None

    def test_check_with_long_detail(self):
        """Detail can be an arbitrarily long string."""
        # [Subtask 8.1.1]
        detail = "x" * 10_000
        c = Check("test", True, detail)
        assert len(c.detail) == 10_000


class TestRowCountInputValidation:
    """Input validation for check_row_count [Subtask 8.2.1]."""

    def test_target_rows_is_one(self):
        """Boundary: target=1, actual=1 → passes."""
        # [Subtask 8.2.1]
        c = check_row_count(pd.DataFrame({"x": [1]}), {"total_rows": 1})
        assert c.passed is True

    def test_over_target_by_just_under_10_percent(self):
        """Boundary: 549/500 = 9.8% → passes."""
        # [Subtask 8.2.1]
        c = check_row_count(
            pd.DataFrame({"x": range(549)}), {"total_rows": 500},
        )
        assert c.passed is True


class TestCardinalityInputValidation:
    """Input validation for check_categorical_cardinality [Subtask 8.2.2]."""

    def test_no_columns_key_returns_empty(self):
        """Meta without 'columns' key → returns empty list (not error)."""
        # [Subtask 8.2.2]
        checks = check_categorical_cardinality(pd.DataFrame({"x": [1]}), {})
        assert checks == []

    def test_values_fallback_for_cardinality(self):
        """When 'cardinality' key absent, falls back to len(values)."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B", "C"] * 5})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "values": ["A", "B", "C"]},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert len(checks) == 1
        assert checks[0].passed is True

    def test_neither_cardinality_nor_values_skips(self):
        """Column with no cardinality or values field is skipped silently."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A"] * 5})
        meta = {"columns": [{"name": "h", "type": "categorical"}]}
        checks = check_categorical_cardinality(df, meta)
        assert checks == []


# =====================================================================
# 3. OUTPUT CORRECTNESS TESTS
# =====================================================================

class TestCheckOutputCorrectness:
    """Output correctness for Check [Subtask 8.1.1]."""

    def test_check_fields_have_correct_types(self):
        """Verify all field types match the dataclass annotation."""
        # [Subtask 8.1.1]
        c = Check("test", True, "detail")
        assert isinstance(c.name, str)
        assert isinstance(c.passed, bool)
        assert isinstance(c.detail, str)

    def test_check_is_dataclass(self):
        """Check is a dataclass — has __dataclass_fields__."""
        # [Subtask 8.1.1]
        import dataclasses
        assert dataclasses.is_dataclass(Check)


class TestValidationReportOutputCorrectness:
    """Output correctness for ValidationReport [Subtask 8.1.2]."""

    def test_all_passed_returns_python_bool(self):
        """all_passed property returns Python bool, not numpy bool."""
        # [Subtask 8.1.2]
        r = ValidationReport(checks=[Check("a", True)])
        assert type(r.all_passed) is bool

    def test_failures_returns_new_list(self):
        """failures property returns a new list — mutating it does not
        affect the report's internal state."""
        # [Subtask 8.1.2]
        r = ValidationReport(checks=[Check("a", False)])
        failures = r.failures
        failures.clear()
        # Internal state should still have the failure
        assert len(r.failures) == 1

    def test_failures_list_contains_only_failing_checks(self):
        """failures list excludes passing checks."""
        # [Subtask 8.1.2]
        fail1 = Check("f1", False)
        fail2 = Check("f2", False)
        r = ValidationReport(checks=[
            Check("ok", True), fail1, Check("ok2", True), fail2,
        ])
        assert set(id(f) for f in r.failures) == {id(fail1), id(fail2)}


class TestRowCountOutputCorrectness:
    """Output correctness for check_row_count [Subtask 8.2.1]."""

    def test_returns_check_type(self, df_n, meta_500):
        """Return value is a Check instance."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(500), meta_500)
        assert isinstance(c, Check)

    def test_check_name_is_row_count(self, df_n, meta_500):
        """Check name is always 'row_count'."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(500), meta_500)
        assert c.name == "row_count"

    def test_detail_contains_actual_and_target(self, df_n, meta_500):
        """Detail string includes actual count and target for debugging."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(480), meta_500)
        assert "480" in c.detail
        assert "500" in c.detail

    def test_passed_is_python_bool(self, df_n, meta_500):
        """passed field is Python bool, not numpy.bool_."""
        # [Subtask 8.2.1]
        c = check_row_count(df_n(480), meta_500)
        assert type(c.passed) is bool


class TestCardinalityOutputCorrectness:
    """Output correctness for check_categorical_cardinality [Subtask 8.2.2]."""

    def test_returns_list_of_checks(self):
        """Return value is a list of Check instances."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B"] * 5})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "cardinality": 2},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert isinstance(checks, list)
        assert all(isinstance(c, Check) for c in checks)

    def test_check_names_include_column_name(self):
        """Check names follow 'cardinality_{col_name}' pattern."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"my_col": ["A", "B"] * 5})
        meta = {"columns": [
            {"name": "my_col", "type": "categorical", "cardinality": 2},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert checks[0].name == "cardinality_my_col"

    def test_passed_is_python_bool(self):
        """passed field is Python bool for cardinality checks."""
        # [Subtask 8.2.2]
        df = pd.DataFrame({"h": ["A", "B"] * 5})
        meta = {"columns": [
            {"name": "h", "type": "categorical", "cardinality": 2},
        ]}
        checks = check_categorical_cardinality(df, meta)
        assert type(checks[0].passed) is bool


class TestOrthogonalOutputCorrectness:
    """Output correctness for check_orthogonal_independence [Subtask 8.2.5]."""

    def test_check_names_include_root_columns(self, meta_with_orthogonal):
        """Check names follow 'orthogonal_{root_a}_{root_b}' pattern."""
        # [Subtask 8.2.5]
        rng = np.random.default_rng(42)
        df = pd.DataFrame({
            "root_e": rng.choice(["A", "B"], 500),
            "root_p": rng.choice(["X", "Y"], 500),
        })
        checks = check_orthogonal_independence(df, meta_with_orthogonal)
        assert checks[0].name == "orthogonal_root_e_root_p"

    def test_detail_contains_p_value(self, meta_with_orthogonal):
        """Detail string includes chi-squared p-value."""
        # [Subtask 8.2.5]
        rng = np.random.default_rng(42)
        df = pd.DataFrame({
            "root_e": rng.choice(["A", "B"], 500),
            "root_p": rng.choice(["X", "Y"], 500),
        })
        checks = check_orthogonal_independence(df, meta_with_orthogonal)
        assert "p=" in checks[0].detail

    def test_passed_is_python_bool(self, meta_with_orthogonal):
        """passed field is Python bool after chi-squared comparison."""
        # [Subtask 8.2.5]
        rng = np.random.default_rng(42)
        df = pd.DataFrame({
            "root_e": rng.choice(["A", "B"], 500),
            "root_p": rng.choice(["X", "Y"], 500),
        })
        checks = check_orthogonal_independence(df, meta_with_orthogonal)
        assert type(checks[0].passed) is bool


class TestDagAcyclicOutputCorrectness:
    """Output correctness for check_measure_dag_acyclic [Subtask 8.2.6]."""

    def test_returns_single_check(self):
        """Returns a single Check, not a list."""
        # [Subtask 8.2.6]
        c = check_measure_dag_acyclic({"measure_dag_order": ["a", "b"]})
        assert isinstance(c, Check)

    def test_check_name_is_measure_dag_acyclic(self):
        """Check name is always 'measure_dag_acyclic'."""
        # [Subtask 8.2.6]
        c = check_measure_dag_acyclic({"measure_dag_order": []})
        assert c.name == "measure_dag_acyclic"

    def test_detail_contains_count(self):
        """Detail reports the number of measures."""
        # [Subtask 8.2.6]
        c = check_measure_dag_acyclic(
            {"measure_dag_order": ["a", "b", "c"]}
        )
        assert "3" in c.detail


# =====================================================================
# 4. STATE TRANSITION TESTS
# =====================================================================

class TestValidationReportStateTransitions:
    """State transition tests for ValidationReport [Subtask 8.1.2]."""

    def test_add_checks_accumulates_across_calls(self):
        """Multiple add_checks calls accumulate, not overwrite."""
        # [Subtask 8.1.2]
        r = ValidationReport()
        r.add_checks([Check("L1_1", True)])
        r.add_checks([Check("L1_2", False)])
        r.add_checks([Check("L2_1", True)])
        assert len(r.checks) == 3
        assert r.all_passed is False

    def test_fresh_report_has_no_leakage(self):
        """Two distinct reports have independent check lists."""
        # [Subtask 8.1.2]
        r1 = ValidationReport()
        r2 = ValidationReport()
        r1.add_checks([Check("a", True)])
        assert len(r2.checks) == 0

    def test_all_passed_recomputes_after_add(self):
        """all_passed updates dynamically after checks are added."""
        # [Subtask 8.1.2]
        r = ValidationReport()
        assert r.all_passed is True
        r.add_checks([Check("ok", True)])
        assert r.all_passed is True
        r.add_checks([Check("bad", False)])
        assert r.all_passed is False


# =====================================================================
# 5. INTEGRATION TESTS — validator against real simulator output
# =====================================================================

class TestValidatorIntegration:
    """Integration tests: L1 checks against real FactTableSimulator output."""

    def test_row_count_on_real_generate(self):
        """check_row_count passes on actual generate() output [Subtask 8.2.1]."""
        from agpds import FactTableSimulator
        sim = FactTableSimulator(200, 42)
        sim.add_category("h", ["A", "B", "C"], [1, 1, 1], "entity")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        df, meta = sim.generate()
        c = check_row_count(df, meta)
        assert c.passed is True

    def test_dag_acyclic_on_real_generate(self):
        """check_measure_dag_acyclic passes on actual metadata [Subtask 8.2.6]."""
        from agpds import FactTableSimulator
        sim = FactTableSimulator(100, 42)
        sim.add_category("h", ["A", "B"], [1, 1], "entity")
        sim.add_measure("wm", "gaussian", {"mu": 50, "sigma": 10})
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        _, meta = sim.generate()
        c = check_measure_dag_acyclic(meta)
        assert c.passed is True

    def test_orthogonal_check_on_real_generate(self):
        """check_orthogonal_independence passes on correctly generated
        orthogonal groups [Subtask 8.2.5]."""
        from agpds import FactTableSimulator
        sim = FactTableSimulator(1000, 42)
        sim.add_category("h", ["A", "B", "C"], [1, 1, 1], "entity")
        sim.add_category("s", ["X", "Y"], [1, 1], "patient")
        sim.declare_orthogonal("entity", "patient", "independent dims")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        df, meta = sim.generate()
        checks = check_orthogonal_independence(df, meta)
        assert len(checks) == 1
        assert checks[0].passed is True

    def test_full_l1_report_on_real_generate(self):
        """Combine all L1 checks into a single ValidationReport and verify
        all pass on a well-formed simulator output [Subtask 8.1.2]."""
        from agpds import FactTableSimulator
        sim = FactTableSimulator(500, 42)
        sim.add_category("h", ["A", "B", "C"], [1, 1, 1], "entity")
        sim.add_category("s", ["X", "Y"], [1, 1], "patient")
        sim.declare_orthogonal("entity", "patient", "indep")
        sim.add_temporal("dt", "2024-01-01", "2024-06-30", "daily")
        df, meta = sim.generate()

        report = ValidationReport()
        report.add_checks([check_row_count(df, meta)])
        report.add_checks(check_orthogonal_independence(df, meta))
        report.add_checks([check_measure_dag_acyclic(meta)])
        # cardinality check requires meta["columns"] which Sprint 5 doesn't emit
        assert report.all_passed is True
