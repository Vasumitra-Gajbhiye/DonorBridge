# DonorBridge · Lead playbook

**Owner:** ____________ · **Role:** Lead (architecture, interfaces, ILP, oracle, integration)
**The algorithm you present on stage:** the ILP formulation with expected-transplant weights, and why it serves as the oracle that checks everyone else.

You are the critical path twice in every phase. On day 1, your contract or test file unblocks everyone. On merge day, nothing is done until you have merged and run the integration test. Protect those two moments. Teammates go first: if someone is blocked, unblocking them beats your own task list.

This file has the same sections 1–6 as the other four playbooks, then your own phases. **Sections 8–12 also contain the full integration-test spec for each phase.** Each teammate's file lists only the checks that touch their code.

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

After every prompt, add an entry to `ai_logs/<role>.md` (yours: `ai_logs/lead.md`). The lead merges these into `AI_LOG.md` in P5.

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

My role: Lead (architecture, interfaces, ILP, oracle, integration).
I own: pyproject.toml, requirements*.txt, .github/, README.md, every __init__.py, donorbridge/__main__.py, models.py, survival.py, scoring.py, solvers/base.py, solvers/__init__.py, solvers/ilp.py, oracle/glasgow.py, oracle/kep_oracle.py, oracle/crosscheck.py, experiments/answer.py, scripts/kep_oracle_runner.py, tests/conftest.py, tests/fixtures/, tests/integration/.
````

## 7. Before Phase 1 (today, Mon 2 Nov: design gate)

- [ ] Every teammate has committed dated pseudocode and a flowchart for each module they own in P1–P3 to `docs/design/<role>.md`. Review all four tonight. This is the 2 Nov gate.
- [ ] Your own `docs/design/lead.md`: the ILP formulation (section "The core maths" in Plan.md), the Solver template method, and the merge order.
- [ ] Post in the group chat: "Contract v1 lands on main Tue 12:00. Until then, finish pseudocode and list your unit-test cases."

**Prompt L0.1 🧑‍🏫: design-gate review of a teammate's pseudocode**

```text
[paste context block, with my role = Lead]

I'm the lead, reviewing a teammate's design before any code is written. Their role is <role>.
Below are their pseudocode and flowchart (dated). Review it against the contract above:
1. Does every function they plan to write match a contract signature exactly? List mismatches.
2. Is there a hidden assumption that will break integration (ids used as indices, global randomness,
   mutating a frozen dataclass, returning a different type)?
3. Is the algorithm correct? Give one small counterexample input if not.
4. Five unit-test cases they should write first, with expected outputs.
Do not write implementation code.

<paste docs/design/<role>.md>
```

---

## 8. Phase 1: Foundations (Tue 3 – Thu 5 Nov)

**Goal:** the contract exists on `main` as importable stubs by **Tue 12:00**. Your own P1 modules (models, survival, scoring, Solver base, registry, fixtures) are real by **Wed evening**, so teammates can run against real types before merge day.

**Branch:** commit L1.0 and L1.1 **directly to `main`** (the only time you do this). Everything else goes on `p1/lead`.

### Tasks

- [ ] **L1.0** Repo tooling: `pyproject.toml`, `requirements.txt`, `requirements-oracle.txt`, `.gitignore`, CI workflow. Run `pip freeze` and pin exact versions.
- [ ] **L1.1** Skeleton: every module in the module map, as stubs with exact signatures. Also `ai_logs/<role>.md` × 5 and `docs/design/<role>.md` × 5 (empty headers). **Push to `main` by Tue 12:00 as "P1 lead: contract v1".**
- [ ] **L1.2** `models.py` fully implemented and unit-tested.
- [ ] **L1.3** `survival.py` and `scoring.py` implemented and unit-tested.
- [ ] **L1.4** `solvers/base.py` (template method) and `solvers/__init__.py` (registry) implemented and unit-tested with a dummy solver.
- [ ] **L1.5** Fixtures: `pool_8` (from the week-1 paper exercise) with expected answers, `ring_vs_swap`, `greedy_trap`, `empty`, `no_edges`. Push these to `main` on Tue too, since teammates' unit tests use them.
- [ ] **L1.6** `tests/conftest.py`: a `load_fixture(name)` helper, `slow` and `oracle` markers, and a `--run-slow` option.
- [ ] **L1.7** `tests/integration/test_phase1.py` (spec below). Push to `main` Tue afternoon.
- [ ] Merge day (Thu 6 pm): merge the five PRs in order, run integration, assign fixes, tag `phase-1-done`.

### Prompts

**L1.0 🛠: repo tooling**

```text
[context block]

Task: set up repository tooling. Output each file in full, each in its own code block headed by its path.
1. pyproject.toml: setuptools build, package `donorbridge` (find packages), requires-python >=3.11.
   [tool.pytest.ini_options]: testpaths=["tests"], markers "slow: long cross-checks (opt-in)" and
   "oracle: needs .venv-oracle with kep_solver".
2. requirements.txt: numpy, pandas, matplotlib, networkx>=3.1, pulp==2.9.0, highspy, pytest, nbformat
   (unpinned except pulp; I will pin with pip freeze).
3. requirements-oracle.txt: kep_solver and pulp==2.9.0 (kep_solver breaks on PuLP 4.x).
4. .gitignore for Python, .venv*, .ipynb_checkpoints, data/raw/.
5. .github/workflows/ci.yml: on push and pull_request; ubuntu-latest; Python 3.11; pip cache;
   install requirements and `pip install -e .`; run `pytest tests/unit -q` then
   `pytest tests/integration -q -m "not slow and not oracle"`.
Then give me the exact shell commands to create the venv, install, and pin versions.
```

