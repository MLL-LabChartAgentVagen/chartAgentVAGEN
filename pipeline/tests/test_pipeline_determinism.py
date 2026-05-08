"""End-to-end determinism smoke for the AGPDS pipeline surface.

Full `run_single` reproducibility requires LLM mocking (Loop A is non-deterministic
by nature). This smoke instead exercises the deterministic spine: same
`(seed, scenario_id)` → same `generation_id`, on both `core.ids.generation_id`
directly and on the `AGPDSPipeline._new_generation_id` wrapper.
"""

import json
import os
import tempfile

import pytest

from pipeline.core.ids import generation_id


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
