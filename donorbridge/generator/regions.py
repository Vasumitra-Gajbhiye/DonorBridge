"""Region split: one national pool versus separate state-level pools.

Owner: Generator
Implemented in: P3
"""

from __future__ import annotations

from donorbridge.models import Pool


def split_by_region(pool: Pool) -> list[Pool]:
    """One induced sub-pool per region (via pool.subpool), named "<name>-r<k>". Edges that cross
    regions are dropped."""
    raise NotImplementedError("Generator, P3")