**L1.1 🛠: package skeleton (the contract commit)**

```text
[context block]

Task: generate the full package skeleton so five people can work in parallel without ever editing the
same file. Use the module map below. For EVERY file:
- Module docstring: one-line purpose, then "Owner: <role>" and "Implemented in: P<n>".
- Every class/function listed for that file, with the exact contract signature where the contract gives
  one, a docstring describing intended behaviour, and the body
  `raise NotImplementedError("<owner>, P<n>")`.
- Dataclasses in models.py, survival.py, scoring.py: write the field definitions now (they are the
  contract), but leave method bodies as NotImplementedError. I'll implement them next.
- Each Solver subclass: subclass Solver, set `name`, `exact`, `supported_lengths` ClassVars
  (matching: (2,), exact=True; brute-force, branch-bound, ilp: exact=True; first-come, greedy,
  local-search: exact=False), stub `_solve`.
- Each Experiment subclass: subclass Experiment, set `name` (snake_case of the file), stub `run`.
- solvers/__init__.py: SOLVERS dict with all seven names -> classes; get_solver(name, **kwargs)
  raising KeyError listing valid names.
- experiments/__init__.py: EXPERIMENTS dict of all Experiment subclasses.
- __main__.py: argparse with subcommands run, sweep, bench, results, demo. Each prints
  "not implemented yet (P<n>)" and exits with code 2. Keep it tiny; I'll fill it in later.
- Every __init__.py re-exports the public names of its package, so imports never fail.
After the files, give me a one-line command that imports every module to prove the skeleton loads.

Module map (path | owner | phase | public names):
<paste the module map table from section 5 of my playbook>

Extra signatures not in the contract (use exactly these):
- generator/report.py: calibration_report(preset: str, n_pools: int, n: int, seed: int) -> pd.DataFrame
- generator/survival_models.py: class SensitisationSurvival(SurvivalModel): __init__(self, p_low: float, p_high: float)
- generator/regions.py: split_by_region(pool: Pool) -> list[Pool]
- cycles.py: find_cycles_nested_loops(pool: Pool, max_len: int) -> list[Cycle]   # max_len <= 3 only
- simulation/resolve.py: @dataclass(frozen=True) ResolveOutcome(plan: Solution, first: FailureOutcome,
  resolve: Solution | None, final_transplants: int);
  class NightBeforeSimulator: __init__(self, solver: Solver, survival: SurvivalModel, seed: int); run(self, pool: Pool) -> ResolveOutcome
- simulation/fairness.py: class FairnessScorer(ExpectedTransplantScorer): __init__(self, survival: SurvivalModel | float = 1.0, beta: float = 0.0, group: str = "highly_sensitised")
- simulation/benchmark.py: time_solvers(solver_names: list[str], sizes: list[int], n_pools: int, seed: int, max_cycle_len: int = 3, time_limit_s: float = 60.0) -> pd.DataFrame
- simulation/plots.py: make_all_figures(results_dir: Path = Path("results")) -> list[Path]
- oracle/glasgow.py: list_instances(directory: Path) -> list[Path]; load_glasgow(path: Path) -> Pool
- oracle/kep_oracle.py: pool_to_kep_json(pool: Pool) -> dict; kep_optimum(pool: Pool, max_cycle_len: int) -> int
- oracle/crosscheck.py: @dataclass CrosscheckReport(n_pools: int, mismatches: list[dict]); crosscheck(n_pools: int, seed: int, sizes: tuple[int, ...] = (8, 10, 12, 20, 30)) -> CrosscheckReport
- experiments/answer.py: compute_answer(results_dir: Path = Path("results"), threshold: float = 0.05) -> dict
- demos/scripts.py: demo_small() -> None; demo_india() -> None; demo_edge() -> None; DEMOS: dict[str, Callable[[], None]]
```

After it lands: `python -c "import donorbridge, donorbridge.solvers, donorbridge.experiments"`. Commit, push to `main`, and post in the group chat.

**L1.2 🛠: models.py**

```text
[context block]

Task: implement donorbridge/models.py exactly as in the contract, plus tests/unit/test_models.py.
Requirements:
- Pool.__post_init__ validates: ids unique; every edge (i, j) has i != j and both ids in the pool.
  Raise ValueError with a clear message otherwise. Build a private id->Family dict for family()
  (use object.__setattr__ since the dataclass is frozen).
- Pool.ids() sorted. subpool(ids) keeps only those families and edges among them. without_edges(drop)
  returns a new Pool. Neither mutates self.
- JSON format: {"name": str, "families": [ {all Family fields, enums as their .value} ],
  "edges": [[i, j], ...] sorted}. from_dict ignores unknown top-level keys.
- Cycle.of(seq): reject len < 2 or repeated ids (ValueError); rotate so min id is first, keep direction.
  Cycle(1,2,3) and Cycle(1,3,2) are DIFFERENT rings. __post_init__ asserts canonical form.
- Solution.validate(pool, max_cycle_len) raises InvalidSolutionError if: a ring is longer than
  max_cycle_len or shorter than 2; a ring edge is not in pool.edges; a family appears in two rings;
  an id is not in the pool. The message must name the offending ring/family.
- Tests: round-trip JSON; subpool/without_edges; canonical rotation; each validate failure mode;
  empty pool.
```

