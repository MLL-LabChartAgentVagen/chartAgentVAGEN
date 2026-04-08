---
title: "Sprint 2 Fix Plan — Correctness & Security"
date: 2026-03-04
issue_count:
  security: 1
  correctness: 3
sprint1_dependencies: no
---

# Sprint 2 Fix Plan — Correctness & Security

## Step 1 — Sprint 2 Issue List (Verbatim)

From `audit/04_final_report.md` §3 "Sprint 2: Correctness & Security Fixes (P1)":

| Step | Issue IDs | Implementation | Sequencing Rationale |
|------|-----------|----------------|---------------------|
| 2.1 | F-004 | In `sandbox_executor.py:65`, replace `"__import__": __import__` with a `_safe_import` function that whitelists `{"math", "datetime", "decimal", "fractions", "statistics", "random"}` and raises `ImportError` for all others. | Security fix — must be done before running any LLM-generated code in production. |
| 2.2 | F-006 | In `agpds_runner.py:105`, change `default="gemini-3.1-pro-preview"` to `default="gemini-2.0-flash"`. | Independent fix; unblocks CLI without `--model` flag. |
| 2.3 | F-007 | In `scenario_contextualizer.py:283`, change `from phase_0.domain_pool import check_overlap` to `from pipeline.phase_0.domain_pool import check_overlap`. | Independent fix; unblocks `deduplicate_scenarios()`. |
| 2.4 | F-008 | In `sandbox_executor.py`, add `feedback_text: str = ""` before the retry loop (around line 465). | Defensive hardening; prevents future breakage. |

---

## Step 2 — Per-Issue Fix Specifications

### Issue F-004 — Unrestricted `__import__` in sandbox builtins 🔴 SECURITY

- **Affected file(s):** `pipeline/phase_2/sandbox_executor.py` line 66
- **Vulnerability class:** Unsafe Input Handling / Sandbox Bypass
- **Attack surface:** LLM-generated scripts can call `__import__("os").system(...)` because unrestricted `__import__` is exposed via `_SAFE_BUILTINS`.
- **Fix approach:** Replace with whitelist-restricted `_safe_import()` function.
- **Exact change:**
  ```diff
  +_ALLOWED_MODULES = frozenset({
  +    "math", "datetime", "decimal", "fractions", "statistics", "random",
  +})
  +
  +def _safe_import(name, *args, **kwargs):
  +    if name not in _ALLOWED_MODULES:
  +        raise ImportError(
  +            f"Import of '{name}' is not allowed in the sandbox. "
  +            f"Permitted modules: {sorted(_ALLOWED_MODULES)}"
  +        )
  +    return __import__(name, *args, **kwargs)
  +
   _SAFE_BUILTINS = {
  -    "__import__": __import__,
  +    "__import__": _safe_import,
  ```
- **Side effects:** LLM scripts importing disallowed modules will now fail with `ImportError` (intended behavior).
- **Regression risk:** No Sprint 1 interaction.
- **Verification:** Test 4 in `test_sandbox_executor.py` (blocked imports) must correctly block `import os`.

---

### Issue F-006 — Invalid default model name 🟡 CORRECTNESS

- **Affected file(s):** `pipeline/agpds_runner.py` line 105
- **Root cause:** `default="gemini-3.1-pro-preview"` references a non-existent model.
- **Exact change:**
  ```diff
  -    parser.add_argument("--model", default="gemini-3.1-pro-preview", help="Model name")
  +    parser.add_argument("--model", default="gemini-2.0-flash", help="Model name")
  ```
- **Regression risk:** No Sprint 1 interaction.
- **Verification:** Line inspection.

---

### Issue F-007 — Wrong import path in `deduplicate_scenarios` 🟡 CORRECTNESS

- **Affected file(s):** `pipeline/phase_1/scenario_contextualizer.py` line 283
- **Root cause:** `from phase_0.domain_pool import check_overlap` — `phase_0` is not a top-level package.
- **Exact change:**
  ```diff
  -    from phase_0.domain_pool import check_overlap
  +    from pipeline.phase_0.domain_pool import check_overlap
  ```
- **Regression risk:** No Sprint 1 interaction.
- **Verification:** `python -c "from pipeline.phase_1.scenario_contextualizer import deduplicate_scenarios"` must succeed.

---

### Issue F-008 — Uninitialized `feedback_text` before retry loop 🟡 CORRECTNESS

- **Affected file(s):** `pipeline/phase_2/sandbox_executor.py` line 465–467
- **Root cause:** `feedback_text` referenced before assignment if loop flow changes.
- **Exact change:**
  ```diff
       messages_history: list[dict] = []
  +    feedback_text: str = ""

       for attempt in range(max_retries):
  ```
- **Regression risk:** No Sprint 1 interaction.
- **Verification:** All 9 sandbox tests must still pass.

---

## Step 3 — Execution Order

| Priority | Step | Issue ID | Type | File:Lines |
|----------|------|----------|------|------------|
| 1 | 3.1 | F-004 | 🔴 SECURITY | `sandbox_executor.py:55–66` |
| 2 | 3.2 | F-008 | 🟡 CORRECTNESS | `sandbox_executor.py:465–467` |
| 3 | 3.3 | F-006 | 🟡 CORRECTNESS | `agpds_runner.py:105` |
| 4 | 3.4 | F-007 | 🟡 CORRECTNESS | `scenario_contextualizer.py:283` |

**Sprint 1 dependencies:** None identified.

---

## Step 4 — Verification Plan

```bash
# 1. Sandbox executor tests (9 tests) — verifies F-004 + F-008
PYTHONPATH=. python -m pipeline.phase_2.tests.test_sandbox_executor

# 2. F-007 import verification
PYTHONPATH=. python -c "from pipeline.phase_1.scenario_contextualizer import deduplicate_scenarios; print('F-007: OK')"

# 3. F-006 line inspection
grep -n 'default=' pipeline/agpds_runner.py | grep model
```

### Completion Criteria
- All 9 sandbox tests pass
- `import os` blocked in sandbox (Test 4)
- `deduplicate_scenarios` importable without error
- Default model is `gemini-2.0-flash`
- Execution log written to `audit/06_sprint2_execution_log.md`
