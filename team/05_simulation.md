# DonorBridge · Simulation owner playbook

**Owner:** ____________ · **Role:** Simulation owner (night-before failure simulation and re-solve, fairness sweep, runtime benchmarks, all charts)
**The algorithm you present on stage:** the Monte Carlo failure simulator. You show how we check that "expected transplants" is real by actually simulating crossmatches failing the night before surgery.

You turn the engine into the **answer**. The project's headline (3-way rings add about 21% when every test passes, under 4% once 3 in 10 fail, and count-maximising plans fall below 2-way around a quarter failure rate) comes out of your survival sweep and your crossover chart. In P4 you own all four charts.

## 1. How we work: the phase loop

We build in five phases. **Nobody starts phase N+1 until phase N is merged into `main` and `tests/integration/test_phaseN.py` is green.**

| Phase | Dates | The phase is done when |
| --- | --- | --- |
| **P1 Foundations** | Tue 3 – Thu 5 Nov | Contract, data model, generator, graph + cycle finder, first-come + greedy, metrics + failure simulator all work end to end on one pool |
| **P2 Engine v1** | Fri 6 – Tue 10 Nov | ILP matches kep_solver on Glasgow pools; brute force, local search, branch and bound v1, night-before re-solve, `python -m donorbridge run` |
| **P3 Exact solvers + failure model** | Wed 11 – Mon 16 Nov | Matching, branch and bound with its bound, failure-aware scoring in every solver, 1,000-pool cross-check green. ◆ Gate: checks all green, 16 Nov |
| **P4 Experiments** | Tue 17 – Sun 22 Nov | Every experiment, all four charts and the answer rebuild from one command. ◆ **Feature freeze Mon 23 Nov** |
| **P5 Story** | Tue 24 Nov – Mon 7 Dec | Design file, AI log, deck, demo, release check, three rehearsals |

Every phase runs the same seven steps:

1. **Day 1, 10 am.** The lead pushes `tests/integration/test_phaseN.py` to `main`. That file *is* the definition of done for the phase. Read every test whose name contains your role.
2. **Branch.** `git checkout main && git pull && git checkout -b pN/<role>` (for example `p1/generator`).
3. **Build.** Touch only the files you own (see the module map), your unit tests, `ai_logs/<role>.md` and `docs/design/<role>.md`. Need a change in someone else's file or in the contract? Message the lead. The lead changes `main`, and you run `git merge main`.
4. **Check locally.** `pytest tests/unit -q` and `pytest tests/integration/test_phaseN.py -k <role> -q`. Tests with `e2e` in the name only pass after the merge, so don't worry about them on your branch.
5. **Merge day, 6 pm** (last day of the phase). Open a PR `pN/<role> → main`. The lead merges in dependency order (**lead → generator → matching → heuristics → simulation**) and runs the unit tests after each merge.
6. **Integration run.** The lead runs `pytest tests/integration/test_phaseN.py` (plus `--run-slow` at the P3 and P4 gates). Each failure goes to the owner of the module that failed. Fixes go on `pN/fix-<topic>` branches the same evening.
7. **Gate.** When everything is green, the lead tags `phase-N-done` and posts in the group chat. Only then does anyone start phase N+1.

Finished early? Pair with someone who is behind, review their PR, or add unit tests for their module. Read ahead if you like, but don't write next-phase code.

## 2. Rules for every task

- **Python 3.11.** Libraries: standard library, numpy, pandas, matplotlib, networkx, pulp==2.9.0, highspy, pytest. Add nothing else without asking the lead.
- **Type hints and docstrings** on every public class and function.
- **No global random state.** Every random function takes `seed: int` or `rng: random.Random`. Never call `random.seed()` or `np.random.*` at module level. Same seed, same output, every time.
- **Family ids are unique ints, not positions.** Never use an id as a list index. Use `pool.family(fid)` or a dict.
- **Unit tests** go in `tests/unit/test_<module>.py`. Each test runs in under 1 s unless it is marked `@pytest.mark.slow`.
- **The contract is frozen.** Code against the signatures in section 6 exactly. Only the lead changes them, and only on `main`.
- **Your algorithm is yours.** Each person presents one hand-written algorithm on stage. Write that code yourself (see section 3).
- **Commits:** small, present tense, prefixed with the phase, e.g. `P1 generator: sample PRA bands`. Never commit straight to `main`; only the lead merges.

## 3. Using AI (rubric item 6)

Use AI in one of two modes:

- **Tutor mode, for the algorithm you present on stage.** The AI explains the idea, critiques your pseudocode, suggests test cases and reviews code you wrote. **You type the implementation yourself.** You must be able to whiteboard it without notes. Prompts in this mode are marked 🧑‍🏫.
- **Builder mode, for plumbing** (I/O, CLI, test scaffolding, plots, glue). The AI drafts and you read every line, run it and fix it. You still have to be able to explain each line. Prompts in this mode are marked 🛠.

How to run a prompt:

1. Open a new chat and paste the **context block** from section 6, with your role filled in. It tells the AI the project, the rules and the contract.
2. Paste the prompt. Each prompt has an ID such as `G1.3`.
3. Paste your actual code or file contents wherever a prompt says `<paste …>`. Never let the AI guess at code it hasn't seen.
4. Run whatever it gives you. If a test fails, paste the failure back. Don't paste in fixes you haven't run.

After every prompt, add an entry to `ai_logs/<role>.md` (yours: `ai_logs/simulation.md`). The lead merges these into `AI_LOG.md` in P5.

