"""
Sprint 6 — Three-layer validator framework and L1 structural checks.
Sprint 7 — L3 pattern validation checks (outlier entity, trend break),
           L2 helper (_max_conditional_deviation), auto-fix strategy
           dispatch (match_strategy), and three auto-fix isolated stubs
           (widen_variance, amplify_magnitude, reshuffle_pair).

Sprint 6 Subtask IDs: 8.1.1, 8.1.2, 8.2.1, 8.2.2, 8.2.5, 8.2.6
Sprint 7 Subtask IDs: 8.4.1, 8.4.3, 8.3.7, 9.1.1, 9.2.1, 9.2.2, 9.2.3
  Note on numbering: The sprint plan uses pre-merge IDs. The post-audit
  task hierarchy renumbered 8.3.7 to 8.3.6 (after the 8.3.3/8.3.4 merge).
  This module uses SPRINT PLAN numbering throughout for traceability.

This module defines the validator data classes (Check, ValidationReport) and
the individual L1 structural validation functions from §2.9.  Each function
takes (df, meta) or (meta,) and returns Check object(s).  Functions are
standalone — they do NOT import FactTableSimulator or any agpds modules
except agpds.exceptions, avoiding circular dependencies.  The deferred 8.1.3
orchestrator (validate(df, meta)) is NOT implemented here; it depends on
unresolved B2/C6 blockers.

Sprint 7 adds:
  - L3 pattern checks as module-level functions (same pattern as L1).
  - max_conditional_deviation() as a pure-math helper for future L2 use.
  - match_strategy() for glob-based auto-fix dispatch.
  - widen_variance(), amplify_magnitude(), reshuffle_pair() as isolated
    stubs. These are pure input→output transformations with no simulator
    mutation — integration is deferred to Sprint 13 (Blocker 5 resolution).

Design choice: L1/L3 checks and auto-fix stubs are module-level functions,
not methods on a class, because the SchemaAwareValidator class will compose
them in the orchestrator (deferred).  This keeps each check independently
testable.
"""
from __future__ import annotations

import copy
import fnmatch
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd
import scipy.stats

from agpds.exceptions import InvalidParameterError, PatternInjectionError

logger = logging.getLogger(__name__)


# =====================================================================
# Validator Data Classes
# =====================================================================

@dataclass
class Check:
    """A single validation check result.

    [Subtask 8.1.1]

    §2.9 L1 code: Check(name, passed=...).  The detail field carries
    human-readable context (e.g. "χ² p=0.34") for debugging and for
    the auto-fix loop to inspect failure reasons.

    Attributes:
        name: Check identifier (e.g. "row_count", "cardinality_hospital").
        passed: Whether this check passed.
        detail: Optional human-readable detail string.
    """

    name: str
    passed: bool
    detail: Optional[str] = None


@dataclass
class ValidationReport:
    """Aggregates Check results from one or more validation layers.

    [Subtask 8.1.2]

    §2.9 auto-fix loop uses report.all_passed and report.failures to
    decide whether to retry.  The checks list accumulates results from
    L1, L2, and L3 sequentially via add_checks().

    Attributes:
        checks: All Check objects from the validation run.
    """

    checks: list[Check] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        """True iff every check in the report passed.

        [Subtask 8.1.2]

        An empty report (no checks) is considered all-passed —
        vacuously true, consistent with "no failures found".
        """
        # All-passed is vacuously true when no checks exist, and is
        # the logical AND of all check.passed values otherwise
        return all(check.passed for check in self.checks)

    @property
    def failures(self) -> list[Check]:
        """List of Check objects where passed is False.

        [Subtask 8.1.2]

        Returns a new list each call — callers cannot corrupt internal
        state by mutating the returned list.
        """
        # Filter to only failing checks for the auto-fix loop to inspect
        return [check for check in self.checks if not check.passed]

    def add_checks(self, new_checks: list[Check]) -> None:
        """Append a batch of checks to this report.

        [Subtask 8.1.2]

        Used by the orchestrator (deferred 8.1.3) to accumulate results
        from L1, L2, L3 sequentially.

        Args:
            new_checks: List of Check objects to add.
        """
        # Extend rather than replace — reports accumulate across layers
        self.checks.extend(new_checks)


# =====================================================================
# L1 Structural Check: Row Count
# =====================================================================

