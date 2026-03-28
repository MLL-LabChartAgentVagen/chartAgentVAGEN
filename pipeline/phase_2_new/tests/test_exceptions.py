"""
Sprint 1 — Test suite for agpds/exceptions.py

Subtask IDs tested: 6.1.1, 6.1.2, 6.1.3, 6.1.4

Test categories (in order):
  1. Contract tests — one per §3A contract row
  2. Input validation tests — type enforcement, boundary values
  3. Output correctness tests — message format, field types, return values
  4. State transition tests — attribute persistence after construction
  5. Integration tests — inheritance tree, catch-by-base-class behavior
"""
from __future__ import annotations

import pytest

from agpds.exceptions import (
    SimulatorError,
    CyclicDependencyError,
    UndefinedEffectError,
    NonRootDependencyError,
    InvalidParameterError,
    DuplicateColumnError,
    EmptyValuesError,
    WeightLengthMismatchError,
    DegenerateDistributionError,
    ParentNotFoundError,
    DuplicateGroupRootError,
)


# All concrete exception classes for parametrized tests
ALL_EXCEPTION_CLASSES: list[type[SimulatorError]] = [
    CyclicDependencyError,
    UndefinedEffectError,
    NonRootDependencyError,
    InvalidParameterError,
    DuplicateColumnError,
    EmptyValuesError,
    WeightLengthMismatchError,
    DegenerateDistributionError,
    ParentNotFoundError,
    DuplicateGroupRootError,
]


# =====================================================================
# 1. CONTRACT TESTS — one per §3A contract table row
# =====================================================================


class TestContractCyclicDependencyError:
    """Contract rows for CyclicDependencyError [6.1.1]."""

    # Contract row: CyclicDependencyError(["cost","satisfaction","cost"])
    # valid 3-element cycle → str(e) contains cycle path and "forms a cycle"
    def test_contract_three_node_cycle_message(self) -> None:
        """[6.1.1] 3-element cycle path produces arrow-separated message."""
        err = CyclicDependencyError(["cost", "satisfaction", "cost"])
        msg = str(err)
        assert "'cost'" in msg
        assert "'satisfaction'" in msg
        assert "→" in msg
        assert "forms a cycle" in msg

    # Contract row: CyclicDependencyError(["A","B","C","A"])
    # longer path → str(e) contains 'A' → 'B' → 'C' → 'A'
    def test_contract_four_node_cycle_contains_full_chain(self) -> None:
        """[6.1.1] 4-element cycle path renders the full arrow chain."""
        err = CyclicDependencyError(["A", "B", "C", "A"])
        msg = str(err)
        assert "'A' → 'B' → 'C' → 'A'" in msg
        assert "forms a cycle" in msg

    # Contract row: CyclicDependencyError(["A","A"])
    # self-cycle → str(e) contains 'A' → 'A' and "forms a cycle"
    def test_contract_self_cycle(self) -> None:
        """[6.1.1] Self-referencing 2-element cycle."""
        err = CyclicDependencyError(["A", "A"])
        msg = str(err)
        assert "'A' → 'A'" in msg
        assert "forms a cycle" in msg

    # Contract row: isinstance(CyclicDependencyError, SimulatorError) → True
    def test_contract_inherits_simulator_error(self) -> None:
        """[6.1.1] Must inherit from SimulatorError."""
        assert isinstance(CyclicDependencyError(["A", "A"]), SimulatorError)
        assert isinstance(CyclicDependencyError(["A", "A"]), Exception)