```markdown
### 2026-11-03 · G1.3 · Saidman generator pseudocode review
- Tool: Claude / ChatGPT / Copilot
- Prompt: G1.3 as written (or what you changed)
- Kept: what you used from the answer
- Corrected: what the AI got wrong, and how you caught it (a failing test, the paper, a teammate)
- Time: roughly how much it saved or cost
```

The graders care most about **Corrected**, so keep it honest. "The AI said O-patients can receive from A donors; the exhaustive ABO test caught it" is a great entry.

## 4. One-time setup

The lead's contract commit lands on `main` by **Tue 3 Nov, 12:00**. After it lands:

```bash
git clone <repo-url> && cd DonorBridge          # or: git pull
python3.11 -m venv .venv
source .venv/bin/activate                        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
pytest -q                                        # stubs import; most tests are skipped or fail with NotImplementedError — expected
python -m donorbridge --help
```

Only the lead (and anyone running the oracle tests) also needs the kep_solver environment:

```bash
python3.11 -m venv .venv-oracle
.venv-oracle/bin/pip install -r requirements-oracle.txt    # kep_solver + pulp==2.9.0 (kep_solver breaks on PuLP 4.x)
```

## 5. Module map (who owns what)

Every file below exists from the lead's P1 skeleton commit, as a stub that raises `NotImplementedError("<owner>, P<n>")`. You fill in your own stubs and never create new modules under `donorbridge/`. That rule is what makes the merges conflict-free.

| Path (under `donorbridge/` unless noted) | Owner | Phase | Public names |
| --- | --- | --- | --- |
| `pyproject.toml`, `requirements*.txt`, `.github/`, `README.md`, every `__init__.py`, `__main__.py` (CLI) | Lead | P1 | `python -m donorbridge {run,sweep,bench,results,demo}` |
| `models.py` | Lead | P1 | `BloodGroup`, `Sex`, `Relation`, `Family`, `Pool`, `Cycle`, `Solution`, `InvalidSolutionError` |
| `survival.py` | Lead | P1 | `SurvivalModel`, `UniformSurvival` |
| `scoring.py` | Lead | P1 | `Scorer`, `CountScorer`, `ExpectedTransplantScorer` |
| `solvers/base.py`, `solvers/__init__.py` | Lead | P1 | `Solver`, `SOLVERS`, `get_solver` |
| `solvers/ilp.py` | Lead | P2–P3 | `ILPSolver` (`"ilp"`) |
| `oracle/glasgow.py`, `oracle/kep_oracle.py`, `scripts/kep_oracle_runner.py` (repo root) | Lead | P2 | `load_glasgow`, `list_instances`, `pool_to_kep_json`, `kep_optimum` |
| `oracle/crosscheck.py` | Lead | P3 | `crosscheck`, `CrosscheckReport` |
| `experiments/answer.py` | Lead | P4 | `compute_answer` |
| `tests/conftest.py`, `tests/fixtures/`, `tests/integration/` (repo root) | Lead | every phase | fixtures, `test_phaseN.py` |
| `compatibility.py` | Generator | P1 | `blood_compatible` |
| `generator/calibration.py` | Generator | P1–P2 | `Calibration`, `INDIA`, `US` |
| `generator/saidman.py` | Generator | P1–P2 | `PoolGenerator`, `SaidmanGenerator`, `GenerationReport`, `make_generator` |
| `generator/report.py` | Generator | P2 | `calibration_report` |
| `generator/survival_models.py` | Generator | P3 | `SensitisationSurvival` |
| `generator/regions.py` | Generator | P3 | `split_by_region` |
| `experiments/blood_mix.py`, `experiments/female_sensitisation.py`, `experiments/regions.py` | Generator | P4 | `BloodMix`, `FemaleSensitisation`, `RegionSplit` |
| `graph.py` | Matching | P1 | `CompatibilityGraph` |
| `cycles.py` | Matching | P1 | `CycleFinder`, `find_cycles`, `find_cycles_nested_loops` |
| `solvers/brute_force.py` | Matching | P2 | `BruteForceSolver` (`"brute-force"`) |
| `solvers/matching.py` | Matching | P3 | `MatchingSolver` (`"matching"`) |
| `demos/scripts.py`, `notebooks/demo.ipynb` (repo root), `experiments/cycle_growth.py` | Matching | P4 | `DEMOS`, `demo_small`, `demo_india`, `demo_edge`, `CycleGrowth` |
| `solvers/first_come.py`, `solvers/greedy.py` | Heuristics | P1 | `FirstComeSolver` (`"first-come"`), `GreedySolver` (`"greedy"`) |
| `solvers/local_search.py` | Heuristics | P2 | `LocalSearchSolver` (`"local-search"`) |
| `solvers/branch_bound.py` | Heuristics | P2–P3 | `BranchAndBoundSolver` (`"branch-bound"`) |
| `experiments/optimality_gap.py`, `experiments/ring_length.py` | Heuristics | P4 | `OptimalityGap`, `RingLength` |
| `simulation/metrics.py` | Simulation | P1 | `PoolMetrics`, `compute_metrics` |
| `simulation/failure.py` | Simulation | P1 | `FailureSimulator`, `FailureOutcome` |
| `simulation/resolve.py` | Simulation | P2 | `NightBeforeSimulator`, `ResolveOutcome` |
| `experiments/base.py`, `experiments/survival_sweep.py` | Simulation | P2–P3 | `Experiment`, `SurvivalSweep` |
| `simulation/fairness.py`, `simulation/benchmark.py` | Simulation | P3 | `FairnessScorer`, `time_solvers` |
| `experiments/fairness.py`, `experiments/runtime.py`, `simulation/plots.py` | Simulation | P4 | `PriceOfFairness`, `Runtime`, `make_all_figures` |

