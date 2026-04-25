# Stage 2 Deep Dive: LLM Orchestration (M3)

## 1. SUMMARY

**What this module does:** M3 prompts an LLM to generate a valid `build_fact_table()` Python script from a Phase 1 scenario context, executes it against the M1 SDK in a sandbox, and retries with error feedback up to three times if the SDK raises a typed exception.

**Most complex section:** §2.5 (LLM Code Generation Prompt) — it must encode the full SDK contract, all nine hard constraints, and a representative one-shot example into a single prompt template that reliably produces valid scripts across arbitrary domains. The prompt is the sole mechanism for constraining LLM behavior, making its completeness and precision critical to system reliability.

**Most significant ambiguity:** The spec does not address what happens when multiple independent SDK errors exist simultaneously. Standard Python exception propagation surfaces only the first error per execution, meaning the LLM fixes one error per retry. With a budget of 3 retries and potentially 3+ independent errors, the retry budget may be systematically insufficient for scripts with many simultaneous violations.

**Specification completeness: Medium.** The prompt template and retry protocol are clearly defined, but sandbox semantics (isolation level, timeout, state reset between retries), the `scale` parameter on `add_measure`, the `mixture` distribution's `param_model` schema, and several pattern type parameter schemas are left unspecified. The interaction boundary between Loop A (M3↔M1) and Loop B (M5→M2) failure modes is also underspecified.

---

## 2. PHASE A: INTERNAL SECTION ANALYSIS

### Section 2.5 — LLM Code Generation Prompt

#### 2.5.1 PURPOSE

This section defines the complete system prompt template that the LLM receives to produce a `build_fact_table()` Python script. It serves as the sole interface between the natural-language scenario context (from Phase 1) and the typed SDK surface (M1) — translating a domain description into executable code. The prompt must be precise enough that the LLM's output satisfies all SDK validation rules on the first attempt (or at least within the retry budget).

#### 2.5.2 KEY MECHANISM

The prompt is a structured template with five distinct zones:

**Role preamble.** Sets the LLM persona as "expert Data Scientist Agent" and names the deliverable — an atomic-grain fact table via the `FactTableSimulator` SDK.

**SDK method whitelist.** Enumerates every legal method call with inline signature comments. This is split into two ordered blocks — "Step 1: Column declarations" (`add_category`, `add_temporal`, `add_measure`, `add_measure_structural`) and "Step 2: Relationships & patterns" (`declare_orthogonal`, `add_group_dependency`, `inject_pattern`, `set_realism`). The two-step grouping mirrors the SDK's own validation constraint that all columns must be declared before any relationships reference them. Supported distribution families and pattern types are listed as flat enumerations.

**Hard constraints (9 rules).** These are binary pass/fail requirements the script *must* satisfy. They enforce: atomic grain semantics (HC1), minimum structural richness — at least 2 dimension groups, 2+ measures, 1 orthogonal declaration, 1 structural measure, 2 pattern injections (HC2–5), pure Python output (HC6), DAG acyclicity for both the measure graph and the root-level cross-group dependency graph (HC7–8), and completeness of symbolic effect definitions (HC9). These constraints collectively guarantee that M1 will not reject the script on structural grounds.

**Soft guidelines.** Non-mandatory suggestions that increase table richness: temporal derivation, within-group hierarchy with per-parent weights, 3+ measures, cross-group dependencies, and realism injection. These are domain-contingent and do not trigger validation failures if omitted.

**One-shot example.** A complete, runnable `build_fact_table(seed=42)` function for a "2024 Shanghai Emergency Records" scenario. It demonstrates every SDK method, both step orderings, and returns `sim.generate()`. The example embeds the exact scenario context block format (`[SCENARIO]` with Title, target_rows, Entities, Metrics, Temporal) followed by the `[AGENT CODE]` block. This establishes the input/output contract for the LLM.

**Template slot.** The final `{scenario_context}` placeholder is where the Phase 1 output is injected at runtime.

#### 2.5.3 INTERNAL DEPENDENCIES

