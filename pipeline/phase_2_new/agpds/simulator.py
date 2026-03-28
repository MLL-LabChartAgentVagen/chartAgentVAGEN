"""
Sprint 1–6 — FactTableSimulator: SDK entry-point, registries, declaration
API, DAG construction orchestration, and generate() pipeline shell.

Post-Sprint-6 Refactoring: runtime implementation details have been
extracted into dedicated modules while FactTableSimulator retains all
public API methods and thin delegation shells for backward compatibility:
  - agpds.dag — graph algorithms (cycle detection, topological sort)
  - agpds.engine_skeleton — Phase α skeleton builder and samplers
  - agpds.pattern_engine — Phase γ pattern injection
  - agpds.realism_engine — Phase δ realism injection
  - agpds.metadata — §2.6 schema metadata builder

Responsibilities that remain in this module:
  - FactTableSimulator class with constructor and all declaration methods
  - Internal registries (_columns, _groups, etc.) and registry-bound helpers
  - _build_full_dag() orchestration (reads multiple registries)
  - _post_process() DataFrame assembly (reads column types)
  - generate() orchestration shell
  - Declaration-phase validation (param_model, effects, weights, formula)
"""
from __future__ import annotations

import logging
import math
import re
from collections import OrderedDict
from datetime import date
from typing import Any, Optional

import numpy as np
import pandas as pd

from agpds.exceptions import (
    CyclicDependencyError,
    DuplicateColumnError,
    DuplicateGroupRootError,
    EmptyValuesError,
    InvalidParameterError,
    NonRootDependencyError,
    ParentNotFoundError,
    UndefinedEffectError,
    WeightLengthMismatchError,
)
from agpds.models import DimensionGroup, GroupDependency, OrthogonalPair

import agpds.dag as _dag
import agpds.engine_skeleton as _engine
import agpds.metadata as _meta
import agpds.pattern_engine as _pattern
import agpds.realism_engine as _realism

logger = logging.getLogger(__name__)

# ===== Module-Level Constants =====

# §2.1.1 whitelist: "Derived columns (day_of_week, month, quarter, is_weekend)"
_TEMPORAL_DERIVE_WHITELIST: frozenset[str] = frozenset(
    {"day_of_week", "month", "quarter", "is_weekend"}
)

# [A10] The temporal group is auto-named "time"; this name is reserved
# and cannot be used by add_category.
_TEMPORAL_GROUP_NAME: str = "time"

# §2.1.1: Supported distribution family whitelist
_SUPPORTED_FAMILIES: frozenset[str] = frozenset({
    "gaussian", "lognormal", "gamma", "beta",
    "uniform", "poisson", "exponential", "mixture",
})

# [A5] Only gaussian and lognormal have spec-defined param_model key names.
# Other families store raw dicts without key validation until Blocker 3 resolves.
_VALIDATED_PARAM_KEYS: dict[str, frozenset[str]] = {
    "gaussian": frozenset({"mu", "sigma"}),
    "lognormal": frozenset({"mu", "sigma"}),
}

# Regex pattern for extracting identifier symbols from arithmetic formulas.
# Matches Python-style identifiers: letter or underscore followed by
# alphanumerics/underscores. Used by _extract_formula_symbols.
_IDENTIFIER_RE: re.Pattern[str] = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")

# ===== Sprint 4 Module-Level Constants =====

# §2.1.2 pattern types: the six declared pattern type strings.
_VALID_PATTERN_TYPES: frozenset[str] = frozenset({
    "outlier_entity", "trend_break", "ranking_reversal",
    "dominance_shift", "convergence", "seasonal_anomaly",
})

# §2.1.2 examples: outlier_entity requires z_score in params.
_OUTLIER_ENTITY_REQUIRED_KEYS: frozenset[str] = frozenset({"z_score"})

# §2.1.2 examples: trend_break requires break_point and magnitude in params.
_TREND_BREAK_REQUIRED_KEYS: frozenset[str] = frozenset({
    "break_point", "magnitude",
})

# Mapping from the two fully-specified pattern types to their required
# params keys. The remaining four types have no spec-defined params
# schema and accept any dict (subtask 1.8.4, Finding A8).
_PATTERN_REQUIRED_PARAMS: dict[str, frozenset[str]] = {
    "outlier_entity": _OUTLIER_ENTITY_REQUIRED_KEYS,
    "trend_break": _TREND_BREAK_REQUIRED_KEYS,
}


