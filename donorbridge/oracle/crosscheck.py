"""Cross-check every solver against the exact ones on random pools.

Owner: Lead
Implemented in: P3
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CrosscheckReport:
    """Summary of a crosscheck run.

    Attributes:
        n_pools: Pools checked.
        mismatches: One dict per disagreement, including the pool's seed so it can be replayed.
    """

    n_pools: int
    mismatches: list[dict]


def crosscheck(n_pools: int, seed: int, sizes: tuple[int, ...] = (8, 10, 12, 20, 30)) -> CrosscheckReport:
    """On n_pools random pools with sizes cycling through `sizes`: brute force (n <= 12) == B&B == ILP,
    matching == ILP(L=2) == networkx, and every heuristic <= ILP. Logs every mismatch."""
    raise NotImplementedError("Lead, P3")
