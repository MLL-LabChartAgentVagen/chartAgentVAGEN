# DS-4: Multi-Column Group Dependency `on=[...]` — Summary of Changes

Implements DS-4 from `pipeline/phase_2/docs/stub_analysis/stub_gap_analysis.md`:
`add_group_dependency` now accepts `len(on) > 1` with a **nested-dict
`conditional_weights`** whose nesting depth equals `len(on)`. Resolves the
`NotImplementedError` raised at the SDK declaration site and the matching
gaps in the engine sampler, the L2 deviation walk, and two `dep.on[0]`-only
helpers (DAG cycle pre-check, orthogonal-conflict pre-check). Adopts
interpretation **(a)** from `stub_blocker_decisions.md §DS-4`: nested dict
(JSON-serializable, natural extension of the single-column case), full
Cartesian coverage required, no soft cap on combinations.

## Schema (the contract added)

```python
# Nesting depth = len(on); leaf is {child_value: weight}.
# Example for on=["severity", "hospital"]:
conditional_weights = {
    "Mild":     {"Xiehe": {"Insurance": 0.8, "Self-Pay": 0.2},
                 "Mayo":  {"Insurance": 0.7, "Self-Pay": 0.3}},
    "Moderate": {"Xiehe": {"Insurance": 0.6, "Self-Pay": 0.4},
                 "Mayo":  {"Insurance": 0.5, "Self-Pay": 0.5}},
}
```

- At depth `d`, keys must equal `set(columns[on[d]]["values"])` exactly
  — no missing, no extras.
- At the leaf, keys must equal `set(columns[child_root]["values"])` exactly.
- Weights are normalized per leaf via `normalize_weight_dict_values`
  (same rule as the single-column case).
- `len(on) == 1` is the existing single-column case; recursion terminates
  after one level and produces byte-identical normalized output.

## Files changed

### [pipeline/phase_2/sdk/relationships.py](pipeline/phase_2/sdk/relationships.py)

- `add_group_dependency` (L117-216): removed the `len(on) != 1`
  `NotImplementedError` block; the orthogonal-conflict and DAG-acyclicity
  pre-checks now loop over every `parent_col in on`; the inline
  per-parent-value validation block was replaced by a call to a new
  recursive helper. Type hint for `conditional_weights` widened to
  `dict[Any, Any]` (depth depends on `len(on)`); docstring rewritten to
  spell out the nested-dict invariant with an example.
- `_check_dependency_conflict` (L372-395): now iterates `for parent_col
  in dep.on` so multi-parent deps' non-first parent edges are not silently
  skipped during orthogonal declaration.
- New `_validate_and_normalize_nested_weights(cw, parent_value_sets,
  parent_cols, child_values, path)`: depth-first walk that validates key
  coverage at each level (with a key-access-style error path like
  `conditional_weights['Mild']['Mayo']`), rejects extras, and normalizes
  leaves via the existing `_val.normalize_weight_dict_values`. Empty
  top-level `cw` raises a `"... is empty."` ValueError that mirrors the
  pre-DS-4 message.

### [pipeline/phase_2/sdk/dag.py](pipeline/phase_2/sdk/dag.py)

- `check_root_dag_acyclic` (~L437): adjacency build now iterates
  `for parent in dep.on` rather than reading `dep.on[0]`. Without this fix
  cycle pre-checks would miss edges contributed by non-first parents of
  existing multi-parent deps. `build_full_dag` already iterated all
  parents — no change there.

### [pipeline/phase_2/engine/skeleton.py](pipeline/phase_2/engine/skeleton.py)

- `sample_dependent_root` (~L134-200): keeps the original single-parent
  batched path verbatim (per-parent-value mask + one `rng.choice` per
  block) so RNG draw ordering for `len(on) == 1` is **byte-identical**
  to v1. Multi-parent path walks the nested dict per row
  (`for arr in parent_arrays: node = node[arr[i]]`), then samples each
  row individually. Defensive renormalization at the leaf is idempotent
  since the validator normalizes at declaration time. Trailing
  `logger.debug` updated to print the full `dep.on` list.

### [pipeline/phase_2/validation/statistical.py](pipeline/phase_2/validation/statistical.py)

- `max_conditional_deviation` (~L24-65): rewritten as a recursive walker
  over arbitrarily nested dicts of equal depth. Detects leaf vs.
  recursive level by inspecting any value (`isinstance(v, dict)`). Depth-1
  behavior is identical to the previous double-loop, so single-column
  callers see no numerical difference.