- **Depends on §2.7?** Not structurally — §2.5 defines the *initial* prompt. However, the prompt is designed to be conversation-compatible: §2.7's retry protocol appends code + traceback to the same LLM conversation, meaning the prompt from §2.5 is the `messages[0]` system message that persists across retries. The prompt's structure implicitly assumes a multi-turn conversation model.

#### 2.5.4 CONSTRAINTS & INVARIANTS

**EXPLICIT:**

| ID | Constraint | Type |
|----|-----------|------|
| HC1 | Each row = one indivisible event (atomic grain) | Semantic |
| HC2 | ≥2 dimension groups, each with ≥1 categorical column, plus ≥2 measures | Structural minimum |
| HC3 | All column declarations (Step 1) before any relationship declarations (Step 2) | Ordering |
| HC4 | ≥1 `declare_orthogonal()` between genuinely independent groups | Structural minimum |
| HC5 | ≥1 `add_measure_structural()` + ≥2 `inject_pattern()` | Structural minimum |
| HC6 | Pure, valid Python returning `sim.generate()` | Output format |
| HC7 | Measure dependencies must be acyclic (DAG) | Graph constraint |
| HC8 | Cross-group dependencies only between root columns; root DAG acyclic | Graph constraint |
| HC9 | Every symbolic effect must have an explicit numeric definition | Completeness |

**IMPLICIT:**

- The prompt assumes the LLM will produce a function named `build_fact_table` with a `seed` parameter — this name is referenced by §2.7's retry protocol and §2.9's `generate_with_validation(build_fn, ...)` wrapper, but the prompt does not mark the function signature as a hard constraint.
- The prompt does not explicitly state that weights must sum to 1.0 (the SDK auto-normalizes per §2.1.1), but the one-shot example uses pre-normalized weights, which could mislead the LLM into thinking normalization is required.
- The `scale` parameter on `add_measure` appears in the whitelist but is never used in the one-shot example and is never defined anywhere in the spec. Its semantics are unspecified.
- The prompt does not constrain how many dimension groups or measures are *maximum* — only minimums.
- The prompt does not specify which Python version or import style is expected beyond `from chartagent.synth import FactTableSimulator`.

#### 2.5.5 EDGE CASES

- **Scenario with no temporal component.** The soft guideline says "include when naturally fitting," but the one-shot example always includes temporal. If the LLM omits temporal, there is no temporal group, which could affect pattern types like `trend_break` and `seasonal_anomaly` that implicitly require a temporal column. The prompt does not state whether temporal is required for those pattern types.
- **Scenario with exactly 2 dimension groups and 2 measures.** This is the minimum viable configuration. With only 2 groups, the single required `declare_orthogonal()` locks them as independent, leaving no room for `add_group_dependency()` unless a third group exists. The soft guideline for `add_group_dependency` may be impossible to follow at the minimum richness level.
- **Conflicting hard constraints.** HC4 requires at least one orthogonal pair and HC8 allows cross-group dependencies only between roots. With exactly 2 groups declared orthogonal, declaring a dependency between those same roots would contradict the orthogonality. The prompt does not address whether orthogonality and dependency on the same group pair are mutually exclusive.
- **`mixture` distribution.** Listed as supported but never demonstrated. The `param_model` schema for a mixture (component weights, per-component parameters) is unspecified in the prompt.
- **`convergence` and `seasonal_anomaly` pattern types.** Listed but not demonstrated in the one-shot. Parameter schemas for these are unspecified.
- **Multi-column `on` in `add_group_dependency`.** The signature shows `on` as a list, and the one-shot uses `on=["severity"]` (single element). Behavior with multiple conditioning roots (e.g., `on=["severity", "hospital"]`) would require a nested conditional weight dict whose structure is not shown.
- **Empty `derive` list on `add_temporal`.** Presumably legal but untested — the temporal group would have only the root date column.
- **`censoring` parameter in `set_realism`.** Appears in the signature but is `None` by default and never elaborated.

---

### Section 2.7 — Execution-Error Feedback Loop

#### 2.7.1 PURPOSE

This section defines the retry protocol for when the LLM's generated script fails during sandbox execution against M1's SDK. It closes the feedback loop between M3 and M1 (Loop A in the module interaction chain), enabling the LLM to self-correct semantic authoring errors — cyclic dependencies, undefined effects, non-root cross-group dependencies, degenerate distributions — up to a bounded retry limit.

