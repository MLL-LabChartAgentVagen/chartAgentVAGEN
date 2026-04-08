---
title: "AGPDS Implementation Audit — Final Report"
date: 2026-03-04
verdict:
  functional_correctness: Mostly
  spec_alignment: Partially
  phase3_ready: Blocked
issue_counts:
  P0: 3
  P1: 5
  P2: 8
  P3: 4
---

# AGPDS Implementation Audit — Final Report

---

## Section 1 — Executive Summary

**1. Is the implementation functionally correct?** **Mostly.** The core Phase 2 engine (`FactTableSimulator`, 7-stage pipeline, distributions, patterns, validators) is architecturally sound and produces valid `(DataFrame, SchemaMetadata)` pairs when called directly. However, the **end-to-end pipeline is broken**: the orchestrator prompt (`_build_phase2_prompt`) instructs the LLM to call non-existent methods (`generate_with_validation`, `get_schema_metadata`), causing every sandbox execution to fail with `AttributeError`. The sandbox also exposes unrestricted `__import__`, defeating its security purpose. Individual modules (Phase 0 sampler, Phase 1 contextualizer, Phase 2 engine) work correctly in isolation.

**2. Is it aligned with the AGPDS specification?** **Partially.** 14 of 26 auditable requirements are fully compliant, 10 are partial (parameter divergences, missing fields, broken import paths), and 2 are missing (sandbox restriction bypass, non-existent API in prompt). Class naming, directory structure, and the 7-stage engine match the spec precisely.

**3. Is it ready to proceed to Phase 3?** **Blocked.** Three issues must be resolved first: (B1) `columns[*]["role"]` field is not produced — Phase 3's `ViewEnumerator` will crash; (B2) the pipeline prompt references non-existent methods — no data is produced; (B3) pattern `params` flattening can corrupt metadata keys.

---

## Section 2 — Master Issue Registry

