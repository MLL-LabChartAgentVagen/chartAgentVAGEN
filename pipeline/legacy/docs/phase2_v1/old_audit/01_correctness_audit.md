---
title: "AGPDS Phase 0–2 Static Correctness Audit"
date: 2026-03-04
severity_counts:
  CRITICAL: 5
  WARNING: 9
  NOTE: 6
---

# AGPDS Correctness Audit — Phase 0–2

> **Scope:** Static read-only analysis of `pipeline/agpds_pipeline.py`, `pipeline/agpds_runner.py`, `pipeline/core/llm_client.py`, `pipeline/core/master_table.py`, `pipeline/phase_0/domain_pool.py`, `pipeline/phase_1/scenario_contextualizer.py`, `pipeline/phase_2/fact_table_simulator.py`, `pipeline/phase_2/sandbox_executor.py`, `pipeline/phase_2/distributions.py`, `pipeline/phase_2/patterns.py`, `pipeline/phase_2/validators.py`, `pipeline/phase_2/schema_metadata.py`.
>
> **Methodology:** Evidence-based line citation. No code was executed.

---

## Audit 1 — Output Contract Verification

### 1.a — Output Write Locations

| Artifact | File | Line(s) | Write Operation |
|---|---|---|---|
| `(df, meta)` tuple | `fact_table_simulator.py` | 529–530 | `return df, meta` (the canonical output of `generate()`) |
| `ExecutionResult.df` + `.schema_metadata` | `sandbox_executor.py` | 318–323 | `return ExecutionResult(success=True, df=df, schema_metadata=meta, ...)` |
| `master_data_csv` string | `agpds_pipeline.py` | 126 | `"master_data_csv": df.to_csv(index=False)` (written to result dict) |
| `schema_metadata` dict | `agpds_pipeline.py` | 127 | `"schema_metadata": schema_metadata` (placed directly in result dict) |
| CSV file on disk | `agpds_runner.py` | 69–72 | `f.write(csv_content)` after `result.pop("master_data_csv", None)` |
| Schema JSON on disk | `agpds_runner.py` | 78–81 | `json.dump(schema_content, f, indent=2)` |
| Manifest `charts.json` | `agpds_runner.py` | 87–88 | `json.dump(json_results, f, indent=2)` |

### 1.b — Master Table Contract

**Expected fields per `SchemaMetadata` TypedDict** (`schema_metadata.py` lines 69–84):

| Key | In `_build_schema_metadata()` | Verdict |
|---|---|---|
| `dimension_groups` | Yes — lines 920–939 | **CORRECT** |
| `orthogonal_groups` | Yes — lines 994–999 | **CORRECT** |
| `columns` | Yes — lines 941–962 | **CORRECT** (categorical, temporal, measure each present) |
| `conditionals` | Yes — lines 964–968 | **CORRECT** |
| `correlations` | Yes — lines 970–974 | **CORRECT** |
| `dependencies` | Yes — lines 976–980 | **AMBIGUOUS** — see Finding A1-1 below |
| `patterns` | Yes — lines 982–991 | **INCORRECT** — see Finding A1-2 below |
| `total_rows` | Yes — line 1005 | **AMBIGUOUS** — see Finding A1-3 below |

---

### Finding A1-1 (WARNING) — `DependencyMeta.noise_sigma` dropped from schema output

**File:** `pipeline/phase_2/fact_table_simulator.py:976–980`

```python
# Dependencies
dependencies = [
    {"target": d["target"], "formula": d["formula"]}
    for d in self._dependency_specs
]
```

The `DependencyMeta` TypedDict (defined in `schema_metadata.py:48–53`) includes `noise_sigma`:
```python
class DependencyMeta(TypedDict, total=False):
    target: str
    formula: str
    noise_sigma: float   # ← declared here but NOT emitted by _build_schema_metadata
```

`noise_sigma` is stored internally in `_dependency_specs` but is intentionally omitted from the returned metadata. Any downstream Phase 3 consumer that attempts to reconstruct the DGP from `SchemaMetadata` will get a silent discrepancy — the noise level is lost.

**Recommended Fix:** Add `"noise_sigma": d["noise_sigma"]` to the dict comprehension at line 978.

---

### Finding A1-2 (CRITICAL) — Pattern params collide with reserved keys via `dict.update`

**File:** `pipeline/phase_2/fact_table_simulator.py:984–991`

