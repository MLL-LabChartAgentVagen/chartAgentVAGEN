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
    validate_param_model,
    SUPPORTED_FAMILIES,
    VALIDATED_PARAM_KEYS,
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


class TestValidateParamModelKeySchema:
    """validate_param_model rejects unknown keys for every family with a
    declared schema in VALIDATED_PARAM_KEYS, and continues to accept the
    canonical mu/sigma form. This is the fail-loud guard that previously
    let Beta param_models with alpha/beta keys silently default mu→0.0
    and crash deep inside the sampler."""

    def test_beta_with_alpha_beta_keys_rejected(self):
        """LLMs frequently write Beta as {'alpha': ..., 'beta': ...} (canonical
        statistics convention). The SDK reads only mu/sigma, so unknown keys
        must fail at declaration time with a descriptive message."""
        with pytest.raises(InvalidParameterError) as exc:
            validate_param_model(
                name="acceptance_rate", family="beta",
                param_model={"alpha": 1.0, "beta": 1.0}, columns={},
            )
        msg = str(exc.value)
        assert "alpha" in msg
        assert "beta" in msg  # the family name 'beta' should be in the message
        assert "mu" in msg and "sigma" in msg

    def test_beta_with_mu_sigma_scalars_accepted(self):
        """Canonical Beta param_model with mu/sigma scalars passes."""
        validate_param_model(
            name="rate", family="beta",
            param_model={"mu": 5.0, "sigma": 5.0}, columns={},
        )

    def test_beta_with_mu_sigma_intercept_effects_accepted(self):
        """Canonical Beta param_model with intercept+effects dicts passes."""
        validate_param_model(
            name="rate", family="beta",
            param_model={
                "mu": {"intercept": 2.0, "effects": {}},
                "sigma": {"intercept": 5.0, "effects": {}},
            },
            columns={},
        )

    def test_poisson_rejects_sigma(self):
        """Poisson takes only mu; passing sigma is a key-schema error."""
        with pytest.raises(InvalidParameterError) as exc:
            validate_param_model(
                name="count", family="poisson",
                param_model={"mu": 3.0, "sigma": 1.0}, columns={},
            )
        assert "sigma" in str(exc.value)

    def test_exponential_rejects_sigma(self):
        """Exponential takes only mu; passing sigma is a key-schema error."""
        with pytest.raises(InvalidParameterError) as exc:
            validate_param_model(
                name="lifetime", family="exponential",
                param_model={"mu": 0.5, "sigma": 1.0}, columns={},
            )
        assert "sigma" in str(exc.value)

    def test_gaussian_unknown_key_rejected(self):
        """Pre-existing gaussian schema also gains unknown-key rejection."""
        with pytest.raises(InvalidParameterError) as exc:
            validate_param_model(
                name="age", family="gaussian",
                param_model={"mu": 35, "sigma": 10, "rate": 0.1}, columns={},
            )
        assert "rate" in str(exc.value)

    def test_mixture_not_validated(self):
        """Mixture (IS-1) is intentionally absent from VALIDATED_PARAM_KEYS;
        unknown-key validation does not apply until its schema is defined."""
        assert "mixture" not in VALIDATED_PARAM_KEYS
        # Should not raise on schema check (sampling is stubbed elsewhere)
        validate_param_model(
            name="m", family="mixture",
            param_model={"components": [{"family": "gaussian", "weight": 1.0}]},
            columns={},
        )
