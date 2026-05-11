# Stricter-Tests Backlog — what "harder" coverage actually looks like (2026-05-07)

## Why this exists

At the start of the 2026-05-07 audit session you picked the **P0 + P1 (~33 tests)** scope when offered four breadth options (CRITICAL-only, P0-only, P0+P1, P0+P1+P2). The session delivered 84 net new tests against that scope, plus the §2.1.1 PK-protection fix. That work is recorded in [`TEST_AUDIT_2026-05-07.md`](TEST_AUDIT_2026-05-07.md) and the immediate-next-steps list is in [`TEST_AUDIT_FOLLOWUP_2026-05-07.md`](TEST_AUDIT_FOLLOWUP_2026-05-07.md) (four items: seed parametrisation, boundary precision, additional healing roundtrips, real-SDK self-correction).

This document enumerates the **broader rigor ladder** — every dimension along which the suite could be made strictly stronger than today, including categories the immediate-next-steps doc deliberately scopes out. Treat it as a backlog: any single category here is independently fundable; the FOLLOWUP doc is the recommended starting point because it has the highest cost-per-confidence ratio.

Each entry below answers four questions:

- **What kind of test it is** (one-line description).
- **Why the current suite doesn't have it** (gap framing).
- **What it would catch that current tests miss** (concrete bug class).
- **Rough effort + dependencies**.

The categories are roughly ordered by value-per-effort, highest first.

---

## 1. Seed-parametrised statistical tests

- **What:** Wrap every test that draws random samples in `pytest.mark.parametrize("seed", [...])` with 5–10 pre-chosen seeds. Currently each statistical test runs on one seed.
- **Why missing:** The audit prioritised closing spec gaps; cross-seed robustness was deferred to keep scope tight.
- **What it catches:** A bug that fails on most seeds but happens to work on the one I picked. With α=0.05 and 10 seeds you get ~0.5 expected false positives per test for *correct* code — strict-pass band catches anything systematic.
- **Effort:** Small (~30 min). Already specified in [FOLLOWUP §(a)](TEST_AUDIT_FOLLOWUP_2026-05-07.md). **Recommended first**.

## 2. Boundary-precision tests at every L3 threshold

- **What:** For each spec threshold (`z >= 2.0`, `|after-before|/before > 0.15`, `p > 0.05`, `< 0.10`, `>= 0.3`, …) construct fixtures so observed metric lands *exactly* at the boundary, assert pass/fail per the operator's strictness, then verify by mutation test.
- **Why missing:** Pre-fix tests use comfortably-clear fixtures (e.g., target z = 5.0 for an outlier check whose threshold is 2.0). The convergence `>=` test added in this session is the template; nothing else is at boundary level.
- **What it catches:** Off-by-one operator changes (`>` vs `>=`, `<` vs `<=`). Subtle in code review, invisible in the current suite.
- **Effort:** Moderate (~1–2 hours). Specified in [FOLLOWUP §(b)](TEST_AUDIT_FOLLOWUP_2026-05-07.md) with a per-threshold table.

## 3. Healing roundtrips for `amplify_magnitude` and `reshuffle_pair`

- **What:** Stateful `build_fn` that proves the override actually heals the failure on the next attempt. Currently only `widen_variance` has this proof.
- **Why missing:** The session added one healing roundtrip and called it "the auto-fix loop is proven"; I admitted later that's overstated.
- **What it catches:** Sign bugs in the strategy (`factor /= 1.3` instead of `*= 1.3`), missed engine-side handling (`reshuffle_pair` writes `overrides["reshuffle"]` but the engine in `generate_measures:603` must read it), wrong override-dict key.
- **Effort:** Moderate (~2–3 hours). Specified in [FOLLOWUP §(c)](TEST_AUDIT_FOLLOWUP_2026-05-07.md), including the wrinkle that `reshuffle_pair` requires real `run_pipeline` for the permutation to fire.

## 4. Real-SDK self-correction integration test

