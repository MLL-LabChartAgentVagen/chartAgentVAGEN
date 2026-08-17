"""One real model call. Whether the prompt works is only knowable by running it.

Skipped by default. Set CHARTGEN_LLM=1 to send the request.
"""

import os

import pytest

from chartgen.config import Config
from chartgen.s01_data.author import Rejected, build_scenario, failure_counts

pytestmark = pytest.mark.skipif(os.environ.get("CHARTGEN_LLM") != "1",
                                reason="sends a real request; set CHARTGEN_LLM=1 to run")

DOMAIN = {"name": "Retail store inventory turnover", "topic": "Retail",
          "complexity_tier": "medium",
          "typical_entities_hint": ["store", "product category"],
          "typical_metrics_hint": [{"name": "units_sold", "unit": "units"}],
          "temporal_granularity_hint": "weekly"}


@pytest.mark.llm
def test_one_call_produces_a_table_a_schema_and_bound_intents():
    log: list[Rejected] = []
    table, schema = build_scenario("live", 20260816, Config.load(), domain=DOMAIN, log=log)

    assert 500 <= table.n_rows <= 1000
    assert len(schema.groups) >= 2 and len(schema.measures) >= 2
    assert 2 <= len(schema.intents) <= 4
    for intent in schema.intents:
        assert all(schema.has(c) for c in intent.columns)
    print(f"\nretries {failure_counts(log)}  columns {[c.name for c in schema.columns]}")
