# Post-Stub Adversarial Audit — Findings

Cross-check performed after the M1-NC-* and M3-NC-3 stub workflow
shipped (DS-1, DS-2, IS-1, IS-2, IS-3, IS-4, DS-3, DS-4, IS-6
token-budget). Three pre-shipping artifacts were compared against
the actual live source:

- [pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md](stub_analysis/stub_gap_analysis.md)
- [pipeline/phase_2/docs/stub_analysis/stub_blocker_decisions.md](stub_analysis/stub_blocker_decisions.md)
- [pipeline/phase_2/docs/stub_implementation/](stub_implementation/) summaries

Implementations match their blueprints on every behavioral CONTRACT.
The findings below are real bugs, production-relevant gaps, or
documentation drift — listed in severity order.

---

## HIGH severity

### H1 — Temporal-coercion asymmetry in 3 pattern injectors  ✅ **RESOLVED** (commit `6f64495`)

[engine/patterns.py:226](engine/patterns.py#L226),
[:322](engine/patterns.py#L322), and
[:706](engine/patterns.py#L706) all called
`pd.to_datetime(df[temporal_col])` without `errors="coerce"`. Only
[`inject_convergence` at :582](engine/patterns.py#L582) coerced.
Meanwhile EVERY paired validator coerced
([pattern_checks.py:167, 284, 362, 449](validation/pattern_checks.py#L167)).

**Why this was a bug:** A scenario whose generated DataFrame had any
unparseable temporal cell would crash at `inject_trend_break`,
`inject_dominance_shift`, or `inject_seasonal_anomaly` with a stock
pandas `DateParseError`. The §2.7 retry loop would misattribute the
crash to "bad pattern config" and ask the LLM to fix the pattern,
when the actual problem was upstream. The matching validator would
have returned `Check(passed=False, detail=...)` cleanly.

**Resolution:** Added `errors="coerce"`, `valid_mask`, all-NaT
defensive raise, and AND-in `valid_mask` to each downstream mask at
all three sites. Added `TestTemporalCoercionRobustness` regression
class with garbled-temporal fixture. Full writeup at
[docs/fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md](fixes/H1_TEMPORAL_COERCION_ASYMMETRY.md).

---

## MEDIUM severity

### M1 — Mixture `widen_variance` opt-out is inert in production  ✅ **RESOLVED** (commit `893e7e9`)

[pipeline.py:27, 76, 138, 262](pipeline.py#L27) accepts `auto_fix`
from the user but never auto-binds
`partial(widen_variance, columns=meta["columns"])`. Without that
kwarg the opt-out at
[autofix.py:112-120](validation/autofix.py#L112-L120) never fires for
mixture columns. Any caller wiring `auto_fix={"ks_*": widen_variance}`
(the natural pattern, advertised in the autofix docstring at
[:99](validation/autofix.py#L99)) will have `widen_variance` write
`overrides["measures"][col]["sigma"]` that `_sample_mixture` then
silently `del`s at [engine/measures.py:440](engine/measures.py#L440).
The retry loop spins for `max_attempts` without actually changing
the mixture params.

**Resolution:** Auto-bound `columns=meta["columns"]` at the dispatch
site in `generate_with_validation` via a new `_call_strategy` helper
that detects raw `widen_variance` (or unbound `functools.partial` of
it) and injects columns automatically. User-supplied partials with
explicit `columns=` bindings are respected. Strategy contract for
`amplify_magnitude` / `reshuffle_pair` / custom user strategies is
unchanged. Added `TestGenerateWithValidationMixtureOptOut` regression
class (3 tests) covering raw mixture, raw non-mixture, and
explicit-partial paths. Full writeup at
[docs/fixes/M1_WIDEN_VARIANCE_AUTO_BINDING.md](fixes/M1_WIDEN_VARIANCE_AUTO_BINDING.md).

### M2 — `inject_dominance_shift` adds an undocumented "positive_floor"  ✅ **RESOLVED** (commit pending)

[engine/patterns.py:352-356](engine/patterns.py#L352-L356) adds
`max(|peer_max|*0.1, 1.0)` when `peer_std<=0`, else `1e-9`. Decisions
§DS-2
([stub_blocker_decisions.md:622-624](stub_analysis/stub_blocker_decisions.md#L622-L624))
specify only `shift = peer_max + magnitude*peer_std - mean(post_split)`.
The floor materially changes results when `magnitude=0` or peers are
constant.

**Resolution:** Kept the floor (it prevents spurious validator failures
in the two edge cases where the naive formula yields a tie:
zero-variance peers and caller-supplied `magnitude=0`). Amended
`stub_blocker_decisions.md §DS-2` to authorize the two-tier floor and
document its rationale (strict dominance for deterministic rank-flip).
Full writeup at
[docs/fixes/M2_M3_DEFENSIVE_GUARDS.md](fixes/M2_M3_DEFENSIVE_GUARDS.md).

### M3 — `inject_convergence` clips `factor` to `[0, 1]`  ✅ **RESOLVED** (commit pending)

[engine/patterns.py:615-617](engine/patterns.py#L615-L617) clips;
spec pseudocode at
[stub_blocker_decisions.md:626-629](stub_analysis/stub_blocker_decisions.md#L626-L629)
does not. The clip is *safer* (prevents extrapolation past the mean
for `pull_strength>1`) but unauthorized by the decisions doc.

**Resolution:** Kept the clip — without it the injector would push
target rows to the opposite side of `global_mean` for `pull_strength>1`,
*increasing* inter-group variance and undermining the paired
`check_convergence` validator. Amended `stub_blocker_decisions.md §DS-2`
to mark the `[0, 1]` clip as required (not optional) and document the
"injector must agree with validator" rationale. Full writeup at
[docs/fixes/M2_M3_DEFENSIVE_GUARDS.md](fixes/M2_M3_DEFENSIVE_GUARDS.md).

### M4 — Mixture validator rejects `np.integer` weights but accepts `np.floating`

[sdk/validation.py:370](sdk/validation.py#L370):
`not isinstance(w, (int, float, np.floating))` excludes `np.int64` /
`np.int32`. The sampler at
[engine/measures.py:448](engine/measures.py#L448) (`np.array(...,
dtype=float)`) would have accepted them. LLM-emitted code uses Python
literals so this rarely fires, but it is an asymmetric contract.

**Fix:** add `np.integer` to the isinstance tuple.

### M5 — IS-6 token-budget: missing docstring + missing unit test for `_extract_token_usage` exception path

[sandbox.py:683-689](orchestration/sandbox.py#L683-L689) does not
document the new `token_budget` / `initial_token_usage` kwargs in
its `Args:` block. Separately,
[llm_client.py:60-69](orchestration/llm_client.py#L60-L69)'s
`except Exception: return None` branch is exercised only via
integration; no unit test covers a getattr-raises shape.

**Fix:** add docstring lines (matches the existing prose for
`max_retries` / `timeout_seconds`) and a single unit test that
mocks an LLM response whose `usage` attribute access raises.

---

## LOW severity

### L1 — `check_seasonal_anomaly` uses `.std(ddof=0)` (population)

[pattern_checks.py:489](validation/pattern_checks.py#L489) uses
`ddof=0` while other variance computations in the same file default
to `ddof=1` (sample). Inconsistent within file. Population std
slightly inflates `z`; sample std would be more conservative.

### L2 — `GroupDependency` docstring stale post-DS-4

[types.py:191-197](types.py#L191-L197) still says "Currently
restricted to single-column conditioning per assumption A7" — no
longer true after DS-4 widened the contract to N-deep nested
dicts. Behavior is fine; docstring is misleading.

### L3 — `DS-4.md` mis-states the deepcopy rationale

[stub_implementation/DS-4.md L97-99](stub_implementation/DS-4.md#L97-L99)
says the prior shape was "correct only for depth-2 dicts." Actually
the prior `{k: dict(v) for k, v in cw.items()}` was correct for the
single-parent shape that ever existed (depth-1 conditioning + leaf).
The deepcopy fix is needed for the new depth ≥ 2 shapes only — the
"only for depth-2" framing implies depth-3 was previously broken,
when in fact depth-3 didn't exist before DS-4.

### L4 — `DS-4.md` cites `_check_dependency_conflict` at wrong line span

DS-4.md says `~L385-410`; actual span is
[L372-395](sdk/relationships.py#L372-L395). Documentation drift only.

### L5 — IS-4 `anomaly_window` contradiction in decisions doc

[stub_blocker_decisions.md:288-292](stub_analysis/stub_blocker_decisions.md#L288-L292)
marks `anomaly_window` as "**optional**" in §IS-4; §4.2 L892 says
"**mandatory**". The implementation chose mandatory + defensive
last-10% fallback (the validator can still cope if the SDK gate is
bypassed in a test). Both readings are honored, but the decisions
doc itself is internally inconsistent.

### L6 — Confirmations (no bugs, recorded for completeness)

- `_resolve_first_dim_root` reuse across IS-2 / IS-3 / IS-4 verified
  clean — single helper at
  [pattern_checks.py:106-119](validation/pattern_checks.py#L106-L119),
  reused (not redefined) by all three validators that need it.
- `RetryLoopResult.skipped_reason` plumbing verified clean: counter
  seeded with `initial_token_usage`, no double-count, post-call guard
  ordering correct ([sandbox.py:738-740, 803-833](orchestration/sandbox.py#L738)).
- DS-4 single-parent path is byte-identical to v1 (regression test
  `TestSampleDependentRootSingleParentBackwardCompat` confirms). RNG
  draw ordering preserved.

---

## Recommended order of attack

1. **H1** — done (`6f64495`).
2. **M1** — fix the autofix wiring before mixture sees production
   traffic.
3. **M2 / M3** — pick "remove floor & clip" or "amend decisions doc";
   both are quick once the call is made. Coupled because both are
   "spec said X, code does X+ε" drift.
4. **M4, M5, all LOW** — opportunistic; bundle into a "doc + small
   fix" PR alongside any of the above.

---

## Origin classification — pre-existing vs. stub-introduced

| # | Finding | Origin | Why |
|---|---------|--------|-----|
| **H1** | Temporal-coercion asymmetry (3 sites) | **Mixed** — `inject_trend_break` site pre-existed the workflow; `inject_dominance_shift` (IS-2) and `inject_seasonal_anomaly` (IS-4) sites inherited the gap via the "mirrors `inject_trend_break`" template | Already resolved (`6f64495`). |
| **M1** | Mixture `widen_variance` opt-out is inert | **Introduced by IS-1+DS-3** (Step 6) | The opt-out kwarg + the mixture-skip branch were added BY the mixture stub; `pipeline.py`'s `auto_fix` plumbing was pre-existing but the new opt-out was never wired into it. The bug couldn't exist before mixture sampling was implemented. |
| **M2** | `inject_dominance_shift` undocumented positive_floor | **Introduced by IS-2** (Step 3) | `inject_dominance_shift` is a net-new function from IS-2. The floor at [engine/patterns.py:352-356](engine/patterns.py#L352-L356) was added with no spec sanction. |
| **M3** | `inject_convergence` clips `factor` | **Introduced by IS-3** (Step 4) | `inject_convergence` is net-new from IS-3. The clip at [:615-617](engine/patterns.py#L615-L617) was added (defensible defensive widening, unauthorized). |
| **M4** | Mixture validator accepts `np.floating` but rejects `np.integer` | **Introduced by IS-1+DS-3** (Step 6) | The mixture branch of `validate_param_model` at [sdk/validation.py:370](sdk/validation.py#L370) is net-new from the mixture stub. The asymmetric `isinstance` check is new. |
| **M5** | IS-6 token-budget docstring + missing `_extract_token_usage` exception-path test | **Introduced by IS-6 token-budget** (Step 8a) | The `token_budget` / `initial_token_usage` parameter surface and the `_extract_token_usage` helper are net-new from Step 8a. |
| **L1** | `check_seasonal_anomaly` uses `.std(ddof=0)` | **Introduced by IS-4** (Step 5) | The previous stub returned `passed=True` unconditionally with no std calculation. The whole z-score formula is net-new from IS-4. |
| **L2** | `GroupDependency` docstring stale | **Introduced by DS-4** (Step 7) | DS-4 widened the contract from single-column to N-deep nested dicts. The "Currently restricted to single-column" sentence was true before DS-4; the implementer didn't update it. |
| **L3** | `DS-4.md` mis-states deepcopy rationale | **Introduced by DS-4** (Step 7) | The summary doc was authored as part of the DS-4 ship. |
| **L4** | `DS-4.md` cites wrong line span | **Introduced by DS-4** (Step 7) | Same — summary drift authored at ship time, invalidated by surrounding edits. |
| **L5** | IS-4 `anomaly_window` "optional vs mandatory" contradiction | **Pre-existing** | The contradiction lives in [stub_blocker_decisions.md](stub_analysis/stub_blocker_decisions.md) itself (between §IS-4 and §4.2 Theme 2), which is an INPUT to the stub workflow. The IS-4 implementer had to pick a reading; the contradiction in the source doc predates implementation. |

### Distribution

- **1 pre-existing finding** (L5 — contradiction in the decisions doc).
- **1 mixed finding** (H1 — pre-existing seed in `inject_trend_break`,
  propagated by IS-2 and IS-4 via copy-paste).
- **9 introduced by stub implementations**, by step:
  - IS-2 (Step 3): M2
  - IS-3 (Step 4): M3
  - IS-4 (Step 5): L1
  - IS-1+DS-3 (Step 6): M1, M4
  - DS-4 (Step 7): L2, L3, L4
  - IS-6 token-budget (Step 8a): M5

### Pattern observation

Every stub-introduced finding is a **small unauthorized addition**
(M1 wiring gap, M2 floor, M3 clip, M4 isinstance asymmetry, L1 ddof
choice) or a **small documentation lag** (M5, L2, L3, L4) — no
implementer made a behavioral spec violation that contradicts the
decisions doc. The most expensive Mediums (M1, M2, M3) are all
"implementer added defensive code beyond spec." That is a healthier
failure mode than under-implementing the spec, but it does suggest
the next round of decisions docs should have a "do not add helpers
/ clips / floors not specified here" line.