- **What:** Mock only `LLMClient.generate_code`; let the real sandbox run a script that triggers a *real* SDK exception (`WeightLengthMismatchError`); verify the real traceback flows through `format_error_feedback`; verify the second LLM call's user message contains it; verify the fixed script produces a clean DataFrame validating end-to-end.
- **Why missing:** [`tests/test_retry_feedback.py`](../tests/test_retry_feedback.py) already tests the loop's *transport* layer with synthesised `raise ValueError(...)`. The realistic chain (LLM emits SDK-valid Python that hits a real validation contract) is unproven.
- **What it catches:** Sandbox traceback formatting regressions. SDK exception messages that no longer carry the line/column the LLM needs. Format-string drift between `format_error_feedback` and what the prompt template expects.
- **Effort:** Moderate (~2–4 hours; depends on sandbox traceback predictability). Specified in [FOLLOWUP §(d)](TEST_AUDIT_FOLLOWUP_2026-05-07.md).

---

## 5. Independent oracles for every injector/validator pair

- **What:** For every L3 pattern (and every L2 statistical check), the post-injection assertion is computed by an *independent* oracle (numpy directly, hand-rolled formula) rather than calling the validator. The session added this for `ranking_reversal` only.
- **Why missing:** Scope discipline — re-implementing every validator's logic in tests is a lot of code. But: when injector and validator share a code path, a coordinated bug in both is invisible.
- **What it catches:** Coordinated bugs where injector flips ranks for *some* entities and validator's groupby silently agrees. Off-by-one errors that affect both sides equally.
- **Suggested coverage:** independent oracles for `outlier_entity`, `trend_break`, `dominance_shift`, `convergence`, `seasonal_anomaly`. Each oracle is ~10–20 LOC.
- **Effort:** Moderate–high (~4–6 hours). New file `tests/modular/test_pattern_independent_oracles.py`. Highest single-category gain in confidence after FOLLOWUP §(a)–(d).

## 6. Tests written against spec text, not impl behaviour

- **What:** Each test cites the spec line it probes (`§2.1.1: "set_realism protects primary key"`) and asserts against the quoted contract — *not* against what the impl currently does. When the impl deviates, the test fails and surfaces the drift; the human chooses whether to fix the impl or amend the spec.
- **Why missing:** Two places in the current suite where I aligned tests to impl rather than spec:
  - `check_dominance_shift` uses `abs(rank_after - rank_before)` — direction-agnostic. Test T2.1 codifies that. But spec §2.6 says *"rank changed **as declared**"* — direction *might* be supposed to matter.
  - `check_seasonal_anomaly` baseline std is computed across the whole DF, not the target subset. T1.6 worked around this with a single-column fixture rather than questioning whether the spec wants per-target baselines.
- **What it catches:** Silent drift between spec and impl. Today the only mechanical record of these is a comment in this doc; no test would fail if the impl changed in either direction.
- **Effort:** Per-test cost is small, but requires a spec-by-spec re-read to catch every case. A single audit pass through `phase_2.md` flagging every "should/must/protects/validates" sentence and a checklist tick of "tested against spec wording" is ~half a day.
- **Risk:** Some spec text is genuinely ambiguous (e.g., what *does* "rank changed as declared" mean?). Forces those questions into the open, which is itself the point.

## 7. Adversarial / minimal-fixture tests

- **What:** Two extremes per behaviour:
  1. **Smallest passing case** — minimum N, minimum cardinality, minimum number of patterns. Confirms behaviour is correct at the lower bound, not just on comfortably-large fixtures.
  2. **Edge-of-failure case** — fixture deliberately at the threshold so a small perturbation flips the verdict. (Overlaps with §2 for L3 thresholds.)
- **Why missing:** Most current fixtures are mid-range "obviously works" examples (1000 rows, 3–5 hospitals).
- **What it catches:** Bugs that scale with N (e.g., a `groupby` that silently drops single-row groups). Bugs that fire only when the data is borderline (sample variance instabilities at small N, division by zero on edge inputs).
- **Effort:** ~1–2 hours per behaviour. Could be a parametrised fixture-size sweep across a few key checks (`@pytest.mark.parametrize("n", [10, 100, 1000, 10000])`).

## 8. Property-based tests with `hypothesis`