**L1.3 🛠: survival.py and scoring.py**

```text
[context block]

Task: implement donorbridge/survival.py and donorbridge/scoring.py, plus tests/unit/test_scoring.py.
- UniformSurvival(p): validate 0 <= p <= 1. edge() returns p. SurvivalModel.cycle() multiplies edge()
  over cycle.edges().
- CountScorer.name = "count". ExpectedTransplantScorer.name = f"expected(p={p})" for uniform
  survival, else "expected(<ClassName>)". A float argument becomes UniformSurvival(p).
- Scorer.total sums weight over rings.
- Tests: 3-ring weight at p=0.9 == 3*0.9**3; 2-ring at p=0.6 == 0.72; the crossover: for p in
  [0.5, 0.6, 0.66, 0.67, 0.7, 0.9], the 3-ring beats the 2-swap iff p > 2/3; CountScorer ignores p.
```

**L1.4 🛠: Solver base and registry**

```text
[context block]

Task: implement donorbridge/solvers/base.py (Solver) and solvers/__init__.py, plus
tests/unit/test_solver_base.py using a tiny DummySolver defined inside the test file.
Solver.__init__: raise ValueError if max_cycle_len not in supported_lengths; scorer defaults to CountScorer().
Solver.solve(pool, cycles=None) is a TEMPLATE METHOD:
  1. if cycles is None: cycles = find_cycles(pool, self.max_cycle_len)   (import inside the method)
  2. keep only rings with len <= max_cycle_len
  3. t0 = time.perf_counter(); chosen, optimal, stats = self._solve(pool, cycles); runtime
  4. if not self.exact: optimal = False
  5. sol = Solution(tuple(sorted(chosen, key=lambda c: (len(c), c.families))), self.name,
     self.scorer.total(chosen, pool), runtime, optimal, stats)
  6. sol.validate(pool, self.max_cycle_len); return sol
Solver.weights(pool, cycles) returns {c: self.scorer.weight(c, pool)}.
Also __repr__ showing name, max_cycle_len, scorer name.
Explain in 3 lines why this is the Template Method pattern. I'll put that in the design file.
```

**L1.5 🛠: fixtures**

```text
[context block]

Task: turn our hand-solved 8-family pool into a test fixture, and independently re-derive the answers
so I can compare them with ours.
Here is the pool as drawn on paper (families with blood groups, and the arrows):
<paste your week-1 table: id, patient blood, donor blood, sex, relation, PRA; and the edge list>
1. Write tests/fixtures/pool_8.json in our Pool JSON format.
2. List EVERY ring of length 2 and every ring of length 3, in canonical form (smallest id first,
   direction kept). Show how you found them.
3. Give the maximum number of transplants with rings <= 2 and with rings <= 3, and one optimal set each.
4. Write tests/fixtures/pool_8.expected.json:
   {"rings_L2": [...], "rings_L3": [...], "opt_L2": int, "opt_L3": int}.
Also write ring_vs_swap.json, greedy_trap.json, empty.json, no_edges.json from these specs:
<paste the fixtures table from section 5>
Pick any valid blood groups/PRA for the small fixtures (all ABO-compatible along their edges).
```

Compare its rings and optimum with your paper answer. **If they disagree, work it out by hand. Don't just trust either side.** Log the disagreement under "Corrected".

**L1.7 🛠: integration test, phase 1**

```text
[context block]

Task: write tests/integration/test_phase1.py. Use a fixture loader `load_fixture(name) -> Pool` from
tests/conftest.py (write that too). Every test name starts with test_p1_<role>_ or test_p1_e2e_ so
each teammate can run `-k <role>`. Keep the whole file under 30 s. Tests:
<paste the "Integration test spec: Phase 1" list from my playbook>
Use pytest.approx for floats. Where a test needs randomness, fix the seed.
```

### Integration test spec: Phase 1

