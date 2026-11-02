# DonorBridge · Matching owner playbook

**Owner:** ____________ · **Role:** Matching owner (graph, cycle finder, exact 2-way matching, brute-force verifier, demos)
**The algorithms you present on stage:** depth-first cycle search (how we list every possible swap ring) and augmenting-path matching (why 2-way swaps are solvable in polynomial time).

Every solver consumes your ring list. If the cycle finder misses a ring, every solver is quietly wrong, and the ILP oracle won't catch it, because the ILP uses the same list. That is why your cross-check against networkx matters so much. In P4 you also own the demos: the part of the talk the audience remembers.

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

- **Python 3.11, managed by uv.** Libraries: standard library, numpy, pandas, matplotlib, networkx, pulp==2.9.0, highspy, pytest. Add nothing else without asking the lead. Only the lead changes dependencies (with `uv add`), and nobody runs `pip install` in the project (see section 4).
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

After every prompt, add an entry to `ai_logs/<role>.md` (yours: `ai_logs/matching.md`). The lead merges these into `AI_LOG.md` in P5.

```markdown
### 2026-11-03 · G1.3 · Saidman generator pseudocode review
- Tool: Claude / ChatGPT / Copilot
- Prompt: G1.3 as written (or what you changed)
- Kept: what you used from the answer
- Corrected: what the AI got wrong, and how you caught it (a failing test, the paper, a teammate)
- Time: roughly how much it saved or cost
```

The graders care most about **Corrected**, so keep it honest. "The AI said O-patients can receive from A donors; the exhaustive ABO test caught it" is a great entry.

**Reports are the AI's job, not yours.** The context block in section 6 tells the AI to write a report to `report/03_matching/` after every task that creates or changes files. The report says what was done, what deviated from the plan and what to watch out for, and later AI chats read it for context. You don't write these. If the AI can't write files itself, it ends its answer with the report as a code block: save that unchanged under the path it gives, and commit it with the work.

## 4. One-time setup

