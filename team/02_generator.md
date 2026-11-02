# DonorBridge · Generator owner playbook

**Owner:** ____________ · **Role:** Generator owner (pool generator, India and US calibration, sensitisation and spouse rules)
**The algorithm you present on stage:** calibrated random pool generation. You explain how real Indian statistics turn into realistic simulated families, and why the pool ends up skewed toward hard-to-match O patients.

Every number in the project flows through your code. If the generator is off, every chart is off. Your two superpowers are **citations** (every number in `calibration.py` names its source) and **checks** (the US preset reproduces the published Saidman benchmark).

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

After every prompt, add an entry to `ai_logs/<role>.md` (yours: `ai_logs/generator.md`). The lead merges these into `AI_LOG.md` in P5.

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

My role: Generator owner (pool generator, India/US calibration, sensitisation and spouse rules).
I own: donorbridge/compatibility.py, generator/calibration.py, generator/saidman.py, generator/report.py, generator/survival_models.py, generator/regions.py, experiments/blood_mix.py, experiments/female_sensitisation.py, experiments/regions.py, and their tests in tests/unit/.
````

## 7. Before Phase 1 (today, Mon 2 Nov: design gate)

- [ ] `docs/design/generator.md` has dated pseudocode and a flowchart for: `blood_compatible`, `SaidmanGenerator.generate_with_report`, edge creation, the spouse rule, and `split_by_region`.
- [ ] Collect the source tables as text or screenshots: Saidman et al. 2006 (the pool-generation parameter table), Agrawal et al. 2014 (ABO shares), the NOTTO gender figures (South First article), and Plan.md's crossmatch rates (33% wife←husband, 11% unrelated).
- [ ] List the unit-test cases you'll write in P1.

**Prompt G0.1 🧑‍🏫: design-gate check**

```text
[paste context block]

Here is my pseudocode for the pool generator (dated). Don't write code. Please:
1. Turn it into a mermaid flowchart I can paste into markdown.
2. Point out any step that violates the contract or team rules (global randomness, ids used as
   indices, returning the wrong type).
3. Point out where the order of random draws could make the same seed give different pools on
   different runs (e.g. iterating over a set).
4. List 8 unit tests I should write first, with expected results.
<paste docs/design/generator.md>
```

---

## 8. Phase 1: Foundations (Tue 3 – Thu 5 Nov)

**Goal:** `make_generator("india").generate(100, seed=1)` returns a valid, deterministic, realistic `Pool`, and the US preset exists with Saidman's numbers.

