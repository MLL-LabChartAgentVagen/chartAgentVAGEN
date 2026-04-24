# README Accuracy Audit

Audit target: [docs/phase_2/README.md](../../phase_2/README.md) (949 lines at audit time; moved from repo-root `README.md` on 2026-04-24).
Date: 2026-04-24.

## Summary

- Total claims checked: ~120 across 10 sections (file paths, function signatures, module responsibilities, I/O, control flow, CLI, output layout, SVG embedding, directory tree, design rationale).
- **Accurate:** most signatures and high-level narrative.
- **Inaccurate:** 11 claims (1 HIGH type error, 1 HIGH env-var mis-mapping, 5 MED, 4 LOW).
- **Omissions:** 4 items worth surfacing.
- **Unsupported:** 2 implicit claims (default dispatch, "every runner loads .env").

---

## Inaccuracies

### §2 Installation and dependencies

| # | Claim in README | Expected (source/code) | Source | Severity |
|---|---|---|---|---|
| 1 | `.env` table at §2 maps `OPENAI_API_KEY=sk-...   # used by --provider openai \| azure \| gemini` (line 62) | `gemini` uses `GEMINI_API_KEY`, not `OPENAI_API_KEY`. Resolution in `agpds_generate.main()` and `agpds_runner.main()`: `provider in ("gemini", "gemini-native") → os.environ.get("GEMINI_API_KEY")`; only `openai`/`azure` fall back to `OPENAI_API_KEY`. | [agpds_generate.py:138-143](../../../../pipeline/agpds_generate.py#L138-L143), [agpds_runner.py:176-184](../../../../pipeline/agpds_runner.py#L176-L184) | HIGH |
| 2 | "`python-dotenv` is imported inside a `try / except ImportError` guard in every runner" (§2 line 54) — and §3 "Each CLI loads `.env` if `python-dotenv` is available" (line 130) | Only `agpds_generate.py` (line 118) and `agpds_runner.py` (line 167) call `load_dotenv()`. `agpds_execute.py` does not import/call `dotenv` at all. | [agpds_execute.py](../../../../pipeline/agpds_execute.py) (no `load_dotenv` call) | MED |

### §3 Quick start / CLI

| # | Claim in README | Expected | Source | Severity |
|---|---|---|---|---|
| 3 | Programmatic API example shows `model="gemini-3.1-pro-preview"` passed to `run_loop_a()` (line 173) — implying this is the canonical model | The `run_phase2` / `run_loop_a` defaults in code are `model="gemini-2.0-flash-lite"`. The `gemini-3.1-pro-preview` string appears only as a `.env` hardcoded fallback in the CLI shims, not as a function default. Not wrong (caller can pass any string), but misleading against §2's "hardcoded fallback" claim and §8's signature block showing `gemini-2.0-flash-lite`. | [pipeline.py:31,49,86](../../../../pipeline/phase_2/pipeline.py#L31), [llm_client.py:217,401](../../../../pipeline/phase_2/orchestration/llm_client.py#L217) | LOW |

### §8 Pipeline control flow

| # | Claim in README | Expected | Source | Severity |
|---|---|---|---|---|
| 4 | "Budget. `max_retries=3` by default" for Loop A; "`run_phase2` default `max_loop_b_retries=2`" (lines 512, 522) | The `run_phase2` signature defaults match (3 / 2). **However** the CLI entry path (`AGPDSPipeline.generate_artifacts` / `execute_artifact`) hard-codes different budgets: Loop A gets `max_retries=5`; Loop B gets `max_retries=3`. The CLI and the programmatic-API defaults disagree, and the README only documents the programmatic-API numbers. | [agpds_pipeline.py:110,149](../../../../pipeline/agpds_pipeline.py#L110) ; [agpds_execute.py:79](../../../../pipeline/agpds_execute.py#L79) also passes `max_retries=3` | MED |

### §9 M1 — SDK Surface

| # | Claim in README | Expected | Source | Severity |
|---|---|---|---|---|
| 5 | `inject_pattern(...)` — "`SUPPORTED_PATTERNS = {outlier_entity, trend_break, ranking_reversal, dominance_shift, convergence, seasonal_anomaly}`" (line 634) | The constant is named **`VALID_PATTERN_TYPES`**, not `SUPPORTED_PATTERNS`. Contents match the listed 6 types. | [relationships.py:29,237-240](../../../../pipeline/phase_2/sdk/relationships.py#L29) | MED |
| 6 | "`dag.py` exports. `detect_cycle_in_adjacency`, `check_measure_dag_acyclic`, `topological_sort` (Kahn's algorithm), `build_full_dag(...)` aggregating 5 edge sources, and `extract_measure_sub_dag`." (line 641) | Five of those exist, but the module also exports `collect_stochastic_predictor_cols`, `collect_structural_predictor_cols`, and `check_root_dag_acyclic`. README is incomplete, not wrong. | [dag.py:33,105,158,197,300,337,379,413](../../../../pipeline/phase_2/sdk/dag.py) | LOW |
| 7 | "docstring / build_full_dag — aggregating **5 edge sources**" (line 641) | Code agrees: numbered 1–5 in the docstring even though the docstring leading sentence says "four". No inaccuracy in README but worth flagging that the code comment itself is inconsistent. | [dag.py:207-213](../../../../pipeline/phase_2/sdk/dag.py#L207) | LOW |

### §9 M3 — LLM Orchestration

| # | Claim in README | Expected | Source | Severity |
|---|---|---|---|---|
| 8 | "`execute_in_sandbox(...)` — compiles + `exec()`s the script in a restricted namespace (**no `__import__`**, safe builtins allowlist; `FactTableSimulator` pre-injected as `_TrackingSimulator`)" (line 700) | The namespace installs a **restricted `__import__`** that permits `chartagent.synth`, `chartagent`, `phase_2`, `phase_2.simulator`, `phase_2.sdk.simulator` and rejects everything else. "No `__import__`" overstates the sandbox. | [sandbox.py:155-174](../../../../pipeline/phase_2/orchestration/sandbox.py#L155-L174) | LOW |

### §9 M4 — Schema Metadata

| # | Claim in README | Expected | Source | Severity |
|---|---|---|---|---|
| 9 | "Type-discriminated column descriptors. `_build_columns_metadata` produces type-specific shapes: … structural measures carry `formula`, `effects`, `noise`, `depends_on`" (line 744) | Code emits only `type, measure_type, formula, effects, noise` for structural measures. **`depends_on` is never added** to the column descriptor in `_build_columns_metadata`. The anatomy doc (`stage5_anatomy_summary.md:451`) makes the same claim — this is a README carry-over from a doc-drift source. | [builder.py:166-172](../../../../pipeline/phase_2/metadata/builder.py#L166-L172) | MED |

### §9 M5 — Validation Engine

| # | Claim in README | Expected | Source | Severity |
|---|---|---|---|---|
| 10 | "**Strategies.** `match_strategy` uses `fnmatch` on check names. **Default dispatch:** `marginal_*` / `ks_*` → `widen_variance` (×1.2 on relevant `sigma`); `outlier_*` / `trend_*` → `amplify_magnitude` (×1.3 on pattern `z_score` or `magnitude`); `orthogonal_*` → `reshuffle_pair` …" (lines 800-804) | There is **no default dispatch map** anywhere in `validation/autofix.py` or `pipeline.py`. `generate_with_validation(..., auto_fix=None)` guards `if auto_fix:` before calling `match_strategy`; with no mapping provided, no strategy runs. The listed mapping is a *recommended caller-supplied* mapping, not a built-in. The README phrasing ("Default dispatch") reads like shipped behavior. | [autofix.py:214-289](../../../../pipeline/phase_2/validation/autofix.py#L214-L289) (no default passed anywhere); [pipeline.py:256-264](../../../../pipeline/phase_2/pipeline.py#L256-L264) forwards `auto_fix` untransformed | MED |

### §10 Output layout

| # | Claim in README | Expected | Source | Severity |
|---|---|---|---|---|
| 11 | "**`schemas/{id}.json`** — the 7-key `schema_metadata` dict" (line 857) | Actual filename is **`{gen_id}_metadata.json`**, not `{gen_id}.json`. Both Stage 2 and the runner use `save_single_result`, which writes `schemas/{gen_id}_metadata.json`. | [agpds_runner.py:108-113](../../../../pipeline/agpds_runner.py#L108-L113) | MED |
| 12 | `schema_metadata` reference table says `columns` has type `list[dict]` (line 875) | `_build_columns_metadata` returns `dict[str, dict[str, Any]]` — a mapping keyed by column name, not a list. `metadata["columns"]` is therefore a **dict**, not a list. | [builder.py:114-175](../../../../pipeline/phase_2/metadata/builder.py#L114-L175) | HIGH |

---

## Omissions

| # | Missing Content | Source | Belongs In | Severity |
|---|---|---|---|---|
| O1 | README lists 12 typed exceptions in §7 but does not mention the `exceptions.py` **`UndefinedPredictorError`** row (it IS listed at line 484, correct) and does not mention that `_TrackingSimulator` registry also captures `orthogonal_pairs` alongside the other 7 keys documented at §7. `serialization.py` and `orchestration/sandbox.py` both treat `orthogonal_pairs` as an 8th top-level key in `raw_declarations`. | [serialization.py:29-68](../../../../pipeline/phase_2/serialization.py#L29), [retry_loop.py:83-86](../../../../pipeline/phase_2/orchestration/retry_loop.py#L83) | §7 "Stage 1 → Stage 2 handoff" | LOW |
| O2 | No mention of `GeminiClient` backward-compat alias in `llm_client.py` (line 399). Not blocking but users of the older API will look for it. | [llm_client.py:399-406](../../../../pipeline/phase_2/orchestration/llm_client.py#L399) | §9 M3 | LOW |
| O3 | README never documents that `pipeline.py` `_run_loop_b` falls back to `SkipResult` when `build_fn` returns no DataFrame (edge case — Loop B can itself return `SkipResult`, not just Loop A). §10's return-value table only labels `SkipResult` as the Loop A exhaustion path. | [pipeline.py:266-270](../../../../pipeline/phase_2/pipeline.py#L266-L270) | §10 Programmatic return values | MED |
| O4 | The runner bundles `charts/` files into `charts.json` via `AGPDSRunner.save_results` (iterates `results`, appends each `chart_record`). README describes `charts.json` as "combined bundle (runner only)" but does not mention that the bundle is **the list of per-generation chart records**, making `charts.json` a superset of `charts/*.json` — useful for consumers who read just one file. | [agpds_runner.py:58-73](../../../../pipeline/agpds_runner.py#L58-L73) | §10 | LOW |

---

## Unsupported Claims

| # | Claim | Section | Notes |
|---|---|---|---|
| U1 | "Default dispatch: `marginal_*` / `ks_*` → `widen_variance` (×1.2) …" | §9 M5 | No code ships this mapping; see Inaccuracy #10. Reframe as "recommended mapping" or show the one-liner a caller must write. |
| U2 | "Each CLI loads `.env` if `python-dotenv` is available" | §3 | `agpds_execute.py` never loads `.env`. Either restrict the claim to the two LLM-bound CLIs or add a `load_dotenv()` call to `agpds_execute.py` for consistency. |

---

## Spot-check results (passed)

The following were verified against code and match the README:

- File paths: `agpds_generate.py`, `agpds_execute.py`, `agpds_runner.py`, `agpds_pipeline.py`, `phase_2/serialization.py`, `phase_2/pipeline.py`, all M1–M5 sub-packages and files — all exist at the documented paths.
- Function signatures: `run_phase2`, `run_loop_a`, `run_loop_b_from_declarations`, `orchestrate`, `run_retry_loop`, `execute_in_sandbox`, `format_error_feedback`, `run_pipeline`, `build_schema_metadata`, `generate_with_validation`, `match_strategy`, `widen_variance`, `amplify_magnitude`, `reshuffle_pair`, `declarations_to_json`, `declarations_from_json` — signatures, defaults, and return-type annotations match.
- 4-tuple return of `run_loop_a`: `(df, metadata, raw_declarations, source_code)` — confirmed.
- `SandboxResult` / `RetryLoopResult` `source_code: Optional[str]` field — confirmed at types.py:439 and 460.
- `SkipResult` is a `@dataclass` sentinel (not an exception); checked via `isinstance` — confirmed at exceptions.py:371-387.
- L1 thresholds: row-count 0.1, marginal-weight 0.10, chi-squared p>0.05 — confirmed.
- L2 `_iter_predictor_cells` defaults `min_rows=5, max_cells=100`; `p > 0.05` KS threshold; structural zero-noise guard `residual_std < 1e-6` — confirmed.
- SVG embedding path `docs/artifacts/phase2_pipeline_module_split.svg` — file present at that location; per-module SVG paths `docs/svg/module{1..5}_*.svg` — all five present.
- `conftest.py` at repo root injecting `sys.path` for `pipeline.*` imports — confirmed present.
- `core/llm_client.py` is identical (no diff) to `phase_2/orchestration/llm_client.py` — README's "mirror of" description is accurate.
- CLI flag matrix (`--api-key`, `--model`, `--provider`, `--category`, `--count`, `--output-dir`, `--input-dir`, `--workers`, `--ids`) — checkmark pattern across the three CLIs matches argparse definitions.
- Supported distribution families enumerated (`gaussian, lognormal, gamma, beta, uniform, poisson, exponential, mixture` with `mixture` raising `NotImplementedError`) — confirmed at `engine/measures.py:361-362` and `sdk/validation.py:32`.
- Pattern types: only `outlier_entity` and `trend_break` implemented at injection; the other four raise `NotImplementedError` — confirmed at `engine/patterns.py:60-69`.
- Phase lifecycle STEP_1 → STEP_2 → FROZEN, `_check_mutable()` raising `RuntimeError` after freeze — confirmed at types.py:407-412.
- Requirements listed (numpy, pandas, scipy "Phase 2 imports" plus matplotlib/pillow/opencv-python/scikit-learn/scikit-image/statsmodels/seaborn for the rest) match `requirements.txt`.
- Test tree in §11 matches `pipeline/phase_2/tests/` including the modular/ subdirectory file names.
- `charts.json` runner-only — confirmed: only `AGPDSRunner.save_results` writes the combined bundle; Stage 2 writes only per-id files.

---

## Recommended fixes (ranked)

1. **§10 table:** change `columns: list[dict]` → `columns: dict[str, dict]` (Inaccuracy #12, HIGH).
2. **§2 .env table:** fix the key-to-provider mapping comment — `OPENAI_API_KEY` is for `openai | azure` only; `GEMINI_API_KEY` for `gemini | gemini-native` (Inaccuracy #1, HIGH).
3. **§10:** correct `schemas/{id}.json` → `schemas/{id}_metadata.json` (Inaccuracy #11, MED).
4. **§9 M4:** drop `depends_on` from the structural-measure descriptor list, or add it to `_build_columns_metadata` if the intent is to keep README as spec (Inaccuracy #9, MED).
5. **§9 M5:** clarify that the "Default dispatch" block is a *recommended caller-supplied mapping*, not shipped behavior, or ship a default in `generate_with_validation` (Inaccuracy #10, MED).
6. **§9 M1:** rename `SUPPORTED_PATTERNS` → `VALID_PATTERN_TYPES` in the prose (Inaccuracy #5, MED).
7. **§8:** either document the CLI-override retry budgets (Loop A=5, Loop B=3 via `agpds_pipeline` / `agpds_execute`) or remove the CLI-vs-API divergence by unifying defaults (Inaccuracy #4, MED).
8. **§2 / §3:** restrict the "`python-dotenv` in every runner" claim to the two LLM-bound CLIs, or add `load_dotenv()` to `agpds_execute.py` (Inaccuracy #2, MED).
9. Minor: fix "no `__import__`" wording (#8); mention `orthogonal_pairs` as the 8th `raw_declarations` key (O1); note Loop-B-also-returns-`SkipResult` edge (O3).
