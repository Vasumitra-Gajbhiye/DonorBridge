"""Saidman-style pool generator: sample incompatible families, then draw compatibility edges.

Owner: Generator
Implemented in: P1
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from donorbridge.generator.calibration import INDIA, Calibration
from donorbridge.models import Pool


@dataclass(frozen=True)
class GenerationReport:
    """What happened while generating one pool (field names agreed in the generator playbook).

    Attributes:
        pairs_sampled: Every patient-donor pair drawn (= n + rejected_compatible).
        rejected_compatible: Directly compatible pairs, which never enter the pool.
        xm_spouse_female_tested: Wife <- husband pairs sampled.
        xm_spouse_female_positive: ...of which had a positive crossmatch.
        xm_unrelated_tested: Unrelated pairs sampled.
        xm_unrelated_positive: ...of which had a positive crossmatch.
        female_patients_sampled: Female patients drawn.
        female_hs_sampled: ...of which were highly sensitised.
    """

    pairs_sampled: int
    rejected_compatible: int
    xm_spouse_female_tested: int
    xm_spouse_female_positive: int
    xm_unrelated_tested: int
    xm_unrelated_positive: int
    female_patients_sampled: int
    female_hs_sampled: int


class PoolGenerator(ABC):
    """Produces random pools. Every random call is driven by the `seed` argument (no global state)."""

    @abstractmethod
    def generate_with_report(self, n: int, seed: int) -> tuple[Pool, GenerationReport]:
        """Generate a pool of exactly n incompatible families, plus a report of the sampling."""

    def generate(self, n: int, seed: int) -> Pool:
        """generate_with_report(n, seed), keeping only the pool."""
        raise NotImplementedError("Generator, P1")

    def generate_many(self, n_pools: int, n: int, seed: int) -> list[Pool]:
        """n_pools pools of size n, using seeds seed, seed+1, ..."""
        raise NotImplementedError("Generator, P1")


class SaidmanGenerator(PoolGenerator):
    """Saidman et al. (2006) generator with a swappable calibration (India or US)."""

    def __init__(self, calibration: Calibration = INDIA, **overrides: Any) -> None:
        """Use `calibration`, with any field replaced by `overrides` (e.g. female_hs_share=0.3).
        Unknown override names raise ValueError."""
        raise NotImplementedError("Generator, P1")

    def generate_with_report(self, n: int, seed: int) -> tuple[Pool, GenerationReport]:
        """Sample patient-donor pairs until n are incompatible (ABO or positive crossmatch, spouse
        rule applied), then draw edge i -> j if ABO-compatible and the crossmatch is negative."""
        raise NotImplementedError("Generator, P1")


def make_generator(preset: str = "india", **overrides: Any) -> SaidmanGenerator:
    """SaidmanGenerator for preset "india" or "us" (ValueError otherwise), with overrides."""
    raise NotImplementedError("Generator, P1")
