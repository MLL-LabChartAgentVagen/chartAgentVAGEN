# README Blueprint — AGPDS Phase 2

**Purpose:** Map every source document to the 11 confirmed README sections so the draft phase has a complete, duplication-free content plan. Ground-truth code consulted only where documents are silent, ambiguous, or conflict.

**PIPELINE_SPLIT.md routing** (cross-cuts §3, §7, §8, §9, §10 — each piece owned by exactly one section):

| PIPELINE_SPLIT.md piece | Owning section |
|---|---|
| Usage → Split workflow, End-to-end, `.env`, CLI flags table, Programmatic entry points | §3 Quick start |
| New files → `serialization.py` (`declarations_to_json` / `declarations_from_json`) | §7 Shared infrastructure |
| Modified files → `types.py` added `source_code` field on `SandboxResult` / `RetryLoopResult` | §7 Shared infrastructure |
| New files → `agpds_generate.py`, `agpds_execute.py` entries in source tree | §5 Directory structure |
| "What this change is about" — why Loop A and Loop B split (expensive/non-deterministic vs. cheap/deterministic) | §8 Pipeline control flow |
| Modified files → `pipeline.py` added `run_loop_a` / `run_loop_b_from_declarations`; `agpds_pipeline.py` added `generate_artifacts` / `execute_artifact` | §8 Pipeline control flow |
| Modified files → `orchestration/sandbox.py` populates `source_code`; `orchestration/retry_loop.py` 4-tuple return | §9 Per-module detail (M3) |
| Output layout (`scripts/`, `declarations/`, `manifest.jsonl`, `master_tables/`, `schemas/`, `charts/`) | §10 Output layout |
| "Guarantees" (determinism, backward compatibility, parallel safety) | §10 Output layout |

**Path convention used below:** `phase_2/` refers to the Phase 2 package (actual filesystem location: `pipeline/phase_2/`); `pipeline/` refers to the CLI runner directory one level up (actual filesystem location: `pipeline/`). CLAUDE.md's `../../../` hint normalizes to these names.

---

## Section 1: Header + summary

### Sources
- `phase_2.md` → title "PHASE 2: Agentic Data Simulator (SDK-Driven)"; "Core Contribution" paragraph (JSON-based DGP → Code-as-DGP paradigm shift); the three pillars (closed-form DGP declaration, DAG-ordered event-level generation, three-layer validation without additional LLM calls).
- `stage1_module_map.md` → system name "AGPDS Phase 2 — Agentic Data Simulator (SDK-Driven)"; one-line role of each of the 5 modules (for a top-of-README module teaser).
- `stage5_anatomy_summary.md` → confirms system name and that all 36 NEEDS_CLAR items are resolved (maturity statement).
- `stage2_overview.md` → pipeline execution order (M3 → M1 → M2 ∥ M4 → M5) for a one-line dataflow summary.

### Content Points (ordered)
1. Title: "Phase 2 — Agentic Data Simulator (SDK-Driven)".
2. One-paragraph summary: Phase 2 turns a Phase 1 scenario context into a validated fact-table + schema metadata + validation report, via an LLM writing a type-safe SDK script.
3. **Phase 1 → Phase 2 paradigm shift (headline bullet):** Phase 1 emitted a JSON DGP spec whose declared distribution and actual generated distribution could diverge after successive overrides (cite `phase_2.md` §2.3 "Why closed-form?" blockquote). Phase 2 replaces that with **Code-as-DGP** — the LLM writes a single executable Python script calling `FactTableSimulator`, where every measure is declared once as a complete data-generating program.
4. Three pillars teaser (one-liners, each links to its deeper section):
   - Closed-form DGP declaration via a type-safe SDK → §6 Key concepts, §9 M1.
   - DAG-ordered event-level generation (deterministic, `seed` → bit-identical CSV) → §6 Key concepts, §9 M2.
   - Three-layer validation with no additional LLM calls → §6 Key concepts, §9 M5.
5. Dataflow one-liner: `scenario → M3 (LLM) → M1 (SDK) → M2 ∥ M4 → M5 → (df, schema_metadata, ValidationReport)`.
6. Link forward: quick start in §3, module deep-dives in §9.

### Conflicts / Gaps
- None. This section is pure framing; all claims trace to `phase_2.md` and the summary artifacts.

---

## Section 2: Installation and dependencies

### Sources
- No artifact covers installation; this section cannot be written from source docs alone.
- CODE: `pipeline/phase_2/../../pyproject.toml` or repo-root `requirements.txt` → pinned runtime dependencies (numpy, pandas, scipy, pydantic?, openai, google-genai, python-dotenv).
- CODE: repo-root `requirements.txt` → verified to exist (see `git status` — it's tracked).
- CODE: `phase_2/orchestration/llm_client.py` → which LLM provider SDKs are imported (OpenAI, Gemini, Gemini Native, Azure OpenAI per `stage5_anatomy_summary.md` M3 anatomy); these become optional install groups.
- PIPELINE_SPLIT.md → `.env` keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, optional model / provider overrides). Routed here as prerequisite; the *usage* of `.env` in CLI calls goes in §3.

### Content Points (ordered)
1. Python version requirement (extract from `pyproject.toml`).
2. Install command (`pip install -e .` or `pip install -r requirements.txt`, whichever the repo supports).
3. Core runtime deps list (numpy, pandas, scipy) — one line each with version pin if any.
4. Optional LLM provider deps (openai, google-genai/gemini, azure-openai).
5. `.env` setup: enumerate keys from PIPELINE_SPLIT.md "Configuration" block, note that the sample `.env` structure mirrors the four-key precedence — CLI flag → `.env` → hardcoded fallback.
6. Note: actual LLM calls happen only in Stage 1 (`agpds_generate.py`) and the end-to-end runner (`agpds_runner.py`); Stage 2 (`agpds_execute.py`) runs without an API key.

### Conflicts / Gaps
- ⚠️ Gap: no source doc enumerates dependencies. Must read `pyproject.toml` / `requirements.txt` at draft time. Flag to user if files disagree (e.g., pin mismatch).
- ⚠️ Gap: no source doc states the minimum Python version. Must read `pyproject.toml`'s `requires-python` or infer from type-hint syntax (`dict[str, Any]`, `|` unions → Python 3.10+).

---

## Section 3: Quick start / how to run

