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
        scenario_id: Identifier for the scenario (e.g. ``"dom_001/k=0"``).
        prefix: String prepended to the hash. Defaults to ``"agpds"``.

    Returns:
        ``f"{prefix}_{10-char sha256 hex}"`` — deterministic, collision-resistant
        for any practical pipeline volume.
    """
    digest = hashlib.sha256(f"{seed}:{scenario_id}".encode()).hexdigest()[:10]
    return f"{prefix}_{digest}"