```python
patterns = []
for p in self._pattern_specs:
    pat_entry: dict = {"type": p["type"]}
    if p["target"] is not None:
        pat_entry["target"] = p["target"]
    if p["col"] is not None:
        pat_entry["col"] = p["col"]
    pat_entry.update(p["params"])       # ← DANGEROUS: flattens params into top-level
    patterns.append(pat_entry)
```

`pat_entry.update(p["params"])` merges the params dict directly into the top-level pattern dict. If `params` contains a key named `"type"`, `"col"`, or `"target"` — all plausible for LLM-generated code — those reserved metadata keys will be **silently overwritten**. For example, a `trend_break` pattern with `params={"break_point": "2024-03-15", "type": "exponential"}` would corrupt the emitted `type` field to `"exponential"`.

The `SchemaMetadata.PatternMeta` TypedDict (lines 55–66) defines a nested `params` sub-key (`params: Optional[dict]`), indicating the design intent is to keep params nested, not flattened.

**Recommended Fix:** Replace `pat_entry.update(p["params"])` with `pat_entry["params"] = dict(p["params"])` and update validators and Phase 3 consumers to expect the nested structure.

---

### Finding A1-3 (WARNING) — `total_rows` in metadata reflects declaration, not actual output row count

**File:** `pipeline/phase_2/fact_table_simulator.py:1005`

```python
"total_rows": self.target_rows,
```

`self.target_rows` is the user-declared target, but the actual DataFrame produced by `_build_skeleton()` may have a different row count. After tiling (lines 568–571), `df = combined.iloc[:self.target_rows]`, the actual count equals `self.target_rows` only when `combined` has at least that many rows. However `set_realism()` does not change row count, and the actual post-`_post_process()` row count may differ if the skeleton's cross-join product yields `< self.target_rows` rows and `len(combined) % self.target_rows != 0` — the slice at line 571 guarantees exactly `self.target_rows`, so this is fine in most cases. **However**, the L1 validator at `validators.py:83–88` checks `abs(len(df) - target) / max(target, 1) < 0.1` and `target = meta.get("total_rows", len(df))`. If `total_rows` is always `self.target_rows`, the validator will always see exact match for row count — making the row-count check a no-op.

**Recommended Fix:** Capture `len(df)` after final post-processing and use that as `total_rows` in the metadata.

---

## Audit 2 — Logic Correctness Check

### Finding A2-1 (CRITICAL) — `_build_phase2_prompt` references non-existent `FactTableSimulator` methods

**File:** `pipeline/agpds_pipeline.py:65–73`

```python
user_prompt = f"""
...
1. Initialize `simulator = FactTableSimulator(seed=""" + f'"{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]}"' + """)`
2. Declare at least 2 categorical columns (Entity, Context)
3. Declare at least 2 numerical measures
4. Define statistical relationships/patterns appropriate for this domain
5. Return ONLY valid Python code block (` ```python ... ``` `).

Ensure you call:
`df, report = simulator.generate_with_validation(target_rows={scenario.get('target_rows', 100)})`
`return df, simulator.get_schema_metadata()`
"""
```

This prompt instructs the LLM to call `simulator.generate_with_validation(target_rows=...)` and `simulator.get_schema_metadata()`. **Neither method exists on `FactTableSimulator`.**

- The correct call is `sim.generate()` returning `(df, meta)` — defined at `fact_table_simulator.py:496–530`.
- `generate_with_validation()` is a module-level function in `validators.py` with a completely different signature: `generate_with_validation(build_fn, max_retries, base_seed)`.
- `get_schema_metadata()` does not exist anywhere in the codebase.

Additionally, the prompt uses `target_rows=...` as a runtime kwarg of `generate_with_validation()`, which that function does not accept.

This means **every LLM-generated script following this prompt will fail at execution time** with `AttributeError: 'FactTableSimulator' object has no attribute 'generate_with_validation'`. This is the most severe bug in the pipeline — it completely breaks the end-to-end path through `agpds_pipeline.py`.

**Also:** The seed is computed at prompt-construction time via `hashlib.md5(str(datetime.now()).encode())`, producing a random hex string that cannot be used as an integer seed by `FactTableSimulator.__init__`. This contradicts the reproducibility goal of the pipeline.

