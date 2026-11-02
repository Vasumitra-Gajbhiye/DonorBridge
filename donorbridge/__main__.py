"""Command-line interface: python -m donorbridge {run,sweep,bench,results,demo}.

Owner: Lead
Implemented in: P2 (run), P3 (bench), P4 (sweep, results, demo)
"""

from __future__ import annotations

import argparse
import sys

# Subcommand -> phase in which it gets implemented.
COMMANDS: dict[str, tuple[str, str]] = {
    "run": ("P2", "solve one pool and print the plan"),
    "sweep": ("P4", "run the survival sweep experiment"),
    "bench": ("P3", "cross-check solvers on random pools"),
    "results": ("P4", "run every experiment, the answer and the figures"),
    "demo": ("P4", "run a presentation demo"),
}


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch. Every subcommand is a stub for now and returns exit code 2."""
    parser = argparse.ArgumentParser(prog="python -m donorbridge")
    sub = parser.add_subparsers(dest="command", required=True)
    for command, (_, help_text) in COMMANDS.items():
        sub.add_parser(command, help=help_text)
    args = parser.parse_args(argv)
    phase = COMMANDS[args.command][0]
    print(f"not implemented yet ({phase})")
    return 2


if __name__ == "__main__":
    sys.exit(main())
