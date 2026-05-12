"""
Per-family distribution primitives shared by engine sampling (numpy rng.*)
and validation KS testing (scipy.stats frozen dists).

Responsibilities (stateless, no engine arithmetic):
  - Family parameter validation (raises InvalidParameterError with row context).
  - Per-row sampling for 7 base families (sample_family).
  - Per-cell CDF construction for the L2 KS validator (expected_cdf) +
    recursive mixture CDF (expected_cdf_mixture / MixtureFrozen).
  - Per-param clamping of sigma/scale/rate to POSITIVE_CLAMP.

Mixture *sampling* stays in engine/measures.py (_sample_mixture) because it
composes the engine's per-row intercept+effects arithmetic with this module's
sample_family primitive — putting it here would require a callback hack.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import scipy.stats

from ..exceptions import InvalidParameterError

logger = logging.getLogger(__name__)


POSITIVE_CLAMP: float = 1e-6

SUPPORTED_FAMILIES: frozenset[str] = frozenset({
    "gaussian", "lognormal", "gamma", "beta", "uniform",
    "poisson", "exponential", "mixture",
})


def clamp_params(
    params: dict[str, np.ndarray | float],
    *,
    col_name: str | None = None,
    log_clamps: bool = False,
) -> dict[str, np.ndarray | float]:
    """Clamp sigma/scale/rate to POSITIVE_CLAMP. Returns a new dict.

    Engine passes log_clamps=True (and col_name) so per-column clamp counts
    surface in LLM retry feedback. Validator passes log_clamps=False and
    silently clamps scalar per-cell params before handing them to scipy.
    """
    result: dict[str, np.ndarray | float] = {}
    for param_key, theta in params.items():
        if param_key in ("sigma", "scale", "rate"):
            if isinstance(theta, np.ndarray):
                original = theta
                theta = np.maximum(theta, POSITIVE_CLAMP)
                if log_clamps and param_key in ("sigma", "scale") and col_name:
                    n_clamped = int((theta != original).sum())
                    if n_clamped > 0:
                        logger.warning(
                            "Clamped %s.%s: %d values clamped to 1e-6.",
                            col_name, param_key, n_clamped,
                        )
            else:
                theta = max(float(theta), POSITIVE_CLAMP)
        result[param_key] = theta
    return result


def validate_distribution_params(
    col_name: str,
    family: str,
    mu: np.ndarray,
    sigma: np.ndarray,
) -> None:
    """Per-family pre-call validation of per-row distribution parameters.

    Converts bare numpy errors (e.g. ``ValueError: a <= 0`` from ``rng.beta(0, ...)``)
    into structured ``InvalidParameterError`` carrying the column name, family,
    offending parameter, first bad row, and a concrete fix hint. The sandbox
    retry loop feeds this straight to the LLM via ``format_error_feedback()``.

    Only covers conditions not already handled by the per-param clamp
    (which floors ``sigma`` / ``scale`` / ``rate`` to ``1e-6``). That clamp makes
    sigma-based guards redundant for beta, gamma, and lognormal; what remains
    is the ``mu`` axis those distributions use as their first positional parameter.
    """
    if family in ("beta", "gamma"):
        bad = np.where(mu <= 0)[0]
        if len(bad) > 0:
            raise InvalidParameterError(
                param_name="mu",
                value=float(mu[bad[0]]),
                reason=(
                    f"Measure '{col_name}' (family='{family}'): parameter "
                    f"'mu' must be > 0 for all rows, got {float(mu[bad[0]])} "
                    f"at row {int(bad[0])}. Raise the intercept or effect "
                    f"values so every row has a positive mu."
                ),
            )
    elif family == "poisson":
        bad = np.where(mu < 0)[0]
        if len(bad) > 0:
            raise InvalidParameterError(
                param_name="mu",
                value=float(mu[bad[0]]),
                reason=(
                    f"Measure '{col_name}' (family='poisson'): parameter "
                    f"'mu' must be >= 0, got {float(mu[bad[0]])} at row "
                    f"{int(bad[0])}."
                ),
            )


def sample_family(
    col_name: str,
    family: str,
    params: dict[str, np.ndarray],
    n_rows: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Dispatch a per-row sample for one (already-resolved) distribution family.

    `params` must contain the per-row arrays (mu, sigma) of length n_rows.
    Calls validate_distribution_params before dispatch so the column/family/
    row-index error context is preserved (especially when called from
    sample_mixture on a masked subset).
    """
    mu = params.get("mu", np.zeros(n_rows))
    sigma = params.get("sigma", np.ones(n_rows))

    validate_distribution_params(col_name, family, mu, sigma)

    if family == "gaussian":
        return rng.normal(mu, sigma)
    elif family == "lognormal":
        return rng.lognormal(mu, sigma)
    elif family == "gamma":
        return rng.gamma(shape=mu, scale=sigma)
    elif family == "beta":
        return rng.beta(mu, sigma)
    elif family == "uniform":
        return rng.uniform(mu, sigma)
    elif family == "poisson":
        return rng.poisson(mu).astype(np.float64)
    elif family == "exponential":
        rate = np.maximum(mu, POSITIVE_CLAMP)
        return rng.exponential(1.0 / rate)
    else:
        raise ValueError(f"Unknown distribution family: '{family}'")


