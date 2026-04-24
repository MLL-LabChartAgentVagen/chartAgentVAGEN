# M4 — Schema Metadata

## What This Module Does

M4 projects the frozen `DeclarationStore` into the **7-key `schema_metadata` dict** that is the contract between Phase 2 (generation + validation) and Phase 3 (view extraction, QA generation). It is also the input that drives M5's L1 / L2 / L3 validation. Position in the pipeline: **downstream** of M1 (reads frozen store) and logically parallel to M2 (both read the store) — though in the current implementation M4 is invoked **inline at the tail of [`engine.generator.run_pipeline`](../engine/generator.py)** after DataFrame synthesis completes. The transformation is pure: no side effects, deterministic, same inputs → same output.

## Internal Structure

```
pipeline/phase_2/metadata/
├── __init__.py          # re-exports build_schema_metadata
└── builder.py           # build_schema_metadata + 3 private helpers
```

**Data flow.** `build_schema_metadata(groups, orthogonal_pairs, target_rows, measure_dag_order, columns?, group_dependencies?, patterns?)` assembles the 7 keys in a fixed sequence: `dimension_groups` → `orthogonal_groups` → `group_dependencies` → `columns` (via `_build_columns_metadata`, which in turn delegates stochastic-measure `param_model` serialization to `_deep_copy_param_model`) → `measure_dag_order` → `patterns` → `total_rows`. After assembly, `_assert_metadata_consistency` runs as a post-build audit that emits `logger.warning` on failure but never raises — the builder always returns a dict.

## Key Interfaces

### External-facing

```python
from pipeline.phase_2.metadata import build_schema_metadata

build_schema_metadata(
    groups: dict[str, DimensionGroup],
    orthogonal_pairs: list[OrthogonalPair],
    target_rows: int,
    measure_dag_order: list[str],
    columns: OrderedDict[str, dict[str, Any]] | None = None,
    group_dependencies: list[GroupDependency] | None = None,
    patterns: list[dict[str, Any]] | None = None,
) -> dict[str, Any]
```

Returns a dict with exactly these seven top-level keys:

| Key | Shape | Source |
|---|---|---|
| `dimension_groups` | `{group_name: {columns: [...], hierarchy: [...]}}` | `group.to_metadata()` for each `DimensionGroup` |
| `orthogonal_groups` | `[{group_a, group_b, rationale}, ...]` | `pair.to_metadata()` for each `OrthogonalPair` |
| `group_dependencies` | `[{child_root, on, conditional_weights}, ...]` | `dep.to_metadata()` for each `GroupDependency` (or `[]` if none) |
| `columns` | `{col_name: {type, ...type-discriminated fields}}` | `_build_columns_metadata(columns)` (or `{}` if not provided) |
| `measure_dag_order` | `[measure_name, ...]` (topological order) | `list(measure_dag_order)` — M4 does not sort; caller supplies |
| `patterns` | `[{type, target, col, params}, ...]` | rebuilt per-pattern dict (or `[]` if none) |
| `total_rows` | `int` | direct assignment of `target_rows` |

### Internal (in [`builder.py`](builder.py))

| Function | Role |
|---|---|
| `_build_columns_metadata(columns) -> dict[str, dict[str, Any]]` | Type-discriminated per-column descriptor. Emits different fields depending on `col_meta["type"]`: `categorical` → `{type, values, weights, cardinality, group, parent}`; `temporal` → `{type, start, end, freq, derive, group}`; `temporal_derived` → `{type, derivation, source, group}`; `measure` / stochastic → `{type, measure_type, family, param_model}`; `measure` / structural → `{type, measure_type, formula, effects, noise}`. |
| `_deep_copy_param_model(pm) -> dict[str, Any]` | Deep-copies a stochastic measure's `param_model`. Handles both numeric scalar values and the `{intercept, effects: {col: {value: weight}}}` dict form, copying each nested `effects` mapping so downstream mutation is isolated. |
| `_assert_metadata_consistency(meta) -> None` | Post-build self-audit. Checks: every column named in `dimension_groups` appears in `columns`; every entry in `measure_dag_order` is a known `columns` entry; every `pattern.col` references a `type == "measure"` column; every `orthogonal_groups` group name exists in `dimension_groups`. Emits `logger.warning` on failure — does not raise. |

