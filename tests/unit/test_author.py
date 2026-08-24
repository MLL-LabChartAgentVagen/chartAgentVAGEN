"""The single model call: what it must produce, and what happens when it does not.

`compose` is the rules half of that call. It knows nothing about models, so the
whole data stage can be exercised from a hand-written answer with no network.
"""

import json
import re
from pathlib import Path

import pytest

from chartgen.config import Config
from chartgen.s01_data import author as A

SAMPLE = json.loads(Path("tests/samples/er_scenario.json").read_text(encoding="utf-8"))
SEED = 20260816
CONFIG = Config.load()


def payload(**over) -> dict:
    return {**json.loads(json.dumps(SAMPLE)), **over}


class TestTheSampleIsTheOneInThePrompt:
    def test_the_worked_example_and_the_test_sample_are_one_file(self):
        assert A.EXAMPLE_OUTPUT == SAMPLE, "run python tools/make_samples.py"

    def test_the_prompt_names_no_chart_type(self):
        """Scenarios come from subject matter, not from a catalogue of charts."""
        text = A.SYSTEM + A.user_prompt(A.EXAMPLE_DOMAIN, (500, 1000))
        for name in ("bar", "pie", "line", "scatter", "histogram", "heatmap",
                     "box", "funnel", "waterfall", "area", "compound"):
            assert not re.search(rf"\b{name}\b", text, re.I), name

    def test_the_prompt_asks_for_english_content(self):
        assert "in English" in A.user_prompt(A.EXAMPLE_DOMAIN, (500, 1000))

    def test_the_prompt_holds_no_chinese(self):
        import re
        text = A.SYSTEM + A.user_prompt(A.EXAMPLE_DOMAIN, (500, 1000), feedback="why")
        assert not re.search(r"[\u4e00-\u9fff]", text)

    def test_the_output_contract_is_shaped_the_way_structured_output_demands(self):
        """A fake model accepts any schema; the service does not."""
        from llmkit.providers import check_strict

        check_strict(A.SCENARIO_SCHEMA)

    def test_a_retry_carries_the_reason(self):
        text = A.user_prompt(A.EXAMPLE_DOMAIN, (500, 1000),
                            feedback="`cost` and `revenue` reference each other")
        assert "`cost` and `revenue`" in text


class TestComposeIsAllRules:
    def test_the_worked_example_composes_end_to_end(self):
        table, schema = A.compose(payload(), scenario_id="er_wait", seed=SEED, config=CONFIG)
        assert table.n_rows == 900 and schema.n_rows == 900
        assert schema.scenario_title.startswith("Emergency department")
        assert [i.family for i in schema.intents] == ["comparison", "trend", "relation"]
        assert schema.dependencies == (("wait_minutes", "cost"),
                                       ("wait_minutes", "satisfaction"))

    def test_the_schema_describes_the_data_that_was_actually_generated(self):
        table, schema = A.compose(payload(), scenario_id="er_wait", seed=SEED, config=CONFIG)
        for column in schema.categories:
            assert set(table.df[column.name].unique()) == set(column.values), column.name

    def test_a_broken_script_is_rejected_as_a_parse_failure(self):
        with pytest.raises(A.Rejected) as exc:
            A.compose(payload(script='dim("x", ["A"])\nemit(10)'),
                      scenario_id="s", seed=SEED, config=CONFIG)
        assert exc.value.kind == "script" and "values" in str(exc.value)

    def test_an_intent_bound_to_a_missing_column_is_a_binding_failure(self):
        bad = payload()
        bad["intents"][1]["columns"] = ["visit_hour", "wait_minutes"]
        with pytest.raises(A.Rejected) as exc:
            A.compose(bad, scenario_id="s", seed=SEED, config=CONFIG)
        assert exc.value.kind == "binding" and "visit_hour" in str(exc.value)

    def test_the_intent_count_is_part_of_the_contract(self):
        with pytest.raises(A.Rejected) as exc:
            A.compose(payload(intents=[SAMPLE["intents"][0]]), scenario_id="s",
                      seed=SEED, config=CONFIG)
        assert exc.value.kind == "binding"

    def test_a_schema_that_covers_too_few_families_is_a_coverage_failure(self):
        script = ('dim("a", ["p", "q"], group="g")\ndim("b", ["u", "v"], group="h")\n'
                  'measure("m", "gaussian(50, 8)", unit="ratio", additive=False)\n'
                  'measure("n", "m * 2", unit="ratio", additive=False)\nemit(300)')
        thin = payload(script=script, intents=[
            {"sentence": "s", "columns": ["m", "n"], "aggregate": "NONE", "family": "relation"},
            {"sentence": "t", "columns": ["a", "m"], "aggregate": "AVG", "family": "comparison"}])
        with pytest.raises(A.Rejected) as exc:
            A.compose(thin, scenario_id="s", seed=SEED, config=CONFIG)
        assert exc.value.kind == "feasibility" and "families" in str(exc.value)

    def test_a_constant_measure_is_a_structure_failure(self):
        script = SAMPLE["script"].replace(
            '"clip(5.2 - wait_minutes / 32 + gaussian(0, 0.3), 1, 5)"', '"4.0"')
        with pytest.raises(A.Rejected) as exc:
            A.compose(payload(script=script), scenario_id="s", seed=SEED, config=CONFIG)
        assert exc.value.kind == "structure" and "satisfaction" in str(exc.value)


