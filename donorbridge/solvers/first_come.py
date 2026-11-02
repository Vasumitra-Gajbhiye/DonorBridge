"""First-come baseline: take rings in arrival order, ignoring weights.

Owner: Heuristics
Implemented in: P1
"""

from __future__ import annotations

from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


class FirstComeSolver(Solver):
    """Ids are arrival order. Go through rings sorted by (max id, len, families) and take each one
    disjoint from those already taken. Ignores weights on purpose: the naive baseline."""

    name: ClassVar[str] = "first-come"
    exact: ClassVar[bool] = False
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        raise NotImplementedError("Heuristics, P1")
