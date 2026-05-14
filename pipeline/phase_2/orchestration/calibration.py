"""Sigma calibration check for Loop A — measures declared vs empirical noise std.

When LLM-declared `noise sigma` is far from the formula's actual residual std
(typical in multiplicative chains, see FAILURE_MECHANISMS.md §2), the Stage 2
residual_* validator rejects the scenario. This module runs a full-N pre-realism
replay inside Loop A, gives the LLM a typed feedback with concrete sigma
suggestions, and short-circuits if any measure is mis-calibrated past threshold.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CalibrationFailure:
    measure: str
    declared_sigma: float
    empirical_residual_std: float
    suggested_sigma: float   # equals empirical_residual_std
    ratio: float             # |empirical - declared| / declared


@dataclass
class CalibrationResult:
    passed: bool
    failures: list[CalibrationFailure] = field(default_factory=list)
    threshold: float = 0.2


def check_sigma_calibration(
    raw_declarations: dict[str, Any],
    threshold: float = 0.2,
) -> CalibrationResult:
    """Run a full-N pre-realism replay and check declared vs empirical sigma."""
    from ..engine.generator import run_pipeline
    from ..validation.statistical import check_structural_residuals

    columns = raw_declarations["columns"]   # OrderedDict {name: spec}

    df_clean, schema_metadata = run_pipeline(
        columns=columns,
        groups=raw_declarations["groups"],
        group_dependencies=raw_declarations.get("group_dependencies", []),
        measure_dag=raw_declarations["measure_dag"],
        target_rows=raw_declarations["target_rows"],
        seed=raw_declarations.get("seed", 42),
        patterns=raw_declarations.get("patterns", []),
        realism_config=None,
        orthogonal_pairs=raw_declarations.get("orthogonal_pairs", []),
    )

    failures: list[CalibrationFailure] = []
    for col_name, col_spec in columns.items():
        if col_spec.get("type") != "measure":
            continue
        if col_spec.get("measure_type") != "structural":
            continue
        declared_sigma = _extract_declared_sigma(col_spec)
        if declared_sigma is None:
            continue
        check = check_structural_residuals(
            df_clean, col_name, schema_metadata,
            patterns=raw_declarations.get("patterns", []),
        )
        empirical_std = _parse_residual_std_from_detail(check.detail)
        if empirical_std is None:
            continue
        ratio = abs(empirical_std - declared_sigma) / declared_sigma
        if ratio >= threshold:
            failures.append(CalibrationFailure(
                measure=col_name,
                declared_sigma=declared_sigma,
                empirical_residual_std=empirical_std,
                suggested_sigma=empirical_std,
                ratio=ratio,
            ))
    return CalibrationResult(passed=(not failures), failures=failures, threshold=threshold)


def _extract_declared_sigma(col_spec: dict[str, Any]) -> float | None:
    """Pull sigma from a structural measure's noise dict, returning None for invalid/missing."""
    noise = col_spec.get("noise") or {}
    sigma = noise.get("sigma")
    if sigma is None or not isinstance(sigma, (int, float)) or sigma <= 0:
        return None
    return float(sigma)


def _parse_residual_std_from_detail(detail: str | None) -> float | None:
    """Extract residual_std from check_structural_residuals' detail string.

    Extract residual_std= from any check_structural_residuals detail string,
    regardless of whether the deterministic or stochastic branch produced it.
    """
    if not detail:
        return None
    m = re.search(r"residual_std=([\d.eE+-]+)", detail)
    return float(m.group(1)) if m else None
