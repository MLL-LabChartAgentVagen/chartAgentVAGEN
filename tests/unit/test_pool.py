"""The domain pool: two levels, deduplicated and balanced, then sampled per run.

The pool is built once for the project. Sampling runs every time, so what matters
is that one seed always yields the same sequence of sub-topics.
"""

import pytest

from chartgen.s01_data import pool as P


def domain(i: int, tier: str = "medium", topic: str = "Healthcare") -> P.Domain:
    return P.Domain(id=f"dom_{i:03d}", name=f"analysis situation {i}", topic=topic,
                    complexity_tier=tier, typical_entities_hint=("a", "b"),
                    typical_metrics_hint=({"name": "m", "unit": "u"},),
                    temporal_granularity_hint="daily")


@pytest.fixture
def pool() -> P.Pool:
    return P.Pool(tuple(domain(i, tier, topic)
                        for i, (tier, topic) in enumerate(
                            [("simple", "Retail"), ("medium", "Healthcare"),
                             ("complex", "Energy")] * 5)))


class TestPoolFile:
    def test_a_pool_round_trips_through_disk(self, pool, tmp_path):
        path = pool.save(tmp_path / "pool.json")
        assert P.Pool.load(path).domains == pool.domains

    def test_the_file_carries_the_tier_and_topic_statistics(self, pool, tmp_path):
        import json
        raw = json.loads(pool.save(tmp_path / "pool.json").read_text(encoding="utf-8"))
        assert raw["stats"]["tiers"] == {"simple": 5, "medium": 5, "complex": 5}
        assert raw["stats"]["topics"]["Retail"] == 5

    def test_each_tier_declares_its_target_row_count(self):
        assert P.TARGET_ROWS["simple"] == (200, 500)
        assert P.TARGET_ROWS["complex"] == (1000, 3000)


class TestTieredSamplingWithoutReplacement:
    def test_the_same_seed_gives_the_same_sequence(self, pool):
        """Two samplers, drawn from to the end, compared element by element. One
        first draw matching says nothing about the order that follows it."""
        first, second, other = P.Sampler(pool, 7), P.Sampler(pool, 7), P.Sampler(pool, 8)
        a = [first.take().id for _ in range(12)]
        b = [second.take().id for _ in range(12)]
        c = [other.take().id for _ in range(12)]
        assert a == b
        assert a != c


    def test_two_seeds_give_different_sequences(self, pool):
        assert ([P.Sampler(pool, 1).take().id for _ in range(3)]
                != [P.Sampler(pool, 2).take().id for _ in range(3)])

    def test_a_tier_hands_out_each_domain_once_before_resetting(self, pool):
        sampler = P.Sampler(pool, 3)
        taken = [sampler.take("simple").id for _ in range(4)]
        assert len(set(taken)) == 4

    def test_a_tier_resets_after_eighty_percent_is_gone(self, pool):
        sampler = P.Sampler(pool, 3)
        assert sampler.remaining("simple") == 5
        for _ in range(3):
            sampler.take("simple")
        assert sampler.remaining("simple") == 2
        sampler.take("simple")                              # four of five gone, so it resets
        assert sampler.remaining("simple") == 5

    def test_taking_without_a_tier_walks_the_three_tiers(self, pool):
        sampler = P.Sampler(pool, 5)
        assert [sampler.take().complexity_tier for _ in range(3)] == \
               ["simple", "medium", "complex"]

    def test_an_empty_tier_is_reported(self):
        sampler = P.Sampler(P.Pool((domain(0, "simple"),)), 1)
        with pytest.raises(KeyError, match="complex"):
            sampler.take("complex")