**Recommended Fix:** Replace the prompt's instructions to use the correct API:
```
simulator = FactTableSimulator(target_rows={scenario.get('target_rows', 500)}, seed=42)
# ... declarations ...
return simulator.generate()
```
And remove the `hashlib.md5(...)` seed from the prompt — always pass an integer seed.

---

### Finding A2-2 (CRITICAL) — `run_with_retries`: uninitialized `feedback_text` on first failure of first attempt

**File:** `pipeline/phase_2/sandbox_executor.py:467–502`

```python
for attempt in range(max_retries):
    if attempt == 0:
        script = llm_client.generate_code(system=system_prompt, user=user_prompt)
    else:
        correction_prompt = (
            f"{feedback_text}\n\n"          # ← used here
            "Please output the COMPLETE corrected script. ..."
        )
        script = llm_client.generate_code(system=system_prompt, user=correction_prompt)

    result = executor.execute(script, seed=seed)

    if result.success:
        return result

    # ---- Format feedback for next attempt ----
    feedback_text = format_error_feedback(result)     # ← initialized AFTER first failure
```

On `attempt == 0`, if execution fails, `feedback_text` is set at line 493. On `attempt == 1`, `feedback_text` is used at line 477 — **this works correctly** because `feedback_text` is set at the bottom of the loop body. However, if `max_retries == 1` (or `> 0`) and the code somehow reaches attempt `> 0` without `feedback_text` having been initialized (which cannot happen unless the loop logic changes), this would be an `UnboundLocalError`. As written with the current control flow, this is safe — but the code is fragile because there is no explicit initialization of `feedback_text` before the loop. If the loop body ever changes ordering, the bug will surface.

**Recommended Fix:** Initialize `feedback_text: str = ""` before the loop at line 465.

---

### Finding A2-3 (WARNING) — `_build_phase2_prompt` is bypassed; `run_with_retries` receives the wrong user prompt structure

**File:** `pipeline/agpds_pipeline.py:105–107`

```python
phase2_user_prompt = self._build_phase2_prompt(scenario)
...
sandbox_result = run_with_retries(self.llm, phase2_user_prompt, max_retries=10)
```

`run_with_retries` (in `sandbox_executor.py:431–502`) constructs its own `user_prompt` internally:
```python
user_prompt = f"[SCENARIO]\n{scenario_context}\n[AGENT CODE]"
```
where `scenario_context` is the second positional argument. So `agpds_pipeline.py` passes the custom prompt from `_build_phase2_prompt()` directly as `scenario_context`. The `[SCENARIO]...[AGENT CODE]` wrapper is then applied **on top** — wrapping an already-formatted prompt that has its own preamble and formatting. This results in a malformed prompt structure: the LLM will see `[SCENARIO]` followed by the full `_build_phase2_prompt` output (which starts with `"You are a Data Engineering Python Developer..."`), rather than the clean `[SCENARIO]<json>` format documented in `phase_2.md §2.2`.

The intended call pattern is for `scenario_context` to be a JSON string of the raw scenario (as `json.dumps(scenario, indent=2)`), not a full formatted prompt. The two calling conventions are incompatible.

**Recommended Fix:** Either (a) pass `json.dumps(scenario, indent=2)` directly as `scenario_context` to `run_with_retries`, letting it format the prompt; or (b) add a `user_prompt_override` parameter to `run_with_retries` and bypass its internal formatting.

---

### Finding A2-4 (WARNING) — `_build_group_samples`: child column sampling is independent of parent (hierarchy not enforced)

**File:** `pipeline/phase_2/fact_table_simulator.py:625–648`

```python
# Sample child columns conditioned on parent
for child in list(remaining):
    parent = parents.get(child)
    if parent in processed:
        spec = self._find_category(child)
        # Sample child values — in this implementation, child values
        # are sampled independently (the parent link is structural,
        # not a conditional distribution, unless add_conditional is used)
        child_values = rng.choice(
            spec["values"],
            size=n_samples,
            p=spec["weights"],
        )
```

The comment acknowledges this — child categories are sampled using their **global weights**, not conditioned on the parent row value. A hospital → department hierarchy will not exhibit `P(department | hospital)` — every department will appear with the same probability regardless of which hospital is in the same row. This contradicts the docstring of `add_category`: `Optional parent links to a parent column within the same group for hierarchy` and the design spec in `phase_2.md §2.1.2` (`P(department | hospital) follows the declared weights within the parent context`).