def check_row_count(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> Check:
    """L1: Row count within 10% of target.

    [Subtask 8.2.1]

    §2.9 L1: abs(len(df) - target) / target < 0.1

    The 10% threshold uses strict less-than per the spec pseudocode,
    meaning exactly 10% deviation fails.

    Args:
        df: Generated DataFrame.
        meta: Schema metadata with "total_rows" key.

    Returns:
        Check named "row_count".

    Raises:
        KeyError: If meta is missing "total_rows".
    """
    # Extract the declared target row count from metadata
    target = meta["total_rows"]

    # Compute the fractional deviation from target
    actual = len(df)
    deviation = abs(actual - target) / target

    # §2.9: strict less-than comparison — exactly 10% fails.
    # Explicit bool() for numpy-safe conversion.
    passed = bool(deviation < 0.1)

    # Include actual/target in detail for debugging
    detail = (
        f"actual={actual}, target={target}, "
        f"deviation={deviation:.4f} ({'<' if passed else '>='} 0.1)"
    )

    logger.debug("check_row_count: %s", detail)

    return Check(name="row_count", passed=passed, detail=detail)


# =====================================================================
# L1 Structural Check: Categorical Cardinality
# =====================================================================

def check_categorical_cardinality(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> list[Check]:
    """L1: Each categorical column's unique count matches declared cardinality.

    [Subtask 8.2.2]

    §2.9 L1: actual == col["cardinality"]

    Iterates over meta["columns"], filters to type=="categorical", and
    compares nunique() against declared cardinality.

    SPEC_AMBIGUOUS: The spec references meta["columns"] with a
    "cardinality" field, but Sprint 5 does not emit the "columns"
    metadata block (it is SPEC_INCORRECT per C3/C8/C9).  This function
    accepts meta["columns"] when present and falls back to extracting
    cardinality from the column's "values" list length.  When the
    "columns" block is unavailable, this function returns an empty list.

    Args:
        df: Generated DataFrame.
        meta: Schema metadata.  If meta["columns"] exists, uses it.

    Returns:
        List of Checks, one per categorical column.  Empty if no
        categorical columns or no "columns" metadata key.

    Raises:
        KeyError: If a declared column name is not in the DataFrame.
    """
    checks: list[Check] = []

    # Retrieve the columns metadata block; return empty if absent
    columns_meta = meta.get("columns")
    if columns_meta is None:
        logger.debug(
            "check_categorical_cardinality: no 'columns' key in meta, "
            "skipping cardinality checks."
        )
        return checks

    # Iterate over declared columns, checking only categoricals
    for col in columns_meta:
        if col.get("type") != "categorical":
            continue

        col_name = col["name"]

        # Determine declared cardinality — prefer explicit field, fall
        # back to len(values) if "cardinality" key is absent
        declared = col.get("cardinality")
        if declared is None:
            values = col.get("values")
            if values is not None:
                declared = len(values)
            else:
                # Cannot determine cardinality without either field
                logger.warning(
                    "check_categorical_cardinality: column '%s' has no "
                    "'cardinality' or 'values' field, skipping.",
                    col_name,
                )
                continue

        # Count actual unique values in the DataFrame column
        actual = df[col_name].nunique()

        # Compare actual vs declared cardinality. Explicit bool() to
        # prevent numpy integer comparison returning numpy bool.
        passed = bool(actual == declared)
        detail = f"actual={actual}, declared={declared}"

        checks.append(Check(
            name=f"cardinality_{col_name}",
            passed=passed,
            detail=detail,
        ))

        logger.debug(
            "check_categorical_cardinality: '%s' %s",
            col_name,
            detail,
        )

    return checks


# =====================================================================
# L1 Structural Check: Orthogonal Independence (Chi-Squared)
# =====================================================================

def check_orthogonal_independence(
    df: pd.DataFrame,
    meta: dict[str, Any],
) -> list[Check]:
    """L1: Chi-squared independence test on root pairs of orthogonal groups.

    [Subtask 8.2.5]

    §2.9 L1: chi2_contingency on root cross-group pairs, p_val > 0.05.

    For each declared orthogonal pair, extracts the root column of each
    group (hierarchy[0]), builds a contingency table, and runs
    scipy.stats.chi2_contingency.  p > 0.05 means "cannot reject
    independence" → passes.

    Args:
        df: Generated DataFrame.
        meta: Schema metadata with "orthogonal_groups" (list of
              {group_a, group_b, rationale}) and "dimension_groups"
              (dict of group_name → {columns, hierarchy}).

    Returns:
        List of Checks, one per orthogonal pair.  Empty if no pairs.

    Raises:
        KeyError: If a required metadata key or group is missing.
    """
    checks: list[Check] = []

    # Retrieve orthogonal pair declarations; return empty if absent
    orthogonal_groups = meta.get("orthogonal_groups")
    if not orthogonal_groups:
        return checks

    # Retrieve dimension group definitions for root column lookup
    dimension_groups = meta["dimension_groups"]

    for pair in orthogonal_groups:
        # Extract group names from each orthogonal pair declaration
        group_a_name = pair["group_a"]
        group_b_name = pair["group_b"]

        # Look up each group's root column — hierarchy[0] is the root
        # per §2.2 DimensionGroup root-first ordering.  For the "time"
        # group, hierarchy contains *only* the root (derive columns are
        # in ``columns`` but excluded from ``hierarchy``; see §2.6).
        ga = dimension_groups[group_a_name]
        gb = dimension_groups[group_b_name]
        root_a = ga["hierarchy"][0]
        root_b = gb["hierarchy"][0]

        # Build the contingency table from actual data
        ct = pd.crosstab(df[root_a], df[root_b])

        # Guard against degenerate tables: chi2_contingency requires
        # at least 2 rows and 2 columns in the crosstab
        if ct.shape[0] < 2 or ct.shape[1] < 2:
            checks.append(Check(
                name=f"orthogonal_{root_a}_{root_b}",
                passed=False,
                detail=(
                    f"Degenerate contingency table shape={ct.shape}; "
                    f"chi-squared requires at least 2×2."
                ),
            ))
            continue

        # Run the chi-squared test of independence
        try:
            _, p_val, _, _ = scipy.stats.chi2_contingency(ct)
        except ValueError as exc:
            # scipy raises ValueError for truly degenerate inputs
            # (e.g., all-zero row/column)
            checks.append(Check(
                name=f"orthogonal_{root_a}_{root_b}",
                passed=False,
                detail=f"chi2_contingency raised: {exc}",
            ))
            continue

        # p > 0.05 means we cannot reject independence → passes.
        # Explicit bool() conversion because scipy returns numpy booleans
        # which fail Python `is True` identity checks.
        passed = bool(p_val > 0.05)
        detail = f"χ² p={p_val:.4f} (>0.05 = independent)"

        checks.append(Check(
            name=f"orthogonal_{root_a}_{root_b}",
            passed=passed,
            detail=detail,
        ))

        logger.debug(
            "check_orthogonal_independence: %s vs %s → p=%.4f, passed=%s",
            root_a,
            root_b,
            p_val,
            passed,
        )

    return checks


# =====================================================================
# L1 Structural Check: Measure DAG Acyclicity
# =====================================================================

def check_measure_dag_acyclic(
    meta: dict[str, Any],
) -> Check:
    """L1: Verify measure_dag_order is acyclic (defense-in-depth).

    [Subtask 8.2.6]

    §2.9 L1: is_acyclic(meta.get("measure_dag_order", []))

    A valid topological ordering has all elements unique — repeated
    node names indicate corruption in the ordering process.  An empty
    list is trivially acyclic.  This is defense-in-depth; the DAG was
    already validated at declaration time (subtask 1.5.5).

    Args:
        meta: Schema metadata with optional "measure_dag_order" key.

    Returns:
        Check named "measure_dag_acyclic".
    """
    # Retrieve the measure DAG order, defaulting to empty if absent
    dag_order = meta.get("measure_dag_order", [])

    # A topological order is valid (acyclic) iff no duplicates exist —
    # duplicates would mean a node appears multiple times, which is
    # structurally impossible in a well-formed DAG ordering
    unique_count = len(set(dag_order))
    total_count = len(dag_order)
    passed = unique_count == total_count

    # Build detail string for debugging
    if passed:
        detail = f"{total_count} measures, all unique — acyclic."
    else:
        # Identify which nodes are duplicated for the detail message
        seen: set[str] = set()
        duplicates: list[str] = []
        for name in dag_order:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        detail = f"Duplicate nodes in dag_order: {duplicates}"

    logger.debug("check_measure_dag_acyclic: %s", detail)

    return Check(
        name="measure_dag_acyclic",
        passed=passed,
        detail=detail,
    )


# =====================================================================
# L3 Pattern Validation Check: Outlier Entity Z-Score
# =====================================================================

def check_outlier_entity(
    df: pd.DataFrame,
    pattern: dict[str, Any],
) -> Check:
    """L3: Outlier entity z-score check — target subset z >= 2.0.

    [Subtask 8.4.1]

    §2.9 L3: z >= 2.0.

    Computes the z-score of the target subset's mean relative to the
    global distribution: z = |subset_mean - global_mean| / global_std.
    Passes when z >= 2.0.

    The 2.0 threshold uses >= (not strict >) per the spec pseudocode
    `z >= 2.0`, meaning exactly 2.0 passes.

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with keys "target" (str), "col" (str),
                 "params" (dict containing "z_score": float).

    Returns:
        Check named "outlier_{col}" with passed=(z >= 2.0).

    Raises:
        KeyError: If pattern keys ("target", "col", "params", "z_score")
                  or df column are missing.
    """
    # ===== Phase 1: Extract pattern parameters =====

    # Pull the three required fields — KeyError propagates on missing keys
    target_expr = pattern["target"]
    col = pattern["col"]
    # Access z_score to validate pattern structure (not used in the
    # check itself, but confirms the pattern spec is well-formed)
    _ = pattern["params"]["z_score"]

    # ===== Phase 2: Evaluate target expression to get subset mask =====

    # Use df.eval() to evaluate the boolean target expression
    target_mask = df.eval(target_expr)
    target_idx = df.index[target_mask]

    # Zero-match target is a failed check, not an exception — the
    # injection may have been misconfigured but the validator should
    # still report the failure cleanly for the auto-fix loop
    if len(target_idx) == 0:
        return Check(
            name=f"outlier_{col}",
            passed=False,
            detail=(
                f"Target '{target_expr}' matched zero rows; "
                f"cannot compute z-score on empty subset."
            ),
        )

    # ===== Phase 3: Compute global statistics =====

    # FIX: [self-review item 1] — Use pandas default ddof=1 (sample std)
    # to match the spec §2.9 L3 pseudocode line 652: ``df[p["col"]].std()``
    # which uses the pandas default ddof=1.  The prior implementation used
    # ddof=0 (population std), which was conceptually defensible but
    # diverged from the spec's literal code.
    global_mean = float(df[col].mean())
    global_std = float(df[col].std())

    # Zero-std columns produce undefined z-scores — report as failure
    # rather than raising, because the auto-fix loop needs a Check
    if global_std == 0.0 or np.isnan(global_std):
        return Check(
            name=f"outlier_{col}",
            passed=False,
            detail=(
                f"Global std of '{col}' is {global_std}; "
                f"z-score is undefined for zero-variance columns."
            ),
        )

    # ===== Phase 4: Compute target subset z-score and compare =====

    # The z-score measures how far the target subset's mean deviates
    # from the global mean, in units of global standard deviation
    subset_mean = float(df.loc[target_idx, col].mean())
    z = abs(subset_mean - global_mean) / global_std

    # §2.9 L3: z >= 2.0 (non-strict, exactly 2.0 passes)
    passed = bool(z >= 2.0)

    # FIX: [self-review item 6a] — Added comment for detail string block
    # Build detail string with z-score and distribution statistics
    detail = (
        f"z={z:.4f} (subset_mean={subset_mean:.4f}, "
        f"global_mean={global_mean:.4f}, global_std={global_std:.4f})"
    )

    logger.debug("check_outlier_entity: col='%s', %s, passed=%s", col, detail, passed)

    return Check(name=f"outlier_{col}", passed=passed, detail=detail)


# =====================================================================
# L3 Pattern Validation Check: Trend Break Magnitude
# =====================================================================

def _find_temporal_column(meta: dict[str, Any]) -> Optional[str]:
    """Locate the temporal group's root column name from metadata.

    [Subtask 8.4.3 — private helper]

    The spec §2.9 L3 pseudocode finds the temporal column via
    ``[c["name"] for c in meta["columns"] if c["type"] == "temporal"][0]``.
    However, meta["columns"] is SPEC_INCORRECT (C3/C8/C9) and not
    emitted by Sprint 5.  This helper uses the more robust
    ``dimension_groups["time"]`` lookup instead.

    Args:
        meta: Schema metadata with "dimension_groups".

    Returns:
        Root column name of the temporal group, or None if no temporal
        group exists.
    """
    # Search dimension_groups for the reserved "time" group name
    dimension_groups = meta.get("dimension_groups", {})
    time_group = dimension_groups.get("time")

    if time_group is None:
        return None

    hierarchy = time_group.get("hierarchy", [])
    if not hierarchy:
        return None

    # hierarchy[0] is the temporal root per §2.2.  For the "time" group,
    # hierarchy is always [root] — derive columns are members of
    # ``columns`` only, not ``hierarchy`` (§2.6).
    return hierarchy[0]


def check_trend_break(
    df: pd.DataFrame,
    pattern: dict[str, Any],
    meta: dict[str, Any],
) -> Check:
    """L3: Trend break magnitude check — |after - before| / before > 0.15.

    [Subtask 8.4.3]

    §2.9 L3: abs(after - before) / before > 0.15.

    FIX: [self-review item 2] — Removed target filtering.  The spec §2.9
    L3 pseudocode (lines 667–668) operates on the full DataFrame:
    ``before = df[df[tc] < bp][p["col"]].mean()``.  The ``target`` field
    is used by Phase γ injection (subtask 4.3.2), not by the L3 check.

    Splits the full DataFrame at break_point along the temporal column,
    computes the mean of col in both halves, and checks if the relative
    change exceeds 15%.

    The 15% threshold uses strict greater-than per the spec pseudocode,
    meaning exactly 15% fails.

    Args:
        df: Generated DataFrame.
        pattern: Pattern spec dict with "col" (str), and either
                 "break_point" (§2.6 metadata format) or
                 "params" → "break_point" (SDK-internal format).
        meta: Schema metadata (used to find the temporal column via
              dimension_groups).

    Returns:
        Check named "trend_{col}" with passed=(ratio > 0.15).

    Raises:
        KeyError: If pattern keys or df columns are missing.
        PatternInjectionError: If no temporal column exists in metadata.
    """
    # ===== Phase 1: Extract pattern parameters =====

    col = pattern["col"]

    # FIX: [self-review item 3] — Support both §2.6 metadata format
    # (p["break_point"] at top level, per spec L3 line 664) and
    # SDK-internal format (p["params"]["break_point"]).
    break_point_raw = pattern.get("break_point")
    if break_point_raw is None:
        break_point_raw = pattern["params"]["break_point"]

    # ===== Phase 2: Locate temporal column =====

    # The temporal column is needed to split before/after the break_point
    temporal_col = _find_temporal_column(meta)

    # FIX: [self-review item 6b] — Added comment for temporal_col guard
    # Reject missing temporal group — trend break requires time dimension
    if temporal_col is None:
        raise PatternInjectionError(
            pattern_type="trend_break",
            detail=(
                "No temporal column found in metadata. "
                "Trend break validation requires a 'time' dimension group."
            ),
        )

    # Verify temporal column exists in the DataFrame
    if temporal_col not in df.columns:
        raise PatternInjectionError(
            pattern_type="trend_break",
            detail=(
                f"Temporal column '{temporal_col}' from metadata is not "
                f"present in the DataFrame."
            ),
        )

    # ===== Phase 3: Split full DataFrame before/after break_point =====
    # FIX: [self-review item 2] — Operates on full df per spec §2.9 L3

    # Convert temporal column to datetime if it isn't already, so that
    # comparison with the parsed break_point works correctly
    temporal_values = pd.to_datetime(df[temporal_col], errors="coerce")
    break_point_dt = pd.to_datetime(break_point_raw)

    # Split into before (< break_point) and after (>= break_point)
    before_mask = temporal_values < break_point_dt
    after_mask = temporal_values >= break_point_dt

    # FIX: [self-review item 2] — Use df directly, not a target subset
    before_values = df.loc[before_mask, col]
    after_values = df.loc[after_mask, col]

    # ===== Phase 4: Handle degenerate splits =====

    # If either half is empty, the trend break cannot be evaluated —
    # report as a failed check (not an exception) so the auto-fix
    # loop can process it
    if len(before_values) == 0 or len(after_values) == 0:
        return Check(
            name=f"trend_{col}",
            passed=False,
            detail=(
                f"Degenerate split at break_point={break_point_raw}: "
                f"before={len(before_values)} rows, "
                f"after={len(after_values)} rows. "
                f"Both halves must be non-empty."
            ),
        )

    # ===== Phase 5: Compute means and relative change =====

    before_mean = float(before_values.mean())
    after_mean = float(after_values.mean())

    # Guard against division by zero when before_mean is exactly 0
    if before_mean == 0.0:
        return Check(
            name=f"trend_{col}",
            passed=False,
            detail=(
                f"Before-period mean is 0.0; relative change is undefined. "
                f"after_mean={after_mean:.4f}."
            ),
        )

    # FIX: [self-review item 4] — The spec §2.9 L3 line 670 uses
    # ``abs(after - before) / before`` with signed denominator.  For
    # positive means (typical for measures like wait_minutes) the result
    # is identical to abs/abs.  For negative before-means the spec
    # produces a negative ratio that always fails >0.15.  We use
    # abs(before_mean) for robustness with negative means.
    # SPEC_AMBIGUOUS: The spec uses ``before`` directly in the denominator
    # (line 670).  For negative before-means, the unsigned numerator /
    # signed denominator produces a negative ratio that always fails.
    # We use abs(before_mean) as a robustness measure.  No gap analysis
    # finding covers this specific edge case — this is a net-new discovery.
    ratio = abs(after_mean - before_mean) / abs(before_mean)

    # §2.9 L3: strict > 0.15 — exactly 15% fails
    passed = bool(ratio > 0.15)

    # FIX: [self-review item 6c] — Added comment for detail string block
    # Build detail string with before/after means and computed ratio
    detail = (
        f"before_mean={before_mean:.4f}, after_mean={after_mean:.4f}, "
        f"ratio={ratio:.4f} ({'>' if passed else '<='} 0.15), "
        f"break_point={break_point_raw}, "
        f"n_before={len(before_values)}, n_after={len(after_values)}"
    )

    logger.debug("check_trend_break: col='%s', %s, passed=%s", col, detail, passed)

    return Check(name=f"trend_{col}", passed=passed, detail=detail)


# =====================================================================
# L2 Helper: Maximum Conditional Deviation
# =====================================================================

def max_conditional_deviation(
    observed: dict[str, dict[str, float]],
    declared: dict[str, dict[str, float]],
) -> float:
    """Compute the max absolute deviation between observed and declared
    conditional weight distributions.

    [Subtask 8.3.7 (sprint plan) / 8.3.6 (post-audit hierarchy)]

    §2.9 L2 code: self._max_conditional_deviation(observed, declared).

    Iterates over all (parent_value, child_value) cells present in either
    the observed or declared distribution and finds the maximum absolute
    difference. Missing cells in either dict are treated as 0.0 — a
    parent value present in observed but absent in declared contributes
    its full weight as deviation, and vice versa.

    Note: the spec's L2 caller passes a pd.crosstab (DataFrame) as the
    observed argument.  The future L2 integration (subtask 8.3.5) must
    convert the DataFrame to a nested dict before calling this helper.

    Args:
        observed: Normalized conditional distribution.
            Outer keys = parent values, inner keys = child values,
            inner values = observed proportions (should sum to ~1.0
            per parent key).
        declared: Declared conditional weights (same structure).

    Returns:
        Maximum absolute deviation across all cells. Returns 0.0
        when both dicts are empty.
    """
    max_dev: float = 0.0

    # Collect the union of all parent keys from both distributions
    # so we catch parent values present in one but missing in the other
    all_parent_keys = set(observed.keys()) | set(declared.keys())

    for parent_key in all_parent_keys:
        # Retrieve inner dicts, defaulting to empty if the parent key
        # is absent in one distribution
        obs_inner = observed.get(parent_key, {})
        decl_inner = declared.get(parent_key, {})

        # Collect the union of child keys within this parent so we
        # detect children present in one but missing in the other
        all_child_keys = set(obs_inner.keys()) | set(decl_inner.keys())

        for child_key in all_child_keys:
            # Missing child key → treat as 0.0 weight
            obs_val = obs_inner.get(child_key, 0.0)
            decl_val = decl_inner.get(child_key, 0.0)

            # Track the maximum absolute deviation across all cells
            dev = abs(obs_val - decl_val)
            if dev > max_dev:
                max_dev = dev

    logger.debug(
        "max_conditional_deviation: max_dev=%.6f across %d parent keys.",
        max_dev,
        len(all_parent_keys),
    )

    return max_dev


# =====================================================================
# Auto-Fix Strategy Dispatch: Glob-Based Matcher
# =====================================================================

def match_strategy(
    check_name: str,
    auto_fix: dict[str, Any],
) -> Optional[Any]:
    """Glob-based matcher: find the first AUTO_FIX key that matches
    the check name.

    [Subtask 9.1.1]

    §2.9 auto-fix code: match_strategy(check.name, AUTO_FIX).

    Uses fnmatch semantics: "ks_*" matches "ks_wait_minutes_marginal".
    Returns the first matching strategy callable.  Iteration order
    follows dict insertion order (Python 3.7+ guaranteed), so the first
    glob pattern that matches wins when multiple patterns could match
    the same check name.

    Args:
        check_name: The Check.name string (e.g. "ks_wait_minutes_marginal").
        auto_fix: Dict mapping glob patterns to strategy callables.
                  E.g. {"ks_*": widen_variance, "outlier_*": amplify_magnitude}.

    Returns:
        The matched strategy callable, or None if no pattern matches.
    """
    # Iterate over AUTO_FIX patterns in insertion order, returning the
    # first match. This is a linear scan; the AUTO_FIX dict has ~4
    # entries per §2.9, so O(n) is negligible.
    for glob_pattern, strategy_fn in auto_fix.items():
        if fnmatch.fnmatch(check_name, glob_pattern):
            logger.debug(
                "match_strategy: '%s' matched pattern '%s'.",
                check_name,
                glob_pattern,
            )
            return strategy_fn

    # No pattern matched — the auto-fix loop will skip this check
    logger.debug(
        "match_strategy: '%s' matched no pattern in AUTO_FIX.",
        check_name,
    )
    return None


# =====================================================================
# Auto-Fix Strategy Stub: widen_variance
# =====================================================================

def widen_variance(
    check: Check,
    params: dict[str, float],
    factor: float = 1.2,
) -> dict[str, float]:
    """Isolated stub: widen sigma/scale by factor.

    [Subtask 9.2.1]

    §2.9: "ks_*": lambda c: widen_variance(c, factor=1.2)

    B2/B3 DEPENDENCY: This is an isolated stub. It produces a new params
    dict with the variance-controlling parameter multiplied by factor.
    Integration with the simulator instance and retry loop is deferred
    to Sprint 13 (Blocker 5 resolution).

    The function preferentially targets "sigma" (gaussian/lognormal);
    if absent, it falls back to "scale" (gamma/exponential/uniform).
    If neither key exists, raises InvalidParameterError so the
    auto-fix loop can report the failure.

    Args:
        check: The failing Check object (for context/logging; the
               check.name encodes the measure name).
        params: Current distribution parameter dict
                (e.g. {"mu": 5.0, "sigma": 0.35}).
        factor: Multiplicative factor for sigma/scale (default 1.2).

    Returns:
        New params dict with sigma (or scale) multiplied by factor.
        The original dict is NOT mutated.

    Raises:
        InvalidParameterError: If neither "sigma" nor "scale" key
            exists in params.
    """
    # ===== Phase 1: Identify the variance-controlling parameter =====

    # Prefer "sigma" (covers gaussian and lognormal families), then
    # fall back to "scale" (covers gamma, exponential, uniform)
    if "sigma" in params:
        target_key = "sigma"
    elif "scale" in params:
        target_key = "scale"
    else:
        raise InvalidParameterError(
            param_name="sigma|scale",
            value=0.0,
            reason=(
                f"params dict has neither 'sigma' nor 'scale' key. "
                f"Cannot widen variance. Available keys: "
                f"{sorted(params.keys())}"
            ),
        )

    # ===== Phase 2: Build new params with widened parameter =====

    # Shallow-copy to avoid mutating the caller's dict — the stub is a
    # pure transformation that returns a new dict
    new_params = dict(params)
    old_value = new_params[target_key]
    new_params[target_key] = old_value * factor

    logger.debug(
        "widen_variance: check='%s', %s: %.6f → %.6f (factor=%.2f).",
        check.name,
        target_key,
        old_value,
        new_params[target_key],
        factor,
    )

    return new_params


# =====================================================================
# Auto-Fix Strategy Stub: amplify_magnitude
# =====================================================================

def amplify_magnitude(
    check: Check,
    pattern_spec: dict[str, Any],
    factor: float = 1.3,
) -> dict[str, Any]:
    """Isolated stub: amplify pattern z_score or magnitude by factor.

    [Subtask 9.2.2]

    §2.9: "outlier_*" and "trend_*" both map to amplify_magnitude.

    B2/B3 DEPENDENCY: Isolated stub; integration deferred to Sprint 13.

    Targets "z_score" (outlier_entity patterns) preferentially; if
    absent, targets "magnitude" (trend_break patterns).  If neither
    key exists in params, raises InvalidParameterError.

    The returned dict is a deep copy — the original pattern_spec is
    NOT mutated, preserving all non-target keys (e.g. break_point,
    target, col).

    Args:
        check: The failing Check object.
        pattern_spec: Pattern spec dict with "params" sub-dict
                      (e.g. {"type": "outlier_entity", "target": "...",
                       "col": "...", "params": {"z_score": 3.0}}).
        factor: Multiplicative factor (default 1.3).

    Returns:
        New pattern_spec dict with params.z_score or params.magnitude
        multiplied by factor. All other keys are preserved.
        The original dict is NOT mutated.

    Raises:
        InvalidParameterError: If params has neither "z_score" nor
            "magnitude" key.
    """
    # ===== Phase 1: Validate params sub-dict exists =====

    # Access the nested params dict — KeyError propagates if missing
    inner_params = pattern_spec.get("params", {})

    # Identify which magnitude key to amplify: prefer z_score (outlier),
    # then fall back to magnitude (trend_break)
    if "z_score" in inner_params:
        target_key = "z_score"
    elif "magnitude" in inner_params:
        target_key = "magnitude"
    else:
        raise InvalidParameterError(
            param_name="z_score|magnitude",
            value=0.0,
            reason=(
                f"pattern_spec['params'] has neither 'z_score' nor "
                f"'magnitude' key. Cannot amplify. Available keys: "
                f"{sorted(inner_params.keys())}"
            ),
        )

    # ===== Phase 2: Build new pattern_spec with amplified parameter =====

    # Deep-copy the entire pattern_spec so the caller's original is
    # preserved — critical for stub isolation (no simulator mutation)
    new_spec = copy.deepcopy(pattern_spec)
    old_value = new_spec["params"][target_key]
    new_spec["params"][target_key] = old_value * factor

    logger.debug(
        "amplify_magnitude: check='%s', %s: %.6f → %.6f (factor=%.2f).",
        check.name,
        target_key,
        old_value,
        new_spec["params"][target_key],
        factor,
    )

    return new_spec


# =====================================================================
# Auto-Fix Strategy Stub: reshuffle_pair
# =====================================================================

def reshuffle_pair(
    check: Check,
    df: pd.DataFrame,
    column: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Isolated stub: randomly permute one column to destroy spurious
    correlation.

    [Subtask 9.2.3]

    §2.9: "orthogonal_*": lambda c: reshuffle_pair(c)

    B2/B3 DEPENDENCY: Isolated stub; integration deferred to Sprint 13.
    The caller is responsible for ensuring the column is NOT referenced
    in any pattern target expression (the exclusion guard is in the
    caller, not in this stub — per locked assumption [B3]).

    Creates a copy of the DataFrame, then replaces the specified
    column's values with a random permutation of the same values.
    The multiset of values is preserved (same values, different row
    assignment), which destroys any row-level correlation with other
    columns while maintaining marginal distribution.

    Args:
        check: The failing Check object (for context/logging).
        df: DataFrame to reshuffle.
        column: Column name to permute.
        rng: Seeded generator for reproducibility.

    Returns:
        New DataFrame with the specified column permuted.
        The original DataFrame is NOT mutated.

    Raises:
        KeyError: If column is not in df.
    """
    # ===== Phase 1: Validate column exists =====

    # Fail fast if the column name is not in the DataFrame — KeyError
    # matches the interface sketch and is descriptive
    if column not in df.columns:
        raise KeyError(
            f"Column '{column}' not found in DataFrame. "
            f"Available columns: {list(df.columns)}"
        )

    # ===== Phase 2: Create copy and permute the target column =====

    # Copy the entire DataFrame so the caller's original is preserved
    new_df = df.copy()

    # IMPORTANT (cause -> fix):
    # We intentionally avoid `rng.shuffle(StringArray)` because pandas'
    # StringDtype column can expose an extension array that numpy warns is
    # not a guaranteed Sequence for shuffle semantics. That warning signals
    # potential instability in permutation behavior across versions/backends.
    #
    # Safer approach: shuffle positional indices, then reorder the Series via
    # pandas. This preserves the value multiset and keeps StringDtype/NA
    # semantics under pandas instead of relying on numpy to mutate EAs.
    perm = rng.permutation(len(new_df))
    shuffled = new_df[column].take(perm).copy()
    shuffled.index = new_df.index
    new_df[column] = shuffled

    logger.debug(
        "reshuffle_pair: check='%s', shuffled column '%s' (%d rows).",
        check.name,
        column,
        len(new_df),
    )

    return new_df
