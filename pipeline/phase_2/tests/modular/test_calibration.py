"""Tests for pipeline/phase_2/orchestration/calibration.py."""
from __future__ import annotations

import pytest

from pipeline.phase_2.orchestration.calibration import (
    CalibrationFailure,
    CalibrationResult,
    check_sigma_calibration,
    _extract_declared_sigma,
    _parse_residual_std_from_detail,
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

    def test_fails_for_underspecified_sigma(self):
        # Realistic mismatch: declared sigma=5, empirical residual_std=337 (66× ratio).
        # Mocking check_structural_residuals lets us test the dispatch+threshold
        # logic without coercing the engine into a tough multiplicative misfit
        # (the real pingyue case mode that motivated this calibration check).
        from unittest.mock import patch
        from pipeline.phase_2.types import Check

        decls = self._minimal_declarations(noise_sigma=5.0)
        fake_check = Check(
            name="residual_accepted",
            passed=False,
            detail="noise_sigma=5.0000, residual_std=337.6500, ratio=66.5300 (>= 0.2)",
        )
        with patch(
            "pipeline.phase_2.validation.statistical.check_structural_residuals",
            return_value=fake_check,
        ):
            result = check_sigma_calibration(decls, threshold=0.2)

        assert not result.passed
        assert len(result.failures) == 1
        f = result.failures[0]
        assert f.measure == "accepted"
        assert f.declared_sigma == 5.0
        assert abs(f.empirical_residual_std - 337.65) < 0.01
        assert f.suggested_sigma == f.empirical_residual_std
        assert f.ratio > 0.2

    def test_skips_measure_without_noise(self):
        # If `accepted` has no noise.sigma, calibration should not fail on it.
        # We build via FactTableSimulator just like _minimal_declarations does.
        from pipeline.phase_2.sdk.simulator import FactTableSimulator
        sim = FactTableSimulator(target_rows=500, seed=42)
        sim.add_category("region", values=["N", "S"], weights=[0.5, 0.5], group="geo")
        sim.add_measure(
            "applied",
            family="gaussian",
            param_model={"mu": {"intercept": 1000.0}, "sigma": {"intercept": 100.0}},
        )
        sim.add_measure_structural(
            "accepted", formula="applied * 0.5", effects={}, noise={}   # ← no sigma
        )
        decls = {
            "columns": sim._columns,
            "groups": sim._groups,
            "group_dependencies": sim._group_dependencies,
            "measure_dag": sim._measure_dag,
            "target_rows": sim.target_rows,
            "patterns": sim._patterns,
            "seed": sim.seed,
            "orthogonal_pairs": sim._orthogonal_pairs,
        }
        result = check_sigma_calibration(decls, threshold=0.2)
        assert result.passed
        assert result.failures == []


class TestExtractDeclaredSigma:
    @pytest.mark.parametrize("noise_spec,expected", [
        ({"sigma": 5.0}, 5.0),
        ({"sigma": 0.0}, None),
        ({"sigma": -1.0}, None),
        ({"sigma": None}, None),
        ({}, None),
        (None, None),
    ])
    def test_extract_variants(self, noise_spec, expected):
        col_spec = {"type": "measure", "measure_type": "structural"}
        if noise_spec is not None:
            col_spec["noise"] = noise_spec
        assert _extract_declared_sigma(col_spec) == expected


class TestParseResidualStd:
    def test_extract_from_valid_detail(self):
        d = "noise_sigma=5.0000, residual_std=337.6500, ratio=66.5 (>= 0.2)"
        assert _parse_residual_std_from_detail(d) == 337.65

    def test_raises_for_malformed(self):
        with pytest.raises(RuntimeError, match="empty detail"):
            _parse_residual_std_from_detail("")
        with pytest.raises(RuntimeError, match="format unexpected"):
            _parse_residual_std_from_detail("nothing useful")


class TestStochasticMeasuresSkipped:
    def test_stochastic_measure_with_underspecified_sigma_is_not_flagged(self):
        """V1 contract: check_sigma_calibration only inspects structural measures.
        Stochastic measures (e.g. with effects on intercept) are out of scope and
        must not trigger CalibrationFailure even if their declared sigma is way off.
        Future v2 may extend; this test will fail then and be updated intentionally."""
        from pipeline.phase_2.sdk.simulator import FactTableSimulator
        sim = FactTableSimulator(target_rows=500, seed=42)
        sim.add_category("region", values=["N", "S"], weights=[0.5, 0.5], group="geo")
        sim.add_measure(
            "applied", family="gaussian",
            param_model={"mu": {"intercept": 1000.0}, "sigma": {"intercept": 0.001}},
        )
        decls = {
            "columns": sim._columns,
            "groups": sim._groups,
            "group_dependencies": sim._group_dependencies,
            "measure_dag": sim._measure_dag,
            "target_rows": sim.target_rows,
            "patterns": sim._patterns,
            "seed": sim.seed,
            "orthogonal_pairs": sim._orthogonal_pairs,
        }
        result = check_sigma_calibration(decls, threshold=0.2)
        assert result.passed
        assert result.failures == []


from pipeline.phase_2.exceptions import SkipResult


class TestSkipResultSkipReason:
    def test_default_reason_is_exec_error(self):
        s = SkipResult(scenario_id="foo")
        assert s.skip_reason == "exec_error"

    def test_can_set_calibration_unconverged(self):
        s = SkipResult(
            scenario_id="foo", error_log=["..."],
            skip_reason="calibration_unconverged",
        )
        assert s.skip_reason == "calibration_unconverged"


class TestSaveSkipRecord:
    def test_appends_jsonl_with_skip_metadata(self, tmp_path):
        from pipeline.agpds_generate import _save_skip_record
        import json

        skip = SkipResult(
            scenario_id="dom_001/k=2", error_log=["err1", "err2"],
            skip_reason="calibration_unconverged",
        )
        _save_skip_record(str(tmp_path), skip, gen_id="agpds_abc123")

        skip_file = tmp_path / "skipped.jsonl"
        assert skip_file.exists()
        line = skip_file.read_text().strip()
        rec = json.loads(line)
        assert rec["generation_id"] == "agpds_abc123"
        assert rec["scenario_id"] == "dom_001/k=2"
        assert rec["skip_reason"] == "calibration_unconverged"
        assert rec["error_log"] == ["err1", "err2"]
        assert "timestamp" in rec
