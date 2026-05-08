# Phase 2 Test-Robustness — Future Hardening Plan (2026-05-07)

## Why this exists

The first audit ([`TEST_AUDIT_2026-05-07.md`](TEST_AUDIT_2026-05-07.md)) closed 15 distinct spec-promise gaps and added 79 net new tests. After completion, an honest self-review surfaced four classes of weakness that the current suite still has:

- **Statistical tests are seed-specific.** Chi², mixture proportions, KS p-value extraction, the autofix healing roundtrip — every one passes under the *single* seed I picked. A bug that breaks under most seeds but happens to work under that one slips through.
- **Boundary-precision tests were deferred.** L3 thresholds (`z >= 2.0`, `|after-before|/before > 0.15`, `p > 0.05`, multi-parent deviation `0.10`) are tested only with comfortably-clear fixtures. An off-by-one on any operator (`>` vs `>=`) is invisible to the current suite for those thresholds.
- **Auto-fix healing is only proven for `widen_variance`.** `amplify_magnitude` (used for `outlier_*` and `trend_*`) and `reshuffle_pair` (used for `orthogonal_*`) have unit-level override-accumulation tests, but no end-to-end "failure → strategy → next-attempt PASSES" verification. A sign bug in either strategy would slip through.
- **The §2.7 self-correction loop is tested only with hand-crafted exceptions.** Existing `test_retry_feedback.py` exercises the loop with `def build_fact_table(): raise ValueError(...)` — the exception is *synthesised in the script*, not raised by a real SDK call against a real declaration error. The realistic chain (LLM emits SDK-valid Python → SDK validation raises `WeightLengthMismatchError` from inside the sandbox → traceback fed back → LLM fixes → second sandbox run produces a clean DataFrame → validator passes) is unproven.

Each section below is scoped to be picked up cold by a future implementer. The plan is purely additive — none of these touch source code. None invalidates the existing 353-test green baseline.

---

## (a) Seed-parametrized statistical tests

### Why

Every test that draws random samples and asserts a statistical property currently does so with a single hard-coded seed. The mental model "I picked a seed where the math works" is exactly the corner cut the audit was trying to remove. With `pytest.mark.parametrize("seed", [...])` over 5–10 seeds per test, a bug that fails on ≥1/10 seeds becomes visible.

The pattern needs to be applied with care. Statistical tests that pass at α=0.05 will produce false positives roughly once every 20 seeds *for correct code*, so the right contract is one of:

- **Strict-pass band**: pick seeds in advance (no cherry-picking after seeing results), use the spec threshold (`p > 0.05`), accept that with 10 seeds expected false-positive count is 0.5. If a chosen seed turns out to be flaky on the *current* impl, document it and move on; don't expand the pre-chosen list to find a kinder seed.
- **Majority-pass band**: assert that ≥k of n seeds pass, where k is chosen to give a much wider confidence margin than the spec threshold. Less rigorous but tolerates statistical noise.

The strict-pass band is the right default; majority-pass is a fallback for tests where individual-seed failure is genuinely unavoidable (e.g., low-N KS).

### Files and tests

- [`tests/modular/test_validation_structural.py`](../tests/modular/test_validation_structural.py) — `TestCheckOrthogonalIndependence::test_passes_for_seeded_independent_data`. Parametrize `seed in [42, 7, 100, 2024, 31415]`, assert `p > 0.05` for each. The current single-seed test stays as a regression anchor.
- [`tests/modular/test_engine_mixture.py`](../tests/modular/test_engine_mixture.py) — `TestComponentProportions::test_two_component_proportions_match_declared_weights` and `test_three_component_proportions_match_declared_weights`. Parametrize seeds; widen the binomial CI band to a Wilson-score interval at α=0.01 if needed so cross-seed false positives stay rare.
- [`tests/modular/test_validation_statistical_mixture.py`](../tests/modular/test_validation_statistical_mixture.py) — `TestMixtureKsPValueExtraction::test_passing_check_has_p_value_above_005` and `test_failing_check_has_p_value_at_or_below_005`. Parametrize sample seeds.
- [`tests/modular/test_validation_autofix.py`](../tests/modular/test_validation_autofix.py) — `TestGenerateWithValidationHealingRoundtrip::test_widen_variance_actually_heals_ks_failure_on_retry`. Parametrize `base_seed`. The healing roundtrip should converge under any seed that produces a KS-failing first attempt; if it doesn't, the bug is in `widen_variance`.

### Sketch (for one test)

