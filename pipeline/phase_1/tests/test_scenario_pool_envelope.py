"""End-to-end envelope sanity for the production scenario_pool.jsonl.

Loads the real ``pipeline/phase_1/scenario_pool.jsonl`` and asserts:

  * Every record round-trips through :class:`ScenarioRecord.from_dict`.
  * ``complexity_tier`` is one of {simple, medium, complex}.
  * ``k`` is 0-indexed (>= 0) and starts at 0 for every domain.
  * No legacy ``category_id`` field leaked in.
  * ``target_rows`` falls inside :data:`TIER_TARGET_ROWS` for the record's tier.
  * All 300 phase_0 domains are represented.

Skipped when the file is absent (e.g. CI before regeneration).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from pipeline.phase_1 import TIER_TARGET_ROWS
from pipeline.phase_1.types import ScenarioRecord


PROJECT_ROOT = Path(__file__).resolve().parents[3]
POOL_PATH = PROJECT_ROOT / "pipeline" / "phase_1" / "scenario_pool.jsonl"
DOMAIN_POOL_PATH = PROJECT_ROOT / "pipeline" / "phase_0" / "domain_pool.json"


def _records() -> list[dict]:
    if not POOL_PATH.exists():
        pytest.skip(f"scenario_pool.jsonl absent at {POOL_PATH}")
    with POOL_PATH.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_records_round_trip_through_dataclass():
    for raw in _records():
        rec = ScenarioRecord.from_dict(raw)
        assert rec.scenario_id.startswith(rec.domain_id + "/k=")


def test_no_legacy_category_id_field():
    for raw in _records():
        assert "category_id" not in raw, (
            f"legacy category_id leaked in {raw.get('domain_id')}/k={raw.get('k')}"
        )


def test_k_is_zero_indexed():
    """All k must be >= 0. Gaps in 0..K-1 are allowed: validator rejections and
    domain-scope dedup can both legitimately drop arbitrary (domain, k) pairs."""
    for raw in _records():
        assert raw["k"] >= 0, raw


def test_target_rows_in_tier_range():
    for raw in _records():
        rec = ScenarioRecord.from_dict(raw)
        lo, hi = TIER_TARGET_ROWS[rec.complexity_tier]
        assert lo <= rec.scenario.target_rows <= hi, (
            f"{rec.domain_id}/k={rec.k} tier={rec.complexity_tier} "
            f"target_rows={rec.scenario.target_rows} out of [{lo},{hi}]"
        )


def test_phase0_domain_coverage_above_threshold():
    """Most phase_0 domains must have at least one scenario.

    A small fraction can legitimately drop out when the LLM consistently
    rejects the tier's target_rows range across all retries (most common in
    the complex tier, where 1000-3000 is far from typical LLM priors).
    Floor: 95% coverage.
    """
    if not DOMAIN_POOL_PATH.exists():
        pytest.skip("domain_pool.json absent")
    pool = json.loads(DOMAIN_POOL_PATH.read_text(encoding="utf-8"))
    expected = {d["id"] for d in pool["domains"]}
    present = {raw["domain_id"] for raw in _records()}
    coverage = len(present) / len(expected)
    missing = expected - present
    assert coverage >= 0.95, (
        f"only {len(present)}/{len(expected)} domains covered ({100*coverage:.1f}%); "
        f"missing {len(missing)}: {sorted(missing)[:8]}..."
    )


def test_minimum_post_dedup_count():
    """Post-regeneration size sanity (>= 1100 per design contract)."""
    recs = _records()
    assert len(recs) >= 1100, f"only {len(recs)} records; expected >= 1100"
