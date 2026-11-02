"""Survival models that depend on the patient (beyond the uniform model).

Owner: Generator
Implemented in: P3
"""

from __future__ import annotations

from donorbridge.models import Pool
from donorbridge.survival import SurvivalModel


class SensitisationSurvival(SurvivalModel):
    """Crossmatch survival depends on whether the receiving patient is highly sensitised."""

    def __init__(self, p_low: float, p_high: float) -> None:
        """p_low: survival for patients who are not highly sensitised; p_high: for highly
        sensitised patients. Both must lie in [0, 1]."""
        raise NotImplementedError("Generator, P3")

    def edge(self, pool: Pool, donor_family: int, patient_family: int) -> float:
        """p_high if patient_family's patient is highly sensitised, else p_low."""
        raise NotImplementedError("Generator, P3")
