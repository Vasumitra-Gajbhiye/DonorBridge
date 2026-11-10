# 04 · P2 and P3: local search and branch and bound (H2.1–H2.3, H3.1–H3.4)

Date: 2026-11-11

## What was asked

The heuristics owner asked the AI to do the next two phases in one go, "properly with highest precision":
- **P2:** `LocalSearchSolver` and branch and bound v1.
- **P3:** branch and bound v2, with its bound proof.
- Their unit tests, and a check against the lead's P2/P3 integration specs.

`phase-1-done` has not been tagged and `tests/integration/test_phase2.py` doesn't exist yet. This work was done ahead of the gate at the owner's request.

## What was done

- **`solvers/local_search.py`:** starts from greedy, then repeatedly applies the single best move. The moves are ADD a free ring with w > 0, or swap one chosen ring for the best set of at most 2 rings that fit. Helper `best_one_or_two`. Time-limited, with stats `passes`, `moves`, `timed_out`.
- **`solvers/branch_bound.py`:** one class with three versions, selected by the `version` class attribute.
  - **v1:** include/exclude over rings sorted heaviest first. The exclude branch is a loop step, so recursion stays shallow. Starts from greedy.
  - **v2:** the playbook's design. Branch on the family with the fewest available rings, bound = value + each family's best share. Starts from local search.
  - **v3 (default):** v2 plus a toll (Lagrangian) bound, rounded down when all weights are whole numbers.
  - All versions: one deadline for the whole run; negative rings dropped; tolerance scaled to the weights.
  - Stats: `version`, `nodes`, `pruned`, `timed_out`, `time_to_best`, plus `root_bound` for v2 and v3.
- **Tests:** `tests/unit/test_local_search.py` (10) and `tests/unit/test_branch_bound.py` (24, of which 3 are slow). The unit tests run in about 1 s.
- **`docs/design/heuristics.md`:** v3 section with its proof, measurements, test list, modules and decisions 7–8.

## Deviations and things to note

1. **v3 is the default, not the playbook's v2.** This needs the lead's OK, so tell the lead before merging.
   - On 200 pools of 30 at p = 0.7, v2's slowest 1% took 52.5 s and its worst 59 s. v3's took 1.65 s and 23 s.
   - Under count weights: 7.8 s → 0.03 s for the slowest 1%, and 17.9 s → 0.96 s worst.
   - v2 is still available as `solver.version = 2`.
2. **Why v2 struggles:** on the hard pools, the LP relaxation is almost exactly the optimum, but v2's share bound was 20–50% higher. The toll bound starts from v2's bound and moves towards the LP value. It is valid for any tolls ≥ 0 (proof in the design file), so it can never cut off the optimum.
3. **A first attempt, a "family price" bound, was replaced.** It cut timeouts at n = 50 but didn't help the hardest pools of 30.
4. **Tests use pools that imitate blood groups and PRA,** because the generator and `find_cycles` are still stubs on `main`. Unit tests use their own small ring finder and brute force. Re-run everything on real India pools once the generator merges.
5. **One test assumption was wrong and was fixed:** n = 200 doesn't always time out. An easy random pool was solved and proved optimal in 0.39 s. So the test now checks that `optimal` matches "didn't time out" and that the run stays under 1.5 s. The lead's integration test asserts `optimal is False` at n = 200 India. That holds on realistic pools (verified on a 23,143-ring pool), but would fail on an easy one.
6. **The time limit doesn't cover greedy's own start-up,** which takes about 0.24 s at n = 200. Everything after it is timed.
7. **Hard instances remain.** The worst pool of 30 still takes 15–23 s with v3. If the gate's crosscheck gives B&B a time limit below that, a rare pool of 30 would be reported as `optimal=False`, not as a mismatch.

## Checks

- `uv run pytest`: 159 passed, 17 skipped (stubs and slow tests), 0 failed. The slow tests pass with `--run-slow`.
- **Against an independent ILP (PuLP 2.9.0 / CBC), following the lead's specs:**
  - first-come, greedy and local search ≤ ILP, and local search ≥ greedy: 20 pools × 50, both scorers;
  - B&B v1 = ILP with `optimal=True`: 20 pools × 15;
  - B&B v2 and v3 = ILP: 50 pools each of 20 and 30, count and p = 0.7, no time limit;
  - B&B = ILP at L = 2 and L = 4: 20 pools × 12 each;
  - n = 200 with a 1 s limit: 1.29 s (v1), 1.02 s (v2), 1.03 s (v3).
  - **0 failures.**
- **Against brute force:** 1,200 pool/scorer pairs for every version, including arbitrary and zero weights.

## Next steps

1. Ask the lead to approve v3 as the default bound (deviation 1).
2. When `tests/integration/test_phase2.py` and `test_phase3.py` land, merge `main` and run `-k heuristics`.
3. Once the generator and `find_cycles` merge, re-run the timing tables on real India pools.
4. P4: the `optimality_gap` and `ring_length` specs.