Test fixtures (lead, P1), in `tests/fixtures/`:

| Fixture | What it is | Known answers |
| --- | --- | --- |
| `pool_8.json` + `pool_8.expected.json` | The 8-family pool we solved by hand in week 1 | All rings for L=2 and L=3; optimum transplants for L=2 and L=3 |
| `ring_vs_swap.json` | Families 0,1,2; edges 0→1, 1→2, 2→0, 1→0 | Rings (0,1) and (0,1,2). Count picks the ring (3). Expected-transplant scoring picks the swap at p=0.6 (0.72 > 0.648) and the ring at p=0.9 (2.187 > 1.62) |
| `greedy_trap.json` | Families 0–3; edges 0→1, 1→2, 2→0, 2→1, 0→3, 3→0 | Rings (0,3), (1,2), (0,1,2). Greedy-by-size takes the ring and gets 3; the optimum is (0,3)+(1,2) = 4 |
| `empty.json`, `no_edges.json` | 0 families; 5 families and no edges | Every solver returns 0 rings without crashing |

## 6. AI context block (this is also the shared contract)

Paste everything in this box at the start of **every** new AI chat. The last two lines are already filled in for you.

````text
PROJECT CONTEXT: DonorBridge (read fully before answering)

I'm on a 5-person student team (7-week course project) building `donorbridge`, a Python 3.11
package for kidney paired exchange, calibrated to India.

Domain:
- A "family" = one patient + one willing donor who cannot give to that patient (blood group, or a
  positive crossmatch). All families are simulated; real Indian statistics drive the generator.
- Directed edge i -> j: family i's donor can give to family j's patient (ABO-compatible AND negative
  crossmatch).
- A ring (cycle) of 2 or 3 families is a swap. We choose vertex-disjoint rings to maximise total weight.
- Ring weight is either its size |c| ("count") or its expected transplants |c| * p^|c|, where p is the
  chance each final crossmatch passes the night before surgery. A ring goes ahead only if every
  crossmatch in it passes, so a 3-ring beats a 2-swap on the same families only when p > 2/3.
- Rings capped at 2 = maximum matching (polynomial). Rings of 3 = NP-hard (Abraham, Blum, Sandholm 2007).
- We do NOT model altruistic donors/chains or tissue typing beyond PRA. The compatibility model is frozen.

Team rules:
- Python 3.11. Allowed: standard library, numpy, pandas, matplotlib, networkx (>=3.1), pulp==2.9.0,
  highspy, pytest. Nothing else.
- Type hints + docstrings on every public class/function. Readable over clever: I must explain every
  line in a viva.
- No global random state. Every random function takes `seed: int` or `rng: random.Random`.
- Family ids are unique ints but NOT necessarily 0..n-1. Never use an id as a list index.
- The contract below is frozen. Code against it exactly. If it looks wrong, say so and STOP; do not
  change or extend it.
- Only touch the files I own. Tests go in tests/unit/test_<module>.py using pytest.

Shared contract (signatures only):

# donorbridge/models.py (lead)
class BloodGroup(str, Enum): O = "O"; A = "A"; B = "B"; AB = "AB"
class Sex(str, Enum): F = "F"; M = "M"
class Relation(str, Enum): SPOUSE = "spouse"; OTHER = "other"     # donor's relation to patient
@dataclass(frozen=True)
class Family:
    id: int
    patient_blood: BloodGroup
    donor_blood: BloodGroup
    patient_sex: Sex
    donor_sex: Sex
    relation: Relation
    patient_pra: float        # 0..1: chance of a positive crossmatch against a random donor
    region: int = 0           # 0..3, for the state-split experiment
    @property
    def highly_sensitised(self) -> bool: ...      # patient_pra >= 0.80
@dataclass(frozen=True)
class Pool:
    families: tuple[Family, ...]
    edges: frozenset[tuple[int, int]]             # (i, j): donor of i -> patient of j, i != j
    name: str = ""
    @property
    def n(self) -> int: ...
    def ids(self) -> tuple[int, ...]: ...         # sorted
    def family(self, fid: int) -> Family: ...
    def subpool(self, ids: Iterable[int], name: str = "") -> "Pool": ...   # induced: keeps edges among ids
    def without_edges(self, drop: Iterable[tuple[int, int]]) -> "Pool": ...
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, d: dict) -> "Pool": ...
    def save_json(self, path: str | Path) -> None: ...
    @classmethod
    def load_json(cls, path: str | Path) -> "Pool": ...
@dataclass(frozen=True)
class Cycle:
    families: tuple[int, ...]   # canonical: rotated so the smallest id is first; direction kept
    @classmethod
    def of(cls, seq: Sequence[int]) -> "Cycle": ...          # canonicalises any rotation
    def edges(self) -> tuple[tuple[int, int], ...]: ...      # (f0,f1), (f1,f2), ..., (fk,f0)
    def __len__(self) -> int: ...
class InvalidSolutionError(ValueError): ...
@dataclass(frozen=True)
class Solution:
    cycles: tuple[Cycle, ...]
    solver: str
    objective: float          # total weight under the solver's scorer
    runtime_s: float
    optimal: bool | None      # True = proven optimal; False = heuristic or timed out; None = unknown
    stats: dict = field(default_factory=dict, compare=False)
    @property
    def transplants(self) -> int: ...             # sum of ring sizes
    def covered(self) -> frozenset[int]: ...
    def validate(self, pool: Pool, max_cycle_len: int) -> None: ...   # raises InvalidSolutionError