### Sources
- `PIPELINE_SPLIT.md` → **owns this section**. Provides:
  - Usage → Split workflow (Stage 1 `agpds_generate`, Stage 2 `agpds_execute` commands with examples).
  - Usage → End-to-end (`agpds_runner` commands with examples).
  - Configuration block — `.env` keys and priority (CLI flag → `.env` → hardcoded fallback).
  - Common CLI flags table (`--api-key`, `--model`, `--provider`, `--category`, `--count`, `--output-dir`, `--input-dir`, `--workers`, `--ids`) with per-CLI applicability.
  - Programmatic entry points snippet (`run_loop_a`, `run_loop_b_from_declarations`, `declarations_to_json`, `declarations_from_json` usage).
- `phase_2.md` → nothing direct for this section; all usage content is in PIPELINE_SPLIT.md.
- CODE: verify actual CLI argument names match by reading `pipeline/agpds_generate.py`, `pipeline/agpds_execute.py`, `pipeline/agpds_runner.py` `argparse` setup — PIPELINE_SPLIT.md is authoritative but argument spellings (`--api-key` vs `--api_key`) must match code.

### Content Points (ordered)
1. **Split workflow (recommended) — the mental model.** Stage 1 writes scripts + declarations to disk (burns LLM tokens once), Stage 2 replays them (no LLM). One-sentence rationale: "re-run Stage 2 to regenerate CSVs without new LLM calls."
2. Stage 1 command examples (from PIPELINE_SPLIT.md):
   - `python -m pipeline.agpds_generate --provider gemini --count 10`
   - `python -m pipeline.agpds_generate --provider openai --count 5 --category 3`
3. Stage 2 command examples:
   - `python -m pipeline.agpds_execute --workers 4`
   - `python -m pipeline.agpds_execute --workers 1`
   - `python -m pipeline.agpds_execute --ids <scenario_id>`
   - `python -m pipeline.agpds_execute --ids id1,id2,id3 --workers 2`
4. **End-to-end (backward-compatible) command examples:**
   - `python -m pipeline.agpds_runner --provider gemini --count 1 --category 1`
   - `python -m pipeline.agpds_runner --provider openai --count 5`
5. `.env` configuration block — verbatim from PIPELINE_SPLIT.md "Configuration".
6. CLI flags table — verbatim from PIPELINE_SPLIT.md "Common CLI flags".
7. **Programmatic API quick-use snippet** — verbatim from PIPELINE_SPLIT.md "Programmatic entry points" (9 lines). Forward-reference to §8 for the Loop A / Loop B mental model and §7 for `serialization.py` details.

### Conflicts / Gaps
- ⚠️ Cross-reference risk: §7 also mentions `serialization.py`; §8 also mentions `run_loop_a` / `run_loop_b_from_declarations`. Here in §3 we **only** show call-site usage (the snippet). Function signatures and docstring-level API detail go in §9 (pipeline.py per-module); the "why split" rationale goes in §8.
- ⚠️ CODE CHECK NEEDED: PIPELINE_SPLIT.md uses `--api-key`, `--output-dir`, `--input-dir` (hyphens). Python's `argparse` usually accepts both, but the one the `help` text advertises is the authoritative form. Confirm by reading the three CLIs before publishing.

---

## Section 4: Architecture overview

### Sources
- `stage1_module_map.md` → primary source for this section. Provides:
  - Module inventory table (M1–M5 with spec sections, responsibility, I/O).
  - Note that §2.10 (Design Advantages) is a rationale section with no corresponding module (useful "no code for this" callout).
  - Module Interaction Chain (8 directed dependencies + feedback loops).
  - Execution Order text-diagram (`Phase 1 → M3 → M1 → M2 + M4 → M5 → Phase 3` with Loop A / Loop B arrows).
  - Module Boundary Diagram (ASCII).
- `stage5_anatomy_summary.md` §1 → dependency graph at the implementation level (`types.py + exceptions.py` at the bottom, `pipeline.py` at the top); complements stage1's conceptual view.
- `stage2_overview.md` → cross-module coherence reference; useful for ensuring naming/role alignment with §9.
- SVG: `docs/phase2_pipeline_module_split.svg` (Stage 1 / Stage 2 disk boundary) — **embed here per CLAUDE.md**.
- SVG: `docs/phase2_pipeline_modules.svg` (module relationships) — optionally a second figure if the first is too dense.

