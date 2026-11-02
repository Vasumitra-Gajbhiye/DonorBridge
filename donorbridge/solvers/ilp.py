"""Integer linear program (cycle formulation) solved with PuLP: the exact reference solver.

Owner: Lead
Implemented in: P2
"""

from __future__ import annotations

from typing import ClassVar

from donorbridge.models import Cycle, Pool
from donorbridge.solvers.base import Solver


class ILPSolver(Solver):
    """One binary variable per ring; each family in at most one chosen ring; maximise total scorer
    weight. CBC via PuLP, time_limit_s passed through, solver status mapped to the optimal flag."""

    name: ClassVar[str] = "ilp"
    exact: ClassVar[bool] = True
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)

    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]:
        """See the class docstring. Returns (chosen rings, optimal flag, stats)."""
        raise NotImplementedError("Lead, P2")
