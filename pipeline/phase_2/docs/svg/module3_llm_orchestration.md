# Module 3: LLM Orchestration — SVG Flow Diagram Guide

**SVG file:** `module3_llm_orchestration.svg`
**Source of truth:** `docs/artifacts/stage5_anatomy_summary.md` — Module: LLM Orchestration (M3)
**Implementation:** `phase_2/orchestration/`

---

## SVG Section Map

The SVG is divided into two columns:

- **Left column** (x=18..482): The main data flow — input → prompt assembly → retry loop → output
- **Right column** (x=496..852): Supporting detail — M1 sandbox execution and retry pseudocode

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ┌──────────────────────┐                                          │
│   │  1. SCENARIO CONTEXT │                                          │
│   └──────────┬───────────┘                                          │
│              │                                                      │
│              ▼                                                      │
│   ┌──────────────────────┐                                          │
│   │  2. §2.5 PROMPT      │                                          │
│   │     ASSEMBLY         │                                          │
│   └──────────┬───────────┘                                          │
│              │ (A) assembled_prompt                                 │
│              ▼                                                      │
│   ┌──────────────────────┐      ┌───────────────────────┐           │
│   │  3. §2.7 EXECUTION-  │◄────►│  4. M1 SANDBOX        │           │
│   │     ERROR FEEDBACK   │      │     (SDK Validation)  │           │
│   │     LOOP             │      └───────────────────────┘           │
│   └──────────┬───────────┘      ┌───────────────────────┐           │
│              │                  │  5. RETRY DETAIL      │           │
│              │ (B)              │     (pseudocode)       │           │
│       ┌──────┴──────┐          └───────────────────────┘           │
│       │             │                                               │
│   ┌───┴───┐   ┌─────┴─────┐                                        │
│   │6a. B1 │   │6b. B2     │                                        │
│   │SUCCESS│   │SKIP       │                                        │
│   └───────┘   └───────────┘                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. SCENARIO CONTEXT INPUT

**SVG region:** Top-left box (y=54..128)

**What it represents:** The external input entering Module 3 from Phase 1. This is the starting point of the entire Phase 2 pipeline.

**Responsible file:** `phase_2/pipeline.py` → `_run_loop_a()`

| | Detail |
|---|---|
| **Input** | `scenario_context: dict` from Phase 1 — contains `title`, `entities`, `metrics`, `temporal_grain`, `target_rows`, `complexity_tier` |
| **Output** | Same dict, passed into §2.5 prompt assembly |
| **Data flow** | `pipeline.run_phase2(scenario_context)` → `pipeline._run_loop_a(scenario_context, ...)` → `retry_loop.orchestrate(scenario_context, ...)` |

**Call order:**
```
pipeline.run_phase2(scenario_context)
  └─ pipeline._run_loop_a(scenario_context, max_retries, llm_client)
       └─ retry_loop.orchestrate(scenario_context, llm_client, max_retries)
```

---

## 2. §2.5 LLM Code Generation Prompt

**SVG region:** Left column (y=144..334), showing the 5 prompt components

**What it represents:** The one-time assembly of a complete LLM prompt from five composable regions. This prompt is immutable across retries — it becomes `messages[0]` in the conversation history.

**Responsible file:** `phase_2/orchestration/prompt.py`

| | Detail |
|---|---|
| **Input** | `scenario_context: dict` (from section 1 above) |
| **Output** | `assembled_prompt: str` — the rendered system prompt with all 5 regions baked in |
| **Data flow** | `orchestrate()` serializes the dict, then calls `render_system_prompt()` to fill the template |

**The 5 prompt components** (shown as numbered badges ①–⑤ in SVG):

