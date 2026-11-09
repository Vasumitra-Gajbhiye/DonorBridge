# Report 08 (Lead): Solver base (template method) and registry, unit-tested (L1.4)

**Date:** 2026-11-09
**Owner:** Lead
**Status:** Done locally on `p1/lead`, not yet committed

## 1. What was asked

Implement `donorbridge/solvers/base.py` (`Solver`) and `donorbridge/solvers/__init__.py`, plus
`tests/unit/test_solver_base.py` using a `DummySolver` defined inside the test file:

- `__init__` raises `ValueError` if `max_cycle_len` is not in `supported_lengths`. The scorer
  defaults to `CountScorer()`.
- `solve(pool, cycles=None)` is a template method with six steps:
  1. find the rings if none were given;
  2. keep rings with `len <= max_cycle_len`;
  3. time `_solve`;
  4. force `optimal=False` if the solver is not exact;
  5. build the `Solution` with its rings sorted by `(len, families)` and `objective = scorer.total`;
  6. validate it and return it.
- `weights` returns `{c: scorer.weight(c, pool)}`.
- `__repr__` shows the name, `max_cycle_len` and the scorer name.
- A three-line explanation of why this is the Template Method pattern (section 6).

## 2. What was done

| File | Change |
| --- | --- |
| `donorbridge/solvers/base.py` | `__init__`, `solve` and `weights` filled in, and `__repr__` added. New imports: `time` and `CountScorer`. No signature changed. |
| `donorbridge/solvers/__init__.py` | **Unchanged.** The L1.1 skeleton already held the complete `SOLVERS` dict and `get_solver`, which raises a `KeyError` listing the valid names. It matches the contract. |
| `tests/unit/test_solver_base.py` | New: 36 tests (counting each parametrised case), 0.03 s. |

How it works:

- **`__init__`** checks `max_cycle_len` against the *subclass's* `supported_lengths` (it reads
  `self.supported_lengths`). The error message names the solver, for example
  `matching supports max_cycle_len in (2,), got 3`. It stores `max_cycle_len`, `scorer`,
  `time_limit_s` and `seed`. A fresh `CountScorer()` is created per solver, so solvers never share
  a default scorer.
- **`solve`** follows the six steps exactly, with one comment per step:
  - `find_cycles` is imported inside the method, as asked.
  - The filter builds a new list, so the caller's list is never changed. This matters because
    `run_grid` passes the same ring list to every solve.
  - `runtime_s` times only `_solve`.
  - `objective` is `self.scorer.total(chosen, pool)`.
  - `validate` runs last, so an invalid plan raises `InvalidSolutionError` and is never returned.
- **`weights`** is a dict comprehension over the scorer.
- **`__repr__`** gives, for example, `GreedySolver(name='greedy', max_cycle_len=3, scorer='count')`.

Test doubles (all in the test file):

| Double | What it does |
| --- | --- |
| `DummySolver` | Exact. Takes rings first-fit in the order given and records what `_solve` received. |
| `HeuristicDummy` | Not exact. Its `_solve` claims `optimal=True`. |
| `ReturnsDummy` | Returns a fixed answer, used to feed bad or unsorted plans in. |
| `TwoOnlyDummy` | `supported_lengths=(2,)`, like `MatchingSolver`. |

What the tests cover. They use the `ring_vs_swap`, `greedy_trap` and `empty` fixtures.

| Area | Tests |
| --- | --- |
| `__init__` | Rejects 0, 1 and 5. Accepts 2, 3 and 4. A `(2,)`-only subclass rejects the default 3. Checks the defaults, that given settings are kept, that default scorers are not shared, and that `Solver()` raises `TypeError`. |
| Rings in | Longer rings are dropped before `_solve`; rings up to the cap are kept; the caller's list is not mutated; `cycles=None` calls `find_cycles(pool, max_cycle_len)` once (monkeypatched); `cycles=[]` does not call it. |
| Solution out | Checks every field (solver name, objective, optimal, stats, float runtime ≥ 0); rings are sorted even when `_solve` returns them reversed; the objective uses the solver's scorer (3·0.9³, and a sum over two swaps at p=0.6). |
| Optimal flag | An exact solver passes True, None and False through; a heuristic is forced to False. |
| Validation | Overlapping rings, a ring longer than the cap, and a ring with a missing edge each raise `InvalidSolutionError`. |
| Empty pool | No rings and an objective of `0.0`. |
| `weights` | Count weights 2.0/3.0; expected weights 0.72 and 3·0.6³ at p=0.6; empty input gives `{}`. |
| `__repr__` | Exact strings for the default solver and for one with an expected scorer. |
| Registry | Every key equals its class's `name`; `get_solver` passes kwargs through; an unknown name gives a `KeyError` listing all seven names; `get_solver("matching")` raises `ValueError` while `max_cycle_len=2` works. |

