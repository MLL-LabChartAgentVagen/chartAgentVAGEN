---
title: "Sprint 1 Fix Plan — Unblock End-to-End Pipeline (P0)"
date: 2026-03-04
issue_count: 3
estimated_files_modified: 3
---

# Sprint 1 Fix Plan — Unblock End-to-End Pipeline

## Step 1 — Sprint 1 Issue List (Verbatim)

The following issues are reproduced verbatim from `audit/04_final_report.md` §3 "Sprint 1: Unblock End-to-End Pipeline (P0)":

| Issue ID | Priority | File:Lines | Description |
|----------|----------|------------|-------------|
| F-001 | **P0** | `agpds_pipeline.py:65–73` | Prompt references `generate_with_validation()` and `get_schema_metadata()` which do not exist on `FactTableSimulator`; all LLM scripts fail with `AttributeError`. Hex seed also non-integer. |
| F-002 | **P0** | `fact_table_simulator.py:984–991` | `pat_entry.update(p["params"])` flattens params into top-level dict; LLM params containing `"type"`, `"col"`, or `"target"` silently overwrite reserved metadata keys, corrupting the Phase 3 contract. |
| F-003 | **P0** | `fact_table_simulator.py:941–962` | `_build_schema_metadata()` emits `columns[*]["type"]` but not `columns[*]["role"]` (`primary`/`secondary`/`orthogonal`/`temporal`/`measure`). Phase 3's `ViewEnumerator._group_columns_by_role()` reads `col["role"]` — will crash. |

Sprint 1 also addresses **F-005** (P1) as a side-effect of fixing F-001 (the double-wrapping is caused by `_build_phase2_prompt`).

---

## Step 2 — Per-Issue Fix Specifications

### Issue F-001 + F-005 — Non-existent SDK methods in prompt & double-wrapped prompt

- **Affected file(s):** `pipeline/agpds_pipeline.py` lines 51–76 (method `_build_phase2_prompt`), lines 105–107 (call site in `run_single`)
- **Root cause:** `_build_phase2_prompt()` at line 65 instructs the LLM to call `simulator.generate_with_validation()` and `simulator.get_schema_metadata()` — neither method exists on `FactTableSimulator`. The hex seed `hashlib.md5(...).hexdigest()[:6]` is also a string, not an integer. Additionally, the pre-formatted prompt is then passed as `scenario_context` to `run_with_retries()` at line 107, which wraps it again with `[SCENARIO]...[AGENT CODE]` at `sandbox_executor.py:462`, resulting in a malformed double-wrapped prompt. (`agpds_pipeline.py:51–76`, `agpds_pipeline.py:105–107`)
- **Fix approach:** Delete + Patch
- **Exact change description:**
  - **Now:** Lines 51–76 define `_build_phase2_prompt()` which constructs a custom prompt with wrong API calls. Line 105 calls `self._build_phase2_prompt(scenario)`. Line 107 passes the result to `run_with_retries()`.
  - **After:** Delete the entire `_build_phase2_prompt()` method (lines 51–76). Replace line 105 with `phase2_user_prompt = json.dumps(scenario, indent=2)`. This lets `run_with_retries()` use the correct `PHASE2_SYSTEM_PROMPT` already defined in `sandbox_executor.py:370–428`.
- **Risk:** **Low** — `PHASE2_SYSTEM_PROMPT` is already complete, tested, and contains the correct SDK reference. The only change is removing the broken intermediary.
- **Verification method:**
  1. Confirm `_build_phase2_prompt` no longer exists in `agpds_pipeline.py`.
  2. Confirm `run_single()` passes a JSON string (not a pre-formatted prompt) to `run_with_retries()`.
  3. Run the existing test: `cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN && python -m pipeline.phase_2.tests.test_fact_table_simulator` (tests 1–9 should still pass since they test the SDK directly, not the pipeline).

---

### Issue F-002 — Pattern params flattening corrupts metadata keys

- **Affected file(s):** `pipeline/phase_2/fact_table_simulator.py` lines 982–991 (in `_build_schema_metadata`), `pipeline/phase_2/validators.py` lines 306–308 (L3 `trend_break` check reads `p.get("break_point")`)
- **Root cause:** At line 990, `pat_entry.update(p["params"])` flattens all pattern params into the top-level dict. If the LLM passes params like `{"type": "left", "break_point": "2024-06-01"}`, the `"type"` key silently overwrites `pat_entry["type"]` (the pattern type), corrupting the metadata. (`fact_table_simulator.py:990`)
- **Fix approach:** Patch (2 files)
- **Exact change description:**
  - **File 1 — `fact_table_simulator.py:990`**
    - **Now:** `pat_entry.update(p["params"])`
    - **After:** `pat_entry["params"] = dict(p["params"])`
  - **File 2 — `validators.py:308`**
    - **Now:** `bp_str = p.get("break_point")` (reads from top-level, which only works because of the flattening bug)
    - **After:** `bp_str = p.get("params", {}).get("break_point")` (reads from nested params, correct after the fix)
  - **File 2 — `validators.py:286`**
    - **Now:** `metrics = p.get("metrics", [])` (reads from top-level for `ranking_reversal`)
    - **After:** `metrics = p.get("params", {}).get("metrics", [])` (reads from nested params)

  > **Note:** The `_amplify_magnitude` auto-fix function at `validators.py:549` already reads `params = p.get("params", {})` — it is **currently broken** under the flattened schema, and this fix will **correct** it.