| # | Component | Content | Source in `prompt.py` |
|---|-----------|---------|----------------------|
| ① | System prompt | Role preamble, task description, output format | `SYSTEM_PROMPT_TEMPLATE` (top section) |
| ② | SDK whitelist | Permitted M1 API methods the script may call (Step 1 + Step 2 blocks) | `SYSTEM_PROMPT_TEMPLATE` (SDK section) |
| ③ | Hard constraints | HC1–HC9: column count range, type mix, structural rules | `SYSTEM_PROMPT_TEMPLATE` (constraints section) |
| ④ | One-shot example | Exemplar `build_fact_table()` script for in-context learning | `SYSTEM_PROMPT_TEMPLATE` (example section) |
| ⑤ | Scenario slot fill | `{scenario_context}` placeholder replaced with serialized dict | Filled by `render_system_prompt()` |

**Call order:**
```
retry_loop.orchestrate(scenario_context, llm_client, max_retries)
  ├─ retry_loop._format_scenario_context(scenario_context) → scenario_str
  └─ prompt.render_system_prompt(scenario_str) → system_prompt: str
       └─ SYSTEM_PROMPT_TEMPLATE.replace("{scenario_context}", scenario_str)
```

**Key constant:** `SYSTEM_PROMPT_TEMPLATE` is a 388-line Final[str] containing all 5 regions with one `{scenario_context}` slot.

---

## 3. §2.7 Execution-Error Feedback Loop

**SVG region:** Left column (y=360..582), the main loop box with 6 numbered steps

**What it represents:** The core retry mechanism (Loop A). Sends the prompt to an LLM, receives a Python script, executes it in a sandbox, and either succeeds or appends the error to the conversation and retries.

**Responsible files:**
- `phase_2/orchestration/retry_loop.py` — orchestration logic, LLM call wrapper
- `phase_2/orchestration/sandbox.py` — `run_retry_loop()`, `execute_in_sandbox()`, `format_error_feedback()`
- `phase_2/orchestration/code_validator.py` — `extract_clean_code()` (fence stripping)
- `phase_2/orchestration/llm_client.py` — `LLMClient.generate_code()` (LLM API call)

| | Detail |
|---|---|
| **Input** | `system_prompt: str` (from section 2), `llm_client: LLMClient`, `max_retries: int = 3` |
| **Output** | `(df, metadata, raw_declarations)` tuple on success, or `SkipResult` on exhaustion |
| **Stateful artifact** | `conversation_history` — grows with each failed attempt (see section 5) |

**The 6 steps** (shown as numbered items in SVG):

| Step | Action | Responsible file |
|------|--------|-----------------|
| 1 | Send `assembled_prompt` to LLM | `llm_client.py` → `LLMClient.generate_code()` |
| 2 | Receive generated Python script from LLM response | `code_validator.py` → `extract_clean_code()` |
| 3 | Execute script in sandbox → M1 SDK validates (see section 4) | `sandbox.py` → `execute_in_sandbox()` |
| 4 | If `SDKException` raised: append (script + traceback) to conversation, retry | `sandbox.py` → `format_error_feedback()` |
| 5 | If success: emit validated script artifact → output (B1) | `sandbox.py` → `run_retry_loop()` returns `RetryLoopResult(success=True)` |
| 6 | If terminal failure (all retries exhausted): emit SKIP → output (B2) | `retry_loop.py` → returns `SkipResult` |

**Call order:**
```
retry_loop.orchestrate(scenario_context, llm_client, max_retries)
  ├─ [prompt assembly — see section 2]
  ├─ retry_loop._make_generate_fn(llm_client) → generate_fn
  │    └─ inner _generate(system, user):
  │         ├─ llm_client.generate_code(system, user, max_tokens=8192) → raw: str
  │         └─ code_validator.extract_clean_code(raw) → clean_code: str
  │
  ├─ generate_fn(system_prompt, scenario_str) → initial_code: str    ← STEP 1+2
  │
  └─ sandbox.run_retry_loop(initial_code, generate_fn, system_prompt, max_retries)
       └─ for attempt in range(1, max_retries + 1):
            ├─ sandbox.execute_in_sandbox(current_code, timeout, ns)  ← STEP 3
            │    ├─ sandbox._build_sandbox_namespace() → dict
            │    └─ sandbox._SandboxThread(code, namespace).run()
            │         └─ compile() + exec() + build_fact_table()
            │
            ├─ on success: return RetryLoopResult(success=True, ...)  ← STEP 5
            │
            └─ on failure & attempt < max_retries:                    ← STEP 4
                 ├─ sandbox.format_error_feedback(code, exc, tb) → feedback: str
                 └─ generate_fn(system_prompt, feedback) → new_code   ← STEP 1+2 (retry)
       └─ on exhaustion: return RetryLoopResult(success=False, ...)   ← STEP 6
```

