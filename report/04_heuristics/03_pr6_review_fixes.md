# 03 · PR #6 review: CodeRabbit findings

Date: 2026-11-10

## What was asked

Go through the review comments on PR #6 and do what is needed. All comments came from the CodeRabbit bot, and each one was marked "unverified finding". Every finding was reproduced on the real code before anything was changed.

## Findings and what was done

| # | Finding | Checked? | Action |
| --- | --- | --- | --- |
| 1 | Report 01's "next steps" were stale (open the PR by Thu 5 Nov) | Valid | Marked steps 1–2 done, with dates. |
| 2 | Pre-merge check: docstring coverage | Checked, skipped | Both solver files have docstrings on every function. The missing ones are on `test_*` functions, which follow the lead's own test style: 4 of 32 tests in `test_models.py` and 11 of 40 in `test_solver_base.py` have them. Test names describe the behaviour. This is CodeRabbit's check, not CI. |
| 3 | A fixed 1e-9 tolerance can report a non-optimal plan as optimal | **Reproduced** | With every family worth 1e-10 on `greedy_trap`, B&B v1 and v2 returned 3e-10 with `optimal=True`, but the optimum is 4e-10. Fix: tolerance = 1e-9 × the heaviest ring weight, in B&B and in local search. Both versions now return 4e-10. |
| 4 | Negative weights break the bound | **Reproduced** | With rings worth 10 and −20, v1 and v2 returned −10 with `optimal=True`, but the optimum is 10. Fix: B&B drops negative rings before searching (they are never in an optimal plan), and greedy stops at the first one. Both versions now return 10. New unit test: `test_never_takes_a_ring_with_negative_weight`. |
| 5 | B&B's time limit didn't cover building the starting solution | **Reproduced** | At n = 200, a 0.5 s limit took 0.76 s. Fix: one deadline, local search gets only the time left, and B&B returns at once if it's already past. Now 0.56 s for 0.5 s, and 1.02–1.21 s for 1.0 s (the playbook allows 1.5 s). |

## Where the changes are

- **In this PR:**
  - `donorbridge/solvers/greedy.py`: stops at negative-weight rings.
  - `tests/unit/test_greedy.py`: one new test.
  - `docs/design/heuristics.md`: pseudocode and decisions 4, 4b and 6.
  - Report 01: next steps.
- **Not in this PR:** findings 3–5 concern local search and B&B, which are P2 code. The fixes are in the tested P2 draft and ship with the P2 PR after `phase-1-done`.

## Checks after the fixes

- `uv run pytest`: 128 passed, 14 skipped, 0 failed.
- P2 draft on the lead's real models:
  - v1 and v2 agree with brute force on 1,200 pool/scorer pairs (count, p = 0.6, p = 0.9, arbitrary weights including 0).
  - They agree with the ILP (PuLP/CBC) on 50 pools of 20 and 30, both scorers, with 0 wrong answers.
  - All fixture traces are unchanged (v1 on the trap: 7 nodes and 2 prunes; local search stuck at 6 on pool_8).

## Notes for the lead

`Scorer` doesn't forbid negative weights. Heuristics now copes with them, but a check in `scoring.py` or `Solver.weights` (lead-owned) would protect every solver, including the ILP.