| Test | Checks |
| --- | --- |
| `test_p1_lead_all_modules_import` | Every module in the module map imports |
| `test_p1_lead_registry_has_seven_solvers` | `SOLVERS` keys == the seven names; `get_solver("x")` raises `KeyError` |
| `test_p1_lead_pool_json_roundtrip` | Every fixture: `Pool.from_dict(p.to_dict()) == p` |
| `test_p1_lead_cycle_canonical_form` | `Cycle.of([3,1,2]) == Cycle.of([1,2,3])`; `!= Cycle.of([1,3,2])` |
| `test_p1_lead_validate_rejects_bad_solutions` | Overlap, missing edge, too long and unknown id each raise `InvalidSolutionError` |
| `test_p1_lead_expected_weights_crossover` | `ring_vs_swap`: ring beats swap iff p > 2/3 |
| `test_p1_generator_deterministic` | Same seed → equal pools; different seed → different pools |
| `test_p1_generator_pool_shape` | India n=100: 100 families, unique ids, no self-edges, every edge `blood_compatible(donor_i, patient_j)` |
| `test_p1_generator_selection_effect` | 20 India pools × 100: share of O patients > share of O donors |
| `test_p1_generator_report_consistent` | `report.pairs_sampled == n + report.rejected_compatible` |
| `test_p1_matching_graph_matches_edges` | For each fixture, successors/predecessors/has_edge agree with `pool.edges` |
| `test_p1_matching_rings_on_fixtures` | `find_cycles(pool_8, 2/3)` equals `pool_8.expected.json`; ring_vs_swap and greedy_trap rings as in section 5 |
| `test_p1_matching_dfs_equals_nested_loops` | 20 random India pools × 60, L=3: DFS == nested loops |
| `test_p1_heuristics_first_come_valid` | First-come on every fixture and on 10 random pools: validates, `optimal is False` |
| `test_p1_heuristics_greedy_on_fixtures` | greedy_trap → 3 transplants; ring_vs_swap (count) → ring; empty → 0 rings |
| `test_p1_simulation_metrics_on_fixture` | Hand-built solution on pool_8: transplants and matched counts by group as expected |
| `test_p1_simulation_failure_p1_exact` | `UniformSurvival(1.0)`: every draw realises all rings |
| `test_p1_simulation_failure_matches_analytic` | p=0.7, 20,000 trials on a greedy solution: \|mean − Σ\|c\|p^\|c\|\| < 3·SE |
| `test_p1_e2e_pipeline_india_100` | generate → find_cycles → greedy → validate → metrics → simulate, < 10 s |
| `test_p1_e2e_solver_names_resolve` | Every name resolves via `get_solver`; first-come and greedy solve a pool |

**Done when:** `pytest tests/unit tests/integration/test_phase1.py` is green on `main` and you've tagged `phase-1-done`.

---

## 9. Phase 2: Engine v1 (Fri 6 – Tue 10 Nov)

**Goal:** the ILP (your algorithm) is correct and agrees with kep_solver on real benchmark graphs. The CLI runs a pool end to end.

### Tasks

- [ ] **L2.0** Push `test_phase2.py` to `main` Fri 10 am (spec below).
- [ ] **L2.1** 🧑‍🏫 `ILPSolver`: write the formulation yourself, using PuLP with CBC, scorer weights, a time limit, and solver status mapped to the `optimal` flag.
- [ ] **L2.2** Download the Glasgow benchmark pools. Commit 10–20 small instances (≤ 300 pairs) to `data/glasgow/` with a `SOURCE.md` (CC BY 4.0 attribution). Write `load_glasgow`.
- [ ] **L2.3** kep_solver oracle. `pool_to_kep_json` exports **our** Pool in kep_solver's input format. `scripts/kep_oracle_runner.py` runs inside `.venv-oracle`, and `kep_optimum` calls it via subprocess. Because both sides then solve identical input, a mismatch is a real bug, not a format difference.
- [ ] **L2.4** CLI `run`: `python -m donorbridge run [--preset india|us] [--n 100] [--seed 1] [--pool FILE] [--solver ilp] [--max-len 3] [--p 1.0] [--json]`. Prints rings, transplants, expected transplants, runtime and the optimal flag.
- [ ] **L2.5** Help the generator owner with the calibration smoke test (US ≈ 48.5 / 58.2) if it fails.
- [ ] Merge day (Tue 6 pm): merge, run integration (including `-m oracle` locally), tag `phase-2-done`.

### Prompts

**L2.1a 🧑‍🏫: check my formulation before I code it**

```text
[context block]

I'm writing the ILP myself; act as a tutor and reviewer, and do not write the solver for me.
My formulation: one binary x_c per candidate ring c (length <= L); maximise sum w_c x_c subject to,
for every family v, sum over rings containing v of x_c <= 1.
1. Explain why "<= 1" and not "= 1". What would "= 1" do to an infeasible family?
2. Why is this the "cycle formulation", and what is its weakness as L grows? (Number of variables for
   L=3 vs L=4 on 100 families with ~20% edge density, roughly.)
3. In PuLP 2.9.0: how do I set a CBC time limit and silence output, and how do I map
   LpStatus/sol_status to "proven optimal" vs "feasible but not proven" vs "infeasible"? Show only
   those API calls, not the whole solver.
4. Rings with weight 0 (p = 0): should they be variables at all? Edge cases I must handle: no rings,
   empty pool.
5. Give me 6 unit tests (input → expected chosen rings) including ring_vs_swap at p=0.6 and p=0.9
   and greedy_trap.
```

**L2.1b 🧑‍🏫: review my ILP**

```text
[context block]

Review my ILPSolver. Check correctness against the formulation, PuLP pitfalls (variable names with
special characters, duplicate names, reading values with .varValue and rounding), determinism, and
the optimal-flag mapping. Point to lines; suggest minimal fixes; don't rewrite it.
<paste donorbridge/solvers/ilp.py and tests/unit/test_ilp.py>
```

