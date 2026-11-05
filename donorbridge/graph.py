"""Compatibility graph: adjacency view of a Pool.

Owner: Matching
Implemented in: P1
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from donorbridge.models import Pool

if TYPE_CHECKING:
    import networkx as nx


class CompatibilityGraph:
    """Directed graph over family ids; edge i -> j means i's donor can give to j's patient."""

    def __init__(self, pool: Pool) -> None:
        """Build successor/predecessor maps from pool.edges (ids are not indices)."""
        self.pool = pool
        self.gives_to = {fid: [] for fid in pool.ids()}       # i -> families i's donor can give to
        self.receives_from = {fid: [] for fid in pool.ids()}  # j -> families whose donor can give to j
        for i, j in pool.edges:
            self.gives_to[i].append(j)
            self.receives_from[j].append(i)
        
        raise NotImplementedError("Matching, P1")

    def nodes(self) -> tuple[int, ...]:
        """All family ids, sorted."""
        raise NotImplementedError("Matching, P1")

    def successors(self, fid: int) -> tuple[int, ...]:
        """Families whose patient fid's donor can give to, sorted."""
        raise NotImplementedError("Matching, P1")

    def predecessors(self, fid: int) -> tuple[int, ...]:
        """Families whose donor can give to fid's patient, sorted."""
        raise NotImplementedError("Matching, P1")

    def has_edge(self, i: int, j: int) -> bool:
        """True if (i, j) is an edge."""
        raise NotImplementedError("Matching, P1")

    def mutual_pairs(self) -> list[tuple[int, int]]:
        """Every (i, j) with i < j and edges in both directions (the possible 2-swaps)."""
        raise NotImplementedError("Matching, P1")

    def to_networkx(self) -> nx.DiGraph:
        """The same graph as a networkx DiGraph (for cross-checks and plots)."""
        raise NotImplementedError("Matching, P1")
