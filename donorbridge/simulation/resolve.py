"""Night-before re-solve: after failures, re-match the families left over (one round).

Owner: Simulation
Implemented in: P2
"""

from __future__ import annotations

from dataclasses import dataclass

from donorbridge.models import Pool, Solution
from donorbridge.simulation.failure import FailureOutcome
from donorbridge.solvers.base import Solver
from donorbridge.survival import SurvivalModel


@dataclass(frozen=True)
class ResolveOutcome:
    """Result of plan -> failures -> one re-solve round.

    Attributes:
        plan: The original solution.
        first: Failure draw on the original plan.
        resolve: Solution on the leftover pool (None if no re-solve was run).
        final_transplants: Transplants from the first round plus those from the re-solve.
    """

    plan: Solution
    first: FailureOutcome
    resolve: Solution | None
    final_transplants: int


class NightBeforeSimulator:
    """Plan, realise failures, re-solve the leftover families without failed edges, realise again."""

    def __init__(self, solver: Solver, survival: SurvivalModel, seed: int) -> None:
        """Store the solver and survival model; seed a FailureSimulator."""
        raise NotImplementedError("Simulation, P2")

    def run(self, pool: Pool) -> ResolveOutcome:
        """plan = solve(pool); first = realise; leftover = pool.subpool(unmatched or cancelled)
        .without_edges(first.failed_edges); resolve and realise again; add up transplants."""
        raise NotImplementedError("Simulation, P2")
