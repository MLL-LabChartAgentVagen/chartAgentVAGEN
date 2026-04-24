# M3 — LLM Orchestration

## What This Module Does

M3 is the **only module in Phase 2 that calls an LLM**. Its job: turn a scenario-context dict (from Phase 1) into a validated Python script that constructs a `FactTableSimulator`, executes it in a restricted sandbox, and emits the `(DataFrame, metadata, raw_declarations, source_code)` 4-tuple — or returns a `SkipResult` sentinel if all retries are exhausted. Position in the pipeline: **upstream** of M1 (M3 generates and runs a script that *calls* M1 methods) and **upstream** of M2/M4 (which run inline inside the sandboxed script as part of `sim.generate()`); consumed by `pipeline.run_loop_a` and by Phase 1's Stage-1 driver. Boundary: M3 owns the LLM conversation and retry budget; it never touches a DataFrame directly, never validates data, and never mutates anything the LLM script produced — all of that is delegated to M1 (SDK validation at declaration time) and M5 (data validation downstream).

## Internal Structure

```
pipeline/phase_2/orchestration/
├── __init__.py           # re-exports LLMClient
├── retry_loop.py         # orchestrate() — the Loop A entry point
├── sandbox.py            # execute_in_sandbox, _TrackingSimulator, run_retry_loop, format_error_feedback
├── prompt.py             # SYSTEM_PROMPT_TEMPLATE (5 regions) + render_system_prompt
├── code_validator.py     # extract_clean_code + validate_generated_code (AST checks)
└── llm_client.py         # LLMClient + ParameterAdapter (multi-provider)
```

**Data flow.** `orchestrate(scenario_context, llm_client)` serializes the scenario into a string, calls `prompt.render_system_prompt` to substitute the `{scenario_context}` placeholder, wraps `llm_client.generate_code` with `max_tokens=8192` + `extract_clean_code`, and generates the initial script. It then delegates to `sandbox.run_retry_loop`, which iterates: `execute_in_sandbox(code)` → on success return a `RetryLoopResult(success=True, ...)` carrying the DataFrame, metadata, captured `raw_declarations`, and the winning `source_code`; on failure, assemble feedback via `format_error_feedback(original_code, exception, traceback, prior_failures=history)` and re-prompt the LLM with only two messages (system prompt + error-feedback user message — the chat history does not grow). After `max_retries` failures, `orchestrate` maps the failure-mode `RetryLoopResult` to a `SkipResult(scenario_id=..., error_log=[...])`.

## Key Interfaces

### External-facing (1): [`orchestrate`](retry_loop.py) (in `retry_loop.py`)

```python
from pipeline.phase_2.orchestration.retry_loop import orchestrate
from pipeline.phase_2.orchestration.llm_client import LLMClient

client = LLMClient(api_key=..., model="gemini-2.0-flash-lite", provider="auto")

result = orchestrate(
    scenario_context: dict[str, Any],
    llm_client: LLMClient,
    max_retries: int = 3,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any], str] | SkipResult
```

Success returns a 4-tuple: `(df, metadata, raw_declarations, source_code)`. `raw_declarations` carries the captured simulator state (`columns`, `groups`, `group_dependencies`, `measure_dag`, `target_rows`, `patterns`, `seed`, `orthogonal_pairs`) — this is the dict that Stage 2 / Loop B later feeds to `run_loop_b_from_declarations` to reproduce the DataFrame deterministically without re-invoking the LLM. `source_code` is the exact Python string that succeeded (suitable for persisting to `scripts/{id}.py`). On exhaustion, returns `SkipResult(scenario_id, error_log)` — orchestrate itself never raises.

### External-facing (2): [`LLMClient`](llm_client.py) (in `llm_client.py`)

```python
LLMClient(api_key: str, model: str = "gemini-2.0-flash-lite",
          base_url: str | None = None, provider: str = "auto")

client.generate_code(system: str, user: str, **kwargs) -> str
client.generate(system, user, temperature=0.7, max_tokens=4096, response_format="json") -> str
client.generate_json(system, user, **kwargs) -> dict
```

