"""Greedy heuristic: heaviest disjoint rings first.

Owner: Heuristics
Implemented in: P1
"""

from __future__ import annotations

from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


class GreedySolver(Solver):
    """Sort rings by weight (descending), ties by fewest conflicting rings, then by families;
    take each ring disjoint from those already taken."""

    name: ClassVar[str] = "greedy"
    exact: ClassVar[bool] = False
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        raise NotImplementedError("Heuristics, P1")