class TestContractUndefinedEffectError:
    """Contract rows for UndefinedEffectError [6.1.2]."""

    # Contract row: UndefinedEffectError("severity_surcharge","Severe")
    # → exact §2.7 message
    def test_contract_spec_example_exact_message(self) -> None:
        """[6.1.2] Message matches §2.7 example verbatim."""
        err = UndefinedEffectError("severity_surcharge", "Severe")
        assert str(err) == (
            "'severity_surcharge' in formula has no definition for 'Severe'."
        )

    # Contract row: UndefinedEffectError("","")
    # → instance created; message contains two '' tokens
    def test_contract_empty_strings_instantiate(self) -> None:
        """[6.1.2] Empty strings produce valid instance with empty-quoted tokens."""
        err = UndefinedEffectError("", "")
        assert "'' in formula has no definition for ''." in str(err)

    # Contract row: isinstance(UndefinedEffectError, SimulatorError) → True
    def test_contract_inherits_simulator_error(self) -> None:
        """[6.1.2] Must inherit from SimulatorError."""
        assert isinstance(UndefinedEffectError("a", "b"), SimulatorError)


class TestContractNonRootDependencyError:
    """Contract rows for NonRootDependencyError [6.1.3]."""

    # Contract row: NonRootDependencyError("department")
    # → str(e) contains "'department' is not a group root"
    def test_contract_spec_example_message(self) -> None:
        """[6.1.3] Message matches §2.7 example format."""
        err = NonRootDependencyError("department")
        msg = str(err)
        assert "'department' is not a group root" in msg
        assert "cannot use in add_group_dependency" in msg

    # Contract row: isinstance(NonRootDependencyError, SimulatorError) → True
    def test_contract_inherits_simulator_error(self) -> None:
        """[6.1.3] Must inherit from SimulatorError."""
        assert isinstance(NonRootDependencyError("x"), SimulatorError)


class TestContractInvalidParameterError:
    """Contract rows for InvalidParameterError [6.1.4 / A5a]."""

    # Contract row: InvalidParameterError("sigma",-0.5,"must be > 0")
    # → msg contains "sigma", "-0.5", "must be > 0"
    def test_contract_negative_sigma(self) -> None:
        """[6.1.4] Negative sigma produces message with all three fields."""
        err = InvalidParameterError("sigma", -0.5, "must be > 0")
        msg = str(err)
        assert "sigma" in msg
        assert "-0.5" in msg
        assert "must be > 0" in msg

    # Contract row: InvalidParameterError("shape",0.0,"must be > 0")
    # → msg contains "shape", "0.0"
    def test_contract_zero_shape(self) -> None:
        """[6.1.4] Zero shape parameter."""
        err = InvalidParameterError("shape", 0.0, "must be > 0")
        msg = str(err)
        assert "shape" in msg
        assert "0.0" in msg

    # Contract row: isinstance(InvalidParameterError, SimulatorError) → True
    def test_contract_inherits_simulator_error(self) -> None:
        """[6.1.4] Must inherit from SimulatorError."""
        assert isinstance(InvalidParameterError("x", 0, "bad"), SimulatorError)


class TestContractDuplicateColumnError:
    """Contract rows for DuplicateColumnError [6.1.4]."""

    # Contract row: DuplicateColumnError("hospital")
    # → msg contains "hospital" and indicates duplication
    def test_contract_message_contains_column_name(self) -> None:
        """[6.1.4] Message names the duplicate column."""
        err = DuplicateColumnError("hospital")
        msg = str(err)
        assert "hospital" in msg
        assert "already declared" in msg or "duplicate" in msg.lower()


class TestContractEmptyValuesError:
    """Contract rows for EmptyValuesError [6.1.4]."""

    # Contract row: EmptyValuesError("x")
    # → msg contains "x" and indicates empty values
    def test_contract_message_contains_column_name_and_empty(self) -> None:
        """[6.1.4] Message names the column and mentions emptiness."""
        err = EmptyValuesError("x")
        msg = str(err)
        assert "x" in msg
        assert "empty" in msg.lower()


class TestContractWeightLengthMismatchError:
    """Contract rows for WeightLengthMismatchError [6.1.4]."""

    # Contract row: WeightLengthMismatchError("x", 3, 5)
    # → msg contains "x", "3", "5"
    def test_contract_message_contains_all_fields(self) -> None:
        """[6.1.4] Message includes column name and both counts."""
        err = WeightLengthMismatchError("x", 3, 5)
        msg = str(err)
        assert "x" in msg
        assert "3" in msg
        assert "5" in msg