#### 2.7.2 KEY MECHANISM

The protocol is a sequential six-step pipeline:

1. **LLM outputs Python script** — the initial generation from §2.5's prompt.
2. **Sandbox executes `build_fact_table()`** — the SDK methods in M1 run; every `add_*()` / `declare_*()` / `inject_*()` call performs inline validation.
3. **SUCCESS branch** — if no exception is raised, the script artifact passes downstream to M2 (§2.8) and M4 (§2.6). The loop terminates.
4. **FAILURE branch** — M1 raises a *typed* exception. The spec names three specific exception classes as examples: `CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`. Each carries a structured error message describing the exact constraint violation.
5. **Feedback injection** — the orchestrator appends both the failing code and the full traceback to the LLM conversation history, along with a re-prompt instruction: "Adjust parameters to resolve the error."
6. **Retry gate** — if `attempt < max_retries` (3), loop back to step 1 (LLM re-generates). If all retries exhausted, log and skip the scenario entirely.

The key architectural property is that each retry involves an LLM call — this is what distinguishes Loop A (code-level self-correction, with LLM) from Loop B (statistical auto-fix in M5, no LLM). The two loops are nested: Loop A is the outer loop; Loop B only executes after Loop A succeeds.

#### 2.7.3 INTERNAL DEPENDENCIES

- **Depends on §2.5:** The initial prompt from §2.5 is the conversation's system message. The retry protocol appends to this conversation, so the prompt structure and one-shot example remain visible to the LLM across retries.
- **Consumes from M1 (external):** Typed `Exception` objects with structured messages. The quality of self-correction depends entirely on the specificity of M1's error messages.

#### 2.7.4 CONSTRAINTS & INVARIANTS

**EXPLICIT:**

| ID | Constraint |
|----|-----------|
| R1 | Maximum 3 retries (`max_retries=3`) |
| R2 | On terminal failure (all retries exhausted), log and skip — no fallback generation |
| R3 | Each retry involves an LLM call (the code + traceback are appended to the conversation) |
| R4 | The re-prompt instruction is "Adjust parameters to resolve the error" |

**IMPLICIT:**

- The spec implies the conversation is *appended to*, not *replaced* — meaning the LLM sees all prior failed attempts and their tracebacks. This is a multi-turn conversation, not independent single-shot generations. This is important because it means the context window grows with each retry.
- The spec does not state whether the retry counter resets if the script fails at a *different* error than the previous attempt. The phrasing "max_retries=3" suggests a flat budget regardless of error diversity.
- The "log and skip" terminal action implies the existence of a scenario-level orchestration loop outside M3 that can tolerate individual scenario failures. This upstream loop is not specified in Phase 2.
- The spec does not define what constitutes the "sandbox" — whether it's a subprocess, an `exec()` call, or a containerized environment. The isolation level affects security and error propagation behavior.

#### 2.7.5 EDGE CASES

- **Multiple simultaneous errors.** If the script triggers two SDK exceptions (e.g., both a cyclic dependency and an undefined effect), only the first exception propagates (standard Python behavior). The LLM fixes one error per retry, potentially requiring all 3 retries for 3 independent errors. With exactly 3 retries and 3+ independent errors, the budget may be insufficient.
- **Non-SDK exceptions.** The spec only discusses typed SDK exceptions. A `SyntaxError`, `NameError`, or other Python runtime error in the LLM's code is not addressed. Presumably the traceback would still be appended, but the error message would not be a structured SDK violation — it would be a raw Python traceback, which may be less actionable for the LLM.
- **LLM generates identical code on retry.** The spec does not address the degenerate case where the LLM re-produces the same failing code despite seeing the traceback. All 3 retries would fail identically.
- **Partial execution.** If the script executes 8 of 10 `add_*()` calls successfully before the 9th raises an exception, the SDK's internal state is partially populated. The spec does not state whether the SDK state is reset between retries or whether `FactTableSimulator` is re-instantiated. Logically, a fresh `FactTableSimulator(target_rows, seed)` must be created each time, but this is not stated.
- **Context window exhaustion.** With 3 retries, the conversation accumulates the system prompt + scenario context + up to 3 full code blocks + 3 tracebacks. For complex scenarios, this could approach context limits. No truncation or summarization strategy is specified.
- **Timeout.** No execution timeout is specified for the sandbox. A script with an infinite loop or extremely large `target_rows` could hang indefinitely.
- **Interaction with Loop B.** The spec states Loop B only runs after Loop A succeeds. But what if Loop A succeeds (valid script) and then Loop B exhausts its own 3 retries (statistical failures)? The spec does not say whether this triggers a re-entry into Loop A with a request to adjust parameters for better statistical properties. The stage1 module map confirms Loop B does *not* feed back into Loop A — it is a soft failure.

