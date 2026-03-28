"""
Sprint 2 — Comprehensive test suite for FactTableSimulator column declaration API.

Modules under test: agpds/simulator.py (add_category, add_temporal)
Subtask IDs covered: 1.2.1–1.2.6, 1.3.1–1.3.4

Test categories (in order):
  1. Contract tests — one test per contract table row (1–50)
  2. Input validation tests — exhaustive type/boundary/constraint checks
  3. Output correctness tests — return types, numerical accuracy, immutability
  4. State transition tests — registry state, ordering, instance isolation
  5. Integration tests — Sprint 1 ↔ Sprint 2 interface boundary
"""
from __future__ import annotations

import copy
import math
from collections import OrderedDict
from datetime import date

import pytest

from agpds.exceptions import (
    DuplicateColumnError,
    DuplicateGroupRootError,
    EmptyValuesError,
    InvalidParameterError,
    ParentNotFoundError,
    SimulatorError,
    WeightLengthMismatchError,
)
from agpds.models import DimensionGroup
from agpds.simulator import FactTableSimulator


# ===== Shared Fixtures =====


@pytest.fixture
def sim() -> FactTableSimulator:
    """Fresh simulator for each test — no leakage between tests."""
    return FactTableSimulator(target_rows=500, seed=42)


@pytest.fixture
def sim_with_root(sim: FactTableSimulator) -> FactTableSimulator:
    """Simulator with root 'hospital' (5 values) in group 'entity'."""
    sim.add_category(
        "hospital",
        values=["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
        weights=[0.25, 0.20, 0.20, 0.20, 0.15],
        group="entity",
    )
    return sim


@pytest.fixture
def sim_with_hierarchy(sim_with_root: FactTableSimulator) -> FactTableSimulator:
    """Simulator with root 'hospital' and child 'department' in 'entity'."""
    sim_with_root.add_category(
        "department",
        values=["Internal", "Surgery", "Pediatrics", "Emergency"],
        weights=[0.35, 0.25, 0.15, 0.25],
        group="entity",
        parent="hospital",
    )
    return sim_with_root


# Convenience: the 5 hospital values used in fixtures
HOSPITAL_VALUES = ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"]


# =====================================================================
# 1. CONTRACT TESTS — One test per contract table row (1–50)
# =====================================================================


class TestContractAddCategory:
    """Contract rows 1–30: add_category scenarios from the Message 1 table."""

    # ----- Happy paths (rows 1–6) -----

    def test_row01_valid_root_3_values_normalized_weights(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 1: Valid root, 3 values, already-normalized weights.
        [Subtask 1.2.1, 1.2.2, 1.2.5]
        """
        sim.add_category("hospital", ["A", "B", "C"], [0.4, 0.3, 0.3], "entity")

        assert "hospital" in sim._columns
        assert sim._groups["entity"].root == "hospital"
        assert sim._columns["hospital"]["weights"] == pytest.approx(
            [0.4, 0.3, 0.3]
        )

    def test_row02_auto_normalization_unnormalized_weights(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 2: Unnormalized [1,2,3,4,5] → auto-normalized to sum=1.0.
        [Subtask 1.2.2]
        """
        sim.add_category(
            "hospital", ["A", "B", "C", "D", "E"], [1, 2, 3, 4, 5], "entity"
        )
        w = sim._columns["hospital"]["weights"]
        assert sum(w) == pytest.approx(1.0)
        assert w == pytest.approx([1 / 15, 2 / 15, 3 / 15, 4 / 15, 5 / 15])

    def test_row03_valid_child_after_root(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 3: Valid child after root exists in same group.
        [Subtask 1.2.4, 1.2.5]
        """
        sim_with_root.add_category(
            "dept", ["X", "Y"], [0.5, 0.5], "entity", parent="hospital"
        )
        assert "dept" in sim_with_root._columns
        assert sim_with_root._columns["dept"]["parent"] == "hospital"

    def test_row04_per_parent_dict_valid(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 4: Per-parent dict, all keys present, vectors correct length.
        [Subtask 1.2.3]
        """
        per_parent = {v: [1, 1, 1, 1] for v in HOSPITAL_VALUES}
        sim_with_root.add_category(
            "dept", ["W", "X", "Y", "Z"], per_parent, "entity", parent="hospital"
        )
        stored = sim_with_root._columns["dept"]["weights"]
        for v in HOSPITAL_VALUES:
            assert stored[v] == pytest.approx([0.25] * 4)

    def test_row05_flat_weights_with_parent_broadcast(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 5: Flat weights with parent → stored as flat list for broadcast.
        [Subtask 1.2.1, 1.2.2]
        """
        sim_with_root.add_category(
            "dept", ["X", "Y"], [0.6, 0.4], "entity", parent="hospital"
        )
        w = sim_with_root._columns["dept"]["weights"]
        assert isinstance(w, list)
        assert w == pytest.approx([0.6, 0.4])

    def test_row06_second_group_independent_root(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 6: Independent root in a second group 'patient'.
        [Subtask 1.2.5]
        """
        sim_with_root.add_category(
            "severity", ["Mild", "Moderate", "Severe"], [0.5, 0.35, 0.15], "patient"
        )
        assert "patient" in sim_with_root._groups
        assert sim_with_root._groups["patient"].root == "severity"

    # ----- Empty / boundary (rows 7–10) -----

    def test_row07_empty_values_raises_empty_values_error(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 7: Empty values list raises EmptyValuesError.
        [Subtask 1.2.1]
        """
        with pytest.raises(EmptyValuesError):
            sim.add_category("x", [], [], "g")

    def test_row08_single_value_rejected_a9(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 8: Single value rejected per [A9] minimum 2.
        [Subtask 1.2.1]
        """
        with pytest.raises(InvalidParameterError, match="at least 2"):
            sim.add_category("x", ["A"], [1.0], "g")

    def test_row09_two_values_one_weight_mismatch(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 9: 2 values, 1 weight → WeightLengthMismatchError.
        [Subtask 1.2.1]
        """
        with pytest.raises(WeightLengthMismatchError):
            sim.add_category("x", ["A", "B"], [1.0], "g")

    def test_row10_one_value_two_weights_a9_fires_first(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 10: 1 value + 2 weights → A9 check (len<2) fires before length check.
        [Subtask 1.2.1]
        """
        with pytest.raises(InvalidParameterError):
            sim.add_category("x", ["A"], [0.5, 0.5], "g")

    # ----- Type mismatches (rows 11–15) -----

    def test_row11_name_not_str(self, sim: FactTableSimulator) -> None:
        """Row 11: name=123 raises TypeError. [Subtask 1.2.1]"""
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_category(123, ["A", "B"], [0.5, 0.5], "g")  # type: ignore[arg-type]

    def test_row12_values_is_str_not_list(self, sim: FactTableSimulator) -> None:
        """Row 12: values='AB' raises TypeError. [Subtask 1.2.1]"""
        with pytest.raises(TypeError, match="values must be a list"):
            sim.add_category("x", "AB", [0.5, 0.5], "g")  # type: ignore[arg-type]

    def test_row13_weights_is_str(self, sim: FactTableSimulator) -> None:
        """Row 13: weights='bad' raises TypeError. [Subtask 1.2.1]"""
        with pytest.raises(TypeError, match="weights must be a list or dict"):
            sim.add_category("x", ["A", "B"], "bad", "g")  # type: ignore[arg-type]

    def test_row14_group_not_str(self, sim: FactTableSimulator) -> None:
        """Row 14: group=42 raises TypeError. [Subtask 1.2.1]"""
        with pytest.raises(TypeError, match="group must be a str"):
            sim.add_category("x", ["A", "B"], [0.5, 0.5], 42)  # type: ignore[arg-type]

    def test_row15_parent_not_str_or_none(self, sim: FactTableSimulator) -> None:
        """Row 15: parent=42 raises TypeError. [Subtask 1.2.1]"""
        with pytest.raises(TypeError, match="parent must be a str or None"):
            sim.add_category("x", ["A", "B"], [0.5, 0.5], "g", parent=42)  # type: ignore[arg-type]

    # ----- Duplicate / collision (rows 16–18) -----

    def test_row16_duplicate_column_name_raises(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 16: Same column name declared twice. [Subtask 1.2.1]"""
        with pytest.raises(DuplicateColumnError):
            sim_with_root.add_category(
                "hospital", ["X", "Y"], [0.5, 0.5], "other"
            )

    def test_row17_duplicate_root_in_group_raises(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 17: Second root (parent=None) in same group. [Subtask 1.2.6]"""
        with pytest.raises(DuplicateGroupRootError):
            sim_with_root.add_category(
                "region", ["R1", "R2"], [0.5, 0.5], "entity"
            )

    def test_row18_reserved_group_time(self, sim: FactTableSimulator) -> None:
        """Row 18: group='time' is reserved for temporal. [A10]
        [Subtask 1.2.1]
        """
        with pytest.raises(ValueError, match="reserved"):
            sim.add_category("x", ["A", "B"], [0.5, 0.5], "time")

    # ----- Weight constraint violations (rows 19–20) -----

    def test_row19_negative_weight_raises(self, sim: FactTableSimulator) -> None:
        """Row 19: Negative weight raises ValueError. [Subtask 1.2.1]"""
        with pytest.raises(ValueError, match="negative"):
            sim.add_category("x", ["A", "B"], [-1.0, 2.0], "g")

    def test_row20_all_zero_weights_raises(self, sim: FactTableSimulator) -> None:
        """Row 20: All-zero weights raises ValueError. [Subtask 1.2.1]"""
        with pytest.raises(ValueError, match="zero"):
            sim.add_category("x", ["A", "B"], [0.0, 0.0], "g")

    # ----- Parent constraint violations (rows 21–22) -----

    def test_row21_parent_not_declared_raises(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 21: Parent column not declared at all. [Subtask 1.2.4]"""
        with pytest.raises(ParentNotFoundError):
            sim.add_category(
                "dept", ["X", "Y"], [0.5, 0.5], "entity", parent="nonexistent"
            )

    def test_row22_parent_in_different_group_raises(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 22: Parent exists but in a different group. [Subtask 1.2.4]"""
        sim_with_root.add_category(
            "severity", ["Mild", "Moderate", "Severe"], [0.5, 0.35, 0.15], "patient"
        )
        with pytest.raises(ParentNotFoundError):
            sim_with_root.add_category(
                "dept", ["X", "Y"], [0.5, 0.5], "entity", parent="severity"
            )

    # ----- Per-parent dict edge cases (rows 23–28) -----

    def test_row23_extra_key_not_in_parent_values(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 23: Dict has all valid keys plus one unknown key. [Subtask 1.2.3]"""
        weights = {v: [0.5, 0.5] for v in HOSPITAL_VALUES}
        weights["UNKNOWN"] = [0.5, 0.5]
        with pytest.raises(ValueError, match="not in parent"):
            sim_with_root.add_category(
                "dept", ["X", "Y"], weights, "entity", parent="hospital"
            )

    def test_row24_missing_parent_key_a6(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 24: Dict missing parent value key → ValueError. [Subtask 1.2.3, A6]"""
        with pytest.raises(ValueError, match="missing keys"):
            sim_with_root.add_category(
                "dept", ["X", "Y"],
                {"Xiehe": [0.5, 0.5]},
                "entity", parent="hospital",
            )

    def test_row25_per_parent_vector_length_mismatch(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 25: One parent's vector has wrong length. [Subtask 1.2.3]"""
        weights = {v: [0.5, 0.5] for v in HOSPITAL_VALUES}
        weights["Xiehe"] = [1.0]  # length 1, should be 2
        with pytest.raises(WeightLengthMismatchError):
            sim_with_root.add_category(
                "dept", ["X", "Y"], weights, "entity", parent="hospital"
            )

    def test_row26_one_parent_all_zero_weights(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 26: One parent's weights all zero. [Subtask 1.2.3]"""
        weights = {v: [0.5, 0.5] for v in HOSPITAL_VALUES}
        weights["Xiehe"] = [0.0, 0.0]
        with pytest.raises(ValueError, match="zero"):
            sim_with_root.add_category(
                "dept", ["X", "Y"], weights, "entity", parent="hospital"
            )

    def test_row27_negative_in_per_parent_vector(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 27: Negative weight in one per-parent vector. [Subtask 1.2.3]"""
        weights = {v: [0.5, 0.5] for v in HOSPITAL_VALUES}
        weights["Xiehe"] = [-1.0, 2.0]
        with pytest.raises(ValueError, match="negative"):
            sim_with_root.add_category(
                "dept", ["X", "Y"], weights, "entity", parent="hospital"
            )

    def test_row28_empty_dict_with_parent(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Row 28: Empty per-parent dict. [Subtask 1.2.3]"""
        with pytest.raises(ValueError, match="empty"):
            sim_with_root.add_category(
                "dept", ["X", "Y"], {}, "entity", parent="hospital"
            )

    # ----- Group registry state (rows 29–30) -----

    def test_row29_entity_group_root_and_child(
        self, sim_with_hierarchy: FactTableSimulator
    ) -> None:
        """Row 29: After root+child, group state matches spec. [Subtask 1.2.5]"""
        grp = sim_with_hierarchy._groups["entity"]
        assert grp.root == "hospital"
        assert grp.columns == ["hospital", "department"]
        assert grp.hierarchy == ["hospital", "department"]

    def test_row30_new_group_patient(self, sim: FactTableSimulator) -> None:
        """Row 30: New group 'patient' created with root 'severity'. [Subtask 1.2.5]"""
        sim.add_category(
            "severity", ["Mild", "Moderate", "Severe"], [0.5, 0.35, 0.15], "patient"
        )
        grp = sim._groups["patient"]
        assert grp.root == "severity"
        assert grp.columns == ["severity"]


class TestContractAddTemporal:
    """Contract rows 31–50: add_temporal scenarios from the Message 1 table."""

    # ----- Happy paths (rows 31–34) -----

    def test_row31_full_valid_call_with_derive(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 31: Full valid call with two derive tokens. [Subtask 1.3.1–1.3.4]

        §2.6 defines temporal derive columns as deterministic features that
        belong to ``columns`` but NOT to ``hierarchy`` (hierarchy is root-only
        for the "time" group).  See test_models.py contract and audit/phase_2.md.
        """
        sim.add_temporal(
            "visit_date", "2024-01-01", "2024-06-30", "daily",
            ["day_of_week", "month"],
        )
        assert "visit_date" in sim._columns
        assert sim._columns["visit_date"]["type"] == "temporal"
        assert "day_of_week" in sim._columns
        assert "month" in sim._columns
        grp = sim._groups["time"]
        assert grp.root == "visit_date"
        assert grp.hierarchy == ["visit_date"]
        assert set(grp.columns) == {"visit_date", "day_of_week", "month"}
        assert sim._columns["day_of_week"]["parent"] == "visit_date"
        assert sim._columns["month"]["parent"] == "visit_date"

    def test_row32_no_derive_default(self, sim: FactTableSimulator) -> None:
        """Row 32: No derive (empty default) — only root registered. [Subtask 1.3.1]"""
        sim.add_temporal("ts", "2024-01-01", "2024-12-31", "daily")
        assert sim._groups["time"].columns == ["ts"]

    def test_row33_non_daily_freq_stored_as_is(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 33: Non-daily freq='weekly' stored as-is. [Subtask 1.3.2, B1]"""
        sim.add_temporal(
            "d", "2024-01-01", "2024-06-30", "weekly", ["quarter", "is_weekend"]
        )
        assert sim._columns["d"]["freq"] == "weekly"

    def test_row34_minimum_one_day_range(self, sim: FactTableSimulator) -> None:
        """Row 34: Minimum range (1 day) succeeds. [Subtask 1.3.1]"""
        sim.add_temporal("d", "2024-01-01", "2024-01-02", "daily")
        assert "d" in sim._columns

    # ----- Invalid dates (rows 35–38) -----

    def test_row35_inverted_dates_raises(self, sim: FactTableSimulator) -> None:
        """Row 35: end < start. [Subtask 1.3.1]"""
        with pytest.raises(ValueError, match="strictly after"):
            sim.add_temporal("d", "2024-06-30", "2024-01-01", "daily")

    def test_row36_same_date_raises(self, sim: FactTableSimulator) -> None:
        """Row 36: end == start. [Subtask 1.3.1]"""
        with pytest.raises(ValueError, match="strictly after"):
            sim.add_temporal("d", "2024-01-01", "2024-01-01", "daily")

    def test_row37_unparseable_start_raises(self, sim: FactTableSimulator) -> None:
        """Row 37: start='not-a-date'. [Subtask 1.3.1]"""
        with pytest.raises(ValueError, match="Cannot parse"):
            sim.add_temporal("d", "not-a-date", "2024-06-30", "daily")

    def test_row38_unparseable_end_raises(self, sim: FactTableSimulator) -> None:
        """Row 38: end='not-a-date'. [Subtask 1.3.1]"""
        with pytest.raises(ValueError, match="Cannot parse"):
            sim.add_temporal("d", "2024-01-01", "not-a-date", "daily")

    # ----- Frequency validation (row 39) -----

    def test_row39_empty_freq_raises(self, sim: FactTableSimulator) -> None:
        """Row 39: Empty freq string. [Subtask 1.3.2]"""
        with pytest.raises(ValueError, match="non-empty"):
            sim.add_temporal("d", "2024-01-01", "2024-06-30", "")

    # ----- Derive whitelist (rows 40–42) -----

    def test_row40_unknown_derive_token_raises(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 40: 'fiscal_year' not in whitelist. [Subtask 1.3.3]"""
        with pytest.raises(ValueError, match="Unknown derive token"):
            sim.add_temporal(
                "d", "2024-01-01", "2024-06-30", "daily", ["fiscal_year"]
            )

    def test_row41_all_four_valid_derive_tokens(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 41: All 4 whitelist tokens accepted. [Subtask 1.3.3]"""
        sim.add_temporal(
            "d", "2024-01-01", "2024-06-30", "daily",
            ["day_of_week", "month", "quarter", "is_weekend"],
        )
        for tok in ["day_of_week", "month", "quarter", "is_weekend"]:
            assert tok in sim._columns

    def test_row42_duplicate_derive_token_raises(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 42: Duplicate derive token. [Subtask 1.3.3]"""
        with pytest.raises(ValueError, match="Duplicate derive token"):
            sim.add_temporal(
                "d", "2024-01-01", "2024-06-30", "daily",
                ["day_of_week", "day_of_week"],
            )

    # ----- Singleton / collision (rows 43–45) -----

    def test_row43_second_add_temporal_raises(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 43: Second add_temporal call. [A10, Subtask 1.3.4]"""
        sim.add_temporal("d1", "2024-01-01", "2024-06-30", "daily")
        with pytest.raises(ValueError, match="Only one add_temporal"):
            sim.add_temporal("d2", "2024-07-01", "2024-12-31", "daily")

    def test_row44_category_with_time_group_blocks_temporal(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 44: add_category group='time' then add_temporal. [A10]"""
        # add_category rejects group='time' directly due to reservation
        with pytest.raises(ValueError, match="reserved"):
            sim.add_category("x", ["A", "B"], [0.5, 0.5], "time")

    def test_row45_temporal_then_category_with_time_group(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 45: add_temporal then add_category group='time'. [A10]"""
        sim.add_temporal("d", "2024-01-01", "2024-06-30", "daily")
        with pytest.raises(ValueError, match="reserved"):
            sim.add_category("x", ["A", "B"], [0.5, 0.5], "time")

    # ----- Duplicate column names (rows 46–47) -----

    def test_row46_temporal_root_name_collision(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 46: Root name collides with existing category. [Subtask 1.3.1]"""
        sim.add_category("visit_date", ["A", "B"], [0.5, 0.5], "some_group")
        with pytest.raises(DuplicateColumnError):
            sim.add_temporal("visit_date", "2024-01-01", "2024-06-30", "daily")

    def test_row47_derived_name_collision(self, sim: FactTableSimulator) -> None:
        """Row 47: Derived column name collides with category. [Subtask 1.3.3]"""
        sim.add_category("month", ["Jan", "Feb"], [0.5, 0.5], "grp")
        with pytest.raises(DuplicateColumnError):
            sim.add_temporal(
                "d", "2024-01-01", "2024-06-30", "daily", ["month"]
            )

    # ----- Type mismatches (rows 48–49) -----

    def test_row48_name_not_str(self, sim: FactTableSimulator) -> None:
        """Row 48: name=123. [Subtask 1.3.1]"""
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_temporal(123, "2024-01-01", "2024-06-30", "daily")  # type: ignore[arg-type]

    def test_row49_derive_is_str_not_list(self, sim: FactTableSimulator) -> None:
        """Row 49: derive='month'. [Subtask 1.3.1]"""
        with pytest.raises(TypeError, match="derive must be a list"):
            sim.add_temporal(
                "d", "2024-01-01", "2024-06-30", "daily", "month"  # type: ignore[arg-type]
            )

    # ----- Group state (row 50) -----

    def test_row50_time_group_state_after_temporal(
        self, sim: FactTableSimulator
    ) -> None:
        """Row 50: Group 'time' has correct root, columns, hierarchy. [Subtask 1.3.4]

        §2.6: temporal derive columns are in ``columns`` but NOT in
        ``hierarchy`` — hierarchy is root-only for the "time" group.
        """
        sim.add_temporal(
            "visit_date", "2024-01-01", "2024-06-30", "daily",
            ["day_of_week", "month"],
        )
        grp = sim._groups["time"]
        assert grp.root == "visit_date"
        assert grp.hierarchy == ["visit_date"]
        assert set(grp.columns) == {"visit_date", "day_of_week", "month"}


# =====================================================================
# 2. INPUT VALIDATION TESTS — Exhaustive type/boundary/constraint checks
# =====================================================================


class TestAddCategoryTypeEnforcement:
    """Parametrized type enforcement for every add_category parameter.
    [Subtask 1.2.1]
    """

    @pytest.mark.parametrize("bad_name", [
        123, 45.6, None, True, [], {}, ("a",),
    ], ids=["int", "float", "None", "bool", "list", "dict", "tuple"])
    def test_name_rejects_non_str(
        self, sim: FactTableSimulator, bad_name: object
    ) -> None:
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_category(bad_name, ["A", "B"], [0.5, 0.5], "g")  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_values", [
        "AB", ("A", "B"), 42, None, {"A": 1}, frozenset(["A"]),
    ], ids=["str", "tuple", "int", "None", "dict", "frozenset"])
    def test_values_rejects_non_list(
        self, sim: FactTableSimulator, bad_values: object
    ) -> None:
        with pytest.raises(TypeError, match="values must be a list"):
            sim.add_category("x", bad_values, [0.5, 0.5], "g")  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_weights", [
        "bad", 42, None, True, (0.5, 0.5), frozenset([0.5]),
    ], ids=["str", "int", "None", "bool", "tuple", "frozenset"])
    def test_weights_rejects_non_list_non_dict(
        self, sim: FactTableSimulator, bad_weights: object
    ) -> None:
        with pytest.raises(TypeError, match="weights must be a list or dict"):
            sim.add_category("x", ["A", "B"], bad_weights, "g")  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_group", [
        42, None, True, [], {}, 3.14,
    ], ids=["int", "None", "bool", "list", "dict", "float"])
    def test_group_rejects_non_str(
        self, sim: FactTableSimulator, bad_group: object
    ) -> None:
        with pytest.raises(TypeError, match="group must be a str"):
            sim.add_category("x", ["A", "B"], [0.5, 0.5], bad_group)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_parent", [
        42, True, [], {}, 3.14,
    ], ids=["int", "bool", "list", "dict", "float"])
    def test_parent_rejects_non_str_non_none(
        self, sim: FactTableSimulator, bad_parent: object
    ) -> None:
        with pytest.raises(TypeError, match="parent must be a str or None"):
            sim.add_category("x", ["A", "B"], [0.5, 0.5], "g", parent=bad_parent)  # type: ignore[arg-type]


class TestAddCategoryBoundaryValues:
    """Boundary and constraint checks for add_category.
    [Subtask 1.2.1, 1.2.2]
    """

    def test_exactly_two_values_minimum_accepted(
        self, sim: FactTableSimulator
    ) -> None:
        """[A9] Exactly 2 values is the minimum accepted count."""
        sim.add_category("x", ["A", "B"], [0.5, 0.5], "g")
        assert len(sim._columns["x"]["values"]) == 2

    def test_large_value_set_accepted(self, sim: FactTableSimulator) -> None:
        """Boundary: 100 values are accepted without issue."""
        vals = [f"v{i}" for i in range(100)]
        wts = [1.0] * 100
        sim.add_category("big", vals, wts, "g")
        assert len(sim._columns["big"]["values"]) == 100

    @pytest.mark.parametrize("bad_weight_element", [
        "str_weight", None, [0.5],
    ], ids=["str_in_list", "None_in_list", "nested_list"])
    def test_non_numeric_weight_element_raises(
        self, sim: FactTableSimulator, bad_weight_element: object
    ) -> None:
        """Weight elements must be numeric (int or float). [Subtask 1.2.1]"""
        with pytest.raises(TypeError, match="must be numeric"):
            sim.add_category("x", ["A", "B"], [0.5, bad_weight_element], "g")  # type: ignore[arg-type]

    def test_nan_weight_treated_as_non_normalizable(
        self, sim: FactTableSimulator
    ) -> None:
        """NaN weights cause normalization to produce NaN, which we test
        propagates correctly. NaN < 0 is False so it passes the negative
        check but the sum is NaN — total == 0 is False, so normalization
        produces NaN weights. This is a boundary edge case.
        [Subtask 1.2.2]
        """
        # NaN passes the negative check (NaN < 0 → False) and passes the
        # total==0 check (NaN != 0). The result is NaN-contaminated weights.
        # This is a known edge case; documenting behavior rather than asserting
        # a specific error, since the spec does not address NaN inputs.
        # SPEC_AMBIGUOUS: NaN weight handling is unspecified. Current behavior
        # is to let NaN propagate through normalization without error.
        sim.add_category("x", ["A", "B"], [float("nan"), 1.0], "g")
        w = sim._columns["x"]["weights"]
        assert math.isnan(w[0])

    def test_inf_weight_normalizes_to_nan(
        self, sim: FactTableSimulator
    ) -> None:
        """inf + inf = inf; inf/inf = NaN. Edge case documentation.
        SPEC_AMBIGUOUS: inf weight handling is unspecified.
        [Subtask 1.2.2]
        """
        sim.add_category("x", ["A", "B"], [float("inf"), float("inf")], "g")
        w = sim._columns["x"]["weights"]
        # inf/inf = NaN
        assert math.isnan(w[0])

    def test_one_zero_one_positive_weight_normalizes(
        self, sim: FactTableSimulator
    ) -> None:
        """One zero weight is fine — only all-zero is rejected. [Subtask 1.2.2]"""
        sim.add_category("x", ["A", "B"], [0.0, 1.0], "g")
        assert sim._columns["x"]["weights"] == pytest.approx([0.0, 1.0])

    def test_very_small_weights_normalize_correctly(
        self, sim: FactTableSimulator
    ) -> None:
        """Very small positive weights should normalize without error. [Subtask 1.2.2]"""
        sim.add_category("x", ["A", "B"], [1e-300, 2e-300], "g")
        w = sim._columns["x"]["weights"]
        assert sum(w) == pytest.approx(1.0)

    def test_integer_weights_accepted_and_normalized(
        self, sim: FactTableSimulator
    ) -> None:
        """Integer weights (not floats) should work — int is numeric. [Subtask 1.2.2]"""
        sim.add_category("x", ["A", "B", "C"], [1, 2, 3], "g")
        assert sim._columns["x"]["weights"] == pytest.approx(
            [1 / 6, 2 / 6, 3 / 6]
        )


class TestAddTemporalTypeEnforcement:
    """Parametrized type enforcement for every add_temporal parameter.
    [Subtask 1.3.1]
    """

    @pytest.mark.parametrize("bad_name", [
        123, None, True, [], {},
    ], ids=["int", "None", "bool", "list", "dict"])
    def test_name_rejects_non_str(
        self, sim: FactTableSimulator, bad_name: object
    ) -> None:
        with pytest.raises(TypeError, match="name must be a str"):
            sim.add_temporal(bad_name, "2024-01-01", "2024-06-30", "daily")  # type: ignore[arg-type]

    @pytest.mark.parametrize("field_idx,field_name", [
        (0, "start"), (1, "end"),
    ])
    @pytest.mark.parametrize("bad_val", [
        123, None, True, [],
    ], ids=["int", "None", "bool", "list"])
    def test_start_end_reject_non_str(
        self, sim: FactTableSimulator, field_idx: int,
        field_name: str, bad_val: object,
    ) -> None:
        """start and end must both be str. [Subtask 1.3.1]"""
        args = ["2024-01-01", "2024-06-30"]
        args[field_idx] = bad_val  # type: ignore[assignment]
        with pytest.raises(TypeError, match=f"{field_name} must be a str"):
            sim.add_temporal("d", args[0], args[1], "daily")  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_freq", [
        123, None, True, [],
    ], ids=["int", "None", "bool", "list"])
    def test_freq_rejects_non_str(
        self, sim: FactTableSimulator, bad_freq: object
    ) -> None:
        with pytest.raises(TypeError, match="freq must be a str"):
            sim.add_temporal("d", "2024-01-01", "2024-06-30", bad_freq)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_derive", [
        "month", ("month",), 42, {"month": True},
    ], ids=["str", "tuple", "int", "dict"])
    def test_derive_rejects_non_list(
        self, sim: FactTableSimulator, bad_derive: object
    ) -> None:
        with pytest.raises(TypeError, match="derive must be a list"):
            sim.add_temporal(
                "d", "2024-01-01", "2024-06-30", "daily", bad_derive  # type: ignore[arg-type]
            )


class TestAddTemporalBoundaryValues:
    """Boundary and constraint checks for add_temporal.
    [Subtask 1.3.1, 1.3.2, 1.3.3]
    """

    def test_derive_none_defaults_to_empty(self, sim: FactTableSimulator) -> None:
        """None derive defaults to empty list (no derived columns). [Subtask 1.3.1]"""
        sim.add_temporal("d", "2024-01-01", "2024-12-31", "daily", None)
        assert sim._groups["time"].columns == ["d"]

    @pytest.mark.parametrize("freq", [
        "daily", "weekly", "monthly", "quarterly", "custom_freq",
    ])
    def test_any_non_empty_freq_accepted(
        self, sim: FactTableSimulator, freq: str
    ) -> None:
        """[B1] Any non-empty freq string accepted at declaration time. [Subtask 1.3.2]"""
        sim.add_temporal("d", "2024-01-01", "2024-06-30", freq)
        assert sim._columns["d"]["freq"] == freq

    @pytest.mark.parametrize("bad_date", [
        "2024-13-01", "2024-00-15", "2024-02-30", "not-a-date",
        "01-01-2024", "2024/01/01", "",
    ], ids=["month13", "month0", "feb30", "text", "us_format", "slashes", "empty"])
    def test_malformed_dates_raise_value_error(
        self, sim: FactTableSimulator, bad_date: str
    ) -> None:
        """Malformed date strings raise ValueError. [Subtask 1.3.1]"""
        with pytest.raises(ValueError):
            sim.add_temporal("d", bad_date, "2024-12-31", "daily")

    @pytest.mark.parametrize("token", [
        "fiscal_year", "year", "week_number", "hour",
        "DAY_OF_WEEK", "Month", "QUARTER",
    ])
    def test_non_whitelist_derive_tokens_rejected(
        self, sim: FactTableSimulator, token: str
    ) -> None:
        """Only exact whitelist tokens accepted; case-sensitive. [Subtask 1.3.3]"""
        with pytest.raises(ValueError, match="Unknown derive token"):
            sim.add_temporal(
                "d", "2024-01-01", "2024-06-30", "daily", [token]
            )

    def test_empty_derive_list_accepted(self, sim: FactTableSimulator) -> None:
        """Explicit empty list accepted. [Subtask 1.3.3]"""
        sim.add_temporal("d", "2024-01-01", "2024-06-30", "daily", [])
        assert sim._groups["time"].columns == ["d"]


class TestAddCategoryDictWeightsConstraints:
    """Per-parent dict constraint edge cases beyond contract rows.
    [Subtask 1.2.3]
    """

    def test_dict_weights_without_parent_raises(
        self, sim: FactTableSimulator
    ) -> None:
        """Dict weights with parent=None is nonsensical — no parent to condition on."""
        with pytest.raises(ValueError, match="parent to be set"):
            sim.add_category("x", ["A", "B"], {"k": [0.5, 0.5]}, "g")

    def test_per_parent_each_vector_normalized_independently(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Each parent's vector is independently normalized. [Subtask 1.2.3]"""
        weights = {
            "Xiehe": [1, 3],
            "Huashan": [2, 2],
            "Ruijin": [4, 1],
            "Tongren": [0, 5],
            "Zhongshan": [3, 3],
        }
        sim_with_root.add_category(
            "dept", ["X", "Y"], weights, "entity", parent="hospital"
        )
        stored = sim_with_root._columns["dept"]["weights"]
        assert stored["Xiehe"] == pytest.approx([0.25, 0.75])
        assert stored["Huashan"] == pytest.approx([0.5, 0.5])
        assert stored["Tongren"] == pytest.approx([0.0, 1.0])


# =====================================================================
# 3. OUTPUT CORRECTNESS TESTS — Return types, numerical accuracy,
#    immutability, idempotency
# =====================================================================


class TestAddCategoryOutputCorrectness:
    """Verify return value semantics and stored state correctness.
    [Subtask 1.2.1, 1.2.2, 1.2.5]
    """

    def test_returns_none(self, sim: FactTableSimulator) -> None:
        """add_category returns None (mutates self, no return value)."""
        result = sim.add_category("x", ["A", "B"], [0.5, 0.5], "g")
        assert result is None

    def test_column_metadata_has_expected_keys(
        self, sim: FactTableSimulator
    ) -> None:
        """Column metadata dict has all required keys with correct types. [Subtask 1.2.5]"""
        sim.add_category("x", ["A", "B", "C"], [1, 2, 3], "g")
        meta = sim._columns["x"]
        assert meta["type"] == "categorical"
        assert meta["group"] == "g"
        assert meta["parent"] is None
        assert isinstance(meta["values"], list)
        assert isinstance(meta["weights"], list)

    def test_normalization_hand_calculated(
        self, sim: FactTableSimulator
    ) -> None:
        """Verify normalization against hand calculation. [Subtask 1.2.2]

        Input: [3, 7, 10, 5]  sum=25
        Expected: [3/25, 7/25, 10/25, 5/25] = [0.12, 0.28, 0.40, 0.20]
        """
        sim.add_category("x", ["A", "B", "C", "D"], [3, 7, 10, 5], "g")
        w = sim._columns["x"]["weights"]
        assert w == pytest.approx([0.12, 0.28, 0.40, 0.20])
        assert sum(w) == pytest.approx(1.0)

    def test_already_normalized_weights_unchanged(
        self, sim: FactTableSimulator
    ) -> None:
        """Weights already summing to 1.0 are preserved exactly. [Subtask 1.2.2]"""
        sim.add_category("x", ["A", "B"], [0.3, 0.7], "g")
        assert sim._columns["x"]["weights"] == pytest.approx([0.3, 0.7])

    def test_values_list_is_defensive_copy(
        self, sim: FactTableSimulator
    ) -> None:
        """Stored values list is a copy — mutating input doesn't affect internal state.
        [Subtask 1.2.5]
        """
        original_values = ["A", "B", "C"]
        sim.add_category("x", original_values, [1, 1, 1], "g")
        # Mutate the original list after declaration
        original_values.append("D")
        # Internal state should be unaffected
        assert sim._columns["x"]["values"] == ["A", "B", "C"]

    def test_idempotency_duplicate_raises_not_overwrites(
        self, sim: FactTableSimulator
    ) -> None:
        """Calling add_category twice with same name raises DuplicateColumnError
        — declarations are append-only, not mutable. [Subtask 1.2.1]
        """
        sim.add_category("x", ["A", "B"], [0.5, 0.5], "g")
        with pytest.raises(DuplicateColumnError):
            sim.add_category("x", ["C", "D"], [0.3, 0.7], "other_g")

    def test_failed_validation_does_not_mutate_state(
        self, sim: FactTableSimulator
    ) -> None:
        """If validation fails, no partial state should be left behind.
        [Subtask 1.2.1]
        """
        initial_col_count = len(sim._columns)
        initial_group_count = len(sim._groups)
        with pytest.raises(EmptyValuesError):
            sim.add_category("phantom", [], [], "phantom_group")
        assert len(sim._columns) == initial_col_count
        assert len(sim._groups) == initial_group_count
        assert "phantom" not in sim._columns
        assert "phantom_group" not in sim._groups


class TestAddTemporalOutputCorrectness:
    """Verify return value semantics and stored state correctness.
    [Subtask 1.3.1, 1.3.4]
    """

    def test_returns_none(self, sim: FactTableSimulator) -> None:
        """add_temporal returns None (mutates self, no return value)."""
        result = sim.add_temporal("d", "2024-01-01", "2024-06-30", "daily")
        assert result is None

    def test_temporal_root_metadata_has_expected_keys(
        self, sim: FactTableSimulator
    ) -> None:
        """Temporal root metadata has all required keys. [Subtask 1.3.4]"""
        sim.add_temporal(
            "visit", "2024-01-01", "2024-06-30", "daily", ["month"]
        )
        meta = sim._columns["visit"]
        assert meta["type"] == "temporal"
        assert meta["group"] == "time"
        assert meta["parent"] is None
        assert isinstance(meta["start"], date)
        assert isinstance(meta["end"], date)
        assert meta["freq"] == "daily"
        assert meta["derive"] == ["month"]

    def test_derived_column_metadata_has_expected_keys(
        self, sim: FactTableSimulator
    ) -> None:
        """Derived column metadata has derivation token and parent ref. [Subtask 1.3.4]"""
        sim.add_temporal(
            "visit", "2024-01-01", "2024-06-30", "daily", ["day_of_week"]
        )
        meta = sim._columns["day_of_week"]
        assert meta["type"] == "temporal_derived"
        assert meta["group"] == "time"
        assert meta["parent"] == "visit"
        assert meta["derivation"] == "day_of_week"

    def test_date_parsing_produces_correct_date_objects(
        self, sim: FactTableSimulator
    ) -> None:
        """Parsed dates are correct datetime.date objects. [Subtask 1.3.1]"""
        sim.add_temporal("d", "2024-03-15", "2024-09-20", "daily")
        meta = sim._columns["d"]
        assert meta["start"] == date(2024, 3, 15)
        assert meta["end"] == date(2024, 9, 20)

    def test_derive_list_is_defensive_copy(
        self, sim: FactTableSimulator
    ) -> None:
        """Stored derive list is a copy — mutating input doesn't affect state.
        [Subtask 1.3.4]
        """
        original_derive = ["month", "quarter"]
        sim.add_temporal(
            "d", "2024-01-01", "2024-06-30", "daily", original_derive
        )
        original_derive.append("is_weekend")
        assert sim._columns["d"]["derive"] == ["month", "quarter"]

    def test_failed_temporal_does_not_mutate_state(
        self, sim: FactTableSimulator
    ) -> None:
        """Failed add_temporal leaves no partial state. [Subtask 1.3.1]"""
        initial_col_count = len(sim._columns)
        with pytest.raises(ValueError):
            sim.add_temporal("d", "2024-06-30", "2024-01-01", "daily")
        assert len(sim._columns) == initial_col_count
        assert "time" not in sim._groups


# =====================================================================
# 4. STATE TRANSITION TESTS — Registry state, ordering, isolation
# =====================================================================


class TestCategoryStateTransitions:
    """Verify internal registry state after sequential add_category calls.
    [Subtask 1.2.5, 1.2.6]
    """

    def test_columns_in_declaration_order(
        self, sim: FactTableSimulator
    ) -> None:
        """_columns OrderedDict preserves insertion order. [Subtask 1.2.5]"""
        sim.add_category("alpha", ["A", "B"], [0.5, 0.5], "g1")
        sim.add_category("beta", ["X", "Y"], [0.4, 0.6], "g2")
        sim.add_category("gamma", ["P", "Q"], [0.3, 0.7], "g3")
        assert list(sim._columns.keys()) == ["alpha", "beta", "gamma"]

    def test_group_hierarchy_root_first(
        self, sim: FactTableSimulator
    ) -> None:
        """Hierarchy is root-first even if child is declared after root.
        [Subtask 1.2.5]
        """
        sim.add_category("root_col", ["A", "B"], [0.5, 0.5], "g")
        sim.add_category(
            "child1", ["X", "Y"], [0.5, 0.5], "g", parent="root_col"
        )
        sim.add_category(
            "child2", ["M", "N"], [0.5, 0.5], "g", parent="root_col"
        )
        grp = sim._groups["g"]
        assert grp.hierarchy[0] == "root_col"
        assert grp.hierarchy == ["root_col", "child1", "child2"]

    def test_multiple_groups_independent(
        self, sim: FactTableSimulator
    ) -> None:
        """Groups are independent — adding to one doesn't affect another.
        [Subtask 1.2.5]
        """
        sim.add_category("h", ["A", "B"], [0.5, 0.5], "entity")
        sim.add_category("s", ["M", "S"], [0.6, 0.4], "patient")
        assert sim._groups["entity"].columns == ["h"]
        assert sim._groups["patient"].columns == ["s"]
        assert sim._groups["entity"].root == "h"
        assert sim._groups["patient"].root == "s"

    def test_child_without_root_still_creates_group(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Adding a child to an existing group doesn't change the root.
        [Subtask 1.2.5]
        """
        root_before = sim_with_root._groups["entity"].root
        sim_with_root.add_category(
            "dept", ["X", "Y"], [0.5, 0.5], "entity", parent="hospital"
        )
        assert sim_with_root._groups["entity"].root == root_before

    def test_instance_isolation_no_state_leakage(self) -> None:
        """Two simulator instances share no state. [Subtask 1.1.1]"""
        sim_a = FactTableSimulator(100, seed=1)
        sim_b = FactTableSimulator(200, seed=2)
        sim_a.add_category("x", ["A", "B"], [0.5, 0.5], "g")
        # sim_b should have no columns
        assert len(sim_b._columns) == 0
        assert len(sim_b._groups) == 0


class TestTemporalStateTransitions:
    """Verify internal registry state after add_temporal.
    [Subtask 1.3.4]
    """

    def test_temporal_columns_in_order_with_categories(
        self, sim: FactTableSimulator
    ) -> None:
        """Temporal columns appear in _columns in declaration order
        relative to categories. [Subtask 1.3.4]
        """
        sim.add_category("severity", ["A", "B"], [0.5, 0.5], "patient")
        sim.add_temporal(
            "visit_date", "2024-01-01", "2024-06-30", "daily", ["month"]
        )
        keys = list(sim._columns.keys())
        assert keys == ["severity", "visit_date", "month"]

    def test_temporal_group_coexists_with_categorical_groups(
        self, sim: FactTableSimulator
    ) -> None:
        """Temporal 'time' group coexists with categorical groups. [Subtask 1.3.4]"""
        sim.add_category("h", ["A", "B"], [0.5, 0.5], "entity")
        sim.add_temporal("d", "2024-01-01", "2024-06-30", "daily")
        assert "entity" in sim._groups
        assert "time" in sim._groups

    def test_temporal_group_is_dimension_group_instance(
        self, sim: FactTableSimulator
    ) -> None:
        """The 'time' group is a DimensionGroup dataclass instance. [Subtask 1.3.4]"""
        sim.add_temporal("d", "2024-01-01", "2024-06-30", "daily")
        assert isinstance(sim._groups["time"], DimensionGroup)

    def test_derived_columns_are_children_of_temporal_root(
        self, sim: FactTableSimulator
    ) -> None:
        """Each derived column's parent field points to temporal root. [Subtask 1.3.4]"""
        sim.add_temporal(
            "visit", "2024-01-01", "2024-06-30", "daily",
            ["day_of_week", "month", "quarter", "is_weekend"],
        )
        for token in ["day_of_week", "month", "quarter", "is_weekend"]:
            assert sim._columns[token]["parent"] == "visit"


# =====================================================================
# 5. INTEGRATION TESTS — Sprint 1 ↔ Sprint 2 boundary
# =====================================================================


class TestSprint1Sprint2Integration:
    """Test that Sprint 2 methods correctly integrate with Sprint 1 artifacts:
    constructor registries, exception hierarchy, DimensionGroup data class.
    """

    def test_add_category_uses_sprint1_exception_hierarchy(
        self, sim: FactTableSimulator
    ) -> None:
        """All Sprint 2 exceptions inherit from SimulatorError (Sprint 1).
        [Subtask 6.1.4 → 1.2.1]
        """
        # DuplicateColumnError → SimulatorError
        sim.add_category("x", ["A", "B"], [0.5, 0.5], "g")
        with pytest.raises(SimulatorError):
            sim.add_category("x", ["C", "D"], [0.5, 0.5], "g2")

    def test_empty_values_error_is_simulator_error(
        self, sim: FactTableSimulator
    ) -> None:
        """EmptyValuesError is catchable as SimulatorError.
        [Subtask 6.1.4 → 1.2.1]
        """
        with pytest.raises(SimulatorError):
            sim.add_category("x", [], [], "g")

    def test_weight_length_mismatch_error_has_fields(
        self, sim: FactTableSimulator
    ) -> None:
        """WeightLengthMismatchError exposes n_values and n_weights.
        [Subtask 6.1.4 → 1.2.1]
        """
        with pytest.raises(WeightLengthMismatchError) as exc_info:
            sim.add_category("x", ["A", "B", "C"], [0.5, 0.5], "g")
        assert exc_info.value.n_values == 3
        assert exc_info.value.n_weights == 2

    def test_parent_not_found_error_has_fields(
        self, sim: FactTableSimulator
    ) -> None:
        """ParentNotFoundError exposes child_name, parent_name, group.
        [Subtask 6.1.4 → 1.2.4]
        """
        with pytest.raises(ParentNotFoundError) as exc_info:
            sim.add_category(
                "dept", ["X", "Y"], [0.5, 0.5], "entity", parent="nonexistent"
            )
        assert exc_info.value.child_name == "dept"
        assert exc_info.value.parent_name == "nonexistent"
        assert exc_info.value.group == "entity"

    def test_duplicate_group_root_error_has_fields(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """DuplicateGroupRootError exposes group_name, existing_root, attempted_root.
        [Subtask 6.1.4 → 1.2.6]
        """
        with pytest.raises(DuplicateGroupRootError) as exc_info:
            sim_with_root.add_category(
                "region", ["R1", "R2"], [0.5, 0.5], "entity"
            )
        assert exc_info.value.group_name == "entity"
        assert exc_info.value.existing_root == "hospital"
        assert exc_info.value.attempted_root == "region"

    def test_duplicate_column_error_has_column_name(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """DuplicateColumnError exposes column_name field.
        [Subtask 6.1.4 → 1.2.1]
        """
        with pytest.raises(DuplicateColumnError) as exc_info:
            sim_with_root.add_category(
                "hospital", ["X", "Y"], [0.5, 0.5], "other"
            )
        assert exc_info.value.column_name == "hospital"

    def test_dimension_group_to_metadata_after_category(
        self, sim_with_hierarchy: FactTableSimulator
    ) -> None:
        """DimensionGroup.to_metadata() produces §2.6-compatible output
        after add_category populates it. [Subtask 2.1.1 → 1.2.5]
        """
        grp = sim_with_hierarchy._groups["entity"]
        meta = grp.to_metadata()
        assert meta["columns"] == ["hospital", "department"]
        assert meta["hierarchy"] == ["hospital", "department"]

    def test_dimension_group_to_metadata_returns_defensive_copy(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """Mutating to_metadata() output does not affect internal state.
        [Subtask 2.1.1]
        """
        grp = sim_with_root._groups["entity"]
        meta = grp.to_metadata()
        meta["columns"].append("INJECTED")
        assert "INJECTED" not in grp.columns

    def test_constructor_registries_are_correct_types(
        self, sim: FactTableSimulator
    ) -> None:
        """Sprint 1 registry types are maintained after Sprint 2 operations.
        [Subtask 1.1.2]
        """
        sim.add_category("x", ["A", "B"], [0.5, 0.5], "g")
        sim.add_temporal("d", "2024-01-01", "2024-06-30", "daily")
        assert isinstance(sim._columns, OrderedDict)
        assert isinstance(sim._groups, dict)
        assert isinstance(sim._orthogonal_pairs, list)
        assert isinstance(sim._group_dependencies, list)
        assert isinstance(sim._patterns, list)
        assert sim._realism_config is None
        assert isinstance(sim._measure_dag, dict)

    def test_full_one_shot_example_declarations(
        self, sim: FactTableSimulator
    ) -> None:
        """Replicate all column declarations from §2.5 one-shot example.
        Tests Sprint 1 constructor + Sprint 2 add_category + add_temporal
        working together end-to-end. [Subtask 1.2.1–1.2.5, 1.3.1–1.3.4]
        """
        # Entity group: hospital → department
        sim.add_category(
            "hospital",
            ["Xiehe", "Huashan", "Ruijin", "Tongren", "Zhongshan"],
            [0.25, 0.20, 0.20, 0.20, 0.15],
            "entity",
        )
        sim.add_category(
            "department",
            ["Internal", "Surgery", "Pediatrics", "Emergency"],
            [0.35, 0.25, 0.15, 0.25],
            "entity",
            parent="hospital",
        )

        # Patient group
        sim.add_category(
            "severity",
            ["Mild", "Moderate", "Severe"],
            [0.50, 0.35, 0.15],
            "patient",
        )

        # Payment group
        sim.add_category(
            "payment_method",
            ["Insurance", "Self-pay", "Government"],
            [0.60, 0.30, 0.10],
            "payment",
        )

        # Temporal
        sim.add_temporal(
            "visit_date", "2024-01-01", "2024-06-30", "daily",
            ["day_of_week", "month"],
        )

        # Verify the complete state
        assert len(sim._groups) == 4
        assert set(sim._groups.keys()) == {"entity", "patient", "payment", "time"}

        assert sim._groups["entity"].root == "hospital"
        assert sim._groups["entity"].hierarchy == ["hospital", "department"]

        assert sim._groups["time"].root == "visit_date"
        assert "day_of_week" in sim._groups["time"].columns

        # 4 categoricals + 1 temporal root + 2 derived = 7
        assert len(sim._columns) == 7

        # Declaration order preserved
        assert list(sim._columns.keys()) == [
            "hospital", "department", "severity", "payment_method",
            "visit_date", "day_of_week", "month",
        ]

        # All categorical weights normalized
        for col in ["hospital", "department", "severity", "payment_method"]:
            w = sim._columns[col]["weights"]
            assert sum(w) == pytest.approx(1.0)


# =====================================================================
# EXIT GATE TESTS — Spec-backed and assumption-backed assertions
# from the sprint plan exit gate section
# =====================================================================


class TestExitGateSpecBacked:
    """Assertions directly traceable to spec text."""

    def test_empty_values_raises_per_2_1_1(
        self, sim: FactTableSimulator
    ) -> None:
        """§2.1.1: 'rejects empty values'. [Subtask 1.2.1]"""
        with pytest.raises(EmptyValuesError):
            sim.add_category("x", [], [], "g")

    def test_auto_normalization_per_2_1_1(
        self, sim: FactTableSimulator
    ) -> None:
        """§2.1.1: 'Auto-normalized'. [Subtask 1.2.2]"""
        sim.add_category("c", ["a", "b", "c"], [1, 2, 3], "g")
        assert sum(sim._columns["c"]["weights"]) == pytest.approx(1.0)

    def test_parent_wrong_group_per_2_1_1(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """§2.1.1: 'validates parent exists in same group'. [Subtask 1.2.4]"""
        sim_with_root.add_category(
            "sev", ["Mild", "Severe"], [0.5, 0.5], "patient"
        )
        with pytest.raises(ParentNotFoundError):
            sim_with_root.add_category(
                "dept", ["X", "Y"], [0.5, 0.5], "entity", parent="sev"
            )

    def test_inverted_dates_per_2_1_1(self, sim: FactTableSimulator) -> None:
        """§2.1.1: inverted date range raises. [Subtask 1.3.1]"""
        with pytest.raises(ValueError):
            sim.add_temporal("d", "2024-06-30", "2024-01-01", "daily")

    def test_derive_whitelist_per_2_1_1(self, sim: FactTableSimulator) -> None:
        """§2.1.1: 'fiscal_year' rejected; 'quarter','is_weekend' accepted.
        [Subtask 1.3.3]
        """
        with pytest.raises(ValueError):
            sim.add_temporal(
                "d1", "2024-01-01", "2024-06-30", "daily", ["fiscal_year"]
            )
        sim.add_temporal(
            "d2", "2024-01-01", "2024-06-30", "daily", ["quarter", "is_weekend"]
        )

    def test_time_group_structure_per_2_2(
        self, sim: FactTableSimulator
    ) -> None:
        """§2.2: Group 'time' created with correct root and children.
        [Subtask 1.3.4]
        """
        sim.add_temporal(
            "visit_date", "2024-01-01", "2024-06-30", "daily",
            ["day_of_week", "month"],
        )
        grp = sim._groups["time"]
        assert grp.root == "visit_date"
        assert "day_of_week" in grp.columns
        assert "month" in grp.columns


class TestExitGateAssumptionBacked:
    """Assertions proceeding under documented assumptions, not explicit spec."""

    def test_single_value_rejected_assumption_a9(
        self, sim: FactTableSimulator
    ) -> None:
        """[A9] Single-value categorical rejected. [Subtask 1.2.1]"""
        with pytest.raises(InvalidParameterError):
            sim.add_category("x", ["A"], [1.0], "g")

    def test_per_parent_missing_key_assumption_a6(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """[A6] Per-parent dict missing a parent key raises. [Subtask 1.2.3]"""
        with pytest.raises(ValueError, match="missing keys"):
            sim_with_root.add_category(
                "dept", ["X", "Y"],
                {"Xiehe": [0.5, 0.5]},
                "entity", parent="hospital",
            )

    def test_duplicate_root_assumption_2_2(
        self, sim_with_root: FactTableSimulator
    ) -> None:
        """[§2.2] 'a root column' singular → duplicate raises. [Subtask 1.2.6]"""
        with pytest.raises(DuplicateGroupRootError):
            sim_with_root.add_category(
                "region", ["R1", "R2"], [0.5, 0.5], "entity"
            )

    def test_second_temporal_assumption_a10(
        self, sim: FactTableSimulator
    ) -> None:
        """[A10] Second add_temporal call raises. [Subtask 1.3.4]"""
        sim.add_temporal("d1", "2024-01-01", "2024-06-30", "daily")
        with pytest.raises(ValueError):
            sim.add_temporal("d2", "2024-07-01", "2024-12-31", "daily")
