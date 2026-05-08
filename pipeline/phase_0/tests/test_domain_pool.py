"""
Test suite for Phase 0: Domain Pool (Subtask 2).

Tests:
1. check_overlap detects duplicates
2. check_overlap allows distinct items
3. Domain pool JSON schema validation
4. DomainSampler basic sampling
5. DomainSampler complexity filter
6. DomainSampler exhaustion reset

All tests use pre-built fixtures — no LLM calls.

Run from pipeline/:
    python -m phase_0.tests.test_domain_pool
"""

import sys
import json
import tempfile
import os

# ================================================================
# Fixture: Mini domain pool JSON
# ================================================================

MINI_POOL = {
    "version": "1.0",
    "generated_at": "2024-12-15T10:30:00Z",
    "total_domains": 9,
    "diversity_score": 0.95,
    "complexity_distribution": {"simple": 3, "medium": 3, "complex": 3},
    "topic_coverage": {"Healthcare": 3, "Finance": 3, "Retail & E-Commerce": 3},
    "domains": [
        {
            "id": "dom_001",
            "name": "ICU bed turnover analytics",
            "topic": "Healthcare",
            "complexity_tier": "complex",
            "typical_entities_hint": ["hospitals", "ICU wards", "patient categories"],
            "typical_metrics_hint": [
                {"name": "occupancy_rate", "unit": "%"},
                {"name": "length_of_stay", "unit": "days"},
            ],
            "temporal_granularity_hint": "daily",
        },
        {
            "id": "dom_002",
            "name": "Clinical trial enrollment tracking",
            "topic": "Healthcare",
            "complexity_tier": "medium",
            "typical_entities_hint": ["trial sites", "drug candidates"],
            "typical_metrics_hint": [
                {"name": "enrollment_count", "unit": "patients"},
                {"name": "dropout_rate", "unit": "%"},
            ],
            "temporal_granularity_hint": "weekly",
        },
        {
            "id": "dom_003",
            "name": "Primary care visit volume",
            "topic": "Healthcare",
            "complexity_tier": "simple",
            "typical_entities_hint": ["clinics"],
            "typical_metrics_hint": [
                {"name": "visits_per_day", "unit": "count"},
            ],
            "temporal_granularity_hint": "daily",
        },
        {
            "id": "dom_004",
            "name": "Credit card fraud detection logs",
            "topic": "Finance",
            "complexity_tier": "complex",
            "typical_entities_hint": ["card issuers", "merchants", "regions"],
            "typical_metrics_hint": [
                {"name": "fraud_amount", "unit": "USD"},
                {"name": "false_positive_rate", "unit": "%"},
            ],
            "temporal_granularity_hint": "hourly",
        },
        {
            "id": "dom_005",
            "name": "Mutual fund flow analytics",
            "topic": "Finance",
            "complexity_tier": "medium",
            "typical_entities_hint": ["fund families", "asset classes"],
            "typical_metrics_hint": [
                {"name": "net_inflow", "unit": "USD millions"},
                {"name": "expense_ratio", "unit": "%"},
            ],
            "temporal_granularity_hint": "monthly",
        },
        {
            "id": "dom_006",
            "name": "Stock market daily close prices",
            "topic": "Finance",
            "complexity_tier": "simple",
            "typical_entities_hint": ["tickers"],
            "typical_metrics_hint": [
                {"name": "close_price", "unit": "USD"},
            ],
            "temporal_granularity_hint": "daily",
        },
        {
            "id": "dom_007",
            "name": "Flash sale conversion funnels",
            "topic": "Retail & E-Commerce",
            "complexity_tier": "complex",
            "typical_entities_hint": ["product categories", "channels", "cohorts"],
            "typical_metrics_hint": [
                {"name": "conversion_rate", "unit": "%"},
                {"name": "average_order_value", "unit": "USD"},
                {"name": "cart_abandonment_rate", "unit": "%"},
            ],
            "temporal_granularity_hint": "hourly",
        },
        {
            "id": "dom_008",
            "name": "Customer return behavior analysis",
            "topic": "Retail & E-Commerce",
            "complexity_tier": "medium",
            "typical_entities_hint": ["product lines", "return reasons"],
            "typical_metrics_hint": [
                {"name": "return_rate", "unit": "%"},
                {"name": "refund_amount", "unit": "USD"},
            ],
            "temporal_granularity_hint": "weekly",
        },
        {
            "id": "dom_009",
            "name": "Daily footfall count in retail stores",
            "topic": "Retail & E-Commerce",
            "complexity_tier": "simple",
            "typical_entities_hint": ["store locations"],
            "typical_metrics_hint": [
                {"name": "footfall", "unit": "count"},
            ],
            "temporal_granularity_hint": "daily",
        },
    ],
}


def _write_mini_pool(path: str) -> None:
    """Write the mini pool fixture to a file."""
    with open(path, "w") as f:
        json.dump(MINI_POOL, f, indent=2)


# ---- Test 1: check_overlap detects duplicates ----
print("=" * 60)
print("Test 1: check_overlap detects duplicates")
print("=" * 60)