# donorbridge/survival.py (lead)
class SurvivalModel(ABC):
    @abstractmethod
    def edge(self, pool: Pool, donor_family: int, patient_family: int) -> float: ...  # P(crossmatch passes)
    def cycle(self, pool: Pool, cycle: Cycle) -> float: ...    # product over the ring's edges
class UniformSurvival(SurvivalModel):
    def __init__(self, p: float): ...

# donorbridge/scoring.py (lead)
class Scorer(ABC):
    name: str
    @abstractmethod
    def weight(self, cycle: Cycle, pool: Pool) -> float: ...
    def total(self, cycles: Iterable[Cycle], pool: Pool) -> float: ...
class CountScorer(Scorer): ...                 # weight = len(cycle)
class ExpectedTransplantScorer(Scorer):        # weight = len(cycle) * survival.cycle(pool, cycle)
    def __init__(self, survival: SurvivalModel | float = 1.0): ...   # a float p means UniformSurvival(p)

# donorbridge/compatibility.py (generator)
def blood_compatible(donor: BloodGroup, patient: BloodGroup) -> bool: ...

# donorbridge/generator/ (generator)
@dataclass(frozen=True)
class Calibration: ...       # name, blood-group frequencies, sex/relation shares, PRA bands, crossmatch rates
INDIA: Calibration
US: Calibration
@dataclass(frozen=True)
class GenerationReport: ...  # pairs sampled, pairs rejected as directly compatible, positive crossmatches by relation and sex
class PoolGenerator(ABC):
    @abstractmethod
    def generate_with_report(self, n: int, seed: int) -> tuple[Pool, GenerationReport]: ...
    def generate(self, n: int, seed: int) -> Pool: ...                          # concrete
    def generate_many(self, n_pools: int, n: int, seed: int) -> list[Pool]: ...  # seeds seed, seed+1, ...
class SaidmanGenerator(PoolGenerator):
    def __init__(self, calibration: Calibration = INDIA, **overrides): ...
def make_generator(preset: str = "india", **overrides) -> SaidmanGenerator: ...  # "india" | "us"

# donorbridge/graph.py, donorbridge/cycles.py (matching)
class CompatibilityGraph:
    def __init__(self, pool: Pool): ...
    def nodes(self) -> tuple[int, ...]: ...
    def successors(self, fid: int) -> tuple[int, ...]: ...     # sorted
    def predecessors(self, fid: int) -> tuple[int, ...]: ...   # sorted
    def has_edge(self, i: int, j: int) -> bool: ...
    def mutual_pairs(self) -> list[tuple[int, int]]: ...       # (i, j) with i < j and both directions
    def to_networkx(self) -> "nx.DiGraph": ...
class CycleFinder:
    def __init__(self, graph: CompatibilityGraph): ...
    def find(self, max_len: int) -> list[Cycle]: ...  # every simple ring, 2 <= len <= max_len, once each, sorted by (len, families)
def find_cycles(pool: Pool, max_len: int) -> list[Cycle]: ...

# donorbridge/solvers/base.py (lead)
class Solver(ABC):
    name: ClassVar[str]                       # registry name, e.g. "greedy"
    exact: ClassVar[bool]                     # proves optimality when it finishes in time
    supported_lengths: ClassVar[tuple[int, ...]] = (2, 3, 4)
    def __init__(self, max_cycle_len: int = 3, scorer: Scorer | None = None,
                 time_limit_s: float | None = None, seed: int = 0): ...   # scorer defaults to CountScorer()
    def solve(self, pool: Pool, cycles: list[Cycle] | None = None) -> Solution: ...
        # template method: find rings if None, drop rings longer than max_cycle_len, time _solve(),
        # score with self.scorer, build the Solution, validate it, return it
    def weights(self, pool: Pool, cycles: list[Cycle]) -> dict[Cycle, float]: ...   # scorer weight per ring
    @abstractmethod
    def _solve(self, pool: Pool, cycles: list[Cycle]) -> tuple[list[Cycle], bool | None, dict]: ...
        # subclasses implement only this: return (chosen rings, optimal flag, stats dict)
# donorbridge/solvers/__init__.py: get_solver(name: str, **kwargs) -> Solver
#   names: "first-come", "greedy", "local-search", "matching", "brute-force", "branch-bound", "ilp"

# donorbridge/simulation/ (simulation)
@dataclass(frozen=True)
class PoolMetrics: ...       # transplants, expected transplants, matched shares by sensitisation/sex/blood group
def compute_metrics(pool: Pool, solution: Solution, survival: SurvivalModel | None = None) -> PoolMetrics: ...
@dataclass(frozen=True)
class FailureOutcome: ...    # rings that went ahead, failed edges, realised transplants
class FailureSimulator:
    def __init__(self, survival: SurvivalModel, seed: int): ...
    def realise(self, pool: Pool, solution: Solution) -> FailureOutcome: ...       # one night-before draw
    def expected(self, pool: Pool, solution: Solution, n_trials: int) -> tuple[float, float]: ...  # (mean, 95% CI half-width)

# donorbridge/experiments/base.py (simulation)
class Experiment(ABC):
    name: ClassVar[str]
    def __init__(self, out_dir: Path = Path("results"), quick: bool = False, seed: int = 2026): ...
    @abstractmethod
    def run(self) -> "pd.DataFrame": ...      # also writes out_dir / f"{name}.csv"
