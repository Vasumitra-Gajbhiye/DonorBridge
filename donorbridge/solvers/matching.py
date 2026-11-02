"""Maximum-weight matching: exact for 2-swaps only (polynomial time).

Owner: Matching
Implemented in: P3
"""

from __future__ import annotations

from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


class MatchingSolver(Solver):
    """Rings capped at 2 are edges of an undirected graph (mutual pairs); solve maximum-weight
    matching on it. Only max_cycle_len=2 is supported."""

    name: ClassVar[str] = "matching"
    exact: ClassVar[bool] = True
    supported_lengths: ClassVar[tuple[int, ...]] = (2,)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        raise NotImplementedError("Matching, P3")
