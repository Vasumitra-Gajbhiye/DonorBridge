"""Presentation demos, keyed by name for `python -m donorbridge demo`.

Owner: Lead (re-exports only; the module belongs to Matching)
Implemented in: P4
"""

from donorbridge.demos.scripts import DEMOS, demo_edge, demo_india, demo_small

__all__ = ["DEMOS", "demo_edge", "demo_india", "demo_small"]
