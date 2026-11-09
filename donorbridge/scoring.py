"""Scorers: the weight a solver maximises for each ring.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from donorbridge.models import Cycle, Pool
from donorbridge.survival import SurvivalModel, UniformSurvival


class Scorer(ABC):
    """Assigns a weight to each ring; solvers maximise the total weight."""

    name: str

    @abstractmethod
    def weight(self, cycle: Cycle, pool: Pool) -> float:
        """Weight of one ring."""

    def total(self, cycles: Iterable[Cycle], pool: Pool) -> float:
        """Sum of weight() over `cycles`."""
        # Start at 0.0 so an empty plan totals 0.0 (a float), not the int 0.
        return sum((self.weight(cycle, pool) for cycle in cycles), 0.0)


class CountScorer(Scorer):
    """Weight = number of transplants in the ring, |c|. Ignores failure."""

    name = "count"

    def weight(self, cycle: Cycle, pool: Pool) -> float:
        """Return len(cycle)."""
        return float(len(cycle))


class ExpectedTransplantScorer(Scorer):
    """Weight = |c| * P(whole ring survives), i.e. expected transplants from the ring."""

    def __init__(self, survival: SurvivalModel | float = 1.0) -> None:
        """A float p means UniformSurvival(p). Name is "expected(p=<p>)" for uniform survival,
        else "expected(<ClassName>)"."""
        if not isinstance(survival, SurvivalModel):
            survival = UniformSurvival(survival)  # checks 0 <= p <= 1
        self.survival: SurvivalModel = survival
        if isinstance(survival, UniformSurvival):
            self.name = f"expected(p={survival.p})"
        else:
            self.name = f"expected({type(survival).__name__})"

    def weight(self, cycle: Cycle, pool: Pool) -> float:
        """Return len(cycle) * survival.cycle(pool, cycle)."""
        return len(cycle) * self.survival.cycle(pool, cycle)