- **What:** Replace hand-crafted fixtures with `hypothesis.strategies` for column registries, weight vectors, conditional-weight nests. Hypothesis generates many random inputs and shrinks failures to a minimal counter-example.
- **Why missing:** New library dependency; learning curve; most useful for boundary discovery rather than spec-compliance verification.
- **What it catches:** Off-by-one errors in iteration logic, floating-point edge cases, unicode in categorical values, deeply-nested conditional weights. Has historically been particularly valuable for `topological_sort`, `validate_and_normalize_*`, and the AST walker.
- **Effort:** Moderate (~half day to add `hypothesis` as a dev dep, write 4–6 strategy generators, parametrise the relevant tests).
- **Suggested first targets:** `_safe_eval_formula` (random arithmetic strings — should never crash, only `ValueError`); `validate_and_normalize_flat_weights` (random weight vectors with random length — invariant: output sums to 1.0 unless rejection condition holds); `topological_sort` (random DAGs and cycles).

## 9. Mutation testing as a CI gate

- **What:** Run `mutmut` or `cosmic-ray` over `phase_2/` source. Any mutation surviving the entire test suite is, by definition, an untested behaviour. Failed mutants identify exactly which assertions are weak.
- **Why missing:** This session ran *one* hand-crafted mutation test per round (the convergence `>=` flip; the realism PK-protection branch). Systematic coverage was deferred.
- **What it catches:** Tests that pass for the wrong reason. Operators (`+`/`-`, `<`/`<=`, `and`/`or`) that no test exercises. Constants that no test depends on.
- **Effort:** Moderate (~half day to set up `mutmut` config, exclude logging/debug paths, and run a baseline survey). Then ongoing maintenance to keep the surviving-mutant count low.
- **Realistic expectation:** First run will report dozens of survivors. Most are noise (logging changes, debug strings). The real signal is mutations to operators and thresholds in `validation/` and `engine/`.

## 10. End-to-end one-shot scenario tests

