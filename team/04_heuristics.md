# DonorBridge · Heuristics owner playbook

**Owner:** ____________ · **Role:** Heuristics owner (first-come baseline, greedy, local search, branch and bound)
**The algorithm you present on stage:** branch and bound with its bounding rule. You explain how we get **provably optimal** answers with 3-way rings, by hand, without calling a solver.

You are the answer to the panel's most dangerous question: "You just called a solver." The deck leads with your branch and bound and calls the ILP only the oracle that checks it. Your ladder (first-come → greedy → local search → B&B) is also the clearest way to show algorithm choice (rubric item 4).

## Architecture at a glance

```text
Calibration ─► SaidmanGenerator ─► Pool ─► CompatibilityGraph ─► CycleFinder ─► rings
                                                                                 │
              Scorer (count | expected | fair) ─► Solver (7 rungs, one base) ◄───┘
                                                     │
                                                     ▼
                       Solution ─► metrics + FailureSimulator + NightBeforeSimulator
                                                     │
   GridSpec (a list of settings) ─► run_grid (one engine, parallel, rings cached) ─► results/<name>.csv
                                                     │                                (one shared column set)
                                                     ▼
                                         answer.json + 4 charts + demos
```

Six decisions hold the design together. Each was picked over a simpler-looking or a heavier alternative:

| Decision | What we do | What we rejected, and why |
| --- | --- | --- |
| **Contract first** | The lead commits every module as a stub with exact signatures before anyone codes. You only ever fill in your own stubs. | Agreeing interfaces as we go: that's where merge conflicts and last-minute fixes come from |
| **One Solver base class** | Seven solvers share `Solver.solve()` (find rings → `_solve()` → score → validate). You write only `_solve()`. | Separate scripts per solver: duplicated timing, scoring and validation; no visible OOP |
| **Scorer is passed in** | Count, expected-transplant and fairness weights are objects passed to any solver. Failure-awareness costs no extra code in the solvers. | A flag inside each solver: seven places to get it wrong |
| **One experiment engine** | Every experiment is a list of `Setting`s run by `run_grid`. It makes the pools, finds rings once per pool, runs pools in parallel and writes the same columns every time. | One class per experiment: ten copies of the same loop and ten CSV formats to negotiate |
| **Merge early, gate late** | Merge green work to `main` as soon as it's ready. Each phase still ends with one strict gate. | Merging everything on the last night: every integration bug lands at once |
| **Stubs skip, the gate fails them** | An unfinished stub shows as *skipped* in the integration tests. `--gate` turns those skips into failures. | Tests that stay red until merge day: no visible progress, and CI is always red |

## 1. How we work: the phase loop

We build in five phases. **Nobody starts phase N+1 until phase N passes its gate:** `pytest tests/unit tests/integration/test_phaseN.py --gate` is green on `main`.

| Phase | Dates | The phase is done when |
| --- | --- | --- |
| **P0 Contract** (lead only) | Mon 2 Nov evening | Every module stub, the test configuration with the `--gate` flag, CI, and fixtures are on `main` by Tue 3 Nov, 9 am |
| **P1 Foundations** | Tue 3 – Thu 5 Nov | Contract, data model, generator, graph + cycle finder, first-come + greedy, metrics + failure simulator all work end to end on one pool |
| **P2 Engine v1** | Fri 6 – Tue 10 Nov | ILP matches kep_solver on Glasgow pools; brute force, local search, branch and bound v1, night-before re-solve, `python -m donorbridge run` |
| **P3 Exact solvers + failure model** | Wed 11 – Mon 16 Nov | Matching, branch and bound with its bound, failure-aware scoring in every solver, 1,000-pool cross-check green. ◆ Gate: checks all green, 16 Nov |
| **P4 Experiments** | Tue 17 – Sun 22 Nov | Every experiment, all four charts and the answer rebuild from one command. ◆ **Feature freeze Mon 23 Nov** |
| **P5 Story** | Tue 24 Nov – Mon 7 Dec | Design file, AI log, deck, demo, release check, three rehearsals |

Every phase runs the same seven steps:

