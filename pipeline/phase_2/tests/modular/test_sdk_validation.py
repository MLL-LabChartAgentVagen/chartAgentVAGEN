"""
Tests for SDK Validation operations.

Tested functions:
- validate_column_name
- validate_family
"""
from __future__ import annotations

import pytest

from pipeline.phase_2.exceptions import DuplicateColumnError, InvalidParameterError
from pipeline.phase_2.sdk.validation import validate_column_name, validate_family, SUPPORTED_FAMILIES


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
