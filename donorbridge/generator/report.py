"""Calibration report: in-pool statistics for a preset, to check the generator against sources.

Owner: Generator
Implemented in: P2
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def calibration_report(preset: str, n_pools: int, n: int, seed: int) -> pd.DataFrame:
    """Generate n_pools pools of size n (seeds seed, seed+1, ...) and tabulate in-pool statistics:
    patient/donor ABO mix, % female patients, % highly sensitised, edge density, and mean ring
    counts for L=2 and L=3."""
    raise NotImplementedError("Generator, P2")
