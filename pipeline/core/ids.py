"""Deterministic identifier generation for the AGPDS pipeline.

The core contract — ``(declarations, seed) → bit-for-bit reproducible`` —
requires that every artifact path also be a deterministic function of inputs.
:func:`generation_id` is the canonical entry point: same ``(seed, scenario_id)``
always yields the same id.

Two scenario_id namespaces are in use:

* **Cached form** ``dom_NNN/k=N`` (k is 0-indexed) — points at a real entry in
  ``scenario_pool.jsonl``; parseable via :func:`parse_scenario_id`; round-trips
  cleanly. Used by the ``scenario_id=...`` replay path and by the cached
  branch of the ``category_id=...`` random-sampling path.
* **Live form** ``live:dom_NNN:<counter>`` — emitted only when no cached
  scenario backs the run (live mode, or cached-mode fallback on cache miss).
  Not parseable; serves purely as a hash seed for the (necessarily
  non-replayable) artifact path.

Both forms are accepted by :func:`generation_id` — it treats the scenario_id
as an opaque string. :func:`parse_scenario_id` and :func:`format_scenario_id`
only handle the cached form (live ids raise ``ValueError`` on parse, by design).
"""

import hashlib


def generation_id(seed: int, scenario_id: str, prefix: str = "agpds") -> str:
    """Return a stable id for a single generation run.

    Args:
        seed: The pipeline seed.
        scenario_id: Identifier for the scenario. Accepts either cached form
            (e.g. ``"dom_001/k=0"``) or live form
            (e.g. ``"live:dom_001:3"``) — both are hashed identically.
        prefix: String prepended to the hash. Defaults to ``"agpds"``.

    Returns:
        ``f"{prefix}_{10-char sha256 hex}"`` — deterministic, collision-resistant
        for any practical pipeline volume.
    """
    digest = hashlib.sha256(f"{seed}:{scenario_id}".encode()).hexdigest()[:10]
    return f"{prefix}_{digest}"


def parse_scenario_id(scenario_id: str) -> tuple[str, int]:
    """Inverse of :func:`format_scenario_id`.

    scenario_pool.jsonl indexes scenarios by ``(domain_id, k)`` where ``k`` is
    **0-indexed** (0..K_tier-1; no sentinel value). The canonical wire format
    joins them as ``"dom_NNN/k=N"``.

    Live-form scenario_ids (``live:dom_NNN:<counter>``) are not parseable as
    (domain_id, k) and this function raises ``ValueError`` on them by design —
    that is the explicit signal that the run was not backed by a cached entry.

    Raises:
        ValueError on malformed input or live-form ids.
    """
    domain_id, sep, k_part = scenario_id.partition("/")
    if not sep or not k_part.startswith("k="):
        raise ValueError(
            f"Malformed scenario_id: {scenario_id!r}; expected 'dom_NNN/k=N'"
        )
    try:
        k = int(k_part[2:])
    except ValueError as e:
        raise ValueError(
            f"Malformed scenario_id: {scenario_id!r}; k segment is not an integer"
        ) from e
    if k < 0:
        raise ValueError(
            f"Malformed scenario_id: {scenario_id!r}; k must be >= 0 "
            "(0-indexed; no sentinel value)"
        )
    return domain_id, k


def format_scenario_id(domain_id: str, k: int) -> str:
    """Build a cached-form scenario_id string from its components.

    ``k`` must be >= 0 (0-indexed). There is no sentinel value; runs without
    a backing cached entry use the live form constructed elsewhere.
    """
    if k < 0:
        raise ValueError(f"k must be >= 0 (got {k}); no sentinel value")
    return f"{domain_id}/k={k}"