class FactTableSimulator:
    """Top-level SDK class for declaring and generating atomic-grain fact tables.

    [Subtask 1.1.1, 1.1.2]

    The LLM-generated script instantiates this class, calls declaration methods
    (add_category, add_measure, etc.) to build the schema, then calls generate()
    to produce the Master DataFrame and schema metadata.

    Public Attributes:
        target_rows: Number of rows to generate (positive int).
        seed: Random seed for NumPy RNG reproducibility.

    Internal Registries (set in __init__) [Subtask 1.1.2]:
        _columns: Insertion-ordered mapping of column name -> column metadata dict.
                  Preserves declaration order for deterministic DAG construction.
        _groups: Mapping of group name -> DimensionGroup dataclass instance.
        _orthogonal_pairs: List of OrthogonalPair declarations.
        _group_dependencies: List of GroupDependency declarations.
        _patterns: List of pattern specification dicts (from inject_pattern).
        _realism_config: Optional dict holding missing_rate, dirty_rate, censoring.
                         None until set_realism() is called.
        _measure_dag: Adjacency list for the measure-only sub-DAG.
                      Keys are measure names; values are lists of downstream
                      measures that depend on the key.
    """

    def __init__(self, target_rows: int, seed: int) -> None:
        """Initialize the simulator with empty registries.

        [Subtask 1.1.1]

        Args:
            target_rows: Positive integer — the number of rows to generate.
            seed: Integer seed for numpy.random.default_rng reproducibility.

        Raises:
            TypeError: If target_rows is not an int (rejects float, str, None).
            TypeError: If seed is not an int (rejects float, str, None).
            ValueError: If target_rows is not positive (le 0).
        """
        # ===== Input Validation =====

        # Reject bool for target_rows — bool is an int subclass that
        # isinstance(x, int) alone would silently accept, but True/False
        # are not meaningful row counts.
        if not isinstance(target_rows, int) or isinstance(target_rows, bool):
            raise TypeError(
                f"target_rows must be an int, got {type(target_rows).__name__}."
            )

        # Reject bool for seed — same rationale as target_rows above
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise TypeError(
                f"seed must be an int, got {type(seed).__name__}."
            )

        # target_rows must be positive — zero or negative rows are meaningless
        if target_rows <= 0:
            raise ValueError(
                f"target_rows must be a positive integer, got {target_rows}."
            )

        # ===== Store Public Attributes =====

        # These are the two user-facing configuration values from §2.5 one-shot example
        self.target_rows: int = target_rows
        self.seed: int = seed

        # FIX: [self-review item 6] — Added comment above logger.debug call
        # Log successful initialization for DEBUG-level tracing
        logger.debug(
            "FactTableSimulator initialized: target_rows=%d, seed=%d",
            target_rows,
            seed,
        )

        # ===== Initialize Internal Registries [Subtask 1.1.2] =====

        # Column registry: OrderedDict preserves insertion order, which matters
        # for deterministic DAG construction and §2.6 metadata column ordering.
        self._columns: OrderedDict[str, dict[str, Any]] = OrderedDict()

        # Group registry: maps group name -> DimensionGroup instance.
        self._groups: dict[str, DimensionGroup] = {}

        # Orthogonal pair declarations: populated by declare_orthogonal().
        self._orthogonal_pairs: list[OrthogonalPair] = []

        # Cross-group root-level dependency declarations
        self._group_dependencies: list[GroupDependency] = []

        # Pattern specifications: populated by inject_pattern().
        self._patterns: list[dict[str, Any]] = []

        # Realism configuration: None until set_realism() is called.
        self._realism_config: Optional[dict[str, Any]] = None

        # Measure sub-DAG adjacency list
        self._measure_dag: dict[str, list[str]] = {}

    # ================================================================
    # Sprint 2: Column Declaration API
    # ================================================================

    def add_category(
        self,
        name: str,
        values: list[str],
        weights: list[float] | dict[str, list[float]],
        group: str,
        parent: str | None = None,
    ) -> None:
        """Declare a categorical column in a named dimension group.

        [Subtasks 1.2.1, 1.2.2, 1.2.3, 1.2.4, 1.2.5, 1.2.6]

        Registers a categorical column, validates all inputs, creates or
        updates the dimension group, and stores the column metadata. Weights
        are auto-normalized to sum to 1.0 (§2.1.1). If parent is specified,
        the parent must exist in the same group (§2.1.1). If parent is None,
        the column becomes the group root; each group may have only one root
        (§2.2).

        Args:
            name: Unique column name across all groups.
            values: Categorical values; must have len >= 2 ([A9]).
            weights: Either a flat list[float] (same distribution for all
                     parent values) or a dict[str, list[float]] mapping each
                     parent value to a weight vector (§2.1.1 per-parent form).
            group: Dimension group name. Must not be "time" (reserved [A10]).
            parent: Parent column name within the same group, or None for root.

        Raises:
            TypeError: If name, group are not str; parent not str/None;
                       values not list; weights not list or dict.
            DuplicateColumnError: If name already registered in _columns.
            EmptyValuesError: If values is empty (§2.1.1).
            InvalidParameterError: If len(values) < 2 ([A9]).
            WeightLengthMismatchError: If flat weights length != values length,
                                       or any per-parent vector length mismatch.
            ValueError: If any weight is negative.
            ValueError: If all weights sum to zero (non-normalizable).
            ValueError: If group == "time" (reserved for temporal [A10]).
            ParentNotFoundError: If parent not in same group (§2.1.1).
            DuplicateGroupRootError: If parent=None and group already has root.
            ValueError: If per-parent dict keys don't match parent's values [A6].
        """
        # ===== Phase 1: Type Checks [Subtask 1.2.1] =====

        # Reject non-str name — column names must be strings for DAG node identity
        if not isinstance(name, str):
            raise TypeError(
                f"name must be a str, got {type(name).__name__}."
            )

        # Reject non-list values — must be an actual list, not a bare string or tuple
        if not isinstance(values, list):
            raise TypeError(
                f"values must be a list, got {type(values).__name__}."
            )

        # Reject weights that are neither list nor dict — the only two accepted forms
        if not isinstance(weights, (list, dict)):
            raise TypeError(
                f"weights must be a list or dict, got {type(weights).__name__}."
            )

        # Reject non-str group — group names are dict keys and must be strings
        if not isinstance(group, str):
            raise TypeError(
                f"group must be a str, got {type(group).__name__}."
            )

        # Reject parent that is neither str nor None — only these two types are valid
        if parent is not None and not isinstance(parent, str):
            raise TypeError(
                f"parent must be a str or None, got {type(parent).__name__}."
            )

        # ===== Phase 2: Value Validation [Subtask 1.2.1] =====

        # §2.1.1: "rejects empty values" — an empty category cannot be sampled
        if len(values) == 0:
            raise EmptyValuesError(name)

        # [A9] Single-value categoricals are statistically degenerate (zero
        # variance, chi-squared undefined); require at least 2 values
        if len(values) < 2:
            raise InvalidParameterError(
                param_name="values",
                value=float(len(values)),
                reason="categorical columns require at least 2 values ([A9])",
            )

        # ===== Phase 3: Duplicate Column Check [Subtask 1.2.1] =====

        # Column names must be unique across all groups — duplicates would
        # corrupt the DAG with ambiguous node identity
        if name in self._columns:
            raise DuplicateColumnError(name)

        # ===== Phase 4: Reserved Group Name Check [A10] =====

        # "time" is reserved for the temporal dimension group; using it for
        # a categorical group would collide with add_temporal
        if group == _TEMPORAL_GROUP_NAME:
            raise ValueError(
                f"Group name '{_TEMPORAL_GROUP_NAME}' is reserved for "
                f"temporal columns. Use a different group name."
            )

        # ===== Phase 5: Parent Validation [Subtask 1.2.4] =====

        if parent is not None:
            # Parent must be a declared column in the same group — orphaned
            # hierarchy edges produce undefined sampling behavior
            if parent not in self._columns:
                raise ParentNotFoundError(
                    child_name=name, parent_name=parent, group=group
                )

            # Parent must belong to the same group — cross-group parent-child
            # relationships are not supported (use add_group_dependency instead)
            parent_meta = self._columns[parent]
            if parent_meta.get("group") != group:
                raise ParentNotFoundError(
                    child_name=name, parent_name=parent, group=group
                )

        # ===== Phase 6: Duplicate Root Check [Subtask 1.2.6] =====

        # §2.2: "each group has a root column" (singular) — enforce uniqueness
        if parent is None and group in self._groups:
            existing_group = self._groups[group]
            if existing_group.root != "":
                raise DuplicateGroupRootError(
                    group_name=group,
                    existing_root=existing_group.root,
                    attempted_root=name,
                )

        # ===== Phase 7: Weight Validation & Normalization =====

        if isinstance(weights, list):
            # --- Flat weight list [Subtask 1.2.1, 1.2.2] ---
            normalized_weights = self._validate_and_normalize_flat_weights(
                name, values, weights
            )
            # Store as flat list; engine broadcasts to all parent values
            stored_weights: list[float] | dict[str, list[float]] = (
                normalized_weights
            )
        else:
            # --- Per-parent conditional weight dict [Subtask 1.2.3] ---
            # Per-parent dict requires a parent column to condition on
            if parent is None:
                raise ValueError(
                    f"Column '{name}': per-parent weight dict requires "
                    f"parent to be set, but parent is None."
                )

            # Validate and normalize the per-parent dict against parent's values
            stored_weights = self._validate_and_normalize_dict_weights(
                name, values, weights, parent
            )

        # ===== Phase 8: Group Registry Update [Subtask 1.2.5] =====

        if group not in self._groups:
            # Create new group — root will be set below if parent is None
            self._groups[group] = DimensionGroup(
                name=group, root="", columns=[], hierarchy=[]
            )

        grp = self._groups[group]

        # If this is a root column (no parent), record it as the group root
        if parent is None:
            grp.root = name
            # Root is first in hierarchy (root-first ordering per §2.2)
            grp.hierarchy.insert(0, name)
        else:
            # Child columns are appended to hierarchy after the root
            grp.hierarchy.append(name)

        # Append to group's column list in insertion order
        grp.columns.append(name)

        # ===== Phase 9: Column Registry Update [Subtask 1.2.5] =====

        # Store column metadata dict — schema for categorical columns includes
        # type, group, parent, values, and normalized weights
        self._columns[name] = {
            "type": "categorical",
            "group": group,
            "parent": parent,
            "values": list(values),
            "weights": stored_weights,
        }

        # FIX: [self-review item 6] — Added comment above logger.debug call
        # Log successful column registration for DEBUG-level tracing
        logger.debug(
            "add_category: registered '%s' in group '%s' (parent=%s, "
            "n_values=%d)",
            name,
            group,
            parent,
            len(values),
        )

    def add_temporal(
        self,
        name: str,
        start: str,
        end: str,
        freq: str,
        derive: list[str] | None = None,
    ) -> None:
        """Declare a temporal column with optional derived calendar features.

        [Subtasks 1.3.1, 1.3.2, 1.3.3, 1.3.4]

        Registers a temporal root column, parses and validates date range,
        validates frequency and derive tokens, and creates the "time" dimension
        group with the temporal root and any derived children.

        Only one add_temporal call is allowed per simulator instance ([A10]).
        The group name "time" is auto-assigned and reserved.

        FIX: [self-review item 1] — The 1.3.1 done condition says "Parsed
        start/end as datetime". This implementation stores datetime.date (not
        datetime.datetime) because the spec's ISO-8601 examples are date-only
        ("2024-01-01"). If the engine sprint (4.1.4) needs sub-day precision,
        this can be upgraded to datetime.datetime at that time.

        Args:
            name: Unique column name for the temporal root.
            start: ISO-8601 date string (e.g. "2024-01-01").
            end: ISO-8601 date string. Must be strictly after start.
            freq: Frequency string. Stored as-is; only "daily" has defined
                  sampling semantics ([B1]).
            derive: List of derived column tokens from whitelist:
                    {"day_of_week", "month", "quarter", "is_weekend"}.
                    Defaults to empty list.

        Raises:
            TypeError: If name not str; start/end not str; freq not str;
                       derive not list.
            DuplicateColumnError: If name or any derived name already registered.
            ValueError: If start or end not parseable as ISO-8601 date.
            ValueError: If end <= start.
            ValueError: If freq is empty string.
            ValueError: If derive contains unknown token or duplicates.
            ValueError: If add_temporal already called ([A10]).
            ValueError: If group "time" already exists from add_category ([A10]).
        """
        # Default derive to empty list if None
        if derive is None:
            derive = []

        # ===== Phase 1: Type Checks [Subtask 1.3.1] =====

        # Reject non-str name — temporal column names are DAG node identifiers
        if not isinstance(name, str):
            raise TypeError(
                f"name must be a str, got {type(name).__name__}."
            )

        # Reject non-str start/end — must be parseable date strings
        if not isinstance(start, str):
            raise TypeError(
                f"start must be a str, got {type(start).__name__}."
            )
        if not isinstance(end, str):
            raise TypeError(
                f"end must be a str, got {type(end).__name__}."
            )

        # Reject non-str freq — frequency is stored as a string label
        if not isinstance(freq, str):
            raise TypeError(
                f"freq must be a str, got {type(freq).__name__}."
            )

        # Reject non-list derive — must be a list of whitelist tokens
        if not isinstance(derive, list):
            raise TypeError(
                f"derive must be a list, got {type(derive).__name__}."
            )

        # ===== Phase 2: Singleton Constraint [A10] =====

        # Only one temporal column is allowed per simulator; a second call
        # would create an ambiguous temporal dimension
        if _TEMPORAL_GROUP_NAME in self._groups:
            raise ValueError(
                f"Only one add_temporal call is allowed. "
                f"Group '{_TEMPORAL_GROUP_NAME}' already exists."
            )

        # ===== Phase 3: Duplicate Column Check [Subtask 1.3.1] =====

        # Temporal root name must be unique across all declared columns
        if name in self._columns:
            raise DuplicateColumnError(name)

        # ===== Phase 4: Date Parsing & Range Validation [Subtask 1.3.1] =====

        # Parse start date from ISO-8601 string
        start_date = self._parse_iso_date(start, "start")

        # Parse end date from ISO-8601 string
        end_date = self._parse_iso_date(end, "end")

        # end must be strictly after start — equal dates produce an empty
        # range with no valid samples
        if end_date <= start_date:
            raise ValueError(
                f"end date ({end}) must be strictly after start date ({start})."
            )

        # ===== Phase 5: Frequency Validation [Subtask 1.3.2] =====

        # [B1] No whitelist; accept any non-empty string. Only "daily" has
        # defined sampling semantics; others stored for future engine support.
        if freq == "":
            raise ValueError("freq must be a non-empty string.")

        # ===== Phase 6: Derive Whitelist Validation [Subtask 1.3.3] =====

        # Check for duplicate derive tokens before whitelist validation —
        # duplicates would create duplicate column registrations
        if len(derive) != len(set(derive)):
            seen: set[str] = set()
            for token in derive:
                if token in seen:
                    raise ValueError(
                        f"Duplicate derive token: '{token}'. "
                        f"Each derivation may only be specified once."
                    )
                seen.add(token)

        # Validate each token against the §2.1.1 whitelist
        for token in derive:
            if token not in _TEMPORAL_DERIVE_WHITELIST:
                raise ValueError(
                    f"Unknown derive token '{token}'. "
                    f"Allowed: {sorted(_TEMPORAL_DERIVE_WHITELIST)}."
                )

        # Check that derived column names don't collide with existing columns
        for token in derive:
            if token in self._columns:
                raise DuplicateColumnError(token)

        # ===== Phase 7: Temporal Group Registration [Subtask 1.3.4] =====

        # Build the column list: temporal root first, then derived children
        all_columns = [name] + list(derive)

        # FIX: [self-review item 1] — §2.6 example shows "time" hierarchy as
        # ["visit_date"] (root only), not ["visit_date", "day_of_week", "month"].
        # Derived temporal columns are computed features, not a drill-down
        # hierarchy like categorical parent→child. Hierarchy = root only.
        self._groups[_TEMPORAL_GROUP_NAME] = DimensionGroup(
            name=_TEMPORAL_GROUP_NAME,
            root=name,
            columns=list(all_columns),
            hierarchy=[name],
        )

        # ===== Phase 8: Column Registry Updates [Subtask 1.3.4] =====

        # Register the temporal root column with parsed date range and freq
        self._columns[name] = {
            "type": "temporal",
            "group": _TEMPORAL_GROUP_NAME,
            "parent": None,
            "start": start_date,
            "end": end_date,
            "freq": freq,
            "derive": list(derive),
        }

        # Register each derived column with parent=<temporal root>.
        # NOTE: ``parent`` here expresses a DAG generation dependency
        # (the derive value is computed from the root date), NOT membership
        # in ``DimensionGroup.hierarchy``.  Derive columns belong to
        # ``columns`` but not ``hierarchy`` (§2.6).
        for token in derive:
            self._columns[token] = {
                "type": "temporal_derived",
                "group": _TEMPORAL_GROUP_NAME,
                "parent": name,
                "derivation": token,
            }

        # FIX: [self-review item 6] — Added comment above logger.debug call
        # Log successful temporal registration for DEBUG-level tracing
        logger.debug(
            "add_temporal: registered '%s' [%s to %s, freq=%s] "
            "with %d derived columns",
            name,
            start,
            end,
            freq,
            len(derive),
        )

    # ================================================================
    # Sprint 3: Measure Declaration API
    # ================================================================

    def add_measure(
        self,
        name: str,
        family: str,
        param_model: dict[str, Any],
        scale: float | None = None,
    ) -> None:
        """Declare a stochastic root measure.

        [Subtasks 1.4.1, 1.4.2, 1.4.5]

        Registers a root measure column with a named distribution family and
        parameter model. The measure becomes a root node (no incoming edges)
        in the measure sub-DAG. The param_model may be constant-parameter form
        (each key maps to a scalar) or intercept+effects form (each key maps
        to {"intercept": float, "effects": {col: {val: float}}}).

        Args:
            name: Unique column name.
            family: Distribution family from _SUPPORTED_FAMILIES.
            param_model: Parameter specification dict.  For gaussian/lognormal,
                         must contain keys "mu" and "sigma" ([A5]).  For other
                         non-mixture families, stored as-is without key
                         validation.
            scale: Optional scale factor.  Stored but ignored in generation
                   ([A2]).  Logs a DEBUG warning if non-None.

        Raises:
            TypeError: name not str; family not str; param_model not dict;
                       scale not float/int/None.
            DuplicateColumnError: name already registered in _columns.
            ValueError: family not in _SUPPORTED_FAMILIES.
            NotImplementedError: family == "mixture" (BLOCKED: 1.4.4).
            InvalidParameterError: Validated family missing required keys
                                    or non-numeric scalar values.
            UndefinedEffectError: Effects reference undeclared column or
                                  value not in column's value set.
        """
        # ===== Phase 1: Type Checks [Subtask 1.4.1] =====

        # Reject non-str name — measure column names are DAG node identifiers
        if not isinstance(name, str):
            raise TypeError(
                f"name must be a str, got {type(name).__name__}."
            )

        # Reject non-str family — family must be a string label
        if not isinstance(family, str):
            raise TypeError(
                f"family must be a str, got {type(family).__name__}."
            )

        # Reject non-dict param_model — must be a mapping of param names to specs
        if not isinstance(param_model, dict):
            raise TypeError(
                f"param_model must be a dict, got {type(param_model).__name__}."
            )

        # Reject scale that is not None, int, or float — only numeric types valid
        if scale is not None and not isinstance(scale, (int, float)):
            raise TypeError(
                f"scale must be a float, int, or None, "
                f"got {type(scale).__name__}."
            )
        # Reject bool for scale — bool is an int subclass but not a meaningful scale
        if isinstance(scale, bool):
            raise TypeError(
                f"scale must be a float, int, or None, got bool."
            )

        # ===== Phase 2: Duplicate Column Check [Subtask 1.4.1] =====

        # Column names are unique across all declaration methods — a measure
        # cannot share a name with a category, temporal, or another measure
        if name in self._columns:
            raise DuplicateColumnError(name)

        # ===== Phase 3: Family Validation [Subtask 1.4.1] =====

        # Reject unsupported family strings (§2.1.1 supported distributions)
        if family not in _SUPPORTED_FAMILIES:
            raise ValueError(
                f"Unsupported distribution family: '{family}'. "
                f"Supported: {sorted(_SUPPORTED_FAMILIES)}."
            )

        # Mixture family is syntactically valid but semantically BLOCKED —
        # the param_model schema for mixtures is entirely unspecified (A1)
        if family == "mixture":
            raise NotImplementedError("BLOCKED: 1.4.4 — mixture family sub-spec undefined (Finding A1).")

        # ===== Phase 4: Scale Handling [Subtask 1.4.1, A2] =====

        # [A2] scale is stored but has no generation-time effect; warn the
        # caller via DEBUG log so they know it's a no-op
        if scale is not None:
            logger.debug(
                "add_measure('%s'): scale=%s stored but will be ignored "
                "in generation ([A2] — scale semantics undefined).",
                name,
                scale,
            )

        # ===== Phase 5: param_model Validation [Subtask 1.4.2] =====

        # Validate param_model structure and effects references. For
        # gaussian/lognormal this checks required keys exist; for other
        # families it accepts any dict keys without validation.
        self._validate_param_model(name, family, param_model)

        # ===== Phase 6: Register as DAG Root Node [Subtask 1.4.5] =====

        # Stochastic measures are DAG roots — they have no incoming measure
        # edges. The adjacency list entry stores outgoing edges (downstream
        # structural measures that depend on this root).
        self._measure_dag[name] = []

        # ===== Phase 7: Column Registry Update [Subtask 1.4.5] =====

        # Store measure column metadata for downstream DAG construction,
        # effects resolution, and §2.6 metadata emission
        self._columns[name] = {
            "type": "measure",
            "measure_type": "stochastic",
            "family": family,
            "param_model": param_model,
            "scale": scale,
        }

        # Log successful measure registration for DEBUG-level tracing
        logger.debug(
            "add_measure: registered stochastic root '%s' (family=%s).",
            name,
            family,
        )

    def add_measure_structural(
        self,
        name: str,
        formula: str,
        effects: dict[str, dict[str, float]] | None = None,
        noise: dict[str, Any] | None = None,
    ) -> None:
        """Declare a structural (derived) measure.

        [Subtasks 1.5.1, 1.5.3, 1.5.5]

        Registers a structural measure defined by an arithmetic formula over
        previously declared measures and named effects. Creates directed edges
        in the measure DAG from each referenced measure to this measure.
        Detects cycles at declaration time.

        Args:
            name: Unique column name.
            formula: Arithmetic expression string referencing declared measures
                     and effect names. Must not be empty.
            effects: Mapping of effect names to {categorical_value: numeric}.
                     Each effect name must appear in formula; inner keys must
                     match values of some declared categorical column.
                     Defaults to empty dict.
            noise: Optional noise specification dict with "family" and
                   distribution-specific params. Stored as-is (full noise
                   validation for non-gaussian families is BLOCKED per 1.5.4).
                   Defaults to empty dict.

        Raises:
            TypeError: name not str; formula not str; effects not dict/None;
                       noise not dict/None.
            DuplicateColumnError: name already registered.
            ValueError: formula is empty string.
            ValueError: formula symbol references undeclared measure AND is
                        not an effect name AND is not a numeric literal.
            UndefinedEffectError: Effect name not in formula; or inner keys
                                  don't match any declared categorical column.
            CyclicDependencyError: Adding this measure creates a DAG cycle.
        """
        # Default mutable arguments to empty dicts
        if effects is None:
            effects = {}
        if noise is None:
            noise = {}

        # ===== Phase 1: Type Checks [Subtask 1.5.1] =====

        # Reject non-str name — structural measure names are DAG node identifiers
        if not isinstance(name, str):
            raise TypeError(
                f"name must be a str, got {type(name).__name__}."
            )

        # Reject non-str formula — must be an arithmetic expression string
        if not isinstance(formula, str):
            raise TypeError(
                f"formula must be a str, got {type(formula).__name__}."
            )

        # Reject non-dict effects — must be a mapping or None
        if not isinstance(effects, dict):
            raise TypeError(
                f"effects must be a dict or None, got {type(effects).__name__}."
            )

        # Reject non-dict noise — must be a mapping or None
        if not isinstance(noise, dict):
            raise TypeError(
                f"noise must be a dict or None, got {type(noise).__name__}."
            )

        # ===== Phase 2: Duplicate Column Check [Subtask 1.5.1] =====

        # Column names are unique across all declaration methods
        if name in self._columns:
            raise DuplicateColumnError(name)

        # ===== Phase 3: Formula Validation [Subtask 1.5.1] =====

        # Empty formula produces no deterministic component — reject upfront
        if formula.strip() == "":
            raise ValueError(
                f"Structural measure '{name}': formula must not be empty."
            )

        # ===== Phase 4: Symbol Resolution [Subtask 1.5.1, 1.5.5] =====
        # FIX: [self-review item 3] — This phase implements subtask 1.5.2
        # (formula symbol resolution & DAG edge creation) which is not
        # explicitly listed in Sprint 3's subtask table but is a necessary
        # prerequisite for 1.5.5 (cycle detection). Without knowing which
        # edges to add, cycle detection is impossible. Documented as a
        # scope addendum required for correctness.

        # Extract all identifier symbols from the formula string
        formula_symbols = self._extract_formula_symbols(formula)

        # Build the set of effect names for resolution — these are symbols
        # that resolve to categorical lookups, not measure references
        effect_names = set(effects.keys())

        # Identify which formula symbols reference declared measures — these
        # become DAG edges (dependency → this structural measure)
        measure_refs: list[str] = []
        for sym in formula_symbols:
            if sym in effect_names:
                # Symbol resolves to a named effect — no DAG edge needed
                continue
            if sym in self._measure_dag:
                # Symbol resolves to a previously declared measure — record
                # as a dependency for DAG edge creation
                measure_refs.append(sym)
                continue
            # Symbol is neither an effect nor a declared measure — check if
            # it might be a categorical column or temporal column used as a
            # direct reference (which is not valid in a structural formula)
            # SPEC_AMBIGUOUS: The spec does not clarify whether categorical
            # column names can appear directly in structural formulas. We
            # require all non-literal, non-effect symbols to be declared
            # measures, matching §2.3: "formula references previously
            # declared measure columns by name."
            raise ValueError(
                f"Structural measure '{name}': undefined symbol '{sym}' "
                f"in formula. It is not a declared measure or an effect name. "
                f"Formula symbols must reference declared measures or effects "
                f"keys."
            )

        # ===== Phase 5: Effects Validation [Subtask 1.5.3] =====

        # Validate each effect: must be referenced in the formula, and inner
        # dict keys must match some declared categorical column's value set
        if effects:
            self._validate_structural_effects(name, formula, effects)

        # ===== Phase 6: Cycle Detection [Subtask 1.5.5] =====

        # Before adding edges, verify the measure DAG remains acyclic.
        # Defense-in-depth: with sequential declarations and unique names,
        # cycles are structurally impossible, but we check anyway per spec.
        if measure_refs:
            self._check_measure_dag_acyclic(name, measure_refs)

        # ===== Phase 7: DAG Edge Creation [Subtask 1.5.5] =====

        # Register this structural measure as a new DAG node
        self._measure_dag[name] = []

        # Create forward edges: each dependency points to this measure
        for dep in measure_refs:
            self._measure_dag[dep].append(name)

        # ===== Phase 8: Column Registry Update [Subtask 1.5.1] =====

        # Store structural measure metadata with all declaration fields
        # preserved for downstream formula evaluation and §2.6 emission
        self._columns[name] = {
            "type": "measure",
            "measure_type": "structural",
            "formula": formula,
            "effects": effects,
            "noise": noise,
            "depends_on": list(measure_refs),
        }

        # Log successful structural measure registration
        logger.debug(
            "add_measure_structural: registered '%s' (depends_on=%s).",
            name,
            measure_refs,
        )

    # ================================================================
    # Sprint 3: Relationship Declaration API
    # ================================================================

    def declare_orthogonal(
        self,
        group_a: str,
        group_b: str,
        rationale: str,
    ) -> None:
        """Declare two dimension groups as statistically independent.

        [Subtasks 1.6.1, 1.6.2, 1.6.3]

        Stores an OrthogonalPair. Validates both groups exist, rejects
        self-orthogonal, rejects duplicates, and checks for mutual-exclusion
        conflict with existing group dependencies.

        Args:
            group_a: First group name. Must exist in _groups.
            group_b: Second group name. Must exist in _groups.
            rationale: Human-readable justification for independence.

        Raises:
            TypeError: group_a, group_b, rationale not str.
            ValueError: group_a == group_b (self-orthogonal).
            ValueError: Either group not in _groups.
            ValueError: Pair already declared orthogonal.
            ValueError: Pair already has a group dependency (1.6.3 conflict).
        """
        # ===== Phase 1: Type Checks [Subtask 1.6.1] =====

        # Reject non-str group names — group lookup requires string keys
        if not isinstance(group_a, str):
            raise TypeError(
                f"group_a must be a str, got {type(group_a).__name__}."
            )
        if not isinstance(group_b, str):
            raise TypeError(
                f"group_b must be a str, got {type(group_b).__name__}."
            )

        # Reject non-str rationale — documentation text must be a string
        if not isinstance(rationale, str):
            raise TypeError(
                f"rationale must be a str, got {type(rationale).__name__}."
            )

        # ===== Phase 2: Self-Orthogonal Check [Subtask 1.6.1] =====

        # A group is trivially dependent on itself — self-orthogonal is
        # semantically nonsensical and likely a caller bug
        if group_a == group_b:
            raise ValueError(
                f"Cannot declare group '{group_a}' orthogonal to itself."
            )

        # ===== Phase 3: Group Existence Check [Subtask 1.6.1] =====

        # Both groups must have been populated by at least one add_category
        # or add_temporal call before they can participate in relationships
        if group_a not in self._groups:
            raise ValueError(
                f"Group '{group_a}' does not exist. Declare at least one "
                f"column in it before declaring relationships."
            )
        if group_b not in self._groups:
            raise ValueError(
                f"Group '{group_b}' does not exist. Declare at least one "
                f"column in it before declaring relationships."
            )

        # ===== Phase 4: Duplicate Pair Check [Subtask 1.6.2] =====

        # Check if this group pair has already been declared orthogonal;
        # OrthogonalPair.__eq__ is order-independent so we only check once
        candidate = OrthogonalPair(group_a, group_b, rationale)
        for existing in self._orthogonal_pairs:
            if existing == candidate:
                raise ValueError(
                    f"Groups '{group_a}' and '{group_b}' are already "
                    f"declared orthogonal."
                )

        # ===== Phase 5: Conflict with Group Dependencies [Subtask 1.6.3] =====

        # Mutual exclusion: a group pair cannot be both orthogonal and
        # dependent. This is inferred from §2.2 semantics — orthogonal
        # means P(A,B)=P(A)P(B), while dependency means P(A|B)≠P(A).
        self._check_dependency_conflict(group_a, group_b)

        # ===== Phase 6: Store Orthogonal Pair [Subtask 1.6.2] =====

        # Append the validated pair; downstream sprints use this list for
        # independent sampling (§2.4) and L1 chi-squared validation (§2.9)
        self._orthogonal_pairs.append(candidate)

        # Log successful orthogonal declaration
        logger.debug(
            "declare_orthogonal: '%s' ⊥ '%s' (rationale: %s).",
            group_a,
            group_b,
            rationale[:60],
        )

    def add_group_dependency(
        self,
        child_root: str,
        on: list[str],
        conditional_weights: dict[str, dict[str, float]],
    ) -> None:
        """Declare a cross-group root-level dependency.

        [Subtasks 1.7.1, 1.7.2, 1.7.3]

        Registers a GroupDependency where child_root's distribution is
        conditional on on[0]'s values. Both must be group roots in different
        groups. The root-level dependency graph must remain acyclic.

        Args:
            child_root: Column name; must be a group root.
            on: Exactly one column name in a list ([A7]).
            conditional_weights: Outer keys = values of on[0] column;
                                 inner keys = values of child_root column;
                                 inner values = weights (auto-normalized).

        Raises:
            TypeError: child_root not str; on not list; conditional_weights
                       not dict.
            NonRootDependencyError: child_root or on[0] is not a group root.
            ValueError: len(on) != 1 ([A7]).
            ValueError: on is empty.
            ValueError: child_root and on[0] in same group.
            ValueError: child_root == on[0] (self-dependency).
            ValueError: Outer keys don't cover all values of on[0].
            ValueError: Inner keys don't cover all values of child_root.
            ValueError: Any weight is negative.
            ValueError: All weights for an outer key are zero.
            ValueError: Pair already declared orthogonal (conflict).
            CyclicDependencyError: Root-level DAG cycle.
        """
        # ===== Phase 1: Type Checks [Subtask 1.7.1] =====

        # Reject non-str child_root — column lookup requires string
        if not isinstance(child_root, str):
            raise TypeError(
                f"child_root must be a str, got {type(child_root).__name__}."
            )

        # Reject non-list on — must be a list of column names
        if not isinstance(on, list):
            raise TypeError(
                f"on must be a list, got {type(on).__name__}."
            )

        # Reject non-dict conditional_weights — must be a nested mapping
        if not isinstance(conditional_weights, dict):
            raise TypeError(
                f"conditional_weights must be a dict, "
                f"got {type(conditional_weights).__name__}."
            )

        # ===== Phase 2: on Length Constraint [Subtask 1.7.2, A7] =====

        # [A7] Multi-column conditioning schema is undefined; restrict to
        # exactly one column until the spec resolves Finding A7
        if len(on) == 0:
            raise ValueError(
                "on must contain exactly one column name; got empty list."
            )
        if len(on) != 1:
            raise ValueError(
                f"on must contain exactly one column name ([A7]); "
                f"got {len(on)}: {on}."
            )

        parent_col = on[0]

        # ===== Phase 3: Self-Dependency Check =====

        # A column cannot depend on itself — this is a degenerate declaration
        if child_root == parent_col:
            raise ValueError(
                f"child_root '{child_root}' cannot depend on itself."
            )

        # ===== Phase 4: Root-Only Constraint [Subtask 1.7.1] =====

        # §2.2 root-only constraint: both child_root and on[0] must be the
        # root column of their respective groups. Non-root columns like
        # "department" must use within-group hierarchy instead.
        if not self._is_group_root(child_root):
            raise NonRootDependencyError(child_root)
        if not self._is_group_root(parent_col):
            raise NonRootDependencyError(parent_col)

        # ===== Phase 5: Same-Group Exclusion =====

        # Cross-group dependencies link different groups; within-group
        # relationships are expressed via parent-child hierarchy instead
        child_group = self._get_group_for_column(child_root)
        parent_group = self._get_group_for_column(parent_col)
        if child_group == parent_group:
            raise ValueError(
                f"child_root '{child_root}' and on column '{parent_col}' "
                f"are in the same group ('{child_group}'). "
                f"Cross-group dependencies must link different groups."
            )

        # ===== Phase 6: Categorical Column Requirement =====

        # SPEC_AMBIGUOUS: The spec only shows categorical-to-categorical
        # root dependencies. Temporal roots don't have discrete values, so
        # conditional_weights makes no sense for them. Reject temporal roots.
        # FIX: [self-review item 7] — Changed from bare ValueError to
        # InvalidParameterError to match §2.7 error taxonomy. The column
        # type is an invalid parameter value for this context.
        child_meta = self._columns.get(child_root, {})
        parent_meta = self._columns.get(parent_col, {})
        if child_meta.get("type") != "categorical":
            raise InvalidParameterError(
                param_name="child_root",
                value=0.0,
                reason=(
                    f"'{child_root}' must be a categorical column for "
                    f"cross-group dependency (got type="
                    f"'{child_meta.get('type')}')"
                ),
            )
        if parent_meta.get("type") != "categorical":
            raise InvalidParameterError(
                param_name="on",
                value=0.0,
                reason=(
                    f"'{parent_col}' must be a categorical column for "
                    f"cross-group dependency (got type="
                    f"'{parent_meta.get('type')}')"
                ),
            )

        # ===== Phase 7: Orthogonal Conflict Check [Subtask 1.6.3 inverse] =====

        # Mutual exclusion: groups already declared orthogonal cannot also
        # have a dependency — these are contradictory semantics
        self._check_orthogonal_conflict(child_group, parent_group)

        # ===== Phase 8: Conditional Weights Validation [Subtask 1.7.2] =====

        # Retrieve the declared value sets for outer/inner key validation
        parent_values: list[str] = parent_meta["values"]
        child_values: list[str] = child_meta["values"]
        parent_value_set = set(parent_values)
        child_value_set = set(child_values)

        # Outer keys must be exactly the values of the on[0] column — missing
        # keys leave undefined conditional distributions for some parent values
        provided_outer = set(conditional_weights.keys())
        missing_outer = parent_value_set - provided_outer
        if missing_outer:
            raise ValueError(
                f"conditional_weights is missing keys for on-column "
                f"'{parent_col}' values: {sorted(missing_outer)}."
            )

        # Reject extra outer keys that don't correspond to parent values —
        # these are typos or stale references
        extra_outer = provided_outer - parent_value_set
        if extra_outer:
            raise ValueError(
                f"conditional_weights contains keys not in '{parent_col}' "
                f"values: {sorted(extra_outer)}."
            )

        # Validate and normalize each inner weight dict independently
        normalized_cw: dict[str, dict[str, float]] = {}
        for outer_key, inner_dict in conditional_weights.items():
            # Inner dict must itself be a dict
            if not isinstance(inner_dict, dict):
                raise TypeError(
                    f"conditional_weights['{outer_key}'] must be a dict, "
                    f"got {type(inner_dict).__name__}."
                )

            # Inner keys must be exactly the values of child_root column
            provided_inner = set(inner_dict.keys())
            missing_inner = child_value_set - provided_inner
            if missing_inner:
                raise ValueError(
                    f"conditional_weights['{outer_key}'] is missing keys "
                    f"for child_root '{child_root}' values: "
                    f"{sorted(missing_inner)}."
                )

            # Reject extra inner keys not in child_root's value set
            extra_inner = provided_inner - child_value_set
            if extra_inner:
                raise ValueError(
                    f"conditional_weights['{outer_key}'] contains keys not "
                    f"in '{child_root}' values: {sorted(extra_inner)}."
                )

            # Normalize inner weights so they sum to 1.0 (rejects negatives
            # and all-zero vectors)
            normalized_cw[outer_key] = self._normalize_weight_dict_values(
                label=f"conditional_weights['{outer_key}']",
                weights=inner_dict,
            )

        # ===== Phase 9: Root-Level DAG Acyclicity Check [Subtask 1.7.3] =====

        # Before committing, verify that adding this dependency edge does
        # not create a cycle in the root-level dependency DAG
        self._check_root_dag_acyclic(child_root, parent_col)

        # ===== Phase 10: Store Dependency [Subtask 1.7.1] =====

        # Create and append the validated GroupDependency with normalized weights
        dep = GroupDependency(
            child_root=child_root,
            on=list(on),
            conditional_weights=normalized_cw,
        )
        self._group_dependencies.append(dep)

        # Log successful group dependency registration
        logger.debug(
            "add_group_dependency: '%s' depends on %s.",
            child_root,
            on,
        )

    # ================================================================
    # Sprint 4: Pattern & Realism Declaration API
    # ================================================================

    def inject_pattern(
        self,
        type: str,
        target: str,
        col: str,
        params: dict[str, Any],
    ) -> None:
        """Declare a narrative-driven statistical pattern for injection.

        [Subtasks 1.8.1, 1.8.2, 1.8.3, 1.8.5]

        Validates pattern type against the 6-type whitelist (§2.1.2),
        validates col references a declared measure column, validates
        required params keys for the two fully-specified types
        (outlier_entity, trend_break), and stores the pattern spec for
        Phase γ injection (§2.8 step γ).

        The remaining four pattern types (ranking_reversal, dominance_shift,
        convergence, seasonal_anomaly) accept arbitrary params dicts without
        key validation — their param schemas are undefined (Finding A8,
        Blocker 4).

        Args:
            type: Pattern type from _VALID_PATTERN_TYPES.
            target: DataFrame query expression string. Stored as-is for
                    runtime evaluation via df.query() — no declaration-time
                    parsing is performed (1.8.2 assumption locked).
            col: Must reference a declared measure column (1.8.3
                 assumption locked).
            params: Type-specific parameters dict.

        Raises:
            TypeError: type not str; target not str; col not str;
                       params not dict.
            ValueError: type not in _VALID_PATTERN_TYPES.
            ValueError: target is empty string.
            ValueError: col not in _columns.
            ValueError: col is not a measure column.
            ValueError: Required params keys missing for outlier_entity
                        or trend_break.
        """
        # ===== Phase 1: Type Checks [Subtask 1.8.1] =====

        # Reject non-str type — pattern type is a string label from whitelist
        if not isinstance(type, str):
            raise TypeError(
                f"type must be a str, got {type.__class__.__name__}."
            )

        # FIX: [self-review item 1] — Was using type.__class__.__name__ instead
        # of target.__class__.__name__, producing "got str" for any non-str
        # target when type had already passed its own check.
        # Reject non-str target — must be a df.query()-compatible expression
        if not isinstance(target, str):
            raise TypeError(
                f"target must be a str, got {target.__class__.__name__}."
            )

        # Reject non-str col — must be a column name string
        if not isinstance(col, str):
            raise TypeError(
                f"col must be a str, got {col.__class__.__name__}."
            )

        # Reject non-dict params — must be a mapping of param keys to values
        if not isinstance(params, dict):
            raise TypeError(
                f"params must be a dict, got {params.__class__.__name__}."
            )

        # ===== Phase 2: Pattern Type Validation [Subtask 1.8.1] =====

        # §2.1.2 whitelist: only six pattern types are accepted
        if type not in _VALID_PATTERN_TYPES:
            raise ValueError(
                f"Unknown pattern type '{type}'. "
                f"Valid types: {sorted(_VALID_PATTERN_TYPES)}."
            )

        # ===== Phase 3: Target Validation [Subtask 1.8.2] =====

        # Empty target would produce a df.query("") error at injection time;
        # reject upfront to give a clear declaration-time error
        if target.strip() == "":
            raise ValueError(
                "target must be a non-empty query expression string."
            )

        # ===== Phase 4: Column Validation [Subtask 1.8.3] =====

        # col must reference a declared column in the column registry
        if col not in self._columns:
            raise ValueError(
                f"Column '{col}' is not declared. inject_pattern requires "
                f"a declared measure column."
            )

        # col must be a measure column — pattern injection modifies numeric
        # measure values, not categorical or temporal columns
        col_meta = self._columns[col]
        if col_meta.get("type") != "measure":
            raise ValueError(
                f"Column '{col}' is type '{col_meta.get('type')}', not "
                f"'measure'. inject_pattern requires a measure column."
            )

        # ===== Phase 5: Params Validation [Subtask 1.8.1] =====

        # For the two fully-specified types, validate required param keys.
        # The remaining four types store params as-is (Finding A8, Blocker 4).
        if type in _PATTERN_REQUIRED_PARAMS:
            required = _PATTERN_REQUIRED_PARAMS[type]
            provided = set(params.keys())
            missing = required - provided
            if missing:
                raise ValueError(
                    f"Pattern type '{type}' requires params keys "
                    f"{sorted(required)}, but missing: {sorted(missing)}."
                )

        # ===== Phase 6: Store Pattern [Subtask 1.8.5] =====

        # Build a pattern spec dict and append to the _patterns list for
        # later injection during §2.8 Phase γ
        pattern_spec: dict[str, Any] = {
            "type": type,
            "target": target,
            "col": col,
            "params": dict(params),
        }
        self._patterns.append(pattern_spec)

        # Log successful pattern injection declaration
        logger.debug(
            "inject_pattern: stored '%s' pattern on col='%s' "
            "(target='%s').",
            type,
            col,
            target[:60],
        )

    def set_realism(
        self,
        missing_rate: float,
        dirty_rate: float,
        censoring: dict[str, Any] | None = None,
    ) -> None:
        """Configure realism injection (missing values, dirty data, censoring).

        [Subtask 1.9.1]

        Validates rates are in [0, 1]. Censoring is stored as an opaque dict
        pending Blocker 7 resolution ([A4]). Stores config in _realism_config.
        Calling this method a second time overwrites the previous config.

        Args:
            missing_rate: Fraction of cells to set to NaN, in [0, 1].
            dirty_rate: Fraction of categorical cells to corrupt, in [0, 1].
            censoring: Optional opaque dict for censoring configuration.
                       Schema deferred until Blocker 7 (A4) resolves.

        Raises:
            TypeError: missing_rate or dirty_rate not numeric (int/float);
                       censoring not dict or None.
            ValueError: missing_rate or dirty_rate outside [0, 1].
        """
        # ===== Phase 1: Type Checks [Subtask 1.9.1] =====

        # Reject bool for missing_rate — bool is an int subclass but not a
        # meaningful rate value
        if isinstance(missing_rate, bool):
            raise TypeError(
                f"missing_rate must be a float or int, got bool."
            )

        # Reject non-numeric missing_rate — rate must be a real number
        if not isinstance(missing_rate, (int, float)):
            raise TypeError(
                f"missing_rate must be a float or int, "
                f"got {type(missing_rate).__name__}."
            )

        # Reject bool for dirty_rate — same rationale as missing_rate
        if isinstance(dirty_rate, bool):
            raise TypeError(
                f"dirty_rate must be a float or int, got bool."
            )

        # Reject non-numeric dirty_rate — rate must be a real number
        if not isinstance(dirty_rate, (int, float)):
            raise TypeError(
                f"dirty_rate must be a float or int, "
                f"got {type(dirty_rate).__name__}."
            )

        # Reject censoring that is neither dict nor None — opaque dict or
        # absent, no other types accepted
        if censoring is not None and not isinstance(censoring, dict):
            raise TypeError(
                f"censoring must be a dict or None, "
                f"got {type(censoring).__name__}."
            )

        # ===== Phase 2: Rate Range Validation [Subtask 1.9.1] =====

        # FIX: [self-review item 2] — NaN floats silently passed the range
        # check because float('nan') < 0 and float('nan') > 1 are both False.
        # Added explicit NaN rejection before the range check.
        # FIX: [self-review item 6] — Added SPEC_AMBIGUOUS comment for this
        # net-new edge case not covered by the gap analysis.
        # SPEC_AMBIGUOUS: NaN rate inputs are not addressed by the spec or
        # gap analysis (Finding A4 covers censoring dict, not rate params).
        # Rejected here because NaN rates produce undefined injection behavior.

        # Reject NaN rates — NaN comparisons always return False, so NaN
        # would silently pass the [0, 1] range check below
        if math.isnan(missing_rate):
            raise ValueError(
                f"missing_rate must be in [0, 1], got {missing_rate} (NaN)."
            )
        if math.isnan(dirty_rate):
            raise ValueError(
                f"dirty_rate must be in [0, 1], got {dirty_rate} (NaN)."
            )

        # missing_rate must be in [0, 1] — it represents a probability
        if missing_rate < 0.0 or missing_rate > 1.0:
            raise ValueError(
                f"missing_rate must be in [0, 1], got {missing_rate}."
            )

        # dirty_rate must be in [0, 1] — it represents a probability
        if dirty_rate < 0.0 or dirty_rate > 1.0:
            raise ValueError(
                f"dirty_rate must be in [0, 1], got {dirty_rate}."
            )

        # ===== Phase 3: Store Config [Subtask 1.9.1] =====

        # Build the realism config dict. Censoring is stored as-is;
        # schema validation deferred until Blocker 7 resolves ([A4]).
        self._realism_config = {
            "missing_rate": float(missing_rate),
            "dirty_rate": float(dirty_rate),
            "censoring": dict(censoring) if censoring is not None else None,
        }

        # Log successful realism configuration
        logger.debug(
            "set_realism: missing_rate=%.4f, dirty_rate=%.4f, "
            "censoring=%s.",
            missing_rate,
            dirty_rate,
            "present" if censoring is not None else "None",
        )

    # ================================================================
    # Sprint 4: DAG Construction
    # ================================================================

    def _build_full_dag(self) -> dict[str, list[str]]:
        """Build the full generation DAG from all registered declarations.

        [Subtask 3.1.1]

        Merges edge types 1–4 into a single directed graph:
          (1) parent→child — within-group hierarchy edges
          (2) on→child_root — cross-group root dependency edges
          (3) temporal_root→derived — temporal derivation edges
          (4) effects predictor→measure — edges from categorical predictor
              columns to measures that use them in param_model effects
              (stochastic) or structural effects dicts

        Edge type 5 (formula measure ref→structural) is deferred until
        Blocker 2 resolves. However, measure→measure edges that were
        already recorded in _measure_dag during add_measure_structural
        declarations (Sprint 3) ARE included — these were derived via
        simple identifier extraction, not the blocked formula DSL.

        Returns:
            Forward adjacency dict {node: [successors]} containing every
            declared column as a node and every dependency as a directed
            edge.

        Raises:
            CyclicDependencyError: If the constructed DAG contains a cycle
                (should be structurally impossible if all declaration-time
                checks passed, but verified as defense-in-depth).
        """
        # Initialize adjacency list with all declared columns as nodes
        adjacency: dict[str, list[str]] = {
            col_name: [] for col_name in self._columns
        }

        # ===== Edge Type 1: parent→child (within-group hierarchy +
        #                    temporal derivation) =====

        # For every column that has a parent, add a directed edge from
        # parent to child.  This covers two distinct semantics:
        #   - Categorical hierarchy (e.g. hospital→department): conditional
        #     sampling, and reflected in DimensionGroup.hierarchy.
        #   - Temporal derivation (e.g. visit_date→day_of_week): deterministic
        #     transform, NOT reflected in DimensionGroup.hierarchy (§2.6).
        # Both use the ``parent`` field in _columns for DAG ordering.
        for col_name, col_meta in self._columns.items():
            parent = col_meta.get("parent")
            if parent is not None and parent in adjacency:
                adjacency[parent].append(col_name)

        # ===== Edge Type 2: on→child_root (cross-group root dependency) =====

        # For every group dependency, add an edge from each parent root
        # (on[0]) to the child root. This captures §2.2 cross-group
        # conditioning (e.g., severity→payment_method).
        for dep in self._group_dependencies:
            for parent_col in dep.on:
                if parent_col in adjacency:
                    adjacency[parent_col].append(dep.child_root)

        # ===== Edge Type 3: temporal_root→derived (temporal derivations) =====

        # Already captured by Edge Type 1 — temporal derived columns have
        # their temporal root as ``parent`` in column metadata, which gives
        # the correct DAG edge.  This is a generation-dependency edge only;
        # it does NOT imply these columns appear in DimensionGroup.hierarchy.
        # No additional processing needed here.

        # ===== Edge Type 4: effects predictor→measure =====

        # For each measure column, find all categorical columns that act
        # as predictors (via param_model effects or structural effects
        # dicts) and add edges from predictor→measure.
        for col_name, col_meta in self._columns.items():
            if col_meta.get("type") != "measure":
                continue

            measure_type = col_meta.get("measure_type")

            if measure_type == "stochastic":
                # Stochastic measures: extract predictor columns from
                # param_model intercept+effects dicts
                predictor_cols = self._collect_stochastic_predictor_cols(
                    col_meta.get("param_model", {})
                )
                for pred_col in predictor_cols:
                    if pred_col in adjacency:
                        adjacency[pred_col].append(col_name)

            elif measure_type == "structural":
                # Structural measures: resolve effects dict inner key sets
                # to categorical columns to find predictor edges
                effects = col_meta.get("effects", {})
                predictor_cols = self._collect_structural_predictor_cols(
                    effects
                )
                for pred_col in predictor_cols:
                    if pred_col in adjacency:
                        adjacency[pred_col].append(col_name)

        # ===== Include measure→measure edges from _measure_dag =====

        # These edges were computed at declaration time by
        # add_measure_structural (Sprint 3, subtask 1.5.5) via simple
        # regex symbol extraction. They are NOT edge type 5 (formula DSL
        # parsing) — they are pre-computed structural dependency edges.
        for upstream, downstreams in self._measure_dag.items():
            for downstream in downstreams:
                if upstream in adjacency:
                    adjacency[upstream].append(downstream)

        # ===== Deduplicate edges =====

        # Multiple edge sources may produce duplicates (e.g., a categorical
        # column appears in both parent→child and effects predictor→measure).
        # Deduplicate to keep the adjacency list clean.
        for node in adjacency:
            adjacency[node] = list(dict.fromkeys(adjacency[node]))

        # ===== Defense-in-depth cycle check =====

        # All declaration-time checks should prevent cycles, but verify
        # the assembled full DAG as a final safety net
        cycle_path = self._detect_cycle_in_adjacency(adjacency)
        if cycle_path is not None:
            raise CyclicDependencyError(cycle_path)

        logger.debug(
            "_build_full_dag: %d nodes, %d edges.",
            len(adjacency),
            sum(len(succs) for succs in adjacency.values()),
        )

        return adjacency

    def _topological_sort(
        self,
        adjacency: dict[str, list[str]],
    ) -> list[str]:
        """Deterministic topological sort.  Delegates to ``dag.topological_sort``."""
        return _dag.topological_sort(adjacency)

    def _extract_measure_sub_dag(
        self,
        full_dag: dict[str, list[str]],
    ) -> tuple[dict[str, list[str]], list[str]]:
        """Extract measure sub-DAG.  Delegates to ``dag.extract_measure_sub_dag``."""
        measure_names: set[str] = {
            col_name
            for col_name, col_meta in self._columns.items()
            if col_meta.get("type") == "measure"
        }
        return _dag.extract_measure_sub_dag(full_dag, measure_names)

    # ================================================================
    # Sprint 4: Private Helpers — DAG Edge Collection
    # ================================================================

    def _collect_stochastic_predictor_cols(
        self,
        param_model: dict[str, Any],
    ) -> set[str]:
        """Extract categorical predictor column names from a stochastic
        measure's param_model.

        [Subtask 3.1.1 helper]

        Scans each parameter value in param_model. If the value is a dict
        with an "effects" key, the keys of the effects sub-dict are
        categorical column names that act as predictors for this measure.

        Args:
            param_model: The param_model dict from a stochastic measure's
                         column metadata.

        Returns:
            Set of categorical column names referenced as predictors.
        """
        predictor_cols: set[str] = set()

        # Iterate over each parameter (e.g., "mu", "sigma") and check
        # whether it uses the intercept+effects form
        for _param_key, value in param_model.items():
            if not isinstance(value, dict):
                # Constant-form parameter — no categorical predictors
                continue
            effects = value.get("effects")
            if not isinstance(effects, dict):
                # No effects sub-dict — no categorical predictors
                continue

            # Each key in the effects dict is a categorical column name
            # that was already validated by _validate_effects_in_param
            for col_name in effects:
                if col_name in self._columns:
                    predictor_cols.add(col_name)

        return predictor_cols

    def _collect_structural_predictor_cols(
        self,
        effects: dict[str, dict[str, float]],
    ) -> set[str]:
        """Resolve structural measure effects to their categorical predictor
        columns.

        [Subtask 3.1.1 helper]

        For each effect name in a structural measure's effects dict, finds
        the categorical column whose declared value set matches the inner
        dict's key set. This mirrors the matching logic used by
        _validate_structural_effects at declaration time (Sprint 3,
        subtask 1.5.3).

        Args:
            effects: The effects dict from a structural measure's column
                     metadata (e.g., {"severity_surcharge": {"Mild": 50, ...}}).

        Returns:
            Set of categorical column names that act as predictors.
        """
        predictor_cols: set[str] = set()

        # FIX: [self-review item 5] — Added missing comment for this block.
        # Skip non-dict or empty effect values — cannot match against
        # column value sets for predictor resolution
        for _effect_name, val_map in effects.items():
            if not isinstance(val_map, dict) or len(val_map) == 0:
                continue

            # Match the inner key set against all declared categorical
            # columns to find the predictor column
            inner_keys = set(val_map.keys())
            for col_name, col_meta in self._columns.items():
                if col_meta.get("type") != "categorical":
                    continue
                if set(col_meta["values"]) == inner_keys:
                    predictor_cols.add(col_name)
                    break

        return predictor_cols

    # ================================================================
    # Sprint 3: Private Helpers — Lookup Utilities
    # ================================================================

    def _is_group_root(self, column_name: str) -> bool:
        """Check if a column is the root of its dimension group.

        [Subtask 1.7.1 helper]

        A column is a group root if it exists in _columns AND is recorded
        as the root of some group in _groups. Returns False for undeclared
        columns or non-root columns.
        """
        # Column must exist in the registry
        if column_name not in self._columns:
            return False

        # Find the group this column belongs to and check root status
        col_group = self._columns[column_name].get("group")
        if col_group is None or col_group not in self._groups:
            return False

        return self._groups[col_group].root == column_name

    def _get_group_for_column(self, column_name: str) -> str | None:
        """Return the group name a column belongs to, or None if not found.

        [Subtask 1.7.1 helper]
        """
        if column_name not in self._columns:
            return None
        return self._columns[column_name].get("group")

    # ================================================================
    # Sprint 3: Private Helpers — Conflict Detection
    # ================================================================

    def _check_orthogonal_conflict(
        self, group_a: str, group_b: str
    ) -> None:
        """Raise ValueError if group pair has an existing orthogonal declaration.

        [Subtask 1.6.3 / 1.7.3 helper]

        Used by add_group_dependency to enforce mutual exclusion: a pair
        that is declared orthogonal cannot also have a dependency.
        """
        # Build the canonical (order-independent) pair key for comparison
        candidate_pair = frozenset((group_a, group_b))

        # Search existing orthogonal declarations for a matching pair
        for pair in self._orthogonal_pairs:
            if pair.group_pair_set() == candidate_pair:
                raise ValueError(
                    f"Groups '{group_a}' and '{group_b}' are declared "
                    f"orthogonal. Cannot also declare a dependency between "
                    f"them (mutual exclusion per §2.2)."
                )

    def _check_dependency_conflict(
        self, group_a: str, group_b: str
    ) -> None:
        """Raise ValueError if group pair has an existing dependency declaration.

        [Subtask 1.6.3 helper]

        Used by declare_orthogonal to enforce mutual exclusion: a pair
        that has a dependency cannot also be declared orthogonal.
        """
        # Build the canonical pair key for comparison
        candidate_pair = frozenset((group_a, group_b))

        # Search existing group dependencies for a matching pair. A
        # dependency links the group of child_root with the group of on[0].
        for dep in self._group_dependencies:
            dep_child_group = self._get_group_for_column(dep.child_root)
            dep_parent_group = self._get_group_for_column(dep.on[0])
            if dep_child_group is None or dep_parent_group is None:
                continue
            dep_pair = frozenset((dep_child_group, dep_parent_group))
            if dep_pair == candidate_pair:
                raise ValueError(
                    f"Groups '{group_a}' and '{group_b}' already have a "
                    f"group dependency (child_root='{dep.child_root}', "
                    f"on={dep.on}). Cannot also declare them orthogonal "
                    f"(mutual exclusion per §2.2)."
                )

    # ================================================================
    # Sprint 3: Private Helpers — Cycle Detection
    # ================================================================

    @staticmethod
    def _detect_cycle_in_adjacency(
        adjacency: dict[str, list[str]],
    ) -> list[str] | None:
        """Cycle detection.  Delegates to ``dag.detect_cycle_in_adjacency``."""
        return _dag.detect_cycle_in_adjacency(adjacency)

    def _check_measure_dag_acyclic(
        self, new_node: str, depends_on: list[str]
    ) -> None:
        """Verify adding edges to the measure DAG would not create a cycle.

        [Subtask 1.5.5]

        Builds a tentative adjacency list including the proposed new node
        and edges, then runs cycle detection. Raises CyclicDependencyError
        if a cycle would be created.

        Note: With sequential declarations and unique names, cycles are
        structurally impossible (each new structural measure only adds
        incoming edges from existing nodes, and the new node has no outgoing
        edges yet). This check exists as defense-in-depth per spec §2.3.
        """
        # Build a copy of the current measure DAG adjacency list
        tentative: dict[str, list[str]] = {
            k: list(v) for k, v in self._measure_dag.items()
        }

        # Add the new node (no outgoing edges yet)
        tentative.setdefault(new_node, [])

        # Add proposed incoming edges: each dependency → new_node
        for dep in depends_on:
            tentative.setdefault(dep, [])
            tentative[dep].append(new_node)

        # Run cycle detection on the tentative graph
        cycle_path = self._detect_cycle_in_adjacency(tentative)
        if cycle_path is not None:
            raise CyclicDependencyError(cycle_path)

    def _check_root_dag_acyclic(
        self, new_child: str, new_parent: str
    ) -> None:
        """Verify adding a root-level dependency edge preserves DAG property.

        [Subtask 1.7.3]

        FIX: [self-review item 2] — The Message 1 interface sketch defined
        this as parameterless (_check_root_dag_acyclic(self) -> None). This
        implementation takes (new_child, new_parent) so the check runs BEFORE
        mutating _group_dependencies, ensuring failed validations don't corrupt
        state. This is an intentional improvement over the sketch.

        Builds the complete root-level dependency adjacency list from
        existing _group_dependencies plus the proposed new edge, then
        runs cycle detection. Raises CyclicDependencyError if a cycle
        would be created.
        """
        # Build adjacency list from all existing root-level dependencies.
        # Edge direction: on[0] → child_root (parent root → dependent root).
        adjacency: dict[str, list[str]] = {}
        for dep in self._group_dependencies:
            parent = dep.on[0]
            adjacency.setdefault(parent, [])
            adjacency.setdefault(dep.child_root, [])
            adjacency[parent].append(dep.child_root)

        # Add the proposed new edge: new_parent → new_child
        adjacency.setdefault(new_parent, [])
        adjacency.setdefault(new_child, [])
        adjacency[new_parent].append(new_child)

        # Run cycle detection on the combined graph
        cycle_path = self._detect_cycle_in_adjacency(adjacency)
        if cycle_path is not None:
            # FIX: [self-review item 1] — CyclicDependencyError.__init__ from
            # Sprint 1 hardcodes "Measure ... forms a cycle." in the message.
            # For root-level dependency cycles the nodes are categorical roots,
            # not measures. Override the message after construction so the §2.7
            # feedback loop reports the correct context to the LLM.
            exc = CyclicDependencyError(cycle_path)
            arrow_chain = " \u2192 ".join(f"'{n}'" for n in cycle_path)
            exc.message = f"Root dependency {arrow_chain} forms a cycle."
            raise exc

    # ================================================================
    # Sprint 3: Private Helpers — Formula & Symbol Utilities
    # ================================================================

    @staticmethod
    def _extract_formula_symbols(formula: str) -> set[str]:
        """Extract identifier symbols from an arithmetic formula string.

        [Subtask 1.5.1 helper]

        Returns all tokens matching [a-zA-Z_][a-zA-Z0-9_]* — i.e.,
        Python-style identifiers. Numeric literals (e.g. "12", "3.14")
        do not match this pattern and are naturally excluded.
        """
        # Use the pre-compiled regex to find all identifier tokens
        return set(_IDENTIFIER_RE.findall(formula))

    # ================================================================
    # Sprint 3: Private Helpers — param_model Validation
    # ================================================================

    def _validate_param_model(
        self, name: str, family: str, param_model: dict[str, Any]
    ) -> None:
        """Validate param_model for a stochastic measure.

        [Subtask 1.4.2]

        Dispatches between constant-parameter and intercept+effects forms.
        For gaussian/lognormal, validates that required keys (mu, sigma)
        exist. For other families, accepts any dict keys without validation
        ([A5]). For both forms, validates effects references against _columns
        when the intercept+effects form is used.

        A param key's value may be:
          - A numeric scalar (constant form for this parameter)
          - A dict with "intercept" key (intercept+effects form)
        Mixed forms (some params constant, others intercept+effects) are valid.
        """
        # ===== Phase 1: Required Key Check for Validated Families =====

        # [A5] Only gaussian and lognormal have spec-defined param keys;
        # for these families, verify required keys are present
        if family in _VALIDATED_PARAM_KEYS:
            required = _VALIDATED_PARAM_KEYS[family]
            missing = required - set(param_model.keys())
            if missing:
                raise InvalidParameterError(
                    param_name=sorted(missing)[0],
                    value=0.0,
                    reason=(
                        f"required param key(s) {sorted(missing)} missing "
                        f"for family '{family}'"
                    ),
                )

        # ===== Phase 2: Per-Key Validation =====

        # Validate each parameter value — it must be either a numeric scalar
        # or a well-formed intercept+effects dict
        for key, value in param_model.items():
            self._validate_param_value(name, family, key, value)

    def _validate_param_value(
        self,
        measure_name: str,
        family: str,
        param_key: str,
        value: Any,
    ) -> None:
        """Validate a single param_model value (constant or intercept+effects).

        [Subtask 1.4.2 helper]

        A value is valid if it is:
          (a) A numeric scalar (int or float, not bool)
          (b) A dict with "intercept" (numeric) and optional "effects" (dict)

        For validated families (gaussian/lognormal), non-numeric scalars in
        constant form raise InvalidParameterError. For other families, raw
        storage without type enforcement ([A5]).
        """
        # ===== Case A: Numeric Scalar (constant form) =====
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            # For validated families, we accept numeric scalars directly
            # For non-validated families, also accept without further checks
            return

        # ===== Case B: Intercept+Effects Dict =====
        if isinstance(value, dict):
            # Must contain "intercept" key with a numeric value
            if "intercept" not in value:
                # Only enforce for validated families; others store raw [A5]
                if family in _VALIDATED_PARAM_KEYS:
                    raise InvalidParameterError(
                        param_name=param_key,
                        value=0.0,
                        reason=(
                            f"intercept+effects dict for '{param_key}' "
                            f"must contain 'intercept' key"
                        ),
                    )
                # Non-validated families: accept raw dict without structure check
                return

            # Validate intercept is numeric
            intercept = value["intercept"]
            if not isinstance(intercept, (int, float)) or isinstance(
                intercept, bool
            ):
                if family in _VALIDATED_PARAM_KEYS:
                    raise InvalidParameterError(
                        param_name=f"{param_key}.intercept",
                        value=0.0,
                        reason="intercept must be a numeric scalar",
                    )
                return

            # Validate effects sub-dict if present
            if "effects" in value:
                effects = value["effects"]
                if not isinstance(effects, dict):
                    if family in _VALIDATED_PARAM_KEYS:
                        raise InvalidParameterError(
                            param_name=f"{param_key}.effects",
                            value=0.0,
                            reason="effects must be a dict",
                        )
                    return

                # Validate each effect column and its value keys against
                # the column registry
                # FIX: [self-review item 6] — This validation runs for ALL
                # families, including non-validated ones (gamma, beta, etc.),
                # even though subtask 1.4.3 (full intercept+effects validation)
                # is BLOCKED. The BLOCKED status is about per-family parameter
                # *key* validation (e.g., gamma shape vs alpha), not about
                # column-reference validation. Catching undeclared column refs
                # for any family is strictly safety-improving and prevents
                # silent DAG corruption downstream.
                self._validate_effects_in_param(
                    measure_name, param_key, effects
                )
            return

        # ===== Case C: Invalid Type =====

        # Value is neither numeric nor dict — invalid for validated families
        if family in _VALIDATED_PARAM_KEYS:
            raise InvalidParameterError(
                param_name=param_key,
                value=0.0,
                reason=(
                    f"value must be a numeric scalar or an "
                    f"intercept+effects dict, got {type(value).__name__}"
                ),
            )
        # Non-validated families: store raw without enforcement [A5]

    def _validate_effects_in_param(
        self,
        measure_name: str,
        param_key: str,
        effects: dict[str, dict[str, float]],
    ) -> None:
        """Validate effects within a param_model intercept+effects form.

        [Subtask 1.4.2 helper]

        Each key in effects must be a declared categorical column name.
        Each inner dict's keys must match that column's value set exactly.

        Raises:
            UndefinedEffectError: Column not declared or value key missing.
        """
        for col_name, val_map in effects.items():
            # The effects key must be a declared categorical column
            if col_name not in self._columns:
                raise UndefinedEffectError(
                    effect_name=col_name,
                    missing_value="(column not declared)",
                )

            col_meta = self._columns[col_name]
            if col_meta.get("type") != "categorical":
                raise UndefinedEffectError(
                    effect_name=col_name,
                    missing_value=(
                        f"(column '{col_name}' is type "
                        f"'{col_meta.get('type')}', not categorical)"
                    ),
                )

            # Inner dict must be a dict mapping categorical values to numerics
            if not isinstance(val_map, dict):
                raise UndefinedEffectError(
                    effect_name=col_name,
                    missing_value="(effect values must be a dict)",
                )

            # Every declared value of the column must appear as a key in
            # the inner dict — missing keys leave undefined effect values
            declared_values = set(col_meta["values"])
            provided_values = set(val_map.keys())
            missing_values = declared_values - provided_values
            if missing_values:
                # Report the first missing value for a clear error message
                first_missing = sorted(missing_values)[0]
                raise UndefinedEffectError(
                    effect_name=col_name,
                    missing_value=first_missing,
                )

            # SPEC_AMBIGUOUS: Extra keys (values in the effect dict that are
            # not in the column's declared values) are currently rejected.
            # The spec doesn't explicitly address this, but accepting them
            # would allow silent typos that corrupt effect resolution.
            extra_values = provided_values - declared_values
            if extra_values:
                first_extra = sorted(extra_values)[0]
                raise UndefinedEffectError(
                    effect_name=col_name,
                    missing_value=(
                        f"('{first_extra}' is not a value of column "
                        f"'{col_name}')"
                    ),
                )

    # ================================================================
    # Sprint 3: Private Helpers — Structural Effects Validation
    # ================================================================

    def _validate_structural_effects(
        self,
        measure_name: str,
        formula: str,
        effects: dict[str, dict[str, float]],
    ) -> None:
        """Validate the effects dict of a structural measure declaration.

        [Subtask 1.5.3]

        Each effect name must appear as a symbol in the formula.
        Inner dict keys must match the values of some declared categorical
        column (the column is identified by matching the inner key set
        against all declared categoricals).

        Raises:
            UndefinedEffectError: Effect name not in formula; or inner keys
                                  don't match any declared categorical column.
        """
        # Extract all identifier symbols from the formula for reference checks
        formula_symbols = self._extract_formula_symbols(formula)

        for effect_name, val_map in effects.items():
            # ===== Check 1: Effect name must appear in formula =====
            # An effect that is not referenced in the formula is a dead
            # definition — likely a typo or copy-paste error
            if effect_name not in formula_symbols:
                raise UndefinedEffectError(
                    effect_name=effect_name,
                    missing_value="(effect name not found in formula)",
                )

            # ===== Check 2: Inner dict must be a non-empty dict =====
            if not isinstance(val_map, dict) or len(val_map) == 0:
                raise UndefinedEffectError(
                    effect_name=effect_name,
                    missing_value=(
                        "(effect values must be a non-empty dict of "
                        "categorical_value -> numeric)"
                    ),
                )

            # ===== Check 3: Inner keys must match some categorical column =====
            # Search all declared categorical columns for one whose value
            # set exactly matches the inner dict keys
            inner_keys = set(val_map.keys())
            matched_column: str | None = None

            for col_name, col_meta in self._columns.items():
                if col_meta.get("type") != "categorical":
                    continue
                col_values = set(col_meta["values"])
                if col_values == inner_keys:
                    matched_column = col_name
                    break

            if matched_column is not None:
                # Exact match found — effect is valid
                continue

            # No exact match found — produce an informative error. Try to
            # find the closest partial match to suggest which column was
            # likely intended and which value is missing.
            best_col: str | None = None
            best_overlap = 0
            best_missing: set[str] = set()

            for col_name, col_meta in self._columns.items():
                if col_meta.get("type") != "categorical":
                    continue
                col_values = set(col_meta["values"])
                overlap = len(col_values & inner_keys)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_col = col_name
                    best_missing = col_values - inner_keys

            if best_col is not None and best_missing:
                # Report the first missing value from the best-matching column
                first_missing = sorted(best_missing)[0]
                raise UndefinedEffectError(
                    effect_name=effect_name,
                    missing_value=first_missing,
                )

            # No categorical columns have any overlap — completely unknown keys
            raise UndefinedEffectError(
                effect_name=effect_name,
                missing_value=(
                    f"(inner keys {sorted(inner_keys)} do not match any "
                    f"declared categorical column's values)"
                ),
            )

    # ================================================================
    # Sprint 3: Private Helpers — Weight Normalization
    # ================================================================

    def _normalize_weight_dict_values(
        self,
        label: str,
        weights: dict[str, float],
    ) -> dict[str, float]:
        """Normalize a {value: weight} dict so values sum to 1.0.

        [Subtask 1.7.2 helper]

        Used by add_group_dependency to normalize conditional weight rows.
        Rejects negative weights and all-zero vectors.

        Args:
            label: Descriptive label for error messages (e.g.
                   "conditional_weights['Mild']").
            weights: Mapping of categorical values to numeric weights.

        Returns:
            New dict with the same keys, values normalized to sum to 1.0.

        Raises:
            ValueError: If any weight is negative.
            ValueError: If all weights are zero (non-normalizable).
        """
        # Reject negative weights — probabilities cannot be negative
        for key, w in weights.items():
            if not isinstance(w, (int, float)):
                raise TypeError(
                    f"{label}: weight for '{key}' must be numeric, "
                    f"got {type(w).__name__}."
                )
            if isinstance(w, bool):
                raise TypeError(
                    f"{label}: weight for '{key}' must be numeric, got bool."
                )
            if w < 0:
                raise ValueError(
                    f"{label}: weight for '{key}' is negative ({w}). "
                    f"Weights must be >= 0."
                )

        # All-zero weights cannot be normalized — undefined distribution
        total = sum(weights.values())
        if total == 0:
            raise ValueError(
                f"{label}: all weights are zero. At least one weight "
                f"must be positive for normalization."
            )

        # Normalize each weight by the total so they sum to 1.0
        return {k: v / total for k, v in weights.items()}

    # ================================================================
    # Sprint 2: Private Helpers (unchanged)
    # ================================================================

    def _validate_and_normalize_flat_weights(
        self,
        column_name: str,
        values: list[str],
        weights: list[float],
    ) -> list[float]:
        """Validate a flat weight list and return normalized weights.

        [Subtask 1.2.1, 1.2.2]

        Checks length match, rejects negatives and all-zero vectors, then
        normalizes so weights sum to 1.0 (§2.1.1 "Auto-normalized").

        Args:
            column_name: Column name for error messages.
            values: The categorical values list (for length comparison).
            weights: Raw weight list to validate and normalize.

        Returns:
            Normalized weight list summing to 1.0.

        Raises:
            WeightLengthMismatchError: If len(weights) != len(values).
            ValueError: If any weight is negative.
            ValueError: If all weights are zero (non-normalizable).
        """
        # Length must match — each value needs exactly one weight
        if len(weights) != len(values):
            raise WeightLengthMismatchError(
                column_name=column_name,
                n_values=len(values),
                n_weights=len(weights),
            )

        # Reject negative weights — probabilities cannot be negative
        for i, w in enumerate(weights):
            if not isinstance(w, (int, float)):
                raise TypeError(
                    f"Weight at index {i} for column '{column_name}' "
                    f"must be numeric, got {type(w).__name__}."
                )
            if w < 0:
                raise ValueError(
                    f"Weight at index {i} for column '{column_name}' "
                    f"is negative ({w}). Weights must be >= 0."
                )

        # FIX: [self-review item 8] — Added SPEC_AMBIGUOUS comment for NaN/inf
        # handling. NaN/inf weights pass the negative check (NaN < 0 is False)
        # and the zero-sum check (NaN != 0), so they propagate into normalized
        # weights. Spec does not address non-finite weight inputs.
        # SPEC_AMBIGUOUS: NaN/inf weights pass validation and contaminate
        # normalization output. Not covered by gap analysis; net-new edge case.

        # All-zero weights cannot be normalized — the distribution is undefined
        total = sum(weights)
        if total == 0:
            raise ValueError(
                f"All weights for column '{column_name}' are zero. "
                f"At least one weight must be positive for normalization."
            )

        # Normalize to sum to 1.0 — §2.1.1 "Auto-normalized"
        return [w / total for w in weights]

    def _validate_and_normalize_dict_weights(
        self,
        column_name: str,
        values: list[str],
        weights: dict[str, list[float]],
        parent: str,
    ) -> dict[str, list[float]]:
        """Validate per-parent conditional weight dict and return normalized form.

        [Subtask 1.2.3]

        Each key must be a value of the parent column. Each vector must
        have the same length as `values`. Each vector is independently
        normalized. All parent values must appear as keys ([A6]).

        Args:
            column_name: Column name for error messages.
            values: The child categorical values list.
            weights: Dict mapping parent value -> weight vector.
            parent: Parent column name (must already be in _columns).

        Returns:
            Dict with same keys, each vector normalized to sum to 1.0.

        Raises:
            ValueError: If dict is empty.
            ValueError: If dict key is not a parent value.
            ValueError: If dict is missing a parent value key [A6].
            WeightLengthMismatchError: If any vector length != len(values).
            ValueError: If any weight is negative.
            ValueError: If any parent's weights are all zero.
        """
        # Empty dict provides no conditional distributions
        if len(weights) == 0:
            raise ValueError(
                f"Per-parent weight dict for column '{column_name}' is empty. "
                f"Must contain one entry per parent value."
            )

        # Look up the parent column's declared values for key validation
        parent_values = set(self._columns[parent]["values"])

        # [A6] Every parent value must be present as a dict key — missing
        # keys would leave undefined conditional distributions
        provided_keys = set(weights.keys())
        missing_keys = parent_values - provided_keys
        if missing_keys:
            raise ValueError(
                f"Per-parent weight dict for column '{column_name}' is "
                f"missing keys for parent values: {sorted(missing_keys)}. "
                f"All parent values must be present ([A6])."
            )

        # Reject keys that are not valid parent values — typos or stale
        # references would silently corrupt conditional distributions
        extra_keys = provided_keys - parent_values
        if extra_keys:
            raise ValueError(
                f"Per-parent weight dict for column '{column_name}' contains "
                f"keys not in parent '{parent}' values: {sorted(extra_keys)}."
            )

        # Validate and normalize each parent's weight vector independently
        normalized: dict[str, list[float]] = {}
        for parent_val, vec in weights.items():
            # Reuse the flat validation logic per parent value — same rules
            # apply to each conditional weight vector
            normalized[parent_val] = self._validate_and_normalize_flat_weights(
                column_name=f"{column_name}[{parent_val}]",
                values=values,
                weights=vec,
            )

        return normalized

    @staticmethod
    def _parse_iso_date(date_str: str, field_name: str) -> date:
        """Parse an ISO-8601 date string to a datetime.date object.

        [Subtask 1.3.1]

        Args:
            date_str: ISO-8601 date string (e.g. "2024-01-01").
            field_name: Field name for error messages ("start" or "end").

        Returns:
            Parsed date object.

        Raises:
            ValueError: If the string is not a valid ISO-8601 date.
        """
        try:
            # Use date.fromisoformat for strict ISO-8601 date parsing
            return date.fromisoformat(date_str)
        except (ValueError, TypeError) as exc:
            # FIX: [self-review item 5] — Added comment above except block
            # Re-raise with descriptive message so the §2.7 feedback loop
            # can report the exact field and parsing failure to the LLM
            raise ValueError(
                f"Cannot parse '{field_name}' as ISO-8601 date: "
                f"'{date_str}'. Expected format: YYYY-MM-DD."
            ) from exc

    # ================================================================
    # Sprint 5: Public API — generate()
    # ================================================================

    def generate(self) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Execute the deterministic engine pipeline and return (DataFrame, metadata).

        [Subtask 4.1.1, 4.1.2, 4.1.3, 4.1.4, 4.1.5, 4.5.1, 5.1.1, 5.1.2,
         5.1.5, 5.1.7, 4.3.1, 4.3.2, 4.4.1, 4.4.2]

        Pipeline composition per §2.8:
          M = τ_post ∘ δ? ∘ γ ∘ β ∘ α(seed)

        Sprint 5 implements α (skeleton), τ_post (DataFrame assembly), and
        metadata emission. Sprint 6 adds γ (pattern injection on post-measure
        DataFrame) and δ (realism injection — missing/dirty values). Phase β
        (measures) remains blocked (Blockers 2 & 3).

        Given the same seed, output is bit-for-bit reproducible (§2.8).

        Returns:
            Tuple of (df, schema_metadata) where df is a pd.DataFrame with
            target_rows rows containing all non-measure skeleton columns,
            and schema_metadata is the §2.6 dict with all SPEC_READY fields.

        Raises:
            CyclicDependencyError: If DAG construction detects a cycle.
        """
        # ===== Phase 1: Initialize deterministic RNG =====

        # Seed the NumPy Generator for bit-for-bit reproducibility (§2.8)
        rng = np.random.default_rng(self.seed)

        # ===== Phase 2: Build and sort the full generation DAG =====

        # Construct the DAG from all registered declarations (Sprint 4)
        full_dag = self._build_full_dag()

        # Compute deterministic topological order with lexicographic tie-breaking
        topo_order = self._topological_sort(full_dag)

        # ===== Phase α: Skeleton builder — non-measure columns =====

        # Generate all categorical roots, dependent roots, child categories,
        # temporal roots, and derived temporal columns in topological order
        rows = self._build_skeleton(topo_order, rng)

        # ===== Phase β: Measure generation (BLOCKED — Blockers 2 & 3) =====

        # Measure columns require formula DSL (Blocker 2) and distribution
        # parameter specs (Blocker 3). Skeleton-only for this sprint.
        # TODO [4.2.1–4.2.7]: Implement when blockers resolve.

        # ===== Post-processing: assemble DataFrame =====

        # FIX: [self-review item 1] — Added SPEC_AMBIGUOUS comment documenting
        # intentional deviation from §2.8 pipeline ordering.
        # SPEC_AMBIGUOUS: §2.8 pseudocode applies γ and δ to the `rows` dict
        # (numpy arrays) and calls _post_process(rows) last. This implementation
        # moves _post_process before γ/δ so that injection methods can use
        # DataFrame operations (df.eval for target expressions, pd.to_datetime
        # for break_point comparison). Functional outcome is equivalent — same
        # data, same transformations, same deterministic result. The gap analysis
        # does not flag this; it is a pragmatic implementation choice.
        # Convert column arrays into a typed pandas DataFrame. This must
        # happen before Phase γ/δ because pattern and realism injection
        # operate on the DataFrame, not raw arrays.
        df = self._post_process(rows, topo_order)

        # ===== Phase γ: Pattern injection (Sprint 6) =====

        # Apply declared patterns (outlier entity, trend break) to the
        # post-measure DataFrame. Only operates if _patterns is non-empty.
        if self._patterns:
            df = self._inject_patterns(df, rng)

        # ===== Phase δ: Realism injection (Sprint 6) =====

        # Apply missing-value and dirty-value injection if configured.
        # Only operates if set_realism() was called.
        if self._realism_config is not None:
            df = self._inject_realism(df, rng)

        # ===== Metadata: build §2.6 schema metadata =====

        # Emit all SPEC_READY metadata fields for this sprint
        metadata = self._build_schema_metadata()

        logger.debug(
            "generate: produced DataFrame with shape %s and %d metadata keys.",
            df.shape,
            len(metadata),
        )

        return df, metadata

    # ================================================================
    # Sprint 5: Engine Phase α — Skeleton Builder
    # ================================================================

    def _build_skeleton(
        self,
        topo_order: list[str],
        rng: np.random.Generator,
    ) -> dict[str, np.ndarray]:
        """Phase α: skeleton builder.  Delegates to ``engine_skeleton.build_skeleton``."""
        return _engine.build_skeleton(
            self._columns, self.target_rows, self._group_dependencies,
            topo_order, rng,
        )

    # ================================================================
    # Sprint 5: Engine Phase α — Categorical Samplers
    # ================================================================

    def _sample_independent_root(
        self,
        col_name: str,
        col_meta: dict[str, Any],
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Independent root sampler.  Delegates to ``engine_skeleton``."""
        return _engine.sample_independent_root(
            col_name, col_meta, self.target_rows, rng,
        )

    def _sample_dependent_root(
        self,
        col_name: str,
        col_meta: dict[str, Any],
        dep: GroupDependency,
        rows: dict[str, np.ndarray],
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Dependent root sampler.  Delegates to ``engine_skeleton``."""
        return _engine.sample_dependent_root(
            col_name, col_meta, dep, rows, self.target_rows, rng,
        )

    def _sample_child_category(
        self,
        col_name: str,
        col_meta: dict[str, Any],
        rows: dict[str, np.ndarray],
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Child category sampler.  Delegates to ``engine_skeleton``."""
        return _engine.sample_child_category(
            col_name, col_meta, rows, self.target_rows, rng,
        )

    # ================================================================
    # Sprint 5: Engine Phase α — Temporal Samplers
    # ================================================================

    def _sample_temporal_root(
        self,
        col_name: str,
        col_meta: dict[str, Any],
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Temporal root sampler.  Delegates to ``engine_skeleton``."""
        return _engine.sample_temporal_root(
            col_name, col_meta, self.target_rows, rng,
        )

    @staticmethod
    def _enumerate_daily_dates(start: date, end: date) -> list[date]:
        """Daily date enumerator.  Delegates to ``engine_skeleton``."""
        return _engine.enumerate_daily_dates(start, end)

    @staticmethod
    def _enumerate_period_dates(
        start: date, end: date, snap_weekday: int,
    ) -> list[date]:
        """Period date enumerator.  Delegates to ``engine_skeleton``."""
        return _engine.enumerate_period_dates(start, end, snap_weekday)

    @staticmethod
    def _enumerate_monthly_dates(start: date, end: date) -> list[date]:
        """Monthly date enumerator.  Delegates to ``engine_skeleton``."""
        return _engine.enumerate_monthly_dates(start, end)

    def _derive_temporal_child(
        self,
        col_name: str,
        col_meta: dict[str, Any],
        rows: dict[str, np.ndarray],
    ) -> np.ndarray:
        """Temporal child derivation.  Delegates to ``engine_skeleton``."""
        return _engine.derive_temporal_child(col_name, col_meta, rows)

    # ================================================================
    # Sprint 5: Engine Phase α — Helpers
    # ================================================================

    def _get_dependency_for_root(self, col_name: str) -> GroupDependency | None:
        """Look up a GroupDependency where col_name is the child_root.

        [Subtask 4.1.2 helper]

        Scans _group_dependencies to find if this root column is the dependent
        side of a cross-group dependency. Returns the first match or None if
        the root is independent.

        Args:
            col_name: Root column name to look up.

        Returns:
            The matching GroupDependency, or None if the root is independent.
        """
        # Linear scan is acceptable — the number of group dependencies is
        # small (typically <10 in real scenarios)
        for dep in self._group_dependencies:
            if dep.child_root == col_name:
                return dep

        return None

    # ================================================================
    # Sprint 5: Post-Processing
    # ================================================================

    def _post_process(
        self,
        rows: dict[str, np.ndarray],
        topo_order: list[str],
    ) -> pd.DataFrame:
        """Assemble column arrays into a typed DataFrame.

        [Subtask 4.5.1]

        §2.8: return self._post_process(rows), self._build_schema_metadata()

        Dtype policy (implementation design choice, not spec-prescribed):
          - categorical → object (Python str)
          - temporal → datetime64[ns]
          - temporal_derived (day_of_week, month, quarter) → int64
          - temporal_derived (is_weekend) → bool
          - measure → float64 (when implemented)

        Column ordering follows the topological order, filtered to only
        columns present in the rows dict (measures are excluded in skeleton).

        Args:
            rows: Dict mapping column name → numpy array.
            topo_order: Full topological order for column sequencing.

        Returns:
            pd.DataFrame with target_rows rows.
        """
        # ===== Phase 1: Determine column order =====

        # Use topological order but only include columns that were actually
        # generated (measures are skipped in skeleton mode)
        ordered_cols = [col for col in topo_order if col in rows]

        # ===== Phase 2: Build DataFrame from ordered column dict =====

        # Construct an OrderedDict to preserve column ordering in the DataFrame
        data: dict[str, np.ndarray] = {col: rows[col] for col in ordered_cols}

        # FIX: [self-review item 2] — pd.DataFrame({}) produces shape (0,0).
        # Contract requires (target_rows, 0) when no columns are generated.
        # Explicit index ensures correct row count even with zero columns.
        df = pd.DataFrame(data, index=range(self.target_rows))

        # ===== Phase 3: Apply dtype casting per column type =====

        for col_name in ordered_cols:
            # FIX: [self-review item 5] — Added missing comment for loop body.
            # Look up column type to determine appropriate dtype cast
            col_meta = self._columns.get(col_name)
            if col_meta is None:
                continue

            col_type = col_meta.get("type")

            if col_type == "categorical":
                # Ensure categorical columns are string-typed objects
                df[col_name] = df[col_name].astype(object)

            elif col_type == "temporal":
                # Temporal root columns should be datetime64[ns]
                df[col_name] = pd.to_datetime(df[col_name])

            elif col_type == "temporal_derived":
                derivation = col_meta.get("derivation")
                if derivation == "is_weekend":
                    # Boolean dtype for weekend indicator
                    df[col_name] = df[col_name].astype(bool)
                else:
                    # Integer dtype for day_of_week, month, quarter
                    df[col_name] = df[col_name].astype(np.int64)

            # SPEC_AMBIGUOUS: measure dtype handling deferred — measures are
            # not generated in skeleton mode. Will be float64 when implemented.

        logger.debug(
            "_post_process: DataFrame shape=%s, columns=%s.",
            df.shape,
            list(df.columns),
        )

        return df

    # ================================================================
    # Sprint 5: Schema Metadata Builder
    # ================================================================

    def _build_schema_metadata(self) -> dict[str, Any]:
        """Schema metadata builder.  Delegates to ``metadata.build_schema_metadata``."""
        if any(
            col_meta.get("type") == "measure"
            for col_meta in self._columns.values()
        ):
            full_dag = self._build_full_dag()
            _, measure_order = self._extract_measure_sub_dag(full_dag)
        else:
            measure_order = []

        return _meta.build_schema_metadata(
            self._groups, self._orthogonal_pairs,
            self.target_rows, list(measure_order),
        )

    # ================================================================
    # Sprint 6: Phase γ — Pattern Injection
    # ================================================================

    def _inject_patterns(
        self,
        df: pd.DataFrame,
        rng: np.random.Generator,
    ) -> pd.DataFrame:
        """Phase γ: pattern injection.  Delegates to ``pattern_engine``."""
        return _pattern.inject_patterns(df, self._patterns, self._columns, rng)

    def _inject_outlier_entity(
        self,
        df: pd.DataFrame,
        pattern: dict[str, Any],
    ) -> pd.DataFrame:
        """Outlier entity injector.  Delegates to ``pattern_engine``."""
        return _pattern.inject_outlier_entity(df, pattern)

    def _inject_trend_break(
        self,
        df: pd.DataFrame,
        pattern: dict[str, Any],
    ) -> pd.DataFrame:
        """Trend break injector.  Delegates to ``pattern_engine``."""
        return _pattern.inject_trend_break(df, pattern, self._columns)

    # ================================================================
    # Sprint 6: Phase δ — Realism Injection
    # ================================================================

    def _inject_realism(
        self,
        df: pd.DataFrame,
        rng: np.random.Generator,
    ) -> pd.DataFrame:
        """Phase δ: realism injection.  Delegates to ``realism_engine``."""
        if self._realism_config is None:
            return df
        return _realism.inject_realism(
            df, self._realism_config, self._columns, rng,
        )

    def _inject_missing_values(
        self,
        df: pd.DataFrame,
        missing_rate: float,
        rng: np.random.Generator,
    ) -> pd.DataFrame:
        """Missing value injector.  Delegates to ``realism_engine``."""
        return _realism.inject_missing_values(df, missing_rate, rng)

    def _inject_dirty_values(
        self,
        df: pd.DataFrame,
        dirty_rate: float,
        rng: np.random.Generator,
    ) -> pd.DataFrame:
        """Dirty value injector.  Delegates to ``realism_engine``."""
        return _realism.inject_dirty_values(
            df, self._columns, dirty_rate, rng,
        )

    @staticmethod
    def _perturb_string(value: str, rng: np.random.Generator) -> str:
        """String perturbation.  Delegates to ``realism_engine``."""
        return _realism.perturb_string(value, rng)

