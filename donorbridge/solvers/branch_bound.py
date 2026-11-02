"""Branch and bound: exact search over include/exclude decisions with a weight bound.

Owner: Heuristics
Implemented in: P2
"""

from __future__ import annotations

from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


class BranchAndBoundSolver(Solver):
    """Include/exclude branching over rings with an upper bound for pruning; honours time_limit_s
    (optimal=False on timeout). stats: nodes, pruned, timed_out."""

    name: ClassVar[str] = "branch-bound"
    exact: ClassVar[bool] = True
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        raise NotImplementedError("Heuristics, P2")
