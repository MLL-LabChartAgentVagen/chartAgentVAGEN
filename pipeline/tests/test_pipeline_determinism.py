"""End-to-end determinism smoke for the AGPDS pipeline surface.

Full `run_single` reproducibility requires LLM mocking (Loop A is non-deterministic
by nature). This smoke exercises the deterministic spine: same
`(seed, scenario_id)` → same `generation_id`, on both `core.ids.generation_id`
directly and on the `AGPDSPipeline._new_generation_id` wrapper.

The B.8 follow-up adds tests for the new `run_single(scenario_id=...)` API:
format round-trip, malformed input rejection, live-mode rejection, and
end-to-end deterministic generation_id under monkeypatched Loop A.
"""

import json
import os
import tempfile

import pandas as pd
import pytest

from pipeline.core.ids import generation_id, parse_scenario_id, format_scenario_id


_MINI_POOL = {
    "version": "1.0",
    "total_domains": 3,
    "domains": [
        {"id": "dom_001", "name": "demo", "topic": "T",
         "complexity_tier": "simple"},
        {"id": "dom_002", "name": "demo2", "topic": "T",
         "complexity_tier": "medium"},
        {"id": "dom_003", "name": "demo3", "topic": "T",
         "complexity_tier": "complex"},
    ],
}


@pytest.fixture
def pool_path():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w") as f:
        json.dump(_MINI_POOL, f)
    yield path
    os.unlink(path)


def test_generation_id_is_pure_function_of_seed_and_scenario_id():
    """Same inputs → same id, different inputs → different id."""
    a1 = generation_id(seed=42, scenario_id="dom_001/k=0")
    a2 = generation_id(seed=42, scenario_id="dom_001/k=0")
    assert a1 == a2

    b = generation_id(seed=42, scenario_id="dom_001/k=1")
    assert a1 != b, "scenario_id should affect id"

    c = generation_id(seed=43, scenario_id="dom_001/k=0")
    assert a1 != c, "seed should affect id"


def test_generation_id_format():
    """id is `<prefix>_<10 hex chars>` (default prefix 'agpds')."""
    gid = generation_id(seed=42, scenario_id="dom_001/k=0")
    prefix, _, hex_part = gid.partition("_")
    assert prefix == "agpds"
    assert len(hex_part) == 10
    int(hex_part, 16)  # raises if not valid hex


def test_pipeline_new_generation_id_matches_core_ids(pool_path):
    """AGPDSPipeline._new_generation_id is a thin wrapper over core.ids.generation_id."""
    from pipeline.agpds_pipeline import AGPDSPipeline

    pipeline = AGPDSPipeline(
        llm_client=object(),  # never called in this test
        pool_path=pool_path,
        scenario_source="live",
        seed=42,
    )
    scenario_id = "dom_001/k=0"
    assert pipeline._new_generation_id(scenario_id) == generation_id(42, scenario_id)


def test_pipeline_two_instances_same_seed_same_id(pool_path):
    """Two AGPDSPipeline instances built with the same seed yield the same id."""
    from pipeline.agpds_pipeline import AGPDSPipeline

    a = AGPDSPipeline(llm_client=object(), pool_path=pool_path, seed=42)
    b = AGPDSPipeline(llm_client=object(), pool_path=pool_path, seed=42)
    assert a._new_generation_id("dom_001/k=0") == b._new_generation_id("dom_001/k=0")


# ============================================================================
# B.8 follow-up: scenario_id surface tests
# ============================================================================


_MINI_SCENARIO_POOL = [
    {"domain_id": "dom_001", "k": 1, "category_id": 1, "generated_at": "x",
     "scenario": {"scenario_title": "ScenarioA", "data_context": "ctx",
                  "temporal_granularity": "daily", "key_entities": ["e1"],
                  "key_metrics": [{"name": "m", "unit": "u", "range": [0, 1]}],
                  "target_rows": 250}},
    {"domain_id": "dom_002", "k": 1, "category_id": 1, "generated_at": "x",
     "scenario": {"scenario_title": "ScenarioB", "data_context": "ctx2",
                  "temporal_granularity": "daily", "key_entities": ["e2"],
                  "key_metrics": [{"name": "m", "unit": "u", "range": [0, 1]}],
                  "target_rows": 250}},
]


@pytest.fixture
def scenario_pool_path():
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        for rec in _MINI_SCENARIO_POOL:
            f.write(json.dumps(rec) + "\n")
    yield path
    os.unlink(path)


def test_scenario_id_round_trip():
    """format then parse is the identity; k stays 1-based per convention U1."""
    assert format_scenario_id("dom_001", 1) == "dom_001/k=1"
    assert format_scenario_id("dom_017", 3) == "dom_017/k=3"
    assert parse_scenario_id("dom_001/k=1") == ("dom_001", 1)
    assert parse_scenario_id(format_scenario_id("dom_007", 5)) == ("dom_007", 5)


