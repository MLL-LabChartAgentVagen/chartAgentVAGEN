"""
Tests for SDK Validation operations.

Tested functions:
- validate_column_name
- validate_family
"""
from __future__ import annotations

import pytest

from pipeline.phase_2.exceptions import (
    DuplicateColumnError,
    InvalidParameterError,
    UndefinedEffectError,
)
from pipeline.phase_2.sdk.validation import (
    validate_column_name,
    validate_family,
    validate_effects_in_param,
    SUPPORTED_FAMILIES,
)


class TestValidateColumnName:
    
    def test_valid_unique_names(self):
        """Well-formed and unique column names pass without error."""
        existing = {"age": {}, "gender": {}}
        # Should not raise
        validate_column_name("income", existing)
        validate_column_name("A_valid_name_123", existing)

    def test_duplicate_name_rejected(self):
        """Columns must be unique within a simulator instance."""
        existing = {"age": {}}
        with pytest.raises(DuplicateColumnError, match="is already declared"):
            validate_column_name("age", existing)


class TestValidateFamily:
    
    def test_supported_families_accepted(self):
        """All families in SUPPORTED_FAMILIES are accepted."""
        for family in SUPPORTED_FAMILIES:
            # Should not raise
            validate_family(family)

    @pytest.mark.parametrize("bad_family", [
        "unknown_dist",
        "normal",  # It should be 'gaussian' based on Phase 2 spec
        "weibull",
        "",
        " "
    ])
    def test_unsupported_families_rejected(self, bad_family):
        """Unknown statistical families are rejected."""
        with pytest.raises(ValueError, match="Unsupported distribution family"):
            validate_family(bad_family)

    def test_type_error_for_non_string(self):
        """Numeric inputs not in string format raise ValueError out of the support check."""
        with pytest.raises(ValueError):
            validate_family(123)  # type: ignore


class TestUndefinedEffectHints:
    """When a formula references a symbol that isn't a declared column,
    `validate_effects_in_param` raises `UndefinedEffectError`. For the
    common case where the symbol matches a temporal-derive feature name
    (`month`, `quarter`, `day_of_week`, `is_weekend`), the error message
    includes a concrete fix hint pointing at `add_temporal(derive=[...])`."""

    @pytest.mark.parametrize("name", ["month", "quarter", "day_of_week", "is_weekend"])
    def test_undefined_effect_hint_for_temporal_derive(self, name):
        effects = {name: {"__all__": 0.1}}
        with pytest.raises(UndefinedEffectError) as exc:
            validate_effects_in_param(
                measure_name="m", param_key="mu",
                effects=effects, columns={},
            )
        msg = str(exc.value)
        assert name in msg
        assert "derive" in msg
        assert "add_temporal" in msg

    def test_undefined_effect_no_hint_for_unknown_symbol(self):
        """Symbols that aren't temporal-derive names still raise, but without the hint."""
        with pytest.raises(UndefinedEffectError) as exc:
            validate_effects_in_param(
                measure_name="m", param_key="mu",
                effects={"foobar": {"__all__": 0.1}},
                columns={},
            )
        msg = str(exc.value)
        assert "foobar" in msg
        assert "derive" not in msg
        assert "add_temporal" not in msg
