"""Deterministic identifier generation for the AGPDS pipeline.

The core contract — `(declarations, seed) → bit-for-bit reproducible` — requires
that every artifact path also be a deterministic function of inputs. `generation_id`
is the canonical entry point: same `(seed, scenario_id)` always yields the same id.
"""

import hashlib


def generation_id(seed: int, scenario_id: str, prefix: str = "agpds") -> str:
    """Return a stable id for a single generation run.

    Args:
        seed: The pipeline seed.
        scenario_id: Identifier for the scenario (e.g. ``"dom_001/k=1"``).
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
    1-based. The canonical wire format joins them as ``"dom_NNN/k=N"``.

    Raises:
        ValueError on malformed input.
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
    return domain_id, k


def format_scenario_id(domain_id: str, k: int) -> str:
    """Build a scenario_id string from its components."""
    return f"{domain_id}/k={k}"
