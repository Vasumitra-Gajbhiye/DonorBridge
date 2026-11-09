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
        # A ring becomes possible when its last family arrives, so its max id is its arrival time.
        arrival_order = sorted(cycles, key=lambda c: (max(c.families), len(c), c.families))

        chosen: list[Cycle] = []
        covered: set[int] = set()  # families already in a chosen ring
        for ring in arrival_order:
            if covered.isdisjoint(ring.families):
                chosen.append(ring)
                covered.update(ring.families)

        stats = {"rings_considered": len(cycles), "rings_taken": len(chosen)}
        return chosen, False, stats
