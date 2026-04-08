"""
Distribution samplers for FactTableSimulator.

Provides a unified interface to sample from 8 supported distribution
families, with optional scale mapping for bounded outputs.
"""

import numpy as np
from typing import Optional


SUPPORTED_DISTS = frozenset({
    "gaussian", "lognormal", "gamma", "beta",
    "uniform", "poisson", "exponential", "mixture",
})


def _validate_positive(params: dict, *keys: str, dist_name: str) -> None:
    """Ensure specified params are strictly positive."""
    for k in keys:
        if k in params and params[k] <= 0:
            raise ValueError(
                f"Distribution '{dist_name}': parameter '{k}' must be > 0, "
                f"got {params[k]}"
            )


def _validate_required(params: dict, *keys: str, dist_name: str) -> None:
    """Ensure required parameters are present."""
    missing = [k for k in keys if k not in params]
    if missing:
        raise ValueError(
            f"Distribution '{dist_name}': missing required parameter(s): "
            f"{', '.join(missing)}"
        )


def _apply_scale(
    raw: np.ndarray, scale: Optional[list[float]]
) -> np.ndarray:
    """Linearly map raw values into [low, high] range."""
    if scale is None:
        return raw
    low, high = scale[0], scale[1]
    raw_min, raw_max = raw.min(), raw.max()
    if raw_max == raw_min:
        return np.full_like(raw, (low + high) / 2)
    return low + (raw - raw_min) / (raw_max - raw_min) * (high - low)


def sample_distribution(
    dist_name: str,
    params: dict,
    n: int,
    rng: np.random.Generator,
    scale: Optional[list[float]] = None,
) -> np.ndarray:
    """
    Sample n values from the named distribution.

    Args:
        dist_name: One of SUPPORTED_DISTS.
        params: Distribution-specific parameters.
        n: Number of samples to draw.
        rng: NumPy random Generator for reproducibility.
        scale: Optional [low, high] for linear rescaling.

    Returns:
        1-D numpy array of n samples.

    Raises:
        ValueError: If dist_name is unknown or params are invalid.
    """
    if dist_name not in SUPPORTED_DISTS:
        raise ValueError(
            f"Unsupported distribution '{dist_name}'. "
            f"Must be one of: {', '.join(sorted(SUPPORTED_DISTS))}"
        )

    sampler = _SAMPLERS[dist_name]
    raw = sampler(params, n, rng)
    return _apply_scale(raw, scale)


# ---- Individual distribution samplers ----

def _sample_gaussian(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "mu", "sigma", dist_name="gaussian")
    _validate_positive(params, "sigma", dist_name="gaussian")
    return rng.normal(params["mu"], params["sigma"], n)


def _sample_lognormal(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "mu", "sigma", dist_name="lognormal")
    _validate_positive(params, "sigma", dist_name="lognormal")
    return rng.lognormal(params["mu"], params["sigma"], n)


def _sample_gamma(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "shape", "scale", dist_name="gamma")
    _validate_positive(params, "shape", "scale", dist_name="gamma")
    return rng.gamma(params["shape"], params["scale"], n)


def _sample_beta(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "alpha", "beta", dist_name="beta")
    _validate_positive(params, "alpha", "beta", dist_name="beta")
    return rng.beta(params["alpha"], params["beta"], n)


def _sample_uniform(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "low", "high", dist_name="uniform")
    if params["low"] >= params["high"]:
        raise ValueError(
            f"Distribution 'uniform': 'low' ({params['low']}) must be < "
            f"'high' ({params['high']})"
        )
    return rng.uniform(params["low"], params["high"], n)


def _sample_poisson(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "lam", dist_name="poisson")
    _validate_positive(params, "lam", dist_name="poisson")
    return rng.poisson(params["lam"], n).astype(float)


def _sample_exponential(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "scale", dist_name="exponential")
    _validate_positive(params, "scale", dist_name="exponential")
    return rng.exponential(params["scale"], n)


def _sample_mixture(params: dict, n: int, rng: np.random.Generator) -> np.ndarray:
    _validate_required(params, "components", dist_name="mixture")
    components = params["components"]
    if not components:
        raise ValueError("Distribution 'mixture': 'components' list is empty")

    weights = np.array([c.get("weight", 1.0) for c in components])
    weights = weights / weights.sum()

    # Determine how many samples from each component
    assignments = rng.choice(len(components), size=n, p=weights)
    result = np.empty(n, dtype=float)

    for idx, comp in enumerate(components):
        mask = assignments == idx
        count = mask.sum()
        if count == 0:
            continue
        comp_dist = comp["dist"]
        comp_params = comp["params"]
        if comp_dist not in SUPPORTED_DISTS or comp_dist == "mixture":
            raise ValueError(
                f"Mixture component distribution '{comp_dist}' is invalid "
                f"or nested mixtures are not supported."
            )
        result[mask] = _SAMPLERS[comp_dist](comp_params, count, rng)

    return result


_SAMPLERS = {
    "gaussian": _sample_gaussian,
    "lognormal": _sample_lognormal,
    "gamma": _sample_gamma,
    "beta": _sample_beta,
    "uniform": _sample_uniform,
    "poisson": _sample_poisson,
    "exponential": _sample_exponential,
    "mixture": _sample_mixture,
}
