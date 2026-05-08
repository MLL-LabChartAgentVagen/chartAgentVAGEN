## 4. Remaining Stubs & Known Limitations

### 4.0 Status (2026-05-07)

All 9 of the 10 documented Phase 2 stubs (IS-1..IS-4, IS-6 token-budget half, DS-1..DS-4) shipped between 2026-04-22 and 2026-05-07. The full adversarial audit in [POST_STUB_AUDIT_FINDINGS.md](POST_STUB_AUDIT_FINDINGS.md) — H1, M1–M5, L1–L5 — is closed (commits `6f64495`, `893e7e9`, `72ddb0f`, `2dbec22`).

Decisions and per-stub records:
- Authoritative decisions: [stub_analysis/phase_2_spec_decisions.md](stub_analysis/phase_2_spec_decisions.md), [stub_analysis/stub_blocker_decisions.md](stub_analysis/stub_blocker_decisions.md)
- Implementation walkthroughs: [stub_implementation/](stub_implementation/) (one file per stub)
- Post-implementation audit fixes: [fixes/](fixes/)

### 4.1 Resolved stubs

| ID | Feature | Source location | Resolution doc | Audit-fix doc |
|----|---------|-----------------|----------------|---------------|
| IS-1 | Mixture distribution sampling | [phase_2/engine/measures.py](../phase_2/engine/measures.py) `_sample_stochastic` dispatch + `_sample_mixture` | [stub_implementation/IS-1_DS-3_mixture.md](stub_implementation/IS-1_DS-3_mixture.md) | [fixes/M1_WIDEN_VARIANCE_AUTO_BINDING.md](fixes/M1_WIDEN_VARIANCE_AUTO_BINDING.md) (`893e7e9`) |
| IS-2 | Dominance shift validation | [phase_2/validation/pattern_checks.py](../phase_2/validation/pattern_checks.py) `check_dominance_shift` | [stub_implementation/IS-2_dominance_shift.md](stub_implementation/IS-2_dominance_shift.md) | [fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md](fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md) (`6f64495`), [fixes/M2_M3_DEFENSIVE_GUARDS.md](fixes/M2_M3_DEFENSIVE_GUARDS.md) (`72ddb0f`) |
| IS-3 | Convergence validation | [phase_2/validation/pattern_checks.py](../phase_2/validation/pattern_checks.py) `check_convergence` | [stub_implementation/IS-3_convergence.md](stub_implementation/IS-3_convergence.md) | [fixes/M2_M3_DEFENSIVE_GUARDS.md](fixes/M2_M3_DEFENSIVE_GUARDS.md) (`72ddb0f`) |
| IS-4 | Seasonal anomaly validation | [phase_2/validation/pattern_checks.py](../phase_2/validation/pattern_checks.py) `check_seasonal_anomaly` | [stub_implementation/IS-4_seasonal_anomaly.md](stub_implementation/IS-4_seasonal_anomaly.md) | [fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md](fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md) (`6f64495`), [fixes/AUDIT_CLEANUP_M4_M5_L1_L5.md](fixes/AUDIT_CLEANUP_M4_M5_L1_L5.md) (`2dbec22`) |
| IS-6 (token budget) | Per-scenario token budget on retry loop | [phase_2/orchestration/sandbox.py](../phase_2/orchestration/sandbox.py) `run_retry_loop(token_budget=…)` + [phase_2/orchestration/llm_client.py](../phase_2/orchestration/llm_client.py) `LLMResponse.token_usage` | [stub_implementation/IS-6_token_budget.md](stub_implementation/IS-6_token_budget.md) | [fixes/AUDIT_CLEANUP_M4_M5_L1_L5.md](fixes/AUDIT_CLEANUP_M4_M5_L1_L5.md) (`2dbec22`) |
| DS-1 | Censoring injection (left/right/interval, NaN marker) | [phase_2/engine/realism.py](../phase_2/engine/realism.py) `inject_censoring` | [stub_implementation/DS-1.md](stub_implementation/DS-1.md) | — |
| DS-2 | 4 pattern injectors (`ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`) | [phase_2/engine/patterns.py](../phase_2/engine/patterns.py) `inject_*` (4 functions) | [stub_implementation/DS-2.md](stub_implementation/DS-2.md), [stub_implementation/IS-2_dominance_shift.md](stub_implementation/IS-2_dominance_shift.md), [stub_implementation/IS-3_convergence.md](stub_implementation/IS-3_convergence.md), [stub_implementation/IS-4_seasonal_anomaly.md](stub_implementation/IS-4_seasonal_anomaly.md) | [fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md](fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md), [fixes/M2_M3_DEFENSIVE_GUARDS.md](fixes/M2_M3_DEFENSIVE_GUARDS.md) |
| DS-3 | Mixture KS test | [phase_2/validation/statistical.py](../phase_2/validation/statistical.py) `_MixtureFrozen` + `_expected_cdf_mixture` | [stub_implementation/IS-1_DS-3_mixture.md](stub_implementation/IS-1_DS-3_mixture.md) | — |
| DS-4 | Multi-column group dependency `on` | [phase_2/sdk/relationships.py](../phase_2/sdk/relationships.py) (nested-dict spec) + [phase_2/engine/skeleton.py](../phase_2/engine/skeleton.py) `sample_dependent_root` (N-deep walker) | [stub_implementation/DS-4.md](stub_implementation/DS-4.md) | [fixes/AUDIT_CLEANUP_M4_M5_L1_L5.md](fixes/AUDIT_CLEANUP_M4_M5_L1_L5.md) (`2dbec22`) |

