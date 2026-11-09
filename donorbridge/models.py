"""Core data types: families, pools, rings (cycles) and solutions.

Owner: Lead
Implemented in: P1
"""

from __future__ import annotations

import json
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
        return self.patient_pra >= 0.80


def _family_to_dict(family: Family) -> dict:
    """One family as a JSON-ready dict: every field, enums written as their string value."""
    return {
        "id": family.id,
        "patient_blood": family.patient_blood.value,
        "donor_blood": family.donor_blood.value,
        "patient_sex": family.patient_sex.value,
        "donor_sex": family.donor_sex.value,
        "relation": family.relation.value,
        "patient_pra": family.patient_pra,
        "region": family.region,
    }


def _family_from_dict(d: dict) -> Family:
    """Inverse of _family_to_dict. A missing "region" defaults to 0."""
    return Family(
        id=int(d["id"]),
        patient_blood=BloodGroup(d["patient_blood"]),
        donor_blood=BloodGroup(d["donor_blood"]),
        patient_sex=Sex(d["patient_sex"]),
        donor_sex=Sex(d["donor_sex"]),
        relation=Relation(d["relation"]),
        patient_pra=float(d["patient_pra"]),
        region=int(d.get("region", 0)),
    )


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

    def __post_init__(self) -> None:
        """Check ids are unique and every edge joins two different families of this pool.

        Also builds the private id -> Family lookup used by family(). The dataclass is frozen,
        so the attribute is set with object.__setattr__. It is not a dataclass field, so it
        plays no part in == or hashing.
        """
        by_id: dict[int, Family] = {}
        for fam in self.families:
            if fam.id in by_id:
                raise ValueError(f"duplicate family id {fam.id} in pool {self.name!r}")
            by_id[fam.id] = fam

        for i, j in self.edges:
            if i == j:
                raise ValueError(f"edge ({i}, {j}) is a self-loop in pool {self.name!r}")
            for fid in (i, j):
                if fid not in by_id:
                    raise ValueError(
                        f"edge ({i}, {j}) uses family id {fid}, which is not in pool {self.name!r}"
                    )

        object.__setattr__(self, "_by_id", by_id)

    @property
    def n(self) -> int:
        """Number of families in the pool."""
        return len(self.families)

    def ids(self) -> tuple[int, ...]:
        """All family ids, sorted ascending."""
        return tuple(sorted(self._by_id))

    def family(self, fid: int) -> Family:
        """Return the family with id `fid` (KeyError if absent)."""
        try:
            return self._by_id[fid]
        except KeyError:
            raise KeyError(f"no family with id {fid} in pool {self.name!r}") from None

    def subpool(self, ids: Iterable[int], name: str = "") -> Pool:
        """Induced sub-pool: keep only families in `ids` and the edges among them. Does not mutate self.

        Raises ValueError if `ids` contains an id that is not in this pool.
        """
        keep = set(ids)
        unknown = keep - set(self._by_id)
        if unknown:
            raise ValueError(f"subpool: ids {sorted(unknown)} are not in pool {self.name!r}")
        families = tuple(fam for fam in self.families if fam.id in keep)
        edges = frozenset((i, j) for i, j in self.edges if i in keep and j in keep)
        return Pool(families, edges, name)

    def without_edges(self, drop: Iterable[tuple[int, int]]) -> Pool:
        """Return a new pool with the edges in `drop` removed. Does not mutate self."""
        return Pool(self.families, self.edges - frozenset(drop), self.name)

    def to_dict(self) -> dict:
        """JSON-ready dict: {"name", "families": [...], "edges": [[i, j], ...] sorted}, enums as values."""
        return {
            "name": self.name,
            "families": [_family_to_dict(fam) for fam in self.families],
            "edges": [[i, j] for i, j in sorted(self.edges)],
        }

    @classmethod
    def from_dict(cls, d: dict) -> Pool:
        """Inverse of to_dict. Ignores unknown top-level keys."""
        families = tuple(_family_from_dict(f) for f in d["families"])
        edges = frozenset((int(i), int(j)) for i, j in d["edges"])
        return cls(families, edges, d.get("name", ""))

    def save_json(self, path: str | Path) -> None:
        """Write to_dict() to `path` as JSON."""
        text = json.dumps(self.to_dict(), indent=2)
        Path(path).write_text(text + "\n", encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> Pool:
        """Read a pool written by save_json."""
        text = Path(path).read_text(encoding="utf-8")
        return cls.from_dict(json.loads(text))


def _check_ring(families: tuple[int, ...]) -> None:
    """Raise ValueError unless `families` has at least 2 ids and no id twice."""
    if len(families) < 2:
        raise ValueError(f"a ring needs at least 2 families, got {families}")
    if len(set(families)) != len(families):
        raise ValueError(f"a ring cannot visit a family twice, got {families}")


@dataclass(frozen=True)
class Cycle:
    """A ring of families: family k's donor gives to family k+1's patient, and the last to the first.

    Attributes:
        families: Canonical form: rotated so the smallest id is first; direction kept.
            Cycle((1, 2, 3)) and Cycle((1, 3, 2)) are different rings.
    """

    families: tuple[int, ...]

    def __post_init__(self) -> None:
        """Reject rings that are too short, repeat a family, or are not in canonical form."""
        _check_ring(self.families)
        if self.families[0] != min(self.families):
            raise ValueError(
                f"ring {self.families} is not in canonical form (smallest id first); "
                "build it with Cycle.of"
            )

    @classmethod
    def of(cls, seq: Sequence[int]) -> Cycle:
        """Build a ring from any rotation of `seq`, canonicalised (smallest id first, direction kept)."""
        families = tuple(seq)
        _check_ring(families)
        start = families.index(min(families))
        return cls(families[start:] + families[:start])

    def edges(self) -> tuple[tuple[int, int], ...]:
        """The ring's edges in order: (f0, f1), (f1, f2), ..., (fk, f0)."""
        f = self.families
        n = len(f)
        return tuple((f[k], f[(k + 1) % n]) for k in range(n))

    def __len__(self) -> int:
        """Number of families (= transplants if the ring goes ahead)."""
        return len(self.families)


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
        return sum(len(c) for c in self.cycles)

    def covered(self) -> frozenset[int]:
        """Ids of every family in some chosen ring."""
        return frozenset(fid for c in self.cycles for fid in c.families)

    def validate(self, pool: Pool, max_cycle_len: int) -> None:
        """Raise InvalidSolutionError if a ring is too long/short, uses a missing edge or unknown id,
        or two rings share a family. The message names the offending ring or family."""
        known = set(pool.ids())
        owner: dict[int, Cycle] = {}  # family id -> the ring that already uses it
        for cycle in self.cycles:
            ring = cycle.families
            if not 2 <= len(ring) <= max_cycle_len:
                raise InvalidSolutionError(
                    f"ring {ring} has {len(ring)} families; allowed 2..{max_cycle_len}"
                )
            for fid in ring:
                if fid not in known:
                    raise InvalidSolutionError(
                        f"ring {ring} uses family {fid}, which is not in pool {pool.name!r}"
                    )
            for i, j in cycle.edges():
                if (i, j) not in pool.edges:
                    raise InvalidSolutionError(
                        f"ring {ring} needs edge {i} -> {j}, which is not in the pool"
                    )
            for fid in ring:
                if fid in owner:
                    raise InvalidSolutionError(
                        f"family {fid} is in two rings: {owner[fid].families} and {ring}"
                    )
                owner[fid] = cycle
