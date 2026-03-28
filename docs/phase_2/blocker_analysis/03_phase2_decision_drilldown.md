# Phase 2 Decision Drilldown

**Generated from:** `phase_2.md` (spec), `1_phase2_implementation_task_hierarchy.md` (task hierarchy v2), `2_phase2_gap_analysis.md` (gap analysis v2), `3_phase2_implementation_alignment_map.md` (alignment map v4), `4_phase2_sprint_plan.md` (sprint plan v4), `01_phase2_current_state_map.md` (Stage 1 output), `02_phase2_blocker_decomposition.md` (Stage 2 output)

**Method:** Per-blocker decision drilldown. Each blocker is traced from system-level reason → abstraction-level gap → architecture-level consequence → concrete implementation decisions that remain unsafe or undefined. Source documents are authoritative; Stage 2 conclusions are used as starting context but corrected where they diverge from source evidence.

---

## 1. Overall Diagnosis

### 1.1 What the Phase 2 blockers reveal

The Phase 2 specification describes a system with **five distinct execution concerns** — declaration, generation, metadata emission, validation, and auto-repair — that must share formal contracts to compose correctly. The spec defines these concerns with prose, pseudocode examples, and a single one-shot scenario, but **never formalizes the shared data structures that bind them**. The result is a system where each concern is individually coherent but the composition is undefined.

This is not a case of missing features or incomplete API design. It is a case of **missing intermediate abstractions** — the layer between "what the product does" and "what the code must look like." The spec jumps from product-level concepts (e.g., "the validator checks statistical correctness") directly to pseudocode (e.g., `scipy.stats.kstest(data, family, params)`) without ever formally defining the shared data model that both sides depend on (e.g., what `family` maps to in scipy, what `params` are for each family, what metadata fields carry those params to the validator).

### 1.2 Which missing decisions are foundational

Three decisions sit at the root of the dependency graph and, if resolved, would unblock approximately 20 of the 34 blocked subtasks immediately:

1. **The metadata schema** (Blocker 1) — the single shared contract between every producer and consumer in the system. Every validator check, every auto-fix strategy, and Phase 3 consumption all depend on metadata fields that the spec's §2.6 example does not emit. This is the highest-leverage single decision.

2. **The distribution family reference table** (Blocker 3) — the parametric contract between the SDK, the engine's sampling dispatch, and the validator's KS test construction. Without it, the entire stochastic-measure pipeline is inoperable.

3. **The formula DSL grammar** (Blocker 2) — the expression-language contract between the SDK's symbol resolver, the engine's safe evaluator, and the validator's residual computation. Without it, the entire structural-measure pipeline is inoperable.

These three are independent of each other and can be resolved in parallel.

### 1.3 Which missing decisions are secondary

The remaining decisions depend on the foundational three or are isolated:

- **Pattern type behavioral triples** (Blocker 4) — depends partially on the metadata schema (for L3 validation metadata access) and is a design task requiring co-specification of params, injection, and validation.
- **Post-processing invariant contract** (Blocker 5) — depends on both the metadata schema and pattern type resolution; also contains the auto-fix mutation model problem, which is a spec-internal contradiction rather than a missing contract.
- **Phase 1 interface contract** (Blocker 6) — independent but low-leverage; partially mitigated by the existing JSON injection path.
- **Cross-group default semantics** (Blocker 7) and **censoring schema** (Blocker 8) — isolated, low-impact, can be resolved opportunistically.

### 1.4 Correction to prior-stage analysis

The Stage 2 blocker decomposition correctly identifies three root-cause categories (missing contracts, missing behavioral triples, contradictory composed behavior) and correctly establishes the dependency ordering. However, it frames the metadata schema, formula DSL, and distribution family blockers as three instances of "missing shared data contracts." This drilldown refines that framing: these three blockers arise from **three different missing abstractions** (entity model, expression model, parametric model respectively), and the architectural consequences of each are distinct. Grouping them obscures the fact that the metadata schema problem is primarily a **declaration model / entity model** gap, the formula DSL problem is an **expression model** gap, and the distribution family problem is a **parametric dispatch model** gap. Each requires a different kind of design work.

---

## 2. Per-Blocker Drilldown

### 2.1 Schema Metadata Contract (Findings C3, C8, C9, C13, C3a, A2a)

#### A. System-level reason

The Phase 2 system is a **producer-consumer pipeline**: the engine produces a `(DataFrame, metadata)` tuple, and the validator, auto-fix loop, and Phase 3 all consume the metadata to understand the DataFrame's structure. The metadata is the **only** channel through which generation semantics are communicated downstream. The spec treats metadata as an output format (§2.6) but not as a contract — it provides one JSON example rather than a schema definition, and the example was written independently of the validator pseudocode. The result is two halves of the same system that disagree on the data structure that binds them.

The core mental model that is missing is: **the metadata is not a "nice-to-have output" but the formal specification of what was generated, against which all downstream consumers validate.** If the metadata is incomplete, every consumer must reverse-engineer generation semantics from the DataFrame itself — which defeats the purpose of having a deterministic, declarative pipeline.

#### B. Abstraction-level gap

**Entity model / declaration model.** The metadata schema is the serialized form of the internal declaration model. The spec defines the internal model through the SDK API (what `add_category`, `add_measure`, etc. store) and shows a partial serialization (the §2.6 example), but never defines the complete mapping between internal state and serialized metadata. This means the entity model — "what fields describe a categorical column? a stochastic measure? a structural measure? a group dependency? a pattern?" — exists implicitly across scattered API signatures but is never unified into a single typed schema.

More precisely, the gap is in the **metadata model** — the formal definition of what the metadata dict contains, field by field, with types, required/optional status, and the semantic meaning of each field. The absence of this model means the validator, auto-fix loop, and Phase 3 have no stable interface to code against.

#### C. Architecture-level consequence

The metadata schema gap creates unclear boundaries between three component pairs:

1. **Engine → Validator:** The validator pseudocode (§2.9) reads `col["values"]`, `col["weights"]`, `col["formula"]`, `col["noise_sigma"]`, `col["param_model"]`, `dep["conditional_weights"]`, `p["params"]` — none of which appear in the §2.6 metadata example. The data flow from engine to validator is broken because the producer does not emit what the consumer reads.

2. **Engine → Phase 3:** Phase 3 consumes metadata to reconstruct generation semantics for QA and chart extraction. Without `param_model`, `formula`, or `effects` in metadata, Phase 3 cannot formulate statistically grounded questions. The Phase 2 → Phase 3 boundary is undefined.

3. **Validator → Auto-Fix Loop:** The auto-fix loop dispatches fix strategies based on which `Check` failed. Fix strategies like `widen_variance` need to access the measure's parameter spec to know what to widen. If the metadata does not carry `param_model`, the fix strategy has no target to mutate — it must reach into the simulator's internal state, which creates a tight coupling between the auto-fix loop and the simulator's private API.

Additionally, the lack of a `schema_version` field means there is no forward-compatibility mechanism. When new fields are added (as they must be to resolve the C3/C8/C9 findings), existing consumers have no way to detect the change.

#### D. Implementation-level decisions blocked

1. **Metadata builder field list (Module 5, subtasks 5.1.3, 5.1.4, 5.1.6).** The `_build_schema_metadata()` method cannot be completed without knowing which fields to emit. The three SPEC_INCORRECT subtasks need a definitive, typed field specification per column type.

2. **Metadata schema as Python type.** Should the metadata be a `TypedDict`, a `@dataclass`, a Pydantic `BaseModel`, or a plain `dict` validated by JSON Schema? This affects serialization format, validation at the boundary, and whether consumers get IDE autocompletion and type checking.