1. **Day 1, 10 am.** The lead pushes `tests/integration/test_phaseN.py` to `main`. That file *is* the definition of done for the phase. Read every test whose name contains your role.
2. **Branch.** `git checkout main && git pull && git checkout -b pN/<role>` (for example `p1/generator`).
3. **Build.** Touch only the files you own (see the module map), your unit tests, `ai_logs/<role>.md` and `docs/design/<role>.md`. Need a change in someone else's file or in the contract? Message the lead. The lead changes `main`, and you run `git merge main`.
4. **Merge early.** As soon as one piece passes its unit tests, open a PR `pN/<role> → main`. CI runs on every PR, and the lead merges any green PR the same day, in any order (files never overlap, so order doesn't matter). **Aim for a first merge by the middle of the phase.** Small merges surface integration problems on day 2, not on the last night. Then `git merge main` into your branch to pick up everyone else's work.
5. **Watch the progress board.** CI runs `test_phaseN.py` on every push to `main`. A test whose code is still a stub shows as *skipped*, not failed, so the skip count is the work left in the phase. Locally: `pytest tests/integration/test_phaseN.py -k <role> -rs`.
6. **Last day, 6 pm: final PRs in.** The lead runs the gate: `pytest tests/unit tests/integration/test_phaseN.py --gate` (plus `--run-slow` at the P3 and P4 gates). `--gate` turns every stub-skip into a failure. Each failure goes to the owner of the module that failed, and the fix goes on a `pN/fix-<topic>` branch the same evening.
7. **Gate passed.** With zero failures, the lead tags `phase-N-done` and posts in the group chat. Only then does anyone start phase N+1.

Finished early? Pair with someone who is behind, review their PR, or add unit tests for their module. Read ahead if you like, but don't write next-phase code.

## 2. Rules for every task

- **Python 3.11.** Libraries: standard library, numpy, pandas, matplotlib, networkx, pulp==2.9.0, highspy, pytest. Add nothing else without asking the lead.
- **Type hints and docstrings** on every public class and function.
- **No global random state.** Every random function takes `seed: int` or `rng: random.Random`. Never call `random.seed()` or `np.random.*` at module level. Same seed, same output, every time.
- **Family ids are unique ints, not positions.** Never use an id as a list index. Use `pool.family(fid)` or a dict.
- **Unit tests** go in `tests/unit/test_<module>.py`. Each test runs in under 1 s unless it is marked `@pytest.mark.slow`.
- **Partial work is mergeable, fake work is not.** Anything you haven't finished keeps raising `NotImplementedError("<owner>, P<n>")`, so it shows as skipped. Never return a placeholder value: it would pass silently and break someone else's results.
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

After every prompt, add an entry to `ai_logs/<role>.md` (yours: `ai_logs/heuristics.md`). The lead merges these into `AI_LOG.md` in P5.

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

The lead's contract commit (Phase 0) lands on `main` by **Tue 3 Nov, 9 am**. After it lands:

```bash
git clone <repo-url> && cd DonorBridge          # or: git pull
python3.11 -m venv .venv
source .venv/bin/activate                        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
pytest -q -rs                                    # stubs import; unfinished work shows as "skipped" — expected
python -m donorbridge --help
```

Only the lead (and anyone running the oracle tests) also needs kep_solver. It goes into the **same** environment, because our ILP already pins pulp==2.9.0, the version kep_solver needs (it breaks on PuLP 4.x):

```bash
pip install -e ".[oracle]"
```

If that install clashes with our dependencies, the lead switches to the fallback in the lead playbook (L2.3): a separate `.venv-oracle` called via subprocess. Nobody else needs to change anything.

## 5. Module map (who owns what)

Every file below exists from the lead's Phase 0 skeleton commit, as a stub that raises `NotImplementedError("<owner>, P<n>")`. You fill in your own stubs and never create new modules under `donorbridge/`. That rule is what makes the merges conflict-free.

| Path (under `donorbridge/` unless noted) | Owner | Phase | Public names |
| --- | --- | --- | --- |
| `pyproject.toml`, `requirements*.txt`, `.github/`, `README.md`, every `__init__.py`, `__main__.py` (CLI) | Lead | P1 | `python -m donorbridge {run,sweep,bench,results,demo}` |
| `models.py` | Lead | P1 | `BloodGroup`, `Sex`, `Relation`, `Family`, `Pool`, `Cycle`, `Solution`, `InvalidSolutionError` |
| `survival.py` | Lead | P1 | `SurvivalModel`, `UniformSurvival` |
| `scoring.py` | Lead | P1 | `Scorer`, `CountScorer`, `ExpectedTransplantScorer` |
| `solvers/base.py`, `solvers/__init__.py` | Lead | P1 | `Solver`, `SOLVERS`, `get_solver` |
| `solvers/ilp.py` | Lead | P2–P3 | `ILPSolver` (`"ilp"`) |
| `oracle/glasgow.py`, `oracle/kep_oracle.py` | Lead | P2 | `load_glasgow`, `list_instances`, `kep_optimum` |
| `oracle/crosscheck.py` | Lead | P3 | `crosscheck`, `CrosscheckReport` |
| `experiments/answer.py` | Lead | P4 | `compute_answer` |
| `tests/conftest.py`, `tests/fixtures/`, `tests/integration/` (repo root) | Lead | P0, then every phase | `load_fixture`, the `--gate` / `--run-slow` options, `test_phaseN.py` |
| `compatibility.py` | Generator | P1 | `blood_compatible` |
| `generator/calibration.py` | Generator | P1–P2 | `Calibration`, `INDIA`, `US` |
| `generator/saidman.py` | Generator | P1–P2 | `PoolGenerator`, `SaidmanGenerator`, `GenerationReport`, `make_generator` |
| `generator/report.py` | Generator | P2 | `calibration_report` |
| `generator/survival_models.py` | Generator | P3 | `SensitisationSurvival` |
| `generator/regions.py` | Generator | P3 | `split_by_region` |
| `experiments/blood_mix.py`, `experiments/female_sensitisation.py`, `experiments/regions.py` | Generator | P4 | `SPEC` (a `GridSpec`) in each |
| `graph.py` | Matching | P1 | `CompatibilityGraph` |
| `cycles.py` | Matching | P1 | `CycleFinder`, `find_cycles`, `find_cycles_nested_loops` |
| `solvers/brute_force.py` | Matching | P2 | `BruteForceSolver` (`"brute-force"`) |
| `solvers/matching.py` | Matching | P3 | `MatchingSolver` (`"matching"`) |
| `demos/scripts.py`, `notebooks/demo.ipynb` (repo root), `experiments/cycle_growth.py` | Matching | P4 | `DEMOS`, `demo_small`, `demo_india`, `demo_edge`; `SPEC` |
| `solvers/first_come.py`, `solvers/greedy.py` | Heuristics | P1 | `FirstComeSolver` (`"first-come"`), `GreedySolver` (`"greedy"`) |
| `solvers/local_search.py` | Heuristics | P2 | `LocalSearchSolver` (`"local-search"`) |
| `solvers/branch_bound.py` | Heuristics | P2–P3 | `BranchAndBoundSolver` (`"branch-bound"`) |
| `experiments/optimality_gap.py`, `experiments/ring_length.py` | Heuristics | P4 | `SPEC` in each |
| `simulation/metrics.py` | Simulation | P1 | `PoolMetrics`, `compute_metrics` |
| `simulation/failure.py` | Simulation | P1 | `FailureSimulator`, `FailureOutcome` |
| `simulation/resolve.py` | Simulation | P2 | `NightBeforeSimulator`, `ResolveOutcome` |
| `experiments/grid.py` (the engine), `experiments/survival_sweep.py` | Simulation | P2–P3 | `Setting`, `GridSpec`, `ROW_COLUMNS`, `run_grid`; `SPEC` |
| `simulation/fairness.py` | Simulation | P3 | `FairnessScorer` |
| `experiments/fairness.py`, `experiments/runtime.py`, `simulation/plots.py` | Simulation | P4 | `SPEC` in each; `make_all_figures` |

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

# donorbridge/experiments/grid.py (simulation): ONE engine runs every experiment
@dataclass(frozen=True)
class Setting:                    # one configuration; every field has a default
    label: str = ""               # e.g. "two_way"; copied into the CSV
    preset: str = "india"
    n: int = 100
    overrides: tuple[tuple[str, float], ...] = ()   # generator overrides, e.g. (("female_hs_share", 0.3),)
    split_regions: bool = False   # solve each region's sub-pool separately and add up
    solver: str | None = "ilp"    # None = only enumerate rings (timing / ring counts)
    max_len: int = 3
    scorer: str = "expected"      # "count" | "expected" | "fair"
    p: float = 1.0                # survival: used by the scorer AND to evaluate every plan
    survival: str = "uniform"     # "uniform" | "sensitisation"
    beta: float = 0.0             # fair scorer only
    group: str = "highly_sensitised"   # fair scorer only: "highly_sensitised" | "female"
    time_limit_s: float | None = None
    resolve_trials: int = 0       # > 0: mean of NightBeforeSimulator over this many draws
@dataclass(frozen=True)
class GridSpec:
    name: str                     # output is results/<name>.csv
    settings: tuple[Setting, ...]
    n_pools: int = 20
    quick_settings: tuple[Setting, ...] = ()   # empty = reuse settings with n capped at 40
    quick_n_pools: int = 3
ROW_COLUMNS: tuple[str, ...]      # EVERY experiment CSV has exactly these columns, one row per (setting, pool):
#   experiment, label, preset, n, seed, overrides, split_regions, solver, max_len, scorer, p, survival,
#   beta, group, objective, transplants, expected_transplants, optimal, runtime_s, enum_s,
#   rings_2, rings_3, rings_4, hs_matched_share, female_matched_share, male_matched_share, resolve_mean
#   (expected_transplants = ExpectedTransplantScorer(survival at p).total(plan), whatever the solver's scorer)
def run_grid(spec: GridSpec, out_dir: Path = Path("results"), quick: bool = False,
             seed: int = 2026, workers: int = 0) -> "pd.DataFrame": ...
#   pool i of every setting uses seed + i (paired comparisons); rings are found once per pool and passed
#   to every solve via cycles=; pools run in parallel (workers=0 -> os.cpu_count(), 1 -> serial, same output)
# donorbridge/experiments/__init__.py: EXPERIMENTS: dict[str, GridSpec]   (each experiment module exposes SPEC)

My role: Heuristics owner (first-come baseline, greedy, local search, branch and bound).
I own: donorbridge/solvers/first_come.py, solvers/greedy.py, solvers/local_search.py, solvers/branch_bound.py, experiments/optimality_gap.py, experiments/ring_length.py, and their tests in tests/unit/.
````

## 7. Before Phase 1 (today, Mon 2 Nov: design gate)

- [ ] `docs/design/heuristics.md` has dated pseudocode and a flowchart for: first-come, greedy, local search, and branch and bound (both v1 and v2 below).
- [ ] Run each algorithm by hand on the `greedy_trap` fixture (section 5) and on the week-1 8-family pool. Write down what each one returns. These become your unit tests.
- [ ] List the unit-test cases you'll write in P1.

**Prompt H0.1 🧑‍🏫: design-gate check**

```text
[paste context block]

Here is my pseudocode for first-come, greedy, local search and branch and bound (dated). Don't write
code.
1. Turn each into a mermaid flowchart.
2. For each, find an input where it does something I wouldn't expect (ties, empty ring list,
   zero-weight rings at p=0).
3. Check my B&B bound: is it a valid UPPER bound on what the remaining families can add? If not,
   give a counterexample.
4. List 10 unit tests to write first, with expected outputs.
<paste docs/design/heuristics.md>
```

---

## 8. Phase 1: Foundations (Tue 3 – Thu 5 Nov)

**Goal:** two working rungs at the bottom of the ladder, both deterministic and both going through the shared `Solver` template method.

**Files:** `solvers/first_come.py`, `solvers/greedy.py`, `tests/unit/test_first_come.py`, `tests/unit/test_greedy.py`.
**Branch:** `p1/heuristics` (after the lead's contract commit, Tue 9 am).

Implement only `_solve(self, pool, cycles)`. The base class already finds rings, times the run, scores it and validates. Use `self.weights(pool, cycles)` for every comparison, **never `len(c)`**. In P3 that is what makes your solvers failure-aware for free.

| Solver | Rule |
| --- | --- |
| `FirstComeSolver` (`"first-come"`, `exact=False`) | Family ids are arrival order. A ring becomes available when its last family arrives (its max id). Go through rings sorted by `(max id, len, families)` and take each one that is disjoint from those already taken. It ignores weights on purpose: this is the naive baseline. |
| `GreedySolver` (`"greedy"`, `exact=False`) | Sort rings by weight (descending). Break ties first by **fewest conflicts** (how many other rings share a family with it, ascending), then by `families`. Take each ring that is disjoint from those already taken. |

### Tasks

- [ ] **H1.1** 🧑‍🏫 Write `FirstComeSolver` yourself.
- [ ] **H1.2** 🧑‍🏫 Write `GreedySolver` yourself, including the conflict-count tie-break.
- [ ] **H1.3** 🛠 Unit tests. Pass hand-written ring lists as `cycles=` so you don't depend on the cycle finder before it reaches `main`. Cover: greedy_trap → greedy gets 3; ring_vs_swap (count) → ring; ring_vs_swap with `ExpectedTransplantScorer(0.6)` → swap; empty → no rings; ties resolved deterministically.
- [ ] Open PR `p1/heuristics → main` by Thu 6 pm.

### Prompts

**H1.1–H1.2 🧑‍🏫: tutor for first-come and greedy**

```text
[context block]

I'm hand-writing two baseline solvers as subclasses of Solver; I implement only _solve(pool, cycles)
and return (chosen_rings, optimal_flag, stats). Rules:
<paste the first-come / greedy table from my playbook>
Don't write the code. Instead:
1. Point out what data structure makes "is this ring disjoint from what I've taken?" O(|ring|).
2. How do I compute conflict counts for all rings in O(total ring size) using a family -> rings index?
3. Why is greedy's worst case at most a factor of 3 below optimal for rings of size <= 3 under
   count weights? (Intuition only; I may use it on stage.)
4. What should stats contain (rings considered, rings taken)?
5. On greedy_trap (rings (0,3), (1,2), (0,1,2)), trace both solvers.
```

**H1.3 🧑‍🏫: review my solvers**

```text
[context block]

Review my first-come and greedy solvers against the rules and contract. Check: uses self.weights
(never len) in greedy; deterministic tie-breaks; no mutation of the input list; correct return tuple.
Point to lines; minimal fixes only.
<paste solvers/first_come.py and solvers/greedy.py>
```

**H1.4 🛠: unit tests**

```text
[context block]

Write tests/unit/test_first_come.py and tests/unit/test_greedy.py. Build tiny pools with a helper
make_pool(ids, edges) (dummy Family fields), pass explicit cycles=[Cycle.of(...), ...] to solve().
Cases: <paste my case list from H1.3 task>. Also assert Solution.optimal is False and that calling
solve twice gives identical Solutions (ignore runtime_s).
```

### Integration checks that hit your code (Phase 1)

`test_p1_heuristics_first_come_valid`, `test_p1_heuristics_greedy_on_fixtures`, `test_p1_e2e_pipeline_india_100` (greedy) and `test_p1_e2e_solver_names_resolve`. Run them with `pytest tests/integration/test_phase1.py -k heuristics`.

---

## 9. Phase 2: Engine v1 (Fri 6 – Tue 10 Nov)

**Goal:** local search climbs out of the greedy trap, and branch and bound v1 is exact on small pools.

**Files:** `solvers/local_search.py`, `solvers/branch_bound.py`, tests.

| Solver | Rule |
| --- | --- |
| `LocalSearchSolver` (`"local-search"`, `exact=False`) | Start from greedy. Repeat passes until no move improves or `time_limit_s` runs out. **Add:** any ring disjoint from the solution with weight > 0. **Swap 1-out, up-to-2-in:** remove one chosen ring r; among rings that use only r's families and uncovered families, find the best set of at most 2 disjoint rings; apply if its weight > w(r) + 1e-9. In each pass, apply the single best improving move (best-improvement, deterministic). |
| `BranchAndBoundSolver` v1 (`"branch-bound"`, `exact=True`) | Rings sorted by weight (descending). Branch: include ring i (if disjoint) / exclude ring i. Bound: current + sum of weights of the remaining rings that are still disjoint from the chosen ones. Prune if bound ≤ best + 1e-9. The incumbent starts from greedy. Timeout → best found, `optimal=False`. |

### Tasks

- [ ] **H2.1** 🧑‍🏫 Write `LocalSearchSolver` yourself.
- [ ] **H2.2** 🧑‍🏫 Write B&B v1 yourself: simple bound, include/exclude branching, time limit, and stats (`nodes`, `pruned`, `timed_out`).
- [ ] **H2.3** 🛠 Tests: greedy_trap → local search 4; local search ≥ greedy on 50 random pools; B&B == brute force on small pools (merge `main` after `phase-1-done`). Wait for the matching owner's brute force on `main`, or compare against fixture optima until it lands.
- [ ] Open PR by Tue 10 Nov, 6 pm.

### Prompts

**H2.1 🧑‍🏫: local search**

```text
[context block]

I'm hand-writing LocalSearchSolver. Rules: <paste local search row>. Tutor me; don't write it.
1. How do I find "the best set of at most 2 disjoint rings using only r's families + uncovered
   families" efficiently? (Candidate filtering via a family -> rings index; then try singles and
   pairs.)
2. Why does this escape the greedy_trap? Trace it.
3. Give me a small pool where this local search still gets stuck below optimal (a move needing
   2-out). I'll show it on stage as the reason we need exact methods.
4. Termination: prove every applied move strictly increases weight, so it terminates.
```

**H2.2 🧑‍🏫: branch and bound v1**

```text
[context block]

I'm hand-writing branch and bound v1 for choosing disjoint rings. Rules: <paste B&B v1 row>.
Tutor me, don't write it.
1. Why is "current + sum of remaining disjoint rings' weights" a valid upper bound? Why is it weak?
2. Recursive vs explicit stack: how do I add a time limit cleanly to either (check
   time.perf_counter() every k nodes)?
3. How do I make sure a timed-out run still returns a VALID solution (the incumbent)?
4. On greedy_trap and ring_vs_swap (p=0.6 and p=0.9), trace the tree and count nodes.
```

**H2.3 🧑‍🏫: review**

```text
[context block]

Review my local search and B&B v1: correctness, termination, determinism, the time-limit path, use of
self.weights, stats. Then give me 3 tiny inputs (rings + weights) where B&B with an off-by-one or a
wrong prune would return a non-optimal answer, with the true optimum.
<paste solvers/local_search.py and solvers/branch_bound.py>
```

### Integration checks that hit your code (Phase 2)

`test_p2_heuristics_local_search_fixes_trap`, `test_p2_heuristics_never_beat_ilp`, `test_p2_heuristics_bnb_v1_equals_ilp_small`, plus your solvers in `test_p2_e2e_cli_every_solver`.

---

## 10. Phase 3: Exact solvers and failure model (Wed 11 – Mon 16 Nov) · ◆ gate 16 Nov

**Goal:** B&B v2, with a strong bound and smart branching, is exact and fast enough on pools of 30, and it agrees with the ILP on every one of the 1,000 cross-check pools. **This is the plan's #1 reputational risk.** If it's red on Fri 13 Nov, pair with the lead that day.

**B&B v2 rules** (replace v1 in the same file):

- **State:** chosen rings; a set of *decided* families (covered, or explicitly left unmatched). A ring is *available* if none of its families is decided.
- **Branch on a family, not a ring.** Pick the undecided family v with the **fewest available rings** (most constrained first; ties by id). Children: one per available ring containing v (best weight first), then "v left unmatched".
- **Bound:** `current + Σ over undecided families u of max over available rings c ∋ u of w_c / |c|`. Each ring's weight is shared equally among its families, and each family is in at most one chosen ring, so this can never undercount.
- **Incumbent:** start from the local-search solution.
- **Prune** if bound ≤ best + 1e-9. **Time limit** → return the incumbent with `optimal=False`.
- **Stats:** `nodes`, `pruned`, `timed_out`, `root_bound`, `time_to_best`.

### Tasks

- [ ] **H3.1** 🧑‍🏫 Prove the bound is valid (a short argument in `docs/design/heuristics.md`). You will be asked about it on stage.
- [ ] **H3.2** 🧑‍🏫 Implement v2 yourself. Keep v1 as a private method or behind a flag (`stats["version"]`) for the runtime comparison.
- [ ] **H3.3** 🛠 Tests: B&B == ILP on 50 pools of 20 and 30, under both scorers. Time limit: n=200 with `time_limit_s=1` returns a valid solution in < 1.5 s. Node count v2 < v1 on the same pools.
- [ ] **H3.4** 🛠 Make sure all four of your solvers handle `ExpectedTransplantScorer` and `SensitisationSurvival` correctly. ring_vs_swap at p=0.6 must pick the swap. The lead audits this in L3.3.
- [ ] Open PR by Mon 16 Nov, 6 pm.

### Prompts

**H3.1 🧑‍🏫: the bound**

```text
[context block]

My B&B v2 bound: UB = current + sum over undecided families u of max_{available ring c containing u}
(w_c / |c|). Help me write a rigorous but short (6–8 line) proof that UB >= the best completion's
value, for any non-negative weights. Then: is it tight on greedy_trap at the root? Compute it. Then
suggest one stronger bound I could mention as "future work" (e.g. LP relaxation) and why we don't use it.
```

**H3.2 🧑‍🏫: implement v2 (review loop)**

```text
[context block]

Here's my B&B v2 so far. Rules: <paste B&B v2 rules>. Review only: (1) is the branching complete,
i.e. does every feasible solution lie in some leaf? (2) is the bound computed over AVAILABLE rings
only? (3) do I restore state correctly when backtracking? (4) is the time-limit check cheap? Point to
lines. Then suggest the 2 cheapest speed-ups (e.g. precompute family -> rings; incremental bound).
<paste solvers/branch_bound.py>
```

**H3.3 🛠: tests**

```text
[context block]

Write tests/unit/test_branch_bound.py: v2 == brute force on 30 pools of 10 (both scorers);
v2 == ILP on 50 pools of 20 and 30 (mark slow); time-limit test on n=200 (valid, optimal False,
< 1.5 s); node count v2 < v1 on 10 pools of 20; ring_vs_swap at p=0.6 -> swap, p=0.9 -> ring.
Pools from make_generator("india").generate(n, seed).
```

### Integration checks that hit your code (Phase 3)

`test_p3_heuristics_bnb_equals_ilp`, `test_p3_heuristics_bnb_time_limit`, `test_p3_lead_failure_aware_all_exact_solvers`, and the B&B and heuristic rows of `test_p3_e2e_crosscheck_1000` (the gate).

---

## 11. Phase 4: Experiments (Tue 17 – Sun 22 Nov) · ◆ feature freeze Mon 23 Nov

**Goal:** the numbers behind chart 4 (optimality gap) and the Plan.md decision "longest swap allowed" (do 4-family rings add much?).

**Files:** `experiments/optimality_gap.py`, `experiments/ring_length.py`. Each is just `SPEC = GridSpec(...)`. The shared `run_grid` engine does the loops, ring caching, parallelism and the `ROW_COLUMNS` CSV. Because pool i has the same seed in every setting, the ILP row and the heuristic rows for a pool line up, and the gap is computed at plot time: `gap = (ilp − obj) / ilp`, joined on `(seed, n, p)`.

| `SPEC.name` | Settings | Expressed as `Setting`s |
| --- | --- | --- |
| `optimality_gap` | n ∈ {20, 50, 100, 200} × p ∈ {1.0, 0.8} × solver ∈ {first-come, greedy, local-search, branch-bound, ilp}; 10 pools. Quick: n ∈ {20, 40}, 2 pools | `Setting(label=solver, solver=solver, n=n, p=p, scorer="count" if p == 1.0 else "expected", time_limit_s=30)` |
| `ring_length` | L ∈ {2, 3, 4} × n ∈ {25, 50, 100} × p ∈ {1.0, 0.8, 0.6}; ILP; 20 pools. Quick: n=30, 2 pools | `Setting(label=f"L{L}", max_len=L, n=n, p=p, time_limit_s=120)` |

### Tasks

- [ ] **H4.1** 🛠 Both `SPEC`s (one short chat). Run each with `python -m donorbridge results --only <name> --quick`.
- [ ] **H4.3** 🧑‍🏫 Interpret: where does B&B stop finishing within 30 s? How big is greedy's gap at n=100? What do 4-rings add at p=0.8? Write 3 bullet findings for the deck.
- [ ] Open PR by Sun 22 Nov, 6 pm. **Nothing new after the Mon 23 Nov freeze.**

### Prompts

**H4.1 🛠: the two specs**

```text
[context block]

Write SPEC = GridSpec(...) in donorbridge/experiments/optimality_gap.py and ring_length.py from:
<paste my two-row SPEC table>
Settings via list comprehensions, as tuples; quick_settings and pool counts filled in; no other code.
Then give me a pandas snippet (for a notebook) that joins each heuristic row to the ilp row on
(seed, n, p), computes gap = (ilp - obj) / ilp (0 if ilp == 0), and prints mean/max gap and median
runtime_s by solver and n.
```

**H4.3 🧑‍🏫: interpret**

```text
[context block]

Here are summary tables (mean, max gap and median runtime by solver and n; and mean objective by L and p).
Give me: 3 findings in one sentence each, what's surprising, what a CS professor would challenge
(sample size, time limits, pool sizes) and how to answer.
<paste groupby summaries>
```

### Integration checks that hit your code (Phase 4)

`test_p4_heuristics_gap_and_ring_length` (heuristics ≤ ILP per pool; mean L=4 ≥ L=3 ≥ L=2), `test_p4_e2e_every_spec_nonempty`, plus `test_p4_e2e_results_quick`.

**Freed-up time:** with the specs done in about an hour, spend P4 on H4.3 and on speeding up B&B. A faster B&B at n=50 makes a much stronger slide than another experiment.

---

## 12. Phase 5: Story (Tue 24 Nov – Mon 7 Dec)

**You own:** the "algorithm ladder" slide, the "hand-written branch and bound" slide, and the answer to "you just called a solver".

### Tasks

- [ ] **H5.1** Design-file section: final flowcharts and pseudocode for all four solvers, the bound proof, and justification for each rung (what it costs, what it gains, where it fails).
- [ ] **H5.2** Slide: the ladder as a table of solver, idea, exact?, runtime at n=100, and gap at n=100, taken from your CSV.
- [ ] **H5.3** 🧑‍🏫 Rehearse the B&B explanation (90 s) and the "you just called a solver" rebuttal.
- [ ] Rehearsals: Mon 30 Nov dry run plus three timed runs.

### Prompts

**H5.3 🧑‍🏫: stage prep**

```text
[context block]

1. Cut my B&B explanation (pasted) to 90 seconds / 200 words for smart non-specialists, with one
   concrete picture (the search tree on greedy_trap).
2. Act as a CS professor who says "So you just called an ILP solver?" Push back 4 times, harder each
   time; after each of my answers, score 1–5 and suggest a sharper reply that cites our evidence
   (hand-written B&B == ILP on 1,000 pools; ILP == kep_solver on Glasgow pools).
<paste my draft>
```

---

## 13. If you're stuck

- **B&B disagrees with the ILP:** dump the pool (`pool.save_json`), then run brute force on it if it's small. Compare chosen rings. Usual culprits: the bound uses rings that are no longer available, state isn't restored on backtrack, or a prune uses `<` where it should use `≤` (or the reverse).
- **B&B is too slow:** check the incumbent starts from local search, branching is on the most-constrained family, and the bound is computed incrementally. Profile before guessing (`python -m cProfile`).
- **Still red on Fri 13 Nov:** pair with the lead (Plan.md risk row). Final fallback is cut line #5: drop B&B and keep matching, greedy and the ILP. Avoid it if at all possible, because it weakens the talk.
