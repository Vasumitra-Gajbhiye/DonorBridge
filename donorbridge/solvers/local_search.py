"""Local search: improve a greedy start by swapping one ring out for up to two rings in.

Owner: Heuristics
Implemented in: P2
"""

from __future__ import annotations

from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


class LocalSearchSolver(Solver):
    """Start from greedy; repeatedly replace one chosen ring with the best set of at most two disjoint
    rings using its families plus uncovered ones, while total weight improves."""

    name: ClassVar[str] = "local-search"
    exact: ClassVar[bool] = False
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        raise NotImplementedError("Heuristics, P2")