## How It Works

Execution order (see [`builder.py`](builder.py) lines 23–111):

1. **Key 1 — `dimension_groups`** (lines 60–63). Iterates `groups.items()` and calls `group.to_metadata()` on each `DimensionGroup`. **Why delegate to the dataclass:** the serialization shape is co-located with the dataclass definition in [`../types.py`](../types.py), so a future schema change to `DimensionGroup` can't silently skew metadata — the `to_metadata()` method is the contract boundary.
2. **Key 2 — `orthogonal_groups`** (lines 66–68). List comprehension over `orthogonal_pairs`, each calling `pair.to_metadata()`. Same delegation rationale.
3. **Key 3 — `group_dependencies`** (lines 71–76). `dep.to_metadata()` per entry; falls back to `[]` if the caller passed `None`. **Why a nullable default:** legacy callers and some test fixtures construct partial stores. Defaulting to `[]` (not skipping the key) keeps the 7-key shape stable for downstream consumers that index into it unconditionally.
4. **Key 4 — `columns`** (lines 79–82). Delegates to `_build_columns_metadata`, which branches on `col_meta["type"]`. **Why type-discriminated rather than a uniform schema:** a categorical genuinely needs different fields (`values`, `weights`, `cardinality`) than a stochastic measure (`family`, `param_model`) or a structural measure (`formula`, `effects`, `noise`). A uniform shape would either bloat every entry with nulls or force downstream code to do post-hoc type guessing. Null-fallback again if the caller didn't provide `columns`.
5. **Key 5 — `measure_dag_order`** (line 85). `list(measure_dag_order)` — a fresh list, not a reference. Upstream (`engine.generator`) has already topologically sorted the measure sub-DAG; M4 trusts that contract and never resorts.
6. **Key 6 — `patterns`** (lines 88–99). Rebuilt per-pattern dict `{type, target, col, params: dict(p.get("params", {}))}` — note the `dict(...)` wrapper on `params`. **Why rebuild rather than copy:** the declaration store's pattern dicts may contain extra internal fields over time; the 4-tuple shape here is exactly what M5 L3 consumes.
7. **Key 7 — `total_rows`** (line 102). Direct assignment of the scalar `target_rows`.
8. **Consistency audit** (line 105 → `_assert_metadata_consistency`, lines 194–252). Runs four structural checks and emits `logger.warning` on any failure. **Why warn-not-raise:** the builder ships metadata even if the input store is partially inconsistent. Raising here would be a second failure for a problem that should have been caught upstream by M1's incremental validators; warnings expose the bug in logs without blocking the pipeline.

**Defensive copying cuts across keys 3, 4, and 6.** `_deep_copy_param_model` handles nested stochastic-measure dicts; structural `effects` and `noise` are dict-copied inline (lines 168–171); `group_dependencies` copies via the dataclass `to_metadata()`; `patterns.params` is wrapped in `dict(...)`. **Why everywhere:** the returned dict flows to M5, to Phase 3, and potentially to disk via serialization. Downstream code should be free to mutate its copy (e.g. add computed stats, strip internal fields) without corrupting the source `DeclarationStore`. The store is nominally frozen, but Python's default shallow copies would leave nested dicts aliased — isolation has to be explicit.

**Known inconsistency (open).** The big README §9 and `docs/artifacts/stage5_anatomy_summary.md` document that structural-measure descriptors carry a `depends_on` field. The current `_build_columns_metadata` implementation ([`builder.py`](builder.py) lines 166–172) does **not** emit it — structural descriptors ship with `formula`, `effects`, and `noise` only. Pending a Phase 3 consumer decision on whether the doc is spec (add the field) or the code is spec (drop it from the doc).