DonorBridge is a [uv](https://docs.astral.sh/uv/) project. uv installs Python 3.11 for you (pinned in `.python-version`) and every library at the exact version in `uv.lock`, so all five of us run identical environments. Install uv once:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh                                      # macOS / Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows
```

The lead's contract commit (Phase 0) lands on `main` by **Tue 3 Nov, 9 am**. After it lands:

```bash
git clone <repo-url> && cd DonorBridge          # or: git pull
uv sync                                          # creates .venv with Python 3.11 and installs everything, including donorbridge itself
uv run pytest -q -rs                             # stubs import; unfinished work shows as "skipped" — expected
uv run python -m donorbridge --help
```

**Running commands.** This playbook writes commands as plain `pytest ...` and `python -m donorbridge ...`. Either put `uv run` in front of each one, or activate the environment once per terminal with `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`) and type them as written. After every `git pull`, run `uv sync` again in case the lead changed a dependency.

**Never `pip install` into the project.** It bypasses `uv.lock`, and your environment drifts from everyone else's. Need a library? Ask the lead, who adds it with `uv add` and commits the updated `pyproject.toml`, `uv.lock` and `requirements.txt`.

No uv (for example, a grader's machine)? `requirements.txt` is exported from the lock as a fallback: create a Python 3.11 venv, then `pip install -r requirements.txt && pip install -e .`.

Only the lead (and anyone running the oracle tests) also needs kep_solver. It goes into the **same** environment as an optional extra, because our ILP already pins pulp==2.9.0, the version kep_solver needs (it breaks on PuLP 4.x):

```bash
uv sync --extra oracle
```

A plain `uv sync` removes kep_solver again, so run the oracle tests with `uv run --extra oracle pytest -m oracle`. If the extra clashes with our dependencies, uv refuses to lock it, and the lead switches to the fallback in the lead playbook (L2.3): a separate `.venv-oracle` called via subprocess. Nobody else needs to change anything.

## 5. Module map (who owns what)

Every file below exists from the lead's Phase 0 skeleton commit, as a stub that raises `NotImplementedError("<owner>, P<n>")`. You fill in your own stubs and never create new modules under `donorbridge/`. That rule is what makes the merges conflict-free.

| Path (under `donorbridge/` unless noted) | Owner | Phase | Public names |
| --- | --- | --- | --- |
| `pyproject.toml`, `uv.lock`, `.python-version`, `requirements.txt` (exported from the lock), `.github/`, `README.md`, every `__init__.py`, `__main__.py` (CLI) | Lead | P1 | `python -m donorbridge {run,sweep,bench,results,demo}` |
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

Paste everything in this box at the start of **every** new AI chat. The last three lines are already filled in for you.

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
- The project is managed with uv. Give commands as `uv run pytest ...` and `uv run python -m donorbridge ...`.
  Never suggest `pip install`: dependencies live in pyproject.toml / uv.lock and only the lead changes them.
- Type hints + docstrings on every public class/function. Readable over clever: I must explain every
  line in a viva.
- No global random state. Every random function takes `seed: int` or `rng: random.Random`.
- Family ids are unique ints but NOT necessarily 0..n-1. Never use an id as a list index.
- The contract below is frozen. Code against it exactly. If it looks wrong, say so and STOP; do not
  change or extend it.
- Only touch the files I own. Tests go in tests/unit/test_<module>.py using pytest.
- Reports are your job, not mine. Whenever you create or change files, finish by writing a short
  markdown report to my report folder (named at the end of this block) as NN_<topic>.md, where NN is
  the next free number. Read the earlier reports in that folder first for context. Cover: what was
  asked, what you did, every deviation from the request or the contract and why, things to note,
  and next steps. The report folder is the one exception to "only touch the files I own". If you
  cannot write files, end your answer with the report as a code block headed by its path.

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

My role: Matching owner (compatibility graph, cycle finder, exact 2-way matching, brute-force verifier, demos).
I own: donorbridge/graph.py, cycles.py, solvers/brute_force.py, solvers/matching.py, demos/scripts.py, experiments/cycle_growth.py, notebooks/demo.ipynb, and their tests in tests/unit/.
My report folder: report/03_matching/
````

## 7. Before Phase 1 (today, Mon 2 Nov: design gate)

- [ ] `docs/design/matching.md` has dated pseudocode and a flowchart for: `CompatibilityGraph`, `CycleFinder.find` (DFS), `find_cycles_nested_loops`, `BruteForceSolver`, `MatchingSolver`.
- [ ] Solve these by hand on paper, because they become your first unit tests: all rings with L=3 in a triangle 0→1→2→0; in a graph with both 0→1→2→0 and 0→2→1→0; and in the `greedy_trap` fixture (section 5).
- [ ] List the unit-test cases you'll write in P1.

**Prompt M0.1 🧑‍🏫: design-gate check**

```text
[paste context block]

Here is my pseudocode for the cycle finder and the brute-force verifier (dated). Don't write code.
1. Turn each into a mermaid flowchart.
2. Does my DFS find every simple ring of length 2..L exactly once? Give a small graph where it would
   find a ring twice or miss one, if such a graph exists.
3. Does anything break the contract (ids as indices, unsorted output, returning lists of ints instead
   of Cycle objects)?
4. List 8 unit tests to write first, with expected outputs.
<paste docs/design/matching.md>
```

---

## 8. Phase 1: Foundations (Tue 3 – Thu 5 Nov)

**Goal:** `find_cycles(pool, 3)` returns every 2- and 3-ring exactly once, in canonical form, sorted by `(len, families)`. Two independent methods agree: your DFS and the nested-loop fallback.

**Files:** `graph.py`, `cycles.py`, `tests/unit/test_graph.py`, `tests/unit/test_cycles.py`.
**Branch:** `p1/matching` (after the lead's contract commit, Tue 9 am).

### Tasks

- [ ] **M1.1** 🛠 `CompatibilityGraph`: adjacency dicts built once in `__init__`, sorted tuples, `mutual_pairs`, `to_networkx`.
- [ ] **M1.2** 🧑‍🏫 `CycleFinder.find(max_len)`: write the DFS **yourself**. For each start s in sorted order, extend paths only through nodes **greater than s**. When a successor equals s and the path has ≥ 2 nodes, record `Cycle.of(path)`. Stop extending at `max_len`.
- [ ] **M1.3** 🛠 `find_cycles_nested_loops(pool, max_len ≤ 3)`: plain loops over i < j (2-rings) and i < j, k > i (3-rings in both directions). This is the Plan.md fallback, and it's also a cross-check.
- [ ] **M1.4** 🛠 Unit tests: hand graphs, the fixtures (once the lead pushes them on Tue), and DFS == nested loops on 50 random pools.
- [ ] Open PR `p1/matching → main` by Thu 6 pm.

You need pools for testing before the generator merges. Use the lead's fixtures, plus a tiny helper in your test file that builds a `Pool` from an edge list (any blood groups, since edges are taken as given). Don't call the generator in unit tests.

### Prompts

**M1.1 🛠: compatibility graph**

```text
[context block]

Implement donorbridge/graph.py: CompatibilityGraph exactly per the contract. Build _succ and _pred as
dict[int, tuple[int, ...]] (sorted) once in __init__ from pool.edges; nodes() = pool.ids();
has_edge uses a set; mutual_pairs() returns sorted (i, j) with i < j where both directions exist;
to_networkx() returns an nx.DiGraph with every node (including isolated ones) and edge.
Families with no edges must still appear in nodes() with empty successor tuples.
Write tests/unit/test_graph.py with a helper make_pool(ids, edges) that builds a Pool with dummy
Family fields.
```

**M1.2a 🧑‍🏫: learn the DFS before writing it**

```text
[context block]

Teach me depth-first search for enumerating all simple cycles of length <= L in a directed graph, the
"smallest node first" way: start from each node s, only visit nodes > s, close the cycle when we can
step back to s. Don't write Python for me. Instead:
1. Explain why restricting to nodes > s makes each cycle appear exactly once (and why direction still
   matters: 0->1->2->0 and 0->2->1->0 are different rings).
2. Trace it by hand on this graph: edges 0->1, 1->2, 2->0, 2->1, 0->3, 3->0, with L=3. Show the
   recursion stack at each step and the rings found.
3. What is the worst-case number of paths explored for n families, max out-degree d, L=3? Why is L=4
   so much worse?
4. Recursive vs explicit stack: which is easier to explain on stage?
```

**M1.2b 🧑‍🏫: review my DFS**

```text
[context block]

Review my CycleFinder. Check: every ring found exactly once; canonical Cycle objects; output sorted by
(len, families); no recursion bug when a node has no successors; respects max_len; doesn't mutate
shared lists across branches (the classic path.append/pop bug). Point to lines; minimal fixes only.
<paste donorbridge/cycles.py>
```

**M1.3 🛠: nested loops and tests**

```text
[context block]

1. Implement find_cycles_nested_loops(pool, max_len) in donorbridge/cycles.py for max_len in {2, 3}
   (ValueError otherwise), using plain loops over sorted ids and graph.has_edge. 3-rings: i < j, i < k,
   j != k, edges i->j->k->i. Return Cycle objects sorted by (len, families).
2. Write tests/unit/test_cycles.py:
   - triangle 0->1->2->0, L=3 -> [(0,1,2)]; L=2 -> []
   - both directions 0->1->2->0 and 0->2->1->0 -> two distinct 3-rings, plus 2-rings (0,1),(0,2),(1,2)
   - greedy_trap fixture -> (0,3), (1,2), (0,1,2)
   - a 4-cycle 0->1->2->3->0 with L=3 -> nothing
   - non-contiguous ids (e.g. 10, 25, 40) work
   - DFS == nested loops on 50 random pools of 30 families (build random pools in the test with
     random.Random(seed), edge probability 0.2)
```

### Integration checks that hit your code (Phase 1)

`test_p1_matching_graph_matches_edges`, `test_p1_matching_rings_on_fixtures`, `test_p1_matching_dfs_equals_nested_loops`, plus `test_p1_e2e_pipeline_india_100`. Every solver test calls your `find_cycles` through `Solver.solve`. Run them with `pytest tests/integration/test_phase1.py -k matching`.

**Hand-off:** open a PR as soon as `find_cycles` passes your tests (aim for Wed). Every solver test depends on it, so it is the most valuable early merge in P1.

---

## 9. Phase 2: Engine v1 (Fri 6 – Tue 10 Nov)

**Goal:** a brute-force verifier that is obviously correct (slow is fine). It is the referee for the lead's ILP and the heuristics owner's branch and bound. Your ring list is also proven equal to networkx's on realistic pools.

**Files:** `solvers/brute_force.py`, tests.

### Tasks

- [ ] **M2.1** 🧑‍🏫 `BruteForceSolver` (`name="brute-force"`, `exact=True`). Write it yourself as a recursion over families: take the smallest family not yet decided; either leave it unmatched, or pick each ring containing it that is disjoint from what's already chosen. Keep the best total weight (from `self.weights`). Add a class constant `MAX_N = 16`, and raise `ValueError` in `_solve` if more families than that appear in rings.
- [ ] **M2.2** 🛠 Unit tests: every fixture's known optimum, both scorers, ring_vs_swap at p=0.6 and p=0.9, empty pool.
- [ ] **M2.3** 🛠 Cross-check test: your ring list == `nx.simple_cycles(G, length_bound=L)` (canonicalised) on 20 India pools × 100. Merge `main` after `phase-1-done` so the generator is available.
- [ ] **M2.4** 🛠 Profile `find_cycles` at n = 100, 200, 300, 500 for L=3 (time and ring count). If n=300 takes > 5 s, find out why before P4.
- [ ] Open PR by Tue 10 Nov, 6 pm.

### Prompts

**M2.1a 🧑‍🏫: brute force design**

```text
[context block]

I'm hand-writing an exact brute-force solver for: choose vertex-disjoint rings (from a given list)
to maximise total weight. Tutor me, don't write it.
My plan: index rings by family; recurse on the smallest undecided family v: (a) skip v; (b) for each
ring containing v that's disjoint from chosen, choose it and mark all its families decided.
1. Prove (informally) that this explores every feasible set of rings exactly once.
2. Why "smallest undecided family" and not "next ring in the list"? Which has a smaller search tree?
3. How big is the tree for 12 families with ~15 rings? Is MAX_N = 16 sensible?
4. What should stats contain (nodes visited)? What does the optimal flag return?
```

**M2.1b 🧑‍🏫: review brute force**

```text
[context block]

Review my BruteForceSolver for correctness (does it ever skip a feasible combination or double-use a
family?), determinism, and the "skip v" branch. Then give me 3 tiny inputs where a subtle bug would
show up, with the correct optimum for each.
<paste solvers/brute_force.py>
```

**M2.3 🛠: networkx cross-check and profiling**

```text
[context block]

1. Add to tests/unit/test_cycles.py a test (mark slow if > 1 s) comparing find_cycles(pool, 3) with
   networkx: canon = sorted(Cycle.of(c) for c in nx.simple_cycles(G, length_bound=3) if len(c) >= 2)
   on make_generator("india").generate_many(20, 100, seed=0). On mismatch, print the missing and
   extra rings.
2. Write a small script (not committed to donorbridge/; put it in scripts/profile_cycles.py) timing
   find_cycles for n in (100, 200, 300, 500), L=3, 3 seeds each, printing n, ring counts by length,
   median seconds. Use time.perf_counter.
```

### Integration checks that hit your code (Phase 2)

`test_p2_matching_brute_force_equals_ilp`, `test_p2_matching_rings_equal_networkx`, and the brute-force run inside `test_p2_e2e_cli_every_solver`.

---

## 10. Phase 3: Exact solvers and failure model (Wed 11 – Mon 16 Nov) · ◆ gate 16 Nov

**Goal:** `MatchingSolver` (`name="matching"`, `exact=True`, `supported_lengths=(2,)`) solves the 2-way problem exactly in polynomial time, and it's hand-written.

**Files:** `solvers/matching.py`, tests.

**Read this first.** The 2-way problem is maximum matching on an undirected graph: one node per family, one edge per mutual pair. That graph is **not bipartite**, and a plain augmenting-path search (the bipartite version) can miss augmenting paths when there are odd cycles. You only get guaranteed optimality from **Edmonds' blossom algorithm**: augmenting paths plus shrinking odd cycles.

- **Target:** augmenting paths with blossom contraction. Set `optimal=True`.
- **Plan.md cut line #4** (if blossom isn't green by Sat 14 Nov): ship the simpler augmenting-path version and set `optimal=None`. Measure how often it differs from networkx on 1,000 pools and report that number honestly on stage.

### Tasks

- [ ] **M3.1** 🧑‍🏫 Learn augmenting paths and Berge's theorem. Write the bipartite-style version first; it's your fallback.
- [ ] **M3.2** 🧑‍🏫 Add blossom contraction (Edmonds). Write it yourself, with the AI as tutor and reviewer.
- [ ] **M3.3** 🛠 Weighted case. If the scorer gives the 2-rings different weights (sensitisation survival, fairness), delegate to `nx.max_weight_matching` and set `stats["backend"] = "networkx-weighted"`. When all 2-ring weights are equal (count, or uniform p), use your own code and set `stats["backend"] = "hand-written"`.
- [ ] **M3.4** 🛠 Tests: hand cases including a 5-cycle with a pendant (the classic blossom trap), and matching == networkx == ILP(L=2) on 1,000 pools (slow).
- [ ] Open PR by Mon 16 Nov, 6 pm.

### Prompts

**M3.1 🧑‍🏫: augmenting paths**

```text
[context block]

Teach me maximum-cardinality matching by augmenting paths. No Python for me; use pictures in text.
1. What is an augmenting path? State Berge's theorem and give the 2-line intuition.
2. Show the BFS/DFS search for an augmenting path from a free vertex in a bipartite graph.
3. Now show me a small NON-bipartite graph (an odd cycle) where that simple search fails to find an
   augmenting path that exists. Walk through exactly where it goes wrong.
4. In our setting, nodes are families and an undirected edge means a mutual pair (i->j and j->i).
   Each matched edge = one 2-way swap = 2 transplants. Confirm the objective mapping.
```

**M3.2a 🧑‍🏫: blossoms**

```text
[context block]

Now teach me Edmonds' blossom algorithm at the level I need to implement it in ~120 lines of Python.
1. What is a blossom; why can we shrink it and keep correctness?
2. The standard implementation with arrays: match[], parent[], base[], a BFS queue, and the
   "lowest common ancestor" step to find the blossom base. Explain each array's meaning and when it
   changes. Pseudocode only.
3. Trace it on: a 5-cycle 0-1-2-3-4-0 plus a pendant 4-5, starting from matching {1-2, 3-4}.
4. Our ids aren't 0..n-1: how do I map them to indices cleanly and map back?
```

**M3.2b 🧑‍🏫: review my matching**

```text
[context block]

Review my MatchingSolver. Check: blossom contraction and expansion correctness, base[] updates, LCA,
the id <-> index mapping, that chosen rings are Cycle.of((i, j)) for matched pairs, the weighted
fallback, the stats/optimal flags. Then give me 5 small graphs (edge lists) that would break a
typical buggy blossom, with the correct maximum matching size for each.
<paste solvers/matching.py>
```

**M3.4 🛠: tests**

```text
[context block]

Write tests/unit/test_matching.py: the 5 adversarial graphs from my review (pasted), the fixtures,
an empty pool, a pool with no mutual pairs, and a slow test over 1000 India pools (sizes cycling 20,
50, 100): matching transplants == 2 * len(nx.max_weight_matching(undirected mutual graph,
maxcardinality=True)) == ILP(L=2) transplants. Also: max_cycle_len=3 raises ValueError.
<paste the 5 graphs>
```

### Integration checks that hit your code (Phase 3)

`test_p3_matching_equals_networkx`, plus the matching rows of `test_p3_e2e_crosscheck_1000` (the gate).

---

## 11. Phase 4: Experiments (Tue 17 – Sun 22 Nov) · ◆ feature freeze Mon 23 Nov

**Goal:** three scripted demos (rubric item 5: two normal cases and one edge case), a notebook with the ring picture for the deck, and the cycle-growth experiment that shows why 3-way is hard.

**Files:** `demos/scripts.py`, `notebooks/demo.ipynb`, `experiments/cycle_growth.py`.

| Demo | Kind | Story it tells |
| --- | --- | --- |
| `demo_small` | Normal | The 8-family pool from week 1: list the rings, then climb the ladder (first-come → greedy → local search → matching L=2 → B&B → ILP, L=2 and L=3) in one table |
| `demo_india` | Normal | One India pool of 100: every solver, transplants, expected transplants at p=0.8, runtime, optimal flag |
| `demo_edge` | Edge case | (1) ring_vs_swap: count-max picks the 3-ring; failure-aware picks the swap at p=0.6 and the ring at p=0.9. (2) The night before: the count-max plan on ring_vs_swap is the 3-ring (0,1,2). Edge 1→2 fails its final crossmatch (applied deterministically with `pool.without_edges`), so the whole ring is cancelled. A **re-solve** recovers the swap (0,1): 2 transplants instead of 0. Print the word "re-solve" |

Every demo is deterministic, finishes in under 10 s, and prints readable output: a heading, one line per ring, and a closing sentence that states the point.

`cycle_growth` is just a `SPEC` for the shared engine. `Setting(solver=None, max_len=4, n=n)` for n ∈ {50, 100, 200, 300}, plus `Setting(solver=None, max_len=3, n=500)`, because L=4 at n=500 is too slow. `n_pools=5`; quick: n ∈ {20, 40} with 2 pools. With `solver=None`, the engine only enumerates rings and records `rings_2/3/4` and `enum_s` in the shared `ROW_COLUMNS`. The simulation owner plots it in chart 4.

### Tasks

- [ ] **M4.1** 🛠 `demos/scripts.py` with `demo_small`, `demo_india`, `demo_edge` and the `DEMOS` dict. The lead wires `python -m donorbridge demo [name|all]`.
- [ ] **M4.2** 🛠 `notebooks/demo.ipynb`: runs the three demos, then draws the ring picture. Nodes are labelled with blood groups, chosen rings get one colour each, unused edges are light grey. Save it to `results/figures/ring_picture.png` for the deck.
- [ ] **M4.3** 🛠 The `cycle_growth` `SPEC` (about 10 lines). Then check `enum_s` against your M2.4 profiling numbers. They should agree.
- [ ] **M4.4** Rehearse the demos live: `python -m donorbridge demo all` on a clean terminal, with a big font. Time each one.
- [ ] Open PR by Sun 22 Nov, 6 pm. **Nothing new after the Mon 23 Nov freeze.**

### Prompts

**M4.1 🛠: demos**

```text
[context block]

Implement donorbridge/demos/scripts.py with demo_small, demo_india, demo_edge and
DEMOS = {"small": ..., "india": ..., "edge": ...}. Specs:
<paste the demo table from my playbook>
Use get_solver, find_cycles, ExpectedTransplantScorer, compute_metrics, and the fixtures via
Pool.load_json(Path(__file__).parents[2] / "tests" / "fixtures" / "<name>.json").
For the night-before part of demo_edge: on ring_vs_swap, the count-max ILP plan is the 3-ring
(0,1,2); fail edge (1, 2) with pool.without_edges, so the ring is cancelled; re-solve on the
families not transplanted (all three) and show the swap (0,1) is recovered; print before/after. Pure print output, no colours
(Windows terminals), max 80 columns. Each demo < 10 s.
Then write tests/unit/test_demos.py that runs each demo and checks key phrases in captured stdout.
```

**M4.2 🛠: ring picture notebook**

```text
[context block]

Create notebooks/demo.ipynb (give me the cells as code blocks, I'll paste them in). Cells:
1. Markdown title + one-paragraph explanation for a non-technical audience.
2. Run each demo from donorbridge.demos.
3. Ring picture: load pool_8, solve with ILP L=3; draw with networkx + matplotlib: spring layout with
   fixed seed, node labels "id\npatient/donor blood", chosen rings' edges thick and coloured (one colour
   per ring, colour-blind safe), other edges thin light grey with arrows. Save to
   results/figures/ring_picture.png at 200 dpi and .svg.
4. The same picture for an India pool of 30 families, to show scale.
```

**M4.3 🛠: cycle growth spec**

```text
[context block]

Write SPEC = GridSpec(name="cycle_growth", ...) in donorbridge/experiments/cycle_growth.py:
<paste the cycle_growth description from my playbook>
Settings as tuples; quick_settings and pool counts filled in; no other code.
```

### Integration checks that hit your code (Phase 4)

`test_p4_matching_demos_run` (`demo all` exits 0, and the edge demo prints "re-solve"), plus `test_p4_e2e_results_quick`, which runs `cycle_growth`.

---

## 12. Phase 5: Story (Tue 24 Nov – Mon 7 Dec)

**You own:** the live demo on stage, the backup recording, the ring-picture slide, and the "why 2-way is easy and 3-way is hard" slide.

### Tasks

- [ ] **M5.1** Design-file section: final DFS and matching flowcharts and pseudocode. Justification: matching is polynomial (Edmonds); 3-rings are NP-hard (Abraham, Blum, Sandholm 2007); and the ring count grows like your `cycle_growth.csv` shows.
- [ ] **M5.2** Record a backup screen capture of `demo all` (under 2 min), in case the live demo fails.
- [ ] **M5.3** 🧑‍🏫 Rehearse explaining the DFS and augmenting paths in 60 s each, without slides.
- [ ] **M5.4** Run `scripts/release_check.sh` on your own laptop and report the result to the lead.
- [ ] Rehearsals: Mon 30 Nov dry run plus three timed runs.

### Prompts

**M5.3 🧑‍🏫: 60-second explanations**

```text
[context block]

I have 60 seconds on stage to explain (a) how we list every possible swap ring with depth-first
search and (b) why 2-way swaps are "easy" (matching) but 3-way rings make the problem NP-hard.
Audience: smart non-specialists. Here's my draft script: <paste>. Cut it to 140 words each, keep one
concrete picture per explanation, and list the 3 follow-up questions a CS professor would ask and
crisp answers.
```

---

## 13. If you're stuck

- **Recursion stalls** (DFS not passing by Wed 4 Nov evening): ship `find_cycles_nested_loops` as the implementation behind `find_cycles` for L ≤ 3 so nobody else is blocked, then pair with the lead on the DFS. This is the Plan.md fallback.
- **The DFS finds duplicates:** you're not restricting to nodes > start, or you're canonicalising wrong. Compare against nested loops on the failing pool.
- **Blossom bugs past Sat 14 Nov:** take cut line #4 (augmenting-path only, `optimal=None`), tell the lead, and measure the mismatch rate vs networkx.
- **A demo is flaky:** a seed isn't fixed, or the demo depends on solver timing. Make every choice deterministic.