**Retry arc:** The SVG shows a dashed loop-back arc on the left edge of the §2.7 box (from step 4 back to step 1). This represents `run_retry_loop()` iterating: on failure, it formats the error feedback, calls the LLM again with the accumulated conversation, and re-enters the sandbox execution.

---

## 4. M1 Sandbox (SDK Validation)

**SVG region:** Right column, upper box (y=370..462), dashed border (external component)

**What it represents:** The sandbox execution environment where LLM-generated scripts run against the real M1 SDK. The script calls `FactTableSimulator` methods; if any declaration is invalid, M1 raises a typed `SDKException` that feeds back into the retry loop.

**Responsible file:** `phase_2/orchestration/sandbox.py`

| | Detail |
|---|---|
| **Input** | Python script `source_code: str` from LLM (via step 3 of §2.7) |
| **Output** | `SandboxResult(success, dataframe, metadata, raw_declarations)` on success; re-raised `Exception` on failure |
| **Data flow** | `execute_in_sandbox()` → `_SandboxThread.run()` → `exec()` → `build_fact_table()` → M1 SDK validates each declaration |

**SVG arrows between §2.7 and M1 Sandbox:**
- **→ script** (solid, left-to-right at y=418): the generated Python code sent into the sandbox
- **← exception** (dashed red, right-to-left at y=448): typed `SDKException` returned to §2.7 on validation failure

**Internal mechanism:**
```
sandbox.execute_in_sandbox(source_code, timeout_seconds, namespace)
  ├─ sandbox._build_sandbox_namespace() → dict
  │    └─ Injects: _TrackingSimulator (subclass of FactTableSimulator),
  │       _SAFE_BUILTINS (range, len, dict, list, ...), math, datetime
  │
  ├─ sandbox._SandboxThread(source_code, namespace)
  │    └─ .run():
  │         ├─ compile(source_code, "<llm_generated>", "exec")
  │         ├─ exec(compiled, namespace)
  │         └─ namespace["build_fact_table"]()
  │              └─ Calls M1 SDK: FactTableSimulator(target_rows, seed)
  │                   ├─ .add_category()     ─┐
  │                   ├─ .add_temporal()      │ Each call validates
  │                   ├─ .add_measure()       │ via sdk/validation.py
  │                   ├─ .add_measure_structural() │ Raises SDKError
  │                   ├─ .declare_orthogonal()     │ subtypes on failure
  │                   ├─ .inject_pattern()    │
  │                   └─ .generate()         ─┘ Freezes store, runs M2
  │
  └─ Returns: SandboxResult
       ├─ success=True:  (df, metadata, raw_declarations)
       └─ success=False: exception + traceback_str captured
```

**Exception types raised by M1** (from `phase_2/exceptions.py`):
- `DuplicateColumnError` — duplicate column name
- `CyclicDependencyError` — DAG cycle detected
- `UndefinedEffectError` — formula references undefined symbol
- `NonRootDependencyError` — `add_group_dependency` targets non-root column
- `UndefinedPredictorError` — effects key references undeclared column

---

## 5. RETRY DETAIL (pseudocode)

**SVG region:** Right column, lower box (y=472..780)

**What it represents:** A pseudocode expansion of the §2.7 loop internals, showing exactly how `conversation_history` accumulates and how the try/except dispatches between success and retry paths.

**Responsible file:** `phase_2/orchestration/sandbox.py` → `run_retry_loop()`