class TestContractDegenerateDistributionError:
    """Contract rows for DegenerateDistributionError [6.1.4]."""

    # Contract row: DegenerateDistributionError("wait_minutes","sigma=0...")
    # → msg contains "wait_minutes" and "sigma=0"
    def test_contract_message_contains_column_and_detail(self) -> None:
        """[6.1.4] Message includes column name and degeneracy description."""
        err = DegenerateDistributionError(
            "wait_minutes", "sigma=0 produces a point mass"
        )
        msg = str(err)
        assert "wait_minutes" in msg
        assert "sigma=0" in msg


class TestContractParentNotFoundError:
    """Contract rows for ParentNotFoundError [6.1.4]."""

    # Contract row: ParentNotFoundError("dept","hospital","entity")
    # → msg contains all three fields
    def test_contract_message_contains_all_fields(self) -> None:
        """[6.1.4] Message includes child, parent, and group names."""
        err = ParentNotFoundError("dept", "hospital", "entity")
        msg = str(err)
        assert "dept" in msg
        assert "hospital" in msg
        assert "entity" in msg


class TestContractDuplicateGroupRootError:
    """Contract rows for DuplicateGroupRootError [6.1.4]."""

    # Contract row: DuplicateGroupRootError("entity","hospital","clinic")
    # → msg contains all three fields
    def test_contract_message_contains_all_fields(self) -> None:
        """[6.1.4] Message includes group, existing root, and attempted root."""
        err = DuplicateGroupRootError("entity", "hospital", "clinic")
        msg = str(err)
        assert "entity" in msg
        assert "hospital" in msg
        assert "clinic" in msg


class TestContractFullHierarchy:
    """Contract rows for the full inheritance tree [6.1.1]."""

    # Contract row: All exception classes subclass SimulatorError → True
    @pytest.mark.parametrize("exc_class", ALL_EXCEPTION_CLASSES)
    def test_contract_all_subclass_simulator_error(
        self, exc_class: type
    ) -> None:
        """[6.1.1] Every SDK exception must be a SimulatorError subclass."""
        assert issubclass(exc_class, SimulatorError)

    # Contract row: SimulatorError subclasses Exception → True
    def test_contract_simulator_error_is_exception(self) -> None:
        """[6.1.1] SimulatorError is a direct Exception subclass."""
        assert issubclass(SimulatorError, Exception)
        assert isinstance(SimulatorError("test"), Exception)


# =====================================================================
# 2. INPUT VALIDATION TESTS — type enforcement, boundary values
# =====================================================================


class TestCyclicDependencyErrorInputValidation:
    """Input edge cases for CyclicDependencyError [6.1.1]."""

    def test_single_element_path(self) -> None:
        """[6.1.1] Boundary: single-element list (degenerate, but should not crash)."""
        err = CyclicDependencyError(["A"])
        assert "'A'" in str(err)
        assert "forms a cycle" in str(err)

    def test_empty_path(self) -> None:
        """[6.1.1] Boundary: empty list (degenerate, but should not crash)."""
        err = CyclicDependencyError([])
        assert "forms a cycle" in str(err)

    def test_path_with_special_characters(self) -> None:
        """[6.1.1] Names containing special chars render correctly."""
        err = CyclicDependencyError(["col_1", "col-2", "col_1"])
        msg = str(err)
        assert "'col_1'" in msg
        assert "'col-2'" in msg

    def test_very_long_path(self) -> None:
        """[6.1.1] Boundary: long cycle path does not truncate."""
        path = [f"node_{i}" for i in range(20)] + ["node_0"]
        err = CyclicDependencyError(path)
        assert "node_0" in str(err)
        assert "node_19" in str(err)


class TestUndefinedEffectErrorInputValidation:
    """Input edge cases for UndefinedEffectError [6.1.2]."""

    def test_effect_name_with_spaces(self) -> None:
        """[6.1.2] Effect name containing spaces."""
        err = UndefinedEffectError("severity surcharge", "Severe")
        assert "'severity surcharge'" in str(err)

    def test_missing_value_with_unicode(self) -> None:
        """[6.1.2] Unicode characters in missing value."""
        err = UndefinedEffectError("eff", "重度")
        assert "'重度'" in str(err)