3. **Per-column metadata structure.** What keys does a categorical column entry have? (`name`, `group`, `parent`, `type`, `cardinality` are in the example; `values`, `weights` are needed by the validator but absent.) What keys does a stochastic measure entry have? (`name`, `type`, `measure_type`, `family` are in the example; `param_model`, `scale` are needed but absent.) What keys does a structural measure entry have? (`name`, `depends_on` are in the example; `formula`, `effects`, `noise_sigma` are needed but absent.)

4. **Group dependency metadata structure.** The §2.6 example shows `{"child_root", "on"}` but the validator reads `dep["conditional_weights"]`. Must this field be added? What is its exact structure — nested dict matching the `GroupDependency` dataclass?

5. **Pattern metadata structure.** The §2.6 example shows `{"type", "target", "col"}` but the validator reads `p["params"]["z_score"]`, `p["params"]["break_point"]`, etc. Must the full `params` dict be serialized?

6. **Validator field access patterns.** Every validator subtask that reads from metadata (8.2.3, 8.2.4, 8.3.1, 8.3.3, 8.3.4, 8.3.6, 8.4.x) must know the exact field names and types. Without a schema, every field access is a potential `KeyError`.

7. **Schema versioning.** Should there be a `"schema_version": "2.0"` field? How does the validator behave if it receives metadata from an older version?

#### E. Plausible interpretation / decision options

**Option 1: Extend the §2.6 example to include all validator-required fields.** Define metadata as a plain `dict` with a documented field table. This is the minimal change — it preserves the current architecture and unblocks all 9+ subtasks. The risk is schema drift over time without a machine-readable schema definition.

**Option 2: Define metadata as a typed Python model (dataclass or Pydantic).** Create a `SchemaMetadata` class with nested models for each section (`DimensionGroupMeta`, `ColumnMeta`, `PatternMeta`, etc.). This provides compile-time type checking, IDE support, and automatic validation. The cost is more upfront design work and a coupling between the metadata model and the Python implementation.

**Option 3: Define metadata as a JSON Schema document with a Python model auto-generated from it.** This provides both a language-independent schema (for Phase 3, which may not be Python) and a Python-typed model. Highest upfront cost, best long-term stability.

All three options require the same core work: enumerating every field, its type, and its required/optional status. The implementation vehicle differs.

#### F. Recommended clarification priority

**Decide first:** The complete field-by-field metadata specification — what fields exist, for each column type, for group dependencies, for patterns, with types and required/optional status. This is the single highest-leverage decision in the entire blocker set. It directly unblocks 9 SPEC_INCORRECT subtasks and indirectly enables the auto-fix loop and pipeline orchestrator.

**Decide second:** The representation format (plain dict with documented schema vs. typed Python model). This can be decided concurrently but is lower-urgency — a plain dict with a field table is sufficient to unblock implementation; a typed model is better engineering but not a prerequisite.

**Can wait:** Schema versioning. Important for Phase 3 integration but not for Phase 2 implementation.

**Why this order:** The metadata schema is consumed by every downstream module. Until it is defined, the validator produces `KeyError` on every check that reads a field the metadata doesn't emit, and the auto-fix loop has no metadata to pass to the validator. The field specification is the atomic unit of work that unblocks everything.

#### G. Evidence

- §2.6 (spec): metadata example with 7 top-level keys, per-column entries missing `values`, `weights`, `param_model`, `formula`, `effects`, `noise_sigma`
- §2.9 (spec): validator pseudocode that reads `col["values"]` (line 574), `col["weights"]` (line 575), `col["formula"]` (line 626), `col["noise_sigma"]` (line 631), `dep["conditional_weights"]` (line 636), `spec.iter_predictor_cells()` (line 616)
- Gap analysis findings C3 (three reviewers), C8, C9, C13 (post-audit structural), C3a, A2a
- Alignment map Blocker 1: 3 SPEC_INCORRECT + 6 downstream = 9+ subtasks
- Task hierarchy 5.1.3, 5.1.4, 5.1.6: SPEC_INCORRECT metadata emitter subtasks

---

### 2.2 Formula DSL Grammar (Finding A3)

#### A. System-level reason

The structural-measure subsystem is built around the idea that derived measures are defined by string formulas (e.g., `"wait_minutes * 12 + severity_surcharge"`). This formula string is written by the LLM at code-generation time, validated by the SDK at declaration time, evaluated by the engine at generation time, and re-evaluated by the validator at check time. Three independent consumers must agree on what this string means — but the string's language is never defined.

The core mental model that is missing is: **the formula is a mini-language (DSL) embedded in Python strings, and any DSL requires a formal grammar.** The spec treats formulas as self-evident arithmetic expressions, but they are actually a security boundary (the evaluator must reject arbitrary code), a dependency-extraction target (the DAG builder must parse variable references), and a reproducibility contract (the validator must evaluate identically to the engine). None of these can be implemented without a grammar.

#### B. Abstraction-level gap

**Formula / expression model.** The spec uses formula strings in three roles — declaration, generation, and validation — but provides no definition of the formula language itself. The missing abstraction is an expression model: a formal specification of what tokens are valid (operators, variables, literals, functions), how they compose (precedence, associativity), how variables are resolved (measure names vs. effect names, collision handling), and what the evaluation semantics are (vectorized NumPy? element-wise Python?).

This is distinct from the metadata gap (which is about the entity model) and the distribution gap (which is about the parametric model). The formula DSL gap is about the **expression model** — the grammar and semantics of the embedded language.

#### C. Architecture-level consequence

1. **SDK → DAG Builder boundary.** The SDK's `add_measure_structural()` must parse the formula to extract variable references, which become DAG edges (edge type 5: formula measure→structural measure). Without a parser, DAG construction is incomplete — the full DAG cannot include formula-derived edges, and the topological sort may produce an incorrect generation order where a structural measure is generated before its upstream dependency. Sprint 4 works around this by scoping DAG construction to edge types 1–4, but this is a temporary measure.

2. **Engine evaluator security boundary.** The `eval_formula()` function (4.2.8) must evaluate untrusted strings (written by the LLM) in a safe sandbox. Without an operator whitelist, the security boundary is undefined. Using Python's `eval()` with no restriction allows arbitrary code execution. Using `ast.literal_eval()` rejects all arithmetic. Any intermediate solution requires knowing exactly which AST node types to allow — which requires a grammar.

3. **Engine ↔ Validator evaluation consistency.** The engine evaluates the formula in `_eval_structural()` to generate data. The validator re-evaluates the same formula in `eval_formula()` to compute expected values for residual checks. If these two evaluations use different implementations (e.g., one uses `ast` parsing, the other uses regex substitution), they may diverge on edge cases (operator precedence, NaN handling). The shared grammar ensures evaluation consistency.

4. **LLM output validation.** The LLM may generate formulas with constructs the evaluator rejects (e.g., `log(wait_minutes)`, `wait_minutes ** 2`, `max(cost, 100)`). Without a grammar, the SDK cannot validate the formula at declaration time, and the error surfaces only at generation time — deeper in the pipeline, harder to diagnose, and more expensive to fix.

#### D. Implementation-level decisions blocked

1. **Tokenizer / parser design (subtask 1.5.2).** A regex-based tokenizer, a recursive-descent parser, a Python `ast` walker, or a restricted `eval()` sandbox each require different implementations depending on the token set. The parser cannot be started without knowing whether functions like `log()` are allowed or whether only basic arithmetic (`+`, `-`, `*`, `/`) is supported.

