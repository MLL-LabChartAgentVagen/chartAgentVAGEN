"""Sigma calibration check for Loop A — measures declared vs empirical noise std.

When LLM-declared `noise sigma` is far from the formula's actual residual std
(typical in multiplicative chains, see FAILURE_MECHANISMS.md §2), the Stage 2
residual_* validator rejects the scenario. This module runs a full-N pre-realism
replay inside Loop A, gives the LLM a typed feedback with concrete sigma
suggestions, and short-circuits if any measure is mis-calibrated past threshold.
"""
from __future__ import annotations
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
    """Run a full-N pre-realism replay and check declared vs empirical sigma.

    Args:
        raw_declarations: The dict returned by sandbox exec (SandboxResult.raw_declarations).
        threshold: Max allowed |empirical - declared| / declared. Default 0.2 (matches validator).

    Returns:
        CalibrationResult with failures list (empty iff passed).
    """
    raise NotImplementedError("implement in Task 2")
