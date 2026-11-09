# Report 07 (Lead): survival.py and scoring.py implemented and unit-tested (L1.3)

**Date:** 2026-11-09
**Owner:** Lead
**Status:** Done locally on `p1/lead`, not yet committed

## 1. What was asked

Implement `donorbridge/survival.py` and `donorbridge/scoring.py` exactly as in the contract, plus
`tests/unit/test_scoring.py`:

- `UniformSurvival(p)` checks that 0 <= p <= 1, and `edge()` returns p.
  `SurvivalModel.cycle()` multiplies `edge()` over `cycle.edges()`.
- `CountScorer.name = "count"`. `ExpectedTransplantScorer.name` is `f"expected(p={p})"` for
  uniform survival and `"expected(<ClassName>)"` otherwise. A float argument becomes
  `UniformSurvival(p)`.
- `Scorer.total` sums `weight` over the rings.
- Tests:
  - a 3-ring at p=0.9 weighs `3*0.9**3`
  - a 2-ring at p=0.6 weighs 0.72
  - for p in [0.5, 0.6, 0.66, 0.67, 0.7, 0.9], the 3-ring beats the 2-swap iff p > 2/3
  - `CountScorer` ignores p

## 2. What was done

| File | Change |
| --- | --- |
| `donorbridge/survival.py` | All 3 stub bodies filled in, and `import math` added. No signature changed. |
| `donorbridge/scoring.py` | All 4 stub bodies filled in, and `UniformSurvival` is now imported. No signature changed. |
| `tests/unit/test_scoring.py` | New: 27 tests (counting each parametrised case), 0.02 s. |

How it works:

- **`SurvivalModel.cycle`** returns `math.prod(self.edge(pool, donor, patient) for donor, patient in cycle.edges())`.
  It goes through `edge()`, so `SensitisationSurvival` (Generator, P3) only has to define `edge()`.
- **`UniformSurvival.__init__`** raises `ValueError("p must be in [0, 1], got …")` unless
  `0 <= p <= 1`. That check is also False for NaN, so NaN is rejected too. It stores `self.p = float(p)`.
- **`Scorer.total`** returns `sum((weight(c) for c in cycles), 0.0)`. An empty plan gives `0.0`, a float rather than the int 0.
- **`CountScorer.weight`** returns `float(len(cycle))`, which matches the `-> float` annotation.
- **`ExpectedTransplantScorer.__init__`**:
  - Anything that is not a `SurvivalModel` is wrapped in `UniformSurvival(...)`. That covers floats and ints, and a bad p raises the same `ValueError`.
  - It stores `self.survival`.
  - It sets `self.name` with `isinstance(survival, UniformSurvival)`, using the p format for uniform survival and the class name otherwise.
- **`ExpectedTransplantScorer.weight`** returns `len(cycle) * self.survival.cycle(pool, cycle)`.

What the tests cover. All of them use the `ring_vs_swap` fixture: swap (0,1), ring (0,1,2).

| Area | Tests |
| --- | --- |
| `UniformSurvival` | rejects -0.1, 1.1 and NaN; accepts 0 and 1, as ints and floats; `edge()` is p on every edge; `cycle()` is p**len |
| `SurvivalModel.cycle` | a test-only `PerEdgeSurvival` gives each edge its own chance. The ring's product is 0→1 · 1→2 · 2→0, and the swap's is 0→1 · 1→0, so edge direction is checked too |
| Expected weights | 3-ring at 0.9 is 2.187; 2-ring at 0.6 is 0.72; the crossover over all six p values (parametrised) |
| Float → model | `ExpectedTransplantScorer(0.6).survival` is a `UniformSurvival` with p 0.6 and gives the same weights as the explicit model; `ExpectedTransplantScorer(1.5)` raises |
| `CountScorer` | weights 2.0 and 3.0, identical to `ExpectedTransplantScorer(1.0)` |
| `total` | sums the weights; an empty plan gives float `0.0`; accepts a generator |
| Names | `count`, `expected(p=1.0)` (the default), `expected(p=0.6)`, `expected(p=1.0)` from the int 1, `expected(p=0.9)` from the model, `expected(PerEdgeSurvival)` |
| ABCs | `Scorer()` and `SurvivalModel()` raise `TypeError` |