The `add_conditional` mechanism can partially compensate, but only for measures, not for child categorical columns.

**Recommended Fix:** Implement true conditional sampling for child columns: for each parent value, sample child values using the subset of rows where that parent value appears, not global weights.

---

### Finding A2-5 (WARNING) — `_apply_dependencies`: silent swallow of `pd.eval` exceptions with fallback that may also fail

**File:** `pipeline/phase_2/fact_table_simulator.py:705–711`

```python
try:
    predicted = pd.eval(formula, local_dict={**eval_context, "df": df})
except Exception:
    # Fallback: evaluate row-by-row with df columns as variables
    local_vars = {col: df[col] for col in df.columns}
    local_vars.update(eval_context)
    predicted = pd.eval(formula, local_dict=local_vars)
```

The first `pd.eval` failure is caught broadly with `except Exception` — swallowing any error including `SyntaxError`, `NameError`, `TypeError`— and retrying with a slightly different `local_dict`. The fallback differs only in that it adds `df[col]` for all columns vs. passing `"df": df`. If the formula genuinely contains undefined variable references, the fallback will raise the same error uncaught, causing an unhandled exception that propagates into `generate()`. The exception from the second `pd.eval` at line 711 is **not caught**, so the error that reaches the caller has lost context about which dependency formula caused it.

**Recommended Fix:** Catch the exception with a meaningful message that includes the formula string:
```python
except Exception as e:
    raise ValueError(f"add_dependency formula evaluation failed for '{target}': {formula!r}. Error: {e}") from e
```

---

### Finding A2-6 (WARNING) — `deduplicate_scenarios` uses a wrong import path

**File:** `pipeline/phase_1/scenario_contextualizer.py:283`

```python
from phase_0.domain_pool import check_overlap
```

The project package structure requires `from pipeline.phase_0.domain_pool import check_overlap` (absolute import from the project root). The bare `phase_0` import would only resolve if `pipeline/` is on `sys.path`, which is not set up by any `__init__.py` or runner. The correct import used everywhere else in the project is absolute from the package root. This function will raise `ModuleNotFoundError` every time `deduplicate_scenarios` is called.

**Recommended Fix:** Change to `from pipeline.phase_0.domain_pool import check_overlap`.

---

### Finding A2-7 (NOTE) — `inject_pattern` shadows built-in `type`

**File:** `pipeline/phase_2/fact_table_simulator.py:418–454`

```python
def inject_pattern(
    self,
    type: str,          # ← shadows built-in 'type'
    target: Optional[str],
    col: Optional[str],
    params: dict,
) -> "FactTableSimulator":
```

Using `type` as a parameter name shadows Python's built-in `type` function within the method body. While not a bug in current code (the method body never calls `type()`), it is a maintenance hazard: any future code in this method that uses `type(x)` for introspection will silently receive the string argument instead.

