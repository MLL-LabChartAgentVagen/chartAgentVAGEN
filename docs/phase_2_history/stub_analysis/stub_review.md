# Stub Gap Analysis — Adversarial Review

## Summary verdict

The analysis is broadly accurate and well-scoped — line numbers and code spans match the live source for 9 of 10 stubs, and the dependency chains between IS-1↔DS-3 and DS-2↔IS-2/3/4 are correct. However, two non-trivial issues stand out: (1) **IS-5 fabricates spec semantics** ("hint for log/linear scaling") that do not appear in `phase_2.md` §2.1.1 and frames the situation as a "3-way drift" when the spec is actually content-free on `scale`; and (2) **DS-1 misses a cross-cutting finding** — the `censoring=` kwarg has been removed from the *live prompt* (`prompt.py:70`), so censoring is now "double-gated out" exactly like the 4 deferred patterns in DS-2, but the analysis treats it as a single-stub gap. Plus a handful of minor line-range / file-reference inaccuracies. **Overall:** Significant issues on 2 stubs, minor issues on 3, clean on 5.

---

## Per-stub findings

### [IS-1] Mixture distribution sampling

**Verdict:** Minor issues

#### Issues found
1. **Code span accuracy** — Verified: the stub is at [engine/measures.py:360-366](pipeline/phase_2/engine/measures.py#L360-L366) and the analyst's "line drift from CLAUDE.md" note is correct.
2. **Proposed solution — sub_meta construction** — In the `_sample_mixture` sketch, the line `sub_meta = {"family": comp["family"], "param_model": comp["param_model"]}` quietly drops the `"measure_type": "stochastic"` key that `_compute_per_row_params` may expect. Not necessarily a bug (depends on how `_compute_per_row_params` reads its arg), but worth flagging in implementation.
   - **Evidence:** [engine/measures.py:376-378](pipeline/phase_2/engine/measures.py#L376-L378) shows `_compute_per_row_params(col_name, col_meta, rows, n_rows, overrides)` is called with the *full* col_meta dict; the sub-spec dict the analyst constructs has fewer keys.
   - **Impact:** Implementation must verify `_compute_per_row_params` doesn't rely on `measure_type` or `name` being in col_meta, or build the sub_meta to match.
3. **Architectural consideration — auto-fix interaction** — The proposed solution does not discuss how `widen_variance` (the existing `ks_*` auto-fix) should behave on a mixture. There is no single `sigma` to widen — every component has its own. The analysis flags this only obliquely in DS-3 ("`AUTO_FIX` has a `ks_*` strategy but it doesn't naturally apply to mixture") but doesn't account for it in the IS-1 implementation plan.
   - **Evidence:** [validation/autofix.py](pipeline/phase_2/validation/autofix.py) — `widen_variance` indexes a single `sigma`; mixture would need per-component handling or an opt-out.
   - **Impact:** Co-implementing IS-1 + DS-3 + autofix mixture support is a larger surface than the "Medium (80–200 LOC)" estimate suggests once the autofix path is included.

---

### [IS-2] Dominance shift validation

**Verdict:** Clean

No issues found. Code span [pattern_checks.py:189-213](pipeline/phase_2/validation/pattern_checks.py#L189-L213) verified; spec references (§2.1.2 L127, §2.5 L305, §2.9 L672-674) verified verbatim. The "rank-change-across-temporal-split" interpretation is the most consistent reading of the in-code TODO and the existing `check_trend_break` analog. Proposed scope (~110 LOC) lines up with the existing `check_trend_break` analog.

---

### [IS-3] Convergence validation

**Verdict:** Clean

Code span [pattern_checks.py:216-239](pipeline/phase_2/validation/pattern_checks.py#L216-L239) verified. The claim "spec has the thinnest coverage of any stub" matches what `phase_2.md` §2.9 actually contains — `convergence` is in `PATTERN_TYPES` (L127) and in the prompt list (L305) but has no L3 verification sketch anywhere. Proposed scope and analog (`check_ranking_reversal`) are reasonable.

---

### [IS-4] Seasonal anomaly validation

**Verdict:** Clean

Code span [pattern_checks.py:242-265](pipeline/phase_2/validation/pattern_checks.py#L242-L265) verified. Spec coverage assessment matches: only the type-name listings, no L3 algorithm. The window-vs-baseline z-score interpretation is reasonable; the analog (`check_outlier_entity`) is appropriate.

---

### [IS-5] `scale` kwarg on `add_measure`

**Verdict:** Significant issues

#### Issues found
1. **False spec gap — fabricated semantics** — The "Spec references" section claims:
   > §2.1.1 (L51–70): Specifies `add_measure(name, family, param_model, scale=None)` signature; `scale` documented as a hint for log/linear scaling.

   The "documented as a hint for log/linear scaling" claim is **not in the spec.** §2.1.1 L51 shows `scale=None` in the signature followed by the prose "Stochastic root measure. Sampled from a named distribution. Parameters may vary by categorical context, but the measure does **not** depend on any other measure" — there is no further mention of what `scale=` means anywhere in the spec.
   - **Evidence:** Direct grep — `scale` appears only on [phase_2.md:51](pipeline/phase_2/docs/artifacts/phase_2.md#L51) (in the signature line) and [phase_2.md:287](pipeline/phase_2/docs/artifacts/phase_2.md#L287) (in the prompt template signature). No prose anywhere explains `scale`.
   - **Impact:** The "Blocking question" `(a) per-family enum hint specifying parameter interpretation (scale="log" → mu is log-scale; scale="linear" → mu is on natural scale)` is an *invented* interpretation, not a spec reading. The Phase B summary's "spec / prompt / SDK 3-way drift" framing overstates the spec content — the spec doesn't *claim* anything about `scale`, it just lists the kwarg in the signature without semantics. This is closer to a "ghost kwarg" in the spec than a competing claim.

2. **Code span line range — prompt.py inaccuracy** — The analyst writes `pipeline/phase_2/orchestration/prompt.py:50-54` and quotes only the `sim.add_measure(name, family, param_model)` line. Actual file:
   - L50-52: comments about `add_temporal`'s `freq` and `derive` (unrelated to `scale`).
   - L53: `# TODO [M?-NC-scale]: re-add scale=None kwarg ...`
   - L54: `"  sim.add_measure(name, family, param_model)\n"`
   - **Evidence:** [orchestration/prompt.py:50-54](pipeline/phase_2/orchestration/prompt.py#L50-L54) — only L53-54 are scale-related.
   - **Impact:** The cited range is wrong by 3 lines; the relevant TODO+signature is at L53-54, not L50-54. Easy to fix; misleading as an authoritative pointer in an analysis document.

3. **Recommendation correctness (with caveat)** — "Do not restore the kwarg" is the right call given the spec's content-free state. But the recommendation conflates "fix the spec/prompt drift" with "remove `scale` from the spec." Since the spec contains no behavioral claim about `scale`, removing it from the spec is a fine first step — but the analysis should be clearer that there's nothing to lose because the spec never said what `scale` did.

---

### [IS-6] M3 multi-error + token budget

**Verdict:** Clean

#### Issues found
1. **Code span — sandbox.py reference** — The analyst writes `phase_2/orchestration/sandbox.py:~657` with the parenthetical "Sandbox attempt loop." Verified: [sandbox.py:649-680](pipeline/phase_2/orchestration/sandbox.py#L649-L680) contains the `run_retry_loop` docstring describing the algorithm, and the actual retry loop body sits in the surrounding function. The `~` notation is appropriate given that this is a "capability absence" rather than a stub raise. No correction needed.

The "two independent sub-features" framing (multi-error collection + token budget) is correct; the LOC estimate (~340 combined) is consistent with the touchpoints listed.

---

### [DS-1] Censoring injection

**Verdict:** Significant issues

#### Issues found
1. **Missed dependency — prompt-side gating** — The analysis treats DS-1 as "engine raises NotImplementedError, SDK accepts the kwarg" — but the live LLM prompt has *also* been updated to omit `censoring=`. The prompt at [orchestration/prompt.py:70-71](pipeline/phase_2/orchestration/prompt.py#L70-L71) reads:
   ```python
   # TODO [M1-NC-7]: censoring kwarg deferred — re-add when engine/realism.py supports it.
   "  sim.set_realism(missing_rate, dirty_rate)    # optional\n"
   ```
   This is the **same "double-gated out" pattern** the analyst correctly identifies for DS-2 (4 deferred patterns are SDK-gated AND prompt-omitted) — but the DS-1 entry doesn't mention it.
   - **Evidence:** [orchestration/prompt.py:70-71](pipeline/phase_2/orchestration/prompt.py#L70-L71); cf. the same analyst correctly flagging the analogous behavior at DS-2 (`prompt.py:72`).
   - **Impact:** The DS-1 dependency chain understates restoration cost: bringing censoring back is not just (a) define schema + (b) implement engine — it also requires (c) re-advertise the kwarg in the prompt + (d) update the One-Shot Example. The analyst's stage5 reference even notes "scale was removed in same advertising-a-nonfeature class as `censoring=`" — so the repository is internally aware of this pattern, but the DS-1 analysis itself does not surface it.

2. **Spec reference accuracy** — "§2.1.2 (L129)" claim verified — `set_realism(missing_rate, dirty_rate, censoring)` is at [phase_2.md:129](pipeline/phase_2/docs/artifacts/phase_2.md#L129). ✓

3. **Architectural consideration — proposed marker semantics** — The proposed `(a) per-column dict, marker (a) NaN replacement` approach is reasonable but loses censoring information for downstream Phase 3 view extraction. The analysis does flag this in "Blocking questions" but then quietly chooses NaN-replacement in "Proposed solution" without revisiting the trade-off. A separate `<col>_censored` indicator column (option b in the analyst's own list) is the safer Phase-3-aware default.
   - **Impact:** Phase 3's view extraction may need to distinguish "missing" from "censored," and NaN-only marking erases that signal — the Phase 3 implications belong in the dependency chain, not just in the blocking-questions list.

---

### [DS-2] 4 pattern type injection

**Verdict:** Minor issues

#### Issues found
1. **`inject_ranking_reversal` algorithm — verifier mismatch risk** — The proposed sketch:
   ```python
   sorted_by_m1 = df.loc[target_idx, m1].sort_values().index
   m2_descending = sorted(df.loc[target_idx, m2], reverse=True)
   df.loc[sorted_by_m1, m2] = m2_descending
   ```
   pairs high-m1 *rows* with low-m2 values. But the verifier (`check_ranking_reversal`, mirrored from spec §2.9 L655-661) groups by entity, takes group means, then checks rank correlation of means.
   - **Evidence:** [phase_2.md:655-661](pipeline/phase_2/docs/artifacts/phase_2.md#L655-L661) — verifier is `means[m1].rank().corr(means[m2].rank()) < 0`, computed on entity-level means.
   - **Impact:** Row-level anti-correlation does not necessarily produce group-mean rank reversal. If entities have similar m1 distributions, the per-row reversal can cancel out at the group-mean level. The injector should be entity-mean-aware (e.g., scale m2 down for entities with high m1 and up for entities with low m1) to reliably trigger the verifier. This belongs in the proposed solution caveats.

2. **Code span verification** — [engine/patterns.py:61-71](pipeline/phase_2/engine/patterns.py#L61-L71) confirmed. Pattern types listed in the elif tuple match the analyst's quote. ✓

3. **`VALID_PATTERN_TYPES` location verified** — [sdk/relationships.py:29-31](pipeline/phase_2/sdk/relationships.py#L29-L31) is `frozenset({"outlier_entity", "trend_break"})`, confirming the "double-gated out" claim. ✓

4. **Spec L656-661 reference (off-by-one)** — Analyst cites "§2.9 L656-661" for the ranking_reversal verifier; the actual range is L655-661 (the `elif` line is at L655, not L656). Trivially minor.

---

### [DS-3] Mixture KS test

**Verdict:** Minor issues

#### Issues found
1. **`_expected_cdf` line reference inaccuracy** — Analyst writes:
   > `_expected_cdf(family="mixture", params)` at `validation/statistical.py:165` returns `None`

   Looking at actual [statistical.py:130-166](pipeline/phase_2/validation/statistical.py#L130-L166): `_expected_cdf` has explicit branches for gaussian, lognormal, exponential, gamma, beta, uniform (L143-162), and a poisson branch returning None at L163-165. There is **no explicit `mixture` branch**. The function falls through to `return None` at L166 for any unrecognized family (including mixture). So the technical claim "returns None for mixture" is correct via fall-through, but the cited line (L165) is the poisson branch — wrong reference.
   - **Evidence:** [validation/statistical.py:163-166](pipeline/phase_2/validation/statistical.py#L163-L166).
   - **Impact:** Cosmetic, but a future implementer following the line reference would land on poisson handling instead of the actual fall-through site.

2. **Proposed `_MixtureFrozen` adapter — scipy compat caveat** — `scipy.stats.kstest` accepts a callable `cdf` argument, so an object exposing only `.cdf()` works *if* `kstest` is called as `kstest(sample, dist.cdf)` (which the existing code does at [statistical.py:296](pipeline/phase_2/validation/statistical.py#L296)). The proposed sketch is compatible with this calling convention.

---

### [DS-4] Multi-column group dependency `on`

**Verdict:** Clean

Code span [sdk/relationships.py:123-132](pipeline/phase_2/sdk/relationships.py#L123-L132) verified. Spec coverage assessment correct — §2.1.2 L106-117 declares `on` as a list (multi-column implied) but no nested-weights schema is given. The proposed nested-dict schema with full Cartesian coverage is the natural extension of the existing single-column rule (mirrored at [relationships.py:166-200](pipeline/phase_2/sdk/relationships.py#L166-L200)).

The cardinality blow-up concern (5×4×3 → 60 inner dicts) is real but correctly identified as an LLM-side problem, not a code-side one.

---

## Cross-cutting findings

1. **"Double-gated out" pattern undercounted.** The analysis correctly identifies the SDK-gate + prompt-omission pattern for DS-2 (4 patterns). The same pattern applies to **DS-1 (censoring)** and **IS-5 (`scale`)** — all three are now defensively removed from the live prompt. The DS-2 entry is the only one that surfaces the prompt-side gate as a first-class fact in its dependency chain. DS-1's prompt removal is invisible in its analysis; IS-5's prompt removal is acknowledged but framed as part of a "3-way drift" rather than as the same defensive pattern.
   - **Recommendation:** Add a cross-stub note that the project has a consistent "absent + TypeError + prompt-omitted" pattern for un-implemented LLM-facing parameters, and that all three entries (IS-5, DS-1, DS-2) follow it.

2. **"8 of 10 spec-blocked" claim is overstated.** Phase B summary says "Spec gaps dominate over code gaps. 8 of 10 stubs are blocked at least partially by missing spec definitions." But:
   - **IS-6** (multi-error / token budget) is explicitly noted as operational, not a spec feature — it is *not* spec-blocked.
   - **DS-2's `ranking_reversal` injector** could derive its contract from the existing verifier (already in spec §2.9 L655-661) — not strictly spec-blocked.

   So a more honest count is 6-7 of 10 spec-blocked. Not a critical issue, but the framing inflates the apparent dependency on spec extensions.

3. **Spec line drift in IS-1.** The analyst calls out one drift (CLAUDE.md `~L297-303` → actual L360-366). They do not check whether the same kind of drift applies elsewhere — for example, the stage5 anatomy summary itself is dated 2026-04-22 and may have other stale line references. Worth a one-liner acknowledging this is a likely-systemic issue rather than IS-1-specific.

4. **`set_realism(censoring=)` SDK-side surfacing.** [relationships.py:281](pipeline/phase_2/sdk/relationships.py#L281) confirms `set_realism` still accepts `censoring=None`. The analyst's claim "sdk/relationships.py::set_realism already accepts censoring" is correct. But because the prompt no longer documents it (cross-cutting #1), the kwarg is effectively unreachable in normal LLM-driven flow. The DS-1 dependency chain should note this asymmetry.

5. **Test coverage claim "(none found)" not independently verified for some stubs.** Spot-checked IS-5: both `test_add_stochastic_measure` (L130) and `test_add_measure_rejects_scale_kwarg` (L145) exist at [test_sdk_columns.py:130-157](pipeline/phase_2/tests/modular/test_sdk_columns.py#L130-L157). For the other stubs the "(none found)" claim is plausible but not exhaustively verified by the reviewer; this may be worth a follow-up scan if the analysis is to be used as the basis for test-coverage claims.

---

## Recommendations

Ordered by severity for fixes to `stub_gap_analysis.md` before using it for implementation:

1. **(High) Rewrite IS-5 spec section.** Replace "documented as a hint for log/linear scaling" with the literal spec content — "L51 lists `scale=None` in the signature; no prose semantics anywhere in §2.1.1 or elsewhere." Reframe blocking questions to acknowledge that interpretation (a) is not a *spec reading*, it's a *proposal to add semantics*. The "3-way drift" framing should become "spec/prompt/SDK have all converged on omission, but the spec still contains a vestigial signature line."

2. **(High) Add prompt-side gating to DS-1.** The DS-1 entry should explicitly note that `prompt.py:70-71` no longer advertises `censoring=` to the LLM, and add this to both "Role in pipeline" and "Dependency chain — Co-dependent with." Restoration cost grows from "implement engine + define schema" to "implement engine + define schema + re-advertise in prompt + update One-Shot Example."

3. **(Medium) Refine `inject_ranking_reversal` proposal in DS-2.** The current sketch operates row-level; the verifier operates entity-mean-level. Either (a) revise the algorithm to scale group-level means, or (b) note explicitly that the row-level reversal is a heuristic that may not always trigger the verifier and a more direct entity-level approach would be more reliable.

4. **(Medium) Add cross-cutting note on "double-gated out" defensive pattern.** A 3-line cross-cutting paragraph naming IS-5, DS-1, DS-2 as instances of the same SDK + prompt removal pattern would prevent the inconsistency between how each is analyzed.

5. **(Low) Fix line references.** 
   - IS-5: `prompt.py:50-54` → `prompt.py:53-54`.
   - DS-3: `validation/statistical.py:165` → `:166` (fall-through, not a mixture branch).
   - DS-2: spec `§2.9 L656-661` → `L655-661` (off-by-one on the `elif` line).

6. **(Low) Soften "8 of 10 spec-blocked" in Phase B summary.** Acknowledge IS-6 (operational only) and DS-2's `ranking_reversal` injector (verifier-derivable) as exceptions; the honest count is closer to 6-7 of 10.

7. **(Low) Add IS-1 implementation caveat re: autofix.** Note that `widen_variance` (the `ks_*` autofix strategy) does not naturally apply to mixture distributions — implementing IS-1 + DS-3 also requires a decision about autofix opt-out or per-component handling, which inflates the effective scope.

Stub gap analysis is fundamentally sound and ready for implementation use after fixes 1-3 land. Fixes 4-7 are polish.