Verification:

```bash
uv run pytest tests/unit/test_scoring.py -q                    # 27 passed
uv run pytest tests/integration/test_phase1.py -k lead -rs     # 6 passed (crossover no longer skipped)
uv run pytest tests/unit tests/integration -q -rs              # 76 passed, 14 skipped, 0 failed
```

After report 06 the suite was 48 passed and 15 skipped. It is now 76 passed (+27 unit tests, +1
crossover) and 14 skipped. Every remaining skip names its stub:

- `Lead, P1`: 4 tests, waiting on the solver base and registry (L1.4).
- `Generator, P1`: 6 tests.
- `Matching, P1`: 2 tests.
- `Simulation, P1`: 2 tests.

`test_p1_simulation_failure_p1_exact` used to stop at the `UniformSurvival` stub. It now gets as far
as the simulation stub, which is why the Simulation count went from 1 to 2.

## 3. Deviations from the request or the contract

1. **Two public instance attributes that the contract text does not list:** `UniformSurvival.p` and
   `ExpectedTransplantScorer.survival`. The contract implies both. The name format
   `expected(p={p})` has to read p from a model passed in, and `FairnessScorer` (a subclass,
   Simulation P3) computes `survival.cycle(pool, c)`, so it needs `self.survival`. Neither is a new
   method or class, and no signature changed.
2. **p is stored as `float(p)`.** As a result, `ExpectedTransplantScorer(1)` is named
   `expected(p=1.0)` rather than `expected(p=1)`. Every way of writing the same p gives one name,
   which keeps the `scorer`/`solver` labels in the CSVs consistent.
3. **Uniform survival is detected with `isinstance`.** A future subclass of `UniformSurvival` would
   therefore get the `expected(p=…)` name. None exists, and `SensitisationSurvival` subclasses
   `SurvivalModel` directly, so it gets `expected(SensitisationSurvival)`.
4. **Survival tests are in `test_scoring.py`.** The request names only that file. There is no
   separate `test_survival.py`.

## 4. Things to note

1. **Names with awkward p values are long:** `ExpectedTransplantScorer(2/3).name` is
   `expected(p=0.6666666666666666)`. That follows the requested format exactly. If the grid ever
   uses names as labels, it should pass round p values such as 0.6 or 0.9.
2. **`total` does not validate.** It adds weights even for overlapping rings. Feasibility is
   `Solution.validate`'s job, and the solver base calls it.
3. **`CountScorer.weight` returns a float** (`3.0`, not `3`), so `Solution.objective` is always a
   float, whichever scorer is used.
4. **A p of exactly 2/3 is a tie** (8/9 each). The integration test checks this and it passes. Any
   solver tie-break at p = 2/3 is therefore arbitrary, and experiments should avoid exactly 2/3 as
   a grid point.
5. **Tell the Generator owner** that `SensitisationSurvival` only has to implement `__init__` and
   `edge()`, because `cycle()` is inherited.
6. **Tell the Simulation owner** that `FairnessScorer` can call `super().__init__(survival)` to
   get float→model conversion and p validation for free. It must then set its own `self.name`
   afterwards, because the parent's `expected(...)` name would otherwise stay.

## 5. Next steps

- [ ] Review the diff, then commit on `p1/lead`, e.g. `P1 lead: implement survival.py and scoring.py (L1.3)`.
      The unstaged edit to `team/01_lead.md` was left alone again.
- [ ] L1.4: `solvers/base.py` (template method) and `solvers/__init__.py` (registry), unit-tested
      with a dummy solver. This clears the last 4 `Lead, P1` skips. Then open the L1.2–L1.4 PR
      (target: Wed noon).
- [ ] Add `ai_logs/lead.md` entries for L1.2 and L1.3. The folder still doesn't exist.
- [ ] Once this is merged, post notes 5 and 6 to the Generator and Simulation owners.
