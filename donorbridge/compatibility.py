"""ABO blood-group compatibility.

Owner: Generator
Implemented in: P1
"""

from __future__ import annotations

from donorbridge.models import BloodGroup


def blood_compatible(donor: BloodGroup, patient: BloodGroup) -> bool:
    """True if a donor of group `donor` can give to a patient of group `patient` (ABO rules only:
    O gives to all, AB receives from all, A->A/AB, B->B/AB)."""
    raise NotImplementedError("Generator, P1")