- `check_group_dependency_transitions` (~L554-625): driver now groups the
  DataFrame by the **full `on` tuple** (always passed as a list to
  `df.groupby(...)`, which makes pandas yield tuple keys uniformly even
  for length 1). Builds the `observed` nested dict by drilling per-key
  into nested `setdefault` levels, then compares against declared via the
  recursive `max_conditional_deviation`. Missing-column branch lists all
  missing columns (parents and child) instead of the first parent only.
  Pass threshold (`< 0.10`) and `Check.name` format (`group_dep_<child>`)
  preserved.

### [pipeline/phase_2/types.py](pipeline/phase_2/types.py)

- `import copy` added at the module top (already used `dataclasses`).
- `GroupDependency.to_metadata` (~L204-216): the inline shallow
  comprehension `{k: dict(v) for k, v in cw.items()}` is replaced by
  `copy.deepcopy(self.conditional_weights)` so downstream metadata
  consumers can mutate at any depth without aliasing back into the
  store. The previous shallow form was correct for the only shape
  that existed pre-DS-4 (depth-2: one parent level + leaf); deepcopy
  is required for the new depth ≥ 3 shapes DS-4 enables.

### [pipeline/phase_2/tests/modular/test_sdk_relationships_multi_parent.py](pipeline/phase_2/tests/modular/test_sdk_relationships_multi_parent.py) (new)

Six test classes, 24 cases total:

- **`TestMultiParentDeclaration`** (3) — happy paths for 2-parent and
  3-parent declarations; per-leaf normalization (mixed scales,
  e.g., `80/20` and `4/1` both produce `0.8/0.2`).
- **`TestMultiParentValidationErrors`** (7) — missing parent at depth
  0/1/leaf, extra parent at depth 0, negative weight at leaf, empty
  `on`, empty `conditional_weights`. Asserts the error path string
  (`['Mild']['Mayo']`-style key access) and the relevant parent column
  name appear in the message.
- **`TestSingleParentBackwardCompat`** (2) — `on=["severity"]` with the
  old flat dict shape produces byte-identical normalized output to v1
  (pinned dict equality); single-column missing-parent error preserved.
- **`TestMultiParentDagAndConflict`** (5) — multi-parent cycle through
  `on[0]`; multi-parent cycle through `on[1]` (regression for the
  `dep.on[0]`-only adjacency bug); orthogonal conflict via first parent
  and via second parent (regression for the `_check_dependency_conflict`
  bug); declaring orthogonal **after** a multi-parent dep that touches
  the orthogonal pair via a non-first parent.
- **`TestToMetadataDeepCopy`** (1) — mutating both leaf weights and an
  inner dict on the metadata copy must not leak into the source
  `GroupDependency`.
- **`TestL2MultiParentDeviation`** (6) — `max_conditional_deviation` at
  depths 1/2/3; `check_group_dependency_transitions` 2-parent pass /
  fail / missing-column with the assertion that the detail string lists
  every parent column.

### [pipeline/phase_2/tests/modular/test_engine_skeleton_multi_parent.py](pipeline/phase_2/tests/modular/test_engine_skeleton_multi_parent.py) (new)

Two test classes, 3 cases:

- **`TestSampleDependentRootMultiParent`** (2) — 2-parent and 3-parent
  declarations with `target_rows ∈ {16000, 20000}` and a fixed RNG
  seed; per-cell empirical conditional matches declared within
  `< 0.025` (2-parent) and `< 0.05` (3-parent) absolute deviation,
  well below the 0.10 L2 threshold.
- **`TestSampleDependentRootSingleParentBackwardCompat`** (1) —
  byte-identical RNG output regression: replays the pre-DS-4 batched
  algorithm on the same seed and asserts `np.array_equal(out_new,
  result_ref)`.

## Verification

```bash
conda run -n chart pytest pipeline/phase_2/tests/ -x
# → 257 passed in 0.95s   (230 pre-existing + 27 new)
```

## Out of scope

- Updating `phase_2.md` Theme 4 spec (recommended in
  `stub_blocker_decisions.md §4.4` but not blocking — code can ship
  before the spec edit lands).
- Updating `orchestration/prompt.py` to advertise multi-column `on`
  in the LLM prompt or to demonstrate it in the One-Shot Example. The
  SDK signature change is the only public-API surface this stub needed
  to unblock; revealing it to the LLM is deferred until a workflow
  needs it.
- Soft cap on Cartesian-product cardinality for very deep `on` lists.
  Per the adopted decision, the LLM is responsible for declaring
  sensible cardinalities; failures fall through to
  `_validate_and_normalize_nested_weights`'s "missing keys" /
  "contains keys not in ..." errors with the full path.
- Non-string parent or child value handling in the L2 driver. The
  pre-DS-4 code already coerced observed keys to `str` while declared
  keys retained their native type; this implementation preserves that
  behavior (any latent str-vs-int mismatch was a pre-existing bug, not
  one introduced by DS-4).