2. **AST / DSL representation.** Should the parsed formula be represented as a Python `ast.Expression` node tree (leveraging Python's built-in parser), a custom AST dataclass hierarchy, or a simple post-fix token list? The representation determines the engine's evaluation strategy and the DAG builder's edge-extraction algorithm.

3. **Variable resolution order (subtask 1.5.2).** If a formula contains `"severity_surcharge"`, is that an effect name or a measure name? In the one-shot example, `severity_surcharge` is an effect declared in the structural measure's `effects` dict, not a standalone measure column. But what if a measure and an effect share a name? The resolution order (measure names first? effect names first? error on collision?) is a semantic decision that affects correctness.

4. **Numeric literal and constant handling.** The examples contain `12`, `0.04`, `9` as literals. Are these always floating-point? Can they be negative? Is scientific notation (`1e-3`) allowed?

5. **Operator whitelist and precedence table (subtask 4.2.8).** The safe evaluator must whitelist allowed AST node types. This is both a security decision (which operations are safe) and a functionality decision (which operations the LLM can use). The examples show `*`, `+`, `-`, but never `**`, `/`, `%`, or function calls.

6. **DAG edge extraction algorithm (subtask 1.5.2).** To add edge type 5 to the DAG, the builder must parse the formula and identify which tokens are measure names. This requires knowing the token grammar to distinguish measure names from operators, literals, and effect names.

7. **L2 residual computation (subtask 8.3.5).** The validator's L2 structural check must evaluate the formula on the generated data, subtract the result from the actual column, and check residual statistics. This reuses the same `eval_formula()` — same parser, same security boundary, same blocked decision.

#### E. Plausible interpretation / decision options

**Option 1: Minimal arithmetic DSL.** Operators: `+`, `-`, `*`, `/`, unary `-`. Operands: numeric literals (integer and float, including negative), declared measure names, declared effect names. Parentheses for grouping. No function calls. Precedence: standard mathematical (PEMDAS/BODMAS). Implementation: Python `ast` module with a whitelist of `ast.BinOp`, `ast.UnaryOp`, `ast.Num`, `ast.Name` node types. This is the simplest option and covers the one-shot example. It is sufficient for linear and polynomial relationships.

**Option 2: Extended arithmetic DSL with function whitelist.** Everything in Option 1, plus a small set of allowed functions: `log`, `exp`, `abs`, `sqrt`, `min`, `max`, `clip`. This enables nonlinear transformations (e.g., `log(wait_minutes)`) that are common in real data-generating processes. Implementation: add `ast.Call` with a whitelist of function names.

**Option 3: Python expression subset.** Allow any valid Python expression that passes an AST whitelist excluding imports, attribute access, subscripts, assignments, and calls to non-whitelisted functions. This is the most flexible but hardest to secure and test.

The spec's examples all use only Option 1 constructs. The gap analysis (A3) recommends Option 1 as the minimal set. Option 2 is a natural extension if nonlinear measures are desired.

#### F. Recommended clarification priority

**Decide first:** The operator whitelist and precedence table. This is the atomic decision that unblocks all four BLOCKED subtasks (1.5.2, 4.2.5/4.2.8, 8.3.5) plus the DAG edge type 5 addition. A one-page specification: "Allowed operators: `+`, `-`, `*`, `/`, unary `-`. Allowed operands: numeric literals, measure names, effect names. Parentheses for grouping. Standard mathematical precedence. No function calls." This single statement unblocks the entire structural-measure pipeline.

**Decide second:** Variable resolution order (measure names vs. effect names on collision). The simplest resolution is "effect names are scoped to the structural measure's `effects` dict and do not appear in the formula namespace; instead, the formula references the effect-produced column by the effect key name." This matches the one-shot example where `severity_surcharge` is an effect key.

**Can wait:** Whether to expand to function calls (Option 2). The system can ship with Option 1 and extend later. Function calls add complexity to the parser, security whitelist, and validator evaluation.

**Why this order:** The operator whitelist is the gateway decision. Without it, no parser can be built, no DAG edges can be extracted, no evaluator can be secured, and no L2 residual check can be computed. The variable resolution order is needed for correctness but is a smaller decision that can be made during implementation with a documented assumption.

#### G. Evidence

- §2.1.1 (spec lines 72–81): formula examples `"wait_minutes * 12 + severity_surcharge"`, `"cost * 0.04 + 9"` — only `*`, `+`, numeric literals, and names
- §2.3 (spec lines 178–182): structural measure description referencing formula without grammar
- Gap analysis finding A3 (CRITICAL): explicit enumeration of six missing grammar elements
- Alignment map Blocker 2: 4 BLOCKED subtasks across 3 modules
- Task hierarchy 1.5.2, 4.2.5, 4.2.8, 8.3.5: all blocked on formula DSL
- Sprint plan Sprint 4 scope note: DAG construction scoped to edge types 1–4 because formula edges blocked

---

### 2.3 Distribution Family Parameter Specification (Findings A5, A5a, A1, A1b)

#### A. System-level reason

The Phase 2 system supports eight named distribution families for stochastic measures. Each family has a different set of parameters (e.g., `mu`/`sigma` for Gaussian, `alpha`/`beta` for Beta, `shape`/`rate` for Gamma). The `param_model` schema uses an `intercept + effects` form to compute these parameters per categorical context. But the spec only demonstrates two families (`gaussian`, `lognormal`) and leaves the remaining six with no parameter keys defined.

The core mental model that is missing is: **the distribution family name is an opaque token that the SDK, engine, and validator must all interpret identically.** The SDK must validate that `param_model` contains the right keys. The engine must map those keys to `numpy.random.Generator` method arguments. The validator must map those keys to `scipy.stats` distribution constructors for KS tests. All three mappings must agree — and none of them can be built without a reference table.

The `mixture` family compounds this: it is a fundamentally different kind of distribution that cannot be expressed in the `intercept + effects` param_model schema at all. It requires component distributions, per-component parameters, and mixing weights. It also has no standard scipy CDF, making the L2 KS test impossible.

#### B. Abstraction-level gap

**Parametric dispatch model / declaration model.** The missing abstraction is a **distribution family registry** — a formal lookup table from family name to (required parameter keys, valid parameter domains, numpy sampling method, scipy distribution constructor). This is a parametric dispatch model: given a family name, what parameters does it need, and how do you sample from it and validate it?

A secondary gap is in the **parameter domain / link function model.** The `intercept + effects` computation (`θ = β₀ + Σβₘ(Xₘ)`) is an unrestricted affine combination. For some families, this can produce invalid parameter values (e.g., `sigma < 0` for Gaussian, `shape < 0` for Gamma). The spec provides no link function (e.g., `exp()` to ensure positivity) or domain clamping rule. This is a gap in the declaration model — the relationship between the `param_model` schema and the distribution's parameter constraints.

#### C. Architecture-level consequence

1. **SDK validation boundary (Module 1).** The `add_measure()` method must validate that `param_model` contains the correct keys for the declared family. Without knowing the keys for `gamma`, `beta`, `uniform`, `poisson`, `exponential`, and `mixture`, the SDK cannot perform key validation — it must either accept any keys (losing type safety) or reject everything except `gaussian`/`lognormal` (losing 6 families).

2. **Engine sampling dispatch (Module 4).** The `_sample_stochastic()` method must call `rng.normal(mu, sigma)` for Gaussian, `rng.gamma(shape, scale)` for Gamma, etc. Without the key→argument mapping, the dispatch table cannot be built. The method signature of each numpy sampling function differs (positional args, keyword args, parameterization conventions), making this a non-trivial mapping.

3. **Validator KS test construction (Module 8).** The L2 KS test (8.3.1) passes resolved parameters to `scipy.stats.kstest(data, family, params)`. But the SDK uses names like `"gaussian"` while scipy uses `"norm"`. The key mapping also differs: the SDK's `sigma` is scipy's `scale` for normal distribution. Without a mapping table, the validator cannot construct the expected CDF.

4. **`iter_predictor_cells()` algorithm (Module 8).** The helper (8.3.2) computes the cross-product of effect predictor values and resolves per-cell parameters. This algorithm depends on knowing which parameters a family uses and how effects compose on each parameter.

5. **Mixture as architectural anomaly.** The `mixture` family breaks the uniform `param_model` schema. If mixture is supported, the SDK, engine, and validator all need special-case code paths. If deferred, the family list should be reduced to 7 to avoid silent failures when the LLM emits `family="mixture"`.

#### D. Implementation-level decisions blocked

1. **Parameter keys per family.** For each of `gamma`, `beta`, `uniform`, `poisson`, `exponential`: what keys must `param_model` contain? The naming convention is not obvious — scipy uses `shape`/`scale` for Gamma but the statistical convention is `alpha`/`beta` or `k`/`theta`.

2. **SDK-to-numpy parameter mapping.** For each family: which numpy `rng.*` method to call, and how to map SDK keys to positional/keyword arguments. Example: for `gamma`, is the SDK key `shape` mapped to `rng.gamma(shape=shape, scale=1/rate)`?

3. **SDK-to-scipy name and parameter mapping.** For each family: what scipy distribution name corresponds to the SDK name, and how to map SDK keys to scipy frozen distribution arguments. Example: `"gaussian"` → `scipy.stats.norm`, SDK `mu`/`sigma` → scipy `loc`/`scale`.

4. **Parameter domain validation / link functions (finding A5a).** When `θ = β₀ + Σβₘ(Xₘ)` produces `sigma = -0.3`, what happens? Options: (a) raise `InvalidParameterError` at generation time, (b) apply a link function like `exp()` to ensure positivity, (c) clamp to a minimum value. This affects the SDK (can it validate domain at declaration time?) and the engine (must it handle invalid parameters at generation time?).

5. **Mixture decision: include or defer.** If included: define a component-list `param_model` schema, a sampling algorithm, and an L2 validation strategy (custom CDF or deferred KS test). If deferred: remove `"mixture"` from the supported families list and add a clear `NotImplementedError` or `ValueError` when the LLM emits it.

6. **L2 KS test for mixture (finding A1b).** Even if mixture sampling is defined, `scipy.stats.kstest` requires a CDF. A user-defined mixture has no standard scipy CDF. Options: (a) construct a custom CDF from component CDFs and mixing weights, (b) use a two-sample KS test against a synthetic sample from the declared mixture, (c) skip L2 for mixture columns.

#### E. Plausible interpretation / decision options

**Option 1: Define a 7-family reference table; defer mixture entirely.** For each of `gaussian`, `lognormal`, `gamma`, `beta`, `uniform`, `poisson`, `exponential`: specify SDK keys, valid domains, numpy method, scipy mapping. Remove `"mixture"` from the supported list. Raise `ValueError("mixture is not yet supported")` in the SDK. This is the safest path — it unblocks 7 subtasks immediately and avoids the mixture complexity entirely.

**Option 2: Define a 7-family reference table; add mixture as a separate schema.** Everything in Option 1, plus a mixture-specific `param_model` format: `{"components": [{"family": "gaussian", "params": {"mu": ..., "sigma": ...}, "weight": 0.6}, ...]}`. Mixture sampling via weighted component selection. L2 for mixture via custom CDF or two-sample KS. Higher implementation cost, better feature coverage.

**Option 3: Adopt scipy parameterization conventions wholesale.** Use scipy parameter names as the SDK's canonical keys (e.g., `loc`/`scale` for normal, `a`/`b`/`loc`/`scale` for beta). This minimizes the mapping layer but produces a less user-friendly API for the LLM.

The gap analysis recommends Option 1 (defer mixture) as the pragmatic path. The alignment map's Blocker 3 resolution text supports this.

**On link functions / domain validation:**

**Option A: Raise `InvalidParameterError` at generation time.** Simple, catches the error, but only at generation time — not at declaration time. The LLM would need the error feedback loop to fix it.

**Option B: Apply canonical link functions per parameter.** E.g., `exp(θ)` for scale parameters to ensure positivity. This ensures valid parameters but changes the statistical meaning of the `intercept + effects` model — the effects become multiplicative (on the log scale) rather than additive.

**Option C: Clamp to minimum valid value with a warning.** E.g., `sigma = max(θ, 1e-6)`. Quick, but silently changes the declared distribution.

The gap analysis (A5a) notes the issue but does not recommend a specific path.

#### F. Recommended clarification priority

**Decide first:** The 7-family reference table (keys, domains, numpy mapping, scipy mapping). This is the single decision that unblocks 7 BLOCKED subtasks across 3 modules. It requires specifying approximately 7 × 4 = 28 cells in a lookup table.

**Decide second:** Mixture — include or defer. This is a binary decision with clear trade-offs. Deferring is lower-risk and unblocks nothing additional; including is higher-effort but covers a richer distribution space. The recommendation is to defer and revisit after the 7-family pipeline is operational.

**Decide third:** Domain validation strategy (link function vs. error vs. clamp). This can be decided during implementation with a documented assumption. The simplest path — `InvalidParameterError` at generation time — is the lowest-risk starting point.

**Why this order:** The reference table is the atomic unit that unblocks the stochastic pipeline. Mixture is a binary gate — decide once and move on. Domain validation is an edge-case handling question that can be deferred to implementation.

#### G. Evidence

- §2.1.1 (spec line 94): eight family names listed
- §2.1.1 code examples: only `gaussian` (`mu`, `sigma`) and `lognormal` (`mu`, `sigma`) demonstrated
- Gap analysis findings A1 (CRITICAL: mixture zero-spec), A5 (CRITICAL: missing param keys), A5a (domain validation), A1b (mixture has no scipy CDF)
- Alignment map Blocker 3: 7 BLOCKED subtasks across 3 modules
- Task hierarchy 1.4.3, 1.4.4, 1.5.4, 4.2.1, 4.2.2, 8.3.1, 8.3.2: all blocked on this

---

### 2.4 Pattern Type Behavioral Triples (Findings A8, B6, C1, C10)

#### A. System-level reason

The spec defines six pattern types for injecting narrative-driven anomalies into the generated data. Two (`outlier_entity`, `trend_break`) are fully specified — their params schema, injection algorithm, and L3 validation check are all either explicitly stated or inferrable from pseudocode. Four (`ranking_reversal`, `dominance_shift`, `convergence`, `seasonal_anomaly`) are named in the API but have no specification beyond the name.

The core mental model that is missing is: **a pattern type is not a single concept but a triple of (declaration, transformation, validation) that must be co-designed.** The params schema constrains what the LLM can declare. The injection algorithm determines what statistical signature appears in the data. The validation check determines whether the injection succeeded. If any one of the three is designed without the others, the result is either an unvalidatable pattern (injection produces a signature the check cannot detect) or an undetectable pattern (the check looks for a signature the injection does not produce).

#### B. Abstraction-level gap

**Pattern behavioral model / validator contract / injection contract — jointly.** The missing abstraction is not one model but three tightly coupled models that must be specified simultaneously:

1. **Declaration model (params schema):** What keys must the `params` dict contain for each pattern type? What are their types and valid ranges?
2. **Execution model (injection algorithm):** Given `(pattern_spec, DataFrame, rng)`, what transformation does the engine apply? Is it additive? Multiplicative? Does it affect a subset of rows or all rows?
3. **Validator contract (L3 check):** Given `(DataFrame, pattern_spec, metadata)`, what statistical test determines whether the pattern was successfully injected? What is the pass/fail threshold?

These three must be specified as a unit because each constrains the others. The injection must produce a signal that exceeds the check's detection threshold. The params must control the signal strength. The check must be sensitive enough to detect the injection but robust enough to avoid false positives from random noise.

#### C. Architecture-level consequence

1. **SDK → Engine boundary.** The SDK stores pattern specs as opaque dicts for the four unspecified types (Sprint 4 workaround). The engine's `_inject_patterns()` method must dispatch on pattern type and apply the transformation — but without a transformation algorithm, the dispatch has four empty branches.

2. **Engine → Validator boundary.** The L3 validator must detect each pattern. For `dominance_shift`, the pseudocode delegates to `_verify_dominance_change()` — a function that is never defined (finding C10). For `convergence` and `seasonal_anomaly`, no L3 branch exists at all (finding C1). The engine-validator data flow has four undefined paths.

3. **Validator → Auto-Fix boundary.** The `amplify_magnitude` fix strategy is designed for outlier and trend patterns. Whether it applies to the four unspecified types — and what "amplifying magnitude" means for convergence or seasonal anomaly — is undefined. The auto-fix coverage gap (finding C4) means 5+ failure modes have no recovery path.

4. **LLM prompt guidance.** The §2.5 prompt includes pattern types in the soft guidelines but cannot advise the LLM on what params to pass for the four unspecified types. The LLM may generate invalid pattern specs that the SDK accepts (because it stores them as opaque dicts) and the engine cannot execute.

#### D. Implementation-level decisions blocked

1. **Params schema per type (subtask 1.8.4).** Cannot validate `params` dict for four types without knowing required keys. Currently stored as opaque dicts — a validation hole.

2. **Injection algorithm per type (subtasks 4.3.3–4.3.6).** For `ranking_reversal`: does it swap means of two measures across entity categories? Selectively scale one category's values? For `dominance_shift`: does it change category proportions over time? Shift measure values for the dominant category? For `convergence`: does it reduce variance over time? Compress means toward the grand mean? For `seasonal_anomaly`: does it add an additive shift during a specific season? Multiply seasonal values by a factor?

3. **L3 validation check per type (subtasks 8.4.4–8.4.7).** For `ranking_reversal`: the pseudocode exists but hard-codes `list(meta["dimension_groups"].keys())[0]` as the grouping axis (finding C11), producing incorrect results if the first group is wrong. For `dominance_shift`: delegates to an undefined function (C10). For `convergence` and `seasonal_anomaly`: no branch exists.

4. **Auto-fix strategy coverage.** Should `amplify_magnitude` apply to all pattern types? Does "magnitude" mean the same thing for convergence (variance reduction rate?) as for outlier (z-score)?

5. **L2/L3 interaction per pattern type.** Each injection algorithm will distort the underlying distribution in a specific way. The post-processing invariant contract (Blocker 5) needs to know what each pattern does to determine whether L2 must exclude pattern-target rows.

#### E. Plausible interpretation / decision options

**Option 1: Fully specify all four types now.** For each type, define (params_schema, injection_algorithm, L3_check) as a co-designed triple. This enables the full 6-type pattern system. Highest design effort.

Plausible designs (implied by pattern names and the spec's hospital scenario context):

- **ranking_reversal:** params `{metrics: [str, str], group_col: str, target_entity: str}`. Injection: swap the relative means of two measures for the target entity vs. others. L3 check: verify that the rank order of `metrics` for `target_entity` differs from the global rank order.
- **dominance_shift:** params `{group_col: str, dominant_before: str, dominant_after: str, shift_point: date}`. Injection: adjust category proportions or measure values so that the dominant entity changes at the shift point. L3 check: verify top-ranked entity differs before vs. after `shift_point`.
- **convergence:** params `{group_col: str, measure: str, rate: float}`. Injection: reduce inter-entity variance over time by compressing entity means toward the grand mean. L3 check: verify that the coefficient of variation of entity means decreases over the temporal range.
- **seasonal_anomaly:** params `{season: str, measure: str, multiplier: float}`. Injection: scale measure values during the specified season by `multiplier`. L3 check: verify that the seasonal mean differs from the non-seasonal mean by at least `(multiplier - 1) * baseline_mean * threshold`.

**Option 2: Defer the four types; ship with 2 of 6.** Mark the four types as `NotImplementedError` in the engine and SDK. The system ships with `outlier_entity` and `trend_break` only. This unblocks the architecture — the pipeline orchestrator can be wired with 2 working pattern types — and defers the design work to a future iteration.

**Option 3: Specify 2 additional types now; defer 2.** Design `ranking_reversal` and `seasonal_anomaly` (arguably the most useful for narrative-driven scenarios) and defer `dominance_shift` and `convergence`. A middle ground.

#### F. Recommended clarification priority

**Decide first:** Whether to specify all four now, defer all four, or pick a subset. This is a scope decision, not a technical one. The system is architecturally functional with 2 pattern types. The four unspecified types are feature additions, not structural requirements.

**If specifying:** Design each type as a (params, injection, validation) triple in a single pass. Do not design params first and injection later — the coupling is too tight. Each triple requires approximately one page of specification.

**If deferring:** Add explicit `NotImplementedError("BLOCKED: pattern type '{type}' is not yet specified")` stubs in the SDK validation, engine injection, and L3 validator. Ensure the `inject_pattern` API still accepts the type names (for forward compatibility) but the engine and validator reject them at runtime.

**Why:** The four unspecified types block 9 subtasks, but those subtasks are all in the same feature slice (pattern injection + L3 validation). They do not block the metadata schema, the formula DSL, the distribution families, or the auto-fix loop. Deferring them reduces the blocked backlog from 34 to 25 without affecting the critical path.

#### G. Evidence

- §2.1.2 (spec lines 127–129): six pattern type names; only two have examples
- §2.9 L3 (spec lines 647–676): validation pseudocode for 4 types, but `ranking_reversal` hard-codes grouping (C11), `dominance_shift` delegates to undefined function (C10), `convergence`/`seasonal_anomaly` have no branch (C1)
- Gap analysis findings A8 (CRITICAL), B6 (CRITICAL), C1 (MODERATE), C10 (MODERATE)
- Alignment map Blocker 4: 9 BLOCKED subtasks across 3 modules

---

### 2.5 Post-Processing Invariant Contract (Findings B2, B3, B7, C5, C6)

#### A. System-level reason

The §2.8 engine pipeline has four sequential phases: α (skeleton), β (measures), γ (pattern injection), δ (realism injection). Each phase transforms the data in ways that may violate invariants established by previous phases. The §2.9 validator then runs on the final output — but its checks were designed against the Phase β output, not the Phase γ/δ output. The result is a validator that is structurally incompatible with the data it validates.

This is compounded by a second problem: the auto-fix pseudocode contains a **logical contradiction** where fix strategies modify parameters (lines 695–698) and then the next iteration calls `build_fn(seed=42+attempt)` (line 691), which re-executes the original LLM script from scratch, discarding all parameter modifications. This is not an ambiguity — it is two lines of pseudocode that undo each other.

The core mental model that is missing is: **a multi-phase transformation pipeline needs an explicit invariant contract specifying what properties each phase preserves and what validation applies to each phase's output.** Without this, the validation system checks properties that the data no longer has (because a later phase deliberately destroyed them) and the auto-fix system repairs properties that the next regeneration will re-break.

#### B. Abstraction-level gap

**Execution model / validator contract / auto-fix contract — jointly.** Three abstractions are missing:

1. **Post-processing invariant contract (execution model):** For each engine phase (α, β, γ, δ), what properties of the data are established and what properties may be violated? For each validation layer (L1, L2, L3), which phase's output should it validate?

2. **Auto-fix mutation model (auto-fix contract):** What object does a fix strategy mutate? The `FactTableSimulator` instance? The `Check` object? The DataFrame directly? And how does the retry loop re-generate after mutation — by calling `sim.generate()` (preserving mutations) or `build_fn(seed+attempt)` (discarding them)?

3. **Validation-phase assignment (validator contract):** The specific assignment of {L1, L2, L3} × {Phase β output, Phase γ output, Phase δ output, final output}. This determines whether L2 sees pre-injection or post-injection data.

These three are coupled: the invariant contract determines which checks apply where, which determines what the auto-fix must repair, which determines what the mutation model must support.

#### C. Architecture-level consequence

1. **Validator orchestrator design (subtask 8.1.3, deferred).** The `validate(df, meta)` method cannot be implemented without knowing whether to pass pre-injection data to L2 and post-injection data to L3. If a single DataFrame is passed, L2 and L3 validate the same data — but L2 checks properties that L3-targeted patterns deliberately violate.

2. **Auto-fix retry loop architecture (subtask 9.3.1, SPEC_INCORRECT).** The retry loop cannot be implemented as specified because the pseudocode is self-contradictory. An implementer must choose between: (a) the loop calls `sim.generate()` directly (preserving fix mutations), contradicting `build_fn(seed+attempt)`; or (b) the loop calls `build_fn(seed+attempt)` (discarding fixes), rendering fix strategies ineffective. Neither option matches the spec.

3. **Fix strategy interaction model.** The `widen_variance` strategy (for KS failures) and `amplify_magnitude` strategy (for pattern failures) can target the same column. If L2 runs post-injection, `widen_variance` fights `amplify_magnitude` — widening variance weakens the pattern signal, triggering L3 failure, triggering `amplify_magnitude`, which re-distorts the distribution, triggering L2 failure again. This oscillation makes the auto-fix loop non-convergent.

4. **Pipeline orchestrator composition (subtasks 11.1.1, 11.1.2).** The orchestrator composes the §2.7 execution-error loop with the §2.9 auto-fix loop. The composition is inferable as sequential (§2.7 step 3: "SUCCESS → proceed to ... Validation"), but the total budget, escalation policy, and the question of whether §2.9 failure can escalate back to §2.7 are all undefined.

5. **L1 finiteness vs. realism (finding C6).** L1 asserts `notna().all()` for measures. Phase δ introduces NaN at `missing_rate`. If L1 runs on final output, it always fails when realism is active. If L1 runs pre-realism, a separate realism-rate check is needed. The validator architecture must account for this.

#### D. Implementation-level decisions blocked

1. **Validation phase assignment.** The single most important decision: does L2 run on Phase β output (pre-injection) or on final output (post-injection)? This determines whether L2 KS tests ever interact with pattern injection, which determines whether the L2/L3 oscillation exists. Per the gap analysis (B2), running L2 on Phase β output is the cleanest resolution.

2. **Auto-fix mutation target.** What does `widen_variance(check, factor=1.2)` actually modify? Options: (a) the `FactTableSimulator` instance's `_columns["wait_minutes"].param_model.sigma` value (persistent across retries); (b) the `Check` object's metadata (lost on re-generation); (c) the DataFrame directly (post-hoc adjustment, not re-generation). The pseudocode's use of `build_fn` implies (b) or (c), but both are ineffective.

3. **Retry loop callable.** What function does the retry loop invoke on each iteration? `build_fn(seed=42+attempt)` (as written in pseudocode — re-runs the original LLM script, discards all fixes) or `sim.generate()` (requires the loop to hold a reference to a mutable simulator instance)? This is a binary architectural decision.

4. **Loop composition semantics.** Are the §2.7 and §2.9 loops sequential (§2.7 runs to completion, then §2.9 runs on the result) or nested (each §2.7 iteration includes a full §2.9 sub-loop)? The task hierarchy (11.1.4) and gap analysis (C5) both interpret the spec as sequential, but this is inference, not specification.

5. **Total budget and escalation policy.** Sequential composition implies 3 LLM calls + 3 engine re-runs = 6 total attempts. Nested implies up to 3 × 3 = 9 LLM calls. The spec does not state the budget. The task hierarchy assumes 6 (no escalation).

6. **Soft-fail contract (finding C12).** When the auto-fix loop exhausts retries, the pipeline returns a soft-fail `(df, report)` tuple. What does Phase 3 do with failed data? Is there a quality threshold below which the data is rejected entirely? The spec does not define the soft-fail contract.

7. **`reshuffle_pair` interaction with patterns.** Reshuffling a column to fix an orthogonal failure may destroy patterns whose `target` expression references that column. Should `reshuffle_pair` exclude pattern-target columns?

#### E. Plausible interpretation / decision options

**On validation phase assignment:**

**Option A: Phase-segregated validation.** L1 structural checks run on Phase β output (pre-injection) except for realism-aware finiteness which runs post-δ with adjusted threshold. L2 statistical checks run on Phase β output. L3 pattern checks run on Phase γ output. Separate realism-rate check runs post-δ. This cleanly separates concerns and eliminates the L2/L3 oscillation. The engine must expose intermediate Phase β output.

**Option B: Single-pass validation with exclusion masks.** All checks run on final output, but L2 excludes rows matched by pattern `target` expressions from KS tests. L1 finiteness threshold is adjusted for `missing_rate`. This preserves the current single-DataFrame architecture but adds complexity to L2 (target expression parsing for exclusion) and L1 (conditional thresholds).

**Option C: Two-pass validation.** The engine runs `generate()` twice — once without patterns/realism for L1+L2, once with patterns/realism for L3+delivery. Deterministic seeds ensure reproducibility. Simple but doubles generation cost.

**On auto-fix mutation model:**

**Option X: Mutate simulator instance; retry with `sim.generate()`.** Fix strategies modify the `FactTableSimulator`'s internal declarations (e.g., increase `sigma` in `_columns["wait_minutes"].param_model`). The retry loop calls `sim.generate()` directly with an incremented seed. This is the only option where fixes persist across retries. It contradicts the pseudocode's `build_fn` but is the only functionally correct option.

**Option Y: Post-process the DataFrame after each `generate()`.** Fix strategies apply adjustments to the DataFrame (e.g., scale values to widen variance) rather than modifying declarations. This avoids mutation but means the fixed data no longer matches the declared distribution — validation against declared parameters will still fail.

**Option Z: Modify the SDK script source and re-execute.** Fix strategies edit the Python script text (e.g., change `sigma=0.35` to `sigma=0.42`) and re-execute. This is the most faithful to the `build_fn` pattern but is fragile (string manipulation of code) and expensive (re-parsing and re-executing).

#### F. Recommended clarification priority

**Decide first:** Validation phase assignment (Option A vs. B vs. C). This resolves the L2/L3 oscillation, the L1/realism conflict, and determines the validator orchestrator architecture. Option A (phase-segregated) is the cleanest and is recommended by the gap analysis (B2). It requires the engine to expose Phase β output, which is a small API change.

**Decide second:** Auto-fix mutation model (Option X vs. Y vs. Z). This resolves the pseudocode contradiction and determines the retry loop's callable. Option X (mutate instance, call `sim.generate()`) is the only functionally correct option and is recommended by the gap analysis (B3, B7). It requires the retry loop to hold a reference to the mutable `FactTableSimulator` instance.

**Decide third:** Loop composition semantics. The sequential interpretation (§2.7 then §2.9, no escalation, total budget 6) is well-supported by §2.7 step 3 wording and can be adopted as the resolution.

**Can wait:** Soft-fail contract (what Phase 3 does with failed data), `reshuffle_pair` pattern-column exclusion, auto-fix strategy coverage expansion (finding C4).

**Why this order:** The validation phase assignment is the most consequential architectural decision — it determines whether L2 and L3 can coexist without oscillation, which determines whether the auto-fix loop can converge, which determines whether the pipeline orchestrator produces usable output. The mutation model is second because it determines the retry loop's implementation. The loop composition is third because it is largely inferable from the spec and adds less risk.

#### G. Evidence

- §2.8 (spec): four-phase engine pipeline (α, β, γ, δ) with no inter-phase invariant contract
- §2.9 (spec lines 574–575 vs. 582–584): L1 finiteness contradicts realism NaN
- §2.9 (spec lines 613–621): L2 KS on post-injection data vs. pre-injection parameters
- §2.9 (spec lines 691–698): fix strategies applied then discarded by `build_fn` re-execution
- §2.7 step 3: "SUCCESS → proceed to ... Validation (§2.9)" — sequential composition implied
- Gap analysis findings B2 (CRITICAL), B3 (CRITICAL), B7 (MODERATE), C5 (MODERATE), C6 (MODERATE)
- Alignment map Blocker 5: 1 SPEC_INCORRECT directly, 8+ degraded indirectly
- Task hierarchy 9.3.1 (SPEC_INCORRECT), 11.1.1–11.1.2 (BLOCKED)

---

### 2.6 Phase 1 → Phase 2 Interface Contract (Finding D1)

#### A. System-level reason

Phase 2 receives a scenario context from Phase 1 and uses it to populate the LLM prompt (§2.5 `{scenario_context}` placeholder). The working system already passes this as a JSON blob via `json.dumps(scenario, indent=2)`. What is missing is a typed, validated, versioned contract — a formal definition of what fields the scenario must contain, what types they have, and how to validate completeness.

The core mental model that is not missing but is only partially formalized: the scenario context is a **cross-phase boundary object** that must be defined at the interface, not inferred from implementation. A de facto schema exists (enforced by `ScenarioContextualizer.validate_output()` in Phase 1), but it is not expressed as a formal type.

#### B. Abstraction-level gap

**Inter-phase contract / declaration model.** The missing abstraction is a **typed scenario context schema** — a formal definition of `ScenarioContext` as a data structure with required fields, optional fields, types, and validation rules. This is a declaration model gap at the inter-phase boundary.

Note: The Stage 2 blocker decomposition correctly observes that this is a formalization blocker, not a capability blocker. The basic injection path works. The remaining gap is about typed interface completeness.

#### C. Architecture-level consequence

1. **Prompt template builder (Module 10).** The prompt template (10.1.1) can render `{scenario_context}` from a raw dict, but cannot validate completeness without a schema. If Phase 1 produces a scenario missing `target_rows`, the prompt is malformed and the LLM generates incorrect code.

2. **Pipeline orchestrator entry point (Module 11).** The orchestrator accepts a scenario from Phase 1 and passes it to the prompt builder. Without a typed contract, error handling for malformed scenarios is ad hoc (catching `KeyError` vs. validating upfront).

3. **Integration testing.** End-to-end tests need fixture scenarios. Without a formal schema, fixtures are copies of the one-shot example rather than validated against a contract.

#### D. Implementation-level decisions blocked

1. **`ScenarioContext` class design.** Dataclass vs. Pydantic model vs. TypedDict. Field names, types, required/optional status.

2. **Required fields.** The de facto set from `ScenarioContextualizer.validate_output()`: `scenario_title: str`, `data_context: str`, `key_entities: list[dict]`, `key_metrics: list[dict]`, `temporal_granularity: dict`, `target_rows: int`. Are all of these required? Are there additional fields?

3. **Serialization format.** JSON (current)? Dataclass-to-dict? Pydantic `.model_dump()`? The prompt template needs a string representation.

4. **Version field.** Should `ScenarioContext` include a `version` field for forward compatibility between Phase 1 and Phase 2?

#### E. Plausible interpretation / decision options

**Option 1: Formalize the de facto schema as a Pydantic `BaseModel`.** Take the six fields from `ScenarioContextualizer.validate_output()`, add types and validation, add an optional `version` field. This is the minimal change that formalizes the existing working interface.

**Option 2: Co-design with the `result_models.py` design from the pipeline redesign audit.** The alignment map v4 notes that `audit/5_agpds_pipeline_runner_redesign.md` already contains a `ScenarioContext` design. Adopt it as the starting point.

**Option 3: Defer formalization; proceed with the raw dict interface.** Accept the `json.dumps` path as "good enough" for Phase 2. Formalize when Phase 3 integration requires it.

#### F. Recommended clarification priority

**Decide first:** The required field list and types. This is a small decision that can be made by examining the existing `ScenarioContextualizer.validate_output()` code and the §2.5 prompt template.

**Can wait:** Versioning, serialization format, Pydantic vs. dataclass. These are engineering quality decisions, not correctness decisions.

**Why:** This blocker affects only 2 subtasks (10.1.2, 11.1.1) and is partially mitigated. It should not consume decision bandwidth before the three foundational blockers are resolved.

#### G. Evidence

- §2.5 (spec lines 387–389): `{scenario_context}` placeholder with no schema
- Alignment map Blocker 6: 2 BLOCKED subtasks, softened in v3
- Alignment map v4 annotation: references `audit/5_agpds_pipeline_runner_redesign.md` design
- Task hierarchy 10.1.2 (BLOCKED), 11.1.1 (BLOCKED on this + C5)
- Existing code: `ScenarioContextualizer.validate_output()` enforces de facto field set

---

### 2.7 Cross-Group Default Semantics (Finding A12)

#### A. System-level reason

When two dimension groups have neither a `declare_orthogonal()` nor an `add_group_dependency()` declaration, the spec does not define how their root columns are sampled relative to each other. §2.2 states cross-group independence is "opt-in, not default" but never defines the actual default. With N dimension groups, there are O(N²) pairwise relationships, and the LLM is only required to declare at least one `declare_orthogonal()` — most pairs will have no explicit declaration.

The core mental model that is unstable is: **"opt-in, not default" implies a non-independence default exists, but no such default is specified.** The most natural implementation (treat undeclared pairs as independent) directly contradicts the "not default" language.

#### B. Abstraction-level gap

**Dependency model / execution model.** The missing abstraction is the **default cross-group sampling policy** — a rule for how the skeleton builder samples root columns from two groups that have no explicit pairwise declaration. This is a dependency model gap: the spec defines two explicit modes (orthogonal, dependent) but not the implicit mode.

#### C. Architecture-level consequence

The skeleton builder (4.1.1) must decide at generation time how to sample undeclared pairs. The current assumption (independent sampling via `rng.choice` per group) is the simplest and is documented. The risk is that this assumption is later rejected, requiring a change to the sampling algorithm.

The validator's orthogonal check (8.2.5) only tests declared orthogonal pairs. If undeclared pairs are assumed independent, there is no check verifying this assumption. If undeclared pairs are not independent, there is no check detecting the dependency.

#### D. Implementation-level decisions blocked

1. **Skeleton builder sampling logic (subtask 4.1.1).** Independent sampling? Joint sampling from an implicit distribution? Rejection of the scenario if not all pairs are declared?

2. **Validator coverage for undeclared pairs.** Should L1 include a check for undeclared pairs? What should the check verify?

3. **LLM prompt guidance.** Should the prompt instruct the LLM to declare all pairs? Warn about undeclared pairs?

#### E. Plausible interpretation / decision options

**Option 1: Default to independent.** Undeclared pairs are sampled independently. This contradicts the "opt-in, not default" language but is the simplest, most predictable behavior. The spec's language may have been aspirational rather than prescriptive.

**Option 2: Require exhaustive pairwise declarations.** The LLM must declare every pair of groups as either orthogonal or dependent. The SDK rejects scenarios with undeclared pairs. This is the cleanest semantically but most constraining for the LLM.

**Option 3: Default to "weakly correlated" with a small, unspecified correlation.** This respects the "not default" language but introduces an unparameterized dependency that is hard to validate and hard to explain.

#### F. Recommended clarification priority

**Can wait.** The current assumption (Option 1: independent) is documented and confined to a single method. No hard-blocked subtasks depend on this decision. If the decision changes later, the impact is limited to `_build_skeleton` and possibly a new L1 check.

#### G. Evidence

- §2.2 (spec line 153): "Cross-group independence is opt-in, not default"
- §2.1.2 prompt hard constraint 4: "at least 1 `declare_orthogonal()`" — not exhaustive
- Gap analysis finding A12 (CRITICAL, post-audit)
- Alignment map 4.1.1: NEEDS_CLARIFICATION with documented assumption

---

### 2.8 Censoring Schema (Finding A4)

#### A. System-level reason

The `censoring` parameter in `set_realism()` appears in the method signature and in the engine pipeline but has no type annotation, schema, or semantic definition. This is the simplest blocker — a single API parameter with no definition.

#### B. Abstraction-level gap

**Declaration model / metadata model.** The missing abstraction is the censoring specification schema — what does the `censoring` dict contain? This is a narrow gap in the declaration model for the realism subsystem.

#### C. Architecture-level consequence

Confined to the realism injection module (Phase δ). The metadata has no field to record censoring for Phase 3. The validator has no adjustment for censored columns (L2 KS tests will fail on censored distributions).

#### D. Implementation-level decisions blocked

1. **Censoring dict schema.** Target column(s), direction (left/right/interval), threshold value(s), indicator column creation.
2. **Metadata representation of censoring.**
3. **L2 adjustment for censored columns.**

#### E. Plausible interpretation / decision options

**Option 1: Minimal censoring schema.** `{"columns": ["cost"], "direction": "right", "threshold": 10000}`. Right-censoring clips values above the threshold. Left-censoring clips below. Interval censoring clips both. An optional indicator column marks censored rows.

**Option 2: Defer entirely.** The `censoring=None` default path works. Censoring is optional. Defer specification to a future version.

#### F. Recommended clarification priority

**Can wait.** Only 1 subtask (4.4.3) is blocked. Censoring is optional. Resolve opportunistically after the three foundational blockers.

#### G. Evidence

- §2.1.2 (spec line 129): `censoring` in signature with no definition
- Gap analysis finding A4 (MODERATE)
- Alignment map Blocker 7: 1 BLOCKED subtask

---

## 3. Cross-Blocker Synthesis

### 3.1 Blockers sharing the same missing abstraction

**Declaration model / entity model** underpins three blockers:

- Blocker 1 (metadata schema) — the serialized form of the declaration model
- Blocker 3 (distribution families) — the parametric part of the declaration model
- Blocker 8 (censoring schema) — a narrow corner of the realism declaration model

These three share the root cause: the spec defines what the LLM writes (the SDK API surface) but not what the system records (the internal data model) or what it communicates downstream (the metadata model). Resolving the declaration model — "what fields describe each entity type, and how are they serialized" — addresses all three.

**Expression model** is specific to Blocker 2 (formula DSL). No other blocker shares this abstraction gap.

**Execution model** underpins two blockers:

- Blocker 5 (post-processing invariant contract) — the execution model for the multi-phase pipeline
- Blocker 7 (cross-group default semantics) — the execution model for the skeleton builder

**Behavioral triple model** is specific to Blocker 4 (pattern types). This is a unique gap where three tightly coupled abstractions must be co-designed.

### 3.2 Decisions that would unlock the largest amount of implementation work

Ordered by downstream subtask count:

1. **Metadata schema field specification** — directly unblocks 9 SPEC_INCORRECT subtasks (5.1.3, 5.1.4, 5.1.6, 8.2.3, 8.2.4, 8.3.3, 8.3.4, 8.3.6, 8.4.2); indirectly enables the auto-fix retry loop (9.3.1) and pipeline orchestrator (11.1.1, 11.1.2). **~12 subtasks enabled.**

2. **Distribution family reference table** — directly unblocks 7 BLOCKED subtasks (1.4.3, 1.4.4/deferral, 1.5.4, 4.2.1, 4.2.2, 8.3.1, 8.3.2). **7 subtasks enabled.**

3. **Formula DSL operator whitelist** — directly unblocks 4 BLOCKED subtasks (1.5.2, 4.2.5/4.2.8, 8.3.5) plus enables DAG edge type 5. **4+ subtasks enabled.**

4. **Validation phase assignment** — directly unblocks 1 SPEC_INCORRECT subtask (9.3.1) and resolves the degradation for 8+ subtasks. Enables the auto-fix loop and pipeline orchestrator. **~9 subtasks unlocked** (overlapping with metadata).

5. **Pattern type triples** — directly unblocks 9 BLOCKED subtasks. **9 subtasks enabled** but all in the same feature slice.

### 3.3 Blockers caused by incomplete system model vs. hard coding work

**Incomplete system model (the system design is unfinished):**

- Blocker 1 (metadata schema) — the metadata contract was never formally designed
- Blocker 2 (formula DSL) — the expression language was never formally specified
- Blocker 3 (distribution families) — the parametric reference table was never created
- Blocker 5 (post-processing invariant) — the multi-phase execution model was never formalized
- Blocker 7 (cross-group defaults) — the dependency model has an undefined case

**Hard coding work (the design is clear but the implementation is non-trivial):**

- Blocker 4 (pattern types) — the design work is genuinely creative (inventing injection algorithms and validation checks), not just formalizing existing concepts
- Blocker 8 (censoring) — small but requires a design decision about semantics

The first group (5 blockers) is where clarification effort should be concentrated. These are not coding bottlenecks — they are design specification bottlenecks. An engineer cannot resolve them by writing code; they require a spec author or architect to make decisions. The second group (2 blockers) can be resolved by an engineer making design decisions within the spirit of the spec.

---

## 4. Final Takeaway

### The few deepest root problems

The Phase 2 specification describes a system that is conceptually well-architected (producer-consumer pipeline with declarative SDK, deterministic engine, and three-layer validation) but **has not completed the intermediate design layer** between product concepts and implementation code. Specifically:

1. **The declaration model is implicit.** The SDK API defines what the LLM writes, and the metadata example shows a partial serialization, but the canonical data model — what fields describe each entity type — is scattered across API signatures, pseudocode examples, and inference. There is no single source of truth for "what does the system know about a stochastic measure?" or "what does the system know about a group dependency?"

2. **The execution model has no inter-phase invariant contract.** The engine's four phases (α, β, γ, δ) and the validator's three layers (L1, L2, L3) were designed in isolation. No contract specifies which validation layers apply to which phase's output, creating structural contradictions (L2 vs. patterns, L1 vs. realism).

3. **The parametric dispatch model was never tabulated.** Eight distribution family names are listed, but only two are demonstrated. The mapping from family name → parameter keys → numpy sampling → scipy validation is the kind of reference table that should have been part of the original spec.

### The most important unresolved decisions

In priority order:

1. **Metadata schema field specification** — what fields, what types, for each entity type. (~1 day of design work, unblocks ~12 subtasks)
2. **Distribution family reference table** — 7 rows × 4 columns of lookup data. (~2 hours of design work, unblocks 7 subtasks)
3. **Formula DSL operator whitelist and precedence** — one page of grammar specification. (~1 hour of design work, unblocks 4 subtasks)
4. **Validation phase assignment** — L2 runs pre-injection or post-injection? One architectural decision. (~30 minutes of decision, unblocks the auto-fix loop)
5. **Auto-fix mutation model** — mutate simulator instance and call `generate()`, not `build_fn`. One pseudocode correction. (~30 minutes of decision, fixes the retry loop)

### The shortest path from current ambiguity to implementation-ready clarity

**Step 1 (parallel, ~1 day):** Resolve Blockers 1, 2, and 3 simultaneously. These are independent and together unblock ~23 subtasks. Blocker 1 requires a metadata field table. Blocker 2 requires an operator whitelist. Blocker 3 requires a distribution reference table. All three are documentation tasks, not coding tasks.

**Step 2 (~2 hours):** Resolve Blocker 5 by deciding: (a) L2 runs on Phase β output (pre-injection); (b) auto-fix mutates the simulator instance and retries via `sim.generate()`; (c) loops compose sequentially with budget 3+3=6. These three decisions resolve all SPEC_INCORRECT and degraded subtasks in the auto-fix and pipeline orchestrator path.

**Step 3 (scope decision):** Decide whether to specify the four unspecified pattern types now or defer them. If now, allocate ~1 day for co-designing the four (params, injection, validation) triples. If deferred, add `NotImplementedError` stubs and move on.

**Step 4 (low priority):** Formalize `ScenarioContext` as a typed dataclass. Resolve cross-group default semantics. Define censoring schema. These can be done opportunistically.

After Steps 1 and 2, the system goes from 34 blocked subtasks to approximately 9 (the pattern types, if deferred) or 0 (if all blockers are resolved). The critical path from ambiguity to implementation-ready clarity is approximately **1–2 days of design specification work**, not coding work.
