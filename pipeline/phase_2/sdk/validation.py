"""
SDK declaration-time validation rules — dispatcher.

Implementation lives in _validate_*.py topic modules; this file re-exports
the public surface so callers (`from . import validation as _val`) and
tests (`from pipeline.phase_2.sdk.validation import ...`) keep working
without changes.

Implements: §2.1.1, §2.1.2 validation rules
"""
from __future__ import annotations

from ._validate_basic import (
    IDENTIFIER_RE,
    SUPPORTED_FAMILIES,
    TEMPORAL_DERIVE_NAMES,
    extract_formula_symbols,
    validate_column_name,
    validate_family,
    validate_parent,
)
from ._validate_groups import (
    TEMPORAL_GROUP_NAME,
    normalize_weight_dict_values,
)
from ._validate_param_model import (
    TEMPORAL_DERIVE_WHITELIST,
    VALIDATED_PARAM_KEYS,
    validate_effects_in_param,
    validate_param_model,
    validate_param_value,
)
from ._validate_relationships import validate_root_only
from ._validate_structural import validate_structural_effects
from ._validate_weights import (
    validate_and_normalize_dict_weights,
    validate_and_normalize_flat_weights,
)

__all__ = [
    # Constants
    "IDENTIFIER_RE",
    "SUPPORTED_FAMILIES",
    "TEMPORAL_DERIVE_NAMES",
    "TEMPORAL_DERIVE_WHITELIST",
    "TEMPORAL_GROUP_NAME",
    "VALIDATED_PARAM_KEYS",
    # Validators
    "extract_formula_symbols",
    "normalize_weight_dict_values",
    "validate_and_normalize_dict_weights",
    "validate_and_normalize_flat_weights",
    "validate_column_name",
    "validate_effects_in_param",
    "validate_family",
    "validate_param_model",
    "validate_param_value",
    "validate_parent",
    "validate_root_only",
    "validate_structural_effects",
]