See [`../../../docs/svg/module4_schema_metadata.md`](../../../docs/svg/module4_schema_metadata.md) for the visual walkthrough.

## Usage Example

**Inline call site from [`engine/generator.py`](../engine/generator.py) lines 105–126** — the only path that fires in production:

```python
from ..metadata.builder import build_schema_metadata as _build_meta
from ..sdk import dag as _dag

# Extract measure topological order from the already-built full DAG
measure_names: set[str] = {
    col_name for col_name, col_meta in columns.items()
    if col_meta.get("type") == "measure"
}
if measure_names:
    _, measure_order = _dag.extract_measure_sub_dag(full_dag, measure_names)
else:
    measure_order = []

metadata = _build_meta(
    groups=groups,
    orthogonal_pairs=orthogonal_pairs,
    target_rows=target_rows,
    measure_dag_order=list(measure_order),
    columns=columns,
    group_dependencies=group_dependencies,
    patterns=patterns,
)
# metadata is returned as the second element of run_pipeline's (df, metadata) tuple
```

**Standalone call from a test** (pattern from [`tests/modular/test_metadata_builder.py`](../tests/modular/test_metadata_builder.py)):

```python
from pipeline.phase_2.metadata import build_schema_metadata
from pipeline.phase_2.types import DeclarationStore, DimensionGroup, OrthogonalPair, GroupDependency

store = DeclarationStore(1000, 42)
store.columns.update({
    "region": {"type": "categorical", "group": "geo"},
    "city":   {"type": "categorical", "group": "geo", "parent": "region"},
    "revenue": {
        "type": "measure", "measure_type": "stochastic",
        "family": "gaussian", "param_model": {"mu": 100, "sigma": 15},
    },
})
store.groups["geo"] = DimensionGroup(
    name="geo", root="region",
    columns=["region", "city"], hierarchy=["region", "city"],
)
store.orthogonal_pairs.append(OrthogonalPair("geo", "demographics", "no relation"))

meta = build_schema_metadata(
    groups=store.groups,
    orthogonal_pairs=store.orthogonal_pairs,
    target_rows=1000,
    measure_dag_order=["revenue"],
    columns=store.columns,
    group_dependencies=store.group_dependencies,
    patterns=store.patterns,
)
assert set(meta) == {
    "dimension_groups", "orthogonal_groups", "group_dependencies",
    "columns", "measure_dag_order", "patterns", "total_rows",
}
```

## Dependencies

**Imported from the rest of `phase_2/`:**

- [`phase_2.types`](../types.py) — `DimensionGroup`, `OrthogonalPair`, `GroupDependency` (only for their `.to_metadata()` methods).

**External libraries:** `logging`, `collections.OrderedDict`, `typing.Any`.

**Preconditions.** Inputs come from a frozen `DeclarationStore`. `measure_dag_order` must already be topologically sorted — M4 does not sort; the upstream engine computes it via `sdk.dag.extract_measure_sub_dag`. `columns`, `group_dependencies`, and `patterns` are all `None`-tolerant: missing inputs become empty collections in the output.

**Postconditions.** Returns a fresh dict with exactly 7 top-level keys. All nested data is defensively copied; mutating the result cannot corrupt the source store. `_assert_metadata_consistency` has run and emitted any warnings.

**Who imports this module:** [`engine/generator.py`](../engine/generator.py) (line 106) calls it inline at the tail of `run_pipeline`; [`validation/validator.py`](../validation/validator.py) documents the returned dict as the input contract to `SchemaAwareValidator`.

## Testing

Unit tests live in [`../tests/modular/test_metadata_builder.py`](../tests/modular/test_metadata_builder.py) as the `TestBuildSchemaMetadata` class. Coverage includes the 7-key contract, `total_rows` pass-through, column extraction, defensive-copy isolation, and the consistency-check code path.

```bash
# From repo root
pytest pipeline/phase_2/tests/modular/test_metadata_builder.py -v

# M4 is exercised indirectly by any engine test that runs run_pipeline
pytest pipeline/phase_2/tests/modular/test_engine_generator.py -v
```
