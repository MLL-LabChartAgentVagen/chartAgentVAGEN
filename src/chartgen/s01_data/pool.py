"""The domain pool: two levels of subject matter, built once and sampled every run.

Building is four steps and happens once for the project:

    1  ask the model for topics          industry-level areas, mutually distinct
    2  ask it for sub-topics per topic   concrete analysis situations, with hints
    3  drop near-duplicates              by name similarity, one judge for both levels
    4  stop at the target count          keeping the three complexity tiers balanced

The result is a file with both levels in it: the topic list, and one entry per
sub-topic carrying the topic it came from. Sampling then draws sub-topics without
replacement inside a complexity tier and resets that tier once most of it is used,
so a long run keeps moving through the pool instead of circling a few entries.

The hints on a sub-topic are soft: a scenario may rewrite or replace them, but it
may not leave the subject area or the complexity tier.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal, Sequence

from ..common.rng import derive

Tier = Literal["simple", "medium", "complex"]

TIERS: tuple[Tier, ...] = ("simple", "medium", "complex")

#: Row counts each tier aims for, handed to the generating script.
TARGET_ROWS: dict[Tier, tuple[int, int]] = {
    "simple": (200, 500),
    "medium": (500, 1000),
    "complex": (1000, 3000),
}

TIER_MEANING: dict[Tier, str] = {
    "simple": "one entity type, 1-2 metrics, a straightforward time series",
    "medium": "several related metrics, more than one entity type",
    "complex": "nested hierarchies, three or more interdependent metrics",
}

#: Fraction of a tier that gets handed out before the tier resets to full.
RESET_AFTER = 0.8

POOL_VERSION = 1


@dataclass(frozen=True)
class Domain:
    """One sub-topic. The hint fields are suggestions a scenario may rewrite."""

    id: str
    name: str
    topic: str
    complexity_tier: Tier
    typical_entities_hint: tuple[str, ...] = ()
    typical_metrics_hint: tuple[dict[str, str], ...] = ()
    temporal_granularity_hint: str = "daily"

    @property
    def target_rows(self) -> tuple[int, int]:
        return TARGET_ROWS[self.complexity_tier]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "topic": self.topic,
                "complexity_tier": self.complexity_tier,
                "typical_entities_hint": list(self.typical_entities_hint),
                "typical_metrics_hint": [dict(m) for m in self.typical_metrics_hint],
                "temporal_granularity_hint": self.temporal_granularity_hint}

    @classmethod
    def from_dict(cls, raw: dict[str, Any], id: str | None = None) -> "Domain":
        return cls(id=id or raw["id"], name=str(raw["name"]), topic=str(raw.get("topic", "")),
                   complexity_tier=raw.get("complexity_tier", "medium"),
                   typical_entities_hint=tuple(str(v) for v in raw.get("typical_entities_hint", ())),
                   typical_metrics_hint=tuple(dict(m) for m in raw.get("typical_metrics_hint", ())),
                   temporal_granularity_hint=str(raw.get("temporal_granularity_hint", "daily")))


@dataclass(frozen=True)
class Pool:
    """Both levels of the pool: the topics, and the sub-topics under them."""

    domains: tuple[Domain, ...] = ()
    topics: tuple[str, ...] = ()
    version: int = POOL_VERSION

    def of_tier(self, tier: Tier) -> tuple[Domain, ...]:
        return tuple(d for d in self.domains if d.complexity_tier == tier)

    def under(self, topic: str) -> tuple[Domain, ...]:
        return tuple(d for d in self.domains if d.topic == topic)

    def stats(self) -> dict[str, dict[str, int]]:
        return {"tiers": {t: len(self.of_tier(t)) for t in TIERS},
                "topics": _counts(d.topic for d in self.domains)}

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "version": self.version,
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "stats": self.stats(),
            "topics": list(self.topics or tuple(dict.fromkeys(d.topic for d in self.domains))),
            "domains": [d.to_dict() for d in self.domains],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Pool":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if raw.get("version") != POOL_VERSION:
            raise ValueError(
                f"the domain pool is version {raw.get('version')}, this code writes {POOL_VERSION}")
        return cls(tuple(Domain.from_dict(d) for d in raw["domains"]),
                   tuple(raw.get("topics", ())), raw["version"])


def _counts(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


# ---------------------------------------------------------------- sampling

@dataclass
class Sampler:
    """Draw sub-topics without replacement inside a tier; reset the tier when
    `RESET_AFTER` of it is gone."""

    pool: Pool
    seed: int
    _left: dict[str, list[Domain]] = field(default_factory=dict, repr=False)
    _n: int = 0

    def __post_init__(self) -> None:
        self._left = {t: list(self.pool.of_tier(t)) for t in TIERS}

    def remaining(self, tier: Tier) -> int:
        return len(self._left[tier])

    def take(self, tier: Tier | None = None) -> Domain:
        """With no tier given, cycle simple, medium, complex."""
        tier = tier or TIERS[self._n % len(TIERS)]
        total = len(self.pool.of_tier(tier))
        if total == 0:
            raise KeyError(f"the domain pool holds no {tier} sub-topics")
        left = self._left[tier]
        picked = left.pop(int(derive(self.seed, "s01_pool", tier, self._n).integers(len(left))))
        self._n += 1
        if total - len(left) >= RESET_AFTER * total:
            self._left[tier] = list(self.pool.of_tier(tier))
        return picked


# ---------------------------------------------------------------- building

TOPIC_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["topics"],
                "properties": {"topics": {"type": "array", "items": {"type": "string"}}}}

#: One metric hint: what is measured and in what unit. Spelled out rather than
#: left as a free-form object, because structured output closes every object.
METRIC_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["name", "unit"],
    "properties": {"name": {"type": "string"}, "unit": {"type": "string"}},
}

SUBTOPIC_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["sub_topics"],
    "properties": {"sub_topics": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["name", "complexity_tier"],
        "properties": {"name": {"type": "string"},
                       "complexity_tier": {"type": "string", "enum": list(TIERS)},
                       "typical_entities_hint": {"type": "array", "items": {"type": "string"}},
                       "typical_metrics_hint": {"type": "array", "items": METRIC_SCHEMA},
                       "temporal_granularity_hint": {"type": "string"}}}}},
}

SYSTEM = ("You are building a pool of data analysis subject areas for chart "
          "generation. Reply with JSON only, no explanation.")

TOPIC_USER = """List {n} industry-level topics that do not overlap, to organise
data analysis situations under.

