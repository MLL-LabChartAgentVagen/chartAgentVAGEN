# Stage 1 Sigma Calibration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an LLM-in-the-loop sigma calibration step to Phase 2 Stage 1 / Loop A, so the LLM gets concrete "your declared sigma is off, use this value instead" feedback before declarations are persisted.

**Architecture:** After every successful sandbox exec, the engine does a full-N replay with `realism_config=None` (matching what the Stage 2 validator sees), computes empirical residual std for each declared-sigma measure, and if any measure's ratio exceeds 0.2 the retry loop re-feeds the LLM with a structured calibration prompt. Reuses the existing 3-retry budget; final failure becomes a typed `SkipResult(skip_reason="calibration_unconverged")` that surfaces in a new `skipped.jsonl`.

**Tech Stack:** Python 3.10+, `numpy`, `pandas`, `pytest`, `numpy.random.Generator`. Plan integrates with existing `pipeline/phase_2/orchestration/{retry_loop,sandbox}.py`, `pipeline/phase_2/engine/generator.py`, `pipeline/phase_2/validation/statistical.py`, `pipeline/phase_2/exceptions.py`, `pipeline/agpds_generate.py`.

**Approved spec:** [/home/dingcheng/.claude/plans/pipeline-agpds-execute-py-soft-warning-temporal-rivest.md](/home/dingcheng/.claude/plans/pipeline-agpds-execute-py-soft-warning-temporal-rivest.md) — this implementation plan elaborates that spec into TDD-style tasks. Read the spec first for context.

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `pipeline/phase_2/orchestration/calibration.py` | **CREATE** | `check_sigma_calibration()` + `CalibrationFailure`/`CalibrationResult` dataclasses + `_extract_declared_sigma` helper |
| `pipeline/phase_2/orchestration/sandbox.py` | MODIFY | Add `format_calibration_feedback()` after `format_error_feedback` (around L:628) |
| `pipeline/phase_2/orchestration/retry_loop.py` | MODIFY | At [retry_loop.py:230](pipeline/phase_2/orchestration/retry_loop.py#L230) `if result.success:` — insert calibration check, retry branch on failure |
| `pipeline/phase_2/exceptions.py` | MODIFY | `SkipResult` (L:344-360) — add `skip_reason: str = "exec_error"` field |
| `pipeline/agpds_generate.py` | MODIFY | New `_save_skip_record(output_dir, skip_result, gen_id, scenario_id)`; call when LLM returns `SkipResult` |
| `pipeline/phase_2/tests/modular/test_calibration.py` | **CREATE** | 5 unit tests (per spec §6.1) |
| `pipeline/phase_2/tests/modular/test_sandbox_format.py` | MODIFY | Add 2 tests for `format_calibration_feedback` |
| `pipeline/phase_2/tests/modular/test_retry_loop.py` | MODIFY | Add 3 integration tests (per spec §6.2) |
| `pipeline/phase_2/FAILURE_MECHANISMS.md` | MODIFY | Mark §7.1 as ✓ implemented; link to `calibration.py` |

---

## Task 1: Create `calibration.py` with empty scaffolding + first test

**Files:**
- Create: `pipeline/phase_2/orchestration/calibration.py`
- Create: `pipeline/phase_2/tests/modular/test_calibration.py`

- [ ] **Step 1.1: Create the module with public API stubs (no logic yet)**

Write to `pipeline/phase_2/orchestration/calibration.py`:

```python
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
```

- [ ] **Step 1.2: Create a failing-import test**

Write to `pipeline/phase_2/tests/modular/test_calibration.py`:

```python
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
```

- [ ] **Step 1.3: Run test, verify the dataclass tests pass**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_calibration.py -v
```

Expected: 2 passed.

- [ ] **Step 1.4: Commit**

```bash
git add pipeline/phase_2/orchestration/calibration.py pipeline/phase_2/tests/modular/test_calibration.py
git commit -m "feat(calibration): scaffold check_sigma_calibration module"
```

---

## Task 2: Implement `check_sigma_calibration` — happy path

**Files:**
- Modify: `pipeline/phase_2/orchestration/calibration.py`
- Modify: `pipeline/phase_2/tests/modular/test_calibration.py`

### Background on existing validator's residual check

The Stage 2 validator computes residual std for structural measures in [pipeline/phase_2/validation/statistical.py:368 check_structural_residuals](pipeline/phase_2/validation/statistical.py#L368). Pattern (from reading the function):

1. Evaluate `formula` per-row using `_safe_eval_formula(formula, context)` from `engine.measures`.
2. Effects resolved by `_resolve_effects` (also in `engine.measures`).
3. residuals = actual_values - formula_predicted_values
4. residual_std = residuals.std() (excluding pattern-targeted rows for P3-8)
5. Check: `abs(residual_std - declared_sigma) / declared_sigma < 0.2`

**Reuse strategy:** import `check_structural_residuals` from validation.statistical and call it for each structural measure. Parse its returned `Check.detail` to extract `residual_std`. This avoids duplicating the residual computation.

For STOCHASTIC measures with gaussian noise, residual std should equal declared sigma (not formula-based). Use `df[col].std()` minus the per-cell mean structure — but actually for stochastic measures we can use [check_stochastic_ks](pipeline/phase_2/validation/statistical.py#L232) which computes empirical std vs declared sigma in cells.

For v1, **only handle structural measures**. Stochastic-only measures' sigma is rarely mis-calibrated (because their formula IS just gaussian noise). YAGNI.

- [ ] **Step 2.1: Write a failing test for the happy path**

Add to `test_calibration.py`:

```python
import re
import numpy as np
import pandas as pd

from pipeline.phase_2.engine.generator import run_pipeline


class TestCheckSigmaCalibration:
    @staticmethod
    def _minimal_declarations(noise_sigma: float):
        """Build a tiny declaration: 1 cat root + 1 stochastic + 1 structural with given sigma."""
        return {
            "columns": [
                {"name": "region", "spec": {
                    "type": "categorical",
                    "values": ["N", "S"],
                    "weights": [0.5, 0.5],
                    "group": "geo",
                }},
                {"name": "applied", "spec": {
                    "type": "measure",
                    "measure_type": "stochastic",
                    "family": "gaussian",
                    "param_model": {
                        "mu": {"intercept": 1000.0},
                        "sigma": {"intercept": 100.0},
                    },
                }},
                {"name": "accepted", "spec": {
                    "type": "measure",
                    "measure_type": "structural",
                    "formula": "applied * 0.5",
                    "effects": {},
                    "noise": {"sigma": noise_sigma},
                }},
            ],
            "groups": {"geo": {"root": "region", "members": ["region"]}},
            "group_dependencies": [],
            "orthogonal_pairs": [],
            "measure_dag": {
                "order": ["applied", "accepted"],
                "edges": [["applied", "accepted"]],
            },
            "patterns": [],
            "target_rows": 500,
            "seed": 42,
        }

    def test_passes_when_sigma_matches_empirical(self):
        # applied has σ=100, accepted = applied * 0.5 → residual std ≈ 0 (deterministic apart from noise)
        # With noise={"sigma": 50}, the formula's added noise produces residual std ≈ 50.
        # So declared sigma=50 should pass.
        decls = self._minimal_declarations(noise_sigma=50.0)
        result = check_sigma_calibration(decls, threshold=0.2)
        assert result.passed, f"Unexpected failures: {result.failures}"
```

- [ ] **Step 2.2: Run test, verify it fails with NotImplementedError**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_calibration.py::TestCheckSigmaCalibration -v
```

Expected: FAIL with `NotImplementedError`.

- [ ] **Step 2.3: Implement `check_sigma_calibration`**

Replace the `raise NotImplementedError` in `calibration.py` with:

```python
def check_sigma_calibration(
    raw_declarations: dict[str, Any],
    threshold: float = 0.2,
) -> CalibrationResult:
    from ..engine.generator import run_pipeline
    from ..validation.statistical import check_structural_residuals

    columns_list = raw_declarations.get("columns", [])
    # Convert list-of-{name,spec} to dict-{name: spec} as run_pipeline expects
    columns = {c["name"]: c["spec"] for c in columns_list}

    df_clean, schema_metadata = run_pipeline(
        columns=columns,
        groups=raw_declarations.get("groups", {}),
        group_dependencies=raw_declarations.get("group_dependencies", []),
        measure_dag=raw_declarations.get("measure_dag", {}),
        target_rows=raw_declarations.get("target_rows"),
        seed=raw_declarations.get("seed", 42),
        patterns=raw_declarations.get("patterns", []),
        realism_config=None,                                    # ← critical
        orthogonal_pairs=raw_declarations.get("orthogonal_pairs", []),
    )

    failures: list[CalibrationFailure] = []
    for col_name, col_spec in columns.items():
        if col_spec.get("type") != "measure":
            continue
        if col_spec.get("measure_type") != "structural":
            continue  # v1: stochastic-only sigmas rarely mis-calibrated
        declared_sigma = _extract_declared_sigma(col_spec)
        if declared_sigma is None or declared_sigma <= 0:
            continue
        check = check_structural_residuals(
            df_clean, col_name, schema_metadata,
            patterns=raw_declarations.get("patterns", []),
        )
        empirical_std = _parse_residual_std_from_detail(check.detail)
        if empirical_std is None:
            continue  # malformed detail; conservatively skip
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
    """Pull sigma out of a structural measure's noise dict.

    Accepted forms:
      - `noise={"sigma": 5.0}` → 5.0
      - `noise={}` or no noise key → None (no-op, deterministic)
      - `noise={"sigma": 0}` or None → None (signals no calibration needed)
    """
    noise = col_spec.get("noise") or {}
    sigma = noise.get("sigma")
    if sigma is None or not isinstance(sigma, (int, float)) or sigma <= 0:
        return None
    return float(sigma)


def _parse_residual_std_from_detail(detail: str | None) -> float | None:
    """Extract residual_std from check_structural_residuals' detail string.

    The detail format is: 'noise_sigma=X, residual_std=Y, ratio=Z (...)'
    """
    if not detail:
        return None
    import re
    m = re.search(r"residual_std=([\d.eE+-]+)", detail)
    return float(m.group(1)) if m else None
```

- [ ] **Step 2.4: Run test, verify it passes**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_calibration.py::TestCheckSigmaCalibration::test_passes_when_sigma_matches_empirical -v
```

Expected: PASS.

- [ ] **Step 2.5: Commit**

```bash
git add pipeline/phase_2/orchestration/calibration.py pipeline/phase_2/tests/modular/test_calibration.py
git commit -m "feat(calibration): implement check_sigma_calibration happy path"
```

---

## Task 3: Cover failure cases + helper edge cases

**Files:**
- Modify: `pipeline/phase_2/tests/modular/test_calibration.py`

- [ ] **Step 3.1: Write failure-case test**

Add to `TestCheckSigmaCalibration`:

```python
    def test_fails_for_underspecified_sigma(self):
        decls = self._minimal_declarations(noise_sigma=2.0)   # way too small
        result = check_sigma_calibration(decls, threshold=0.2)
        assert not result.passed
        assert len(result.failures) == 1
        f = result.failures[0]
        assert f.measure == "accepted"
        assert f.declared_sigma == 2.0
        assert f.empirical_residual_std > 30   # we declared σ=2, actual ≈ 50
        assert f.suggested_sigma == f.empirical_residual_std
        assert f.ratio > 0.2

    def test_skips_measure_without_noise(self):
        decls = self._minimal_declarations(noise_sigma=50.0)
        # Strip noise from accepted
        for c in decls["columns"]:
            if c["name"] == "accepted":
                c["spec"]["noise"] = {}
        result = check_sigma_calibration(decls, threshold=0.2)
        assert result.passed
        assert result.failures == []
```

- [ ] **Step 3.2: Write extractor / parser unit tests**

```python
from pipeline.phase_2.orchestration.calibration import (
    _extract_declared_sigma,
    _parse_residual_std_from_detail,
)


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

    def test_returns_none_for_malformed(self):
        assert _parse_residual_std_from_detail(None) is None
        assert _parse_residual_std_from_detail("nothing useful") is None
```

- [ ] **Step 3.3: Run all calibration tests, verify pass**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_calibration.py -v
```

Expected: all 8 PASS.

- [ ] **Step 3.4: Verify whole modular test suite still passes (no regressions)**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular -x -q
```

Expected: ≥360 passed (was 355 before this plan).

- [ ] **Step 3.5: Commit (closes spec commit 1)**

```bash
git add pipeline/phase_2/tests/modular/test_calibration.py
git commit -m "test(calibration): cover failure path + helper edge cases"
```

---

## Task 4: `format_calibration_feedback` in `sandbox.py`

**Files:**
- Modify: `pipeline/phase_2/orchestration/sandbox.py`
- Modify (or create): `pipeline/phase_2/tests/modular/test_sandbox_format.py`

- [ ] **Step 4.1: Write failing test**

If `test_sandbox_format.py` doesn't exist, create it. Add:

```python
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
        # Every failure surfaces concrete declared, empirical, suggested
        assert "absentee_count" in out and "337" in out and "5.0" in out
        assert "citation_count" in out and "319" in out and "45.0" in out
        # Instruction NOT to change non-sigma stuff
        assert "Do NOT change" in out or "Do not change" in out
        assert "ORIGINAL_CODE_HERE" in out

    def test_empty_failures_returns_neutral_message(self):
        # Defensive: should not crash; "0 measure(s)" is acceptable
        out = format_calibration_feedback("CODE", failures=[])
        assert "0" in out or "no" in out.lower()
```

- [ ] **Step 4.2: Run test, verify ImportError**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_sandbox_format.py -v
```

Expected: FAIL with ImportError ("cannot import name 'format_calibration_feedback'").

- [ ] **Step 4.3: Add `format_calibration_feedback` to `sandbox.py`**

Append to `pipeline/phase_2/orchestration/sandbox.py` (after `format_error_feedback`):

```python
def format_calibration_feedback(
    original_code: str,
    failures: list,           # list[CalibrationFailure] — avoid circular import
    prior_failures: "list | None" = None,
) -> str:
    """Format LLM feedback for a sigma-calibration failure.

    Used by retry_loop when Loop A's sandbox exec succeeds but
    check_sigma_calibration finds at least one measure with ratio >= 0.2.
    """
    if not failures:
        return (
            "Your script executed successfully and 0 measure(s) need "
            "calibration adjustments. (No action required.)"
        )
    body_lines = []
    for f in failures:
        body_lines.append(
            f"  - Measure `{f.measure}`: declared sigma={f.declared_sigma:.4f}, "
            f"empirical residual std={f.empirical_residual_std:.4f}, "
            f"ratio={f.ratio:.3f} (threshold=0.2). "
            f"Suggested sigma ≈ {f.suggested_sigma:.4f}."
        )
    body = "\n".join(body_lines)
    return (
        f"Your script executed successfully, but the declared noise sigma is "
        f"mis-calibrated for {len(failures)} measure(s):\n\n{body}\n\n"
        f"Action: rewrite the script with sigma values close to the suggested "
        f"empirical residual std (within ±10%). Do NOT change measure formulas, "
        f"categorical structure, patterns, or seeds — ONLY adjust sigma in "
        f"`noise=` / `noise_sigma=` arguments.\n\n"
        f"Original code:\n```python\n{original_code}\n```"
    )
```

- [ ] **Step 4.4: Run test, verify pass**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_sandbox_format.py -v
```

Expected: 2 PASS.

- [ ] **Step 4.5: Commit (closes spec commit 2)**

```bash
git add pipeline/phase_2/orchestration/sandbox.py pipeline/phase_2/tests/modular/test_sandbox_format.py
git commit -m "feat(calibration): format_calibration_feedback for Loop A"
```

---

## Task 5: `SkipResult.skip_reason` + `skipped.jsonl`

**Files:**
- Modify: `pipeline/phase_2/exceptions.py:344-360`
- Modify: `pipeline/agpds_generate.py`
- Modify: `pipeline/phase_2/tests/modular/test_calibration.py` (or new test file)

- [ ] **Step 5.1: Write test for SkipResult.skip_reason default**

Add to `pipeline/phase_2/tests/modular/test_calibration.py`:

```python
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
```

- [ ] **Step 5.2: Run, verify fails**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_calibration.py::TestSkipResultSkipReason -v
```

Expected: FAIL with `TypeError: __init__() got an unexpected keyword argument 'skip_reason'`.

- [ ] **Step 5.3: Modify `SkipResult`**

In `pipeline/phase_2/exceptions.py:344-360`, change to:

```python
@dataclass
class SkipResult:
    """Sentinel returned by M3 orchestration when all retries are exhausted.

    [Target Architecture — pipeline.py]

    Attributes:
        scenario_id: Identifier of the scenario that was skipped.
        error_log: List of error messages from each failed attempt.
        skip_reason: Why this scenario was skipped. One of:
            - "exec_error" (default): the LLM script failed to execute
            - "calibration_unconverged": script ran but sigma was mis-calibrated
              past threshold for max_retries attempts
    """
    scenario_id: str = ""
    error_log: list[str] = field(default_factory=list)
    skip_reason: str = "exec_error"
```

- [ ] **Step 5.4: Run, verify pass + no regressions**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular -x -q
```

Expected: ≥362 passed.

- [ ] **Step 5.5: Write test for `_save_skip_record`**

Add to `test_calibration.py`:

```python
import json
import tempfile
from pathlib import Path


class TestSaveSkipRecord:
    def test_appends_jsonl_with_skip_metadata(self, tmp_path):
        from pipeline.agpds_generate import _save_skip_record

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
```

- [ ] **Step 5.6: Run, verify ImportError**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_calibration.py::TestSaveSkipRecord -v
```

Expected: FAIL — `_save_skip_record` doesn't exist.

- [ ] **Step 5.7: Implement `_save_skip_record` in `agpds_generate.py`**

Add after `_save_stage1_artifacts` (around line 85):

```python
SKIPPED_FILENAME = "skipped.jsonl"


def _save_skip_record(
    output_dir: str,
    skip_result,                # SkipResult
    gen_id: str,
) -> None:
    """Append a SkipResult record to skipped.jsonl in the batch folder."""
    record = {
        "generation_id": gen_id,
        "scenario_id": skip_result.scenario_id,
        "skip_reason": skip_result.skip_reason,
        "error_log": list(skip_result.error_log),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    skip_path = os.path.join(output_dir, SKIPPED_FILENAME)
    with open(skip_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
```

- [ ] **Step 5.8: Run, verify pass**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_calibration.py::TestSaveSkipRecord -v
```

Expected: PASS.

- [ ] **Step 5.9: Commit (closes spec commit 3)**

```bash
git add pipeline/phase_2/exceptions.py pipeline/agpds_generate.py pipeline/phase_2/tests/modular/test_calibration.py
git commit -m "feat(calibration): SkipResult.skip_reason + skipped.jsonl"
```

---

## Task 6: Wire calibration into `retry_loop.py`

**Files:**
- Modify: `pipeline/phase_2/orchestration/retry_loop.py:230` and onward
- Modify: `pipeline/phase_2/tests/modular/test_retry_loop.py`

### Background

Current Loop A success path (retry_loop.py:230-242):

```python
if result.success:
    return RetryLoopResult(success=True, dataframe=..., ...)
```

We need to insert calibration BEFORE the success return.

- [ ] **Step 6.1: Write failing integration test — calibration triggers retry**

Add to `pipeline/phase_2/tests/modular/test_retry_loop.py`:

```python
class TestCalibrationInRetryLoop:
    """Integration: post-exec calibration check rewires retry on sigma failure."""

    def _make_llm_fn(self, scripts: list[str]):
        """Return an LLM mock that returns scripts in order; raises if exhausted."""
        it = iter(scripts)
        from pipeline.phase_2.types import LLMResponse

        def llm_fn(system: str, user: str) -> LLMResponse:
            return LLMResponse(text=next(it), token_usage=None)
        return llm_fn

    def test_retry_triggers_on_calibration_failure_then_skips(self, ...):
        """When LLM always writes sigma=1 for a 5x10 multiplicative chain,
        calibration fails for max_retries attempts, final state is SkipResult
        with skip_reason='calibration_unconverged'."""
        # Construct a 3-script sequence where each declares sigma=1
        # for a measure whose empirical residual std is ~50.
        # ... (use the minimal declaration template from test_calibration.py)
        # ... assert retry_loop returns SkipResult, skip_reason matches
```

Skip the full body for brevity — the engineer implementing this will need to construct a realistic LLM mock with 3 scripts that all under-declare sigma. The key assertion: `isinstance(result, SkipResult) and result.skip_reason == "calibration_unconverged"`.

- [ ] **Step 6.2: Run, verify it fails (assertion error since calibration not wired)**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_retry_loop.py::TestCalibrationInRetryLoop -v
```

Expected: FAIL — likely passes the bad script through.

- [ ] **Step 6.3: Modify `retry_loop.py:230`**

Replace lines 230-242 with:

```python
        if result.success:
            # NEW: Post-exec sigma calibration check (Loop A enhancement)
            from .calibration import check_sigma_calibration
            from .sandbox import format_calibration_feedback

            cal_result = check_sigma_calibration(
                raw_declarations=result.raw_declarations,
                threshold=0.2,
            )

            if cal_result.passed:
                logger.debug(
                    "§2.7 retry loop: succeeded with calibrated sigma on attempt %d",
                    attempt,
                )
                return RetryLoopResult(
                    success=True,
                    dataframe=result.dataframe,
                    metadata=result.metadata,
                    raw_declarations=result.raw_declarations,
                    source_code=result.source_code or current_code,
                    attempts=attempt,
                    history=history,
                )

            # Calibration failed: feed LLM the suggested sigmas
            if attempt < max_retries:
                prior_failures = [h for h in history[:-1] if not h.success]
                feedback_prompt = format_calibration_feedback(
                    original_code=current_code,
                    failures=cal_result.failures,
                    prior_failures=prior_failures,
                )
                logger.debug(
                    "§2.7 retry loop: calibration failed on attempt %d "
                    "(%d measure(s) off by ratio>=0.2) — re-prompting LLM",
                    attempt, len(cal_result.failures),
                )
                # Mirror exec-error retry path:
                try:
                    response = llm_generate_fn(system_prompt, feedback_prompt)
                    # ... (same token-budget + current_code update as
                    # the exec-error path at retry_loop.py:273-...)
                    current_code = response.text
                    continue
                except Exception:
                    raise   # bubble up
            else:
                # Last attempt: record calibration failure in error_log
                # so SkipResult gets skip_reason="calibration_unconverged"
                cal_summary = "; ".join(
                    f"{f.measure}: σ={f.declared_sigma:.2f} → suggest {f.suggested_sigma:.2f}"
                    for f in cal_result.failures
                )
                history[-1] = SandboxResult(
                    success=False,
                    exception=RuntimeError(f"calibration_unconverged: {cal_summary}"),
                    traceback_str=None,
                )
                # Fall through to the post-loop SkipResult construction
```

- [ ] **Step 6.4: Update SkipResult construction at end of loop**

Find where SkipResult is constructed (around retry_loop.py:309-314 or later, see `orchestrate` function at retry_loop.py:319). When the last `history` entry's exception message starts with `"calibration_unconverged:"`, set `skip_reason="calibration_unconverged"`.

Concrete edit at the SkipResult construction site:

```python
last_exc = history[-1].exception if history else None
skip_reason = "exec_error"
if last_exc and str(last_exc).startswith("calibration_unconverged:"):
    skip_reason = "calibration_unconverged"

return SkipResult(
    scenario_id=scenario_id,
    error_log=[str(h.exception) for h in history if h.exception],
    skip_reason=skip_reason,
)
```

(Exact location depends on retry_loop.py:309-314 / 319-370 layout — read those lines and slot in the skip_reason logic at SkipResult construction.)

- [ ] **Step 6.5: Run the integration test, verify pass**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular/test_retry_loop.py::TestCalibrationInRetryLoop -v
```

Expected: PASS.

- [ ] **Step 6.6: Write the convergence test**

Add to `TestCalibrationInRetryLoop`:

```python
    def test_retry_recovers_after_calibration_feedback(self, ...):
        """If LLM accepts the suggested sigma on attempt 2, retry_loop returns
        RetryLoopResult(success=True, attempts=2)."""
        # Construct 2 scripts: first under-declares sigma=2; second uses ~50.
        # ... assert: result.success and result.attempts == 2
```

- [ ] **Step 6.7: Write the no-trigger test**

```python
    def test_no_calibration_trigger_when_no_structural_measure_has_sigma(self, ...):
        """If declarations have NO structural measure with declared sigma,
        calibration returns passed=True immediately and retry budget is unused."""
        # ... assert: result.success and result.attempts == 1
```

- [ ] **Step 6.8: Run the full suite — no regressions**

```bash
~/miniconda3/envs/chart/bin/python -m pytest pipeline/phase_2/tests/modular -x -q
```

Expected: ≥367 passed.

- [ ] **Step 6.9: Commit (closes spec commit 4 — main feature now live)**

```bash
git add pipeline/phase_2/orchestration/retry_loop.py pipeline/phase_2/tests/modular/test_retry_loop.py
git commit -m "feat(calibration): wire check_sigma_calibration into Loop A retry"
```

---

## Task 7: Update `FAILURE_MECHANISMS.md` §7.1

**Files:**
- Modify: `pipeline/phase_2/FAILURE_MECHANISMS.md`

- [ ] **Step 7.1: Mark §7.1 as ✓ implemented**

In `pipeline/phase_2/FAILURE_MECHANISMS.md`, find `### 7.1 机制 1 的根没动` and update to:

```markdown
### 7.1 机制 1 的根（已修复 → 见 calibration.py）

Path A 的 heuristic prompt 是 prevention layer。**实际修复**机制 1 的根
靠的是 [orchestration/calibration.py](orchestration/calibration.py)：
Loop A 的 LLM-in-loop dry-run sigma 校准。算法：

1. Loop A exec 成功后，engine 用 `realism_config=None` 做 full-N replay。
2. 对每个声明 sigma 的 structural measure，量 empirical residual std。
3. 若任一 measure 的 ratio ≥ 0.2，构造 typed feedback 把 suggested sigma
   送回 LLM（同 retry 通道）。
4. 3 轮未收敛 → `SkipResult(skip_reason="calibration_unconverged")`，
   每行写入 `output/agpds/<batch>/skipped.jsonl`。

实测 V2 数据：[FAILURE_MECHANISMS.md §8](#8-实测数据3-way-对照) 的 -v2
基准上加 calibration 后，residual_* ratio median 应从 2.5 降到 < 0.2。
```

- [ ] **Step 7.2: Commit**

```bash
git add pipeline/phase_2/FAILURE_MECHANISMS.md
git commit -m "docs(phase_2): mark §7.1 as implemented (calibration.py)"
```

---

## Task 8: Production validation on `pingyue-samples-gemini-pathA`

Per spec §7 V2: re-run Stage 1 + Stage 2 on the same 10 scenarios with calibration enabled, compare to the previous `pingyue-samples-gemini-pathA`.

- [ ] **Step 8.1: Run Stage 1 with calibration**

```bash
~/miniconda3/envs/chart/bin/python -m pipeline.agpds_generate \
    --provider gemini --model gemini-3.1-pro-preview \
    --batch-name pingyue-samples-gemini-pathA-calibrated \
    --category 3 --count 10 \
    --scenario-source cached_strict --seed 42 2>&1 | tee /tmp/pathA_cal_stage1.log
```

Expected: 10/10 declarations saved OR some in `skipped.jsonl` with `skip_reason="calibration_unconverged"`.

- [ ] **Step 8.2: Run Stage 2**

```bash
~/miniconda3/envs/chart/bin/python -m pipeline.agpds_execute \
    --input-dir output/agpds/pingyue-samples-gemini-pathA-calibrated \
    --output-dir output/agpds/pingyue-samples-gemini-pathA-calibrated 2>&1 | tail -20
```

- [ ] **Step 8.3: Run diff script**

```bash
~/miniconda3/envs/chart/bin/python <<'EOF'
import json, re, os, statistics
from collections import Counter

def collect(batch):
    s = json.load(open(f'output/agpds/{batch}/validation_summary.json'))
    bucket = Counter()
    ratios = []
    for entry in s:
        for f in entry['failures']:
            for p in ['ks_','residual_','group_dep_','marginal_','orthogonal_']:
                if f['name'].startswith(p):
                    bucket[p.rstrip('_')] += 1
                    break
            if f['name'].startswith('residual_'):
                m = re.search(r'ratio=([\d.]+)', f['detail'])
                if m: ratios.append(float(m.group(1)))
    return bucket, ratios

old_b, old_r = collect('pingyue-samples-gemini-pathA')
new_b, new_r = collect('pingyue-samples-gemini-pathA-calibrated')
print(f'{"":<12} {"pathA":>8} {"calibrated":>11}')
for k in sorted(set(old_b)|set(new_b)):
    print(f'{k:<12} {old_b.get(k,0):>8} {new_b.get(k,0):>11}')
print(f'{"residual:":<12} median={statistics.median(old_r) if old_r else 0:.2f} -> '
      f'{statistics.median(new_r) if new_r else 0:.2f}, '
      f'max={max(old_r,default=0):.2f} -> {max(new_r,default=0):.2f}')
EOF
```

Expected delta:
- residual_* median ratio: 2.49 → **<0.2** (or zero failures if all calibrated)
- residual_* count: 15 → **≤ 3**
- passed (full pass): 0/10 → **≥3/10**

- [ ] **Step 8.4: Decide on next steps**

If targets met → consider mechanism 1 closed. Mark in plan + commit final FAILURE_MECHANISMS.md update.

If targets NOT met → investigate `skipped.jsonl` to see if LLM is failing convergence; may need to bump retry budget from 3 to 5 (spec §10 fallback).

---

## Self-Review Notes

- **Spec coverage:** every section of [the approved spec](/home/dingcheng/.claude/plans/pipeline-agpds-execute-py-soft-warning-temporal-rivest.md) maps to a task: §1→T2, §2→T4, §3→T6, §4→T5, §5→T5, §6→T1-T7, §7 V1→T3.4 + T6.8, V2→T8, V3→manual exercise post-T8. §8 non-goals respected (validator + Loop B + prompt all untouched).
- **Placeholder scan:** Step 6.1 + 6.6 + 6.7 say "..." for the LLM mock fixture body — this is intentional skeleton (the helper is generic; engineer fills in with the minimal-declaration template from Task 2). All other steps are fully concrete.
- **Type consistency:** `CalibrationFailure.suggested_sigma` (T1) used identically in T2-T4. `SkipResult.skip_reason` (T5) consistent across consumer sites (T5 + T6).
- **No backwards-compat hacks.** No "TODO". No "implement later". All commit messages concrete.
