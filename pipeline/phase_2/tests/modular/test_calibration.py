"""Tests for pipeline/phase_2/orchestration/calibration.py."""
from __future__ import annotations

import pytest

from pipeline.phase_2.orchestration.calibration import (
    CalibrationFailure,
    CalibrationResult,
    check_sigma_calibration,
)


class TestCalibrationDataclasses:
    def test_calibration_result_default_passed_false_empty_failures(self):
        r = CalibrationResult(passed=False)
        assert r.failures == []
        assert r.threshold == 0.2

    def test_calibration_failure_fields(self):
        f = CalibrationFailure(
            measure="x", declared_sigma=5.0, empirical_residual_std=337.0,
            suggested_sigma=337.0, ratio=66.4,
        )
        assert f.measure == "x" and f.suggested_sigma == 337.0


import numpy as np
import pandas as pd


class TestCheckSigmaCalibration:
    @staticmethod
    def _minimal_declarations(noise_sigma: float):
        """Build declarations via FactTableSimulator — same shape sandbox produces."""
        from pipeline.phase_2.sdk.simulator import FactTableSimulator

        sim = FactTableSimulator(target_rows=500, seed=42)
        sim.add_category("region", values=["N", "S"], weights=[0.5, 0.5], group="geo")
        sim.add_measure(
            "applied",
            family="gaussian",
            param_model={
                "mu": {"intercept": 1000.0},
                "sigma": {"intercept": 100.0},
            },
        )
        sim.add_measure_structural(
            "accepted",
            formula="applied * 0.5",
            effects={},
            noise={"sigma": noise_sigma},
        )
        return {
            "columns": sim._columns,
            "groups": sim._groups,
            "group_dependencies": sim._group_dependencies,
            "measure_dag": sim._measure_dag,
            "target_rows": sim.target_rows,
            "patterns": sim._patterns,
            "seed": sim.seed,
            "orthogonal_pairs": sim._orthogonal_pairs,
        }

    def test_passes_when_sigma_matches_empirical(self):
        # accepted = applied * 0.5 + noise(sigma=50).
        # The residual is just the gaussian noise → residual std ≈ 50.
        # So declared sigma=50 should pass.
        decls = self._minimal_declarations(noise_sigma=50.0)
        result = check_sigma_calibration(decls, threshold=0.2)
        assert result.passed, f"Unexpected failures: {result.failures}"