# donorbridge/experiments/__init__.py: EXPERIMENTS: dict[str, type[Experiment]]

My role: Simulation owner (failure simulation and re-solve, fairness, benchmarks, all charts).
I own: donorbridge/simulation/metrics.py, simulation/failure.py, simulation/resolve.py, simulation/fairness.py, simulation/benchmark.py, simulation/plots.py, experiments/base.py, experiments/survival_sweep.py, experiments/fairness.py, experiments/runtime.py, and their tests in tests/unit/.
````

## 7. Before Phase 1 (today, Mon 2 Nov: design gate)

- [ ] `docs/design/simulation.md` has dated pseudocode and a flowchart for: `compute_metrics`, `FailureSimulator.realise` and `.expected`, `NightBeforeSimulator.run`, and the survival sweep.
- [ ] Work out by hand the expected transplants of a plan with one 3-ring and two 2-swaps at p = 0.8: 3·0.8³ + 2·(2·0.8²) = 1.536 + 2.56 = 4.096. This becomes your first test.
- [ ] Re-read the prototype table in Plan.md. Your P3 job is to reproduce it.

**Prompt S0.1 🧑‍🏫: design-gate check**

```text
[paste context block]

Here is my pseudocode for the failure simulator, the re-solve simulator and metrics (dated). Don't
write code.
1. Turn each into a mermaid flowchart.
2. Is my Monte Carlo estimate unbiased for sum |c| * prod(p_e)? What's its variance for one 3-ring
   at p = 0.7, and how many trials do I need for a 95% CI half-width of 0.01 transplants?
3. Where could the order of random draws make results non-reproducible?
4. List 8 unit tests to write first, with expected outputs.
<paste docs/design/simulation.md>
```

---

## 8. Phase 1: Foundations (Tue 3 – Thu 5 Nov)

**Goal:** given any `Pool` and `Solution`, we can count who was matched (by sensitisation, sex and blood group) and simulate night-before failures. The Monte Carlo mean matches the formula.

