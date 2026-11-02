"""Fairness-weighted scorer: extra weight for transplants to a disadvantaged group.

Owner: Simulation
Implemented in: P3
"""

from __future__ import annotations

from donorbridge.models import Cycle, Pool
from donorbridge.scoring import ExpectedTransplantScorer
from donorbridge.survival import SurvivalModel


class FairnessScorer(ExpectedTransplantScorer):
    """weight(c) = survival.cycle(pool, c) * sum over v in c of (1 + beta * [v in group]).
    With beta = 0 it equals ExpectedTransplantScorer."""

    def __init__(
        self,
        survival: SurvivalModel | float = 1.0,
        beta: float = 0.0,
        group: str = "highly_sensitised",
    ) -> None:
        """group is "highly_sensitised" or "female" (ValueError otherwise)."""
        raise NotImplementedError("Simulation, P3")

    def weight(self, cycle: Cycle, pool: Pool) -> float:
        """Survival-discounted, group-boosted transplant count of the ring."""
        raise NotImplementedError("Simulation, P3")