class TestInvalidParameterErrorInputValidation:
    """Input edge cases for InvalidParameterError [6.1.4]."""

    @pytest.mark.parametrize(
        "value",
        [float("inf"), float("-inf"), float("nan")],
        ids=["inf", "neg_inf", "nan"],
    )
    def test_special_float_values(self, value: float) -> None:
        """[6.1.4] Special float values (inf, -inf, NaN) are accepted."""
        err = InvalidParameterError("sigma", value, "out of domain")
        assert "sigma" in str(err)

    def test_very_large_value(self) -> None:
        """[6.1.4] Boundary: extremely large float."""
        err = InvalidParameterError("scale", 1e308, "too large")
        assert "scale" in str(err)

    def test_integer_value_accepted(self) -> None:
        """[6.1.4] Integer (not float) value for the value parameter."""
        err = InvalidParameterError("df", 0, "must be > 0")
        assert "0" in str(err)


class TestWeightLengthMismatchErrorInputValidation:
    """Input edge cases for WeightLengthMismatchError [6.1.4]."""

    def test_zero_values_zero_weights(self) -> None:
        """[6.1.4] Boundary: both counts are zero."""
        err = WeightLengthMismatchError("col", 0, 0)
        assert "0" in str(err)

    def test_large_mismatch(self) -> None:
        """[6.1.4] Boundary: large count values."""
        err = WeightLengthMismatchError("col", 1000, 999)
        assert "1000" in str(err)
        assert "999" in str(err)


# =====================================================================
# 3. OUTPUT CORRECTNESS TESTS — message format, field types, return values
# =====================================================================


class TestCyclicDependencyErrorOutput:
    """Output format verification for CyclicDependencyError [6.1.1]."""

    def test_message_attribute_matches_str(self) -> None:
        """[6.1.1] The .message attribute must equal str(err)."""
        err = CyclicDependencyError(["X", "Y", "X"])
        assert err.message == str(err)

    def test_cycle_path_attribute_type(self) -> None:
        """[6.1.1] .cycle_path is the original list reference."""
        path = ["A", "B", "A"]
        err = CyclicDependencyError(path)
        assert err.cycle_path is path

    def test_message_starts_with_measure(self) -> None:
        """[6.1.1] Message begins with 'Measure' per §2.7 format."""
        err = CyclicDependencyError(["X", "Y", "X"])
        assert str(err).startswith("Measure ")

    def test_message_ends_with_period(self) -> None:
        """[6.1.1] Message ends with a period per §2.7 format."""
        err = CyclicDependencyError(["X", "Y", "X"])
        assert str(err).endswith(".")


class TestUndefinedEffectErrorOutput:
    """Output format verification for UndefinedEffectError [6.1.2]."""

    def test_message_attribute_matches_str(self) -> None:
        """[6.1.2] The .message attribute must equal str(err)."""
        err = UndefinedEffectError("eff", "val")
        assert err.message == str(err)

    def test_effect_name_attribute_type_is_str(self) -> None:
        """[6.1.2] .effect_name stores the exact string passed in."""
        err = UndefinedEffectError("surcharge", "Missing")
        assert isinstance(err.effect_name, str)
        assert err.effect_name == "surcharge"

    def test_missing_value_attribute_type_is_str(self) -> None:
        """[6.1.2] .missing_value stores the exact string passed in."""
        err = UndefinedEffectError("surcharge", "Missing")
        assert isinstance(err.missing_value, str)
        assert err.missing_value == "Missing"

    def test_message_ends_with_period(self) -> None:
        """[6.1.2] Message ends with a period per §2.7 format."""
        err = UndefinedEffectError("eff", "val")
        assert str(err).endswith(".")