**L2.2 🛠: Glasgow loader**

```text
[context block]

Task: write donorbridge/oracle/glasgow.py: list_instances(directory) and load_glasgow(path) -> Pool.
Here is the start of one instance file and its README (format description):
<paste first ~60 lines of an instance file and the dataset README section on format>
Rules: drop non-directed (altruistic) donors and every edge from them. If a recipient has several
donors, merge them into one family: edge i -> j if ANY donor of i is compatible with j's patient
(document this in the docstring). Map blood groups to BloodGroup; if a field we need is missing
(sex, PRA), fill a documented default (Sex.F, 0.0) and set pool.name to the file stem.
Write tests/unit/test_glasgow.py on a tiny hand-written file in the same format.
```

**L2.3 🛠: kep_solver oracle**

```text
[context block]

Task: build the kep_solver oracle. kep_solver lives in a separate venv (.venv-oracle) because it
needs pulp==2.9.0; our package must never import it.
Here is kep_solver's documentation on its input file format and how to solve for maximum
transplants with a max cycle length (no chains):
<paste the relevant kep_solver docs / README sections>
1. donorbridge/oracle/kep_oracle.py:
   - pool_to_kep_json(pool) -> dict in kep_solver's JSON input format (one donor per family, no altruists).
   - kep_optimum(pool, max_cycle_len) -> int: writes the JSON to a temp file, runs
     `.venv-oracle/bin/python scripts/kep_oracle_runner.py <file> <max_len>` via subprocess with a
     timeout, parses one integer from stdout. Raise a clear error if .venv-oracle is missing.
2. scripts/kep_oracle_runner.py: standalone (imports only kep_solver + stdlib); prints the optimum
   number of transplants with cycles only, max length = argv[2], chains disabled.
3. A pytest mark `oracle` on any test that calls kep_optimum.
Tell me which kep_solver calls you are unsure about so I can check them against the installed version.
```

**L2.4 🛠: CLI `run`**

```text
[context block]

Task: implement the `run` subcommand in donorbridge/__main__.py (keep the other subcommands as stubs).
Flags: --preset {india,us} (default india), --n 100, --seed 1, --pool FILE (overrides generator),
--solver NAME (default ilp), --max-len 3, --p 1.0 (if p < 1 use ExpectedTransplantScorer(p), else
CountScorer), --time-limit SECONDS, --json (print Solution as JSON instead of a table).
Human output: pool summary line; one line per ring "ring (3): 12 -> 40 -> 7"; then transplants,
expected transplants at p, runtime, optimal flag. Exit 0 on success, 1 on bad input.
Write tests/unit/test_cli.py using subprocess with a fixture pool.
```

**L2.0 🛠: integration test, phase 2.** Reuse the L1.7 prompt with the Phase 2 spec below and `test_p2_` prefixes. Mark Glasgow tests `@pytest.mark.oracle` and the calibration tests `@pytest.mark.slow`.

### Integration test spec: Phase 2

| Test | Checks |
| --- | --- |
| `test_p2_lead_ilp_on_fixtures` | pool_8 optimum L=2/L=3; greedy_trap = 4; ring_vs_swap picks the swap at p=0.6 and the ring at p=0.9; empty → 0 |
| `test_p2_lead_ilp_matches_kep_solver` (oracle) | Every committed Glasgow instance, L=2 and L=3: ILP transplants == `kep_optimum` |
| `test_p2_lead_cli_run` | `python -m donorbridge run --n 40 --seed 3` exits 0 and prints "transplants" |
| `test_p2_generator_spouse_rule` | INDIA, ≥ 20,000 sampled pairs (report): wife-from-husband positive-crossmatch rate within ±0.04 of `INDIA.target_xm_spouse` (Plan: 0.33), unrelated within ±0.03 of `INDIA.target_xm_unrelated` (Plan: 0.11); spouse rate > unrelated rate |
| `test_p2_generator_female_hs_knob` | `make_generator(female_hs_share=0.4)`: sampled female patients highly sensitised 0.40 ± 0.03 |
| `test_p2_generator_calibration_us` (slow) | US, 20 pools × 100, ILP count: mean L=2 in [45.5, 51.5], L=3 in [55.2, 61.2] (prototype 48.5 / 58.2) |
| `test_p2_generator_calibration_india` (slow) | India, same: L=2 in [49, 55], L=3 in [60, 66] (prototype 52.0 / 63.0) |
| `test_p2_matching_brute_force_equals_ilp` | 30 pools × 10 families, L ∈ {2, 3}, Count and Expected(0.7): equal objectives |
| `test_p2_matching_rings_equal_networkx` | 20 India pools × 100, L=3: ring set == `nx.simple_cycles(G, length_bound=3)` canonicalised |
| `test_p2_heuristics_local_search_fixes_trap` | greedy_trap: local search → 4 |
| `test_p2_heuristics_never_beat_ilp` | 20 pools × 50: first-come, greedy, local-search ≤ ILP (+1e-9); local-search ≥ greedy |
| `test_p2_heuristics_bnb_v1_equals_ilp_small` | 20 pools × 15, L=3, Count: B&B == ILP and `optimal is True` |
| `test_p2_simulation_resolve_properties` | Same seed: final transplants ≥ first-draw transplants; no family transplanted twice; re-solve uses only families not transplanted |
| `test_p2_simulation_experiment_quick` | `SurvivalSweep(quick=True, out_dir=tmp).run()` returns the agreed columns and writes the CSV |
| `test_p2_e2e_cli_every_solver` | CLI `run --n 30` with first-come, greedy, local-search, brute-force (n=12), branch-bound, ilp |