| | Detail |
|---|---|
| **Input** | `initial_code: str`, `llm_generate_fn: Callable`, `system_prompt: str`, `max_retries: int` |
| **Output** | `RetryLoopResult(success, dataframe, metadata, raw_declarations, history)` |
| **Stateful artifact** | Conversation history accumulates failed attempts — LLM sees prior code + error trace on each retry |

**SVG pseudocode mapping to implementation:**

| SVG pseudocode line | Implementation |
|---|---|
| `conversation_history = [system_prompt ← from §2.5]` | `system_prompt` parameter to `run_retry_loop()` |
| `for attempt in 0..max_retries:` | `for attempt in range(1, max_retries + 1):` in `run_retry_loop()` |
| `script = LLM(conversation_history)` | `llm_generate_fn(system_prompt, user_prompt) → str` |
| `conversation_history.append(role="assistant", content=script)` | Implicit — LLM output is the current `current_code` |
| `sandbox_exec(script) ──► M1 SDK validates` | `execute_in_sandbox(current_code, timeout, namespace) → SandboxResult` |
| `return script ✓` | `return RetryLoopResult(success=True, dataframe=result.dataframe, ...)` |
| `except SDKException as e:` | `if not result.success:` branch in `run_retry_loop()` |
| `conversation_history.append(role="user", content=f"Code:\n{script}\nError:\n{e}")` | `format_error_feedback(current_code, exception, traceback_str) → feedback_prompt` |
| `return SKIP ✗` | `return RetryLoopResult(success=False, ...)` → converted to `SkipResult` in `orchestrate()` |

**Conversation history growth per attempt:**

```
messages[0]:       system prompt from §2.5                  (fixed, immutable)
-- attempt 0 --
messages[1]:       assistant — script attempt 1
messages[2]:       user — code + traceback 1                (formatted by format_error_feedback)
-- attempt 1 --
messages[3]:       assistant — script attempt 2
messages[4]:       user — code + traceback 2
-- attempt 2 --
messages[5]:       assistant — script attempt 3
messages[6]:       user — code + traceback 3
-- attempt 3 (final) --
messages[7]:       assistant — script attempt 4             (last chance)
```

At max retries (3 failures), up to **8 messages** total. Token count scales with `script_length × 4 + traceback_length × 3`.

---

## 6a. Output Branch (B1): SUCCESS

**SVG region:** Bottom-left green box (y=600..714)

**What it represents:** The happy path — a validated Python script that successfully executed against the M1 SDK, producing a frozen `DeclarationStore`, a DataFrame, and schema metadata.

**Responsible file:** `phase_2/orchestration/retry_loop.py` → `orchestrate()` return path

| | Detail |
|---|---|
| **Input** | `RetryLoopResult(success=True, dataframe, metadata, raw_declarations)` from `run_retry_loop()` |
| **Output** | `(df: pd.DataFrame, metadata: dict, raw_declarations: dict)` tuple |
| **Downstream consumers** | `pipeline._run_loop_a()` receives this tuple, then passes it to Loop B (M5 validation) |

**Call order on success:**
```
sandbox.run_retry_loop() returns RetryLoopResult(success=True, ...)
  └─ retry_loop.orchestrate() returns (result.dataframe, result.metadata, result.raw_declarations)
       └─ pipeline._run_loop_a() returns this tuple
            └─ pipeline.run_phase2() proceeds to _run_loop_b()
                 └─ M2 re-generation + M5 validation (Loop B)
```

**What flows downstream:**
- `df` (pd.DataFrame) → M5 Validation Engine as the candidate DataFrame
- `metadata` (dict) → M5 as schema_metadata for check parameterization
- `raw_declarations` (dict) → `_run_loop_b()` to reconstruct `build_fn` for Loop B re-execution

---

## 6b. Output Branch (B2): TERMINAL FAILURE

**SVG region:** Bottom-right red box (y=600..714)

**What it represents:** The failure path — all retry attempts exhausted, no valid script was produced.