class TestTheTwoAxes:
    """Area is what the data is about; register is who published it and for whom.
    Asking only for areas is what produced the pool this replaced: seventeen areas
    spanning aviation, banking, farming and sport, every one of them written as an
    operations dashboard."""

    def test_every_subject_declares_registers_that_exist(self):
        for subject in P.SUBJECTS:
            assert subject.registers, subject.name
            for name in subject.registers:
                assert name in P.REGISTER, (subject.name, name)

    def test_every_register_is_used_by_some_subject(self):
        used = {r for s in P.SUBJECTS for r in s.registers}
        assert used == set(P.REGISTER)

    def test_a_cell_is_a_subject_and_one_of_its_own_registers(self):
        for subject, register in P.cells():
            assert register.name in subject.registers

    def test_the_registers_that_go_negative_say_so(self):
        """A diverging scale, a zero line and a waterfall need numbers that can fall
        below zero, and a register of counts never produces one."""
        signed = {r.name for r in P.REGISTERS if r.signed}
        assert signed == {"official_statistics", "research", "disclosure"}

    def test_every_register_publishes_at_a_grain_the_declaration_step_accepts(self):
        from chartgen.s01_data.declare import FREQS

        for register in P.REGISTERS:
            assert register.grain and set(register.grain) <= set(FREQS), register.name


class TestBuildingThePool:
    """Two levels per cell, plus dedup and a backfill. The model is faked; the rules
    are what is tested."""

    def one_cell(self, monkeypatch, register: str = "operational"):
        subject = P.Subject("test subject", "what it covers", (register,))
        monkeypatch.setattr(P, "SUBJECTS", (subject,))
        return subject

    def test_two_levels_produce_domains_with_ids(self, monkeypatch):
        self.one_cell(monkeypatch)
        llm = FakeLLM()
        built = P.build(llm, topics_per_cell=2, per_topic=2, target=0)
        assert len(built.domains) == 4
        assert [d.id for d in built.domains] == ["dom_0001", "dom_0002",
                                                 "dom_0003", "dom_0004"]
        assert llm.calls[0][0] == "topics" and llm.calls[1][0] == "sub_topics"

    def test_every_domain_carries_the_cell_it_came_from(self, monkeypatch):
        subject = self.one_cell(monkeypatch, "official_statistics")
        built = P.build(FakeLLM(), topics_per_cell=1, per_topic=3, target=0)
        assert {d.subject for d in built.domains} == {subject.name}
        assert {d.register for d in built.domains} == {"official_statistics"}

    def test_the_register_reaches_both_prompts(self, monkeypatch):
        self.one_cell(monkeypatch, "official_statistics")
        llm = FakeLLM()
        P.build(llm, topics_per_cell=1, per_topic=1, target=0)
        for _, prompt in llm.calls[:2]:
            assert "a statistical agency publishing comparable indicators" in prompt
            assert "age band" in prompt

    def test_a_register_whose_numbers_go_negative_asks_for_one(self, monkeypatch):
        self.one_cell(monkeypatch, "official_statistics")
        llm = FakeLLM()
        P.build(llm, topics_per_cell=1, per_topic=1, target=0)
        assert "can be negative" in llm.calls[1][1]

    def test_a_register_of_counts_does_not(self, monkeypatch):
        self.one_cell(monkeypatch, "operational")
        llm = FakeLLM()
        P.build(llm, topics_per_cell=1, per_topic=1, target=0)
        assert "can be negative" not in llm.calls[1][1]

    def test_the_publication_grain_is_closed_by_the_schema(self, monkeypatch):
        """Left as free text, a granularity the declaration step does not accept
        reaches it and costs a retry of the whole scenario to fix one word."""
        self.one_cell(monkeypatch, "registry")
        llm = FakeLLM()
        P.build(llm, topics_per_cell=1, per_topic=1, target=0)
        closed = llm.schemas[1]["properties"]["sub_topics"]["items"]
        assert closed["properties"]["temporal_granularity_hint"]["enum"] == \
            list(P.REGISTER["registry"].grain)

    def test_dashboard_words_are_refused_outside_the_operational_register(self):
        assert P.operational_words("Quarterly hiring dashboard") == ["dashboard"]
        assert P.operational_words("Quarterly hiring by sector") == []

    def test_a_subject_named_like_a_dashboard_is_dropped(self, monkeypatch):
        self.one_cell(monkeypatch, "survey")
        built = P.build(FakeLLM(dashboard_names=True), topics_per_cell=1, per_topic=4,
                        target=0)
        assert built.domains == ()

    def test_near_duplicate_names_are_dropped(self, monkeypatch):
        self.one_cell(monkeypatch)
        llm = FakeLLM(duplicate_names=True)
        built = P.build(llm, topics_per_cell=1, per_topic=4, target=0,
                        is_duplicate=lambda text: text.endswith("2"))
        assert all(not d.name.endswith("2") for d in built.domains)

    def test_the_existing_topics_are_passed_in_to_avoid_overlap(self, monkeypatch):
        subject = self.one_cell(monkeypatch)
        llm = FakeLLM()
        P.build(llm, topics_per_cell=1, per_topic=1, target=0,
                existing_topics=(f"{subject.name}: Retail",))
        assert "Retail" in llm.calls[0][1]

    def test_every_cell_is_asked_for(self, monkeypatch):
        """A count is a floor, not a place to stop. Stopping at one leaves the cells
        after it empty, which is the bias the two axes exist to remove."""
        monkeypatch.setattr(P, "SUBJECTS", (
            P.Subject("a", "one", ("operational",)), P.Subject("b", "two", ("survey",))))
        llm = FakeLLM()
        P.build(llm, topics_per_cell=1, per_topic=4, target=0)
        assert sum(1 for kind, _ in llm.calls if kind == "topics") == 2

    def test_no_floor_asks_for_no_backfill(self, monkeypatch):
        self.one_cell(monkeypatch)
        llm = FakeLLM()
        P.build(llm, topics_per_cell=1, per_topic=4, target=0)
        assert sum(1 for kind, _ in llm.calls if kind == "topics") == 1

    def test_the_backfill_adds_to_the_tier_that_came_out_thin(self, monkeypatch):
        """It asks for the tier by name, from the cell that produced the fewest of
        it, so the top-up widens the same two axes rather than deepening whichever
        cell happened to answer at length."""
        monkeypatch.setattr(P, "SUBJECTS", (
            P.Subject("a", "one", ("operational",)), P.Subject("b", "two", ("survey",))))
        base = P.build(FakeLLM(), topics_per_cell=1, per_topic=4, target=0)
        topped = P.build(FakeLLM(), topics_per_cell=1, per_topic=4, target=99)
        assert len(topped.domains) > len(base.domains)
        counts = {t: sum(1 for d in topped.domains if d.complexity_tier == t)
                  for t in P.TIERS}
        assert min(counts.values()) > 0, counts
        thin = min(P.TIERS, key=lambda t: sum(
            1 for d in base.domains if d.complexity_tier == t))
        assert counts[thin] > sum(1 for d in base.domains if d.complexity_tier == thin)

    def test_both_schemas_are_shaped_the_way_structured_output_demands(self):
        """A fake model accepts any schema; the service does not."""
        from llmkit.providers import check_strict

        check_strict(P.TOPIC_SCHEMA)
        check_strict(P.SUBTOPIC_SCHEMA)


