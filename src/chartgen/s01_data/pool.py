"""The domain pool: two levels of subject matter, built once and sampled every run.

The pool is built over two declared axes, not one. **Area** is what the data is
about; **register** is who produced it and for whom. Asking only for subjects is
what produced the pool this replaced: seventeen subjects spanning aviation, banking,
farming and sport, and every one of them written as an operations dashboard --
"Operations", "Merchandising", "Processing", "Usage", "Occupancy". Municipal transit
and clinical trials were in it and came back as operations monitoring too, so the
register is not something a subject implies. It is asked for.

A register decides the vocabulary a subject is written in: who the entities are, what
one row is, how often it is published, and whether the numbers can go negative. A
national statistics release breaks a country down by age band and reports a
year-on-year change; a company's own dashboard breaks a site down by shift and
reports a count. Those are different pages, and only one of them was in the pool.

Building runs over the declared (subject, register) cells:

    1  per cell, ask for topics           topics inside that subject, in that register
    2  per topic, ask for sub-topics      concrete situations, with hints
    3  drop near-duplicates               by name similarity, one judge for both levels
    4  backfill the thin tier             until the three complexity tiers are level

The result is a file with both levels in it: the topic list, and one entry per
sub-topic carrying its topic, subject and register. Sampling then draws sub-topics
without replacement inside a complexity tier and resets that tier once most of it is
used, so a long run keeps moving through the pool instead of circling a few entries.

The hints on a sub-topic are soft: a scenario may rewrite or replace them, but it may
not leave the subject, the register or the complexity tier.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
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

POOL_VERSION = 2


# ---------------------------------------------------------------- the two axes

@dataclass(frozen=True)
class Register:
    """Who published a number and for whom, spelled out far enough to write with.

    Four mechanical facts rather than an adjective: a register the prompt can only
    paraphrase is a register the answer collapses back out of.
    """

    name: str
    what: str
    producer: str
    audience: str
    grain: tuple[str, ...]
    entities: str
    metrics: str
    signed: bool = False        # whether its numbers routinely go negative


REGISTERS: tuple[Register, ...] = (
    Register("operational", "an organisation watching its own process",
             "the organisation running the process", "the people running it",
             ("daily", "weekly"),
             "site, store, line, route, shift, team, product",
             "counts, durations and rates"),
    Register("official_statistics",
             "a statistical agency publishing comparable indicators",
             "a national or intergovernmental statistics body",
             "anyone comparing places or groups",
             ("yearly", "quarterly", "monthly"),
             "country, region, sector, age band, sex, education level, income group",
             "indices, shares, per-capita figures and year-on-year changes",
             signed=True),
    Register("research", "a study reporting what it measured",
             "the researchers who ran it", "other researchers",
             ("daily", "weekly", "monthly", "yearly"),
             "treatment arm, cohort, species, instrument, site, dose",
             "measurements with spread, distributions and relations",
             signed=True),
    Register("survey", "a survey or panel reporting what respondents said",
             "the organisation that fielded it", "readers of its report",
             ("yearly", "monthly", "quarterly"),
             "respondent segment, answer option, wave, country",
             "shares of respondents and index scores"),
    Register("disclosure", "an organisation reporting results to outsiders",
             "the organisation itself", "investors, regulators and the press",
             ("quarterly", "yearly", "monthly"),
             "business segment, geography, fiscal period, product line, line item",
             "amounts, margins and growth rates",
             signed=True),
    Register("registry", "an administrative record system counted up",
             "the agency that keeps the records", "the public and the agency",
             ("daily", "monthly", "quarterly"),
             "case, permit, filing, inspection, incident, agency, programme, district",
             "counts and amounts per line item"),
)

REGISTER = {r.name: r for r in REGISTERS}


@dataclass(frozen=True)
class Subject:
    """What the data is about, and which registers publish it."""

    name: str
    what: str
    registers: tuple[str, ...]


#: Fourteen subjects over six registers. A subject declares the registers it is
#: published in rather than all six, because the product would ask for pages nobody
#: writes -- a household survey of ore extraction is not a thing.
SUBJECTS: tuple[Subject, ...] = (
    Subject("labour and work", "jobs, pay, hours, skills and workplaces",
     ("official_statistics", "survey", "operational", "registry")),
    Subject("education and learning", "schools, universities, training and attainment",
     ("official_statistics", "survey", "operational")),
    Subject("research and innovation", "studies, funding, publication and patents",
     ("research", "official_statistics", "disclosure")),
    Subject("health and care", "illness, treatment, services and the people who give them",
     ("operational", "official_statistics", "research", "registry")),
    Subject("population and society", "who lives where, households, migration and time use",
     ("official_statistics", "survey", "registry")),
    Subject("government and public finance", "budgets, taxes, programmes and public services",
     ("registry", "official_statistics", "disclosure", "survey")),
    Subject("macroeconomy and trade", "output, prices, trade flows and the balance of payments",
     ("official_statistics", "registry", "survey")),
    Subject("money and markets", "lending, insurance, investment and payments",
     ("disclosure", "official_statistics", "operational")),
    Subject("energy and utilities", "generation, networks, fuel, water and waste",
     ("operational", "official_statistics", "disclosure")),
    Subject("climate and environment", "weather, emissions, land, water quality and species",
     ("research", "official_statistics", "registry")),
    Subject("food and agriculture", "crops, livestock, fisheries, food supply and diet",
     ("operational", "official_statistics", "research")),
    Subject("transport and mobility", "how people and goods move, and the networks they move on",
     ("operational", "official_statistics", "registry")),
    Subject("industry and technology", "making things, construction, software and communications",
     ("operational", "disclosure", "survey", "official_statistics")),
    Subject("culture, media and consumer", "what people read, watch, buy and spend time on",
     ("survey", "operational", "disclosure")),
)


def cells() -> tuple[tuple[Subject, Register], ...]:
    """Every declared (subject, register) pair, in declaration order."""
    return tuple((s, REGISTER[r]) for s in SUBJECTS for r in s.registers)


@dataclass(frozen=True)
class Domain:
    """One sub-topic. The hint fields are suggestions a scenario may rewrite."""

    id: str
    name: str
    topic: str
    complexity_tier: Tier
    subject: str = ""
    register: str = ""
    typical_entities_hint: tuple[str, ...] = ()
    typical_metrics_hint: tuple[dict[str, str], ...] = ()
    temporal_granularity_hint: str = "daily"

    @property
    def target_rows(self) -> tuple[int, int]:
        return TARGET_ROWS[self.complexity_tier]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "topic": self.topic,
                "subject": self.subject, "register": self.register,
                "complexity_tier": self.complexity_tier,
                "typical_entities_hint": list(self.typical_entities_hint),
                "typical_metrics_hint": [dict(m) for m in self.typical_metrics_hint],
                "temporal_granularity_hint": self.temporal_granularity_hint}

    @classmethod
    def from_dict(cls, raw: dict[str, Any], id: str | None = None) -> "Domain":
        return cls(id=id or raw["id"], name=str(raw["name"]), topic=str(raw.get("topic", "")),
                   complexity_tier=raw.get("complexity_tier", "medium"),
                   subject=str(raw.get("subject", "")), register=str(raw.get("register", "")),
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

    def of_register(self, register: str) -> tuple[Domain, ...]:
        return tuple(d for d in self.domains if d.register == register)

    def stats(self) -> dict[str, dict[str, int]]:
        """What the file records about its own shape, per the spec: version, time,
        the complexity spread and the coverage of both axes."""
        return {"tiers": {t: len(self.of_tier(t)) for t in TIERS},
                "subjects": _counts(d.subject for d in self.domains),
                "registers": _counts(d.register for d in self.domains),
                "cells": _counts(f"{d.subject} / {d.register}" for d in self.domains),
                "topics": _counts(d.topic for d in self.domains)}

    def merged(self, extra: "Pool") -> "Pool":
        """This pool plus another, keeping the ids already recorded on disk.

        A schema records the sub-topic it was drawn from by identifier, so renumbering
        an existing entry orphans every artifact that names it. The new entries are
        numbered after the highest already in use.
        """
        start = len(self.domains)
        added = tuple(replace(d, id=f"dom_{start + i + 1:04d}")
                      for i, d in enumerate(extra.domains))
        return Pool(self.domains + added,
                    tuple(dict.fromkeys(self.topics + extra.topics)))

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

#: The register, written into both prompts. Topics come back stripped of it, so the
#: sub-topic call has to be told again -- and told in facts rather than in an
#: adjective, because an adjective is what the answer paraphrases away.
REGISTER_BLOCK = """Register:  {what}
  who produces the data   {producer}
  who reads it            {audience}
  what the entities are   {entities}
  what the numbers are    {metrics}
  how often it is published  {grain}"""

#: Words a subject may not be named with unless it really is operations monitoring.
#: The same list is what `_operational_words` checks after the answer arrives.
DASHBOARD_WORDS = ("dashboard", "kpi", "scorecard", "monitoring", "tracking")

TOPIC_USER = """List {n} topics inside the subject "{subject}" that are published
in this register.

