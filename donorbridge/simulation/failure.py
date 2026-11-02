"""Night-before failure simulation: which planned crossmatches pass, which rings go ahead.

Owner: Simulation
Implemented in: P1
"""

from __future__ import annotations

from dataclasses import dataclass

from donorbridge.models import Cycle, Pool, Solution
from donorbridge.survival import SurvivalModel


@dataclass(frozen=True)
class FailureOutcome:
    """One random draw of the final crossmatches for a plan.

    Attributes:
        went_ahead: Rings whose every crossmatch passed.
        cancelled: Rings with at least one failed crossmatch.
        failed_edges: Every edge whose crossmatch failed.
        transplants: Sum of sizes of the rings that went ahead.
    """

    went_ahead: tuple[Cycle, ...]
    cancelled: tuple[Cycle, ...]
    failed_edges: frozenset[tuple[int, int]]
    transplants: int


class FailureSimulator:
    """Draws crossmatch outcomes from a survival model using its own seeded random.Random."""

    def __init__(self, survival: SurvivalModel, seed: int) -> None:
        """Store the survival model and create a private RNG from `seed`."""
        raise NotImplementedError("Simulation, P1")

    def realise(self, pool: Pool, solution: Solution) -> FailureOutcome:
        """One night-before draw: for each ring (in order) and each edge (in order), pass if
        rng.random() < survival.edge(...). Draw for every edge, even after a failure in the ring."""
        raise NotImplementedError("Simulation, P1")

    def expected(self, pool: Pool, solution: Solution, n_trials: int) -> tuple[float, float]:
        """Monte Carlo over n_trials draws: (mean transplants, 95% CI half-width)."""
        raise NotImplementedError("Simulation, P1")