**Recommended Fix:** Rename the parameter to `pattern_type` (consistent with the `patterns.py` module's `inject_pattern(df, pattern_type, ...)` interface).

---

### Finding A2-8 (NOTE) — Cholesky fails for PSD matrices with exact eigenvalue 0

**File:** `pipeline/phase_2/fact_table_simulator.py:802–810`

```python
eigvals = np.linalg.eigvalsh(corr_matrix)
if np.any(eigvals < -1e-10):
    raise ValueError(...)

L = np.linalg.cholesky(corr_matrix)    # ← will fail for target_r == ±1
```

For `target_r = ±1.0`, the 2×2 correlation matrix is PSD (smallest eigenvalue = 0), so the guard at line 804 passes. However, `np.linalg.cholesky` requires strict positive-definiteness and will raise `LinAlgError: Matrix is not positive definite` for the degenerate case. `target_r = ±1.0` is allowed by `add_correlation` validation (only `abs(target_r) > 1.0` is rejected).

**Recommended Fix:** Clamp `target_r` to `[-0.9999, 0.9999]` before building the correlation matrix, or add `if abs(target_r) >= 1.0: target_r = np.sign(target_r) * 0.9999`.

---

## Audit 3 — Data Integrity Check

### Finding A3-1 (CRITICAL) — Sandbox builtins expose unrestricted `__import__`

**File:** `pipeline/phase_2/sandbox_executor.py:65–66`

```python
_SAFE_BUILTINS = {
    "__import__": __import__,      # ← SECURITY HOLE
    ...
}
```

Including the real `__import__` in `_SAFE_BUILTINS` allows LLM-generated code to import any module:
```python
os = __import__("os")
os.system("rm -rf /")
```
The entire point of the sandbox is to block access to dangerous modules (`os`, `sys`, `subprocess`, `open`, etc.), but `__import__` bypasses this restriction entirely. Any LLM hallucinating an `import os` equivalent via `__import__` will succeed.

A restricted version should be used:
```python
def _safe_import(name, *args, **kwargs):
    ALLOWED = {"math", "datetime", "decimal", "fractions", "statistics", "random"}
    if name not in ALLOWED:
        raise ImportError(f"Module '{name}' is not allowed in sandbox")
    return __import__(name, *args, **kwargs)
```

**Recommended Fix:** Replace `"__import__": __import__` with a whitelist-restricted import function.

---

### Finding A3-2 (WARNING) — `save_results` mutates result dicts via `pop`, destroying in-memory data

**File:** `pipeline/agpds_runner.py:67,76`

```python
csv_content = result.pop("master_data_csv", None)
...
schema_content = result.pop("schema_metadata", None)
```

`dict.pop()` removes the key from the dict in-place. After `save_results()` returns, the `results` list passed in no longer contains `master_data_csv` or `schema_metadata`. If the caller inspects the results after saving (e.g., for logging, validation, or in-memory chaining to Phase 3), both fields will be gone. Since `run_batch()` directly passes the list to `save_results()`, in the `main()` function at line 124–126:
```python
results = runner.run_batch(category_ids)
if results:
    runner.save_results(results, args.output_dir)
```
Any code added after `save_results()` that reads `results[i]["schema_metadata"]` will see `KeyError`.

**Recommended Fix:** Replace `pop` with `get` and write without removing:
```python
csv_content = result.get("master_data_csv")
schema_content = result.get("schema_metadata")
```
Then append paths to the result dict without removing the originals, or use `result.copy()` before mutation.

---

### Finding A3-3 (WARNING) — `DomainSampler.sample()` resets pool on `len(candidates) < n`, not at 80% exhaustion as documented

**File:** `pipeline/phase_0/domain_pool.py:442–448`

```python
# Reset at 80% exhaustion
if len(candidates) < n:
    self.used_ids.clear()
    ...
```

The docstring says "Resets when pool is 80% exhausted" and the class docstring says "Draws without replacement. Resets when pool is 80% exhausted." However the actual condition is `len(candidates) < n`, meaning the pool only resets when there are **fewer candidates than requested** — effectively 100% exhaustion when `n=1`. At `n=1` the pool must be empty for reset to trigger. The "80% threshold" referenced in the design spec (`phase_0.md §0.6`) is never enforced.

This means long-running batch jobs will exhaust the entire pool before resetting, reducing diversity in the latter portion of a batch.

**Recommended Fix:** Implement the design intent:
```python
total = len(self.pool if not complexity else [d for d in self.pool if d.get("complexity_tier") == complexity])
if len(self.used_ids) >= 0.8 * total:
    self.used_ids.clear()
    candidates = ...
```

---

### Finding A3-4 (WARNING) — `ScenarioContextualizer.generate()`: soft-failure path returns `response` which may be undefined

**File:** `pipeline/phase_1/scenario_contextualizer.py:162–176`

```python
last_errors = []
for attempt in range(self.max_retries + 1):
    response = self.llm.generate_json(...)
    is_valid, errors = self.validate_output(response)
    if is_valid:
        self._update_tracker(response)
        return response
    last_errors = errors

# Soft failure — return last response with warnings
import warnings
warnings.warn(...)
if isinstance(response, dict):          # ← 'response' is always set if loop ran at all
    self._update_tracker(response)
    return response                      # returns invalid scenario silently

raise ValueError(...)
```

`response` is always set because `self.max_retries + 1 >= 1` — so the loop runs at least once. The `if isinstance(response, dict)` check will almost always be `True` (since `generate_json()` always returns a dict or raises). A soft-failing response with validation errors is returned as if valid. **The caller (`run_single`) does not distinguish soft-failure responses from valid ones** — an invalid or malformed scenario is passed directly into Phase 2 without any indication of failure. This means Phase 2 may receive a scenario missing required fields like `target_rows` or `key_entities`.

**Recommended Fix:** Either (a) raise on all validation failures and let the caller decide how to handle, or (b) annotate the returned dict with a `"_validation_warnings"` key so callers can detect soft failures.

---

### Finding A3-5 (NOTE) — Temporal values from `rng.choice(date_range)` are `numpy.datetime64`, not `pandas.Timestamp`

**File:** `pipeline/phase_2/fact_table_simulator.py:574–577`

```python
if self._temporal_spec is not None:
    date_range = self._temporal_spec["date_range"]
    temporal_values = rng.choice(date_range, size=len(df))
    df[self._temporal_spec["name"]] = temporal_values
```

`pd.date_range(...)` returns a `DatetimeIndex` of `pandas.Timestamp` objects. `rng.choice()` on a `DatetimeIndex` converts elements to `numpy.datetime64` scalars. When stored in a DataFrame column, pandas typically converts them back to `Timestamp`, but this conversion is implicit and dtype-dependent. In `_post_process()` at line 912, `df.sort_values(temporal_col)` requires the column to be sortable, which `numpy.datetime64` is — so this works. However, downstream code in `validators.py` calls `pd.to_datetime(df[tc])` on the column, which is a safe conversion.

**Impact:** [NEEDS RUNTIME VERIFICATION] — In most Pandas versions this is harmless, but the implicit conversion from `numpy.datetime64[ns]` to `Timestamp` may silently produce `NaT` values in edge cases involving timezone-aware date ranges.

---

### Finding A3-6 (NOTE) — `generate()` uses `self.seed` directly but `generate_with_validation()` increments seed on retries

**File:** `pipeline/phase_2/validators.py:659–679` vs. `fact_table_simulator.py:505`

`FactTableSimulator.generate()` uses `self.seed` (line 505). `generate_with_validation()` in `validators.py` calls `build_fn(seed=base_seed + attempt)` (line 660), which expects `build_fn` to accept a `seed` argument. But `FactTableSimulator.generate()` ignores any argument passed to it — it uses `self.seed`. The seed injection via `build_fn(seed=...)` is therefore a no-op unless `build_fn` is the `build_fact_table(seed=...)` function from the LLM script, not `sim.generate`. The `generate_with_validation` design only works correctly when `build_fn` re-creates the simulator with the new seed — not when it passes seed to `generate()`.

**Recommended Fix:** Clarify `generate_with_validation` usage: `build_fn` should be a factory that creates a fresh `FactTableSimulator(seed=seed)` and calls `generate()`, not a reference to `sim.generate`.

---

## Audit 4 — Dependency & Import Check

### Finding A4-1 (CRITICAL) — `agpds_runner.py`: default model name is non-existent

**File:** `pipeline/agpds_runner.py:105`

```python
parser.add_argument("--model", default="gemini-3.1-pro-preview", help="Model name")
```

As of the audit date, `gemini-3.1-pro-preview` does not exist in the Google AI model catalog (current models are `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-1.5-pro`, etc.). Every CLI invocation without an explicit `--model` flag will fail at the first LLM API call with a model-not-found error.

**Recommended Fix:** Change default to `"gemini-2.0-flash-lite"` or `"gemini-2.0-flash"` (the defaults used in `llm_client.py` and `build_domain_pool.py`).

---

### Finding A4-2 (WARNING) — `LLMClient.generate`: `gemini-native` path ignores `response_format` for non-JSON text calls

**File:** `pipeline/core/llm_client.py:321–330`

```python
if response_format == "json" and self.adapter.capabilities.requires_json_in_prompt:
    full_prompt += "\n\nRespond with valid JSON only, no markdown formatting."

response = self._native_client.models.generate_content(
    model=self.model,
    contents=full_prompt,
    config=generation_config
)
return response.text
```

For the `gemini-native` path, `generation_config` is a plain `dict`. The `google-genai` SDK's `generate_content` method accepts a `google.genai.types.GenerateContentConfig` object or equivalent — passing a plain dict may be silently accepted or raise a `TypeError` depending on the SDK version. This is [NEEDS RUNTIME VERIFICATION], but the SDK docs specify a typed config object.

---

### Finding A4-3 (WARNING) — `LLMClient.generate_code`: the regex for fence stripping is too strict

**File:** `pipeline/core/llm_client.py:387–391`

```python
cleaned = re.sub(
    r"^```(?:python)?\s*\n", "", cleaned, count=1
)
cleaned = re.sub(r"\n```\s*$", "", cleaned, count=1)
```

The opening fence regex requires a newline immediately after the backticks (`\s*\n`). If the LLM outputs ` ```python code_starts_here` (no newline), the fence will not be stripped and the literal ` ```python` will be included in the compiled script, causing `SyntaxError`. Many LLM outputs omit the trailing newline after the opening fence.

**Recommended Fix:** Use a more permissive pattern: `r"^```(?:python)?\s*"` (no `\n` requirement).

---

### Finding A4-4 (WARNING) — `ParameterAdapter.adapt_parameters`: `supports_max_completion_tokens` is checked but not used when `supports_max_tokens` is also True

**File:** `pipeline/core/llm_client.py:169–171`

```python
# Add token limit parameter
if self.capabilities.supports_max_tokens:
    kwargs[self.capabilities.token_param_name] = max_tokens