Multi-provider with `ProviderCapabilities` adaptation — supports OpenAI, Gemini (OpenAI-compat), Gemini Native (`google-genai`), Azure OpenAI, and a custom/OpenAI-compat fallback. `provider="auto"` detects from the model name. The `ParameterAdapter` clamps `temperature` to the provider's allowed range, picks the right token parameter name (`max_tokens` vs `max_completion_tokens`), and appends a "Respond with valid JSON only" sentence to the user message when `response_format="json"` is requested but the provider doesn't natively support JSON mode (e.g., Gemini). Reasoning-model overrides in `MODEL_OVERRIDES` disable unsupported parameters (e.g., `temperature` for `o1`/`o3`/`gpt-5`) rather than letting the API reject the call.

### Internal-facing

- [`sandbox.py`](sandbox.py)
  - `execute_in_sandbox(source_code, timeout_seconds=30, sandbox_namespace=None) -> SandboxResult` — compiles + `exec`s the script in a daemon thread with a restricted namespace. Catches every `Exception` subclass + `TimeoutError`.
  - `_build_sandbox_namespace()` — constructs the namespace: `_SAFE_BUILTINS` allowlist (~50 entries, notably **no** `__import__`, `open`, `eval`, `exec`, `compile`, `__build_class__`), a restricted `__import__` that only resolves `FactTableSimulator` aliases (`chartagent.synth`, `chartagent`, `phase_2`, `phase_2.simulator`, `phase_2.sdk.simulator`), and `FactTableSimulator` pre-injected as `_TrackingSimulator`.
  - `_TrackingSimulator(FactTableSimulator)` — thin subclass that appends `self` to the namespace's `_sim_registry` list on `__init__`, so after a successful `build_fact_table()` call the orchestrator can read the last entry to recover raw declarations.
  - `format_error_feedback(original_code, exception, traceback_str, prior_failures=None) -> str` — assembles up to 5 sections: optional "PRIOR FAILED ATTEMPTS" (class+message per earlier failure, no tracebacks), "ORIGINAL CODE", "ERROR", "TRACEBACK", "INSTRUCTION". Strengthens the instruction when `prior_failures` is non-empty.
  - `run_retry_loop(initial_code, llm_generate_fn, system_prompt, max_retries=3, ...) -> RetryLoopResult` — the actual retry loop.
- [`prompt.py`](prompt.py) — `SYSTEM_PROMPT_TEMPLATE: Final[str]` (~388 lines, 5 regions) + `render_system_prompt(scenario_context: str) -> str` (uses `str.replace` rather than `str.format` because the one-shot example contains literal `{...}` in Python dicts).
- [`code_validator.py`](code_validator.py) — `extract_clean_code(raw_response) -> str` strips markdown fences tolerating leading prose. `validate_generated_code(source_code) -> CodeValidationResult(is_valid, has_build_fact_table, has_generate_call, errors)` runs AST-level pre-flight checks: `ast.parse` for syntax, `_BuildFactTableVisitor` for the `def build_fact_table(...)` definition, `_GenerateCallVisitor` for a `.generate()` method call.

## How It Works

### The three-move retry dance

Each retry is exactly **two messages sent to the LLM**: a system prompt and a user message. The conversation history does not grow across retries. **Why two messages, not a growing transcript:** LLMs condition on the last message most strongly, and each retry's task is narrowly "fix *this* error", not "reconcile five prior attempts". Shipping the full transcript would dilute the fix signal and exhaust the context window on long scripts. The "PRIOR FAILED ATTEMPTS" section at the top of each feedback message carries just the class names and messages of previous failures, which is enough to prevent regressions without the cost of the full transcripts.

### Why typed exceptions drive the retry, not string matching

`format_error_feedback` inserts the exception's class name (`CyclicDependencyError`, `UndefinedEffectError`, `NonRootDependencyError`, `DuplicateColumnError`, `WeightLengthMismatchError`, `InvalidParameterError`, …) verbatim into the feedback message. **Why:**
1. **Class names are a stable semantic contract**; messages evolve. If the `WeightLengthMismatchError` message string changes from "weights length mismatch" to "weight vector length doesn't match values" in a later refactor, any LLM prompt that relied on the old string would silently break. Class names are part of the public API and change only with deliberate migrations.
2. **Class identity enables targeted reasoning.** An LLM that sees `CyclicDependencyError` knows structurally what went wrong — a cycle in either the measure DAG (from `add_measure_structural`) or the root-level dependency graph (from `add_group_dependency`). The fix space is narrow: reorder declarations, drop an edge, or re-express the formula. A raw error message like "A → B → A" gives the same information but forces the LLM to do extra inference to identify the failure category.
3. **String matching is fragile across I18n or formatting changes.** Some providers wrap exception messages, indent them, or truncate them at arbitrary lengths. The class identity survives.

