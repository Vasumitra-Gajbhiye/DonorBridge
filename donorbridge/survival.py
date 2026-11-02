"""Survival models: the chance each final crossmatch passes the night before surgery.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from donorbridge.models import Cycle, Pool


class SurvivalModel(ABC):
    """Probability that a planned donation (edge) survives the final crossmatch."""

    @abstractmethod
    def edge(self, pool: Pool, donor_family: int, patient_family: int) -> float:
        """P(crossmatch passes) for donor of `donor_family` -> patient of `patient_family`."""

    def cycle(self, pool: Pool, cycle: Cycle) -> float:
        """P(every crossmatch in the ring passes): product of edge() over cycle.edges()."""
        raise NotImplementedError("Lead, P1")


class UniformSurvival(SurvivalModel):
    """Every edge survives with the same probability p."""

    def __init__(self, p: float) -> None:
        """Store p; raise ValueError unless 0 <= p <= 1."""
        raise NotImplementedError("Lead, P1")

    def edge(self, pool: Pool, donor_family: int, patient_family: int) -> float:
        """Return p for every edge."""
        raise NotImplementedError("Lead, P1")