def test_parse_scenario_id_rejects_malformed():
    """parse_scenario_id raises ValueError on anything that isn't `dom_NNN/k=N`."""
    with pytest.raises(ValueError, match="Malformed"):
        parse_scenario_id("dom_001")  # no separator
    with pytest.raises(ValueError, match="Malformed"):
        parse_scenario_id("dom_001/x=1")  # wrong key
    with pytest.raises(ValueError, match="Malformed"):
        parse_scenario_id("dom_001/k=abc")  # non-int k


def test_live_mode_rejects_scenario_id(pool_path):
    """U3: live + scenario_id raises ValueError (cached lookup impossible)."""
    from pipeline.agpds_pipeline import AGPDSPipeline

    pipe = AGPDSPipeline(
        llm_client=object(),
        pool_path=pool_path,
        scenario_source="live",
        seed=42,
    )
    with pytest.raises(ValueError, match="scenario_source"):
        pipe.generate_artifacts(scenario_id="dom_001/k=1")


def test_run_single_scenario_id_deterministic_gen_id(
    monkeypatch, pool_path, scenario_pool_path,
):
    """Two run_single(scenario_id=...) calls with same seed produce same generation_id.

    Loop A and Loop B are stubbed so no LLM is needed; this isolates the
    deterministic spine that B.8+9 are responsible for.
    """
    from pipeline.agpds_pipeline import AGPDSPipeline
    import pipeline.agpds_pipeline as agpds_mod
    from pipeline.phase_2.types import ValidationReport

    def fake_run_loop_a(**kwargs):
        return (
            pd.DataFrame({"x": [1, 2]}),
            {"meta": "stub"},
            {"columns": [], "groups": [], "group_dependencies": [],
             "measure_dag": [], "target_rows": 2, "patterns": [],
             "seed": kwargs.get("seed", 42), "orthogonal_pairs": []},
            "stub source",
        )

    def fake_run_loop_b(raw_declarations, **kwargs):
        # ValidationReport with no checks is vacuously all_passed
        return (
            pd.DataFrame({"x": [1, 2]}),
            {"meta": "stub"},
            ValidationReport(checks=[]),
        )

    monkeypatch.setattr(agpds_mod, "run_loop_a", fake_run_loop_a)
    monkeypatch.setattr(agpds_mod, "run_loop_b_from_declarations", fake_run_loop_b)

    class _StubLLM:
        api_key = "stub"
        model = "stub-model"
        provider = "stub-provider"

    def make_pipeline(seed=42):
        return AGPDSPipeline(
            llm_client=_StubLLM(),
            pool_path=pool_path,
            scenario_source="cached_strict",
            scenario_pool_path=scenario_pool_path,
            seed=seed,
        )

    a = make_pipeline().run_single(scenario_id="dom_001/k=1")
    b = make_pipeline().run_single(scenario_id="dom_001/k=1")
    assert a["generation_id"] == b["generation_id"]
    assert a["scenario_id"] == "dom_001/k=1"
    assert a["category_id"] is None  # scenario_id-mode does not carry category_id

    # Different seed should yield different generation_id even for same scenario_id
    c = make_pipeline(seed=43).run_single(scenario_id="dom_001/k=1")
    assert a["generation_id"] != c["generation_id"]


def test_generate_artifacts_scenario_field_is_json_serializable(
    monkeypatch, pool_path, scenario_pool_path,
):
    """Sprint C.3 made `scenario` a ScenarioContext internally; the result
    dict returned by generate_artifacts must still be plain JSON so that
    agpds_generate._save_stage1_artifacts and agpds_runner._save_run_result
    can `json.dump(result["scenario"], ...)` without a custom encoder.

    Regression for the production crash:
        TypeError: Object of type ScenarioContext is not JSON serializable
    """
    from pipeline.agpds_pipeline import AGPDSPipeline
    import pipeline.agpds_pipeline as agpds_mod

    def fake_run_loop_a(**kwargs):
        return (
            pd.DataFrame({"x": [1, 2]}),
            {"meta": "stub"},
            {"columns": [], "groups": [], "group_dependencies": [],
             "measure_dag": [], "target_rows": 2, "patterns": [],
             "seed": kwargs.get("seed", 42), "orthogonal_pairs": []},
            "stub source",
        )

    monkeypatch.setattr(agpds_mod, "run_loop_a", fake_run_loop_a)

    class _StubLLM:
        api_key = "stub"
        model = "stub-model"
        provider = "stub-provider"

    pipe = AGPDSPipeline(
        llm_client=_StubLLM(),
        pool_path=pool_path,
        scenario_source="cached_strict",
        scenario_pool_path=scenario_pool_path,
        seed=42,
    )
    stage1 = pipe.generate_artifacts(scenario_id="dom_001/k=1")

    # Exact crash site from production:
    #   File "agpds_generate.py", line 67
    #   json.dump(stage1["scenario"], f, ...)
    serialized = json.dumps(stage1["scenario"])
    round_tripped = json.loads(serialized)
    assert round_tripped["scenario_title"] == "ScenarioA"
    assert round_tripped["target_rows"] == 250
    assert round_tripped["key_metrics"][0]["range"] == [0, 1]

    # Whole stage1 must also dump (manifest entry path in agpds_generate)
    json.dumps(stage1)
