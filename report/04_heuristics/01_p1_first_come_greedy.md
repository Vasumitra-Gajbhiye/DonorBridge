# 01 · P1 first-come and greedy (H1.1–H1.4)

Date: 2026-11-05

## What was asked

Heuristics P1 work: `FirstComeSolver` and `GreedySolver` (`_solve` only), plus `tests/unit/test_first_come.py` and `tests/unit/test_greedy.py`. The heuristics owner asked the AI to write the code to study from. On 2026-11-09 they asked the AI to put the files into the repo directly instead of typing them by hand.

## What was done

- **`solvers/first_come.py`:** sorts rings by `(max id, len, families)` and takes each ring that doesn't share a family with one already taken. It ignores the scorer on purpose. Stats: `rings_considered`, `rings_taken`.
- **`solvers/greedy.py`:** sorts by `(-weight, conflicts, families)` using `self.weights`, never `len`, then takes each ring that still fits. A module-level helper, `conflict_counts(cycles)`, counts the distinct other rings that share a family with each ring. Stats match first-come's.
- **Unit tests:**
  - 7 for first-come: the trap, ignoring weights, the arrival tie-break, non-contiguous ids, empty inputs, stats and repeatability, and not mutating the input list.
  - 8 for greedy: the trap gives 3, ring_vs_swap under count / p=0.6 / p=0.9, conflict counts, a neighbour sharing two families counted once, the conflict tie-break, the families tie-break, empty inputs, stats and repeatability.
  - Rings are passed in through `cycles=`, so neither file depends on the cycle finder.

## Deviations and things to note

- **First-come scores 4 on greedy_trap, not 3.** By arrival order, (1,2) is taken before (0,1,2), so first-come happens to hit the optimum. The tests assert 4. Only greedy is expected to fall into the trap.
- **The conflict count is not O(total ring size).** Prompt H1.1 suggests it can be. A plain sum over a family → rings index counts a neighbour twice when it shares two families. Counting distinct neighbours needs a set union, which costs O(Σ over rings of the rings at its families). It uses ring positions instead of `Cycle` objects because hashing `Cycle` objects took 3.2 s on a pool of 200 (23,143 rings).
- **Rings of weight 0 are still taken.** At p=0, greedy takes zero-weight rings at the end, as the rule "take each ring that is disjoint" says. The objective is unaffected.
- **Not yet tested against the real contract.** `models.py`, `scoring.py`, `survival.py` and `solvers/base.py` were still stubs on `main` (665a905). The code was checked in a throwaway copy with test-only stand-ins for those stubs and for `find_cycles`:
  - 15 of 15 unit tests pass.
  - `test_p1_heuristics_greedy_on_fixtures` and `test_p1_e2e_solver_names_resolve` pass, also with `--gate`.
  - `test_p1_heuristics_first_come_valid` skips at the generator stub, after its fixture part has passed.
- **Test rings are built inside functions** (`trap_rings()`, `ring_vs_swap_rings()`), not as module constants. The first version built them at import time. While `Cycle.of` is a stub, that crashed pytest's collection step, which the conftest skip hook doesn't cover: CI showed 2 errors instead of skips. With the functions, the tests skip cleanly on the current `main` (`5 passed, 33 skipped` for the whole suite).
- **Earlier cross-check:** the same logic matched brute force on 1,200 random pool/scorer pairs. Greedy and first-come never beat the optimum.

## Next steps

1. Once the lead's L1.2–L1.4 are merged, run `uv run pytest tests/unit/test_first_come.py tests/unit/test_greedy.py tests/integration/test_phase1.py -k "heuristics or first_come or greedy" -rs`.
2. Open the PR for both solvers and their tests by Thu 5 Nov, 6 pm.
3. P2, after `phase-1-done`: `LocalSearchSolver`, then branch and bound v1.