### 4.2 Remaining limitations

The items below are intentional non-stubs or accepted limitations — none block production use.

#### `scale` Kwarg on `add_measure` (IS-5 / M?-NC-scale) — not restored
- **Location:** [phase_2/sdk/columns.py](../phase_2/sdk/columns.py) (`TODO [M?-NC-scale]` marker), mirrored by absence in [phase_2/orchestration/prompt.py](../phase_2/orchestration/prompt.py).
- **Behavior:** `add_measure(name, family, param_model)` does not accept a `scale` keyword. Passing `scale=...` raises `TypeError`. The prompt does not advertise the kwarg.
- **Decision:** Per [stub_analysis/phase_2_spec_decisions.md §IS-5](stub_analysis/phase_2_spec_decisions.md), `scale` is **not restored**. The spec never defined `scale` semantics; the previous silent no-op misled LLMs into burning retry budget on a dead parameter. Current `TypeError` is the correct defensive behavior.
- **Related fixes:** [fixes/PROMPT_TRUTH_AND_DIVZERO_GUARD.md](fixes/PROMPT_TRUTH_AND_DIVZERO_GUARD.md), [fixes/GPT_FAILURE_ROUND_3_FIXES.md](fixes/GPT_FAILURE_ROUND_3_FIXES.md).
- **To unstub (if ever required):** define a scaling mechanism, then restore the kwarg in `sdk/columns.py` and re-add it to the `add_measure` signature shown in `orchestration/prompt.py`. Grep `TODO [M?-NC-scale]` for both sites.

#### M3 Multi-Error Compound Exception (M3-NC-3) — deferred
- **Location:** [phase_2/sdk/simulator.py](../phase_2/sdk/simulator.py) (`TODO [M3-NC-3]` comment, ~lines 32–36).
- **Behavior:** The sandbox catches one exception per execution; multiple simultaneous SDK validation errors (e.g. two bad effects + a cycle) are surfaced one per retry attempt.
- **Status:** Functional and acceptable within the default `max_retries=3` budget — the **token-budget half of IS-6 has shipped** (see §4.1). Multi-error accumulation was deferred per [stub_analysis/phase_2_spec_decisions.md §IS-6](stub_analysis/phase_2_spec_decisions.md) pending A/B-test evidence that compound exceptions help LLM correction.
- **To fix:** Collect validation errors into a compound exception in M1 (opt-in `ValidationContext(accumulate=True)` per the decisions doc).

#### `inject_dirty_values` Primary-Key Protection Gap
- **Location:** [phase_2/engine/realism.py](../phase_2/engine/realism.py) `inject_dirty_values`.
- **Behavior:** `inject_dirty_values` iterates *all* categorical columns including roots and may character-perturb a PK string ("Xiehe" → "Xeihe") when `dirty_rate > 0`. The companion missing-injection path **does** protect PK roots (resolved 2026-05-07 — see immediately below).
- **Status:** Open. Spec §2.1.1 protects "primary key" without scoping to missing-only, so this is a remaining spec violation. Tracked for a future round; closing it requires the same `protected_columns=` skip-set threading into `inject_dirty_values`.

#### ~~Primary-Key Protection in `set_realism` (REM-realism-pk-protection)~~ — RESOLVED 2026-05-07
- **Resolution:** `_primary_key_columns(columns)` helper in `engine/realism.py` identifies categorical roots (`type=='categorical'` AND `parent is None`); `inject_realism` forwards them as `protected_columns=` to `inject_missing_values`, which forces those columns' mask cells to `False` before applying. The xfail decorator on `tests/modular/test_realism.py::TestPrimaryKeyProtection::test_primary_key_categorical_root_never_nulled_at_rate_one` was removed; three complementary tests added (intermediate rate `0.5`, child categorical NOT protected, multiple group roots all protected) plus a regression guard that direct callers of `inject_missing_values` without `protected_columns` keep the all-cells-masked default.
- **Out of scope:** see "`inject_dirty_values` Primary-Key Protection Gap" above.