class MixtureFrozen:
    """scipy frozen-dist-like adapter exposing .cdf() for kstest (DS-3).

    For a mixture of K components with normalized weights w_k and frozen scipy
    distributions D_k: cdf(x) = sum(w_k * D_k.cdf(x)).
    """

    def __init__(self, components: list[tuple[float, Any]]):
        self.components = components  # list of (normalized_weight, frozen_dist)

    def cdf(self, x):
        return sum(w * d.cdf(x) for w, d in self.components)


def expected_cdf(family: str, params: dict[str, float]) -> Any:
    """Build a scipy frozen distribution for KS testing.

    Returns a scipy.stats frozen distribution, or None if unsupported
    (poisson — KS test on discrete distributions is approximate) or
    degenerate (uniform with high <= low).
    """
    mu = params.get("mu", 0.0)
    sigma = params.get("sigma", 1.0)

    if family == "gaussian":
        return scipy.stats.norm(loc=mu, scale=sigma)
    elif family == "lognormal":
        return scipy.stats.lognorm(s=sigma, scale=np.exp(mu))
    elif family == "exponential":
        rate = max(mu, POSITIVE_CLAMP)
        return scipy.stats.expon(scale=1.0 / rate)
    elif family == "gamma":
        shape = max(mu, POSITIVE_CLAMP)
        scale = max(sigma, POSITIVE_CLAMP)
        return scipy.stats.gamma(a=shape, scale=scale)
    elif family == "beta":
        a = max(mu, POSITIVE_CLAMP)
        b = max(sigma, POSITIVE_CLAMP)
        return scipy.stats.beta(a, b)
    elif family == "uniform":
        low, high = mu, sigma
        if high <= low:
            return None
        return scipy.stats.uniform(loc=low, scale=high - low)
    elif family == "poisson":
        return None
    elif family == "mixture":
        return expected_cdf_mixture(params)
    return None


def expected_cdf_mixture(params: dict[str, Any]) -> MixtureFrozen | None:
    """Build a frozen mixture CDF from cell-resolved mixture params (DS-3).

    `params` shape (from the validator's _compute_cell_params recursion):
      {"components": [{"family": str, "weight": float, "params": {...}}, ...]}

    Returns None if any component family is unsupported by expected_cdf
    (e.g. poisson) — the cell will then be soft-passed by the caller.
    """
    components = params.get("components")
    if not components:
        return None
    frozen: list[tuple[float, Any]] = []
    total = 0.0
    for i, comp in enumerate(components):
        sub = expected_cdf(comp["family"], comp["params"])
        if sub is None:
            logger.debug(
                "mixture KS skipped: component[%d] family='%s' has no scipy CDF.",
                i, comp["family"],
            )
            return None
        frozen.append((float(comp["weight"]), sub))
        total += float(comp["weight"])
    if total <= 0:
        return None
    return MixtureFrozen([(w / total, d) for w, d in frozen])