class TestTheRetryLoop:
    def test_a_clean_first_answer_costs_one_call(self):
        llm = FakeLLM([payload()])
        table, schema = A.build_scenario("er_wait", SEED, CONFIG, llm=llm,
                                         domain=A.EXAMPLE_DOMAIN)
        assert llm.n == 1 and table.n_rows == 900

    def test_a_rejected_answer_is_fed_back_with_its_reason(self):
        llm = FakeLLM([payload(script='dim("x", ["A"])\nemit(10)'), payload()])
        log: list[A.Rejected] = []
        A.build_scenario("er_wait", SEED, CONFIG, llm=llm, domain=A.EXAMPLE_DOMAIN, log=log)
        assert llm.n == 2
        assert [r.kind for r in log] == ["script"]
        assert "values" in llm.prompts[1]

    def test_giving_up_after_the_retry_limit(self):
        broken = payload(script='dim("x", ["A"])\nemit(10)')
        llm = FakeLLM([broken] * 9)
        with pytest.raises(A.Rejected):
            A.build_scenario("s", SEED, CONFIG.set("llm.max_retries", 2), llm=llm,
                             domain=A.EXAMPLE_DOMAIN)
        assert llm.n == 3                       # the first attempt plus two retries

    def test_a_duplicate_scenario_draws_another_domain(self):
        llm = FakeLLM([payload(), payload()])
        seen = {SAMPLE["scenario_title"]}
        sampler = FakeSampler()
        A.build_scenario("s", SEED, CONFIG, llm=llm, sampler=sampler,
                         is_duplicate=lambda text: text in seen and not seen.discard(text))
        assert sampler.taken == 2               # the first scenario collided, so it drew again

    def test_each_scenario_draws_its_own_sub_topic(self, tmp_path):
        """One sampler per scenario would otherwise start every scenario from the
        same draw, and a batch would be one sub-topic repeated."""
        from chartgen.s01_data import pool as P

        domains = tuple(P.Domain(f"dom_{i:03d}", f"situation {i}", "T", tier)
                        for tier in P.TIERS for i in range(8))
        path = P.Pool(domains, ("T",)).save(tmp_path / "pool.json")
        config = Config.load().set("data.pool_path", str(path))

        drawn = []
        for scenario in ("s000", "s001", "s002"):
            llm = FakeLLM([payload()])
            A.build_scenario(scenario, SEED, config, llm=llm)
            drawn.append(re.search(r'"name": "(situation \d+)"', llm.prompts[0])[1])
        assert len(set(drawn)) == 3, drawn

    def test_the_scenario_id_reaches_the_schema(self):
        _, schema = A.build_scenario("run7_s3", SEED, CONFIG, llm=FakeLLM([payload()]),
                                     domain=A.EXAMPLE_DOMAIN)
        assert schema.scenario_id == "run7_s3"


class FakeLLM:
    def __init__(self, answers: list[dict]) -> None:
        self.answers, self.n, self.prompts = answers, 0, []

    def json(self, system: str, user: str, *, schema: dict) -> dict:
        self.prompts.append(user)
        self.n += 1
        return self.answers[self.n - 1]


class FakeSampler:
    def __init__(self) -> None:
        self.taken = 0

    def take(self, tier=None) -> dict:
        self.taken += 1
        return {**A.EXAMPLE_DOMAIN, "name": f"domain {self.taken}"}


class TestOneDrawForTheWholeRun:
    """A sampler draws without replacement, which says nothing if every scenario gets
    a fresh one: each starts with the full pool and they collide. And a collision is
    not a near miss -- the data prompt carries no scenario identifier, so the second
    scenario is a cache hit and comes back byte for byte the same."""

    def pipeline(self, tmp_path):
        """Its own pool and its own memory file. Pointed at the project's, a test run
        would draw from whatever the pool happens to hold and write into what real
        runs remember."""
        from chartgen.config import Config
        from chartgen.pipeline import Pipeline
        from chartgen.s01_data.pool import Domain, Pool, TIERS

        pool = Pool(tuple(Domain(id=f"dom_{i:04d}", name=f"situation {i}",
                                 topic="t", subject="health and care", register="operational",
                                 complexity_tier=TIERS[i % 3]) for i in range(30)))
        path = pool.save(tmp_path / "pool.json")
        config = Config.load().override(
            [f"data.scenario_memory={tmp_path / 'seen.json'}",
             f"data.pool_path={path}"])
        return Pipeline(config, tmp_path / "run")

    def test_every_scenario_of_a_run_draws_from_one_sampler(self, tmp_path):
        from chartgen.s01_data.author import _next_domain

        pipe = self.pipeline(tmp_path)
        sampler, _ = pipe._drawing()
        assert pipe._drawing()[0] is sampler, "built once, not once per scenario"
        # Ten sub-topics in the tier, and a tier resets once four fifths of it is
        # gone -- so eight draws is what "without replacement" covers here.
        drawn = [_next_domain(sampler, "simple")["id"] for _ in range(8)]
        assert len(set(drawn)) == len(drawn), drawn

    def test_the_duplicate_judge_remembers_across_scenarios(self, tmp_path):
        pipe = self.pipeline(tmp_path)
        _, is_duplicate = pipe._drawing()
        assert not is_duplicate("Weekly claim turnaround by processing centre")
        assert is_duplicate("Weekly claim turnaround by processing centre")

    def test_a_hand_written_domain_bypasses_the_pool(self, tmp_path):
        """`chartgen data --domain` names its own subject, so nothing is drawn and
        the pool file need not exist."""
        pipe = self.pipeline(tmp_path)
        assert pipe._sampler is None
