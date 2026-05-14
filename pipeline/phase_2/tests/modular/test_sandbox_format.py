"""Tests for the calibration feedback formatter in sandbox.py."""
from __future__ import annotations

import pytest

from pipeline.phase_2.orchestration.calibration import CalibrationFailure
from pipeline.phase_2.orchestration.sandbox import format_calibration_feedback


class TestFormatCalibrationFeedback:
    def test_includes_each_failure_with_concrete_numbers(self):
        failures = [
            CalibrationFailure(
                measure="absentee_count", declared_sigma=5.0,
                empirical_residual_std=337.3, suggested_sigma=337.3, ratio=66.5,
            ),
            CalibrationFailure(
                measure="citation_count", declared_sigma=45.0,
                empirical_residual_std=319.3, suggested_sigma=319.3, ratio=6.1,
            ),
        ]
        out = format_calibration_feedback("ORIGINAL_CODE_HERE", failures)
        assert "absentee_count" in out and "337" in out and "5.0" in out
        assert "citation_count" in out and "319" in out and "45.0" in out
        assert "Do NOT change" in out or "Do not change" in out
        assert "ORIGINAL_CODE_HERE" in out

    def test_empty_failures_returns_neutral_message(self):
        out = format_calibration_feedback("CODE", failures=[])
        assert "0" in out or "no" in out.lower()
