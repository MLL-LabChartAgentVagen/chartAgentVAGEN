"""
AGPDS Phase 1: Scenario Pool Deduplication (§1.3)

Embedding-based JSONL record deduplication, scoped global / category /
domain. Extracted from scenario_contextualizer.py so generation and
dedup are independent modules.
"""

from collections import defaultdict


def deduplicate_scenario_records(
    records: list[dict],
    threshold: float = 0.85,
    scope: str = "category",
    min_per_domain: int = 1,
) -> list[dict]:
    """Deduplicate JSONL scenario records while preserving cache coverage.

    Args:
        records: Scenario-pool envelopes containing domain_id, category_id,
            and scenario.data_context.
        threshold: Cosine similarity threshold for dedup.
        scope: Comparison scope: "global", "category", or "domain".
        min_per_domain: Minimum records to keep for each domain_id.

    Returns:
        Filtered records in their original order.
    """
    if scope not in {"global", "category", "domain"}:
        raise ValueError(
            f"Invalid dedup scope: {scope!r}. "
            "Expected 'global', 'category', or 'domain'."
        )
    if min_per_domain < 0:
        raise ValueError("min_per_domain must be >= 0")
    if len(records) < 2:
        return list(records)

    domain_counts: dict[str, int] = defaultdict(int)
    for rec in records:
        domain_counts[rec.get("domain_id", "")] += 1

    drop_indices: set[int] = set()
    for group_indices in _record_groups(records, scope):
        if len(group_indices) < 2:
            continue

        contexts = [
            records[i].get("scenario", {}).get("data_context", "")
            for i in group_indices
        ]
        for _local_a, local_b, _sim in _overlap_index_pairs(
            contexts, threshold=threshold
        ):
            global_b = group_indices[local_b]
            domain_id = records[global_b].get("domain_id", "")
            if domain_counts[domain_id] <= min_per_domain:
                continue
            if global_b in drop_indices:
                continue
            drop_indices.add(global_b)
            domain_counts[domain_id] -= 1

    return [r for i, r in enumerate(records) if i not in drop_indices]


def _record_groups(records: list[dict], scope: str) -> list[list[int]]:
    """Return record index groups for the requested dedup scope."""
    if scope == "global":
        return [list(range(len(records)))]

    key_name = "category_id" if scope == "category" else "domain_id"
    buckets: dict[object, list[int]] = defaultdict(list)
    for i, rec in enumerate(records):
        buckets[rec.get(key_name)].append(i)
    return list(buckets.values())


def _overlap_index_pairs(
    contexts: list[str],
    threshold: float = 0.85,
) -> list[tuple[int, int, float]]:
    """Return index pairs whose data_context embeddings are near-duplicates."""
    if len(contexts) < 2:
        return []

    from pipeline.phase_0.overlap_checker import get_embeddings, cosine_similarity

    embeddings = get_embeddings(contexts)
    sim_matrix = cosine_similarity(embeddings)

    overlaps: list[tuple[int, int, float]] = []
    for i in range(len(contexts)):
        for j in range(i + 1, len(contexts)):
            sim = float(sim_matrix[i][j])
            if sim >= threshold:
                overlaps.append((i, j, sim))
    return overlaps
