"""Core data types: families, pools, rings (cycles) and solutions.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class BloodGroup(str, Enum):
    """ABO blood group of a patient or donor."""

    O = "O"
    A = "A"
    B = "B"
    AB = "AB"


class Sex(str, Enum):
    """Sex of a patient or donor."""

    F = "F"
    M = "M"


class Relation(str, Enum):
    """The donor's relation to their own patient."""

    SPOUSE = "spouse"
    OTHER = "other"


@dataclass(frozen=True)
class Family:
    """One patient plus one willing donor who cannot give to that patient.

    Attributes:
        id: Unique family id. Not necessarily 0..n-1; never use it as a list index.
        patient_blood: Patient's ABO group.
        donor_blood: Donor's ABO group.
        patient_sex: Patient's sex.
        donor_sex: Donor's sex.
        relation: Donor's relation to the patient.
        patient_pra: 0..1, chance of a positive crossmatch against a random donor.
        region: 0..3, used by the state-split experiment.
    """

    id: int
    patient_blood: BloodGroup
    donor_blood: BloodGroup
    patient_sex: Sex
    donor_sex: Sex
    relation: Relation
    patient_pra: float
    region: int = 0

    @property
    def highly_sensitised(self) -> bool:
        """True when the patient's PRA is at least 0.80."""
        raise NotImplementedError("Lead, P1")


@dataclass(frozen=True)
class Pool:
    """A set of families and the directed compatibility edges between them.

    Attributes:
        families: The families in the pool.
        edges: (i, j) means family i's donor can give to family j's patient; i != j.
        name: Optional label, e.g. "india-n100-s1".
    """

    families: tuple[Family, ...]
    edges: frozenset[tuple[int, int]]
    name: str = ""

    @property
    def n(self) -> int:
        """Number of families in the pool."""
        raise NotImplementedError("Lead, P1")

    def ids(self) -> tuple[int, ...]:
        """All family ids, sorted ascending."""
        raise NotImplementedError("Lead, P1")

    def family(self, fid: int) -> Family:
        """Return the family with id `fid` (KeyError if absent)."""
        raise NotImplementedError("Lead, P1")

    def subpool(self, ids: Iterable[int], name: str = "") -> Pool:
        """Induced sub-pool: keep only families in `ids` and the edges among them. Does not mutate self."""
        raise NotImplementedError("Lead, P1")

    def without_edges(self, drop: Iterable[tuple[int, int]]) -> Pool:
        """Return a new pool with the edges in `drop` removed. Does not mutate self."""
        raise NotImplementedError("Lead, P1")

    def to_dict(self) -> dict:
        """JSON-ready dict: {"name", "families": [...], "edges": [[i, j], ...] sorted}, enums as values."""
        raise NotImplementedError("Lead, P1")

    @classmethod
    def from_dict(cls, d: dict) -> Pool:
        """Inverse of to_dict. Ignores unknown top-level keys."""
        raise NotImplementedError("Lead, P1")

    def save_json(self, path: str | Path) -> None:
        """Write to_dict() to `path` as JSON."""
        raise NotImplementedError("Lead, P1")

    @classmethod
    def load_json(cls, path: str | Path) -> Pool:
        """Read a pool written by save_json."""
        raise NotImplementedError("Lead, P1")


@dataclass(frozen=True)
class Cycle:
    """A ring of families: family k's donor gives to family k+1's patient, and the last to the first.

    Attributes:
        families: Canonical form: rotated so the smallest id is first; direction kept.
            Cycle((1, 2, 3)) and Cycle((1, 3, 2)) are different rings.
    """

    families: tuple[int, ...]

    @classmethod
    def of(cls, seq: Sequence[int]) -> Cycle:
        """Build a ring from any rotation of `seq`, canonicalised (smallest id first, direction kept)."""
        raise NotImplementedError("Lead, P1")

    def edges(self) -> tuple[tuple[int, int], ...]:
        """The ring's edges in order: (f0, f1), (f1, f2), ..., (fk, f0)."""
        raise NotImplementedError("Lead, P1")

    def __len__(self) -> int:
        """Number of families (= transplants if the ring goes ahead)."""
        raise NotImplementedError("Lead, P1")


class InvalidSolutionError(ValueError):
    """Raised by Solution.validate when a solution breaks a rule of the problem."""


@dataclass(frozen=True)
class Solution:
    """A set of vertex-disjoint rings chosen by a solver.

    Attributes:
        cycles: The chosen rings.
        solver: Registry name of the solver that produced it.
        objective: Total weight under the solver's scorer.
        runtime_s: Wall-clock time of the solve, in seconds.
        optimal: True = proven optimal; False = heuristic or timed out; None = unknown.
        stats: Solver-specific diagnostics (not compared).
    """

    cycles: tuple[Cycle, ...]
    solver: str
    objective: float
    runtime_s: float
    optimal: bool | None
    stats: dict = field(default_factory=dict, compare=False)

    @property
    def transplants(self) -> int:
        """Sum of ring sizes."""
        raise NotImplementedError("Lead, P1")

    def covered(self) -> frozenset[int]:
        """Ids of every family in some chosen ring."""
        raise NotImplementedError("Lead, P1")

    def validate(self, pool: Pool, max_cycle_len: int) -> None:
        """Raise InvalidSolutionError if a ring is too long/short, uses a missing edge or unknown id,
        or two rings share a family. The message names the offending ring or family."""
        raise NotImplementedError("Lead, P1")
