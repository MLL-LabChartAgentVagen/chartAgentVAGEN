"""
Engine post-processing — DataFrame assembly from column arrays.

Extracted from FactTableSimulator._post_process.

Implements: §2.8 τ_post
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def to_dataframe(
    rows: dict[str, np.ndarray],
    topo_order: list[str],
    columns: dict[str, dict[str, Any]],
    target_rows: int,
) -> pd.DataFrame:
    """Convert column arrays into a typed pandas DataFrame.

    [Subtask 4.5.1]

    Dtype policy:
      - categorical → object (Python str)
      - temporal → datetime64[ns]
      - temporal_derived (day_of_week, month, quarter) → int64
      - temporal_derived (is_weekend) → bool
      - measure → float64 (when implemented)

    Column ordering follows the topological order, filtered to only
    columns present in the rows dict.

    Args:
        rows: Dict mapping column name → numpy array.
        topo_order: Full topological order for column sequencing.
        columns: Column registry for dtype information.
        target_rows: Expected row count.

    Returns:
        pd.DataFrame with target_rows rows.
    """
    # Determine column order — only columns actually generated
    ordered_cols = [col for col in topo_order if col in rows]

    # Build DataFrame from ordered column dict
    data: dict[str, np.ndarray] = {col: rows[col] for col in ordered_cols}
    df = pd.DataFrame(data, index=range(target_rows))

    # Apply dtype casting per column type
    for col_name in ordered_cols:
        col_meta = columns.get(col_name)
        if col_meta is None:
            continue

        col_type = col_meta.get("type")

        if col_type == "categorical":
            df[col_name] = df[col_name].astype(object)

        elif col_type == "temporal":
            df[col_name] = pd.to_datetime(df[col_name])

        elif col_type == "temporal_derived":
            derivation = col_meta.get("derivation")
            if derivation == "is_weekend":
                df[col_name] = df[col_name].astype(bool)
            else:
                df[col_name] = df[col_name].astype(np.int64)

    logger.debug(
        "to_dataframe: DataFrame shape=%s, columns=%s.",
        df.shape,
        list(df.columns),
    )

    return df
