"""Survival models: the chance each final crossmatch passes the night before surgery.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from donorbridge.models import Cycle, Pool


class SurvivalModel(ABC):
    """Probability that a planned donation (edge) survives the final crossmatch."""

    @abstractmethod
    def edge(self, pool: Pool, donor_family: int, patient_family: int) -> float:
        """P(crossmatch passes) for donor of `donor_family` -> patient of `patient_family`."""

    def cycle(self, pool: Pool, cycle: Cycle) -> float:
        """P(every crossmatch in the ring passes): product of edge() over cycle.edges()."""
        # The draws are independent, so the ring survives with the product of its edge chances.
        # Going through edge() means subclasses only need to define edge().
        return math.prod(self.edge(pool, donor, patient) for donor, patient in cycle.edges())


class UniformSurvival(SurvivalModel):
    """Every edge survives with the same probability p."""

    def __init__(self, p: float) -> None:
        """Store p; raise ValueError unless 0 <= p <= 1."""
        if not 0 <= p <= 1:  # also False for NaN, so NaN is rejected
            raise ValueError(f"p must be in [0, 1], got {p}")
        self.p: float = float(p)  # float, so UniformSurvival(1) and UniformSurvival(1.0) match

    def edge(self, pool: Pool, donor_family: int, patient_family: int) -> float:
        """Return p for every edge."""
        return self.p