**Files:** `simulation/metrics.py`, `simulation/failure.py`, `tests/unit/test_metrics.py`, `tests/unit/test_failure.py`.
**Branch:** `p1/simulation` (after the lead's contract commit, Tue 12:00).

### Agreed shapes (inside your files: stick to these names)

```python
@dataclass(frozen=True)
class PoolMetrics:
    n_families: int
    transplants: int                       # sum of ring sizes in the plan
    expected_transplants: float            # sum |c| * survival.cycle(pool, c); survival defaults to UniformSurvival(1.0)
    rings_by_len: dict[int, int]
    hs_total: int; hs_matched: int         # highly sensitised patients
    female_total: int; female_matched: int
    male_total: int; male_matched: int
    by_blood: dict[str, tuple[int, int]]   # patient blood group -> (matched, total)
    @property
    def hs_matched_share(self) -> float: ...       # 0.0 when the total is 0; same for the two below
    @property
    def female_matched_share(self) -> float: ...
    @property
    def male_matched_share(self) -> float: ...

@dataclass(frozen=True)
class FailureOutcome:
    went_ahead: tuple[Cycle, ...]
    cancelled: tuple[Cycle, ...]
    failed_edges: frozenset[tuple[int, int]]
    transplants: int                       # sum of sizes of rings that went ahead
```

**Simulator rule:** for each ring in `solution.cycles` (already sorted) and each edge in `ring.edges()` (in order), draw `rng.random() < survival.edge(pool, i, j)` to decide pass or fail. A ring goes ahead only if all its edges pass. **Draw for every edge, even after a failure in the same ring.** That keeps the random stream aligned across plans, which makes paired comparisons fairer. Note this in your design file.

### Tasks

- [ ] **S1.1** 🛠 `compute_metrics`.
- [ ] **S1.2** 🧑‍🏫 Write `FailureSimulator.realise` and `.expected` **yourself**. `expected` returns `(mean, 1.96 · sd / √n_trials)`.
- [ ] **S1.3** 🛠 Unit tests: hand-built pools and solutions (don't depend on other P1 modules). p=1 → every ring goes ahead; p=0 → none do; the 4.096 example within 3·SE over 20,000 trials; same seed gives the same outcome.
- [ ] Open PR `p1/simulation → main` by Thu 6 pm.

You can build `Solution` objects by hand in tests: `Solution(cycles=(Cycle.of((0,1)),), solver="hand", objective=2.0, runtime_s=0.0, optimal=None)`.

### Prompts

**S1.1 🛠: metrics**

```text
[context block]

Implement donorbridge/simulation/metrics.py: PoolMetrics (fields below) and
compute_metrics(pool, solution, survival=None). A family is "matched" if it is in any ring of the
solution (planned, before failures). Shares return 0.0 when the denominator is 0.
<paste PoolMetrics shape from my playbook>
Write tests/unit/test_metrics.py using a hand-built 6-family pool (mix of sexes, blood groups, one
highly sensitised patient) and a hand-built Solution, with every expected number written out
explicitly in the test.
```

**S1.2a 🧑‍🏫: learn before writing**

```text
[context block]

I'm hand-writing a Monte Carlo night-before failure simulator. Rule: <paste simulator rule>.
Tutor me, don't write it.
1. Why is the mean of realised transplants an unbiased estimate of sum |c| * prod_e p_e?
2. Why do I draw every edge even after one fails? What does "common random numbers" buy us when
   comparing two plans on the same pool with the same seed?
3. How to compute a 95% CI half-width; when is the normal approximation OK?
4. Using random.Random(seed): should one simulator instance give different draws on each realise()
   call (yes: why) and how do I make expected() reproducible?
```

**S1.2b 🧑‍🏫: review**

```text
[context block]

Review my FailureSimulator: correctness of the pass/fail rule, draw order, reproducibility, the CI
formula, edge cases (empty solution, n_trials=1). Point to lines; minimal fixes.
<paste simulation/failure.py>
```

### Integration checks that hit your code (Phase 1)

`test_p1_simulation_metrics_on_fixture`, `test_p1_simulation_failure_p1_exact`, `test_p1_simulation_failure_matches_analytic`, `test_p1_e2e_pipeline_india_100`. Run them with `pytest tests/integration/test_phase1.py -k simulation`.

---

## 9. Phase 2: Engine v1 (Fri 6 – Tue 10 Nov)

**Goal:** a night-before re-solve simulator, the shared `Experiment` base class that every experiment builds on, and a first quick version of the survival sweep.

**Files:** `simulation/resolve.py`, `experiments/base.py`, `experiments/survival_sweep.py`.

**Re-solve rule** (one round only; the multi-round simulation is Plan.md cut line #3):
1. `plan = solver.solve(pool)`
2. `first = FailureSimulator.realise(pool, plan)`
3. `remaining = pool ids − families in first.went_ahead`
4. `resolve_pool = pool.subpool(remaining).without_edges(first.failed_edges)`. Failed crossmatches are never retried.
5. `resolve = solver.solve(resolve_pool)`; realise it with the same simulator, so new edges can fail too.
6. `final_transplants = first.transplants + second.transplants`

**`Experiment` base helpers** (implement in `experiments/base.py`; everyone's experiments use them):

```python
def pools(self, preset: str, n: int, n_pools: int, **overrides) -> list[Pool]   # seeds self.seed + k
def write(self, df: pd.DataFrame) -> pd.DataFrame                               # CSV to out_dir/{name}.csv, returns df
def log(self, msg: str) -> None                                                 # "[name] msg" with elapsed seconds
```

**`SurvivalSweep` (`survival_sweep`):**

| | Full | Quick |
| --- | --- | --- |
| p | 1.0, 0.9, 0.8, 0.7, 0.6, 0.5 | 1.0, 0.7, 0.5 |
| Pools | 20 India pools × 100 | 3 × 40 |
| Re-solve trials | 20 per pool (`resolve_mean`) | 0 (NaN) |

Policies, all using the ILP:
- `two_way`: L=2, `ExpectedTransplantScorer(p)`
- `three_way_failure_aware`: L=3, `ExpectedTransplantScorer(p)`
- `three_way_count_max`: L=3, `CountScorer()`; evaluate its plan's expected transplants under p

**CSV columns** (one row per pool × p × policy): `p, policy, seed, n, planned_transplants, expected_transplants, resolve_mean`.

### Tasks

- [ ] **S2.1** 🧑‍🏫 `NightBeforeSimulator` and `ResolveOutcome`.
- [ ] **S2.2** 🛠 `Experiment` base helpers.
- [ ] **S2.3** 🛠 `SurvivalSweep`. Make quick mode work now; full mode is P3. Until the ILP merges, test it with `"greedy"` behind a `solver_name` attribute, then switch to `"ilp"`.
- [ ] **S2.4** 🛠 Tests: re-solve properties (final ≥ first; no family transplanted twice; the re-solve uses only remaining families and never a failed edge), and the quick sweep's columns.
- [ ] Open PR by Tue 10 Nov, 6 pm.

### Prompts

**S2.1 🧑‍🏫: re-solve simulator**

```text
[context block]

I'm hand-writing NightBeforeSimulator.run(pool). Rule: <paste re-solve rule>. Tutor me, don't write it.
1. Prove final_transplants >= first.transplants always.
2. Is it realistic to re-test new edges in the re-solve but never retry failed ones? What's the
   honest limitation sentence for the deck?
3. Which properties should my tests check to catch bugs (double-transplanting a family, re-using a
   failed edge, re-solving on the full pool)?
Then review my code: <paste simulation/resolve.py>
```

**S2.2–S2.3 🛠: experiment base and survival sweep**

```text
[context block]

1. Implement donorbridge/experiments/base.py: Experiment(ABC) per the contract plus helpers pools(),
   write(), log() as specified: <paste helper signatures>. out_dir is created if missing.
2. Implement donorbridge/experiments/survival_sweep.py: class SurvivalSweep(Experiment),
   name "survival_sweep". Settings, policies and columns: <paste the SurvivalSweep spec>.
   expected_transplants for every policy = ExpectedTransplantScorer(p).total(solution.cycles, pool)
   (so count-max is evaluated under failure). resolve_mean = mean final_transplants of
   NightBeforeSimulator over resolve_trials draws (seed = self.seed + 1000*k + trial), NaN if 0.
   Use a class attribute solver_name = "ilp".
3. Quick-mode unit test: columns, row count = len(p) * 3 * n_pools, and three_way_failure_aware >=
   two_way per (pool, p) when solver_name is an exact solver.
```

### Integration checks that hit your code (Phase 2)

`test_p2_simulation_resolve_properties`, `test_p2_simulation_experiment_quick`.

---

## 10. Phase 3: Exact solvers and failure model (Wed 11 – Mon 16 Nov) · ◆ gate 16 Nov

**Goal:** **reproduce the prototype table.** That's the core result. Also: the fairness scorer, the benchmark harness, and proof that your simulator agrees with the formula on 1,000 pools.

**Files:** `simulation/fairness.py`, `simulation/benchmark.py`, `experiments/survival_sweep.py` (full mode).

Target: the prototype table from Plan.md, expected transplants per pool (India, 20 × 100):

| p (1 − fail rate) | 2-way | Failure-aware 3-way | Count-max 3-way |
| --- | --- | --- | --- |
| 1.0 | 52.00 | 63.00 | 63.00 |
| 0.9 | 42.12 | 48.50 | 47.24 |
| 0.8 | 33.28 | 36.38 | 34.33 |
| 0.7 | 25.48 | 26.37 | 23.99 |
| 0.6 | 18.72 | 18.98 | 15.94 |
| 0.5 | 13.00 | 13.14 | 9.90 |

Your means should land within ±3 of these. They'll differ a little, because the generator is new code with different seeds. Large gaps mean a bug somewhere: debug with S3.3.

**`FairnessScorer(survival, beta, group)`:** `weight(c) = survival.cycle(pool, c) · Σ_{v∈c} (1 + β·[v in group])`, with group ∈ {`"highly_sensitised"`, `"female"`}. With β = 0 it equals `ExpectedTransplantScorer`.

**`time_solvers(...)`:** returns one row per (solver, n) with columns `solver, max_len, n, median_s, max_s, n_pools, n_timeouts`. Use the same pools for every solver. `matching` runs with L=2, the others with the given `max_cycle_len`.

### Tasks

- [ ] **S3.1** 🛠 `FairnessScorer` + tests: β=0 matches Expected exactly; with β=2, more highly sensitised patients are matched on average over 20 pools.
- [ ] **S3.2** 🛠 `time_solvers` + a test.
- [ ] **S3.3** 🧑‍🏫 Full survival sweep: run it, compare with the table above, and investigate any gap.
- [ ] **S3.4** 🛠 Simulator validation (slow test): on 1,000 pools, the Monte Carlo mean (2,000 trials) lies within 3·SE of the analytic expected transplants for the ILP plan at p=0.7. Report how many fall outside. About 0.3% is expected by chance; more than 1% means a bug.
- [ ] Open PR by Mon 16 Nov, 6 pm.

### Prompts

**S3.1 🛠: fairness scorer**

```text
[context block]

Implement donorbridge/simulation/fairness.py: FairnessScorer(ExpectedTransplantScorer) with
__init__(survival=1.0, beta=0.0, group="highly_sensitised"); group in {"highly_sensitised","female"}
(ValueError otherwise); weight = survival.cycle(pool, c) * sum(1 + beta * in_group(v) for v in c);
name = f"fair({group},beta={beta},p=...)". Tests: beta=0 equals ExpectedTransplantScorer on 20 random
rings; hand-computed weight for a 3-ring with one in-group patient at p=0.8, beta=1:
0.512 * (1 + 1 + 2) = 2.048.
```

**S3.2 🛠: benchmark harness**

```text
[context block]

Implement donorbridge/simulation/benchmark.py: time_solvers(solver_names, sizes, n_pools, seed,
max_cycle_len=3, time_limit_s=60.0) -> pd.DataFrame with columns
solver, max_len, n, median_s, max_s, n_pools, n_timeouts. Same pools for every solver
(make_generator("india").generate(n, seed + k)); "matching" uses max_cycle_len=2; a run with
Solution.optimal False and solver.exact True counts as a timeout. Find rings once per pool and pass
them via cycles= so enumeration time isn't counted (note this in the docstring). Unit test on tiny sizes.
```

**S3.3 🧑‍🏫: when the table doesn't match**

```text
[context block]

My survival sweep (20 India pools x 100) gives this table: <paste groupby mean table>.
The prototype gave: <paste the target table>. Help me debug, ranked by likelihood: generator
calibration (check p=1.0 first; if that's off it's the generator, not me), scorer used per policy,
count-max being evaluated under p, ring-length filter, ILP returning non-optimal (check optimal flags).
For each, a 5-minute check I can run.
```

### Integration checks that hit your code (Phase 3)

`test_p3_simulation_prototype_table` (slow), `test_p3_simulation_fairness_scorer`, `test_p3_simulation_benchmark_harness`.

---

## 11. Phase 4: Experiments (Tue 17 – Sun 22 Nov) · ◆ feature freeze Mon 23 Nov

**Goal:** two more experiments and **all four charts**, rebuilt by `python -m donorbridge results`.

**Files:** `experiments/fairness.py`, `experiments/runtime.py`, `simulation/plots.py`.

On Tue 17 Nov, 10 am, confirm every CSV's columns with the lead and the other owners. You consume all of them.

| Experiment (`name`) | Settings (full / quick) | CSV columns |
| --- | --- | --- |
| `PriceOfFairness` (`fairness`) | group ∈ {highly_sensitised, female} × β ∈ {0, 0.5, 1, 2, 4}, p = 0.8, ILP L=3; 20 × 100 / 3 × 40 with β ∈ {0, 2} | `group, beta, seed, transplants, expected_transplants, female_matched_share, male_matched_share, hs_matched_share` |
| `Runtime` (`runtime`) | solvers greedy, local-search, matching, branch-bound, ilp; n ∈ {25, 50, 100, 200, 400}; 5 pools; time limit 60 s / n ∈ {20, 40}, 2 pools, limit 10 s | the `time_solvers` columns |

**The four charts**, written by `make_all_figures` to `results/figures/` as PNG (200 dpi) and SVG:

| File | Shows | Built from |
| --- | --- | --- |
| `survival.png` | **The headline.** x: share of final tests that fail (1 − p); y: expected transplants per pool. Three lines (2-way, failure-aware 3-way, count-max 3-way), each with a 95% CI band. Mark p* from `answer.json` and the 3p³ = 2p² crossover at p = 2/3 | `survival_sweep.csv`, `answer.json` |
| `blood_mix.png` | India vs US: % gain from 3-way over 2-way at p ∈ {1.0, 0.8, 0.6} | `blood_mix.csv` (generator owner) |
| `fairness.png` | Two panels (highly sensitised, female). x: β. Left axis: % of expected transplants lost vs β = 0 (price of fairness). Right axis: matched share, female vs male | `fairness.csv`, `female_sensitisation.csv` (generator owner) |
| `runtime.png` | Left: runtime vs n per solver (log y). Right: optimality gap vs n per heuristic. Optional inset: ring count vs n | `runtime.csv`, `optimality_gap.csv` (heuristics owner), `cycle_growth.csv` (matching owner) |

**Chart rules:** one consistent colour per policy and per solver across all charts, chosen colour-blind safe. Every chart title states the takeaway ("3-way rings stop paying off once ~25% of final tests fail"), not the variable names. Axis labels carry units. A missing CSV is skipped with a warning instead of a crash.

### Tasks

- [ ] **S4.1** 🛠 `PriceOfFairness`.
- [ ] **S4.2** 🛠 `Runtime`.
- [ ] **S4.3** 🛠 `plots.py`: one function per chart plus `make_all_figures`. Draft with the AI, then make every visual decision yourself.
- [ ] **S4.4** 🧑‍🏫 Critique the charts: would a non-technical panel get each one in 5 seconds?
- [ ] Open PR by Sun 22 Nov, 6 pm. **Nothing new after the Mon 23 Nov freeze.**

### Prompts

**S4.1–S4.2 🛠: experiments (one chat each)**

```text
[context block]

Implement donorbridge/experiments/<file>.py: class <Name>(Experiment), name "<name>".
Settings and columns: <paste the row from my table>. Use self.pools(...), get_solver, compute_metrics,
FairnessScorer / time_solvers as relevant; self.log progress; return self.write(df).
Quick-mode unit test: columns and row count.
<paste experiments/base.py and the relevant module's signatures>
```

**S4.3 🛠: plots**

```text
[context block]

Implement donorbridge/simulation/plots.py with matplotlib only: plot_survival, plot_blood_mix,
plot_fairness, plot_runtime, and make_all_figures(results_dir) -> list[Path]. Specs:
<paste the four-chart table and chart rules from my playbook>
CSV columns: <paste every CSV's column list>
Define a single PALETTE dict (policy/solver -> colour, colour-blind safe) at the top. Means and 95% CI
from pool-level rows (mean ± 1.96*sd/sqrt(n)). Save PNG (200 dpi) and SVG to results_dir/"figures".
Skip a chart with a warning if its CSV is missing. Unit test: run on tiny synthetic CSVs in tmp_path,
check 4 PNGs exist and are non-empty.
```

**S4.4 🧑‍🏫: chart critique**

```text
[context block]

I'm attaching our four charts (images). For each: what's the first thing a non-technical viewer
sees; does the title state the takeaway; is anything cluttered, mislabelled or misleading (truncated
axes, overlapping CIs presented as a difference); one concrete fix. Then: which single chart should
be the closing slide?
```

### Integration checks that hit your code (Phase 4)

`test_p4_simulation_fa_never_below_two_way`, `test_p4_simulation_count_max_equals_fa_at_p1`, `test_p4_simulation_figures_exist`, plus `test_p4_e2e_results_quick`, which runs all your experiments and plots.

---

## 12. Phase 5: Story (Tue 24 Nov – Mon 7 Dec)

**You own:** the results slides (the crossover chart is the most important slide in the deck), the results section of `DESIGN.md`, and the statistics side of the Q&A.

### Tasks

- [ ] **S5.1** Results section: the reproduced table, the four charts with a two-sentence reading of each, seeds and pool counts, and limitations (one round of re-solve, independent failures, simulated patients).
- [ ] **S5.2** Deck: polish the charts for slides (larger fonts, ≤ 3 lines per chart, annotate p*). Say "real statistics, simulated patients" on the first results slide.
- [ ] **S5.3** 🧑‍🏫 Statistics Q&A drill.
- [ ] **S5.4** Check that the committed `results/` exactly match a fresh `python -m donorbridge results` run, which shows the seeds work. Report any drift to the lead.
- [ ] Rehearsals: Mon 30 Nov dry run plus three timed runs.

### Prompts

**S5.3 🧑‍🏫: statistics drill**

```text
[context block]

You're a statistician on our panel. Ask me 10 questions, one at a time, about our results: why 20
pools, confidence intervals, independence of failures, common random numbers, whether p* is robust,
multiple comparisons, simulated vs real data. After each answer: score 1–5 and a better 2-sentence
answer I can memorise.
```

---

## 13. If you're stuck

- **The Monte Carlo mean disagrees with the formula:** check that you multiply survival over *edges* (|c| of them, not |c| − 1), and that the RNG isn't re-seeded inside the trial loop.
- **The sweep is too slow:** cache the rings per pool (`find_cycles` once, then `cycles=` to each solve), cut `resolve_trials`, and run the ILP with `backend="highs"`.
- **Your numbers are way off the prototype at p = 1.0:** that's the generator, not you. Tell the generator owner and the lead with your table.
- **The fairness result is null or reversed:** that's a finding, not a failure (Plan.md risk row). Show whether the gap is in who enters the pool or in the matcher.