```python
@pytest.mark.parametrize("seed", [42, 7, 100, 2024, 31415])
def test_passes_for_seeded_independent_data(self, seed):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "root_a": rng.choice(["X", "Y"], size=400),
        "root_b": rng.choice(["K", "L"], size=400),
    })
    meta = {
        "dimension_groups": {
            "g1": {"hierarchy": ["root_a"]},
            "g2": {"hierarchy": ["root_b"]},
        },
        "orthogonal_groups": [{"group_a": "g1", "group_b": "g2"}],
    }
    checks = check_orthogonal_independence(df, meta)
    assert checks[0].passed
    p_val = _extract_chi2_p(checks[0].detail)
    assert p_val > 0.05
```

### Verification

Run each parametrized file, confirm every seed instance passes. If any single seed fails, do **not** drop it — investigate whether it reveals a real bug. After parametrization, the chi² flake-loop sanity check (50× rerun) becomes redundant for those tests but remains useful as a meta-stability check.

---

## (b) Boundary-precision tests for L3 thresholds

### Why

The audit deferred z=1.99 vs z=2.01 (and friends) because the existing suite already covers each pattern's pass and fail branches. But pass-far-above-threshold + fail-far-below-threshold tells you nothing about which side of the boundary the operator falls on. A regression that flipped `z >= 2.0` to `z > 2.0` would silently break every LLM-generated outlier whose actual z is *exactly* 2.0 — those are common because injection scaling targets the threshold.

The convergence `>=` vs `>` mutation test (added in the prior round, see [`TEST_AUDIT_2026-05-07.md`](TEST_AUDIT_2026-05-07.md) Fix 2) is the template: replicate the validator's arithmetic in-test to obtain the bit-identical float, feed it as the threshold, assert pass; then add an epsilon and assert fail. Apply this pattern to every L3 threshold.

### Thresholds to pin

| Validator | Threshold (spec §2.6 L3) | File | Sketch |
|-----------|---------------------------|------|--------|
| `check_outlier_entity` | `z >= 2.0` | `tests/modular/test_engine_patterns.py` | Construct df where target subset has mean = ref_mean + 2.0 * ref_std (z=2.0 exactly), assert pass; nudge by -ε in target mean, assert fail. |
| `check_trend_break` | `|after-before|/before > 0.15` | `tests/modular/test_engine_patterns.py` | Construct df where post-mean / pre-mean = 1.15 exactly, assert *fail* (strict `>`); 1.15 + ε → pass. |
| `check_orthogonal_independence` | `p > 0.05` | `tests/modular/test_validation_structural.py` | Harder — p is computed by `scipy.stats.chi2_contingency`, not an in-test formula. Use a hand-tuned contingency where p is just over/under 0.05 (extract via probe call, then inject ±ε rows to nudge across the boundary). Acceptable to loosen to "p just above 0.05 → pass; p just below → fail" without exact-equality. |
| `check_marginal_weights` | `max_deviation < 0.10` | `tests/modular/test_validation_structural.py` | Construct df where observed max deviation is exactly 0.10; assert behavior matches strict `<` (deviation == 0.10 must FAIL since the contract is `<`, not `<=`). |
| `check_structural_residuals` | `abs(residual_std - sigma) / sigma < 0.2` | `tests/modular/test_validation_statistical.py` | Same pattern. |
| `max_conditional_deviation` (multi-parent) | `< 0.10` | `tests/modular/test_sdk_relationships_multi_parent.py` | Same pattern; existing tests use far-extreme values (0.0 and 0.5). |

### Files

- [`tests/modular/test_engine_patterns.py`](../tests/modular/test_engine_patterns.py) — extend `TestInjectOutlierEntity` (or add it if absent — confirm against the file) and `TestInjectTrendBreak` with boundary cases.
- [`tests/modular/test_validation_structural.py`](../tests/modular/test_validation_structural.py) — extend `TestCheckMarginalWeights` and `TestCheckOrthogonalIndependence` with boundary cases.
- [`tests/modular/test_validation_statistical.py`](../tests/modular/test_validation_statistical.py) — boundary case for `check_structural_residuals`.
- [`tests/modular/test_sdk_relationships_multi_parent.py`](../tests/modular/test_sdk_relationships_multi_parent.py) — boundary case for `max_conditional_deviation`.

### Sketch (for one threshold — outlier z=2.0)