---

## 3. PHASE B: INTRA-MODULE DATA FLOW

### 3.1 ASCII Data Flow Diagram

```
                    ┌─────────────────────────────────────┐
                    │        M3: LLM ORCHESTRATION        │
                    │                                     │
  Phase 1           │                                     │
  scenario_context ─┼──►┌─────────────────────────┐       │
  dict              │   │                         │       │
                    │   │  §2.5 LLM Code          │       │
                    │   │  Generation Prompt       │       │
                    │   │                         │       │
                    │   │  Assembles:             │       │
                    │   │  • system prompt         │       │
                    │   │  • SDK whitelist         │       │
                    │   │  • hard constraints      │       │
                    │   │  • one-shot example      │       │
                    │   │  • scenario slot fill    │       │
                    │   │                         │       │
                    │   └────────────┬────────────┘       │
                    │                │                     │
                    │        (A) assembled_prompt          │
                    │        (complete LLM system          │
                    │         message + user turn)         │
                    │                │                     │
                    │                ▼                     │
                    │   ┌─────────────────────────┐       │
                    │   │                         │       │
                    │   │  §2.7 Execution-Error   │◄──────┼── typed Exception
                    │   │  Feedback Loop          │       │    from M1 (SDK)
                    │   │                         │       │
                    │   │  1. Send prompt to LLM  │       │
                    │   │  2. Receive script       │       │
                    │   │  3. Execute in sandbox ──┼───────┼──► Python script
                    │   │  4. If exception:        │       │    to M1 sandbox
                    │   │     append code+trace    │       │
                    │   │     to conversation      │       │
                    │   │     retry (≤3)           │       │
                    │   │  5. If success:          │       │
                    │   │     emit script artifact │       │
                    │   │  6. If terminal failure: │       │
                    │   │     emit skip signal     │       │
                    │   │                         │       │
                    │   └────────────┬────────────┘       │
                    │                │                     │
                    │        (B) FINAL OUTPUT              │
                    │        one of:                       │
                    │        • validated Python script ────┼──► M1 (declaration
                    │          (build_fact_table())        │    store) → M2, M4
                    │        • logged skip signal ────────┼──► upstream
                    │                                     │    orchestrator
                    └─────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────┐
  │  RETRY DETAIL (inside §2.7)                              │
  │                                                          │
  │  conversation_history = [system_prompt_from_§2.5]        │
  │                                                          │
  │  for attempt in 0..max_retries:                          │
  │      script = LLM(conversation_history)                  │
  │      conversation_history.append(assistant: script)      │
  │      try:                                                │
  │          sandbox_exec(script)  ──► M1 SDK validates      │
  │          return script  ✓                                │
  │      except SDKException as e:                           │
  │          conversation_history.append(user: code+trace)   │
  │                                                          │
  │  return SKIP  ✗                                          │
  └──────────────────────────────────────────────────────────┘
```

### 3.2 INTERNAL STATE

M3 has one piece of accumulating internal state: the **LLM conversation history**. This is the critical stateful object that ties §2.5 and §2.7 together.

**Initial state (set by §2.5):**

The conversation begins with one message — the assembled system prompt. This contains the role preamble, SDK whitelist, hard constraints, soft guidelines, one-shot example, and the filled `{scenario_context}`. This message is immutable across retries.

**Growth per retry iteration (managed by §2.7):**

Each failed attempt appends two messages to the conversation:

- An **assistant turn** containing the LLM's generated Python script.
- A **user turn** containing the failing code, the full traceback, and the re-prompt instruction ("Adjust parameters to resolve the error").

So after *n* failed attempts, the conversation contains:

```
messages[0]:       system prompt from §2.5          (fixed)
messages[1]:       assistant — script attempt 1      (attempt 0)
messages[2]:       user — code + traceback 1         (attempt 0 failure)
messages[3]:       assistant — script attempt 2      (attempt 1)
messages[4]:       user — code + traceback 2         (attempt 1 failure)
...
messages[2n-1]:    assistant — script attempt n
messages[2n]:      user — code + traceback n
messages[2n+1]:    assistant — script attempt n+1    (final attempt)
```

At maximum retries (3 failures), the conversation holds 1 system message + up to 6 user/assistant turns + 1 final assistant turn = **8 messages**. The total token count scales with script length × 4 (attempts) + traceback length × 3 (failures).

No other internal state accumulates. M3 does not maintain a declaration store, a DataFrame, or any metadata — those are M1's responsibility. M3's sole job is to produce a valid script string.

### 3.3 ORDERING CONSTRAINTS

**Explicitly stated:**

- §2.5 executes before §2.7 — the prompt must be assembled before any LLM call or retry can occur.
- Within §2.7, the retry loop is strictly sequential: execute → check → (fail → append → re-prompt) or (succeed → exit).

**Implicitly required but not stated:**

- **Prompt assembly is a one-time operation.** The spec does not say whether the system prompt from §2.5 can be modified between retries (e.g., to add hints based on the error type). The current design treats it as frozen. This is implied by the append-only conversation model but never stated as a constraint.
- **Sandbox re-instantiation.** Each retry must execute against a fresh `FactTableSimulator` instance. The spec describes appending code + traceback to the conversation, but never states that the sandbox environment is reset. This is logically necessary — a partially-populated SDK instance from a failed attempt would corrupt the next attempt — but is implicit.
- **M3 must fully terminate (success or skip) before M1's declaration store is considered frozen.** The stage1 module map states the declaration store is "frozen after M1 succeeds," but M3's retry loop means M1 may execute multiple times. The freeze point is after M3's final successful invocation of M1, not after M1's first execution.
- **The scenario_context dict must be fully formed before §2.5 can assemble the prompt.** This is an inter-module dependency (Phase 1 → M3) stated in stage1 but worth noting: §2.5 has no mechanism for handling a partial or malformed scenario context.

### 3.4 CROSS-CHECK AGAINST INTERFACE OUT (stage2_overview.md)

**§2.5 — INTERFACE OUT per overview:**
> "Executable Python string containing a `build_fact_table(seed) → (DataFrame, metadata)` function, passed to M1 for sandbox execution."

**Assessment:** Broadly consistent, but with a nuance. The prompt in §2.5 does not directly produce the output — it produces the *prompt* that the LLM uses to generate the script. The actual script emission happens during §2.7's execution loop. Saying §2.5's INTERFACE OUT is the script is a slight abstraction; more precisely, §2.5's output is the assembled prompt, and §2.7's output is the script. However, since §2.7 cannot function without §2.5, treating the two as a unit with a single combined output is reasonable. **No material mismatch.**

**§2.7 — INTERFACE OUT per overview:**
> "On success, the same Python script artifact as §2.5 (now error-free). On terminal failure, a logged skip signal. Consumes `Exception` objects from M1."

**Assessment:** Consistent with the spec. Two outputs, exactly two branches. The overview correctly identifies the consumption of `Exception` objects from M1.

**One flag worth noting:** The overview states the script is "passed to M1 for sandbox execution," which is true during the retry loop. But after final success, the script's *side effect* — M1's populated declaration store — is what actually flows downstream to M2 and M4. The script string itself is not re-consumed; it has already been executed. The overview's framing could be read as implying the script is handed off as a data artifact to M1 *after* M3 completes, but in reality M1 has already executed it during M3's loop. This is a **minor framing ambiguity** in the overview, not a true mismatch — the pipeline execution order in stage1 makes the actual flow clear.
