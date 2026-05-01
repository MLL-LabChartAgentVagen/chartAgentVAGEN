"""
Phase δ — Realism injection extracted from FactTableSimulator.

This module injects missing values (NaN) and dirty values (character-level
perturbations) into the generated DataFrame.  Functions accept explicit
parameters rather than reading FactTableSimulator instance state.

Extracted during the Sprint 6 post-completion refactoring.
Original locations: FactTableSimulator._inject_realism,
    FactTableSimulator._inject_missing_values,
    FactTableSimulator._inject_dirty_values,
    FactTableSimulator._perturb_string.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def inject_realism(
    df: pd.DataFrame,
    realism_config: dict[str, Any],
    columns: dict[str, dict[str, Any]],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Phase δ: Apply censoring, missing-value, and dirty-value realism injection.

    [Subtask 4.4.1, 4.4.2, 4.4.3]

    Censoring runs first so missing_rate is computed against the post-censor
    distribution; dirty injection runs last to avoid perturbing cells that
    will be NaN'd by missing.

    Args:
        df: DataFrame after pattern injection.
        realism_config: Dict with optional keys ``missing_rate``,
            ``dirty_rate``, ``censoring``.
        columns: Column registry for categorical column identification.
        rng: Seeded NumPy random generator.

    Returns:
        DataFrame with realism applied (modified in-place and returned).
    """
    missing_rate = realism_config.get("missing_rate", 0.0)
    dirty_rate = realism_config.get("dirty_rate", 0.0)
    censoring = realism_config.get("censoring")

    if censoring:
        df = inject_censoring(df, censoring, rng)

    if missing_rate > 0.0:
        df = inject_missing_values(df, missing_rate, rng)

    if dirty_rate > 0.0:
        df = inject_dirty_values(df, columns, dirty_rate, rng)

    return df


def inject_censoring(
    df: pd.DataFrame,
    censoring_config: dict[str, dict[str, Any]],
    rng: np.random.Generator,  # unused; kept for signature symmetry with sibling injectors
) -> pd.DataFrame:
    """Apply per-column censoring by masking out-of-range values to NaN.

    [Subtask 4.4.3]

    Schema (CensoringSpec):
        {"col": {"type": "right",    "threshold": <float>}}  -> values > threshold -> NaN
        {"col": {"type": "left",     "threshold": <float>}}  -> values < threshold -> NaN
        {"col": {"type": "interval", "low": <float>, "high": <float>}}  -> outside -> NaN

    Missing columns are warned and skipped (no error).  Empty config is a no-op.
    Unknown ``type`` raises ValueError.

    Args:
        df: DataFrame to censor.
        censoring_config: Mapping of column name -> per-column spec dict.
        rng: Unused; accepted for signature symmetry with the other injectors.

    Returns:
        DataFrame with censored cells set to NaN (modified in-place and returned).
    """
    if not censoring_config:
        return df

    total_censored = 0
    for col, spec in censoring_config.items():
        if col not in df.columns:
            logger.warning(
                "inject_censoring: column '%s' not in DataFrame; skipping.", col,
            )
            continue
        c_type = spec["type"]
        if c_type == "right":
            mask = df[col] > spec["threshold"]
        elif c_type == "left":
            mask = df[col] < spec["threshold"]
        elif c_type == "interval":
            mask = (df[col] < spec["low"]) | (df[col] > spec["high"])
        else:
            raise ValueError(
                f"Unknown censoring type '{c_type}' for column '{col}'. "
                f"Expected one of: right, left, interval."
            )
        df.loc[mask, col] = np.nan
        total_censored += int(mask.sum())

    logger.debug(
        "inject_censoring: censored %d cells across %d columns.",
        total_censored, len(censoring_config),
    )
    return df


def inject_missing_values(
    df: pd.DataFrame,
    missing_rate: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Inject NaN values at the declared *missing_rate*.

    [Subtask 4.4.1]

    Creates a boolean mask of shape ``df.shape`` where each cell has
    independent probability *missing_rate* of being True, then sets
    masked cells to NaN.

    Args:
        df: DataFrame to inject into.
        missing_rate: Fraction of cells to nullify, in [0, 1].
        rng: Seeded generator.

    Returns:
        DataFrame with NaN values injected.
    """
    if df.size == 0:
        return df

    mask = rng.random(size=df.shape) < missing_rate
    df = df.mask(mask)

    injected_count = mask.sum()
    logger.debug(
        "inject_missing_values: rate=%.4f, injected %d / %d cells.",
        missing_rate, injected_count, df.size,
    )
    return df


def inject_dirty_values(
    df: pd.DataFrame,
    columns: dict[str, dict[str, Any]],
    dirty_rate: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Inject dirty values (typos) into categorical columns.

    [Subtask 4.4.2]

    For each categorical column, selects approximately *dirty_rate*
    fraction of non-NaN cells and applies a random character-level
    perturbation (swap, delete, or insert).

    Args:
        df: DataFrame to inject into.
        columns: Column registry for type identification.
        dirty_rate: Fraction of categorical cells to corrupt, in [0, 1].
        rng: Seeded generator.

    Returns:
        DataFrame with dirty categorical values.
    """
    cat_cols = [
        col_name for col_name, col_meta in columns.items()
        if col_meta.get("type") == "categorical" and col_name in df.columns
    ]

    if not cat_cols:
        return df

    total_dirty = 0

    for col_name in cat_cols:
        series = df[col_name]
        valid_mask = series.notna()
        valid_idx = df.index[valid_mask]

        if len(valid_idx) == 0:
            continue

        selection_mask = rng.random(size=len(valid_idx)) < dirty_rate
        dirty_idx = valid_idx[selection_mask]

        if len(dirty_idx) == 0:
            continue

        perturbed_values = []
        for idx in dirty_idx:
            original = str(series.loc[idx])
            perturbed = perturb_string(original, rng)
            perturbed_values.append(perturbed)

        df.loc[dirty_idx, col_name] = perturbed_values
        total_dirty += len(dirty_idx)

    logger.debug(
        "inject_dirty_values: rate=%.4f, perturbed %d categorical cells "
        "across %d columns.",
        dirty_rate, total_dirty, len(cat_cols),
    )
    return df


def perturb_string(value: str, rng: np.random.Generator) -> str:
    """Apply a single random character-level perturbation to a string.

    [Subtask 4.4.2 helper]

    Perturbation types (selected uniformly at random):
      0 = swap two adjacent characters (requires len >= 2)
      1 = delete one character (requires len >= 2)
      2 = insert a random lowercase letter at a random position

    Args:
        value: Original string value.
        rng: Seeded generator.

    Returns:
        Perturbed string.
    """
    if len(value) == 0:
        return value

    chars = list(value)

    if len(chars) < 2:
        perturbation_type = 2
    else:
        perturbation_type = int(rng.integers(0, 3))

    if perturbation_type == 0:
        pos = int(rng.integers(0, len(chars) - 1))
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
    elif perturbation_type == 1:
        pos = int(rng.integers(0, len(chars)))
        chars.pop(pos)
    else:
        pos = int(rng.integers(0, len(chars) + 1))
        letter = chr(int(rng.integers(ord("a"), ord("z") + 1)))
        chars.insert(pos, letter)

    return "".join(chars)