| Issue ID | Source Audit | File:Lines | Priority | Category | Description | Recommended Action |
|----------|-------------|------------|----------|----------|-------------|-------------------|
| F-001 | 01 (A2-1), 02 (P2-6, P2-7), 03 (Mod 13) | `agpds_pipeline.py:65–73` | **P0** | CORRECTNESS_BUG | Prompt references `generate_with_validation()` and `get_schema_metadata()` which do not exist on `FactTableSimulator`; all LLM scripts fail with `AttributeError`. Hex seed also non-integer. | Rewrite `_build_phase2_prompt` to instruct `return sim.generate()` with integer seed, or remove `_build_phase2_prompt` entirely and pass `json.dumps(scenario)` to `run_with_retries` which uses the correct `PHASE2_SYSTEM_PROMPT`. |
| F-002 | 01 (A1-2), 02 (P2-9, B3), 03 (Mod 10) | `fact_table_simulator.py:984–991` | **P0** | CORRECTNESS_BUG | `pat_entry.update(p["params"])` flattens params into top-level dict; LLM params containing `"type"`, `"col"`, or `"target"` silently overwrite reserved metadata keys, corrupting the Phase 3 contract. | Replace `pat_entry.update(p["params"])` with `pat_entry["params"] = dict(p["params"])`. Update L3 pattern validators to read `p.get("params", {}).get("break_point")` instead of `p.get("break_point")`. |
| F-003 | 02 (R5, B1), 03 (Mod 7, Mod 10) | `fact_table_simulator.py:941–962` | **P0** | MISSING_FEATURE | `_build_schema_metadata()` emits `columns[*]["type"]` but not `columns[*]["role"]` (`primary`/`secondary`/`orthogonal`/`temporal`/`measure`). Phase 3's `ViewEnumerator._group_columns_by_role()` reads `col["role"]` — will crash. | Add role assignment in `_build_schema_metadata()`: root categorical → `"primary"`, child categorical → `"secondary"`, columns in orthogonal counterpart group → `"orthogonal"`, temporal → `"temporal"`, measure → `"measure"`. |
| F-004 | 01 (A3-1), 02 (P2-13) | `sandbox_executor.py:65–66` | **P1** | CORRECTNESS_BUG | `__import__` in `_SAFE_BUILTINS` allows unrestricted module imports, fully bypassing sandbox restrictions. LLM code can execute `__import__("os").system(...)`. | Replace `"__import__": __import__` with a whitelist-restricted import function allowing only `math`, `datetime`, `decimal`, `fractions`, `statistics`, `random`. |
| F-005 | 01 (A2-3), 02 (P2-14), 03 (Mod 11, Mod 13) | `agpds_pipeline.py:105–107` | **P1** | CORRECTNESS_BUG | Pre-formatted prompt from `_build_phase2_prompt()` is passed as `scenario_context` to `run_with_retries`, which wraps it again with `[SCENARIO]...[AGENT CODE]`. Result is a malformed double-wrapped prompt. | Pass `json.dumps(scenario, indent=2)` as `scenario_context` directly, letting `run_with_retries` use `PHASE2_SYSTEM_PROMPT`. Eliminate `_build_phase2_prompt()`. |
| F-006 | 01 (A4-1), 02 (CC-2), 03 (Mod 14) | `agpds_runner.py:105` | **P1** | CORRECTNESS_BUG | Default model `gemini-3.1-pro-preview` does not exist. All CLI invocations without `--model` fail at first API call. | Change default to `"gemini-2.0-flash"` or `"gemini-2.0-flash-lite"`. |
| F-007 | 01 (A2-6), 02 (P1-5), 03 (Mod 6) | `scenario_contextualizer.py:283` | **P1** | CORRECTNESS_BUG | `from phase_0.domain_pool import check_overlap` — wrong import path. Will raise `ModuleNotFoundError` whenever `deduplicate_scenarios()` is called. | Change to `from pipeline.phase_0.domain_pool import check_overlap`. |
| F-008 | 01 (A2-2), 03 (Mod 11) | `sandbox_executor.py:467` | **P1** | CODE_QUALITY | `feedback_text` not initialized before the retry loop. Safe with current flow but fragile — any loop restructure causes `UnboundLocalError`. | Add `feedback_text: str = ""` before the `for attempt in range(max_retries)` loop. |
| F-009 | 01 (A1-1), 02 (P2-9), 03 (Mod 10) | `fact_table_simulator.py:976–980` | **P2** | SPEC_DIVERGENCE | `noise_sigma` declared in `DependencyMeta` TypedDict but dropped from schema output. Phase 3 consumers cannot reconstruct the DGP's noise level. | Add `"noise_sigma": d["noise_sigma"]` to the dependencies list comprehension. |
| F-010 | 01 (A1-3), 02 (P2-9), 03 (Mod 10) | `fact_table_simulator.py:1005` | **P2** | SPEC_DIVERGENCE | `total_rows` uses `self.target_rows` (declared) instead of `len(df)` (actual). L1 row-count validator becomes a no-op. | Set `"total_rows": len(df)` after `_post_process()`. |
| F-011 | 01 (A3-3), 02 (P0-5), 03 (Mod 5) | `domain_pool.py:442–448` | **P2** | SPEC_DIVERGENCE | Pool resets when `len(candidates) < n` (100% exhaustion), not at 80% as documented in spec and docstring. | Implement `if len(self.used_ids) >= 0.8 * total_pool_size: self.used_ids.clear()`. |
| F-012 | 01 (A3-4), 03 (Mod 6) | `scenario_contextualizer.py:162–176` | **P2** | SPEC_DIVERGENCE | Soft-failure path silently returns invalid scenario after exhausting retries. Caller cannot distinguish from valid response. Phase 2 may receive scenario missing required fields. | Annotate returned dict with `"_validation_warnings": errors` key, or raise on all validation failures. |
| F-013 | 01 (A2-4), 02 (P2-4), 03 (Mod 10) | `fact_table_simulator.py:625–648` | **P2** | SPEC_DIVERGENCE | Child categorical columns sampled independently of parent; `P(department \| hospital)` not enforced despite spec §2.1.2 requiring conditional sampling. | Implement per-parent-value conditional sampling for child columns using parent-specific weight subsets. |
| F-014 | 01 (A2-5), 03 (Mod 10) | `fact_table_simulator.py:705–711` | **P2** | CODE_QUALITY | `pd.eval()` first failure silently swallowed; fallback can also fail with no formula context in error. | Wrap fallback in `try/except` raising `ValueError(f"Dependency formula '{formula}' for '{target}' failed: {e}")`. |
| F-015 | 01 (A4-3), 03 (Mod 2) | `llm_client.py:387–391` | **P2** | CORRECTNESS_BUG | Code-fence regex requires `\n` after opening backticks. Fences without newline are not stripped, causing `SyntaxError` in compiled scripts. | Change pattern to `r"^```(?:python)?\s*"` (remove `\n` requirement). |
| F-016 | 02 (P2-8), 03 (Mod 11, Mod 13) | `agpds_pipeline.py:107` | **P2** | SPEC_DIVERGENCE | `max_retries=10` vs spec's `max_retries=3`. Possibly intentional for robustness. | Document rationale or align with spec (`max_retries=3`). |
| F-017 | 01 (A2-7), 02 (Check 4a), 03 (Mod 10) | `fact_table_simulator.py:418` | **P3** | CODE_QUALITY | Parameter named `type` shadows Python built-in `type` function. Maintenance hazard. | Rename to `pattern_type`. |
| F-018 | 01 (A2-8), 03 (Mod 10) | `fact_table_simulator.py:802–810` | **P3** | CORRECTNESS_BUG | `np.linalg.cholesky` raises `LinAlgError` for `target_r = ±1.0` (PSD but not PD). Allowed by validation. | Clamp `target_r` to `[-0.9999, 0.9999]`. |
| F-019 | 01 (A3-2), 03 (Mod 14) | `agpds_runner.py:67,76` | **P3** | CODE_QUALITY | `result.pop()` mutates caller's result dicts; post-save reads will `KeyError`. | Replace `pop` with `get`; write without removing originals. |
| F-020 | 01 (A4-5), 03 (Mod 10) | `fact_table_simulator.py:14` | **P3** | CODE_QUALITY | `from scipy.stats import norm` at module level — no graceful degradation if `scipy` not installed. | Ensure `scipy` in `requirements.txt` or use lazy import with `try/except`. |

