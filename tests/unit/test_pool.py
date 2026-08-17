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
        a = [P.Sampler(pool, 7).take().id for _ in range(5)]
        sampler = P.Sampler(pool, 7)
        b = [sampler.take().id for _ in range(5)]
        assert a[0] == b[0]
        assert [P.Sampler(pool, 7).take().id] * 5 == a[:1] * 5

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


class TestBuildingThePool:
    """Two levels plus dedup. The model is faked; the rules are what is tested."""

    def test_two_levels_produce_domains_with_ids(self):
        llm = FakeLLM()
        built = P.build(llm, n_topics=2, per_topic=2, target=4)
        assert len(built.domains) == 4
        assert [d.id for d in built.domains] == ["dom_001", "dom_002", "dom_003", "dom_004"]
        assert llm.calls[0][0] == "topics" and llm.calls[1][0] == "sub_topics"

    def test_near_duplicate_names_are_dropped(self):
        llm = FakeLLM(duplicate_names=True)
        built = P.build(llm, n_topics=1, per_topic=4, target=1,
                        is_duplicate=lambda text: text.endswith("2"))
        assert all(not d.name.endswith("2") for d in built.domains)

    def test_the_existing_topics_are_passed_in_to_avoid_overlap(self):
        llm = FakeLLM()
        P.build(llm, n_topics=1, per_topic=1, target=1, existing_topics=("Retail",))
        assert "Retail" in llm.calls[0][1]

    def test_building_stops_when_the_target_is_reached(self):
        llm = FakeLLM()
        P.build(llm, n_topics=8, per_topic=4, target=4)
        assert sum(1 for kind, _ in llm.calls if kind == "sub_topics") <= 2

    def test_both_schemas_are_shaped_the_way_structured_output_demands(self):
        """A fake model accepts any schema; the service does not."""
        from llmkit.providers import check_strict

        check_strict(P.TOPIC_SCHEMA)
        check_strict(P.SUBTOPIC_SCHEMA)


class FakeLLM:
    """Answers exactly two questions: give me topics, give me sub-topics of one."""

    def __init__(self, duplicate_names: bool = False) -> None:
        self.calls: list[tuple[str, str]] = []
        self.duplicate_names = duplicate_names
        self.n = 0

    def json(self, system: str, user: str, *, schema: dict) -> dict:
        if "topics" in schema.get("properties", {}):
            self.calls.append(("topics", user))
            return {"topics": [f"Topic {i}" for i in range(1, 9)]}
        self.calls.append(("sub_topics", user))
        tiers = ("simple", "medium", "complex")
        items = []
        for i in range(1, 9):
            self.n += 1
            items.append({"name": f"situation {self.n if not self.duplicate_names else i}",
                          "complexity_tier": tiers[self.n % 3],
                          "typical_entities_hint": ["x", "y"],
                          "typical_metrics_hint": [{"name": "m", "unit": "u"}],
                          "temporal_granularity_hint": "daily"})
        return {"sub_topics": items}
