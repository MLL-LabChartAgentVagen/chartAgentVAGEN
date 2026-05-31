"""JSON (de)serialization for Phase 2 raw_declarations.

Stage 1 (agpds_generate) persists raw_declarations to disk so Stage 2
(agpds_execute) can replay deterministic generation without the LLM.

raw_declarations is the dict captured from the _TrackingSimulator registry:
    columns               OrderedDict[str, dict]
    groups                dict[str, DimensionGroup]       (dataclass)
    group_dependencies    list[GroupDependency]           (dataclass list)
    orthogonal_pairs      list[OrthogonalPair]            (dataclass list)
    measure_dag           dict[str, list[str]]
    patterns              list[dict]
    target_rows           int
    seed                  int
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict
from typing import Any

from .types import DimensionGroup, GroupDependency, OrthogonalPair


def declarations_to_json(raw_declarations: dict[str, Any]) -> dict[str, Any]:
    """Convert a raw_declarations dict into a fully JSON-serializable dict."""
    groups = raw_declarations.get("groups", {}) or {}
    group_deps = raw_declarations.get("group_dependencies", []) or []
    ortho = raw_declarations.get("orthogonal_pairs", []) or []

    return {
        "columns": [
            {"name": k, "spec": v} for k, v in raw_declarations.get("columns", {}).items()
        ],
        "groups": {name: asdict(g) for name, g in groups.items()},
        "group_dependencies": [asdict(d) for d in group_deps],
        "orthogonal_pairs": [asdict(p) for p in ortho],
        "measure_dag": raw_declarations.get("measure_dag", {}) or {},
        "patterns": raw_declarations.get("patterns", []) or [],
        "target_rows": raw_declarations.get("target_rows"),
        "seed": raw_declarations.get("seed", 42),
    }


def _coerce_keys_by_columns(
    node: Any,
    level_cols: list[str],
    columns: dict[str, Any],
) -> Any:
    """Coerce stringified dict keys back to each governing column's declared
    value dtype.

    ``level_cols[i]`` names the column whose values key ``node`` at depth i;
    when ``level_cols`` is exhausted (or ``node`` is not a dict) the node is a
    leaf (a weight float or a per-child weight list) and is returned unchanged.

    Why this is needed: ``json.dumps`` forces every dict key to ``str``, but a
    categorical's ``values`` keep their declared dtype across the round-trip. So
    an int-valued parent (e.g. ``year=[2023, 2024]``) whose conditional weights
    were declared with int keys (``{2023: ...}``) comes back string-keyed
    (``{"2023": ...}``) and never matches the int column in
    ``skeleton.sample_dependent_root`` (``parent_values == parent_val``),
    silently producing an all-None dependent column. This restores the
    in-memory (Stage-1) key dtype so replay == generation.
    """
    if not isinstance(node, dict) or not level_cols:
        return node
    vals = (columns.get(level_cols[0]) or {}).get("values") or []
    keymap = {str(v): v for v in vals}
    return {
        keymap.get(k, k): _coerce_keys_by_columns(sub, level_cols[1:], columns)
        for k, sub in node.items()
    }


def declarations_from_json(d: dict[str, Any]) -> dict[str, Any]:
    """Rehydrate a JSON dict back into the raw_declarations shape Loop B expects."""
    columns = OrderedDict()
    for entry in d.get("columns", []):
        columns[entry["name"]] = entry["spec"]

    # Restore key dtypes the JSON round-trip stringified (see
    # _coerce_keys_by_columns). Within-group child categoricals key their dict
    # weights by the parent column's values; leaf is a per-child weight list.
    # Replace the spec with a shallow copy rather than mutating the input dict.
    for name in list(columns):
        spec = columns[name]
        if (
            spec.get("type") == "categorical"
            and isinstance(spec.get("weights"), dict)
            and spec.get("parent")
        ):
            columns[name] = {
                **spec,
                "weights": _coerce_keys_by_columns(
                    spec["weights"], [spec["parent"]], columns,
                ),
            }

    groups = {
        name: DimensionGroup(**payload)
        for name, payload in (d.get("groups") or {}).items()
    }

    group_deps = []
    for payload in d.get("group_dependencies", []) or []:
        # Cross-group conditional_weights nest by each parent in `on`, then the
        # innermost level is keyed by the child_root's own values. Build a
        # coerced copy — do not mutate the caller's payload dict.
        level_cols = list(payload.get("on", [])) + [payload["child_root"]]
        gd_payload = {
            **payload,
            "conditional_weights": _coerce_keys_by_columns(
                payload.get("conditional_weights", {}), level_cols, columns,
            ),
        }
        group_deps.append(GroupDependency(**gd_payload))
    ortho = [OrthogonalPair(**payload) for payload in d.get("orthogonal_pairs", []) or []]

    return {
        "columns": columns,
        "groups": groups,
        "group_dependencies": group_deps,
        "orthogonal_pairs": ortho,
        "measure_dag": d.get("measure_dag", {}) or {},
        "patterns": d.get("patterns", []) or [],
        "target_rows": d.get("target_rows"),
        "seed": d.get("seed", 42),
    }