Verification:

```bash
uv run pytest tests/unit/test_solver_base.py -q                # 36 passed
uv run pytest tests/integration/test_phase1.py -k lead -rs     # 6 passed
uv run pytest tests/unit tests/integration -q -rs              # 112 passed, 14 skipped, 0 failed
```

Report 07 ended at 76 passed and 14 skipped. The 36 new unit tests explain the change. The
skip count is unchanged, but **no skip is labelled `Lead, P1` any more**:

- `Matching, P1`: 6 tests. The 4 former `Lead, P1` tests call `solver.solve(pool)` without rings,
  so they now get past the solver base and stop at the `find_cycles` stub. Several of them will
  stop next at the Heuristics `_solve` stubs.
- `Generator, P1`: 6 tests.
- `Simulation, P1`: 2 tests.

## 3. Deviations from the request or the contract

1. **`solvers/__init__.py` was not touched.** It was already complete from L1.1. The new unit tests
   cover it instead.
2. **Four public instance attributes that the contract text does not list:** `max_cycle_len`,
   `scorer`, `time_limit_s` and `seed`. The contract implies them:
   - the ILP needs `time_limit_s`;
   - randomised solvers build `random.Random(self.seed)`;
   - every subclass reads `scorer` and `max_cycle_len`.

   No signature changed.
3. **Tests in addition to those requested:** the registry tests, and the `cycles=[]` must-not-call
   test. Neither changes behaviour.

## 4. Things to note

1. **`get_solver("matching")` now raises `ValueError`** with the default `max_cycle_len=3`. This
   was flagged in report 02, note 1, and is still undecided. A test now pins this behaviour, so if
   you later give `MatchingSolver` its own default of 2, update
   `test_get_solver_checks_max_cycle_len`.
2. **`solve` does not check that the chosen rings come from `cycles`.** This was not requested.
   `validate` still rejects any ring that uses a missing edge, an unknown id or a shared family, so
   a wrong plan cannot get through. It could only pick a ring that was not offered but is real.
3. **`runtime_s` excludes ring enumeration.** This is intended: `run_grid` records `enum_s`
   separately.
4. **The `cycles=None` path works with monkeypatching** because `find_cycles` is imported at call
   time. The test patches `donorbridge.cycles.find_cycles`, so it does not depend on the Matching
   stub.
5. **Tell the solver owners:**
   - implement only `_solve`, and never override `solve`;
   - compare rings with `self.weights(pool, cycles)`, never `len(c)`;
   - return `(list_of_rings, optimal_flag, stats_dict)`;
   - the base class sorts, scores and validates for you.

## 5. Next steps

- [ ] Review the diff, then commit on `p1/lead`, e.g.
      `P1 lead: implement solvers/base.py with unit tests (L1.4)`.
      The unstaged edit to `team/01_lead.md` was left alone again.
- [ ] Open the L1.2–L1.4 PR (target: Wed noon).
- [ ] Decide on the `MatchingSolver` default `max_cycle_len` (note 1).
- [ ] Paste the Template Method lines (section 6) into `docs/design/lead.md`.
- [ ] Add `ai_logs/lead.md` entries for L1.2–L1.4. The folder still doesn't exist.
- [ ] After the merge, post note 5 to the Heuristics, Matching and B&B owners.

## 6. Template Method: the lines for the design file

1. `Solver.solve` fixes the skeleton of every solve once, in the base class: find rings, filter by
   length, time, score, build and validate the `Solution`.
2. The one step that varies, choosing the rings, is the abstract hook `_solve`. Each subclass
   overrides it, and no subclass overrides `solve`.
3. So all seven solvers share the same timing, scoring, optimal-flag and validation logic. That
   makes their results comparable, and an invalid plan can never be returned ("don't call us,
   we'll call you").