- **What:** Run the full §2.2 one-shot example (Shanghai Emergency Records) through `orchestrate()` with a mocked LLM that returns the spec-quoted code. Verify the resulting DataFrame matches the §2.3 metadata example (cardinalities, rationales, hierarchies).
- **Why missing:** `test_retry_feedback.py` proves the orchestration plumbing; `test_validation_validator.py::TestSchemaAwareValidatorRealE2E` proves the validator works on a synthetic clean DF; nothing tests the *spec's own example* end-to-end.
- **What it catches:** Drift from the spec's published shape. If the metadata builder ever stops emitting `dimension_groups[g].hierarchy` exactly as §2.3 shows, this test fires.
- **Effort:** Small (~1–2 hours, but depends on whether the §2.2 code runs cleanly today against the current SDK; if it doesn't, that itself is a finding).

## 11. Sample-size-sufficiency tests

- **What:** For each statistical test, parametrise across multiple `N` values and confirm the test holds at the *smallest* N the spec or product targets. Today every statistical test runs at one fixed N (often 1000 or 3000).
- **Why missing:** Out of scope for the current audit.
- **What it catches:** Validators that work fine for big DataFrames but produce flaky verdicts at small N (which is a realistic LLM scenario — early experimentation runs at 100–500 rows). Also identifies the *minimum N* below which a check is unreliable; useful for spec authors.
- **Effort:** Small per check (~30 min) once §1 (seed parametrisation) is in place. The two parametrise patterns compose naturally.

## 12. Differential / invariant tests

- **What:** Run the same generation with two seeds, then assert *property-level* invariants that should hold *for any seed*: row count within target ±10%, marginal weights within ±10% of declared, every measure column finite, every primary key unique-and-fully-populated. Distinguish from determinism tests (same seed → identical output) which we already have.
- **Why missing:** Property invariants are scattered across L1 individual checks; nothing aggregates them into a "any seed must satisfy these" sweep.
- **What it catches:** Bugs that violate an invariant only some of the time. The single-seed integration tests would not surface them.
- **Effort:** Small (~1 hour). Single new test class running the pipeline at e.g. seeds `[0, 7, 42, 100, 1000]` and asserting the invariant set on each result.

## 13. Exhaustive negative coverage of typed exceptions

- **What:** For every exception class in [`phase_2/exceptions.py`](../exceptions.py), at least one test that constructs the precondition for it being raised. Currently `EmptyValuesError`, `DuplicateGroupRootError`, `WeightLengthMismatchError`, `CyclicDependencyError`, `InvalidParameterError`, `PatternInjectionError`, `ParentNotFoundError`, `UndefinedEffectError` are tested unevenly.
- **Why missing:** Tests grew organically, focusing on common-failure paths.
- **What it catches:** Typed exceptions whose raise sites are never exercised. If a future refactor stops raising `ParentNotFoundError` (substitutes a generic `ValueError`), Loop A's typed-exception feedback formatting silently degrades.
- **Effort:** Small (~1 hour). Audit by greping `raise.*Error` in `phase_2/`, cross-reference with `pytest.raises(...Error)` in tests, list the gaps.

## 14. Performance / scale regression tests

- **What:** Pin a target time budget (e.g., `target_rows=10_000` finishes in under 5 seconds). Add as `@pytest.mark.timeout(5)` or a custom fixture.
- **Why missing:** Out of scope. Phase 2 is currently CPU-bound on numpy and scipy operations; nobody's been worried about performance.
- **What it catches:** A regression that introduces a quadratic loop into the per-row formula evaluator (`_eval_structural`) or per-cell sandbox evaluation. Also a guard against accidentally calling the LLM in `generate_with_validation` (would hang against a network-isolated CI).
- **Effort:** Small (~1 hour). One test class with several N points.

## 15. Cross-version stability snapshots

- **What:** Pin numpy/scipy/pandas versions in `pyproject.toml`. Add a snapshot test that records the exact bytes of `run_pipeline(seed=42, target_rows=100)` against a known-good output. CI fails on byte drift, forcing version updates to be explicit.
- **Why missing:** The audit assumed lockfile discipline; in fact `pyproject.toml` only declares minimums (`numpy>=1.24`, `pandas>=2.0`).
- **What it catches:** A pandas point-release that changes default `groupby` ordering, breaking deterministic-pipeline downstream expectations. Or a scipy `chi2_contingency` change that perturbs p-values just enough to make the §2 boundary tests flake.
- **Effort:** Moderate (~half day to set up snapshot infra, plus ongoing maintenance of the snapshot file as legitimate output changes occur).

---

## What this list explicitly excludes

- **Concurrency / thread-safety:** Phase 2 is not thread-aware; the `np.random.default_rng(seed)` model assumes single-threaded sampling. Adding concurrency tests would require a concurrency model first.
- **Network / API integration:** The LLM client is mockable and the sandbox is in-process. No external services to integration-test against (modulo §10's spec-example test, which mocks the LLM).
- **UI / human factors:** N/A — this is a backend pipeline.
- **Security beyond the formula sandbox:** The formula sandbox tests are exhaustive (25 payloads). Whole-script sandbox security (`execute_in_sandbox`) is partially covered; expanding to e.g. resource-exhaustion attacks (memory bomb scripts, fork bombs) requires container-level isolation that the in-process sandbox can't enforce regardless.

---

## Recommended sequencing if pursued

The cheapest-and-highest-value path through the ladder, in order:

1. [FOLLOWUP §(a)](TEST_AUDIT_FOLLOWUP_2026-05-07.md) — seed parametrisation. ½ day. Gates everything statistical.
2. [FOLLOWUP §(b)](TEST_AUDIT_FOLLOWUP_2026-05-07.md) — L3 boundary precision. 1–2 days.
3. **§5 here** — independent oracles. 1 day. Eliminates the largest class of validator-vs-injector blind spots.
4. [FOLLOWUP §(c)](TEST_AUDIT_FOLLOWUP_2026-05-07.md) — additional healing roundtrips. ½–1 day.
5. [FOLLOWUP §(d)](TEST_AUDIT_FOLLOWUP_2026-05-07.md) — real-SDK self-correction. 1 day.
6. **§6 here** — spec-text-cited tests, with a re-read of `phase_2.md`. ½–1 day. Forces ambiguity in the spec into the open.
7. **§9 here** — set up `mutmut`, run a baseline survey, prune the survivor list. 1 day. Reveals every untested operator across the codebase.
8. **§10 here** — full §2.2 one-shot scenario E2E. ½ day. Prevents spec-vs-impl drift on the published example.
9. **§13 here** — typed exception coverage audit. ½ day. Shores up Loop A's typed-feedback contract.
10. **§8 here** — `hypothesis` for AST walker, weight validators, topological sort. 1 day.
11. **§12, §11, §7, §15, §14** — diminishing returns. Pursue if a specific incident motivates them.

Total bottom-of-stack-to-§10: ~7 working days for one focused person, doubling the suite size and catching essentially every off-by-one and oracle-reuse bug. §11–§15 are insurance against rarer failure modes; pursue piecewise as needed.
