"""Oracles: external benchmarks and cross-checks that prove the exact solvers right.

Owner: Lead
Implemented in: P2
"""

from donorbridge.oracle.crosscheck import CrosscheckReport, crosscheck
from donorbridge.oracle.glasgow import list_instances, load_glasgow
from donorbridge.oracle.kep_oracle import kep_optimum

__all__ = ["CrosscheckReport", "crosscheck", "kep_optimum", "list_instances", "load_glasgow"]
