"""
AGPDS Phase 1 typed schemas (Sprint C.3).

Three frozen dataclasses replace the loose dicts that used to flow from
Phase 1 generation through scenario_pool.jsonl into Phase 2:

  Metric          — one named measure with unit + (low, high) numeric range
  ScenarioContext — the six fields produced by ScenarioContextualizer.generate
  ScenarioRecord  — the JSONL envelope (domain_id, k, scenario, generated_at)

`from_dict` constructors silently ignore unknown keys so legacy
scenario_pool.jsonl records carrying ``category_id`` (Sprint C.2) or
``_validation_warnings`` (Sprint C.4) load without modification.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pipeline.core.ids import format_scenario_id


@dataclass(frozen=True)
class Metric:
    name: str
    unit: str
    range: tuple[float, float]   # strict low < high

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Metric":
        if not isinstance(raw, dict):
            raise TypeError(
                f"Metric must come from a dict, got {type(raw).__name__}"
            )
        rng_raw = raw.get("range")
        if not (isinstance(rng_raw, (list, tuple)) and len(rng_raw) == 2):
            raise ValueError(
                f"Metric.range must be a [low, high] pair; got {rng_raw!r}"
            )
        try:
            rng = (float(rng_raw[0]), float(rng_raw[1]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Metric.range elements must be numeric: {exc}")
        if not (rng[0] < rng[1]):
            raise ValueError(
                f"Metric.range low must be < high; got {rng}"
            )
        return cls(name=str(raw["name"]), unit=str(raw["unit"]), range=rng)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "unit": self.unit,
            "range": [self.range[0], self.range[1]],
        }


_SCENARIO_REQUIRED = (
    "scenario_title",
    "data_context",
    "temporal_granularity",
    "key_entities",
    "key_metrics",
    "target_rows",
)


@dataclass(frozen=True)
class ScenarioContext:
    scenario_title: str
    data_context: str
    temporal_granularity: str
    key_entities: tuple[str, ...]
    key_metrics: tuple[Metric, ...]
    target_rows: int

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ScenarioContext":
        if not isinstance(raw, dict):
            raise TypeError(
                f"ScenarioContext must come from a dict, got {type(raw).__name__}"
            )
        missing = [k for k in _SCENARIO_REQUIRED if k not in raw]
        if missing:
            raise ValueError(f"ScenarioContext missing fields: {missing}")
        return cls(
            scenario_title=str(raw["scenario_title"]),
            data_context=str(raw["data_context"]),
            temporal_granularity=str(raw["temporal_granularity"]),
            key_entities=tuple(str(e) for e in raw["key_entities"]),
            key_metrics=tuple(Metric.from_dict(m) for m in raw["key_metrics"]),
            target_rows=int(raw["target_rows"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_title": self.scenario_title,
            "data_context": self.data_context,
            "temporal_granularity": self.temporal_granularity,
            "key_entities": list(self.key_entities),
            "key_metrics": [m.to_dict() for m in self.key_metrics],
            "target_rows": self.target_rows,
        }


@dataclass(frozen=True)
class ScenarioRecord:
    """Top-level envelope for one ``scenario_pool.jsonl`` line.

    ``scenario_id`` is derived from (domain_id, k) and never persisted —
    matches the format helpers added in Sprint B.8.
    """
    domain_id: str
    k: int
    scenario: ScenarioContext
    generated_at: str = ""

    @property
    def scenario_id(self) -> str:
        return format_scenario_id(self.domain_id, self.k)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ScenarioRecord":
        if not isinstance(raw, dict):
            raise TypeError(
                f"ScenarioRecord must come from a dict, got {type(raw).__name__}"
            )
        if "domain_id" not in raw or "k" not in raw or "scenario" not in raw:
            raise ValueError(
                "ScenarioRecord requires domain_id, k, and scenario "
                f"(got keys: {sorted(raw)})"
            )
        return cls(
            domain_id=str(raw["domain_id"]),
            k=int(raw["k"]),
            scenario=ScenarioContext.from_dict(raw["scenario"]),
            generated_at=str(raw.get("generated_at", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "domain_id": self.domain_id,
            "k": self.k,
            "scenario": self.scenario.to_dict(),
        }
        if self.generated_at:
            out["generated_at"] = self.generated_at
        return out