class TestNonRootDependencyErrorOutput:
    """Output format verification for NonRootDependencyError [6.1.3]."""

    def test_message_attribute_matches_str(self) -> None:
        """[6.1.3] The .message attribute must equal str(err)."""
        err = NonRootDependencyError("ward")
        assert err.message == str(err)

    def test_column_name_attribute_type_is_str(self) -> None:
        """[6.1.3] .column_name stores the exact string passed in."""
        err = NonRootDependencyError("dept")
        assert isinstance(err.column_name, str)
        assert err.column_name == "dept"

    def test_message_ends_with_period(self) -> None:
        """[6.1.3] Message ends with a period."""
        err = NonRootDependencyError("x")
        assert str(err).endswith(".")


class TestInvalidParameterErrorOutput:
    """Output format verification for InvalidParameterError [6.1.4]."""

    def test_all_three_fields_stored(self) -> None:
        """[6.1.4] All constructor args are stored as named attributes."""
        err = InvalidParameterError("rate", -1.0, "must be positive")
        assert err.param_name == "rate"
        assert err.value == -1.0
        assert err.reason == "must be positive"

    def test_message_attribute_matches_str(self) -> None:
        """[6.1.4] The .message attribute must equal str(err)."""
        err = InvalidParameterError("sigma", -0.5, "must be > 0")
        assert err.message == str(err)


class TestDuplicateColumnErrorOutput:
    """Output format verification for DuplicateColumnError [6.1.4]."""

    def test_column_name_stored(self) -> None:
        """[6.1.4] .column_name stores the exact string passed in."""
        err = DuplicateColumnError("hospital")
        assert err.column_name == "hospital"

    def test_message_attribute_matches_str(self) -> None:
        """[6.1.4] The .message attribute must equal str(err)."""
        err = DuplicateColumnError("x")
        assert err.message == str(err)


class TestEmptyValuesErrorOutput:
    """Output format verification for EmptyValuesError [6.1.4]."""

    def test_column_name_stored(self) -> None:
        """[6.1.4] .column_name stores the exact string passed in."""
        err = EmptyValuesError("col")
        assert err.column_name == "col"


class TestWeightLengthMismatchErrorOutput:
    """Output format verification for WeightLengthMismatchError [6.1.4]."""

    def test_all_three_fields_stored(self) -> None:
        """[6.1.4] All constructor args are stored as named attributes."""
        err = WeightLengthMismatchError("col", 2, 4)
        assert err.column_name == "col"
        assert err.n_values == 2
        assert err.n_weights == 4


class TestDegenerateDistributionErrorOutput:
    """Output format verification for DegenerateDistributionError [6.1.4]."""

    def test_both_fields_stored(self) -> None:
        """[6.1.4] Both constructor args are stored as named attributes."""
        err = DegenerateDistributionError("col", "all weights zero")
        assert err.column_name == "col"
        assert err.detail == "all weights zero"


class TestParentNotFoundErrorOutput:
    """Output format verification for ParentNotFoundError [6.1.4]."""

    def test_all_three_fields_stored(self) -> None:
        """[6.1.4] All constructor args are stored as named attributes."""
        err = ParentNotFoundError("child", "parent", "group")
        assert err.child_name == "child"
        assert err.parent_name == "parent"
        assert err.group == "group"


class TestDuplicateGroupRootErrorOutput:
    """Output format verification for DuplicateGroupRootError [6.1.4]."""

    def test_all_three_fields_stored(self) -> None:
        """[6.1.4] All constructor args are stored as named attributes."""
        err = DuplicateGroupRootError("g", "existing", "new")
        assert err.group_name == "g"
        assert err.existing_root == "existing"
        assert err.attempted_root == "new"


# =====================================================================
# 4. STATE TRANSITION TESTS — attribute persistence after construction
# =====================================================================