**Files:** `compatibility.py`, `generator/calibration.py`, `generator/saidman.py`, `tests/unit/test_compatibility.py`, `tests/unit/test_generator.py`.
**Branch:** `p1/generator` (after the lead's contract commit, Tue 12:00).

### Agreed shapes (inside your files, so you design them, but stick to these names)

```python
@dataclass(frozen=True)
class Calibration:
    name: str
    blood_freq: tuple[tuple[BloodGroup, float], ...]   # population ABO shares, sum to 1
    patient_female_share: float
    spouse_share_female_patient: float                 # P(donor is husband | female patient)
    spouse_share_male_patient: float                   # P(donor is wife | male patient)
    pra_bands: tuple[tuple[float, float], ...]         # (PRA value, probability), probabilities sum to 1
    female_hs_share: float | None = None               # P(highly sensitised | female patient); None = use pra_bands
    target_xm_spouse: float = 0.33                     # target positive-crossmatch rate, wife <- husband
    target_xm_unrelated: float = 0.11                  # target positive-crossmatch rate, unrelated
    n_regions: int = 4
    sources: tuple[str, ...] = ()                      # citations for every number above

@dataclass(frozen=True)
class GenerationReport:
    pairs_sampled: int
    rejected_compatible: int             # directly compatible pairs, which never enter the pool
    xm_spouse_female_tested: int         # wife <- husband pairs sampled
    xm_spouse_female_positive: int
    xm_unrelated_tested: int
    xm_unrelated_positive: int
    female_patients_sampled: int
    female_hs_sampled: int
```

**The US preset must use Saidman's parameters exactly,** because it's how we prove the generator against the published 49.8 / 59.8. **The India preset** swaps in Indian ABO shares, NOTTO sex shares and Plan.md's crossmatch targets.

Our recollection of the published numbers is below. **Treat it as a lead, not a source.** Check every value against the paper before typing it in:
- Saidman US ABO: O 48.14%, A 33.73%, B 14.28%, AB 3.85%. PRA bands: 5% / 45% / 90% with shares 70.19% / 20.00% / 9.81%. Spouse rule: a wife's crossmatch with her husband uses PRA' = 1 − 0.75·(1 − PRA).
- Agrawal 2014 India ABO: O ≈ 37.1%, B ≈ 32.3%, A ≈ 22.9%, AB ≈ 7.7%.
- NOTTO 2025: women are 22.7% of recipients and 70.7% of living donors.
- **Known tension:** Saidman's PRA bands imply an unrelated positive-crossmatch rate of about 21%, but Plan.md says 11%. Decide with the lead which rate each preset uses, and record the decision in the assumptions register. Don't silently pick one.

### Tasks

- [ ] **G1.1** 🧑‍🏫 Extract and cross-check calibration numbers from the sources. Write `calibration.py` with `INDIA` and `US`, and a source comment on every number.
- [ ] **G1.2** 🛠 `blood_compatible` plus an exhaustive 16-case test you check by hand.
- [ ] **G1.3** 🧑‍🏫 Write `SaidmanGenerator.generate_with_report` **yourself**: sample pairs until you have n incompatible ones, then draw edges.
- [ ] **G1.4** 🧑‍🏫 AI review of your generator code.
- [ ] **G1.5** 🛠 Unit tests: determinism, shape, selection effect, report consistency, both presets.
- [ ] Open PR `p1/generator → main` by Thu 6 pm.

### Prompts

**G1.1 🧑‍🏫: calibration extraction**

```text
[context block]

I'm building the calibration presets. Below are excerpts I copied from the sources. Using ONLY these
excerpts (do not fill anything from memory), produce:
1. A table: parameter | US (Saidman) value | India value | source excerpt it came from.
2. Every parameter where the excerpts disagree or a value is missing, marked "DECIDE".
3. A check: with the PRA bands given, what is the expected positive-crossmatch rate for an unrelated
   pair? For a wife <- husband pair under the spouse rule? Compare with Plan.md targets 11% and 33%
   and explain the gap.
4. Any share that doesn't sum to 1.
Excerpts:
<paste Saidman table / paragraphs>
<paste Agrawal 2014 ABO results>
<paste NOTTO gender figures>
<paste Plan.md "Women and sensitisation" row>
```

**G1.2 🛠: compatibility**

```text
[context block]

Task: implement donorbridge/compatibility.py: blood_compatible(donor, patient) -> bool using the ABO
rule only (Rh ignored: our model is frozen). Write tests/unit/test_compatibility.py that checks all 16
(donor, patient) combinations against an explicit hand-written truth table in the test (not computed
from the function). Then print the truth table as a 4x4 grid so I can verify it by hand.
```

Check the 4×4 grid yourself: O gives to everyone; A gives to A and AB; B gives to B and AB; AB gives only to AB.

**G1.3 🧑‍🏫: generator pseudocode review (you write the code)**

```text
[context block]

I'm hand-writing SaidmanGenerator.generate_with_report(n, seed). Tutor me; do NOT write the
implementation. Here is my pseudocode:
<paste pseudocode>
My intended algorithm:
  rng = random.Random(seed)
  while len(families) < n:
      draw patient blood, donor blood (independently, from blood_freq)
      draw patient sex; draw relation (spouse share depends on patient sex); donor sex follows
      draw patient PRA from pra_bands (or from female_hs_share override for female patients)
      own crossmatch positive with prob PRA (spouse rule for wife <- husband)
      if blood_compatible(donor, patient) and crossmatch negative: rejected_compatible += 1; continue
      add Family(id=len(families), ..., region=rng.randrange(n_regions))
  edges: for i in ids, for j in ids, i != j: edge if blood_compatible(donor_i, patient_j)
         and rng.random() >= PRA_j
Questions:
1. Is this faithful to Saidman et al.? What did I miss?
2. Is the draw order deterministic for a fixed seed? (Watch out for iteration over sets/dicts.)
3. Edge creation is O(n^2) random draws; is that fine for n=500?
4. Should the edge crossmatch use the same PRA rule as the own-pair crossmatch? Why or why not?
5. What should GenerationReport count, exactly, so the spouse-rule rates can be tested?
```

**G1.4 🧑‍🏫: code review**

```text
[context block]

Review my generator implementation. Check: matches my pseudocode and the contract; determinism;
off-by-one in the loop; enums vs strings; frozen dataclasses built correctly; report counters correct.
Point to lines and propose minimal fixes; don't rewrite.
<paste generator/saidman.py and generator/calibration.py>
```

**G1.5 🛠: unit tests**

```text
[context block]

Write tests/unit/test_generator.py for my generator (code below). Tests:
- same seed -> equal pools; different seeds -> different pools; generate_many uses seeds seed..seed+k-1
- n=100: 100 families, unique ids, no self-edges, every edge blood-compatible
- report.pairs_sampled == n + report.rejected_compatible
- selection effect: over 20 India pools of 100, share of O patients > share of O donors
- blood_freq and pra_bands probabilities each sum to 1 for INDIA and US
- n=0 returns an empty Pool; n=1 returns 1 family and no edges
Each test < 1 s; mark anything slower @pytest.mark.slow.
<paste generator/saidman.py>
```

### Integration checks that hit your code (Phase 1)

`test_p1_generator_deterministic`, `test_p1_generator_pool_shape`, `test_p1_generator_selection_effect`, `test_p1_generator_report_consistent`, plus `test_p1_matching_dfs_equals_nested_loops` and `test_p1_e2e_pipeline_india_100`, which use your pools. Run them with `pytest tests/integration/test_phase1.py -k generator`.

**Hand-off:** once your branch has a working `generate`, post in the group chat. The matching, heuristics and simulation owners will use your pools on their branches by `git merge p1/generator` (read-only use).

---

## 9. Phase 2: Engine v1 (Fri 6 – Tue 10 Nov)

**Goal:** the spouse rule and sex-dependent sensitisation are in. The US preset reproduces Saidman's benchmark (prototype: 48.5 / 58.2), and the India preset reproduces the prototype (52.0 / 63.0).

**Files:** `generator/saidman.py`, `generator/calibration.py`, `generator/report.py`.

### Tasks

- [ ] **G2.1** 🧑‍🏫 Spouse rule and donor sex: a wife receiving from her husband gets the boosted crossmatch. Use `GenerationReport` to verify the measured rates hit the calibration targets.
- [ ] **G2.2** 🧑‍🏫 The `female_hs_share` override: female patients are highly sensitised with that probability. Needed later for the 10–40% sweep.
- [ ] **G2.3** 🛠 `calibration_report(preset, n_pools, n, seed)` returns a DataFrame of in-pool statistics: patient/donor ABO mix, % female patients, % highly sensitised, edge density, mean ring counts for L=2 and L=3. Also `python -m donorbridge.generator.report` prints INDIA vs US side by side.
- [ ] **G2.4** 🧑‍🏫 Calibration smoke test: once the lead's ILP lands on `main` (merge `main` into your branch), run 20 US pools × 100 and 20 India pools × 100. If the means are outside the bands, debug with G2.4.
- [ ] Open PR by Tue 10 Nov, 6 pm.

### Prompts

**G2.1 🧑‍🏫: spouse rule**

```text
[context block]

I'm adding the spouse rule. Plan.md: a wife receiving from her husband has a positive crossmatch about
33% of the time, vs 11% for unrelated pairs (source: <paste>). Saidman uses PRA' = 1 - 0.75(1 - PRA)
for wife <- husband. Tutor me:
1. With my PRA bands <paste>, what positive-crossmatch rate does Saidman's rule give for wives? Does it
   hit 33%? If not, what multiplier would, and is changing it defensible?
2. Should the spouse boost also apply to the wife's crossmatches with OTHER families' donors? (Saidman:
   no — explain why.)
3. Which GenerationReport counters prove the rule works, and what tolerance is reasonable over
   20,000 sampled pairs (binomial SE)?
I'll write the code; review it after.
```

**G2.2 🧑‍🏫: female sensitisation knob**

```text
[context block]

I need Calibration.female_hs_share (P(highly sensitised | female patient)), overridable via
make_generator(female_hs_share=0.3). The sweep goes 0.10 to 0.40. My plan: for female patients, draw
"highly sensitised?" with that probability; if yes, PRA = the high band value; if no, draw from the
non-high bands renormalised. Male patients keep the base bands.
1. Does this keep the overall pool comparable across the sweep, or does it also change total
   sensitisation? Is that what we want for "women and sensitisation"?
2. How do I expose overrides cleanly with a frozen dataclass (dataclasses.replace)?
3. Tests I need.
```

**G2.3 🛠: calibration report**

```text
[context block]

Write generator/report.py: calibration_report(preset, n_pools, n, seed) -> pd.DataFrame (one row per
statistic, columns: statistic, mean, sd), and a __main__ block printing INDIA vs US side by side.
Statistics: in-pool patient ABO shares, in-pool donor ABO shares, % female patients, % highly
sensitised patients, edges per family, number of 2-rings and 3-rings (use donorbridge.cycles.find_cycles),
report-based wife<-husband and unrelated positive-crossmatch rates.
<paste generator/saidman.py public API>
```

**G2.4 🧑‍🏫: when the benchmark doesn't match**

```text
[context block]

My US preset gives mean transplants (20 pools x 100, ILP, count) of <x> with L=2 and <y> with L=3.
Saidman et al. report 49.8 / 59.8; our prototype got 48.5 / 58.2. Here's my calibration report and
generator code. Rank the likely causes (pool size convention, PRA bands, spouse rule, edge crossmatch,
rejection rule, ABO shares) and give me one quick experiment per cause to confirm or rule it out.
<paste calibration_report output>
<paste generator code>
```

### Integration checks that hit your code (Phase 2)

`test_p2_generator_spouse_rule`, `test_p2_generator_female_hs_knob`, `test_p2_generator_calibration_us` (slow), `test_p2_generator_calibration_india` (slow). Run them with `pytest tests/integration/test_phase2.py -k generator --run-slow`.

---

## 10. Phase 3: Exact solvers and failure model (Wed 11 – Mon 16 Nov) · ◆ gate 16 Nov

**Goal:** the two extra models the experiments need: sensitisation-dependent crossmatch failure, and splitting the national pool into state pools. Your generator is also hardened by 1,000-pool invariant tests.

**Files:** `generator/survival_models.py`, `generator/regions.py`, tests.

### Tasks

- [ ] **G3.1** 🛠 `SensitisationSurvival(p_low, p_high)`: `edge(pool, i, j)` returns `p_high` if patient j is highly sensitised, else `p_low`. Plan.md decision: "highly sensitised patients fail more often". Record the chosen default values (e.g. `p_high = p_low − 0.1`) in the assumptions register as an assumption, not a fact.
- [ ] **G3.2** 🛠 `split_by_region(pool)` returns 4 sub-pools by `Family.region`, via `pool.subpool`, named `"<name>-r<k>"`. Edges that cross regions are dropped; that is the point of the experiment.
- [ ] **G3.3** 🛠 Invariant tests on 1,000 generated pools (marked slow): every pool validates, ids are unique, edges are ABO-compatible, there are no self-edges, and the report adds up. Also a timing test: n=500 generates in under 2 s.
- [ ] **G3.4** Write the generator section of `docs/design/generator.md`: final flowchart, pseudocode and the assumptions-register rows you own.

### Prompts

**G3.1 🛠: sensitisation-dependent survival**

```text
[context block]

Implement donorbridge/generator/survival_models.py: SensitisationSurvival(SurvivalModel) with
__init__(p_low, p_high) validating 0 <= p_high <= p_low <= 1, and edge() returning p_high when the
PATIENT of the edge (pool.family(patient_family)) is highly sensitised, else p_low. Add __repr__.
Tests: a 3-ring with one highly sensitised patient has survival p_low^2 * p_high;
ExpectedTransplantScorer(SensitisationSurvival(0.9, 0.7)) weights; works with ILP via get_solver.
```

**G3.2 🛠: region split**

```text
[context block]

Implement donorbridge/generator/regions.py: split_by_region(pool) -> list[Pool], one per region
present, sorted by region, each pool.subpool(ids of that region, name=f"{pool.name}-r{k}").
Tests: ids partition the original; no edge crosses regions; sum of sizes == n; a pool with all
families in region 0 returns one pool equal (families/edges) to the original.
```

**G3.3 🛠: invariant tests**

```text
[context block]

Write slow invariant tests in tests/unit/test_generator_invariants.py over 1000 pools
(make_generator("india").generate_many(1000, n, seed=0) with n cycling through 10, 50, 100) checking:
<list the invariants from my task G3.3>. Plus a timing test for n=500 < 2 s (not slow-marked; skip
if CI is slower — use an env var).
```

### Integration checks that hit your code (Phase 3)

`test_p3_generator_sensitisation_survival`, `test_p3_generator_split_by_region`. Your pools also drive `test_p3_e2e_crosscheck_1000`.

---

## 11. Phase 4: Experiments (Tue 17 – Sun 22 Nov) · ◆ feature freeze Mon 23 Nov

**Goal:** three experiments that answer three of the Plan.md "decisions to lock in" rows: India vs US mix, women and sensitisation, and one pool vs many. Each one writes a tidy CSV that the simulation owner turns into charts.

**Files:** `experiments/blood_mix.py`, `experiments/female_sensitisation.py`, `experiments/regions.py`.

On Tue 17 Nov, 10 am, confirm the CSV columns below with the lead and the simulation owner. They go into `test_phase4.py`.

| Experiment (`name`) | Settings (full / quick) | CSV columns (one row per pool per setting) |
| --- | --- | --- |
| `BloodMix` (`blood_mix`) | preset ∈ {india, us} × max_len ∈ {2, 3} × p ∈ {1.0, 0.8, 0.6}; 20 pools × 100 / 3 pools × 40 | `preset, max_len, p, seed, n, transplants, expected_transplants` |
| `FemaleSensitisation` (`female_sensitisation`) | female_hs_share ∈ {0.1, 0.2, 0.3, 0.4}, ILP L=3, p ∈ {1.0, 0.8}; 20 × 100 / 3 × 40 | `female_hs_share, p, seed, transplants, female_matched_share, male_matched_share, hs_matched_share` |
| `RegionSplit` (`regions`) | national vs 4 regions, ILP L=3, p ∈ {1.0, 0.8}; 20 × 200 / 3 × 60 | `setting, p, seed, transplants` (setting ∈ {national, regional}; regional = sum over the 4 sub-pools) |

All use `ExpectedTransplantScorer(p)` (failure-aware) and `compute_metrics` from the simulation owner. Seeds are `self.seed + k`.

### Tasks

- [ ] **G4.1** 🛠 `BloodMix`.
- [ ] **G4.2** 🛠 `FemaleSensitisation`.
- [ ] **G4.3** 🛠 `RegionSplit`.
- [ ] **G4.4** 🧑‍🏫 Read your results. Does India gain more or less from 3-way than the US? Is the gender gap in the matcher or in who enters the pool? (Plan.md risk: the gender result may be null or reversed. If so, present it as a finding.)
- [ ] **G4.5** 🛠 Pool-statistics table for the slides (from `calibration_report`): India vs US in-pool mix.
- [ ] Open PR by Sun 22 Nov, 6 pm. **Nothing new after the Mon 23 Nov freeze.**

### Prompts

**G4.1–G4.3 🛠: experiments (one chat per experiment)**

```text
[context block]

Implement donorbridge/experiments/<file>.py: class <Name>(Experiment) with name = "<name>".
Settings: <paste that experiment's row from my table>. In quick mode use the quick sizes.
For each setting and each pool k: pool = make_generator(preset, **overrides).generate(n, self.seed + k);
solve with get_solver("ilp", max_cycle_len=L, scorer=ExpectedTransplantScorer(p));
metrics = compute_metrics(pool, solution, UniformSurvival(p)); append one row.
Return a DataFrame with exactly these columns: <paste columns>; write it to
self.out_dir / f"{self.name}.csv". Print one progress line per setting.
Here's the Experiment base class: <paste experiments/base.py>
Here's PoolMetrics: <paste simulation/metrics.py PoolMetrics>
Then write a quick-mode unit test that checks columns and row count.
```

**G4.4 🧑‍🏫: interpret the results**

```text
[context block]

Here are summary tables from my three experiments. For each: what is the one-sentence finding, how
confident can we be with 20 pools (rough 95% CI from the sd), and what would a sceptical clinician
object to? For the gender experiment specifically: is the gap in the matcher (female matched share
< male matched share within the pool) or in who enters the pool? Suggest the exact wording for one
slide each.
<paste groupby summaries>
```

### Integration checks that hit your code (Phase 4)

`test_p4_generator_csvs` (columns, and national ≥ regional), plus `test_p4_e2e_results_quick`, which runs your experiments in quick mode.

---

## 12. Phase 5: Story (Tue 24 Nov – Mon 7 Dec)

**You own:** the **assumptions register** in `DESIGN.md` §2, the "real statistics, simulated patients" slide, the India vs US slide, and the medical side of the Q&A drill.

### Tasks

- [ ] **G5.1** 🛠 Assumptions register: assumption | value | source | how we tested whether it matters. Cover all six Plan.md "decisions to lock in", plus ABO shares, PRA bands, the spouse rule and survival p.
- [ ] **G5.2** Slides (about 60 s of talk): where the numbers come from; India vs US.
- [ ] **G5.3** 🧑‍🏫 Medical Q&A drill: be ready for PRA, crossmatch, why ABO only, why no HLA, and why there are no altruists.
- [ ] **G5.4** Final read of `calibration.py`: every number has a source comment, and the README calibration section matches it.
- [ ] Rehearsals: Mon 30 Nov dry run plus three timed runs.

### Prompts

**G5.1 🛠: assumptions register**

```text
[context block]

Build the assumptions-register table for DESIGN.md from my calibration file, my design notes and
Plan.md's "Decisions to lock in" table. Columns: assumption | our value | alternative | source |
how we tested whether it matters (point to the experiment CSV or test). Don't invent sources; write
"TODO" where I haven't given one.
<paste generator/calibration.py, docs/design/generator.md, Plan.md decisions table>
```

**G5.3 🧑‍🏫: medical drill**

```text
[context block]

You are a transplant nephrologist on our panel. Ask me 10 questions, one at a time, about the
medical realism of our generator: PRA, crossmatch, ABO, spouse sensitisation, why we ignore HLA
and Rh, altruistic donors, what "simulated" means for our conclusions. After each answer, score
1-5 and give a better 2-sentence answer I can memorise.
```

---

## 13. If you're stuck

- **Benchmark won't match Saidman:** run G2.4 first, then pair with the lead. The most common causes are the pool-size convention and whether directly compatible pairs are rejected.
- **The same seed gives different pools:** you are iterating over a `set` or `dict` somewhere in the draw order. Iterate over `sorted(...)`.
- **A number has no source:** don't guess. Mark it `# ASSUMPTION` in `calibration.py`, add it to the register, and tell the lead.
- **Medical rabbit hole** (HLA typing, antibody levels): the model was frozen in week 1. Add the question to Limitations and move on.