### Content Points (ordered)
1. Five-module map (table: module, single responsibility, primary input, primary output). Verbatim restructured from `stage1_module_map.md` Module Inventory.
2. Callout: §2.10 Design Advantages is rationale-only — no implementation module. (Per `stage1_module_map.md`.)
3. Module dependency graph — use `stage5_anatomy_summary.md` §1 ASCII graph (types/exceptions → M1 → M2/M3/M4 → M5 → pipeline.py). Shows implementation-level import graph.
4. Execution order flow: `scenario → M3 → M1 → M2 ∥ M4 → M5`. Call out that M2 and M4 both read the frozen `DeclarationStore` and can execute sequentially (they're independent reads).
5. Two feedback loops at a glance — one-line each, with forward-link to §8:
   - Loop A (M3 ↔ M1): LLM self-correction on typed SDK exceptions.
   - Loop B (M5 → M2): deterministic auto-fix re-execution without LLM.
6. **Embed `docs/phase2_pipeline_module_split.svg`** — this is the canonical Stage 1 vs. Stage 2 disk boundary figure, showing Loop A as Stage 1 and Loop B as Stage 2.
7. Transition: "implementation tree is in §5, control flow in §8, per-module internals in §9."

### Conflicts / Gaps
- ⚠️ Both SVGs exist. Blueprint recommends embedding `phase2_pipeline_module_split.svg` here (since it's mentioned explicitly in CLAUDE.md section intent) and forward-linking `phase2_pipeline_modules.svg` in §8. Alternative: use both in §4. Final call belongs to draft phase.
- ⚠️ Terminology: `stage1_module_map.md` uses "Phase 1 → Phase 3" convention; `stage5_anatomy_summary.md` uses "pipeline.py" as top orchestrator. These are the same flow at different abstraction levels — ensure §4 says so explicitly so the reader doesn't think Phase 1 and `pipeline.py` are separate things.

---

## Section 5: Codebase directory structure

### Sources
- `stage5_anatomy_summary.md` §2 "File Tree" → primary source. Annotated source tree of `phase_2/` package with per-file spec refs.
- `PIPELINE_SPLIT.md` "New files" (`pipeline/agpds_generate.py`, `pipeline/agpds_execute.py`, `pipeline/phase_2/serialization.py`) → adds files not shown in stage5 anatomy.
- `PIPELINE_SPLIT.md` "Modified files" → confirms `pipeline/agpds_pipeline.py`, `pipeline/agpds_runner.py` are the CLI runner locations.
- CODE: `pipeline/` directory listing — to render the correct top-level tree (CLI runners at `pipeline/`, package at `pipeline/phase_2/`).
- CODE: `pipeline/phase_2/tests/` → actual tests tree (see §11 for conflict with stage5).

### Content Points (ordered)
1. Top-level tree showing the two key roots — `pipeline/` for CLI runners and `pipeline/phase_2/` for the library package:
   ```
   pipeline/
   ├── agpds_generate.py          # Stage 1 CLI
   ├── agpds_execute.py           # Stage 2 CLI
   ├── agpds_runner.py            # End-to-end CLI (backward-compat)
   ├── agpds_pipeline.py          # Shared helper layer (generate_artifacts, execute_artifact)
   └── phase_2/                   # Package (documented below)
   ```
2. Per-file annotated tree for `phase_2/` — verbatim structure from `stage5_anatomy_summary.md` §2, with one addition (`serialization.py`) from PIPELINE_SPLIT.md:
   ```
   phase_2/
   ├── __init__.py
   ├── types.py                     # shared dataclasses (§2.1, §2.1.1, §2.1.2, §2.2)
   ├── exceptions.py                # typed SDK exceptions (§2.7)
   ├── pipeline.py                  # top-level Phase 2 orchestrator (Loop A + Loop B wiring)
   ├── serialization.py             # declarations_to_json / declarations_from_json (Stage 1↔2 disk boundary)
   ├── orchestration/               # M3: LLM Orchestration (§2.5, §2.7)
   │   ├── prompt.py
   │   ├── sandbox.py
   │   ├── retry_loop.py
   │   ├── code_validator.py
   │   └── llm_client.py
   ├── sdk/                         # M1: SDK Surface (§2.1–§2.3)
   │   ├── simulator.py
   │   ├── columns.py
   │   ├── relationships.py
   │   ├── groups.py
   │   ├── dag.py
   │   └── validation.py
   ├── engine/                      # M2: Generation Engine (§2.4, §2.8)
   │   ├── generator.py
   │   ├── skeleton.py
   │   ├── measures.py
   │   ├── patterns.py
   │   ├── realism.py
   │   └── postprocess.py
   ├── metadata/                    # M4: Schema Metadata (§2.6)
   │   └── builder.py
   └── validation/                  # M5: Validation Engine (§2.9)
       ├── validator.py
       ├── structural.py
       ├── statistical.py
       ├── pattern_checks.py
       └── autofix.py
   ```
3. Each annotation: one line, spec-section ref + one-sentence responsibility (copy from `stage5_anatomy_summary.md` §2).
4. Tests tree goes in §11, not here.

### Conflicts / Gaps
- ⚠️ `stage5_anatomy_summary.md` §2 file tree does not list `phase_2/serialization.py`. PIPELINE_SPLIT.md introduces it as a new file. **Resolution:** add to tree here (PIPELINE_SPLIT.md is the more recent source); cross-ref §7 for content detail.
- ⚠️ `stage5_anatomy_summary.md` §2 shows `pyproject.toml` and `README.md` at the top of the `phase_2/` tree, implying the package is a standalone project with its own pyproject. **Resolution:** confirm at draft time whether `pipeline/phase_2/pyproject.toml` actually exists as a distinct install target, or whether the actual repo has a single repo-root pyproject. If only the repo-root exists, drop the duplicate line from the tree.
- ⚠️ Do not duplicate the PIPELINE_SPLIT.md output-layout tree (`output/agpds/scenarios/`, etc.) here — that belongs in §10.

---

## Section 6: Key concepts

### Sources
- `phase_2.md` → primary source. Specifically:
  - §2.1.1, §2.1.2, §2.3 → closed-form declaration (one-shot DGP per measure).
  - §2.3 "Why closed-form?" blockquote → **design rationale** verbatim.
  - §2.2 → dimension groups, within-group hierarchy, root-only cross-group dependency DAG, orthogonality propagation.
  - §2.4 → DAG-ordered event-level row generation, topological layering, atomic-grain contract.
  - §2.9 → L1 / L2 / L3 validation layer definitions.
  - §2.10 → design advantages (chart/view flexibility); the σ∘γ∘π formula for "View = row selection ∘ aggregation ∘ projection".
- `stage2_overview.md` → cross-checks role of §2.2, §2.3, §2.4, §2.9 in the module taxonomy.
- `stage1_module_map.md` → "Feedback Loops" section distinguishes *semantic authoring errors* (Loop A) vs. *statistical sampling variance* (Loop B); useful here to frame why validation is three-layered.

### Content Points (ordered)
1. **Closed-form DGP declaration.** Each measure declared once as a complete data-generating program (from §2.1.1 `add_measure` / `add_measure_structural` and §2.3). Include the "Why closed-form?" rationale (§2.3 blockquote) as a pull-quote: previous designs chained `add_measure` → `add_conditional` → `add_dependency` → `add_correlation`, and declared vs. actual distribution could diverge. Closed-form guarantees each measure's statistical semantics are self-contained and aligned with validation.
2. **DAG-ordered generation.** All columns (categorical, temporal, measure) form a single DAG. Generation proceeds in topological order. Use the 4-layer layering example from §2.4 (independent roots → dependent non-measures → stochastic measures → structural measures) as the conceptual anchor. Forward-link to §9 M2 for the `build_full_dag` / `topological_sort` implementation.
3. **Dimension groups & orthogonality.** Within-group hierarchies via `parent`; cross-group orthogonality propagates to all column pairs (`entity ⊥ patient` → `hospital ⊥ severity`, `department ⊥ severity`, ...). Cross-group dependencies are opt-in and root-only. Explain *why* root-only (from §2.2 design-principle blockquote): prevents logical contradictions while keeping the dependency model simple.
4. **Three-layer validation (L1 / L2 / L3).** One paragraph per layer, summarizing what each layer catches. Use §2.9 header for each level: L1 structural (row count, cardinality, marginals, finiteness, orthogonality χ², DAG acyclicity); L2 statistical (KS-test per predictor cell for stochastic measures; residual mean/std for structural; conditional transition deviation for group dependencies); L3 pattern (z-score for outliers, relative magnitude for trend breaks, rank-correlation sign for reversals).
5. **Why three layers (not one).** Pull the last blockquote from §2.9 verbatim: validation runs in milliseconds, aligned with declaration level. Complement with `stage1_module_map.md`'s distinction between semantic authoring errors (caught by M1 via Loop A) and statistical sampling variance (caught by M5 via Loop B).
6. **Atomic-grain contract.** One-liner from §2.4: each row = one indivisible event; the engine does not materialize a cross-product cube. Explain why (cited in §2.4 `> Why event-level?` blockquote): realistic cell-occupancy distributions.
7. **Design advantages payoff.** Brief paragraph from §2.10: atomic-grain + dimension groups + closed-form measures enable distribution/aggregation/drill-down/relationship/multi-view/causal-reasoning chart families from a single master table. Include the `View = σ_filter ∘ γ_agg ∘ π_cols(M)` formula as a visual anchor.

### Conflicts / Gaps
- None internal to this section. All points trace to `phase_2.md` directly.
- Coordination note: this section stays **conceptual**. Concrete API signatures, function names, and file paths belong in §9. Loop A / Loop B *mechanism* belongs in §8. Control-flow rationale sentences appear in both §6 and §8, but §6 keeps them at the "why" level and §8 owns the "how".

---

## Section 7: Shared infrastructure (`types.py`, `exceptions.py`, `serialization.py`)

### Sources
- `stage5_anatomy_summary.md` §3 "Shared Infrastructure" → primary source for `types.py`, `exceptions.py`, `pipeline.py`. Lists every dataclass (`ColumnDescriptor`, `PatternSpec`, `OrthogonalPair`, `GroupDependency`, `RealismConfig`, `DeclarationStore`, `Check`, `ValidationReport`, `ParameterOverrides`), every exception type, and the orchestration role of `pipeline.py`.
- `PIPELINE_SPLIT.md` → **owns** the `serialization.py` subsection:
  - "New files → `pipeline/phase_2/serialization.py` — `declarations_to_json` / `declarations_from_json` helpers that handle `DimensionGroup`, `GroupDependency`, `OrthogonalPair` dataclasses inside `raw_declarations`."
  - "Modified files → `pipeline/phase_2/types.py` — added `source_code: Optional[str]` field to `SandboxResult` and `RetryLoopResult`." (Routed here because it's cross-cutting type state, not M3-specific behavior.)
- `phase_2.md` §2.7 → `exceptions.py` spec origin.
- CODE: `pipeline/phase_2/serialization.py` → confirmed present with `declarations_to_json` (line 25) and `declarations_from_json` (line 45). Consult at draft time for exact type signatures to include verbatim.

### Content Points (ordered)
1. Overview sentence: three module-level utility files imported everywhere; no business logic.
2. **`types.py`** subsection — dataclasses, grouped by consumer:
   - Declaration-side (M1 → M2/M4): `ColumnDescriptor`, `PatternSpec`, `OrthogonalPair`, `GroupDependency`, `RealismConfig`, `DeclarationStore`. Highlight `DeclarationStore.freeze()` as the M1 → M2 boundary contract.
   - Validation-side (M5): `Check`, `ValidationReport`, `ParameterOverrides` (note: a plain nested `dict`, not a custom class).
   - **From PIPELINE_SPLIT.md:** `SandboxResult` and `RetryLoopResult` now carry `source_code: Optional[str]` so the validated LLM script survives past the retry loop (enables Stage 1 to persist it to `scripts/{id}.py`).
3. **`exceptions.py`** subsection — list each typed exception (`SDKError` base, `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`, `DuplicateColumnError`, `UndefinedPredictorError`) with one-line description. Include `SkipResult` sentinel and explain that it is *not* an exception — it is a terminal-failure signal produced by M3 and checked by `pipeline.py`.
4. **`serialization.py`** subsection — `declarations_to_json(raw_declarations) → dict` and `declarations_from_json(dict) → raw_declarations`. Explain why it exists: the `raw_declarations` dict contains dataclass instances (`DimensionGroup`, `GroupDependency`, `OrthogonalPair`) that `json.dumps` cannot handle; these helpers round-trip them through the Stage 1 → Stage 2 disk boundary. Forward-link to §8 for the Stage 1/2 rationale.

### Conflicts / Gaps
- ⚠️ `stage5_anatomy_summary.md` §2 file tree omits `serialization.py` entirely; PIPELINE_SPLIT.md introduces it. This section's content is the reconciliation. **Resolution:** trust PIPELINE_SPLIT.md + confirm in code (verified present). Also cross-reference §5 to ensure the directory tree there includes `serialization.py`.
- ⚠️ `stage5_anatomy_summary.md` lists `pipeline.py` under "Shared Infrastructure" with `run_phase2` / `_run_loop_a` / `_run_loop_b` signatures. PIPELINE_SPLIT.md additionally introduces the public `run_loop_a` and `run_loop_b_from_declarations` API. **Resolution:** put `pipeline.py`'s full public API in §9 (under "top-level orchestrator" subsection), keep §7 scoped to the three data/contract files. Reference from here to §9 for `pipeline.py` detail.

---

## Section 8: Pipeline control flow

### Sources
- `stage1_module_map.md` → **primary source.**
  - Directed Dependencies (8 edges).
  - Feedback Loops subsection: Loop A (M3 ↔ M1, with LLM) vs. Loop B (M5 → M2, no LLM), their nesting semantics, and the *semantic authoring errors* vs. *statistical sampling variance* framing.
  - Execution Order ASCII diagram.
- `phase_2.md`:
  - §2.7 "Execution-Error Feedback Loop" → Loop A step-by-step (1. LLM outputs → 2. sandbox → 3/4. success/failure → 5. feedback → 6. retry).
  - §2.8 "Deterministic Engine Execution" → `M = τ_post ∘ δ^? ∘ γ ∘ β ∘ α(seed)` pipeline composition formula.
  - §2.9 "Auto-Fix Loop (No LLM Re-Call)" → Loop B pseudocode (`generate_with_validation`).
- `stage5_anatomy_summary.md` "Shared Infrastructure → pipeline.py" → `_run_loop_a` / `_run_loop_b` internal wiring.
- `PIPELINE_SPLIT.md` → **owns the Stage 1 / Stage 2 split rationale** ("What this change is about" + "Guarantees"):
  - Stage 1 = Phase 0 + Phase 1 + Phase 2 Loop A; expensive and non-deterministic.
  - Stage 2 = Phase 2 Loop B; cheap and deterministic (pure function of `raw_declarations`).
  - Disk boundary enables parallel replay, inspection, byte-identical CSVs on re-run.
  - New public API: `run_loop_a`, `run_loop_b_from_declarations`.
  - `agpds_pipeline.py` gains `generate_artifacts` (Stage 1) and `execute_artifact` (Stage 2); `run_single` now chains them.
- SVG: `docs/phase2_pipeline_module_split.svg` is the canonical disk-boundary figure; also referenced from §4. **Do not re-embed here — link back** to avoid duplication.

### Content Points (ordered)
1. The two nested control loops, one paragraph each:
   - **Loop A (code-level self-correction).** M3 prompts LLM → M1 SDK validates declarations → on typed exception, M3 appends code + traceback and re-prompts (max 3 retries). Fixes *semantic authoring errors*. Cite `stage1_module_map.md` feedback-loops framing. Forward-link to §9 M3 for `sandbox.run_retry_loop`.
   - **Loop B (statistical auto-fix).** M5 validates the generated DataFrame → on L1/L2/L3 failure, apply auto-fix strategies (`widen_variance`, `amplify_magnitude`, `reshuffle_pair`) and re-execute M2 with `seed + attempt` offset and parameter overrides (max 3 retries). No LLM calls. Fixes *statistical sampling variance*. Forward-link to §9 M5 for `generate_with_validation`.
2. Loop nesting: Loop A (outer) → Loop B (inner). Loop B runs only after Loop A has produced a valid script.
3. **Stage 1 vs. Stage 2 split (from PIPELINE_SPLIT.md "What this change is about"):** why Loop A lives in Stage 1 (expensive, non-deterministic, LLM-bound) and Loop B in Stage 2 (cheap, deterministic, pure function of `raw_declarations`). The disk boundary is the `declarations/{id}.json` file.
4. **How Stage 1 persists its handoff.** List the three on-disk artifacts from PIPELINE_SPLIT.md: `scripts/{id}.py` (the LLM source), `declarations/{id}.json` (round-tripped via `serialization.py`), `manifest.jsonl` (per-generation index). Forward-link to §10 for the full output tree.
5. **Public API for programmatic orchestration (from PIPELINE_SPLIT.md "Modified files"):**
   - `run_phase2(scenario_context, ...)` — thin wrapper chaining both loops (backward-compatible).
   - `run_loop_a(scenario_context, api_key, model, provider) → (df, metadata, raw_declarations, source_code) | SkipResult` — Stage 1 only.
   - `run_loop_b_from_declarations(raw_declarations) → (df, metadata, ValidationReport) | SkipResult` — Stage 2 only.
   - Note that these are the public functions behind `agpds_pipeline.generate_artifacts` (Stage 1) and `agpds_pipeline.execute_artifact` (Stage 2); `agpds_runner`'s `run_single` now chains them.
6. **Determinism guarantee (from PIPELINE_SPLIT.md "Guarantees"):** given `declarations/{id}.json`, Stage 2 always produces the same CSV (same seed, same logic). Parallel-safe: workers share no state because `raw_declarations` round-trips through JSON — no pickling hazards.
7. **Backward compatibility (from PIPELINE_SPLIT.md "Guarantees"):** `agpds_runner.py` produces identical outputs to the pre-split version; end-to-end users see no behavior change.
8. Back-reference: for the `M = τ_post ∘ δ^? ∘ γ ∘ β ∘ α(seed)` deterministic-engine composition, see §6 Key concepts and §9 M2. For SVG of the split, see §4.

### Conflicts / Gaps
- ⚠️ Risk of overlap with §3 (which shows *usage* of `run_loop_a` / `run_loop_b_from_declarations`). Resolution: §3 = call-site snippet; §8 = signatures + semantics + loop-nesting narrative; §9 = per-function internal dispatch detail.
- ⚠️ `stage1_module_map.md` execution-order diagram shows M2 and M4 as parallel (`M2 + M4`); `stage5_anatomy_summary.md` §1 shows them sequential (M4 depends on M2 in the import graph). These are not contradictory — M2 and M4 are *logically* parallel (both read the frozen store) but *practically* serialized in the current implementation (M2 calls `metadata.builder.build_schema_metadata` inline at the end of `run_pipeline`). Clarify this explicitly here so the reader doesn't expect multi-threading.

---

## Section 9: Per-module detail

### Sources
- `svg/module1_sdk_surface.md`, `svg/module2_gen_engine.md`, `svg/module3_llm_orchestration.md`, `svg/module4_schema_metadata.md`, `svg/module5_validation_engine.md` → **primary sources** for per-module narrative, SVG anchor points, and end-to-end call traces.
- `stage5_anatomy_summary.md` §3 → backup anatomy detail (file list, function signatures, data flow notes). Use when SVG markdown is terser than needed.
- `phase_2.md` §2.1–§2.9 → original spec language for each module. Quote for "intent" callouts; the SVG markdowns already track implementation-level detail.
- `PIPELINE_SPLIT.md` → per-module changes:
  - M3 (`orchestration/sandbox.py`): `execute_in_sandbox` / `run_retry_loop` now populate `source_code` on their result objects.
  - M3 (`orchestration/retry_loop.py`): `orchestrate()` now returns a 4-tuple `(df, metadata, raw_declarations, source_code)`.
  - `phase_2/pipeline.py` (shared): gains `run_loop_a` and `run_loop_b_from_declarations` public functions.
- SVGs to embed: one per module (`docs/svg/module[1-5]_*.svg`) at the start of each subsection.

### Content Points (ordered)

Each module subsection follows the same template: **Intent (1 sentence from `phase_2.md`) → SVG figure → Files (from stage5) → Key functions & I/O (from SVG markdowns) → Integration edges (from stage5)**.

1. **Top-level orchestrator — `phase_2/pipeline.py`.** (Placed before M3 because it is the entry function that users call.)
   - Sources: `stage5_anatomy_summary.md` "Shared Infrastructure → pipeline.py" + PIPELINE_SPLIT.md public-API additions.
   - Functions: `run_phase2` (backward-compat wrapper), `run_loop_a`, `run_loop_b_from_declarations`, private helpers `_run_loop_a`, `_apply_pattern_overrides`, `_run_loop_b`.
   - Integration: imports all 5 modules. Only file aware of the full pipeline.
2. **Module 1 — SDK Surface (`phase_2/sdk/`).**
   - Sources: `svg/module1_sdk_surface.md` (primary), `stage5_anatomy_summary.md` §3 M1, `phase_2.md` §2.1–§2.3.
   - Files: `simulator.py`, `columns.py`, `relationships.py`, `groups.py`, `dag.py`, `validation.py`.
   - Step 1 methods: `add_category`, `add_temporal`, `add_measure`, `add_measure_structural`.
   - Step 2 methods: `declare_orthogonal`, `add_group_dependency`, `inject_pattern`, `set_realism`.
   - Phase lifecycle: STEP_1 (declaring) → STEP_2 (relating) → FROZEN (after `generate()`). Cite the phase-transition enforcement from `columns.py:_validate_phase_step1` / `relationships.py:_validate_phase_step2`.
   - `DeclarationStore` lifecycle: accumulating → frozen → consumed.
   - Typed exceptions raised (cross-ref §7).
3. **Module 2 — Generation Engine (`phase_2/engine/`).**
   - Sources: `svg/module2_gen_engine.md` (primary), `stage5_anatomy_summary.md` §3 M2, `phase_2.md` §2.4 + §2.8.
   - Files: `generator.py`, `skeleton.py`, `measures.py`, `postprocess.py`, `patterns.py`, `realism.py`.
   - `run_pipeline(...)` is the entry; 4-stage pipeline α → β → τ_post → γ → δ. Note RNG flow: single `np.random.Generator` threaded α → β → γ → δ; bypasses τ_post; terminated after δ.
   - Distribution families supported (7 implemented + `mixture` stub from §4.1 of stage5).
   - `_safe_eval_formula` restricted-AST evaluator — why it exists (LLM code executed in-process).
   - Pattern stage γ: `outlier_entity`, `trend_break` implemented; four others stubbed — cross-reference §9 M1 `SUPPORTED_PATTERNS` and stage5 §4.2.
   - Loop B re-entry: `seed + attempt`, `overrides` dict (multiplicative scaling + reshuffle list).
4. **Module 3 — LLM Orchestration (`phase_2/orchestration/`).**
   - Sources: `svg/module3_llm_orchestration.md` (primary), `stage5_anatomy_summary.md` §3 M3, `phase_2.md` §2.5 + §2.7.
   - Files: `prompt.py`, `sandbox.py`, `retry_loop.py`, `code_validator.py`, `llm_client.py`.
   - `SYSTEM_PROMPT_TEMPLATE` — 5 composable regions (role, SDK whitelist, hard constraints HC1–HC9, soft guidelines, one-shot example) + `{scenario_context}` slot.
   - `execute_in_sandbox` — fresh namespace per attempt, `_TrackingSimulator`, 30 s default timeout, catches all `Exception` subclasses.
   - `run_retry_loop` — max 3 retries; each retry re-prompts with `format_error_feedback`. **From PIPELINE_SPLIT.md:** now propagates the validated script as `source_code` on `SandboxResult` / `RetryLoopResult`, consumed by Stage 1 to persist `scripts/{id}.py`.
   - `orchestrate` — **From PIPELINE_SPLIT.md:** returns 4-tuple `(df, metadata, raw_declarations, source_code)` on success.
   - Multi-provider `llm_client.py`: OpenAI, Gemini, Gemini Native, Azure OpenAI.
   - `SkipResult` on max-retry exhaustion.
5. **Module 4 — Schema Metadata (`phase_2/metadata/`).**
   - Sources: `svg/module4_schema_metadata.md` (primary), `stage5_anatomy_summary.md` §3 M4, `phase_2.md` §2.6.
   - File: `builder.py` (single public function `build_schema_metadata`).
   - Returns 7-key dict: `dimension_groups`, `orthogonal_groups`, `group_dependencies`, `columns`, `measure_dag_order`, `patterns`, `total_rows`.
   - Type-discriminated column descriptors (enriched per round-3 P0: `values`/`weights` on categoricals, full `param_model` on stochastic, `formula`/`effects`/`noise`/`depends_on` on structural, `conditional_weights` on group deps, full params on patterns).
   - Defensive deep-copy (`_deep_copy_param_model`).
   - Post-build self-check `_assert_metadata_consistency` (warnings, does not raise).
   - Called inline from M2's `run_pipeline` at the end — see §8 for the "logically parallel, practically serialized" note.
6. **Module 5 — Validation Engine (`phase_2/validation/`).**
   - Sources: `svg/module5_validation_engine.md` (primary), `stage5_anatomy_summary.md` §3 M5, `phase_2.md` §2.9.
   - Files: `validator.py`, `structural.py`, `statistical.py`, `pattern_checks.py`, `autofix.py`.
   - `SchemaAwareValidator(meta).validate(df, patterns)` — sequential L1 → L2 → L3 → aggregated `ValidationReport`.
   - L1 checks: `check_row_count`, `check_categorical_cardinality`, `check_marginal_weights`, `check_measure_finiteness`, `check_orthogonal_independence`, `check_measure_dag_acyclic`.
   - L2 checks: `check_stochastic_ks` (predictor-cell Cartesian product, `min_rows=5`, `max_cells=100`), `check_structural_residuals` (reuses `engine.measures._safe_eval_formula` and `_resolve_effects`), `check_group_dependency_transitions`.
   - L3 checks: `check_outlier_entity`, `check_trend_break`, `check_ranking_reversal` (implemented); `check_dominance_shift`, `check_convergence`, `check_seasonal_anomaly` (stubs — see §9 "Limitations" note).
   - `generate_with_validation` (Loop B driver): `max_attempts=3`, `seed = base_seed + attempt`, `fnmatch`-based strategy dispatch, overrides dict accumulates across retries, validation runs pre-realism, realism applied post-pass.
   - 3 strategies: `widen_variance` (×1.2 on sigma), `amplify_magnitude` (×1.3 on z_score / magnitude), `reshuffle_pair`.
7. **Known stubs and limitations** (close of §9, from `stage5_anatomy_summary.md` §4):
   - Intentional stubs (6): `mixture` sampling, `dominance_shift` / `convergence` / `seasonal_anomaly` validation, `scale` kwarg removal on `add_measure` (round-3), M3 one-error-at-a-time + token-budget.
   - Dependent stubs (4): `censoring` injection, four pattern-type injections, mixture KS test, multi-column group dependency `on`.
   - Each item: one-line "behavior today" and one-line "to-unstub requirement" from stage5 §4.

### Conflicts / Gaps
- ⚠️ **Round-3 `scale` kwarg removal.** `stage5_anatomy_summary.md` §Reconciliation log + §4.1 says `add_measure` no longer accepts `scale=` (raises `TypeError`). `svg/module1_sdk_surface.md` line 148 still shows `simulator.add_measure(name, family, param_model, scale=None)` in the call-order trace. **Resolution:** trust stage5 + reconcile (CODE: confirm by reading `phase_2/sdk/columns.py:add_measure` signature). Flag to user that `svg/module1_sdk_surface.md` is stale on this point.
- ⚠️ `svg/module2_gen_engine.md` says `_safe_eval_formula` allows `BinOp, UnaryOp, Constant, Name` (no `Pow`). `phase_2.md` §2.8 doesn't specify a restricted AST. `stage5_anatomy_summary.md` M2 says `BinOp (+, -, *, /, Pow), UnaryOp(-), Constant, Name`. **Resolution:** trust stage5 (the implementation-truth doc); `Pow` is permitted. CODE: confirm by reading `phase_2/engine/measures.py:_safe_eval_formula`.
- ⚠️ `svg/module3_llm_orchestration.md` says conversation history accumulates across retries (≤8 messages). `stage5_anatomy_summary.md` M3 `retry_loop.py` says "no accumulating conversation history — two messages per retry (`system_prompt`, `error_feedback`)". **Resolution:** trust stage5. CODE: confirm by reading `phase_2/orchestration/retry_loop.py` — this is a semantic conflict that affects how readers understand token budget.
- ⚠️ `svg/module4_schema_metadata.md` describes an optional "M2 DataFrame as input to enrich `df_stats`" — this is future-work, not current behavior. Mark as "Not implemented" in the README; the dict's 7 keys are the complete current output.

---

## Section 10: Output layout and pipeline output

### Sources
- `PIPELINE_SPLIT.md` "Output layout (unchanged)" → **owns the directory tree.** Eight subdirectories/files under `output/agpds/`: `scenarios/`, `scripts/`, `declarations/`, `manifest.jsonl`, `master_tables/`, `schemas/`, `charts/`, `charts.json`.
- `PIPELINE_SPLIT.md` "Guarantees" → byte-identical re-runs + parallel safety + backward compatibility (already cited in §8; repeat the determinism guarantee here as a user-facing "what to expect" rather than a control-flow claim).
- `phase_2.md` §2.6 → `schema_metadata` dict fully specified (reprinted example with 7 keys).
- `svg/module4_schema_metadata.md` → 7-key reference table with value-type/shape column.
- `stage5_anatomy_summary.md` §3 "Shared Infrastructure → pipeline.py" → return type `tuple[pd.DataFrame, dict, ValidationReport] | SkipResult`.

### Content Points (ordered)
1. **On-disk output layout** — verbatim PIPELINE_SPLIT.md tree:
   ```
   output/agpds/
   ├── scenarios/        # Phase 1 scenarios (existed before)
   ├── scripts/          # NEW: LLM source .py files (Stage 1)
   ├── declarations/     # NEW: raw_declarations JSON (Stage 1)
   ├── manifest.jsonl    # NEW: per-generation index (Stage 1)
   ├── master_tables/    # final CSVs (Stage 2 or runner)
   ├── schemas/          # schema metadata JSON (Stage 2 or runner)
   ├── charts/           # chart record JSON (Stage 2 or runner)
   └── charts.json       # combined bundle (runner only)
   ```
2. Annotate each directory's contents (one sentence each). Specifically call out:
   - `scripts/{id}.py` is the exact LLM-generated source; can be hand-edited and replayed via `--ids`.
   - `declarations/{id}.json` is the `raw_declarations` JSON; Stage 2 workers read this.
   - `manifest.jsonl` — one line per successful Stage 1 generation; consumed by Stage 2 `agpds_execute` to enumerate replay targets.
3. **Programmatic return values.** Document what `run_phase2`, `run_loop_a`, and `run_loop_b_from_declarations` return:
   - `run_phase2(...)` → `tuple[pd.DataFrame, dict, ValidationReport] | SkipResult`
   - `run_loop_a(...)` → `tuple[pd.DataFrame, dict, dict, str] | SkipResult` (the 4-tuple adds `raw_declarations` and `source_code`).
   - `run_loop_b_from_declarations(raw_declarations, ...)` → `tuple[pd.DataFrame, dict, ValidationReport] | SkipResult`.
4. **`schema_metadata` reference.** Reprint the 7-key table from `svg/module4_schema_metadata.md` (`dimension_groups`, `orthogonal_groups`, `group_dependencies`, `columns`, `measure_dag_order`, `patterns`, `total_rows`). Link forward to Phase 3 for how view extraction and QA generation consume it.
5. **Validation report.** `ValidationReport.checks: list[Check]`, with `all_passed` / `failures` properties. Reference §9 M5 for check names the reader may see.
6. **Determinism claim (user-facing).** Given the same `declarations/{id}.json`, Stage 2 always emits the same CSV. Parallel-safe workers: no pickling hazards because `raw_declarations` round-trips through JSON.

### Conflicts / Gaps
- ⚠️ `phase_2.md` §2.6 shows `schema_metadata` with keys including `total_rows` and `measure_dag_order`, matching the builder output. Some older docs may show a `schema` key; the round-3 reconciled key set is the 7 listed above. Use `svg/module4_schema_metadata.md` as authoritative.
- ⚠️ `charts/` and `charts.json` are Phase-3 outputs, not Phase 2. The README should acknowledge them (they appear in the tree) but explicitly say they are produced by downstream Phase 3 and are not within Phase 2's scope.

---

## Section 11: Testing

### Sources
- `stage5_anatomy_summary.md` §2 (end of file tree) → enumerates many tests (integration: `test_end_to_end.py`, `test_integration_advanced.py`, `test_module_s2e.py`, `test_validation_failures.py`; modular: 20+ per-file tests).
- CODE: actual `pipeline/phase_2/tests/` directory → has a smaller modular set: `test_engine_generator.py`, `test_engine_measures.py`, `test_metadata_builder.py`, `test_sdk_columns.py`, `test_sdk_dag.py`, `test_sdk_validation.py`, `test_validation_autofix.py`, `test_validation_structural.py`, `test_validation_validator.py`. Plus `demo_end_to_end.py` and `test_retry_feedback.py` at the tests root.
- CODE: repo-level `tests/` subdirectories (if present) for integration-level coverage.
- PIPELINE_SPLIT.md → no test changes mentioned.

### Content Points (ordered)
1. Run command: `pytest pipeline/phase_2/tests/` (confirm at draft with actual pyproject/pytest config).
2. **Tests directory tree** — from CODE, not from stage5 (stage5 is stale on this point):
   ```
   pipeline/phase_2/tests/
   ├── demo_end_to_end.py             # runnable demo + smoke
   ├── test_retry_feedback.py         # Loop A retry / error feedback
   └── modular/
       ├── test_engine_generator.py
       ├── test_engine_measures.py
       ├── test_metadata_builder.py
       ├── test_sdk_columns.py
       ├── test_sdk_dag.py
       ├── test_sdk_validation.py
       ├── test_validation_autofix.py
       ├── test_validation_structural.py
       └── test_validation_validator.py
   ```
3. Coverage map — group tests by module:
   - M1 SDK: `test_sdk_columns.py`, `test_sdk_dag.py`, `test_sdk_validation.py`.
   - M2 Engine: `test_engine_generator.py`, `test_engine_measures.py`.
   - M3 Orchestration: `test_retry_feedback.py` (+ `demo_end_to_end.py` exercises Loop A end-to-end).
   - M4 Metadata: `test_metadata_builder.py`.
   - M5 Validation: `test_validation_validator.py`, `test_validation_structural.py`, `test_validation_autofix.py`.
4. Note gaps vs. anatomy (stage5 §2 claimed broader modular coverage — `test_sdk_simulator.py`, `test_sdk_relationships.py`, `test_sdk_groups.py`, `test_engine_skeleton.py`, `test_engine_patterns.py`, `test_engine_realism.py`, `test_engine_postprocess.py`, `test_orchestration_prompt.py`, `test_orchestration_sandbox.py`, `test_orchestration_retry_loop.py`, `test_orchestration_code_validator.py`, `test_orchestration_llm_client.py`, `test_validation_statistical.py`, `test_validation_pattern.py`). Call out which modules have direct coverage today and which are covered only via integration tests.
5. Demo entry point: `pipeline/phase_2/tests/demo_end_to_end.py` — runs the full pipeline as a smoke test; useful for new contributors.

### Conflicts / Gaps
- ⚠️ **Major conflict: `stage5_anatomy_summary.md` §2 test listing does not match the actual `pipeline/phase_2/tests/` directory.** stage5 lists 20+ modular tests including four integration tests at the tests root (`test_end_to_end.py`, `test_integration_advanced.py`, `test_module_s2e.py`, `test_validation_failures.py`). Actual tree has 9 modular tests + `demo_end_to_end.py` + `test_retry_feedback.py`. **Resolution:** trust code (per CLAUDE.md ground rule). Flag to user that stage5's file tree is stale on the tests section; the blueprint already uses the actual tree.
- ⚠️ Unverified: whether there is a repo-level integration test directory outside `pipeline/phase_2/tests/`. CODE: run `find . -name "test_*.py" -path "*/tests/*"` at draft time.
- ⚠️ No source doc states the pytest invocation or configured fixtures. CODE: check repo-root `pyproject.toml` `[tool.pytest.ini_options]` or `conftest.py` (one exists at repo root per `ls`) for the test-runner setup.

---

## Cross-section coordination (duplication avoidance)

| Topic | Owner section | Forbidden in |
|---|---|---|
| Stage 1 / Stage 2 CLI commands and flags | §3 | §7, §8, §9, §10 |
| `serialization.py` signatures and purpose | §7 | §3, §8 (reference only) |
| `source_code` field on `SandboxResult` / `RetryLoopResult` | §7 (types) + §9 M3 (behavior) | §3, §8, §10 |
| Loop A / Loop B *why* (rationale) | §6 | — |
| Loop A / Loop B *how* (mechanism, API) | §8 | §6 (reference only) |
| Loop A / Loop B *where* (file:function detail) | §9 M3 (Loop A), §9 M5 (Loop B) | §6, §8 (reference only) |
| `schema_metadata` 7-key dict | §10 | §9 M4 (reference only: "see §10 for full reference") |
| SVG embed: `phase2_pipeline_module_split.svg` | §4 | §8 (link back) |
| Per-module SVGs (module1–module5) | §9 (one per subsection) | §4 |
| Directory tree of `phase_2/` package | §5 | §9 (do not re-print; reference file paths inline only) |
| `output/agpds/` directory tree | §10 | §3 (use plain prose for "saves to disk") |
| Tests tree | §11 | §5 |
| Stubs list (dominance/convergence/seasonal/mixture/scale/multi-column `on`) | §9 (closing subsection) | §6, §8 |

---

## Global conflicts / verification checklist

These are conflicts between source docs that the draft phase must resolve by consulting code. Each has been flagged inline above; listed together here for the draft owner.

1. ⚠️ **`scale=` kwarg on `add_measure`** — stage5 (removed round-3, raises `TypeError`) vs. `svg/module1_sdk_surface.md` line 148 (still shows it). **Authority: stage5 + code.** VERIFY: `grep -n "def add_measure" pipeline/phase_2/sdk/columns.py`.
2. ⚠️ **`_safe_eval_formula` AST node allowlist** — stage5 includes `Pow`; `svg/module2_gen_engine.md` omits `Pow`. **Authority: stage5 + code.** VERIFY: read `pipeline/phase_2/engine/measures.py:_safe_eval_formula`.
3. ⚠️ **Conversation history in Loop A** — stage5 says no accumulation (2 msgs per retry); `svg/module3_llm_orchestration.md` shows up to 8-message history. **Authority: stage5 + code.** VERIFY: read `pipeline/phase_2/orchestration/retry_loop.py` and `sandbox.run_retry_loop`.
4. ⚠️ **`serialization.py` existence** — stage5 file tree omits it; PIPELINE_SPLIT.md introduces it. **Authority: PIPELINE_SPLIT.md + code (confirmed present).**
5. ⚠️ **Tests tree** — stage5 lists 20+ modular tests including 4 top-level integration files; actual has 9 modular + 2 top-level. **Authority: code.**
6. ⚠️ **M2 / M4 parallel vs. sequential** — stage1_module_map shows them parallel; stage5 shows M4 called inline from M2. Both are technically correct (conceptually parallel, implementation serial). Call this out in §4 and §8.
7. ⚠️ **`pyproject.toml` in `phase_2/`** — stage5 file tree shows one; unconfirmed whether the actual repo has a nested `pipeline/phase_2/pyproject.toml` or only a repo-root one. VERIFY at draft time; affects §5 tree and §2 install command.
8. ⚠️ **CLI flag spelling** — PIPELINE_SPLIT.md uses hyphens (`--api-key`, `--output-dir`). VERIFY by reading `argparse` setup in `pipeline/agpds_generate.py`, `pipeline/agpds_execute.py`, `pipeline/agpds_runner.py`.

---

**Blueprint status:** Ready for review. Awaiting confirmation before moving to DRAFT mode.
