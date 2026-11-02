"""Scorers: the weight a solver maximises for each ring.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from donorbridge.models import Cycle, Pool
from donorbridge.survival import SurvivalModel


class Scorer(ABC):
    """Assigns a weight to each ring; solvers maximise the total weight."""

    name: str

    @abstractmethod
    def weight(self, cycle: Cycle, pool: Pool) -> float:
        """Weight of one ring."""

    def total(self, cycles: Iterable[Cycle], pool: Pool) -> float:
        """Sum of weight() over `cycles`."""
        raise NotImplementedError("Lead, P1")


class CountScorer(Scorer):
    """Weight = number of transplants in the ring, |c|. Ignores failure."""

    name = "count"

    def weight(self, cycle: Cycle, pool: Pool) -> float:
        """Return len(cycle)."""
        raise NotImplementedError("Lead, P1")


class ExpectedTransplantScorer(Scorer):
    """Weight = |c| * P(whole ring survives), i.e. expected transplants from the ring."""

    def __init__(self, survival: SurvivalModel | float = 1.0) -> None:
        """A float p means UniformSurvival(p). Name is "expected(p=<p>)" for uniform survival,
        else "expected(<ClassName>)"."""
        raise NotImplementedError("Lead, P1")

    def weight(self, cycle: Cycle, pool: Pool) -> float:
        """Return len(cycle) * survival.cycle(pool, cycle)."""
        raise NotImplementedError("Lead, P1")
