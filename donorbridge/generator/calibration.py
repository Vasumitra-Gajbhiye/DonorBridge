"""Calibration presets: the real-world statistics that drive the pool generator.

Owner: Generator
Implemented in: P1
"""

from __future__ import annotations

from dataclasses import dataclass

from donorbridge.models import BloodGroup


@dataclass(frozen=True)
class Calibration:
    """Parameters of one population (field names agreed in the generator playbook).

    Attributes:
        name: Preset name, e.g. "india".
        blood_freq: Population ABO shares as (group, share); shares sum to 1.
        patient_female_share: Share of patients who are female.
        spouse_share_female_patient: P(donor is husband | female patient).
        spouse_share_male_patient: P(donor is wife | male patient).
        pra_bands: (PRA value, probability) pairs; probabilities sum to 1.
        female_hs_share: P(highly sensitised | female patient); None = use pra_bands.
        target_xm_spouse: Target positive-crossmatch rate, wife <- husband.
        target_xm_unrelated: Target positive-crossmatch rate, unrelated.
        n_regions: Number of regions families are spread over.
        sources: Citations for every number above.
    """

    name: str
    blood_freq: tuple[tuple[BloodGroup, float], ...]
    patient_female_share: float
    spouse_share_female_patient: float
    spouse_share_male_patient: float
    pra_bands: tuple[tuple[float, float], ...]
    female_hs_share: float | None = None
    target_xm_spouse: float = 0.33
    target_xm_unrelated: float = 0.11
    n_regions: int = 4
    sources: tuple[str, ...] = ()


# PLACEHOLDERS so the package imports. NaN/empty on purpose: any use fails loudly or yields NaN.
# Owner: Generator, real sourced values filled in P1 (G1.1).
_NAN = float("nan")

INDIA: Calibration = Calibration(
    name="india",
    blood_freq=(),
    patient_female_share=_NAN,
    spouse_share_female_patient=_NAN,
    spouse_share_male_patient=_NAN,
    pra_bands=(),
)

US: Calibration = Calibration(
    name="us",
    blood_freq=(),
    patient_female_share=_NAN,
    spouse_share_female_patient=_NAN,
    spouse_share_male_patient=_NAN,
    pra_bands=(),
)