---

## Section 3 — Sprint Plan

### Sprint 1: Unblock End-to-End Pipeline (P0)

| Step | Issue IDs | Implementation | Sequencing Rationale |
|------|-----------|----------------|---------------------|
| 1.1 | F-001, F-005 | **Delete `_build_phase2_prompt()` entirely** from `agpds_pipeline.py`. In `run_single()`, replace `phase2_user_prompt = self._build_phase2_prompt(scenario)` with `phase2_user_prompt = json.dumps(scenario, indent=2)`. Pass this directly to `run_with_retries(self.llm, phase2_user_prompt, max_retries=10)`. The existing `PHASE2_SYSTEM_PROMPT` in `sandbox_executor.py` already contains the correct SDK instructions. | This is the #1 blocker — nothing else matters if the pipeline can't produce data. F-005 is resolved simultaneously because the double-wrapping was caused by `_build_phase2_prompt`. |
| 1.2 | F-002 | In `fact_table_simulator.py:987`, replace `pat_entry.update(p["params"])` with `pat_entry["params"] = dict(p["params"])`. In `validators.py`, update L3 pattern checks to read params from nested `p.get("params", {})` instead of top-level keys (e.g., `p.get("params", {}).get("break_point")` at lines ~308, ~347, ~379). | Must fix before F-003 because pattern metadata correctness affects Phase 3's ability to consume the contract. |
| 1.3 | F-003 | In `fact_table_simulator.py:_build_schema_metadata()`, add a `"role"` field to each column entry in the `columns` list. Logic: for each category spec, if it has no parent → `"primary"`, if it has a parent → `"secondary"`; for temporal → `"temporal"`; for measure → `"measure"`. For columns in orthogonal group counterparts, add `"orthogonal"` as an additional role annotation. | Depends on 1.2 (clean metadata structure) before adding new fields. |

### Sprint 2: Correctness & Security Fixes (P1)

| Step | Issue IDs | Implementation | Sequencing Rationale |
|------|-----------|----------------|---------------------|
| 2.1 | F-004 | In `sandbox_executor.py:65`, replace `"__import__": __import__` with a `_safe_import` function that whitelists `{"math", "datetime", "decimal", "fractions", "statistics", "random"}` and raises `ImportError` for all others. | Security fix — must be done before running any LLM-generated code in production. |
| 2.2 | F-006 | In `agpds_runner.py:105`, change `default="gemini-3.1-pro-preview"` to `default="gemini-2.0-flash"`. | Independent fix; unblocks CLI without `--model` flag. |
| 2.3 | F-007 | In `scenario_contextualizer.py:283`, change `from phase_0.domain_pool import check_overlap` to `from pipeline.phase_0.domain_pool import check_overlap`. | Independent fix; unblocks `deduplicate_scenarios()`. |
| 2.4 | F-008 | In `sandbox_executor.py`, add `feedback_text: str = ""` before the retry loop (around line 465). | Defensive hardening; prevents future breakage. |

