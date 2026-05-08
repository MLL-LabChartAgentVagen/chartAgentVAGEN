"""Determinism tests for DomainSampler.

`(pool, seed) → identical sample sequence` is a hard contract: same seed must
yield bit-for-bit identical samples across runs and across instances. This test
exercises that contract without LLM calls.
"""

import json
import os
import tempfile

import pytest

from pipeline.phase_0.domain_pool import DomainSampler


_MINI_POOL = {
    "version": "1.0",
    "total_domains": 12,
    "domains": [
        {"id": f"dom_{i:03d}", "name": f"domain {i}", "topic": "T",
         "complexity_tier": tier}
        for i, tier in enumerate(
            ["simple", "medium", "complex"] * 4, start=1
        )
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


def test_same_seed_two_samplers_yield_identical_sequence(pool_path):
    """Two fresh DomainSamplers with the same seed produce identical samples."""
    a = DomainSampler(pool_path, seed=42)
    b = DomainSampler(pool_path, seed=42)
    seq_a = [d["id"] for d in a.sample(n=10)]
    seq_b = [d["id"] for d in b.sample(n=10)]
    assert seq_a == seq_b, f"determinism broken: {seq_a} vs {seq_b}"


def test_different_seed_yields_different_sequence(pool_path):
    """Different seeds should (with overwhelming probability) yield different samples."""
    a = DomainSampler(pool_path, seed=42)
    b = DomainSampler(pool_path, seed=43)
    seq_a = [d["id"] for d in a.sample(n=10)]
    seq_b = [d["id"] for d in b.sample(n=10)]
    assert seq_a != seq_b, "seed=42 and seed=43 produced identical 10-sample sequence"


def test_repeated_calls_stay_deterministic(pool_path):
    """Successive sample() calls on the same instance are deterministic."""
    a = DomainSampler(pool_path, seed=7)
    b = DomainSampler(pool_path, seed=7)
    for _ in range(3):
        assert [d["id"] for d in a.sample(n=2)] == [d["id"] for d in b.sample(n=2)]


def test_default_seed_is_zero(pool_path):
    """DomainSampler() with no seed defaults to seed=0 (stable across runs)."""
    a = DomainSampler(pool_path)  # default seed=0
    b = DomainSampler(pool_path, seed=0)
    seq_a = [d["id"] for d in a.sample(n=5)]
    seq_b = [d["id"] for d in b.sample(n=5)]
    assert seq_a == seq_b