Subject:   {subject_what}
{register}

A subject is what the data is about, not a report template. Do not name a chart
type. Do not write "... dashboard", "... KPI", "... scorecard", "... monitoring" or
"... tracking" unless the register above is an organisation watching its own process.

Topics already under this subject (do not repeat them or offer near-synonyms):
{existing}

Reply with {{"topics": ["...", ...]}}."""

SUBTOPIC_USER = """Under the topic "{topic}", list {n} concrete data analysis
situations, all of them in this register.

{register}

For each one give:
  name                        the situation in a few words, e.g. "ICU bed turnover"
  complexity_tier             {tiers}
  typical_entities_hint       2-4 entity types, at least one of them from the
                              register's entity list above
  typical_metrics_hint        1-3 metrics, each with a unit
  temporal_granularity_hint   one of: {grain}
{signed}
Keep the three complexity tiers roughly balanced.
Reply with {{"sub_topics": [{{...}}, ...]}}."""

#: Added for the registers whose numbers routinely go negative. Without it every
#: register comes back as a ladder of counts, and a diverging scale, a zero line and
#: a waterfall have nothing to be drawn from.
SIGNED_LINE = ("  at least one metric whose values can be negative -- a change, a "
               "balance,\n                              a gap or a net flow\n")


def _subtopic_schema(register: Register) -> dict[str, Any]:
    """The sub-topic envelope, with this register's publication grain closed.

    Left as free text, a granularity outside daily / weekly / monthly reaches the
    declaration step and is refused there, which costs a retry of the whole scenario
    to fix one word.
    """
    schema = json.loads(json.dumps(SUBTOPIC_SCHEMA))
    item = schema["properties"]["sub_topics"]["items"]
    item["properties"]["temporal_granularity_hint"] = {
        "type": "string", "enum": list(register.grain)}
    return schema


def _cell_topics(llm: Any, subject: Subject, register: Register, n: int,
                 existing: Sequence[str]) -> list[str]:
    prompt = TOPIC_USER.format(
        n=n, subject=subject.name, subject_what=subject.what, existing=", ".join(existing) or "none",
        register=REGISTER_BLOCK.format(
            what=register.what, producer=register.producer, audience=register.audience,
            entities=register.entities, metrics=register.metrics,
            grain=", ".join(register.grain)))
    return [str(x) for x in llm.json(SYSTEM, prompt, schema=TOPIC_SCHEMA)["topics"][:n]]


def _cell_domains(llm: Any, topic: str, subject: Subject, register: Register,
                  n: int) -> list[dict[str, Any]]:
    tiers = "; ".join(f"{t} ({TIER_MEANING[t]})" for t in TIERS)
    prompt = SUBTOPIC_USER.format(
        topic=topic, n=n, tiers=tiers, grain=", ".join(register.grain),
        signed=SIGNED_LINE if register.signed else "",
        register=REGISTER_BLOCK.format(
            what=register.what, producer=register.producer, audience=register.audience,
            entities=register.entities, metrics=register.metrics,
            grain=", ".join(register.grain)))
    return list(llm.json(SYSTEM, prompt,
                         schema=_subtopic_schema(register))["sub_topics"][:n])


def operational_words(name: str) -> list[str]:
    """Dashboard vocabulary in a subject name. A subject is what the data is about."""
    lowered = name.lower()
    return [w for w in DASHBOARD_WORDS if w in lowered]


def build(llm: Any, *, topics_per_cell: int = 2, per_topic: int = 7,
          target: int = 600, existing_topics: Sequence[str] = (),
          is_duplicate: Callable[[str], bool] | None = None,
          report: Callable[[str], None] | None = None) -> Pool:
    """Walk the declared cells, ask two levels per cell, then level the tiers.

    `target` is a floor on the whole pool rather than a place to stop: stopping at a
    count leaves the cells after it with nothing in them, which is the bias the two
    axes exist to remove. Every cell is asked for; the count is what the cells add up
    to, and the backfill only tops up the thin tier afterwards.
    """
    seen = is_duplicate or (lambda _: False)
    say = report or (lambda _: None)
    known = list(existing_topics)
    domains: list[Domain] = []
    topics: list[str] = []

    for subject, register in cells():
        here = [x for x in known if x.startswith(f"{subject.name}: ")]
        for topic in _cell_topics(llm, subject, register, topics_per_cell, here):
            known.append(f"{subject.name}: {topic}")
            topics.append(topic)
            kept = 0
            for item in _cell_domains(llm, topic, subject, register, per_topic):
                name = str(item["name"])
                if seen(name) or operational_words(name) and register.name != "operational":
                    continue
                domains.append(Domain.from_dict(
                    {**item, "topic": topic, "subject": subject.name,
                     "register": register.name}, id=f"dom_{len(domains) + 1:04d}"))
                kept += 1
            say(f"{subject.name} / {register.name} / {topic}: {kept}")

    domains += _backfill(llm, domains, target, seen, say)
    return Pool(tuple(domains), tuple(topics))


def _backfill(llm: Any, domains: Sequence[Domain], target: int,
              seen: Callable[[str], bool], say: Callable[[str], None]) -> list[Domain]:
    """Top up the thinnest tier until the three are level and the floor is met.

    The tier is asked for by name, from the cells that produced the fewest of it, so
    the top-up widens the same two axes rather than deepening whichever cell happened
    to answer at length. A target of zero asks for no floor, and then there is
    nothing to top up.
    """
    if target <= 0:
        return []
    out: list[Domain] = []
    lookup = {(s.name, r.name): (s, r) for s, r in cells()}
    for _ in range(len(cells())):
        counts = _counts(d.complexity_tier for d in [*domains, *out])
        thin = min(TIERS, key=lambda t: counts.get(t, 0))
        level = max(counts.get(t, 0) for t in TIERS)
        if counts.get(thin, 0) >= level and len(domains) + len(out) >= target:
            break
        per_cell = _counts(f"{d.subject} / {d.register}" for d in [*domains, *out]
                           if d.complexity_tier == thin)
        key = min(lookup, key=lambda k: per_cell.get(f"{k[0]} / {k[1]}", 0))
        subject, register = lookup[key]
        topic = _cell_topics(llm, subject, register, 1, [])[0]
        for item in _cell_domains(llm, topic, subject, register, 4):
            name = str(item["name"])
            if seen(name) or str(item.get("complexity_tier")) != thin:
                continue
            out.append(Domain.from_dict(
                {**item, "topic": topic, "subject": subject.name, "register": register.name},
                id=f"dom_{len(domains) + len(out) + 1:04d}"))
        say(f"backfill {thin}: {subject.name} / {register.name} -> {len(out)}")
    return out