Topics already in the pool (do not repeat them or offer near-synonyms): {existing}

Reply with {{"topics": ["...", ...]}}."""

SUBTOPIC_USER = """Under the topic "{topic}", list {n} concrete data analysis situations.

For each one give:
  name                        the situation in a few words, e.g. "ICU bed turnover"
  complexity_tier             {tiers}
  typical_entities_hint       2-4 entity types
  typical_metrics_hint        1-3 metrics, each with a unit
  temporal_granularity_hint   daily, weekly or monthly

Keep the three complexity tiers roughly balanced.
Reply with {{"sub_topics": [{{...}}, ...]}}."""


def build(llm: Any, *, n_topics: int = 20, per_topic: int = 12, target: int = 200,
          existing_topics: Sequence[str] = (),
          is_duplicate: Callable[[str], bool] | None = None) -> Pool:
    """Ask for two levels, drop near-duplicates, stop at the target count."""
    seen = is_duplicate or (lambda _: False)
    topics = llm.json(SYSTEM,
                      TOPIC_USER.format(n=n_topics, existing=", ".join(existing_topics) or "none"),
                      schema=TOPIC_SCHEMA)["topics"][:n_topics]

    domains: list[Domain] = []
    used: list[str] = []
    tiers = "; ".join(f"{t} ({TIER_MEANING[t]})" for t in TIERS)
    for topic in topics:
        raw = llm.json(SYSTEM,
                       SUBTOPIC_USER.format(topic=topic, n=per_topic, tiers=tiers),
                       schema=SUBTOPIC_SCHEMA)["sub_topics"][:per_topic]
        used.append(topic)
        for item in raw:
            if seen(str(item["name"])):
                continue
            domains.append(Domain.from_dict({**item, "topic": topic},
                                            id=f"dom_{len(domains) + 1:03d}"))
        if len(domains) >= target:
            break
    return Pool(tuple(domains), tuple(used))
