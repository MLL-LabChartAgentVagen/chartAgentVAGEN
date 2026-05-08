"""
AGPDS Phase 0: Domain Pool Construction

Provides domain taxonomy generation, overlap detection, and stratified sampling.
"""

from .domain_pool import (
    DomainPool,
    DomainSampler,
    check_overlap,
)

__all__ = [
    "DomainPool",
    "DomainSampler",
    "check_overlap",
]