---

## 10. Phase 3: Exact solvers and failure model (Wed 11 – Mon 16 Nov) · ◆ gate 16 Nov

**Goal:** every solver honours the failure-aware scorer, and the 1,000-pool cross-check is green. That cross-check is the correctness evidence for rubric item 4.

### Tasks

- [ ] **L3.0** Push `test_phase3.py` Wed 10 am.
- [ ] **L3.1** `oracle/crosscheck.py` + CLI `bench --crosscheck N [--seed S]`: on N random pools of mixed sizes, check brute force (n ≤ 12) == B&B == ILP, matching == ILP(L=2) == networkx, heuristics ≤ ILP. Log every mismatch with the pool's seed, so it can be replayed with `run --seed`.
- [ ] **L3.2** ILP: L=4 support (needed for the ring-length experiment) and `backend="highs"` as a fallback, via PuLP's HiGHS interface. Pass `time_limit_s` through to both backends.
- [ ] **L3.3** Failure-aware audit: read every `_solve`. Each one must use `self.weights(...)`, never `len(c)`, when ranking or bounding.
- [ ] **L3.4** Pair with the heuristics owner if B&B is still failing tests on Fri 13 Nov (plan risk: "You just called a solver").
- [ ] **L3.5** Gate review Mon 16 Nov: run `pytest -m "slow or not slow"` and `bench --crosscheck 1000`. Decide on cut lines (see the end of this phase).

### Prompts

**L3.1 🛠: cross-check harness**

```text
[context block]

Task: implement donorbridge/oracle/crosscheck.py and wire `bench --crosscheck N --seed S` in __main__.py.
For i in range(N): size = sizes[i % len(sizes)]; pool = make_generator("india").generate(size, seed+i).
Checks (record a dict {seed, size, check, expected, got} for each mismatch, never raise):
- size <= 12: brute-force == ilp for L in (2, 3) under CountScorer and ExpectedTransplantScorer(0.7)
- size <= 30: branch-bound == ilp for L=3, both scorers
- all sizes: matching == ilp(L=2) == networkx max cardinality matching on mutual pairs (count only)
- all sizes: first-come, greedy, local-search objective <= ilp + 1e-9; every Solution validates
Compare objectives with a 1e-6 tolerance. Print a progress line every 50 pools and a final summary
table. Exit code 1 if any mismatch. Also write results/crosscheck.json.
```

**L3.2 🧑‍🏫: L=4 and HiGHS**

```text
[context block]

Here's my ILPSolver. I want to (a) allow max_cycle_len=4 and (b) add backend="highs" using PuLP 2.9.0's
HiGHS interface (highspy installed). Explain what changes are needed and why, show only the PuLP calls
for HiGHS (time limit, silence, status mapping), and list the pitfalls. I'll edit the code myself.
<paste solvers/ilp.py>
```

**L3.3 🧑‍🏫: failure-aware audit**

```text
[context block]

Audit these solver implementations for one bug class: anywhere a solver ranks, compares or bounds rings
by size (len(c)) instead of by the scorer's weight (self.weights / self.scorer.weight). Under
ExpectedTransplantScorer(0.6) such a bug picks a 3-ring over a 2-swap when it shouldn't. For each
finding: file, line, why it's wrong, the one-line fix. Do not comment on anything else.
<paste all files in donorbridge/solvers/>
```

### Integration test spec: Phase 3

| Test | Checks |
| --- | --- |
| `test_p3_lead_failure_aware_all_exact_solvers` | ring_vs_swap: brute-force, branch-bound, ilp pick the swap at p=0.6 and the ring at p=0.9 |
| `test_p3_lead_ilp_length_4` | 20 pools × 10, L=4: ILP == brute force |
| `test_p3_lead_highs_equals_cbc` | 20 pools × 60: same objective |
| `test_p3_e2e_crosscheck_quick` | `bench --crosscheck 50` exits 0 |
| `test_p3_e2e_crosscheck_1000` (slow) | `bench --crosscheck 1000` exits 0. **This is the gate** |
| `test_p3_generator_sensitisation_survival` | Edges into highly sensitised patients get `p_high`, others `p_low`; ILP accepts the scorer |
| `test_p3_generator_split_by_region` | 4 sub-pools; ids partition the pool; no edge crosses regions; sizes sum to n |
| `test_p3_matching_equals_networkx` | 100 pools × 100: matching size == nx max cardinality; `optimal is True` (or `None` if the blossom was cut) |
| `test_p3_heuristics_bnb_equals_ilp` | 50 pools of 20 and 30, both scorers |
| `test_p3_heuristics_bnb_time_limit` | n=200, `time_limit_s=1`: returns a valid solution in < 1.5 s with `optimal is False` |
| `test_p3_simulation_prototype_table` (slow) | Survival sweep at p ∈ {1.0, 0.7, 0.5} within ±3 of the prototype table (2-way and failure-aware 3-way); count-max 3-way < 2-way at p = 0.5 |
| `test_p3_simulation_fairness_scorer` | β=0 gives the same objective as Expected; β=2 matches ≥ as many highly sensitised patients on 20 pools |
| `test_p3_simulation_benchmark_harness` | `time_solvers(["greedy","ilp"], [20, 40], 2, seed)` returns rows with `solver, n, median_s` |

