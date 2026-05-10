"""Tests for the AGPDSPipeline scenario cache loader and policy.

Covers:
  - Cache file is parsed into {domain_id: [scenario, ...]}
  - Cache hit returns a dict shape-compatible with validate_output
  - Cache miss in "cached" mode falls back to live generation
  - Cache miss in "cached_strict" mode raises KeyError
  - Cache file not found raises FileNotFoundError
  - Invalid scenario_source raises ValueError
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.agpds_pipeline import AGPDSPipeline  # noqa: E402
from pipeline.phase_1 import ScenarioContext, ScenarioContextualizer  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "scenario_pool_mini.jsonl"
DOMAIN_POOL = PROJECT_ROOT / "pipeline" / "phase_0" / "domain_pool.json"


def _make_pipeline(scenario_source: str, cache_path=None, llm=None):
    """Construct an AGPDSPipeline without touching real LLM/network paths."""
    llm = llm or MagicMock(api_key="fake", model="fake-model", provider="openai")
    return AGPDSPipeline(
        llm_client=llm,
        pool_path=str(DOMAIN_POOL),
        scenario_source=scenario_source,
        scenario_pool_path=str(cache_path or FIXTURE),
    )


class TestScenarioCache(unittest.TestCase):

    def test_cache_parsed_correctly(self):
        pipe = _make_pipeline("cached")
        cache = pipe._scenario_cache
        self.assertIsNotNone(cache)
        self.assertEqual(len(cache), 3)  # 3 unique domain_ids
        self.assertEqual(len(cache["dom_001"]), 2)  # K=2 for dom_001
        self.assertEqual(len(cache["dom_015"]), 1)
        self.assertEqual(len(cache["dom_042"]), 1)

    def test_cache_hit_shape(self):
        pipe = _make_pipeline("cached")
        scenario = pipe._get_scenario({"id": "dom_015"})
        # _get_scenario now returns a typed ScenarioContext (Sprint C.3)
        self.assertIsInstance(scenario, ScenarioContext)
        # dom_015 fixture has target_rows=200 → tier "simple" matches (200-500)
        ok, errors = ScenarioContextualizer.validate_output(
            scenario.to_dict(), "simple",
        )
        self.assertTrue(ok, f"validate_output errors: {errors}")

    def test_cache_hit_returns_one_of_bucket(self):
        pipe = _make_pipeline("cached")
        # dom_001 has 2 scenarios; repeated calls should always return one of them
        titles = {pipe._get_scenario({"id": "dom_001"}).scenario_title
                  for _ in range(20)}
        self.assertTrue(titles.issubset({
            "2024 H1 Shanghai Metro Ridership Log",
            "2023 Beijing Subway Peak Hour Analysis",
        }))

    def test_cache_miss_falls_back_in_cached_mode(self):
        pipe = _make_pipeline("cached")
        fake_scenario = {"scenario_title": "live-fallback"}
        with patch.object(pipe.contextualizer, "generate",
                          return_value=fake_scenario) as mock_gen:
            result = pipe._get_scenario({"id": "dom_999"})
        mock_gen.assert_called_once()
        self.assertEqual(result, fake_scenario)

    def test_cache_miss_raises_in_strict_mode(self):
        pipe = _make_pipeline("cached_strict")
        with self.assertRaises(KeyError):
            pipe._get_scenario({"id": "dom_999"})

    def test_live_mode_ignores_cache(self):
        pipe = _make_pipeline("live")
        self.assertIsNone(pipe._scenario_cache)
        fake_scenario = {"scenario_title": "live-only"}
        with patch.object(pipe.contextualizer, "generate",
                          return_value=fake_scenario) as mock_gen:
            result = pipe._get_scenario({"id": "dom_001"})
        mock_gen.assert_called_once()
        self.assertEqual(result, fake_scenario)

    def test_missing_cache_file_raises(self):
        llm = MagicMock(api_key="fake", model="fake-model", provider="openai")
        with self.assertRaises(FileNotFoundError):
            AGPDSPipeline(
                llm_client=llm,
                pool_path=str(DOMAIN_POOL),
                scenario_source="cached",
                scenario_pool_path="/tmp/does-not-exist.jsonl",
            )

    def test_invalid_scenario_source_raises(self):
        llm = MagicMock(api_key="fake", model="fake-model", provider="openai")
        with self.assertRaises(ValueError):
            AGPDSPipeline(
                llm_client=llm,
                pool_path=str(DOMAIN_POOL),
                scenario_source="not-a-mode",
            )


if __name__ == "__main__":
    unittest.main()