---

## Section 4 — What the Code Gets Right

1. **The 7-stage deterministic engine is faithfully implemented.** All stages (β→δ→γ→λ→ψ→φ→ρ) match the spec's ordering and semantics precisely. The freeze guard between Step 1 (column declarations) and Step 2 (relationship declarations) prevents a class of ordering bugs at the API level. [Evidence: `fact_table_simulator.py:496–530`; Audit 02 P2-10: COMPLIANT]

2. **Phase 0 and Phase 1 are clean, spec-compliant modules.** `DomainPool`/`DomainSampler` (builder + consumer separation), `ScenarioContextualizer` (validation, retry, diversity tracking), and the prompt designs all closely follow the design spec. Phase 1's "zero mention of chart types" constraint is strictly honored. [Evidence: Audit 02 P0-1/2, P1-1/2/3/4/6: all COMPLIANT]

3. **The three-layer validator is a strong quality gate.** L1 (structural), L2 (statistical), and L3 (pattern) checks with auto-fix strategies provide meaningful post-generation QA without LLM calls. The auto-fix dispatch table pattern is extensible. [Evidence: `validators.py:52–633`; Audit 02 P2-11: COMPLIANT]

4. **The LLM client's Strategy pattern is well-designed.** `ProviderCapabilities` + `ParameterAdapter` cleanly abstracts provider differences (OpenAI, Gemini, Azure). Adding a new provider requires one dict entry, not new branching logic. Model-specific overrides (`MODEL_OVERRIDES`) handle reasoning models that lack temperature support. [Evidence: `llm_client.py:24–107`; Audit 03 Module 2]

5. **Naming and directory structure are spec-faithful.** All major classes (`FactTableSimulator`, `SandboxExecutor`, `SchemaAwareValidator`, `DomainPool`, `ScenarioContextualizer`) use the exact names from the spec. The `pipeline/phase_{0,1,2}/` directory layout mirrors the spec's phase numbering. [Evidence: Audit 02 Check 4a: all ✅ Match]

---

## Section 5 — Open Questions

- **[Q-001]** The spec (`phase_0.md §0.4`) calls for embedding-based deduplication via `text-embedding-3-small`; the implementation uses TF-IDF with Jaccard fallback. Was this an intentional simplification or a planned-but-not-yet-implemented feature? → **Ask Dr. Tong Sun whether embedding-based dedup is required for Phase 3 diversity guarantees, or if TF-IDF is an acceptable substitute.**

- **[Q-002]** `max_retries=10` in `agpds_pipeline.py:107` vs the spec's `max_retries=3` (`phase_2.md §2.4`). Is this an intentional robustness measure for weaker models, or an unintended divergence? → **Ask the author to either document the rationale or revert to 3.**

- **[Q-003]** The `gemini-native` LLM path passes a plain `dict` as `config` to `generate_content()`. The `google-genai` SDK documentation specifies a `GenerateContentConfig` typed object. Does this work reliably across SDK versions? → **Run `pipeline/agpds_runner.py` with `--provider gemini-native` and verify no `TypeError` on the config parameter.**

- **[Q-004]** `generate_with_validation()` in `validators.py` increments the seed via `build_fn(seed=base_seed + attempt)`, but `FactTableSimulator.generate()` ignores passed arguments and uses `self.seed`. The function only works if `build_fn` is a factory that instantiates a fresh `FactTableSimulator(seed=seed)`. Is this function intended only for the sandbox path (where `build_fact_table(seed=...)` re-creates the simulator), or should it also work with direct `sim.generate()` calls? → **Clarify intended usage in docstring; if both paths needed, add `seed` parameter to `generate()`.**

- **[Q-005]** Several legacy modules (`pipeline/core/topic_agent.py`, `pipeline/core/schema_mapper.py`, `pipeline/core/pipeline_runner.py`, `pipeline/core/basic_operators.py`, `pipeline/adapters/basic_operators.py`, `pipeline/generation_pipeline.py`) are still present but unused by the AGPDS pipeline. Should they be removed, archived to a separate branch, or kept as reference for Phase 3? → **Ask the author for a cleanup policy decision.**

---

[WRITE CONFIRMED] audit/04_final_report.md | 139 lines