**Gate decision, 16 Nov.** If B&B or blossom matching is still red, apply the Plan.md cut lines in order: drop the web viewer, then chains, then the multi-round simulation, then the hand-written blossom (keep augmenting-path and flag `optimal=None`), then B&B. **Never cut** failure-aware scoring, the brute-force/kep_solver cross-checks or the edge-case demo.

---

## 11. Phase 4: Experiments (Tue 17 – Sun 22 Nov) · ◆ feature freeze Mon 23 Nov

**Goal:** `python -m donorbridge results` rebuilds every CSV, all four charts and the answer from nothing. `--quick` does it in under 5 minutes.

### Tasks

- [ ] **L4.0** Push `test_phase4.py` Tue 10 am. Agree CSV column names with each experiment owner **that morning** (put them in the test).
- [ ] **L4.1** CLI `results [--quick] [--only NAME]`: run every `EXPERIMENTS` entry, then `compute_answer`, then `make_all_figures`. Print timings. `sweep` = only `survival_sweep`; `bench` keeps `--crosscheck` and gains `--runtime`.
- [ ] **L4.2** 🧑‍🏫 `experiments/answer.py`: from `survival_sweep.csv`, find the survival rate p* below which failure-aware 3-way adds < 5% over 2-way. Interpolate linearly between grid points and write `results/answer.json` with `threshold_p`, the gain table and a one-sentence answer.
- [ ] **L4.3** Wire `demo [small|india|edge|all]` to `demos.DEMOS`.
- [ ] **L4.4** Review every experiment's seeds and pool counts (20 pools per setting minimum, seeds documented).
- [ ] **L4.5** Freeze: on Mon 23 Nov, after `phase-4-done`, tag `v1.0-freeze`. From then on only bug fixes with a test go in, through a PR you approve.
- [ ] **Stretch (cut first):** `run --export-viewer out.json` (nodes, edges, chosen rings) for a Next.js viewer.

### Prompts

**L4.1 🛠: `results` command**

```text
[context block]

Task: implement `results`, `sweep` and `bench --runtime` in donorbridge/__main__.py.
results: for each name, cls in EXPERIMENTS (or only --only NAME): cls(out_dir, quick, seed).run(), timing
each; then experiments.answer.compute_answer(out_dir) (writes answer.json); then
simulation.plots.make_all_figures(out_dir) (the survival chart marks p* from answer.json); print a summary table (experiment, rows, seconds) and the answer sentence. --out DIR (default results),
--seed (default 2026), --quick. A failure in one experiment is reported and the others still run;
exit 1 at the end if any failed.
sweep: same but only "survival_sweep". bench --runtime: calls simulation.benchmark.time_solvers with
defaults and writes results/runtime.csv.
```

**L4.2 🧑‍🏫: the answer**

```text
[context block]

I'm computing the project's headline number myself; review my method, don't write it.
Data: results/survival_sweep.csv has one row per pool: (p, policy, seed, n, planned_transplants,
expected_transplants, resolve_mean) with policy in {"two_way", "three_way_failure_aware",
"three_way_count_max"}. I average expected_transplants over pools per (p, policy).
My method: gain(p) = FA3(p)/TWO(p) - 1; p* = the p where gain crosses 0.05, by linear interpolation
between the two grid points that straddle it.
1. Is linear interpolation defensible on a 0.1-spaced grid? Should I refine the grid near p*?
2. How do I report uncertainty on p* honestly given 20 pools (bootstrap over pools?) — sketch it.
3. Edge cases: gain never drops below 5%; gain non-monotone.
4. Draft the one-sentence answer for the closing slide in plain English for a non-technical panel.
<paste my compute_answer draft>
```

### Integration test spec: Phase 4

| Test | Checks |
| --- | --- |
| `test_p4_e2e_results_quick` | `results --quick --out tmp` exits 0 in < 5 min; every expected CSV, the 4 PNGs and `answer.json` exist |
| `test_p4_lead_answer_json` | `0.5 < threshold_p < 1.0`; sentence is a non-empty string; gain table has every p |
| `test_p4_simulation_fa_never_below_two_way` | survival_sweep: for every pool and p, FA3 expected ≥ 2-way expected (exact property: every 2-way plan is feasible for FA3) |
| `test_p4_simulation_count_max_equals_fa_at_p1` | At p = 1.0 the two 3-way policies are equal |
| `test_p4_generator_csvs` | blood_mix, female_sensitisation, regions CSVs have the agreed columns; national pool ≥ four regional pools |
| `test_p4_matching_demos_run` | `demo all` exits 0; the edge demo output contains "re-solve" |
| `test_p4_heuristics_gap_and_ring_length` | gap ≥ 0 everywhere; ring_length mean L=4 ≥ L=3 ≥ L=2 |
| `test_p4_simulation_figures_exist` | 4 non-empty PNGs (survival, blood_mix, fairness, runtime) |