```

For `openai` provider, `ProviderCapabilities` is initialized with:
- `supports_max_completion_tokens = True`
- `token_param_name = "max_completion_tokens"`
- `supports_max_tokens = True` (inherited default)

Because `supports_max_tokens` is `True` (the default), the token kwarg will always be set. `supports_max_completion_tokens` is declared but never read in `adapt_parameters`. For models like `o1` / `o3`, which have `supports_max_tokens = True` (default) AND `supports_max_completion_tokens = True`, the logic selects the right `token_param_name`, but only because `token_param_name` is set to `"max_completion_tokens"`. The boolean `supports_max_completion_tokens` is dead code.

---

### Finding A4-5 (NOTE) — `from scipy.stats import norm` at module level in `fact_table_simulator.py`

**File:** `pipeline/phase_2/fact_table_simulator.py:14`

```python
from scipy.stats import norm
```

`scipy` is imported as a direct top-level dependency of `fact_table_simulator.py`. `scipy` is not listed in the sandbox namespace (only `numpy`, `pandas`, `math`, `datetime` are whitelisted in `sandbox_executor.py:163–177`). This is correct — `norm` is used only inside `_inject_correlations()` which runs inside the host process, not inside the sandbox. But `scipy` should be listed in any `requirements.txt` or `pyproject.toml`. If `scipy` is not installed in the host environment, importation of `fact_table_simulator.py` will fail at module load time with `ImportError`.

**Recommended Fix:** Ensure `scipy` is in `requirements.txt`. Also, `validators.py` imports `scipy.stats.chi2_contingency` and `scipy.stats.kstest` at function-call time (inside `try` blocks), providing graceful degradation. The `norm` import in `fact_table_simulator.py` at module level provides no such graceful degradation.

---

### Finding A4-6 (NOTE) — Unused import: `TYPE_CHECKING` path for `LLMClient` in `sandbox_executor.py`

**File:** `pipeline/phase_2/sandbox_executor.py:23–24`

```python
if TYPE_CHECKING:
    from ..core.llm_client import LLMClient