```python
def test_outlier_z_at_exact_threshold_passes(self):
    """z >= 2.0 is the spec L3 contract. Construct data where the target
    subset's z is exactly 2.0 and assert pass; nudge -epsilon, assert fail.
    Mutation guard: a regression `z > 2.0` would flip the equality test."""
    rng = np.random.default_rng(0)
    base = rng.normal(0.0, 1.0, 1000)
    ref_mean = float(base.mean())
    ref_std = float(base.std(ddof=1))

    # Construct a target subset whose mean is exactly ref_mean + 2.0 * ref_std.
    target_size = 50
    target_value = ref_mean + 2.0 * ref_std
    df = pd.DataFrame({
        "flag": [True] * target_size + [False] * (1000 - target_size),
        "cost": np.r_[
            np.full(target_size, target_value),
            base[:1000 - target_size],
        ],
    })
    pattern = {"target": "flag == True", "col": "cost", "params": {"z_score": 2.0}}
    chk = check_outlier_entity(df, pattern)
    assert chk.passed, f"z=2.0 must pass under `>=`; got {chk.detail}"

    # Nudge target mean down by 1% — z falls below 2.0 → must fail.
    df.loc[df["flag"], "cost"] = target_value - 0.01 * ref_std
    chk_fail = check_outlier_entity(df, pattern)
    assert not chk_fail.passed
```

### Verification

After each boundary test, perform the same kind of mutation test the convergence fix used: surgically flip the validator's operator (e.g., `>=` → `>`) in a copy of the source, re-run the boundary test, confirm it fails. If it doesn't fail, the boundary test isn't actually pinning the operator.

---

## (c) Healing roundtrips for `amplify_magnitude` and `reshuffle_pair`

### Why

Spec §2.6 promises: *"Auto-fix applies targeted parameter adjustments — correlation relaxation, variance widening, **pattern amplification** — and re-runs the engine."* The previous audit's T1.4 added a healing roundtrip for `widen_variance` (`ks_*` failures), proving the *full* chain: validation failure → strategy mutates override → next attempt observes the override → next attempt passes. But two of the three live strategies remain proven only at the override-accumulation level:

- `amplify_magnitude` ([`validation/autofix.py:147`](../validation/autofix.py#L147)) — used for `outlier_*` and `trend_*` failures. It must mutate the *pattern's* `z_score` / `magnitude` parameter so the engine re-injects with stronger amplitude.
- `reshuffle_pair` ([`validation/autofix.py:206`](../validation/autofix.py#L206)) — used for `orthogonal_*` failures. It must flag a column for reshuffle so `generate_measures` ([`engine/measures.py:603-606`](../engine/measures.py#L603)) permutes the column and breaks unwanted correlation.

A sign bug in either (e.g., `factor /= 1.3` instead of `*= 1.3`) is invisible to the current suite.

### Files and approach

[`tests/modular/test_validation_autofix.py`](../tests/modular/test_validation_autofix.py) — append two classes mirroring `TestGenerateWithValidationHealingRoundtrip::test_widen_variance_actually_heals_ks_failure_on_retry`. Use the *real* `SchemaAwareValidator` (no monkeypatching) and a stateful `build_fn` whose attempt-2 output explicitly reflects the override.

#### `TestAmplifyMagnitudeHealing`

```python
class TestAmplifyMagnitudeHealing:
    def test_amplify_magnitude_heals_outlier_failure_on_retry(self):
        """Attempt 1: target subset z = 1.5 — fails L3 outlier check (needs >=2.0).
        autofix's amplify_magnitude bumps the pattern's z_score override.
        Attempt 2: build_fn reads the override, injects with the higher z,
        the validator now reports passed=True."""
        meta = self._meta_with_outlier_pattern_declared()
        patterns = [{"type": "outlier_entity",
                     "target": "flag == True", "col": "cost",
                     "params": {"z_score": 2.0}}]
        state = {"attempt": 0, "overrides_seen": []}

        def build_fn(seed, overrides):
            state["attempt"] += 1
            state["overrides_seen"].append(deepcopy(overrides))
            rng = np.random.default_rng(seed)
            base = rng.normal(0.0, 1.0, 1000)
            ref_std = float(base.std(ddof=1))

            # Pattern amplification: read overrides["patterns"][0]["params"]["z_score"]
            # if present, else fall back to declared 1.5 (deliberately weak).
            applied_z = 1.5
            if overrides and "patterns" in overrides:
                applied_z = max(applied_z, overrides["patterns"][0]["params"]["z_score"])

            df = pd.DataFrame({
                "flag": [True] * 50 + [False] * 950,
                "cost": np.r_[np.full(50, applied_z * ref_std), base[:950]],
            })
            return df, meta

        df, _, report = generate_with_validation(
            build_fn=build_fn, meta=meta, patterns=patterns,
            base_seed=42, max_attempts=3,
            auto_fix={"outlier_*": amplify_magnitude},
        )

        assert state["attempt"] == 2, f"expected healing on attempt 2, got {state['attempt']}"
        assert report.all_passed
        # The override delivered to attempt 2 carries amplified z_score.
        assert state["overrides_seen"][1] is not None
        assert "patterns" in state["overrides_seen"][1]
```

The same shape applies to `trend_*` (use a `trend_break` pattern with magnitude=0.10 first, amplified to >0.15 on retry).

#### `TestReshufflePairHealing`

`reshuffle_pair` writes `overrides["reshuffle"] = [col_name]`. `generate_measures` ([`engine/measures.py:603`](../engine/measures.py#L603)) reads that key and applies `rng.permutation(rows[col_name])`. The healing test must therefore call **real `run_pipeline`** (not a synthesised `build_fn`) so the engine-side reshuffle actually fires.

```python
class TestReshufflePairHealing:
    def test_reshuffle_pair_heals_orthogonal_failure_on_retry(self):
        """Attempt 1: declared cross-group dependent on hospital — chi² fails.
        autofix's reshuffle_pair flags the offending column.
        Attempt 2: engine permutes the column, the chi² test now passes."""
        # Use real run_pipeline; build_fn calls it with the column registry
        # plus the override. After permutation the marginals are preserved
        # but the contingency table de-correlates.
        ...
```

### Verification

For each of the three strategies (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`), do a mutation test: monkeypatch the strategy's mutation operator (multiplication → division, append → no-op), confirm the healing test flips to a failure. This is the same mutation-testing pattern as the convergence fix.

---

## (d) Real LLM-emits-broken-SDK-script integration test

### Why

[`tests/test_retry_feedback.py`](../tests/test_retry_feedback.py) exercises `format_error_feedback` and `run_retry_loop` with *synthesised* exceptions:

```python
return LLMResponse(
    code="def build_fact_table():\n    raise ValueError('bug_attempt_1')\n",
    ...
)
```

The "broken script" raises a stock `ValueError` — it never reaches the SDK at all. So the loop is proven to *transport* exceptions, but not to integrate with the SDK's real validation surface. The realistic §2.7 path is:

1. LLM returns Python that *uses* `FactTableSimulator` and looks plausible at first glance.
2. The script reaches `sim.add_category(...)` with a *real* SDK contract violation (e.g., `weights=[0.5, 0.6]` against `values=["A","B","C"]` → `WeightLengthMismatchError`).
3. The sandbox catches the typed exception with file/line info from the sandboxed exec.
4. `format_error_feedback` formats the real traceback into the user prompt.
5. The mocked LLM "fix" returns a corrected script.
6. The second sandbox run produces a non-empty DataFrame.
7. `SchemaAwareValidator` reports `all_passed=True`.

This is the most valuable single integration test the suite is missing — it proves the full chain end-to-end, not by component.

### File

New file: `tests/test_self_correction_loop_real.py`. Top-level (not under `modular/`) because it spans SDK + sandbox + orchestration + validation.

### Sketch

```python
"""End-to-end §2.7 self-correction test using REAL SDK exceptions.

Mocks ONLY LLMClient.generate_code. Real execute_in_sandbox runs both
attempts. The broken first script triggers a real SDK contract violation
(WeightLengthMismatchError or InvalidParameterError); its traceback flows
through format_error_feedback into the second LLM call's user message;
the LLM "fix" produces a clean script whose generated DataFrame passes
SchemaAwareValidator.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from pipeline.phase_2.orchestration.retry_loop import orchestrate
from pipeline.phase_2.types import SkipResult
from pipeline.phase_2.validation.validator import SchemaAwareValidator


_BROKEN_CODE = '''
from pipeline.phase_2.sdk.simulator import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=200, seed=seed)
    # SDK violation: weights vector is one element short of values.
    sim.add_category(
        name="hospital",
        values=["A", "B", "C"],
        weights=[0.5, 0.5],   # length-2 vs values length-3 → WeightLengthMismatchError
        group="entity",
    )
    return sim.generate()
'''.strip()

_FIXED_CODE = '''
from pipeline.phase_2.sdk.simulator import FactTableSimulator

def build_fact_table(seed=42):
    sim = FactTableSimulator(target_rows=200, seed=seed)
    sim.add_category(
        name="hospital",
        values=["A", "B", "C"],
        weights=[0.4, 0.4, 0.2],
        group="entity",
    )
    sim.add_measure(
        name="revenue",
        family="gaussian",
        param_model={"mu": 100.0, "sigma": 10.0},
    )
    return sim.generate()
'''.strip()

_SCENARIO = {"scenario_id": "rt-001", "title": "Hospital", "target_rows": 200}


class TestRealSdkSelfCorrectionLoop:
    def test_broken_then_fixed_real_traceback_flows_through(self):
        client = MagicMock()
        client.generate_code.side_effect = [_BROKEN_CODE, _FIXED_CODE]

        # NO patch on execute_in_sandbox — real exec.
        result = orchestrate(_SCENARIO, llm_client=client, max_retries=3)

        # 1. Two LLM calls — initial + one retry — and result is not a SkipResult.
        assert client.generate_code.call_count == 2
        assert not isinstance(result, SkipResult)
        df, meta, _ = result

        # 2. The retry call's user-message contains the REAL SDK traceback.
        retry_user_arg = client.generate_code.call_args_list[1][0][1]
        assert "ORIGINAL CODE" in retry_user_arg
        assert "ERROR" in retry_user_arg
        assert "TRACEBACK" in retry_user_arg
        # The original broken `weights=[0.5, 0.5]` line must appear.
        assert "weights=[0.5, 0.5]" in retry_user_arg
        # The exception name from sdk/validation.py must appear.
        assert any(name in retry_user_arg
                   for name in ("WeightLengthMismatchError",
                                "InvalidParameterError"))
        # And the message must mention the actual constraint violation.
        assert ("length" in retry_user_arg.lower()
                or "weights" in retry_user_arg.lower())

        # 3. The fixed code's DataFrame is non-empty and the right shape.
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 200
        assert {"hospital", "revenue"}.issubset(df.columns)

        # 4. SchemaAwareValidator passes on the result.
        report = SchemaAwareValidator(meta).validate(df, patterns=[])
        assert report.all_passed, [(c.name, c.detail) for c in report.failures]
```

### Variants worth adding

- **Sandbox timeout case**: `_BROKEN_CODE` enters an infinite loop; the sandbox catches `TimeoutError`; the retry feedback mentions timeout; the LLM "fix" terminates correctly. Tests the timeout integration with the loop.
- **Multiple retry case**: `client.generate_code.side_effect = [_BAD1, _BAD2, _GOOD]`. Verify the second retry's user message contains *both* prior errors (the `PRIOR FAILED ATTEMPTS` accumulation `test_retry_feedback.py:108` already exercises this with synthetic errors — the variant proves it works with real SDK errors too).
- **Exhaustion case**: all three attempts fail with real SDK errors; assert `isinstance(result, SkipResult)` and that the skip log includes the typed exception class names.

### Verification

Run the new file individually first (it depends on real subprocess-y behavior of `execute_in_sandbox`, so it will be slower than other modular tests). Then run the full suite to confirm no regressions. As a sanity check, deliberately introduce a typo in `_FIXED_CODE` (e.g., `family="gausian"`) and verify the test fails with a clear pointer to the real SDK error — that proves the test is actually integrating with the SDK, not pattern-matching strings.

---

## Suggested execution order

1. **(a) seed parametrization** — smallest LOC, biggest immediate confidence boost. ~30 min.
2. **(b) boundary precision** — moderate LOC, surfaces likely operator regressions if any exist. ~1–2 hours.
3. **(c) healing roundtrips** — needs careful build_fn shaping per strategy. ~2–3 hours.
4. **(d) real-SDK self-correction integration** — most valuable, also most fragile because it depends on sandbox-traceback format. Save until last so the easier wins are banked first. ~2–4 hours.

Total estimate: one focused half-day per item, two days end-to-end if a single person picks up the whole batch.

## What this plan does NOT cover

Same scope discipline as the prior audit:

- Implementing missing source-side functionality (e.g., the xfail'd PK protection in `set_realism`). That's tracked in [`remaining_gaps.md`](remaining_gaps.md), not here.
- Re-auditing the codebase. The prior audit's out-of-scope list (boundary cases beyond the threshold-pinning above, predictor effect parametrizations, schema-metadata round-trip with downstream consumers) stays deferred.
- Mutation testing as a CI gate. The mutation tests recommended above for verification are local sanity checks, not automation.
