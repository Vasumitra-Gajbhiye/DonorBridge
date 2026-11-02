"""The experiment engine: ONE function runs every experiment and writes one CSV format.

Owner: Simulation
Implemented in: P2
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass(frozen=True)
class Setting:
    """One configuration to run on every pool of an experiment. Every field has a default."""

    label: str = ""               # e.g. "two_way"; copied into the CSV
    preset: str = "india"
    n: int = 100
    overrides: tuple[tuple[str, float], ...] = ()   # generator overrides, e.g. (("female_hs_share", 0.3),)
    split_regions: bool = False   # solve each region's sub-pool separately and add up
    solver: str | None = "ilp"    # None = only enumerate rings (timing / ring counts)
    max_len: int = 3
    scorer: str = "expected"      # "count" | "expected" | "fair"
    p: float = 1.0                # survival: used by the scorer AND to evaluate every plan
    survival: str = "uniform"     # "uniform" | "sensitisation"
    beta: float = 0.0             # fair scorer only
    group: str = "highly_sensitised"   # fair scorer only: "highly_sensitised" | "female"
    time_limit_s: float | None = None
    resolve_trials: int = 0       # > 0: mean of NightBeforeSimulator over this many draws


@dataclass(frozen=True)
class GridSpec:
    """A named experiment: settings x pools. Output is results/<name>.csv."""

    name: str                     # output is results/<name>.csv
    settings: tuple[Setting, ...]
    n_pools: int = 20
    quick_settings: tuple[Setting, ...] = ()   # empty = reuse settings with n capped at 40
    quick_n_pools: int = 3


# EVERY experiment CSV has exactly these columns, one row per (setting, pool).
# expected_transplants = ExpectedTransplantScorer(survival at p).total(plan), whatever the solver's scorer.
ROW_COLUMNS: tuple[str, ...] = (
    "experiment",
    "label",
    "preset",
    "n",
    "seed",
    "overrides",
    "split_regions",
    "solver",
    "max_len",
    "scorer",
    "p",
    "survival",
    "beta",
    "group",
    "objective",
    "transplants",
    "expected_transplants",
    "optimal",
    "runtime_s",
    "enum_s",
    "rings_2",
    "rings_3",
    "rings_4",
    "hs_matched_share",
    "female_matched_share",
    "male_matched_share",
    "resolve_mean",
)


def run_grid(
    spec: GridSpec,
    out_dir: Path = Path("results"),
    quick: bool = False,
    seed: int = 2026,
    workers: int = 0,
) -> pd.DataFrame:
    """Run every setting of `spec` on its pools and write out_dir/<spec.name>.csv.

    Pool i of every setting uses seed + i (paired comparisons). Rings are found once per pool and
    passed to every solve via cycles=. Pools run in parallel (workers=0 -> os.cpu_count(),
    1 -> serial, same output). Returns the DataFrame with columns ROW_COLUMNS.
    """
    raise NotImplementedError("Simulation, P2")
