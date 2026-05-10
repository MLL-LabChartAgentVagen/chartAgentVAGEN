"""Tests for Phase 1 typed schemas (Sprint C.3).

Covers:
  - Metric.from_dict / to_dict round-trip; range validation (numeric, low<high)
  - ScenarioContext.from_dict tolerance for unknown keys (grandfather D2)
  - ScenarioRecord JSONL round-trip; scenario_id property
  - ScenarioContext.from_dict rejects missing required fields
"""
import json
from pathlib import Path

import pytest

from pipeline.phase_1.types import Metric, ScenarioContext, ScenarioRecord


VALID_SCENARIO_DICT = {
    "scenario_title": "Demo title",
    "data_context": "Demo context",
    "temporal_granularity": "daily",
    "key_entities": ["e1", "e2", "e3"],
    "key_metrics": [
        {"name": "m1", "unit": "u", "range": [0, 1]},
        {"name": "m2", "unit": "u", "range": [10.0, 20.0]},
    ],
    "target_rows": 1500,
}


def test_metric_round_trip():
    m = Metric.from_dict({"name": "x", "unit": "y", "range": [1, 2]})
    assert m.range == (1.0, 2.0)
    out = m.to_dict()
    m2 = Metric.from_dict(out)
    assert m2 == m


def test_metric_range_validation():
    with pytest.raises(ValueError, match="low must be < high"):
        Metric.from_dict({"name": "x", "unit": "y", "range": [5, 5]})
    with pytest.raises(ValueError, match="low must be < high"):
        Metric.from_dict({"name": "x", "unit": "y", "range": [10, 1]})
    with pytest.raises(ValueError, match="\\[low, high\\] pair"):
        Metric.from_dict({"name": "x", "unit": "y", "range": [1, 2, 3]})
    with pytest.raises(ValueError, match="numeric"):
        Metric.from_dict({"name": "x", "unit": "y", "range": ["lo", "hi"]})


def test_scenario_context_round_trip():
    ctx = ScenarioContext.from_dict(VALID_SCENARIO_DICT)
    assert ctx.scenario_title == "Demo title"
    assert ctx.target_rows == 1500
    assert len(ctx.key_metrics) == 2
    assert ctx.key_metrics[0].range == (0.0, 1.0)

    # Round-trip through to_dict + JSON
    serialized = json.loads(json.dumps(ctx.to_dict()))
    ctx2 = ScenarioContext.from_dict(serialized)
    assert ctx2 == ctx


def test_scenario_context_grandfather_unknown_keys():
    """D2: legacy category_id and _validation_warnings are silently ignored."""
    legacy = {
        **VALID_SCENARIO_DICT,
        "category_id": 1,                   # pre-Sprint-C.2 envelope leak
        "_validation_warnings": ["foo"],    # pre-Sprint-C.4 soft-fail leak
        "future_field": {"anything": True},
    }
    ctx = ScenarioContext.from_dict(legacy)
    assert ctx.scenario_title == "Demo title"
    # to_dict must NOT carry the unknown keys back out
    out = ctx.to_dict()
    assert "category_id" not in out
    assert "_validation_warnings" not in out


def test_scenario_context_missing_required():
    bad = {k: v for k, v in VALID_SCENARIO_DICT.items() if k != "target_rows"}
    with pytest.raises(ValueError, match="missing fields.*target_rows"):
        ScenarioContext.from_dict(bad)


def test_scenario_record_round_trip():
    rec = ScenarioRecord(
        domain_id="dom_001",
        k=3,
        scenario=ScenarioContext.from_dict(VALID_SCENARIO_DICT),
        generated_at="2026-05-10T00:00:00+00:00",
    )
    assert rec.scenario_id == "dom_001/k=3"  # @property derived

    out = rec.to_dict()
    assert out["domain_id"] == "dom_001"
    assert out["k"] == 3
    assert out["generated_at"] == "2026-05-10T00:00:00+00:00"
    assert "scenario_id" not in out  # never persisted

    rec2 = ScenarioRecord.from_dict(json.loads(json.dumps(out)))
    assert rec2 == rec
    assert rec2.scenario_id == "dom_001/k=3"


def test_scenario_record_grandfather_legacy_envelope():
    """D2: existing scenario_pool.jsonl rows with category_id load fine."""
    legacy_envelope = {
        "domain_id": "dom_001",
        "k": 1,
        "category_id": 23,             # legacy
        "generated_at": "2026-05-01T00:00:00+00:00",
        "scenario": VALID_SCENARIO_DICT,
    }
    rec = ScenarioRecord.from_dict(legacy_envelope)
    assert rec.domain_id == "dom_001"
    assert rec.k == 1
    out = rec.to_dict()
    assert "category_id" not in out


def test_load_real_scenario_pool_first_line():
    """Fixture ↔ ScenarioRecord round-trip on the actual mini fixture."""
    fixture = Path(__file__).parent / "fixtures" / "scenario_pool_mini.jsonl"
    if not fixture.exists():
        pytest.skip("mini fixture absent")
    with fixture.open() as f:
        first_raw = json.loads(f.readline())
    rec = ScenarioRecord.from_dict(first_raw)
    assert rec.scenario_id.startswith(rec.domain_id + "/k=")
    # Re-serializing must drop category_id even though source had it
    assert "category_id" not in rec.to_dict()