class FakeLLM:
    """Answers exactly two questions: give me topics, give me sub-topics of one."""

    def __init__(self, duplicate_names: bool = False, dashboard_names: bool = False,
                 one_tier: str | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self.schemas: list[dict] = []
        self.duplicate_names = duplicate_names
        self.dashboard_names = dashboard_names
        self.one_tier = one_tier
        self.n = 0

    def json(self, system: str, user: str, *, schema: dict) -> dict:
        self.schemas.append(schema)
        if "topics" in schema.get("properties", {}):
            self.calls.append(("topics", user))
            return {"topics": [f"Topic {i}" for i in range(1, 9)]}
        self.calls.append(("sub_topics", user))
        tiers = ("simple", "medium", "complex")
        grain = schema["properties"]["sub_topics"]["items"]["properties"][
            "temporal_granularity_hint"].get("enum", ["daily"])[0]
        items = []
        for i in range(1, 9):
            self.n += 1
            name = f"situation {i if self.duplicate_names else self.n}"
            items.append({"name": f"{name} dashboard" if self.dashboard_names else name,
                          "complexity_tier": self.one_tier or tiers[self.n % 3],
                          "typical_entities_hint": ["x", "y"],
                          "typical_metrics_hint": [{"name": "m", "unit": "u"}],
                          "temporal_granularity_hint": grain})
        return {"sub_topics": items}