This decision ripples backward into M1: the SDK raises **specific, fine-grained exception subclasses** (13+ in [`../exceptions.py`](../exceptions.py)) rather than a catch-all `SimulatorError` with an enum field. Each subclass is a distinct retry signal.

### The sandbox's threat model and allowlist

`execute_in_sandbox` compiles and `exec()`s LLM-authored code with a hand-built namespace. The threat model is **untrusted code in a trusted process**: the LLM might emit anything, including imports of `os`, file reads, network calls, or infinite loops. The defenses:

- **`_SAFE_BUILTINS` allowlist**, not denylist. Only ~50 names are exposed (`True`, `False`, `None`, arithmetic primitives, `list`/`dict`/`tuple`/`set`, `range`, `len`, `print`, standard exceptions, etc.). Notably absent: `__import__`, `__build_class__` (class bodies still work via the AST path), `open`, `eval`, `exec`, `compile`, `globals`, `locals`, `vars`, `input`, `breakpoint`. **Why allowlist:** a denylist invites misses; an allowlist makes the attack surface enumerable.
- **Restricted `__import__`**. A custom `_restricted_import` replaces the builtin and only resolves the five accepted aliases for `FactTableSimulator`, raising `ImportError` otherwise. **Why aliases:** the LLM prompt and the one-shot example use different conventions (`from chartagent.synth import FactTableSimulator`, `from phase_2.sdk.simulator import FactTableSimulator`) and we don't want to fight the LLM over the *form* of the import when only the resolution matters.
- **Daemon-thread execution with `timeout_seconds` join**. `_SandboxThread` is a daemon (won't block process exit), and the main thread's `worker.join(timeout)` is how timeouts are enforced. **Why daemon thread rather than subprocess or `signal.alarm`:** subprocesses are costly per-scenario (tens of ms startup + pickling), `signal.alarm` doesn't work off the main thread (so it would break when Phase 2 is invoked from an async context), and this sandbox only needs to protect against accidental infinite loops in LLM code, not against a malicious RCE (we already trust the Python process).
- **`_TrackingSimulator` for recovery**. The registry-based approach lets the orchestrator extract raw declarations *after* execution completes, without the LLM script needing to know it's being observed.

### The prompt's five composable regions

`SYSTEM_PROMPT_TEMPLATE` is deliberately structured as five stable regions: role preamble, SDK method whitelist (Step 1 + Step 2), hard constraints HC1–HC10, soft guidelines, one-shot example — plus a single `{scenario_context}` slot. **Why this layout rather than a single narrative prompt:** each region has a different stability profile. The hard constraints change rarely and are contract-level (HC7 — DAG acyclicity — is a correctness requirement, not a stylistic preference); the soft guidelines evolve as we learn what patterns LLMs handle well; the one-shot example is the most volatile because it reflects the current "idiom" for a good declaration. Keeping them textually distinct means edits to one region don't risk contaminating another, and A/B tests on a single region are trivial to run.

The template uses `str.replace("{scenario_context}", …)` rather than `str.format(**kwargs)` because the one-shot example contains literal Python dicts with curly braces (`param_model={"mu": ..., "sigma": ...}`), which `str.format` would parse as template placeholders and fail on.

### Provider abstraction

`ParameterAdapter` mediates between a single Phase 2 API (`generate_code(system, user, temperature=…, max_tokens=…)`) and whatever the underlying provider actually accepts. **Why abstract rather than pick one provider:** Phase 2 is designed to be provider-portable — swapping Gemini for OpenAI or Azure is a `provider=` argument, not a code change. This matters because different LLM families have different failure modes on the same prompt, and having a plug-and-play comparison layer is a requirement for evaluation.

See [`../../../docs/svg/module3_llm_orchestration.md`](../../../docs/svg/module3_llm_orchestration.md) for the visual walkthrough.

## Usage Example

> **Requires an LLM API key.** Set `OPENAI_API_KEY` / `GEMINI_API_KEY` / `AZURE_OPENAI_API_KEY` in your environment (or pass `api_key=` directly). Without a key, `LLMClient.generate_code` will raise on the first call.

**Primary path — the full Loop A** (pattern from [`../pipeline.py`](../pipeline.py) `_run_loop_a`):

```python
import os
from pipeline.phase_2.orchestration.llm_client import LLMClient
from pipeline.phase_2.orchestration.retry_loop import orchestrate
from pipeline.phase_2.exceptions import SkipResult

client = LLMClient(
    api_key=os.environ["GEMINI_API_KEY"],
    model="gemini-2.0-flash-lite",
    provider="auto",           # detects from model name
)

scenario_context = {
    "scenario_id": "emergency_2024",
    "title": "2024 Shanghai Emergency Records",
    "target_rows": 500,
    "entities": ["Xiehe", "Huashan", "Ruijin"],
    "metrics": ["wait_minutes", "cost"],
    "temporal_grain": "daily",
}

result = orchestrate(scenario_context, llm_client=client, max_retries=3)

if isinstance(result, SkipResult):
    print(f"Scenario {result.scenario_id} skipped. Error log:")
    for line in result.error_log:
        print(f"  - {line}")
else:
    df, metadata, raw_declarations, source_code = result
    print(f"Success: {df.shape[0]} rows, {len(metadata)} metadata keys.")
    # raw_declarations → feed to pipeline.run_loop_b_from_declarations for Stage 2
    # source_code      → persist to scripts/{scenario_id}.py
```

**No-LLM path — sandbox-only** (smoke-tests the sandbox without burning LLM budget; pattern from [`../tests/demo_end_to_end.py`](../tests/demo_end_to_end.py)):

```python
from pipeline.phase_2.orchestration.sandbox import execute_in_sandbox

code = """
def build_fact_table():
    sim = FactTableSimulator(target_rows=3, seed=99)
    sim.add_category("status", ["Active", "Inactive"], [0.8, 0.2], "accounts")
    return sim.generate()
"""

result = execute_in_sandbox(code, timeout_seconds=30)
if result.success:
    print(result.dataframe)
    print(list(result.metadata.keys()))
else:
    print(f"Error: {type(result.exception).__name__}: {result.exception}")
    print(result.traceback_str)
```

## Dependencies

**Imported from the rest of `phase_2/`:**

- [`phase_2.sdk.simulator`](../sdk/simulator.py) — `FactTableSimulator` (pre-injected into the sandbox namespace as `_TrackingSimulator`).
- [`phase_2.types`](../types.py) — `SandboxResult`, `RetryLoopResult` dataclasses.
- [`phase_2.exceptions`](../exceptions.py) — `SkipResult` (return sentinel), plus every `SimulatorError` subclass that can surface from M1 during sandbox execution.

**External libraries:** `openai` (lazy-imported for OpenAI/Gemini-compat providers), `google.genai` (lazy-imported for Gemini Native), `threading` (daemon thread), `traceback`, `ast`, `re`, `json`, `dataclasses`, `logging`.

**Preconditions.** An `LLMClient` is configured with a valid API key and a model name the provider recognizes. The `FactTableSimulator` SDK is importable (so the sandbox's restricted `__import__` can resolve it).

**Postconditions.** `orchestrate` returns either the 4-tuple or a `SkipResult` — it never raises. On the 4-tuple path, `raw_declarations` has all the keys needed by `pipeline.run_loop_b_from_declarations`; `source_code` is a self-contained script that re-executes deterministically in a fresh sandbox.

## Testing

```bash
# From repo root, chart conda env active
pytest pipeline/phase_2/tests/test_retry_feedback.py -v    # cumulative-failure feedback + history threading

# Sandbox-only smoke test (no LLM call)
python -m pipeline.phase_2.tests.demo_end_to_end
```

The retry-loop tests assert that `format_error_feedback` omits the PRIOR FAILED ATTEMPTS section when there's no history, lists all priors in order when provided, skips prior entries without an exception, and that `run_retry_loop` actually passes the accumulated history through to the LLM on each retry.