- **Risk:** **Medium** — Any downstream code that reads pattern metadata from the top-level dict will break. However, the only downstream consumer is the L3 validator which we are updating in the same fix.
- **Verification method:**
  1. Run `cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN && python -m pipeline.phase_2.tests.test_fact_table_simulator` — Test 1 (hospital example) exercises patterns and must still pass.
  2. Run `cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN && python -m pipeline.phase_2.tests.test_validators` — Tests 1–8 exercise L3 pattern validation and must still pass.
  3. Manually inspect the `meta["patterns"]` output from Test 1 to confirm params are nested under `"params"` key, not flattened.

---

### Issue F-003 — Missing `role` field in column metadata

- **Affected file(s):** `pipeline/phase_2/fact_table_simulator.py` lines 941–962 (in `_build_schema_metadata`, the `columns_meta` construction)
- **Root cause:** The `columns_meta` list comprehension builds entries with `"type"` (categorical/temporal/measure) but never assigns a `"role"` field. Phase 3's `ViewEnumerator._group_columns_by_role()` reads `col["role"]` and will `KeyError`. (`fact_table_simulator.py:944–962`)
- **Fix approach:** Add
- **Exact change description:**
  - **Now:** Categorical column entries have `{"name", "type", "group", "parent", "cardinality"}`. Temporal has `{"name", "type"}`. Measure has `{"name", "type", "declared_dist", "declared_params"}`.
  - **After:** Add a `"role"` field to each column entry:
    - **Categorical with no parent** → `"role": "primary"`
    - **Categorical with a parent** → `"role": "secondary"`
    - **Temporal** → `"role": "temporal"`
    - **Measure** → `"role": "measure"`
    - Additionally, for categorical columns whose group participates in an orthogonal declaration as a counterpart, annotate the column with an additional `"orthogonal": True` flag (enables Phase 3 to identify independent dimensions).
- **Risk:** **Low** — This is purely additive; no existing field is changed. The new `"role"` key fills a gap that Phase 3 requires.
- **Verification method:**
  1. Run `cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN && python -m pipeline.phase_2.tests.test_fact_table_simulator` — Test 1 must still pass.
  2. Inspect `meta["columns"]` output from Test 1 to confirm every column has a `"role"` field with the correct value.
  3. Verify orthogonal columns have `"orthogonal": True`.

---

## Step 3 — Execution Sequence

| Step | Issue IDs | Rationale | Est. Lines Touched |
|------|-----------|-----------|-------------------|
| **1** | F-001, F-005 | **Must come first** — this is the #1 blocker. Nothing can run end-to-end until the prompt is fixed. Removes the broken `_build_phase2_prompt` method and fixes the call site. No downstream dependencies. | ~30 lines (delete 26, modify 3) |
| **2** | F-002 | **Must come before F-003** because pattern metadata correctness must be established (nested `params` structure) before adding new fields to column metadata. Also updates validators to read from the new nested structure. | ~6 lines (modify 1 in `fact_table_simulator.py`, modify 2 in `validators.py`) |
| **3** | F-003 | **Must come after F-002** because clean metadata structure is a prerequisite for adding new fields. Adds `"role"` to all column entries in `_build_schema_metadata()`. | ~12 lines (modify/add in `fact_table_simulator.py`) |

---

## Step 4 — Verification Plan

### Automated Tests

All tests run from the project root: `/home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN`

```bash
# 1. FactTableSimulator SDK tests (9 tests: end-to-end, ordering, orthogonality, 
#    hierarchy, correlation, conditional, pattern, reproducibility, validation)
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN && python -m pipeline.phase_2.tests.test_fact_table_simulator

# 2. Validator tests (8 tests: L3 patterns, KS, auto-fix, generate_with_validation, regression)
cd /home/dingcheng/projects/chartAgent_copy/chartAgentVAGEN && python -m pipeline.phase_2.tests.test_validators
```

### Manual Verification

After all fixes are applied, manually verify the schema metadata output:

```python
# Quick smoke test (run from project root)
import sys; sys.path.insert(0, '.')
from pipeline.phase_2.fact_table_simulator import FactTableSimulator
sim = FactTableSimulator(target_rows=100, seed=42)
sim.add_category("hospital", values=["A","B"], weights=[0.5,0.5], group="entity")
sim.add_category("dept", values=["ER","ICU"], weights=[0.6,0.4], group="entity", parent="hospital")
sim.add_category("region", values=["N","S"], weights=[0.5,0.5], group="geo")
sim.add_measure("cost", dist="gaussian", params={"mu":100,"sigma":20})
sim.add_temporal("date", start="2024-01-01", end="2024-06-30", freq="D")
sim.declare_orthogonal("entity", "geo", rationale="test")
sim.inject_pattern("outlier_entity", target="hospital == 'A'", col="cost", params={"z_score": 3.0})
df, meta = sim.generate()

# Verify F-002: params nested
assert "params" in meta["patterns"][0], "F-002: params should be nested"
assert "z_score" not in meta["patterns"][0], "F-002: z_score should NOT be at top level"

# Verify F-003: role field present
for col in meta["columns"]:
    assert "role" in col, f"F-003: column '{col['name']}' missing 'role'"
print("All manual checks passed!")
```

---

[WRITE CONFIRMED] audit/05_sprint1_fix_plan.md | 115 lines