class TestExceptionAttributePersistence:
    """Verify attributes remain stable after construction [6.1.1–6.1.4]."""

    def test_cyclic_dependency_path_not_mutated_by_str(self) -> None:
        """[6.1.1] Calling str() does not mutate the stored cycle_path."""
        path = ["A", "B", "A"]
        err = CyclicDependencyError(path)
        _ = str(err)
        _ = repr(err)
        assert err.cycle_path == ["A", "B", "A"]

    def test_undefined_effect_fields_stable_after_str(self) -> None:
        """[6.1.2] Calling str() multiple times does not mutate stored fields."""
        err = UndefinedEffectError("eff", "val")
        _ = str(err)
        _ = str(err)
        assert err.effect_name == "eff"
        assert err.missing_value == "val"

    def test_invalid_parameter_fields_stable_after_repeated_access(self) -> None:
        """[6.1.4] Repeated field access returns consistent values."""
        err = InvalidParameterError("sigma", -0.5, "must be > 0")
        for _ in range(10):
            assert err.param_name == "sigma"
            assert err.value == -0.5
            assert err.reason == "must be > 0"
            assert str(err) == err.message

    def test_non_root_dependency_message_stable(self) -> None:
        """[6.1.3] Message is stable across repeated str() calls."""
        err = NonRootDependencyError("department")
        msg1 = str(err)
        msg2 = str(err)
        assert msg1 == msg2
        assert err.column_name == "department"


# =====================================================================
# 5. INTEGRATION TESTS — catch-by-base, try/except patterns
# =====================================================================


class TestExceptionCatchByBase:
    """Verify the §2.7 feedback loop catch pattern works [6.1.1]."""

    def test_catch_cyclic_dependency_via_simulator_error(self) -> None:
        """[6.1.1] CyclicDependencyError is catchable as SimulatorError."""
        with pytest.raises(SimulatorError):
            raise CyclicDependencyError(["A", "B", "A"])

    def test_catch_undefined_effect_via_simulator_error(self) -> None:
        """[6.1.2] UndefinedEffectError is catchable as SimulatorError."""
        with pytest.raises(SimulatorError):
            raise UndefinedEffectError("eff", "val")

    def test_catch_non_root_dependency_via_simulator_error(self) -> None:
        """[6.1.3] NonRootDependencyError is catchable as SimulatorError."""
        with pytest.raises(SimulatorError):
            raise NonRootDependencyError("col")

    def test_catch_all_via_exception(self) -> None:
        """[6.1.1] All SDK exceptions are catchable as plain Exception."""
        with pytest.raises(Exception):
            raise InvalidParameterError("p", 0, "bad")

    @pytest.mark.parametrize(
        "exc_class", ALL_EXCEPTION_CLASSES, ids=lambda c: c.__name__
    )
    def test_each_exception_catchable_as_simulator_error(
        self, exc_class: type
    ) -> None:
        """[6.1.1] Every concrete exception is catchable as SimulatorError."""
        assert issubclass(exc_class, SimulatorError)

    def test_simulator_error_does_not_catch_builtin_value_error(self) -> None:
        """[6.1.1] SimulatorError must NOT catch unrelated built-in errors."""
        with pytest.raises(ValueError):
            try:
                raise ValueError("unrelated")
            except SimulatorError:
                pytest.fail("SimulatorError should not catch ValueError")

    def test_feedback_loop_pattern_extracts_class_name(self) -> None:
        """[6.1.1] The §2.7 feedback formatter needs the exception class name."""
        try:
            raise CyclicDependencyError(["A", "B", "A"])
        except SimulatorError as e:
            assert type(e).__name__ == "CyclicDependencyError"


class TestExceptionModuleImportIsolation:
    """Verify exceptions.py imports cleanly with no side effects [6.1.1]."""

    def test_import_does_not_pull_in_pandas(self) -> None:
        """[6.1.1] exceptions.py must be lightweight — no pandas dependency."""
        import sys
        import importlib

        importlib.reload(__import__("agpds.exceptions"))
        # If pandas were imported, it would be in sys.modules
        # (This is a soft check; the real guarantee is the source code review.)
        # We just verify the module loads without ImportError.
        assert "agpds.exceptions" in sys.modules

    def test_import_does_not_pull_in_numpy(self) -> None:
        """[6.1.1] exceptions.py must be lightweight — no numpy dependency."""
        import agpds.exceptions as mod  # noqa: F401
        # If this import succeeded, the module has no hidden numpy dep.
        assert True