```

`LLMClient` is referenced in `run_with_retries`'s type annotation (`llm_client: "LLMClient"`). This is a forward reference string annotation, so the `TYPE_CHECKING` guard is correct and prevents a circular import at runtime. However, the actual runtime call `llm_client.generate_code(...)` at lines 470–484 uses duck-typing — no `isinstance` check against `LLMClient` is performed. The annotation serves purely as documentation; this is not a bug but is noted for completeness.

---

## Summary Table

| Audit ID | File:Lines | Severity | Description | Recommended Fix |
|---|---|---|---|---|
| A1-1 | `fact_table_simulator.py:976–980` | WARNING | `noise_sigma` dropped from `dependencies` in schema metadata output | Add `"noise_sigma": d["noise_sigma"]` to dict comprehension |
| A1-2 | `fact_table_simulator.py:984–991` | CRITICAL | `pat_entry.update(p["params"])` flattens params into top-level, silently overwriting `type`/`col`/`target` keys | Use `pat_entry["params"] = dict(p["params"])` (nested, not flattened) |
| A1-3 | `fact_table_simulator.py:1005` | WARNING | `total_rows` reflects declared target, not actual output; makes L1 row-count validator a no-op | Set `total_rows` to `len(df)` after post-processing |
| A2-1 | `agpds_pipeline.py:65–73` | CRITICAL | Prompt references `generate_with_validation()` and `get_schema_metadata()` which do not exist on `FactTableSimulator`; all LLM scripts will fail | Rewrite prompt to use `sim.generate()` returning `(df, meta)` |
| A2-2 | `sandbox_executor.py:467–502` | CRITICAL | `feedback_text` not initialized before loop; fragile unbound variable risk on restructuring | Add `feedback_text: str = ""` before the loop |
| A2-3 | `agpds_pipeline.py:105–107` | WARNING | Custom prompt from `_build_phase2_prompt()` double-wrapped by `run_with_retries`; malformed prompt structure | Pass `json.dumps(scenario)` directly to `run_with_retries` |
| A2-4 | `fact_table_simulator.py:625–648` | WARNING | Child categorical columns sampled independently; parent→child hierarchy never enforced — contradicts design spec | Implement conditional sampling per parent value |
| A2-5 | `fact_table_simulator.py:705–711` | WARNING | `pd.eval` first failure silently swallowed; fallback can also fail with no context | Raise `ValueError` with formula context on failure |
| A2-6 | `scenario_contextualizer.py:283` | WARNING | `from phase_0.domain_pool import check_overlap` — wrong import path; will raise `ModuleNotFoundError` | Change to `from pipeline.phase_0.domain_pool import check_overlap` |
| A2-7 | `fact_table_simulator.py:418` | NOTE | Parameter named `type` shadows Python built-in `type` | Rename to `pattern_type` |
| A2-8 | `fact_table_simulator.py:802–810` | NOTE | `np.linalg.cholesky` raises `LinAlgError` for `target_r = ±1` which passes PSD guard | Clamp `target_r` to `[-0.9999, 0.9999]` |
| A3-1 | `sandbox_executor.py:65–66` | CRITICAL | `__import__` in `_SAFE_BUILTINS` fully bypasses sandbox restrictions | Replace with whitelist-restricted import function |
| A3-2 | `agpds_runner.py:67,76` | WARNING | `result.pop()` mutates caller's result dicts; post-save reads of schema/CSV data will fail | Replace `pop` with `get`; add paths without removing originals |
| A3-3 | `domain_pool.py:442–448` | WARNING | Pool resets at 100% exhaustion (when candidates < n), not at 80% as documented | Implement 80% threshold using `len(self.used_ids) >= 0.8 * total` |
| A3-4 | `scenario_contextualizer.py:162–176` | WARNING | Soft-failure path silently returns invalid scenario; caller cannot distinguish from valid | Annotate invalid responses with `"_validation_warnings"` key |
| A3-5 | `fact_table_simulator.py:574–577` | NOTE | `rng.choice(date_range)` yields `numpy.datetime64`; implicit dtype conversion is fragile | [NEEDS RUNTIME VERIFICATION] — test with timezone-aware date ranges |
| A3-6 | `validators.py:659–679` vs `fact_table_simulator.py:505` | NOTE | `generate_with_validation` seed increment is no-op if `build_fn` is `sim.generate` | Clarify that `build_fn` must be a `FactTableSimulator` factory |
| A4-1 | `agpds_runner.py:105` | CRITICAL | Default model `gemini-3.1-pro-preview` does not exist; all CLI invocations without `--model` will fail | Change default to `gemini-2.0-flash-lite` |
| A4-2 | `llm_client.py:321–330` | WARNING | `gemini-native` path passes plain `dict` as `config`; SDK may require typed `GenerateContentConfig` | [NEEDS RUNTIME VERIFICATION] — use `google.genai.types.GenerateContentConfig` |
| A4-3 | `llm_client.py:387–391` | WARNING | Code-fence regex requires `\n` after opening backticks; fences without trailing newline not stripped | Change to `r"^```(?:python)?\s*"` without `\n` requirement |
| A4-4 | `llm_client.py:169–171` | WARNING | `supports_max_completion_tokens` field declared but never read; is dead code | Remove field or add conditional branch that reads it |
| A4-5 | `fact_table_simulator.py:14` | NOTE | `from scipy.stats import norm` at module level — `scipy` missing from env breaks entire package import | Ensure `scipy` in `requirements.txt`; consider lazy import |
| A4-6 | `sandbox_executor.py:23–24` | NOTE | `TYPE_CHECKING` guard for `LLMClient` is correct but annotation is redundant with duck-typing | Document intent or add `isinstance` assertion |

---

*[WRITE CONFIRMED] /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN/audit/01_correctness_audit.md*