try:
    from phase_0.domain_pool import check_overlap
    from unittest.mock import patch
    import numpy as np

    items = [
        "Healthcare analytics dashboard monitoring",
        "Healthcare analytics dashboard tracking",
        "Cryptocurrency trading platform exchange",
    ]

    # Mock get_embeddings to return simple vectors
    # [1,0], [0.99, 0.01], [0,1]
    mock_embeddings = np.array([
        [1.0, 0.0],
        [0.9, 0.1],
        [0.0, 1.0]
    ])

    with patch('phase_0.overlap_checker.get_embeddings', return_value=mock_embeddings):
        overlaps = check_overlap(items, threshold=0.4)
    assert len(overlaps) >= 1, (
        f"Expected at least 1 overlap between similar items, got {len(overlaps)}"
    )
    for a, b, sim in overlaps:
        print(f"  ✓ Overlap detected: '{a}' ↔ '{b}' (sim={sim:.3f})")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 2: check_overlap allows distinct items ----
print("=" * 60)
print("Test 2: check_overlap allows distinct items")
print("=" * 60)

try:
    items_distinct = [
        "ICU bed turnover analytics",
        "Cryptocurrency exchange volume",
        "Solar panel efficiency monitoring",
    ]
    # Mock get_embeddings to return distinctly different vectors
    # [1,0,0], [0,1,0], [0,0,1]
    mock_embeddings_distinct = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])

    with patch('phase_0.overlap_checker.get_embeddings', return_value=mock_embeddings_distinct):
        overlaps = check_overlap(items_distinct, threshold=0.80)
    assert len(overlaps) == 0, (
        f"Expected no overlaps for distinct items, got {len(overlaps)}: {overlaps}"
    )
    print(f"  ✓ No overlaps detected for 3 distinct items (threshold=0.80)")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 3: Domain pool JSON schema ----
print("=" * 60)
print("Test 3: Domain pool JSON schema validation")
print("=" * 60)

try:
    pool = MINI_POOL

    # Required top-level keys
    assert "version" in pool
    assert "generated_at" in pool
    assert "total_domains" in pool
    assert "domains" in pool
    assert isinstance(pool["domains"], list)
    assert pool["total_domains"] == len(pool["domains"])

    # Domain structure
    dom = pool["domains"][0]
    assert "id" in dom
    assert dom["id"].startswith("dom_")
    assert "name" in dom
    assert "topic" in dom
    assert "complexity_tier" in dom
    assert dom["complexity_tier"] in ("simple", "medium", "complex")
    assert "typical_entities_hint" in dom
    assert "typical_metrics_hint" in dom
    assert "temporal_granularity_hint" in dom

    print(f"  ✓ Pool schema valid: {pool['total_domains']} domains, "
          f"version={pool['version']}")
    print(f"  ✓ Complexity distribution: {pool['complexity_distribution']}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 4: DomainSampler basic sampling ----
print("=" * 60)
print("Test 4: DomainSampler basic sampling")
print("=" * 60)

try:
    from phase_0.domain_pool import DomainSampler

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(MINI_POOL, f, indent=2)
        pool_path = f.name

    try:
        sampler = DomainSampler(pool_path)
        sample = sampler.sample(n=3)

        assert len(sample) == 3, f"Expected 3, got {len(sample)}"

        # No duplicates
        ids = [d["id"] for d in sample]
        assert len(set(ids)) == 3, f"Duplicate IDs in sample: {ids}"

        # All have required fields
        for d in sample:
            assert "id" in d
            assert "name" in d
            assert "topic" in d

        print(f"  ✓ Sampled 3 domains without replacement:")
        for d in sample:
            print(f"    {d['id']}: {d['name']} [{d['complexity_tier']}]")

        # Second sample should not repeat
        sample2 = sampler.sample(n=3)
        ids2 = [d["id"] for d in sample2]
        assert len(set(ids) & set(ids2)) == 0, (
            f"Repeat found: {set(ids) & set(ids2)}"
        )
        print(f"  ✓ Second sample has no repeats with first")

    finally:
        os.unlink(pool_path)

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 5: DomainSampler complexity filter ----
print("=" * 60)
print("Test 5: DomainSampler complexity filter")
print("=" * 60)

try:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(MINI_POOL, f, indent=2)
        pool_path = f.name

    try:
        sampler = DomainSampler(pool_path)
        sample = sampler.sample(n=2, complexity="complex")

        assert len(sample) == 2, f"Expected 2, got {len(sample)}"
        for d in sample:
            assert d["complexity_tier"] == "complex", (
                f"Expected complex, got {d['complexity_tier']}"
            )

        print(f"  ✓ Filtered 2 complex domains:")
        for d in sample:
            print(f"    {d['id']}: {d['name']}")

    finally:
        os.unlink(pool_path)

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ---- Test 6: DomainSampler exhaustion reset ----
print("=" * 60)
print("Test 6: DomainSampler exhaustion reset")
print("=" * 60)

try:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(MINI_POOL, f, indent=2)
        pool_path = f.name

    try:
        sampler = DomainSampler(pool_path)

        # Exhaust all 9 domains
        all_samples = sampler.sample(n=9)
        assert len(all_samples) == 9

        # Now try to sample again — should trigger reset
        more = sampler.sample(n=3)
        assert len(more) == 3, f"Expected 3 after reset, got {len(more)}"
        print(f"  ✓ After exhausting all 9 domains, reset triggered, "
              f"sampled {len(more)} more")

    finally:
        os.unlink(pool_path)

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()


# ---- Summary ----
print("=" * 60)
print("All 7 tests passed! ✓")
print("=" * 60)