---

## 12. Phase 5: Story (Tue 24 Nov – Mon 7 Dec)

**Goal:** a clean, reproducible submission, a 10-minute talk with three timed rehearsals, and a design file that covers rubric items 1–4.

Two merges: **Mon 30 Nov** (docs and deck draft) and **Sun 6 Dec** (final). Submit Mon 7 Dec.

### Tasks

- [ ] **L5.0** Push `test_phase5.py` (release check) Tue 24 Nov.
- [ ] **L5.1** `DESIGN.md`: merge `docs/design/*.md` under these sections: problem statement; assumptions register (generator owner leads); flowchart and pseudocode per module (dated); algorithm justification (the ladder, NP-hardness, why ILP is the oracle); limitations.
- [ ] **L5.2** `AI_LOG.md`: merge `ai_logs/*.md` by date, with a short summary at the top (counts per mode, the five most useful corrections).
- [ ] **L5.3** `README.md`: what it is, install, one-command demo, `results`, how to read the charts, "real statistics, simulated patients".
- [ ] **L5.4** Deck outline and owner per slide (prompt below). Slides first draft by Sun 29 Nov.
- [ ] **L5.5** Rehearsals: dry run Mon 30 Nov, then three timed runs before 7 Dec, each under 10 minutes. Clinical Q&A drill: everyone answers two questions cold.
- [ ] **L5.6** `scripts/release_check.sh`: fresh clone → venv → install → `pytest -m "not slow"` → `demo all` → `results --quick`.
- [ ] **Stretch, after December:** public repo and the two-page note.

### Prompts

**L5.1 🛠: design file merge**

```text
[context block]

Task: merge these five design notes into one DESIGN.md with the sections: 1 Problem statement,
2 Assumptions register (table: assumption | value | source | how we tested whether it matters),
3 Architecture (module map + Solver template method + data flow diagram in mermaid),
4 Modules: flowchart + pseudocode per module, keeping each author's dates,
5 Algorithm justification (the ladder first-come → greedy → local search → matching → B&B → ILP; why
2-rings are polynomial and 3-rings NP-hard; why the ILP is the oracle, not the answer),
6 Limitations. Do not invent content; where something is missing, write "TODO(<role>)".
<paste docs/design/*.md>
```

**L5.4 🛠: deck outline**

```text
[context block]

Draft a 10-minute, 12-slide outline for a university panel (non-medical). Constraints from our plan:
lead with the hand-written algorithms and call the ILP the oracle; one ring picture, one crossover
chart; at most three formulas (the ILP, w_c = |c| p^|c|, 3p^3 > 2p^2 iff p > 2/3); say "real
statistics, simulated patients" on the first results slide; frame: clinicians decide, unmatched means
waiting for the next round. Give each slide: title, one-sentence message, visual, speaker
(lead/generator/matching/heuristics/simulation; everyone speaks), seconds. Total ≤ 570 s.
Our results: <paste answer.json and the survival_sweep table>
```

**L5.5 🧑‍🏫: clinical Q&A drill**

```text
[context block]

Act as a sceptical nephrologist and a sceptical CS professor on our panel. Ask 15 hard questions
(8 clinical, 7 algorithmic) about our project, one at a time. After each of my answers, rate it 1–5
and tell me what a strong answer would add. Start with: "Why should a hospital trust a simulation?"
```

### Integration test spec: Phase 5 (release check)

| Test | Checks |
| --- | --- |
| `test_p5_release_check` (slow) | `scripts/release_check.sh` exits 0 on a fresh clone |
| `test_p5_readme_commands` | Every `python -m donorbridge ...` line in README runs (with `--quick` where offered) |
| `test_p5_docs_present` | DESIGN.md has all six sections and no `TODO(`; AI_LOG.md has entries from all five roles |
| `test_p5_no_stubs_left` | No `NotImplementedError("` remains in `donorbridge/`, except cut features listed in DESIGN.md §6 |

---

## 13. If you're stuck

- **A teammate stalls on recursion** (cycle finder late on Wed 4 Nov, or B&B red on Fri 13 Nov): pair with them for an hour. The cycle-finder fallback is the nested loops (`find_cycles_nested_loops`), which already exist.
- **kep_solver won't install:** keep it in `.venv-oracle` with `pulp==2.9.0`. If it still fails, compare the ILP against brute force on small Glasgow sub-pools (`pool.subpool`) and note it in Limitations.
- **CBC is slow or crashes:** switch `backend="highs"`.
- **A merge breaks `main`:** revert that merge commit (`git revert -m 1 <sha>`), run integration again and hand the branch back to its owner.
- **A medical debate starts** (tissue typing, HLA): the compatibility model was frozen in week 1. Add the question to the Limitations list and move on.
