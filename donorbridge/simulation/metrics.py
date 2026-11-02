"""Per-pool outcome metrics: transplants, expected transplants and who gets matched.

Owner: Simulation
Implemented in: P1
"""

from __future__ import annotations

from dataclasses import dataclass

from donorbridge.models import Pool, Solution
from donorbridge.survival import SurvivalModel


@dataclass(frozen=True)
class PoolMetrics:
    """Outcome of one plan on one pool (field names agreed in the simulation playbook).

    Attributes:
        n_families: Families in the pool.
        transplants: Sum of ring sizes in the plan.
        expected_transplants: Sum of |c| * survival.cycle(pool, c).
        rings_by_len: Ring length -> number of chosen rings of that length.
        hs_total, hs_matched: Highly sensitised patients in the pool / in a chosen ring.
        female_total, female_matched: Female patients in the pool / matched.
        male_total, male_matched: Male patients in the pool / matched.
        by_blood: Patient blood group value -> (matched, total).
    """

    n_families: int
    transplants: int
    expected_transplants: float
    rings_by_len: dict[int, int]
    hs_total: int
    hs_matched: int
    female_total: int
    female_matched: int
    male_total: int
    male_matched: int
    by_blood: dict[str, tuple[int, int]]

    @property
    def hs_matched_share(self) -> float:
        """hs_matched / hs_total, or 0.0 when hs_total is 0."""
        raise NotImplementedError("Simulation, P1")

    @property
    def female_matched_share(self) -> float:
        """female_matched / female_total, or 0.0 when female_total is 0."""
        raise NotImplementedError("Simulation, P1")

    @property
    def male_matched_share(self) -> float:
        """male_matched / male_total, or 0.0 when male_total is 0."""
        raise NotImplementedError("Simulation, P1")


def compute_metrics(pool: Pool, solution: Solution, survival: SurvivalModel | None = None) -> PoolMetrics:
    """Tabulate the plan's outcome. survival defaults to UniformSurvival(1.0)."""
    raise NotImplementedError("Simulation, P1")
