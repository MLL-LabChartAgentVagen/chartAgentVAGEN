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