**Responsible file:** `phase_2/orchestration/retry_loop.py` → `orchestrate()` return path

| | Detail |
|---|---|
| **Input** | `RetryLoopResult(success=False, history=[...])` from `run_retry_loop()` |
| **Output** | `SkipResult` sentinel |
| **Downstream consumers** | `pipeline.run_phase2()` checks for `SkipResult` and returns it to Phase 1 caller |

**Call order on failure:**
```
sandbox.run_retry_loop() returns RetryLoopResult(success=False, ...)
  └─ retry_loop.orchestrate() returns SkipResult(details=...)
       └─ pipeline._run_loop_a() returns SkipResult
            └─ pipeline.run_phase2() returns SkipResult to caller
                 (no Loop B, no M2/M4/M5 execution)
```

`SkipResult` is a sentinel class (not an exception) defined in `phase_2/exceptions.py`. The pipeline checks `isinstance(result, SkipResult)` to distinguish from the success tuple.

---

## Complete File Responsibility Map

| SVG Section | Primary File | Supporting Files |
|---|---|---|
| 1. Scenario Context Input | `pipeline.py` | — |
| 2. §2.5 Prompt Assembly | `orchestration/prompt.py` | — |
| 3. §2.7 Feedback Loop | `orchestration/retry_loop.py` | `sandbox.py`, `code_validator.py`, `llm_client.py` |
| 4. M1 Sandbox | `orchestration/sandbox.py` | `sdk/simulator.py`, `sdk/validation.py`, `exceptions.py` |
| 5. Retry Detail | `orchestration/sandbox.py` | `orchestration/llm_client.py`, `code_validator.py` |
| 6a. SUCCESS output | `orchestration/retry_loop.py` | `pipeline.py` |
| 6b. SKIP output | `orchestration/retry_loop.py` | `pipeline.py`, `exceptions.py` |

---

## End-to-End Call Trace

```
pipeline.run_phase2(scenario_context)
│
├─ pipeline._run_loop_a(scenario_context, max_retries, llm_client)
│   │
│   └─ retry_loop.orchestrate(scenario_context, llm_client, max_retries)
│       │
│       ├─ retry_loop._format_scenario_context(scenario_context)      → scenario_str
│       ├─ prompt.render_system_prompt(scenario_str)                   → system_prompt
│       ├─ retry_loop._make_generate_fn(llm_client)                   → generate_fn
│       │   └─ inner _generate(system, user):
│       │       ├─ llm_client.generate_code(system, user, max_tokens=8192)  → raw
│       │       └─ code_validator.extract_clean_code(raw)                    → clean
│       │
│       ├─ generate_fn(system_prompt, scenario_str)                   → initial_code
│       │
│       └─ sandbox.run_retry_loop(initial_code, generate_fn, system_prompt, max_retries)
│           │
│           └─ for each attempt:
│               │
│               ├─ sandbox._build_sandbox_namespace()                 → namespace
│               ├─ sandbox.execute_in_sandbox(code, timeout, namespace)
│               │   └─ sandbox._SandboxThread.run()
│               │       ├─ compile(code) + exec(compiled, namespace)
│               │       └─ namespace["build_fact_table"]()
│               │           └─ M1 SDK: FactTableSimulator → .add_*() → .generate()
│               │               ├─ success → SandboxResult(success=True, df, meta)
│               │               └─ failure → SandboxResult(success=False, exception)
│               │
│               ├─ success path → RetryLoopResult(success=True)       → (B1)
│               │
│               └─ failure path (if retries remain):
│                   ├─ sandbox.format_error_feedback(code, exc, tb)   → feedback
│                   └─ generate_fn(system_prompt, feedback)            → new_code
│                       └─ [loop continues]
│
│       └─ exhaustion → SkipResult                                    → (B2)
│
├─ [on B1] pipeline._run_loop_b(df, meta, raw_decl, ...)             → Loop B (M5)
└─ [on B2] return SkipResult to caller
```
