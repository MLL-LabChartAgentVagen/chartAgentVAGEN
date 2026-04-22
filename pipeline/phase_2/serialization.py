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


def declarations_from_json(d: dict[str, Any]) -> dict[str, Any]:
    """Rehydrate a JSON dict back into the raw_declarations shape Loop B expects."""
    columns = OrderedDict()
    for entry in d.get("columns", []):
        columns[entry["name"]] = entry["spec"]

    groups = {
        name: DimensionGroup(**payload)
        for name, payload in (d.get("groups") or {}).items()
    }

    group_deps = [GroupDependency(**payload) for payload in d.get("group_dependencies", []) or []]
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
